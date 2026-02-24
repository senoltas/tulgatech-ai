# engine/reporting/generator.py

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from config import REPORTS_DIR, BASE_DIR, TEMPLATES_DIR


class ReportGenerator:
    """Rapor oluşturucu"""

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(exist_ok=True)

        self.templates_dir = TEMPLATES_DIR  # <--- önemli
        self.template_file = self.templates_dir / "report_template.html"

        # Rapor formatları
        self.formats = {
            "json": self._generate_json_report,
            "txt": self._generate_text_report,
            "csv": self._generate_csv_report,
            "html": self._generate_html_report,
        }

    def generate_all_reports(self, data: Dict) -> Dict:
        """Tüm rapor formatlarını oluştur"""

        project_id = data.get("project", {}).get(
            "project_id", f"PROJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        project_report_dir = self.reports_dir / project_id
        project_report_dir.mkdir(exist_ok=True)

        generated_reports = {}

        for format_name, generator in self.formats.items():
            try:
                report_path = generator(data, project_report_dir)
                if report_path:
                    generated_reports[format_name] = str(report_path)
            except Exception as e:
                print(f"  ⚠️  {format_name.upper()} raporu oluşturulamadı: {e}")

        return generated_reports

    # ----------------------------
    # JSON
    # ----------------------------
    def _generate_json_report(self, data: Dict, output_dir: Path) -> Path:
        report_path = output_dir / "tulgatech_report.json"

        enriched_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "system": "TulgaTech AI v1.0",
                "report_type": "full_analysis",
                "base_dir": str(BASE_DIR),
            },
            "project_summary": self._extract_project_summary(data),
            "detailed_analysis": data,
            "recommendations": data.get("summary", {}).get("recommendations", []),
            "export_info": {
                "formats_available": list(self.formats.keys()),
                "notes": "Bu rapor TulgaTech AI tarafından otomatik oluşturulmuştur.",
            },
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)

        return report_path

    # ----------------------------
    # TXT
    # ----------------------------
    def _generate_text_report(self, data: Dict, output_dir: Path) -> Path:
        report_path = output_dir / "tulgatech_report.txt"

        summary = data.get("summary", {})
        project = data.get("project", {})

        text = "TULGATECH AI - PROJE ANALİZ RAPORU\n"
        text += "=" * 60 + "\n\n"

        text += "TEMEL BİLGİLER:\n"
        text += "-" * 40 + "\n"
        text += f"Proje ID: {project.get('project_id', 'N/A')}\n"
        text += f"Dosya: {project.get('filename', 'N/A')}\n"
        text += f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"

        scale = project.get("scale", 1.0) or 1.0
        scale_conf = project.get("scale_confidence", 0.0)
        inv_scale = int(1 / scale) if scale != 0 else 1
        text += f"Ölçek: 1/{inv_scale} (Güven: {scale_conf:.0%})\n\n"

        text += "ANA METRAJLAR:\n"
        text += "-" * 40 + "\n"
        key_quantities = summary.get("key_quantities", {})
        for name, item_data in key_quantities.items():
            text += f"• {name}: {item_data.get('value', 0):.1f} {item_data.get('unit', '')} "
            text += f"(Güven: {item_data.get('confidence', 0):.0%})\n"

        cost_data = data.get("cost_analysis", {})
        if cost_data:
            text += f"\nMALİYET ÖZETİ:\n"
            text += "-" * 40 + "\n"
            text += f"Toplam Tahmini Maliyet: {cost_data.get('total_cost', 0):,.0f} {cost_data.get('currency', 'TL')}\n"

        schedule = data.get("schedule", {})
        if schedule:
            text += f"\nZAMAN PLANI:\n"
            text += "-" * 40 + "\n"
            text += f"Başlangıç Tarihi: {schedule.get('start_date', 'N/A')}\n"
            text += f"Toplam Süre: {schedule.get('total_duration', 'N/A')}\n"

        recommendations = summary.get("recommendations", [])
        if recommendations:
            text += f"\nÖNERİLER:\n"
            text += "-" * 40 + "\n"
            for i, rec in enumerate(recommendations, 1):
                text += f"{i}. {rec}\n"

        warnings = data.get("warnings", [])
        if warnings:
            text += f"\nUYARILAR:\n"
            text += "-" * 40 + "\n"
            for i, warning in enumerate(warnings[:5], 1):
                text += f"{i}. {warning}\n"
            if len(warnings) > 5:
                text += f"... ve {len(warnings) - 5} daha\n"

        text += f"\n" + "=" * 60 + "\n"
        text += "NOT: Bu rapor otomatik olarak oluşturulmuştur.\n"
        text += "Detaylı kontrol ve onay için profesyonel bir inşaat mühendisine danışınız.\n"
        text += "=" * 60 + "\n"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(text)

        return report_path

    # ----------------------------
    # CSV
    # ----------------------------
    def _generate_csv_report(self, data: Dict, output_dir: Path) -> Optional[Path]:
        import csv

        report_path = output_dir / "tulgatech_quantities.csv"
        quantities = data.get("project", {}).get("quantities", [])

        if not quantities:
            return None

        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["ID", "İş Kalemi", "Kategori", "Miktar", "Birim", "Güven (%)", "Kaynak"]
            )

            for item in quantities:
                writer.writerow(
                    [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("category", ""),
                        item.get("value", ""),
                        item.get("unit", ""),
                        f"{(item.get('confidence', 0) * 100):.0f}",
                        item.get("source", ""),
                    ]
                )

        return report_path

    # ----------------------------
    # HTML (TEMPLATE RENDER)
    # ----------------------------
    def _generate_html_report(self, data: Dict, output_dir: Path) -> Path:
        report_path = output_dir / "tulgatech_report.html"

        summary = data.get("summary", {})
        project = data.get("project", {})
        cost_data = data.get("cost_analysis", {})
        schedule = data.get("schedule", {})

        # Template yoksa, hiç ağlamadan düz HTML üretelim
        if self.template_file.exists():
            template = self.template_file.read_text(encoding="utf-8")
        else:
            template = "<html><body><h1>{{ project_name }}</h1>{{ quantities_rows }}</body></html>"

        # 1) Quantities rows
        quantities_rows = ""
        key_quantities = summary.get("key_quantities", {})
        for name, q in key_quantities.items():
            conf = float(q.get("confidence", 0))
            conf_class = (
                "confidence-high"
                if conf > 0.7
                else "confidence-medium"
                if conf > 0.4
                else "confidence-low"
            )
            quantities_rows += (
                "<tr>"
                f"<td>{name}</td>"
                f"<td>{float(q.get('value', 0)):.2f}</td>"
                f"<td>{q.get('unit', '')}</td>"
                f"<td class='{conf_class}'>{conf:.0%}</td>"
                "</tr>\n"
            )

        # 2) Cost scenarios
        cost_scenarios_html = ""
        scenarios = cost_data.get("scenarios", {}) if cost_data else {}
        if scenarios:
            cost_scenarios_html += "<h3>Alternatif Senaryolar</h3><ul>"
            for _, sc in scenarios.items():
                cost_scenarios_html += (
                    f"<li><strong>{sc.get('description','')}</strong>: "
                    f"{sc.get('total_cost',0):,.0f} TL</li>"
                )
            cost_scenarios_html += "</ul>"

        # 3) Milestones
        milestones_html = ""
        for m in schedule.get("milestones", []) if schedule else []:
            milestones_html += f"<li><strong>{m.get('name','')}</strong>: {m.get('date','')}</li>\n"

        # 4) Recommendations & Warnings
        recommendations_html = ""
        for i, rec in enumerate(summary.get("recommendations", []), 1):
            recommendations_html += f"<div class='recommendation'>{i}. {rec}</div>\n"

        warnings_html = ""
        warnings = data.get("warnings", [])
        for i, w in enumerate(warnings, 1):
            warnings_html += f"<div class='warning'>{i}. {w}</div>\n"

        # Scale display
        scale = project.get("scale", 1.0) or 1.0
        inv_scale = int(1 / scale) if scale != 0 else 1

        ctx = {
            "title": "TulgaTech AI - Proje Raporu",
            "project_name": "TulgaTech AI - Proje Analiz Raporu",
            "project_id": project.get("project_id", "N/A"),
            "report_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "filename": project.get("filename", "N/A"),
            "scale": str(inv_scale),
            "scale_confidence": f"{(project.get('scale_confidence', 0.0) * 100):.0f}",
            "quantities_rows": quantities_rows or "<tr><td colspan='4'>Metraj bulunamadı</td></tr>",
            "total_cost": f"{cost_data.get('total_cost', 0):,.0f}" if cost_data else "0",
            "currency": cost_data.get("currency", "TL") if cost_data else "TL",
            "cost_scenarios": cost_scenarios_html,
            "start_date": schedule.get("start_date", "N/A") if schedule else "N/A",
            "total_duration": str(schedule.get("total_duration", "N/A")) if schedule else "N/A",
            "milestones": milestones_html or "<li>Milestone yok</li>",
            "recommendations": recommendations_html or "<div>Öneri yok</div>",
            "warnings": warnings_html or "<div>Uyarı yok</div>",
            "year": str(datetime.now().year),
        }

        rendered = self._render_template_simple(template, ctx)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        return report_path

    def _render_template_simple(self, template: str, ctx: Dict[str, str]) -> str:
        """Jinja yok, drama yok: basit {{ key }} replace."""
        out = template
        for k, v in ctx.items():
            out = out.replace("{{ " + k + " }}", str(v))
            out = out.replace("{{" + k + "}}", str(v))
            out = out.replace("{{" + k + " }}", str(v))
            out = out.replace("{{ " + k + "}}", str(v))
        return out

    def _extract_project_summary(self, data: Dict) -> Dict:
        summary = data.get("summary", {})
        project = data.get("project", {})

        return {
            "project_id": project.get("project_id", ""),
            "filename": project.get("filename", ""),
            "scale": project.get("scale", 1.0),
            "total_items": len(project.get("quantities", [])),
            "key_quantities": summary.get("key_quantities", {}),
            "confidence_score": summary.get("statistics", {}).get("average_confidence", 0),
            "processing_time": datetime.now().isoformat(),
        }
