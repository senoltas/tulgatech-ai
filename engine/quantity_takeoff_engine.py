from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from engine.quantity_models import QuantityItem, Assumption, ExtractionMethod


class QuantityTakeoffEngine:
    """
    Metraj Motoru

    - Varsayımlar öncelik sırası:
      1) default_assumptions (kod içi)
      2) config/assumptions.json (varsa)
      3) __init__(assumptions=...) (runtime override)
    """

    def __init__(self, assumptions: Dict[str, Any] | None = None):
        # 1) Kod içi varsayılanlar (internal anahtarlar)
        self.default_assumptions: Dict[str, Any] = {
            "wall_thickness": 0.25,         # m
            "wall_height": 3.0,             # m
            "door_width": 0.90,             # m
            "door_height": 2.10,            # m
            "window_height": 1.50,          # m
            "paint_waste_factor": 0.15,     # 0.15 = %15
            "plaster_thickness": 0.02,      # m
            "flooring_waste": 0.10,         # 0.10 = %10
            "window_area_deduction_ratio": 0.15,  # 0.15 = %15
        }

        # 2) config/assumptions.json oku ve uygula
        file_assumptions = self._load_assumptions_file()
        if file_assumptions:
            self.default_assumptions.update(file_assumptions)

        # 3) runtime override
        if assumptions:
            self.default_assumptions.update(assumptions)

        self.quantity_items: List[QuantityItem] = []

    # -------------------------
    # Assumption loading
    # -------------------------
    def _load_assumptions_file(self) -> Dict[str, Any]:
        """
        config/assumptions.json dosyasını okur.

        JSON'da isimler bazen farklı olabilir (floor_waste vs flooring_waste gibi).
        Bu yüzden internal anahtarlara map ediyoruz.
        """
        path = Path(__file__).resolve().parents[1] / "config" / "assumptions.json"
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            print(f"⚠️ assumptions.json okunamadı: {e}")
            return {}

        # JSON -> internal mapping
        # (senin JSON örneğinle uyumlu)
        mapping = {
            "floor_waste": "flooring_waste",
            "paint_waste": "paint_waste_factor",
        }

        normalized: Dict[str, Any] = {}
        for k, v in (raw or {}).items():
            internal_k = mapping.get(k, k)
            normalized[internal_k] = v

        # Tip güvenliği: sayısal beklediklerimiz
        numeric_keys = {
            "wall_thickness",
            "wall_height",
            "door_width",
            "door_height",
            "window_width",
            "window_height",
            "flooring_waste",
            "paint_waste_factor",
            "plaster_thickness",
            "window_area_deduction_ratio",
        }
        for nk in list(normalized.keys()):
            if nk in numeric_keys:
                try:
                    normalized[nk] = float(normalized[nk])
                except Exception:
                    # bozuk değer varsa ignore et
                    normalized.pop(nk, None)

        return normalized

    def _getf(self, key: str, default: float) -> float:
        try:
            return float(self.default_assumptions.get(key, default))
        except Exception:
            return float(default)

    # -------------------------
    # Public API
    # -------------------------
    def calculate_from_architecture(self, arch_data: Dict, scale: float) -> List[QuantityItem]:
        """Mimari veriden metraj hesapla"""
        self.quantity_items = []
        items: List[QuantityItem] = []

        # 1) BRÜT ALAN
        brutto_area = self._calculate_brutto_area(arch_data, scale)
        items.append(brutto_area)
        self.quantity_items.append(brutto_area)  # net alan fallback için erken ekliyoruz

        # 2) NET ALAN
        net_area = self._calculate_net_area(arch_data, scale)
        items.append(net_area)
        self.quantity_items.append(net_area)

        # 3) DUVAR METRAJI
        wall_items = self._calculate_walls(arch_data, scale)
        items.extend(wall_items)
        self.quantity_items.extend(wall_items)

        # 4) KAPI SAYIMI
        door_count = self._count_doors(arch_data)
        items.append(door_count)
        self.quantity_items.append(door_count)

        # 5) ZEMİN KAPLAMA
        flooring = self._calculate_flooring()
        items.append(flooring)
        self.quantity_items.append(flooring)

        # 6) BOYA ALANI
        paint_area = self._calculate_paint_area(wall_items, door_count)
        items.append(paint_area)
        self.quantity_items.append(paint_area)

        return items

    # -------------------------
    # Calculations
    # -------------------------
    def _calculate_brutto_area(self, arch_data: Dict, scale: float) -> QuantityItem:
        """Binanın brüt alanını hesapla (bounding box)"""
        all_points = []
        for wall in arch_data.get("potential_walls", []):
            s = wall.get("start")
            e = wall.get("end")
            if s and e:
                all_points.append(s)
                all_points.append(e)

        if len(all_points) < 3:
            area = 0.0
            confidence = 0.1
            method = ExtractionMethod.USER_CORRECTION
            warnings = ["Yeterli duvar verisi yok"]
        else:
            xs = [p[0] for p in all_points]
            ys = [p[1] for p in all_points]
            width = (max(xs) - min(xs)) * scale
            height = (max(ys) - min(ys)) * scale

            area = width * height
            confidence = 0.6 if len(arch_data.get("potential_walls", [])) > 4 else 0.3
            method = ExtractionMethod.WALL_LINE_DETECTION
            warnings = ["Brüt alan bounding box yöntemiyle hesaplandı"]

        assumptions = [
            Assumption("calculation_method", "bounding_box", "system", 0.7),
            Assumption("includes_exterior_walls", True, "default", 0.8),
        ]

        return QuantityItem(
            id="BRUTTO_AREA_001",
            name="Brüt İnşaat Alanı",
            category="area",
            value=area,
            unit="m²",
            extraction_method=method,
            confidence=confidence,
            assumptions=assumptions,
            source_data={"points_count": len(all_points)},
            warnings=warnings,
        )

    def _calculate_net_area(self, arch_data: Dict, scale: float) -> QuantityItem:
        """Net kullanım alanını hesapla - dominant layer whitelist + alan filtreleri + fallback"""

        spaces = arch_data.get("spaces", []) or []

        MIN_ROOM_AREA_M2 = 5.0
        MAX_ROOM_AREA_M2 = 80.0

        # 1) Dominant layer tabanlı filtre (test_2.dxf için)
        # - AKS ve DETAIL layer'ları oda değildir -> at
        # - DUVAR / DÖŞEME gibi layer'lar daha anlamlı -> tut
        BAD_DOM_LAYER_TOKENS = [
            "AKS", "AXIS", "GRID",          # aks / grid
            "DETAIL", "DETL", "DET",        # detay
            "THIN", "CENTER", "DIM", "TEXT" # ölçü/merkez/yazı
        ]

        # Whitelist: "oda üretmesi muhtemel" ana layerlar
        # Buraya senin DXF'e göre hedef layerları yazıyoruz:
        GOOD_DOM_LAYER_TOKENS = [
            "DUVAR", "WALL", "MUR", "MURO",
            "DÖŞEME", "DOSEME", "FLOOR", "SLAB",
            "BBM-DUVAR", "BBM-DUVARIC", "BBM-DÖŞEME", "M-DÖŞEME"
        ]

        # 2) Eski layer filtre (tefriş/detay yakalamak için, space.layer alanı için)
        BAD_LAYER_TOKENS = [
            "proiezio", "proiezioni", "projection", "project",
            "mobilya", "furniture", "arredi", "tefriş", "tefris",
            "kesit", "sezioni", "section",
            "detail", "detay",
            "koltuk", "sofa", "chair", "tavolo", "table",
        ]

        def _norm(s: str) -> str:
            return (s or "").upper()

        real_rooms = []
        for sp in spaces:
            if not isinstance(sp, dict):
                continue

            area = float(sp.get("area_m2", 0) or 0)
            layer = str(sp.get("layer", "") or "").lower()
            dom = _norm(str(sp.get("dominant_wall_layer", "") or ""))

            # alan bandı
            if area < MIN_ROOM_AREA_M2 or area > MAX_ROOM_AREA_M2:
                continue

            # space.layer üzerinde klasik çöp filtre
            if any(t in layer for t in BAD_LAYER_TOKENS):
                continue

            # dominant layer yoksa (eski dosyalar) -> şimdilik kabul etme
            if not dom or dom == "NONE":
                continue

            # dominant layer blacklist
            if any(tok in dom for tok in BAD_DOM_LAYER_TOKENS):
                continue

            # dominant layer whitelist: en az bir iyi token içermeli
            if not any(tok in dom for tok in GOOD_DOM_LAYER_TOKENS):
                continue

            real_rooms.append(sp)

        total_all = sum(float(sp.get("area_m2", 0) or 0) for sp in spaces if isinstance(sp, dict))

        if real_rooms:
            total = sum(float(r.get("area_m2", 0) or 0) for r in real_rooms)

            # hangi dominant layerlardan geldiğini raporla (debug/şeffaflık)
            from collections import Counter
            dom_counts = Counter([str(r.get("dominant_wall_layer", "") or "") for r in real_rooms])

            return QuantityItem(
                id="NET_AREA_001",
                name="Net Kullanım Alanı",
                category="area",
                value=round(total, 2),
                unit="m²",
                extraction_method=ExtractionMethod.WALL_LINE_DETECTION,  # inferred + layer filtered
                confidence=0.7,
                assumptions=[
                    Assumption("min_room_area_m2", MIN_ROOM_AREA_M2, "system", 0.8),
                    Assumption("max_room_area_m2", MAX_ROOM_AREA_M2, "system", 0.7),
                    Assumption("dominant_layer_whitelist", True, "system", 0.75),
                    Assumption("dominant_layer_blacklist", True, "system", 0.75),
                    Assumption("layer_filtering", True, "system", 0.7),
                ],
                source_data={
                    "spaces_count": len(spaces),
                    "rooms_count": len(real_rooms),
                    "total_all_closed_m2": round(total_all, 2),
                    "dominant_layer_counts": dom_counts.most_common(10),
                },
                warnings=[
                    f"{len(real_rooms)} oda kabul edildi ({MIN_ROOM_AREA_M2}–{MAX_ROOM_AREA_M2} m², dominant layer filtreli).",
                    f"Ham kapanan alan toplamı (filtre yok): {round(total_all, 2)} m²",
                ],
            )

        # fallback: brüt * 0.85
        brutto_item = next((i for i in self.quantity_items if i.name == "Brüt İnşaat Alanı"), None)
        if brutto_item:
            total = float(brutto_item.value) * 0.85
            return QuantityItem(
                id="NET_AREA_001",
                name="Net Kullanım Alanı",
                category="area",
                value=round(total, 2),
                unit="m²",
                extraction_method=ExtractionMethod.USER_CORRECTION,
                confidence=max(0.05, float(brutto_item.confidence) * 0.7),
                assumptions=[Assumption("net_to_brut_ratio", 0.85, "system", 0.7)],
                source_data={"spaces_count": len(spaces), "rooms_count": 0, "total_all_closed_m2": round(total_all, 2)},
                warnings=["Oda konturu güvenilir bulunamadı. Brüt alanın %85'i net kabul edildi."],
            )

        return QuantityItem(
            id="NET_AREA_001",
            name="Net Kullanım Alanı",
            category="area",
            value=0.0,
            unit="m²",
            extraction_method=ExtractionMethod.USER_CORRECTION,
            confidence=0.1,
            assumptions=[Assumption("net_to_brut_ratio", 0.85, "default", 0.7)],
            source_data={"spaces_count": len(spaces), "rooms_count": 0, "total_all_closed_m2": round(total_all, 2)},
            warnings=["Net alan hesaplanamadı (brüt alan da yok)."],
        )

    def _calculate_walls(self, arch_data: Dict, scale: float) -> List[QuantityItem]:
        """Duvar metrajlarını hesapla"""
        wall_items: List[QuantityItem] = []
        wall_thickness = self._getf("wall_thickness", 0.25)
        wall_height = self._getf("wall_height", 3.0)

        exterior_walls = []
        interior_walls = []

        for wall in arch_data.get("potential_walls", []):
            length = float(wall.get("length_m", 0) or 0)
            if length > 4.0:
                exterior_walls.append(wall)
            else:
                interior_walls.append(wall)

        exterior_length = sum(float(w.get("length_m", 0) or 0) for w in exterior_walls) if exterior_walls else 0.0
        exterior_area = exterior_length * wall_height

        wall_items.append(
            QuantityItem(
                id="WALL_EXT_001",
                name="Dış Duvar Alanı",
                category="area",
                value=exterior_area,
                unit="m²",
                extraction_method=ExtractionMethod.WALL_LINE_DETECTION,
                confidence=0.6 if len(exterior_walls) > 0 else 0.3,
                assumptions=[
                    Assumption("wall_thickness", wall_thickness, "default", 0.8),
                    Assumption("wall_height", wall_height, "default", 0.7),
                ],
                source_data={"wall_count": len(exterior_walls), "total_length": exterior_length},
                warnings=[],
            )
        )

        interior_length = sum(float(w.get("length_m", 0) or 0) for w in interior_walls) if interior_walls else 0.0
        interior_area = interior_length * wall_height

        wall_items.append(
            QuantityItem(
                id="WALL_INT_001",
                name="İç Duvar Alanı",
                category="area",
                value=interior_area,
                unit="m²",
                extraction_method=ExtractionMethod.WALL_LINE_DETECTION,
                confidence=0.5,
                assumptions=[
                    Assumption("wall_thickness", wall_thickness * 0.8, "default", 0.7),
                    Assumption("wall_height", wall_height, "default", 0.7),
                ],
                source_data={"wall_count": len(interior_walls), "total_length": interior_length},
                warnings=["İç duvar kalınlığı dış duvarın %80'i kabul edildi"],
            )
        )

        return wall_items

    def _count_doors(self, arch_data: Dict) -> QuantityItem:
        """Kapı sayısını hesapla"""
        detected = len(arch_data.get("potential_doors", []))
        door_count = detected

        if door_count == 0:
            net_area_item = next((i for i in self.quantity_items if i.name == "Net Kullanım Alanı"), None)
            if net_area_item and float(net_area_item.value) > 0:
                door_count = max(1, int(float(net_area_item.value) / 25))
                confidence = 0.3
                method = ExtractionMethod.USER_CORRECTION
                warnings = ["Kapı tespit edilemedi. 25m²'ye 1 kapı varsayıldı."]
            else:
                confidence = 0.1
                method = ExtractionMethod.USER_CORRECTION
                warnings = ["Kapı tespit edilemedi"]
        else:
            confidence = 0.7
            method = ExtractionMethod.WALL_LINE_DETECTION
            warnings = []

        door_width = self._getf("door_width", 0.9)
        door_height = self._getf("door_height", 2.1)

        return QuantityItem(
            id="DOOR_COUNT_001",
            name="Kapı Sayısı",
            category="count",
            value=float(door_count),
            unit="adet",
            extraction_method=method,
            confidence=confidence,
            assumptions=[
                Assumption("door_width", door_width, "default", 0.8),
                Assumption("door_height", door_height, "default", 0.8),
            ],
            source_data={"detected_doors": detected},
            warnings=warnings,
        )

    def _calculate_flooring(self) -> QuantityItem:
        """Zemin kaplama alanını hesapla (net alan referansı)"""
        net_area_item = next((i for i in self.quantity_items if i.name == "Net Kullanım Alanı"), None)

        if net_area_item:
            net_area = float(net_area_item.value)
            confidence = float(net_area_item.confidence) * 0.9
            method = ExtractionMethod.USER_CORRECTION
            warnings = ["Zemin kaplama = Net alan kabul edildi"]
        else:
            net_area = 0.0
            confidence = 0.1
            method = ExtractionMethod.USER_CORRECTION
            warnings = ["Net alan bulunamadı"]

        waste_factor = self._getf("flooring_waste", 0.10)
        total_area = net_area * (1 + waste_factor)

        return QuantityItem(
            id="FLOORING_001",
            name="Zemin Kaplama Alanı",
            category="area",
            value=total_area,
            unit="m²",
            extraction_method=method,
            confidence=confidence,
            assumptions=[
                Assumption("waste_factor", waste_factor, "default", 0.8),
                Assumption("includes_balcony", False, "default", 0.7),
            ],
            source_data={"net_area_reference": net_area_item.id if net_area_item else None},
            warnings=warnings,
        )

    def _calculate_paint_area(self, wall_items: List[QuantityItem], door_item: QuantityItem) -> QuantityItem:
        """Boya alanını hesapla"""
        total_wall_area = sum(float(item.value) for item in wall_items) if wall_items else 0.0

        door_width = self._getf("door_width", 0.9)
        door_height = self._getf("door_height", 2.1)
        door_area = float(door_item.value) * door_width * door_height

        paint_area = max(0.0, total_wall_area - door_area)

        waste_factor = self._getf("paint_waste_factor", 0.15)
        total_paint_area = paint_area * (1 + waste_factor)

        wall_confidence = (sum(float(item.confidence) for item in wall_items) / len(wall_items)) if wall_items else 0.0
        avg_confidence = (wall_confidence + float(door_item.confidence)) / 2

        window_deduction = self._getf("window_area_deduction_ratio", 0.15)

        return QuantityItem(
            id="PAINT_001",
            name="Boya Alanı",
            category="area",
            value=total_paint_area,
            unit="m²",
            extraction_method=ExtractionMethod.USER_CORRECTION,
            confidence=avg_confidence * 0.9,
            assumptions=[
                Assumption("paint_coats", 2, "default", 0.8),
                Assumption("waste_factor", waste_factor, "default", 0.7),
                Assumption("window_area_deduction_ratio", window_deduction, "default", 0.6),
            ],
            source_data={
                "wall_area": total_wall_area,
                "door_area": door_area,
                "wall_item_ids": [item.id for item in wall_items],
                "door_item_id": door_item.id,
            },
            warnings=[f"Pencere alanı indirimi %{window_deduction*100:.0f} varsayıldı"],
        )

    def export_to_json(self) -> str:
        """Metrajı JSON olarak dışa aktar"""
        n = len(self.quantity_items)
        avg_conf = (sum(float(item.confidence) for item in self.quantity_items) / n) if n else 0.0
        total_area = sum(float(item.value) for item in self.quantity_items if item.unit == "m²")

        output = {
            "timestamp": datetime.now().isoformat(),
            "assumptions_used": self.default_assumptions,  # audit trail
            "items": [item.to_dict() for item in self.quantity_items],
            "summary": {
                "total_items": n,
                "average_confidence": round(avg_conf, 3),
                "total_area_m2": round(total_area, 2),
            },
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
