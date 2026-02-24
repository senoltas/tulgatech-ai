from typing import List, Dict, Tuple
import math
from collections import Counter

import ezdxf


class ProjectReader:
    def __init__(self):
        self.scale = 1.0  # Varsayılan ölçek (drawing units -> metre)
        self.scale_confidence = 0.0
        self.detected_elements = []
        self.warnings = []

    def read_dxf(self, file_path: str) -> Dict:
        """DXF dosyasını oku ve temel geometrileri çıkar"""

        # 1) Dosya tipi kontrolü
        if not file_path.lower().endswith(".dxf"):
            raise ValueError("Sadece DXF dosyaları destekleniyor")

        # 2) Layer analizi
        layers_analysis = self._analyze_layers(file_path)

        # 3) Geometrik elemanları topla
        elements = self._extract_geometric_elements(file_path)

        # 4) Ölçek tespiti (kritik)
        self._detect_scale(elements)

        # 5) Mimari elemanları tanıma
        architectural_elements = self._identify_architectural_elements(elements)

        return {
            "elements": elements,
            "architectural": architectural_elements,
            "layers_analysis": layers_analysis,
            "scale": self.scale,
            "scale_confidence": self.scale_confidence,
            "warnings": self.warnings,
            "success": True if self.scale_confidence > 0.3 else False,
        }

    def _analyze_layers(self, file_path) -> Dict:
        """DXF layer'larını analiz et (basit)"""
        layer_categories = {
            "walls": ["DUVAR", "WALL", "ÇİZGİ", "MİMARİ"],
            "doors": ["KAPI", "DOOR", "GEÇİŞ"],
            "windows": ["PENCERE", "WINDOW", "CAM"],
            "text": ["YAZI", "TEXT", "NOT", "METİN"],
            "dimension": ["ÖLÇÜ", "DIMENSION", "ÖLÇEK"],
        }

        try:
            doc = ezdxf.readfile(file_path)
            layers = [layer.dxf.name for layer in doc.layers]
        except Exception as e:
            self.warnings.append(f"Layer okuma hatası: {e}")
            layers = []

        detected = []
        for lname in layers:
            up = (lname or "").upper()
            for cat, keys in layer_categories.items():
                if any(k in up for k in keys):
                    detected.append({"layer": lname, "category": cat})
                    break

        return {"detected": detected, "suggested_categories": layer_categories}

    def _extract_geometric_elements(self, file_path: str) -> Dict:
        """ezdxf ile modelspace'ten geometrileri çıkar"""
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        elements = {
            "lines": [],
            "polylines": [],
            "circles": [],
            "texts": [],
            "dimensions": [],
            "layers": [],
            "bounds": {
                "min_x": float("inf"),
                "min_y": float("inf"),
                "max_x": float("-inf"),
                "max_y": float("-inf"),
            },
        }

        layer_set = set()

        def update_bounds(x: float, y: float):
            b = elements["bounds"]
            b["min_x"] = min(b["min_x"], x)
            b["min_y"] = min(b["min_y"], y)
            b["max_x"] = max(b["max_x"], x)
            b["max_y"] = max(b["max_y"], y)

        for e in msp:
            et = e.dxftype()
            layer = getattr(e.dxf, "layer", None)
            if layer:
                layer_set.add(layer)

            # LINE
            if et == "LINE":
                start = (float(e.dxf.start.x), float(e.dxf.start.y))
                end = (float(e.dxf.end.x), float(e.dxf.end.y))
                elements["lines"].append({"start": start, "end": end, "layer": layer})
                update_bounds(*start)
                update_bounds(*end)

            # LWPOLYLINE
            elif et == "LWPOLYLINE":
                pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
                closed = bool(e.closed)
                elements["polylines"].append(
                    {"points": pts, "closed": closed, "layer": layer}
                )
                for x, y in pts:
                    update_bounds(x, y)

            # POLYLINE (eski tip)
            elif et == "POLYLINE":
                pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in e.vertices]
                closed = bool(e.is_closed)
                elements["polylines"].append(
                    {"points": pts, "closed": closed, "layer": layer}
                )
                for x, y in pts:
                    update_bounds(x, y)

            # CIRCLE
            elif et == "CIRCLE":
                center = (float(e.dxf.center.x), float(e.dxf.center.y))
                radius = float(e.dxf.radius)
                elements["circles"].append(
                    {"center": center, "radius": radius, "layer": layer}
                )
                # bounds approx
                update_bounds(center[0] - radius, center[1] - radius)
                update_bounds(center[0] + radius, center[1] + radius)

            # TEXT / MTEXT
            elif et in ("TEXT", "MTEXT"):
                if et == "TEXT":
                    content = str(e.dxf.text)
                    ins = (float(e.dxf.insert.x), float(e.dxf.insert.y))
                else:
                    content = str(e.text)
                    ins = (float(e.dxf.insert.x), float(e.dxf.insert.y))
                elements["texts"].append(
                    {"content": content, "insert": ins, "layer": layer}
                )
                update_bounds(*ins)

            # DIMENSION (ölçek yakalamaya yardım)
            elif et == "DIMENSION":
                dim = {"layer": layer}
                # measurement: ezdxf bazı dimension tiplerinde render sonrası çıkar
                # Basit yaklaşım: varsa 'actual_measurement' / 'measurement' alanlarını dene
                measurement = None
                for attr in ("actual_measurement", "measurement"):
                    measurement = getattr(e, attr, None)
                    if measurement is not None:
                        break

                text_value = None
                try:
                    # dimension text override olabilir
                    raw = getattr(e.dxf, "text", "") or ""
                    if raw:
                        text_value = raw
                except Exception:
                    pass

                if measurement is not None:
                    try:
                        dim["measurement"] = float(measurement)
                    except Exception:
                        pass
                if text_value is not None:
                    dim["text_value"] = str(text_value)

                elements["dimensions"].append(dim)

        elements["layers"] = sorted(list(layer_set))

        # bounds hiç güncellenmediyse saçma değerleri temizle
        b = elements["bounds"]
        if b["min_x"] == float("inf"):
            elements["bounds"] = None

        return elements

    def _detect_scale(self, elements: Dict) -> None:
        """Proje ölçeğini tespit et (çoklu yöntem)"""
        scale_candidates = []

        # YÖNTEM 1: Ölçü çizgilerinden (dimension)
        if elements.get("dimensions"):
            for dim in elements["dimensions"]:
                if dim.get("measurement") and dim.get("text_value"):
                    try:
                        text_value = float(str(dim["text_value"]).replace(",", "."))
                        drawing_length = float(dim["measurement"])
                        if drawing_length > 0:
                            scale = text_value / drawing_length
                            scale_candidates.append(scale)
                    except Exception:
                        pass

        # YÖNTEM 2: Metinlerden (örn: "1/50")
        for text in elements.get("texts", []):
            text_content = text.get("content", "").lower()
            if "1/" in text_content:
                try:
                    parts = text_content.split("1/")
                    if len(parts) > 1:
                        scale_val = float(parts[1].split()[0].replace(",", "."))
                        scale = 1.0 / scale_val
                        scale_candidates.append(scale)
                except Exception:
                    pass

        # YÖNTEM 3: “en uzun çizgi” heuristiği (çok kaba, ama bazen işe yarar)
        if elements.get("lines"):
            longest_line = max(elements["lines"], key=lambda x: self._calculate_length(x))
            line_length = self._calculate_length(longest_line)
            if line_length > 0:
                # yaklaşık 10m duvar varsayımı
                scale_candidates.append(10.0 / line_length)

        if scale_candidates:
            rounded = [round(s, 6) for s in scale_candidates if s and s > 0]
            counts = Counter(rounded)
            if counts:
                best_scale = max(counts.items(), key=lambda x: x[1])[0]
                self.scale = float(best_scale)
                self.scale_confidence = min(0.9, len(scale_candidates) / 10)
            else:
                self.scale = 1.0
                self.scale_confidence = 0.1
                self.warnings.append("Ölçek tespit edilemedi. Varsayılan: 1.0")
        else:
            self.scale = 1.0
            self.scale_confidence = 0.0
            self.warnings.append("ÖLÇEK BULUNAMADI! Lütfen manuel girin.")

    def _identify_architectural_elements(self, elements: Dict) -> Dict:
        """Geometrik elemanlardan mimari bileşenleri tanı"""
        architectural = {
            "potential_walls": [],
            "potential_doors": [],
            "potential_windows": [],
            "spaces": [],
        }

        # 1) Duvar: 1m+ çizgiler
        for line in elements.get("lines", []):
            length = self._calculate_length(line) * self.scale
            if length > 1.0:
                architectural["potential_walls"].append(
                    {
                        "line": line,
                        "length_m": length,
                        "confidence": 0.7 if length > 2.0 else 0.4,
                    }
                )

        # 2) Kapı: 0.7m - 1.1m arası çizgiler
        for line in elements.get("lines", []):
            length = self._calculate_length(line) * self.scale
            if 0.7 < length < 1.1:
                architectural["potential_doors"].append(
                    {"line": line, "width_m": length, "confidence": 0.6}
                )

        # 3) Oda: kapalı poliline ve 5-50 m²
        for polyline in elements.get("polylines", []):
            if polyline.get("closed", False):
                area = self._calculate_polygon_area(polyline["points"]) * (self.scale ** 2)
                if 5 < area < 50:
                    architectural["spaces"].append(
                        {"polyline": polyline, "area_m2": area, "confidence": 0.8}
                    )

        return architectural

    def _calculate_length(self, line: Dict) -> float:
        """Çizgi uzunluğunu hesapla"""
        x1, y1 = line.get("start", (0.0, 0.0))
        x2, y2 = line.get("end", (0.0, 0.0))
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _calculate_polygon_area(self, points: List[Tuple[float, float]]) -> float:
        """Çokgen alanını hesapla (shoelace)"""
        if len(points) < 3:
            return 0.0
        area = 0.0
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0
