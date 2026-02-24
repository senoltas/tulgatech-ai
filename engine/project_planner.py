"""
Proje Planlama Motoru
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

from engine.quantity_models import QuantityItem


class ProjectPlanner:
    """Proje planlama motoru"""

    def __init__(self):
        self.task_templates = self._load_task_templates()
        self.duration_factors = {
            "foundation": 1.2,
            "structure": 1.0,
            "enclosure": 0.8,
            "interior": 0.9,
            "finishing": 0.7,
            "mep": 0.6,
            "preparation": 1.0,
        }

    def _load_task_templates(self) -> Dict:
        """Görev şablonlarını yükle"""
        return {
            "site_prep": {"name": "Şantiye Kurulumu", "duration_days": 3, "depends_on": [], "category": "preparation", "crew_size": 4},
            "excavation": {"name": "Kazı İşleri", "duration_days": 5, "depends_on": ["site_prep"], "category": "foundation", "crew_size": 6},
            "foundation": {"name": "Temel İşleri", "duration_days": 7, "depends_on": ["excavation"], "category": "foundation", "crew_size": 8},
            "walls_structure": {"name": "Duvar ve Taşıyıcı Sistem", "duration_days": 10, "depends_on": ["foundation"], "category": "structure", "crew_size": 10},
            "roof": {"name": "Çatı İşleri", "duration_days": 5, "depends_on": ["walls_structure"], "category": "enclosure", "crew_size": 6},
            "exterior_walls": {"name": "Dış Cephe", "duration_days": 8, "depends_on": ["roof"], "category": "enclosure", "crew_size": 8},
            "windows_doors": {"name": "Pencere ve Kapı Montajı", "duration_days": 4, "depends_on": ["exterior_walls"], "category": "enclosure", "crew_size": 4},
            "interior_walls": {"name": "İç Bölme Duvar", "duration_days": 6, "depends_on": ["windows_doors"], "category": "interior", "crew_size": 6},
            "electrical_rough": {"name": "Kaba Elektrik", "duration_days": 5, "depends_on": ["interior_walls"], "category": "mep", "crew_size": 3},
            "plumbing_rough": {"name": "Kaba Sıhhi Tesisat", "duration_days": 4, "depends_on": ["interior_walls"], "category": "mep", "crew_size": 3},
            "plaster": {"name": "Sıva İşleri", "duration_days": 7, "depends_on": ["electrical_rough", "plumbing_rough"], "category": "interior", "crew_size": 6},
            "flooring": {"name": "Zemin Kaplama", "duration_days": 6, "depends_on": ["plaster"], "category": "finishing", "crew_size": 4},
            "painting": {"name": "Boya İşleri", "duration_days": 5, "depends_on": ["flooring"], "category": "finishing", "crew_size": 4},
            "finish_electrical": {"name": "Son Elektrik", "duration_days": 3, "depends_on": ["painting"], "category": "mep", "crew_size": 2},
            "finish_plumbing": {"name": "Son Sıhhi Tesisat", "duration_days": 2, "depends_on": ["painting"], "category": "mep", "crew_size": 2},
            "cleanup": {"name": "Temizlik ve Teslim", "duration_days": 2, "depends_on": ["finish_electrical", "finish_plumbing"], "category": "finishing", "crew_size": 4},
        }

    def create_schedule(
        self,
        quantities: List[Union[QuantityItem, Dict]],
        start_date: Optional[datetime] = None,
    ) -> Dict:
        """Proje çizelgesi oluştur"""

        if not start_date:
            start_date = datetime.now() + timedelta(days=7)  # 1 hafta sonra

        project_size = self._estimate_project_size(quantities)
        adjusted_tasks = self._adjust_durations_by_size(project_size)
        scheduled_tasks = self._schedule_tasks(adjusted_tasks, start_date)

        critical_path = self._find_critical_path(scheduled_tasks)
        milestones = self._extract_milestones(scheduled_tasks)
        resource_plan = self._plan_resources(scheduled_tasks)
        procurement_advice = self._generate_procurement_advice(scheduled_tasks)

        end_date = scheduled_tasks[-1]["end_date"] if scheduled_tasks else start_date.isoformat()
        total_duration_days = self._calc_total_duration_days(scheduled_tasks)

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date,
            "total_duration_days": total_duration_days,
            "tasks": scheduled_tasks,
            "critical_path": critical_path,
            "milestones": milestones,
            "resource_plan": resource_plan,
            "procurement_advice": procurement_advice,
            "assumptions": {
                "project_size_factor": project_size["factor"],
                "weather_buffer_days": 5,
                "weekend_work": False,
            },
        }

    def _get_quantity_name_value(self, q: Union[QuantityItem, Dict]) -> (str, float):
        if isinstance(q, dict):
            return (q.get("name", ""), float(q.get("value", 0) or 0))
        return (q.name, float(q.value))

    def _estimate_project_size(self, quantities: List[Union[QuantityItem, Dict]]) -> Dict:
        """Proje büyüklüğünü tahmin et"""

        area = None
        for q in quantities:
            name, val = self._get_quantity_name_value(q)
            if name == "Brüt İnşaat Alanı":
                area = val
                break

        if area is None or area <= 0:
            area = 100.0  # varsayılan

        if area < 50:
            size_category, factor = "small", 0.7
        elif area < 150:
            size_category, factor = "medium", 1.0
        elif area < 300:
            size_category, factor = "large", 1.3
        else:
            size_category, factor = "xlarge", 1.6

        return {"area_m2": area, "category": size_category, "factor": factor}

    def _adjust_durations_by_size(self, project_size: Dict) -> Dict:
        """Proje büyüklüğüne göre süreleri ayarla"""
        adjusted = {}
        for task_id, task in self.task_templates.items():
            t = task.copy()
            category = t["category"]
            category_factor = self.duration_factors.get(category, 1.0)
            size_factor = project_size["factor"]

            base_duration = int(t["duration_days"])
            adjusted_duration = base_duration * category_factor * size_factor
            t["duration_days"] = max(1, int(round(adjusted_duration)))
            adjusted[task_id] = t
        return adjusted

    def _schedule_tasks(self, tasks: Dict, start_date: datetime) -> List[Dict]:
        """Görevleri tarihlendir (basit bağımlılık çözümü)"""
        scheduled: List[Dict] = []
        task_dates: Dict[str, (datetime, datetime)] = {}

        for task_id in tasks.keys():
            task = tasks[task_id]

            if task["depends_on"]:
                latest_end = start_date
                for dep_id in task["depends_on"]:
                    if dep_id in task_dates:
                        dep_end = task_dates[dep_id][1]
                        if dep_end > latest_end:
                            latest_end = dep_end
                start = latest_end + timedelta(days=1)
            else:
                start = start_date

            duration = int(task["duration_days"])
            end = start + timedelta(days=duration - 1)

            task_dates[task_id] = (start, end)

            scheduled.append(
                {
                    "id": task_id,
                    "name": task["name"],
                    "category": task["category"],
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "duration_days": duration,
                    "depends_on": task["depends_on"],
                    "crew_size": task["crew_size"],
                    "progress": 0.0,
                    "status": "planned",
                }
            )

        # kronolojik sıraya diz (daha temiz çıktı)
        scheduled.sort(key=lambda x: x["start_date"])
        return scheduled

    def _find_critical_path(self, tasks: List[Dict]) -> List[str]:
        """Kritik yolu bul (basitleştirilmiş)"""
        critical_path: List[str] = []
        max_duration = 0
        current_path: List[str] = []
        current_duration = 0

        for task in tasks:
            if not task["depends_on"] or all(dep in current_path for dep in task["depends_on"]):
                current_path.append(task["id"])
                current_duration += int(task["duration_days"])
            else:
                if current_duration > max_duration:
                    max_duration = current_duration
                    critical_path = current_path.copy()
                current_path = [task["id"]]
                current_duration = int(task["duration_days"])

        if current_duration > max_duration:
            critical_path = current_path

        return critical_path

    def _extract_milestones(self, tasks: List[Dict]) -> List[Dict]:
        """Kilometre taşlarını çıkar"""
        if not tasks:
            return []

        milestones = [{"name": "Proje Başlangıcı", "date": tasks[0]["start_date"], "type": "start"}]
        important = {"foundation", "roof", "painting", "cleanup"}

        for t in tasks:
            if t["id"] in important:
                milestones.append(
                    {
                        "name": f"{t['name']} Tamamlandı",
                        "date": t["end_date"],
                        "type": "completion",
                        "task_id": t["id"],
                    }
                )

        milestones.append({"name": "Proje Tamamlandı", "date": tasks[-1]["end_date"], "type": "completion"})
        return milestones

    def _plan_resources(self, tasks: List[Dict]) -> Dict:
        """Kaynak planlaması"""
        # basit: her gün toplam işçi (paralel düşünmüyoruz, ama rapor için yeter)
        labor_days: List[int] = []
        for t in tasks:
            labor_days.extend([int(t["crew_size"])] * int(t["duration_days"]))

        peak = max(labor_days) if labor_days else 0
        avg = (sum(labor_days) / len(labor_days)) if labor_days else 0

        return {
            "labor": {
                "peak_workers": peak,
                "average_workers": round(avg, 2),
                "total_worker_days": int(sum(labor_days)),
            },
            "equipment": self._estimate_equipment_needs(tasks),
            "key_resources": [
                "Vinç (ilk 30 gün)",
                "Beton pompası (temel ve taşıyıcı sistem işleri)",
                "İskele sistemi (cephe işleri)",
            ],
        }

    def _estimate_equipment_needs(self, tasks: List[Dict]) -> List[Dict]:
        """Ekipman ihtiyaçlarını tahmin et"""
        equipment = []
        categories_with_equipment = {
            "foundation": ["ekskavatör", "kamyon", "vibratör"],
            "structure": ["vinç", "kalıp", "iskele"],
            "enclosure": ["iskele", "yük asansörü"],
            "finishing": ["zımpara makinesi", "boya tabancası"],
        }

        used = set()
        for t in tasks:
            cat = t["category"]
            for eq in categories_with_equipment.get(cat, []):
                if eq not in used:
                    equipment.append({"name": eq, "duration_days": t["duration_days"], "task": t["name"]})
                    used.add(eq)
        return equipment

    def _generate_procurement_advice(self, tasks: List[Dict]) -> Dict:
        """Satın alma önerileri (metrajdan bağımsız basit timeline)"""
        material_types = {
            "structural": ["çimento", "demir", "tuğla", "beton"],
            "enclosure": ["cam", "pencere", "kapı", "yalıtım"],
            "finishing": ["seramik", "boya", "elektrik malzemesi", "tesisat"],
        }

        timeline = []

        for task in tasks:
            task_id = task["id"]

            if "foundation" in task_id or "excavation" in task_id:
                materials = material_types["structural"]
                lead_time = 14
            elif "walls" in task_id or "roof" in task_id:
                materials = material_types["structural"] + material_types["enclosure"]
                lead_time = 21
            elif "windows" in task_id or "doors" in task_id:
                materials = material_types["enclosure"]
                lead_time = 28
            elif "flooring" in task_id or "painting" in task_id:
                materials = material_types["finishing"]
                lead_time = 7
            else:
                materials = []
                lead_time = 0

            if materials:
                delivery_date = datetime.fromisoformat(task["start_date"])
                order_date = delivery_date - timedelta(days=lead_time)
                timeline.append(
                    {
                        "task": task["name"],
                        "materials": materials,
                        "order_by": order_date.isoformat(),
                        "deliver_by": delivery_date.isoformat(),
                        "lead_time_days": lead_time,
                        "urgency": "high" if lead_time > 21 else "medium",
                    }
                )

        key_advice = [
            {
                "material": "Çimento ve Demir",
                "advice": "İlk 2 hafta içinde sipariş edin. Fiyat dalgalanmasına karşı erken alım düşünün.",
                "priority": "high",
                "estimated_cost": "Proje maliyetinin %25-30'u",
            },
            {
                "material": "Pencere ve Kapı",
                "advice": "Üretim süresi uzun (3-4 hafta). Erken ölçü alıp sipariş verin.",
                "priority": "high",
                "estimated_cost": "Proje maliyetinin %15-20'si",
            },
            {
                "material": "Seramik ve Boya",
                "advice": "Son 1 ayda sipariş edilebilir. Renk/seri seçimlerini erken netleştirin.",
                "priority": "medium",
                "estimated_cost": "Proje maliyetinin %10-15'i",
            },
        ]

        return {
            "timeline": timeline,
            "key_advice": key_advice,
            "recommendations": [
                "Malzemeleri parti parti alın, depolama maliyetinden kaçının",
                "Uzun lead time’lı ürünleri (kapı, pencere) en erken sipariş edin",
                "Nakit akışınıza göre ödeme planı yapın",
            ],
        }

    def _calc_total_duration_days(self, tasks: List[Dict]) -> int:
        if not tasks:
            return 0
        start = min(datetime.fromisoformat(t["start_date"]) for t in tasks)
        end = max(datetime.fromisoformat(t["end_date"]) for t in tasks)
        return (end - start).days + 1
