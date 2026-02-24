# engine/orchestrator.py

from datetime import datetime
from pathlib import Path

from engine.project_reader import ProjectReader
from engine.quantity_takeoff_engine import QuantityTakeoffEngine
from engine.cost_estimator import CostEstimator
from engine.project_planner import ProjectPlanner
from engine.reporting.generator import ReportGenerator


class TulgaTechOrchestrator:
    """Ana yönetim sınıfı - tüm modülleri koordine eder"""

    def __init__(self):
        self.reader = ProjectReader()
        self.qto_engine = QuantityTakeoffEngine()

        # OPTIONAL modüller:
        price_path = Path("data") / "prices" / "custom_prices.json"
        if price_path.exists():
            self.cost_estimator = CostEstimator(price_database=str(price_path))
        else:
            self.cost_estimator = CostEstimator()

        self.planner = ProjectPlanner()
        self.reporter = ReportGenerator()

    def process_project(self, dxf_file_path: str) -> dict:
        print(f"📁 Proje işleniyor: {dxf_file_path}")

        # 1) PROJE OKUMA
        print("🔍 DXF dosyası okunuyor...")
        project_data = self.reader.read_dxf(dxf_file_path)

        result = {
            "success": False,
            "project": project_data,
            "summary": {},
            "warnings": project_data.get("warnings", []),
            "reports": {},
        }

        if not project_data.get("success", False):
            result["error"] = project_data.get("error", "Proje okunamadı")
            return result

        scale = project_data.get("scale", 1.0)
        scale_conf = project_data.get("scale_confidence", 0.0)

        if scale and scale > 0:
            inv = 1 / scale
            try:
                inv_int = int(round(inv))
            except Exception:
                inv_int = inv
            print(f"  ✓ Ölçek: 1/{inv_int} (Güven: {scale_conf:.0%})")
        else:
            print(f"  ✓ Ölçek: bilinmiyor (Güven: {scale_conf:.0%})")

        # 2) METRAJ
        print("📏 Metraj hesaplanıyor...")
        quantities = self.qto_engine.calculate_from_architecture(
            project_data.get("architectural", {}),
            scale if (scale and scale > 0) else 1.0,
        )
        project_data["quantities"] = [q.to_dict() for q in quantities]

        # 3) MALİYET
        print("💰 Maliyet tahmini yapılıyor...")
        cost_analysis = self.cost_estimator.estimate(quantities)

        # 4) PLAN
        print("🗓️ Proje planı oluşturuluyor...")
        schedule = self.planner.create_schedule(quantities)

        # 5) SUMMARY
        summary = self._build_summary(quantities, cost_analysis, schedule)

        # 6) REPORTS
        print("🧾 Raporlar üretiliyor...")
        reports = self.reporter.generate_all_reports({
            "project": project_data,
            "summary": summary,
            "cost_analysis": cost_analysis,
            "schedule": schedule,
            "warnings": result["warnings"],
        })

        result.update({
            "success": True,
            "summary": summary,
            "cost_analysis": cost_analysis,
            "schedule": schedule,
            "reports": reports,
        })

        print("✅ Proje işleme tamamlandı!")
        return result

    def _build_summary(self, quantities, cost_analysis, schedule) -> dict:
        # key quantities: basit seçici
        key = {}
        for q in quantities:
            nm = q.name.lower()
            if "brüt" in nm or "net" in nm or "duvar" in nm or "zemin" in nm or "boya" in nm or "kapı" in nm:
                key[q.name] = {"value": q.value, "unit": q.unit, "confidence": q.confidence}

        avg_conf = sum(q.confidence for q in quantities) / len(quantities) if quantities else 0.0

        return {
            "key_quantities": key,
            "total_estimated_cost": cost_analysis.get("total_cost", 0.0),
            "confidence_score": avg_conf,
            "recommendations": [
                "Ölçek güveni düşükse projede en az 1 bilinen ölçüyle kalibrasyon yapın.",
                "Kapı/pencere tespiti zayıfsa manuel kontrolle adetleri doğrulayın.",
            ],
        }
