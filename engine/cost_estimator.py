"""
Maliyet Tahmin Motoru
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

from engine.quantity_models import QuantityItem


class CostEstimator:
    """Maliyet tahmin motoru"""

    def __init__(self, price_database: Optional[str] = None):
        self.base_dir = Path(__file__).resolve().parents[1]   # tulgatech_ai kök
        self.data_dir = self.base_dir / "data"
        self.price_db = self._load_price_database(price_database)
        self.currency = "TRY"
        self.waste_factors = {
            "material": 1.10,  # %10 fire
            "labor": 1.30,     # %30 işçilik
            "overhead": 1.15,  # %15 genel gider
        }

    def _load_price_database(self, db_path: Optional[str] = None) -> Dict:
        """Fiyat veritabanını yükle"""

        default_prices = {
            "wall_area": {
                "description": "Duvar m² (işçilik+malzeme)",
                "unit": "m²",
                "price": 250.0,
                "category": "construction",
                "source": "default",
                "valid_until": "2024-12-31",
            },
            "floor_area": {
                "description": "Zemin kaplama m²",
                "unit": "m²",
                "price": 300.0,
                "category": "finishing",
                "source": "default",
            },
            "paint_area": {
                "description": "Boya m² (2 kat)",
                "unit": "m²",
                "price": 80.0,
                "category": "finishing",
                "source": "default",
            },
            "door_unit": {
                "description": "Kapı (malzeme+işçilik)",
                "unit": "adet",
                "price": 2500.0,
                "category": "carpentry",
                "source": "default",
            },
            "window_unit": {
                "description": "Pencere (PVC çift cam)",
                "unit": "adet",
                "price": 4000.0,
                "category": "carpentry",
                "source": "default",
            },
            "lighting_unit": {
                "description": "Aydınlatma armatürü",
                "unit": "adet",
                "price": 500.0,
                "category": "electrical",
                "source": "default",
            },
            "brutto_area": {
                "description": "Brüt inşaat m² (toplam)",
                "unit": "m²",
                "price": 8000.0,
                "category": "construction",
                "source": "default",
            },
        }

        # 1) Kullanıcı path verdiyse onu dene
        if db_path:
            p = Path(db_path)
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        custom_prices = json.load(f)
                    default_prices.update(custom_prices)
                    return default_prices
                except Exception:
                    pass

        # 2) data/prices/custom_prices.json varsa onu dene
        fallback = self.data_dir / "prices" / "custom_prices.json"
        if fallback.exists():
            try:
                with open(fallback, "r", encoding="utf-8") as f:
                    custom_prices = json.load(f)
                default_prices.update(custom_prices)
            except Exception:
                pass

        return default_prices

    def estimate(self, quantities: List[Union[QuantityItem, Dict]]) -> Dict:
        """Maliyet tahmini yap (QuantityItem veya dict kabul eder)"""

        cost_items = []
        total_cost = 0.0

        for item in quantities:
            cost_item = self._estimate_item_cost(item)
            if cost_item:
                cost_items.append(cost_item)
                total_cost += float(cost_item["total_cost"])

        scenarios = self._create_scenarios(total_cost, len(cost_items))

        return {
            "currency": self.currency,
            "total_cost": round(total_cost, 2),
            "cost_items": cost_items,
            "scenarios": scenarios,
            "breakdown": self._create_cost_breakdown(cost_items),
            "assumptions": {
                "waste_factors": self.waste_factors,
                "price_source": "default_database_or_custom",
                "calculation_date": datetime.now().isoformat(),
            },
        }

    def _estimate_item_cost(self, item: Union[QuantityItem, Dict]) -> Optional[Dict]:
        """Tekil metraj kalemi maliyeti"""

        # QuantityItem mı dict mi?
        if isinstance(item, dict):
            item_id = item.get("id", "")
            item_name = item.get("name", "")
            item_value = float(item.get("value", 0) or 0)
            item_unit = item.get("unit", "")
            item_conf = float(item.get("confidence", 0) or 0)
            item_cat = item.get("category", "")
        else:
            item_id = item.id
            item_name = item.name
            item_value = float(item.value)
            item_unit = item.unit
            item_conf = float(item.confidence)
            item_cat = item.category

        price_key = self._find_matching_price(item_name, item_cat)
        if not price_key:
            return None

        price_info = self.price_db[price_key]
        unit_price = float(price_info["price"])

        material_cost = item_value * unit_price
        total_cost = material_cost * self.waste_factors["material"]

        # açıklamada labor geçmiyorsa labor+overhead uygula
        if "labor" not in str(price_info.get("description", "")).lower():
            total_cost *= self.waste_factors["labor"] * self.waste_factors["overhead"]

        return {
            "quantity_id": item_id,
            "name": item_name,
            "quantity": item_value,
            "unit": item_unit,
            "unit_price": unit_price,
            "material_cost": round(material_cost, 2),
            "total_cost": round(total_cost, 2),
            "price_key": price_key,
            "confidence": round(item_conf * 0.9, 3),
            "category": price_info.get("category", "unknown"),
            "source": price_info.get("source", "default"),
        }

    def _find_matching_price(self, item_name: str, item_category: str) -> Optional[str]:
        """Metraj kalemine uygun fiyat anahtarını bul"""

        name = (item_name or "").lower()

        name_mappings = {
            "duvar": "wall_area",
            "zemin": "floor_area",
            "döşeme": "floor_area",
            "boya": "paint_area",
            "kapı": "door_unit",
            "pencere": "window_unit",
            "aydınlatma": "lighting_unit",
            "brüt": "brutto_area",
        }

        for keyword, price_key in name_mappings.items():
            if keyword in name:
                return price_key

        # Kategori fallback
        if item_category == "area":
            if "alan" in name:
                return "brutto_area"
        return None

    def _create_scenarios(self, base_cost: float, item_count: int) -> Dict:
        """Alternatif maliyet senaryoları oluştur"""

        return {
            "economy": {
                "description": "Ekonomik Seçenek",
                "cost_factor": 0.75,
                "total_cost": round(base_cost * 0.75, 2),
                "savings": round(base_cost * 0.25, 2),
                "features": ["Standart malzeme", "Yerli ürünler", "Temel işçilik"],
            },
            "standard": {
                "description": "Standart Seçenek",
                "cost_factor": 1.00,
                "total_cost": round(base_cost, 2),
                "savings": 0,
                "features": ["Orta kalite", "Markalı ürünler", "Deneyimli işçilik"],
            },
            "premium": {
                "description": "Premium Seçenek",
                "cost_factor": 1.40,
                "total_cost": round(base_cost * 1.40, 2),
                "savings": round(base_cost * -0.40, 2),
                "features": ["Yüksek kalite", "İthal ürünler", "Uzman işçilik", "Tasarım detayları"],
            },
            "phased": {
                "description": "Aşamalı İnşaat",
                "cost_factor": 1.00,
                "total_cost": round(base_cost, 2),
                "payment_schedule": self._create_payment_schedule(base_cost),
                "features": ["3 aşamada ödeme", "Nakit akışı", "Stok yönetimi"],
            },
        }

    def _create_payment_schedule(self, total_cost: float) -> List[Dict]:
        """Ödeme planı oluştur"""
        return [
            {
                "phase": "Başlangıç",
                "percentage": 30,
                "amount": round(total_cost * 0.30, 2),
                "timing": "İş başlangıcında",
                "description": "Malzeme temini avansı",
            },
            {
                "phase": "İlerleme",
                "percentage": 40,
                "amount": round(total_cost * 0.40, 2),
                "timing": "İşin %50'sinde",
                "description": "Kaba inşaat tamamlandığında",
            },
            {
                "phase": "Tamamlanma",
                "percentage": 30,
                "amount": round(total_cost * 0.30, 2),
                "timing": "Teslimatta",
                "description": "Son ödeme",
            },
        ]

    def _create_cost_breakdown(self, cost_items: List[Dict]) -> Dict:
        """Maliyet dağılımı oluştur"""

        categories: Dict[str, Dict] = {}

        for item in cost_items:
            category = item.get("category", "other")
            if category not in categories:
                categories[category] = {"total_cost": 0.0, "items": [], "percentage": 0.0}

            categories[category]["total_cost"] += float(item["total_cost"])
            categories[category]["items"].append({"name": item["name"], "cost": float(item["total_cost"])})

        total = sum(cat["total_cost"] for cat in categories.values()) if categories else 0.0

        for cat in categories.values():
            cat["percentage"] = (cat["total_cost"] / total) * 100 if total > 0 else 0.0
            cat["total_cost"] = round(cat["total_cost"], 2)

        most_expensive = None
        if categories:
            most_expensive = max(categories.items(), key=lambda x: x[1]["total_cost"])[0]

        return {
            "by_category": categories,
            "total_cost": round(total, 2),
            "most_expensive_category": most_expensive,
        }

    def update_prices(self, new_prices: Dict) -> None:
        """Fiyatları güncelle ve data/prices/custom_prices.json'a yaz"""
        self.price_db.update(new_prices)

        price_file = self.data_dir / "prices" / "custom_prices.json"
        price_file.parent.mkdir(parents=True, exist_ok=True)

        with open(price_file, "w", encoding="utf-8") as f:
            json.dump(self.price_db, f, indent=2, ensure_ascii=False)
