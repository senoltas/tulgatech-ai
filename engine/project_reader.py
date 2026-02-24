import math
from typing import Any, Dict, List, Tuple

import ezdxf
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union, polygonize, snap
from shapely.strtree import STRtree


class ProjectReader:
    def __init__(self):
        self.scale: float = 1.0
        self.scale_confidence: float = 0.0
        self.warnings: List[str] = []

    # =================================================
    # MAIN ENTRY
    # =================================================
    def read_dxf(self, file_path: str) -> Dict[str, Any]:
        if not file_path.lower().endswith(".dxf"):
            raise ValueError("Sadece DXF desteklenir")

        elements = {
            "lines": [],
            "polylines": [],
            "circles": [],
            "texts": [],
            "dimensions": [],
        }

        # -------- DXF OKU --------
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        
        # --- CLUSTER NET AREA (pafta bazlı) ---
        clusters = self.extract_cluster_net_areas_from_msp(msp)

        # --- ELEMENT PARSE ---
        for e in msp:
            t = e.dxftype()

            # LINE
            if t == "LINE":
                s = e.dxf.start
                en = e.dxf.end
                elements["lines"].append(
                    {
                        "start": (float(s.x), float(s.y)),
                        "end": (float(en.x), float(en.y)),
                        "layer": getattr(e.dxf, "layer", None),
                    }
                )

            # LWPOLYLINE
            elif t == "LWPOLYLINE":
                pts = [(float(x), float(y)) for (x, y, *_r) in e.get_points()]
                elements["polylines"].append(
                    {
                        "points": pts,
                        "closed": bool(e.closed),
                        "layer": getattr(e.dxf, "layer", None),
                    }
                )
            # POLYLINE (old)
            elif t == "POLYLINE":
                pts = []
                try:
                    # ezdxf'te doğru kullanım genelde e.vertices() olur
                    for v in e.vertices():
                        p = v.dxf.location
                        pts.append((float(p.x), float(p.y)))
                except Exception:
                    # bazı dosyalarda vertices erişimi farklı olabilir
                    try:
                        for v in e.vertices:
                            p = v.dxf.location
                            pts.append((float(p.x), float(p.y)))
                    except Exception:
                        pass

                if pts:
                    elements["polylines"].append(
                        {
                            "points": pts,
                            "closed": bool(getattr(e, "is_closed", False)),
                            "layer": getattr(e.dxf, "layer", None),
                        }
                    )

            # CIRCLE
            elif t == "CIRCLE":
                c = e.dxf.center
                elements["circles"].append(
                    {
                        "center": (float(c.x), float(c.y)),
                        "radius": float(e.dxf.radius),
                        "layer": getattr(e.dxf, "layer", None),
                    }
                )

            # TEXT / MTEXT
            elif t in ("TEXT", "MTEXT"):
                pos = getattr(e.dxf, "insert", None)
                if pos:
                    x, y = float(pos.x), float(pos.y)
                else:
                    x, y = 0.0, 0.0

                try:
                    txt = e.plain_text() if t == "MTEXT" else str(e.dxf.text)
                except Exception:
                    txt = ""

                elements["texts"].append(
                    {
                        "content": txt,
                        "pos": (x, y),
                        "layer": getattr(e.dxf, "layer", None),
                    }
                )

        # -------- SCALE --------
        self._detect_scale(elements)
        # --- CLUSTER AREA -> m² ---
        for c in clusters:
            try:
                du2 = float(c.get("net_area_drawing_units2", 0.0) or 0.0)
                c["net_area_m2"] = round(du2 * (self.scale ** 2), 4)
            except Exception:
                c["net_area_m2"] = None
        # --- MAIN PLAN CLUSTER (en büyük, quality=ok) ---
        ok = [c for c in clusters if c.get("quality") == "ok" and c.get("net_area_m2") is not None]
        main_plan_cluster = max(ok, key=lambda x: x["net_area_m2"]) if ok else None
        
        # -------- ARCH --------
        architectural = self._extract_architecture(elements)
        
                # -------- SCALE --------
        self._detect_scale(elements)

        # clusters -> m² dönüşümü vs burada...

        # -------- ARCH --------
        architectural = self._extract_architecture(elements)

        # --- OVERRIDE architectural spaces with MAIN cluster spaces ---
        if main_plan_cluster and main_plan_cluster.get("spaces"):
            architectural["spaces_legacy"] = architectural.get("spaces", [])

            new_spaces = []
            for sp in main_plan_cluster["spaces"]:
                sp2 = dict(sp)
                du2 = float(sp2.get("area_draw2", 0.0) or 0.0)
                sp2["area_m2"] = round(du2 * (self.scale ** 2), 4)
                new_spaces.append(sp2)

            architectural["spaces"] = new_spaces
            architectural["spaces_source"] = "MAIN_CLUSTER_WALL_POLYGONIZE"

            architectural["spaces"] = self._label_spaces_from_wall_layers(
                architectural["spaces"],
                architectural.get("potential_walls", []),
                self.scale,
            )

        # --- ARCH SUMMARY from main cluster ---
        if main_plan_cluster:
            architectural["cluster_net_area_m2"] = main_plan_cluster.get("net_area_m2")
            architectural["cluster_spaces_count"] = main_plan_cluster.get("spaces_count")
            architectural["cluster_bbox_draw"] = main_plan_cluster.get("bbox")

        # --- QUANTITIES (A) ---
        quantities = []

        # sanity check: spaces toplamı (m²)
        space_sum_m2 = None
        try:
            space_sum_m2 = round(
                sum(float(s.get("area_m2", 0.0) or 0.0) for s in architectural.get("spaces", [])),
                4
            )
        except Exception:
            space_sum_m2 = None
            
        if main_plan_cluster and main_plan_cluster.get("net_area_m2") is not None:
            quantities.append({
                "code": "net_area_main_cluster_m2",
                "name": "Net Alan (Ana Pafta) (m²)",
                "value": float(main_plan_cluster["net_area_m2"]),
                "unit": "m^2",
                "source": "CLUSTER_WALL_POLYGONIZE",
                "meta": {
                    "cluster_id": main_plan_cluster.get("id"),
                    "spaces_count": main_plan_cluster.get("spaces_count"),
                    "bbox_draw": main_plan_cluster.get("bbox"),
                    "scale": self.scale,
                    "space_sum_m2": space_sum_m2,
                    "space_sum_diff_m2": (
                        round(space_sum_m2 - float(main_plan_cluster["net_area_m2"]), 4)
                        if space_sum_m2 is not None else None
                    ),
                    
                }
            })


        return {
            "elements": elements,
            "architectural": architectural,
            "clusters": clusters,
            "main_plan_cluster": main_plan_cluster,
            "scale": self.scale,
            "scale_confidence": self.scale_confidence,
            "warnings": self.warnings,
            "quantities": quantities,
            "success": True,
        }

    # =================================================
    # SCALE
    # =================================================
    def _detect_scale(self, elements: Dict[str, Any]):
        # şimdilik sabit
        self.scale = 0.5
        self.scale_confidence = 0.1
        self.warnings.append("Ölçek bulunamadı. Varsayılan 1/2 kullanıldı.")

    # =================================================
    # ARCHITECTURAL
    # =================================================
    def _extract_architecture(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        arch = {
            "potential_walls": [],
            "spaces": [],
            "potential_doors": [],
            "potential_windows": [],
        }

        scale = float(self.scale)

        # ---------- LINES ----------
        for ln in elements.get("lines", []):
            p1 = ln["start"]
            p2 = ln["end"]

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.hypot(dx, dy) * scale

            if length <= 0:
                continue

            arch["potential_walls"].append(
                {
                    "start": p1,
                    "end": p2,
                    "length_m": float(length),
                    "layer": ln.get("layer"),
                    "source": "LINE",
                }
            )

        # ---------- POLYLINES ----------
        for pl in elements.get("polylines", []):
            pts = pl.get("points", [])
            closed = pl.get("closed", False)

            if len(pts) < 2:
                continue

            if closed and len(pts) >= 3:
                area = self._polygon_area(pts)
                area_m2 = area * (scale**2)
                if area_m2 > 1:
                    arch["spaces"].append(
                        {
                            "area_m2": float(area_m2),
                            "layer": pl.get("layer"),
                            "source": "CLOSED_POLY",
                        }
                    )
            else:
                for i in range(len(pts) - 1):
                    p1 = pts[i]
                    p2 = pts[i + 1]
                    length = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * scale
                    if length <= 0:
                        continue
                    arch["potential_walls"].append(
                        {
                            "start": p1,
                            "end": p2,
                            "length_m": float(length),
                            "layer": pl.get("layer"),
                            "source": "POLY_SEG",
                        }
                    )

        # ---------- SPACE INFERENCE ----------
        if not arch.get("spaces"):
            inferred = self._infer_spaces_from_walls(arch.get("potential_walls", []), scale)
            if inferred:
                arch["spaces"] = inferred

        # ---------- LABELING (FAIL-SAFE) ----------
        if arch.get("spaces"):
            spaces_before = list(arch["spaces"])
            try:
                labeled = self._label_spaces_from_wall_layers(
                    arch["spaces"],
                    arch.get("potential_walls", []),
                    scale,
                )
                if labeled:
                    arch["spaces"] = labeled
                else:
                    arch["spaces"] = spaces_before
            except Exception as ex:
                arch["spaces"] = spaces_before
                self.warnings.append(f"Space labeling başarısız: {ex}")

        return arch

    def _label_spaces_from_wall_layers(self, spaces: list, potential_walls: list, scale: float) -> list:
        """
        Space'leri yakın duvar layer oylarına göre etiketler.
        Shapely 2 uyumlu STRtree query (indeks veya geometri dönebilir).
        """
        if not spaces or not potential_walls:
            return spaces or []

        wall_geoms: List[LineString] = []
        wall_layers: List[str] = []

        for w in potential_walls:
            if not isinstance(w, dict):
                continue

            s = w.get("start")
            e = w.get("end")
            if s is None or e is None:
                ln = (w or {}).get("line") or {}
                s = s or ln.get("start")
                e = e or ln.get("end")

            if not (isinstance(s, (list, tuple)) and isinstance(e, (list, tuple)) and len(s) >= 2 and len(e) >= 2):
                continue

            try:
                x1, y1 = float(s[0]), float(s[1])
                x2, y2 = float(e[0]), float(e[1])
            except Exception:
                continue

            if x1 == x2 and y1 == y2:
                continue

            layer = str(w.get("layer", "") or "")
            wall_geoms.append(LineString([(x1, y1), (x2, y2)]))
            wall_layers.append(layer)

        if not wall_geoms:
            return spaces

        tree = STRtree(wall_geoms)
        geom_id_to_idx = {id(g): i for i, g in enumerate(wall_geoms)}

        import re
        from collections import Counter

        def _floor_label_from_layer(layer: str) -> str:
            up = (layer or "").upper()
            if "BODRUM" in up or "BASEMENT" in up or "B-" in up:
                return "BODRUM"
            if "ZEMIN" in up or "GROUND" in up or "GND" in up:
                return "ZEMIN"
            if "ASMA" in up or "MEZZ" in up:
                return "ASMA"

            m = re.search(r"(KAT|FLOOR)\s*([0-9]+)", up)
            if m:
                return f"{m.group(1)}_{m.group(2)}"

            m = re.search(r"([0-9]+)\s*\.?\s*(KAT|FLOOR)", up)
            if m:
                return f"{m.group(2)}_{m.group(1)}"

            return "UNKNOWN"

        def _block_label_from_layer(layer: str) -> str:
            up = (layer or "").upper().strip()
            m = re.search(r"([A-Z])\s*[-_ ]?\s*(BLOK|BLOCK)", up)
            if m:
                return f"{m.group(1)}_BLOK"
            m = re.search(r"(BLOK|BLOCK)\s*[-_ ]?\s*([A-Z])", up)
            if m:
                return f"{m.group(2)}_BLOK"
            return "UNKNOWN"

        tol_draw = 0.10 / scale if scale and scale > 0 else 0.0

        labeled: List[dict] = []
        for sp in spaces:
            if not isinstance(sp, dict):
                labeled.append(sp)
                continue

            if "poly_bounds_draw" not in sp:
                labeled.append(sp)
                continue

            minx, miny, maxx, maxy = sp["poly_bounds_draw"]

            query_geom = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
            if tol_draw and tol_draw > 0:
                query_geom = query_geom.buffer(tol_draw)

            candidates = tree.query(query_geom)

            c = Counter()
            for cand in candidates:
                idx = None
                try:
                    idx = int(cand)
                except Exception:
                    idx = geom_id_to_idx.get(id(cand))

                if idx is None:
                    continue

                if 0 <= idx < len(wall_layers):
                    lyr = wall_layers[idx]
                    if lyr:
                        c[lyr] += 1

            if not c:
                labeled.append(sp)
                continue

            dominant_layer, _votes = c.most_common(1)[0]
            top5 = c.most_common(5)

            cx_draw, cy_draw = sp.get("poly_centroid_draw", (None, None))
            cx_m = (float(cx_draw) * scale) if cx_draw is not None else None
            cy_m = (float(cy_draw) * scale) if cy_draw is not None else None

            bbox_m = (
                round(minx * scale, 4),
                round(miny * scale, 4),
                round(maxx * scale, 4),
                round(maxy * scale, 4),
            )

            sp2 = dict(sp)
            sp2["dominant_wall_layer"] = dominant_layer
            sp2["layer_votes"] = top5
            sp2["centroid_m"] = (round(cx_m, 4), round(cy_m, 4)) if cx_m is not None and cy_m is not None else None
            sp2["bbox_m"] = bbox_m
            sp2["floor_label"] = _floor_label_from_layer(dominant_layer)
            sp2["block_label"] = _block_label_from_layer(dominant_layer)

            labeled.append(sp2)

        return labeled

    # =================================================
    # GEOM
    # =================================================
    def _polygon_area(self, pts: List[Tuple[float, float]]) -> float:
        area = 0.0
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0

    def _infer_spaces_from_walls(self, potential_walls: list, scale: float) -> list:
        lines: List[LineString] = []

        for w in (potential_walls or []):
            s = (w or {}).get("start")
            e = (w or {}).get("end")
            if s is None or e is None:
                ln = (w or {}).get("line") or {}
                s = s or ln.get("start")
                e = e or ln.get("end")

            if not (isinstance(s, (list, tuple)) and isinstance(e, (list, tuple)) and len(s) >= 2 and len(e) >= 2):
                continue

            try:
                x1, y1 = float(s[0]), float(s[1])
                x2, y2 = float(e[0]), float(e[1])
            except Exception:
                continue

            if x1 == x2 and y1 == y2:
                continue

            lines.append(LineString([(x1, y1), (x2, y2)]))

        if len(lines) < 10:
            return []

        merged = unary_union(lines)

        tol_draw = 0.02 / scale if scale and scale > 0 else 0.0
        if tol_draw and tol_draw > 0:
            try:
                merged = snap(merged, merged, tol_draw)
            except Exception:
                pass

        polys = list(polygonize(merged))
        if not polys:
            return []

        spaces: List[dict] = []
        for poly in polys:
            if not isinstance(poly, Polygon):
                continue

            area_draw = float(poly.area)
            area_m2 = area_draw * (scale**2)

            if area_m2 < 6.0:
                continue
            if area_m2 > 1000.0:
                continue

            c = poly.centroid
            minx, miny, maxx, maxy = poly.bounds

            spaces.append(
                {
                    "area_m2": round(area_m2, 4),
                    "confidence": 0.55,
                    "layer": "INFERRED_FROM_WALLS",
                    "source": "WALL_POLYGONIZE",
                    "poly_centroid_draw": (float(c.x), float(c.y)),
                    "poly_bounds_draw": (float(minx), float(miny), float(maxx), float(maxy)),
                }
            )

        spaces.sort(key=lambda x: x["area_m2"], reverse=True)
        return spaces[:50]

    @staticmethod
    def extract_cluster_net_areas_from_msp(msp):
        """
        INSERT yoğunluğuna göre pafta cluster bulur ve her cluster için polygonize ile net alan + space özetleri üretir.
        Return: list[dict]
        """
        from collections import defaultdict, deque, Counter
        from shapely.geometry import LineString, MultiLineString, box
        from shapely.ops import unary_union, polygonize

        # -------------------------------------------------
        # 1) INSERT points
        # -------------------------------------------------
        insert_pts = []
        for e in msp:
            if e.dxftype() != "INSERT":
                continue
            ip = e.dxf.insert
            insert_pts.append((float(ip.x), float(ip.y), str(e.dxf.name)))

        # -------------------------------------------------
        # 2) Grid buckets -> neighbor merge -> clusters
        # -------------------------------------------------
        CELL = 120.0
        MIN_BUCKET_N = 20
        MIN_CLUSTER_PTS = 80

        buckets = defaultdict(list)
        for x, y, name in insert_pts:
            gx = int(x // CELL)
            gy = int(y // CELL)
            buckets[(gx, gy)].append((x, y, name))

        active = {k for k, arr in buckets.items() if len(arr) >= MIN_BUCKET_N}

        def neighbors8(k):
            gx, gy = k
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    yield (gx + dx, gy + dy)

        visited = set()
        raw_cell_clusters = []
        for k in sorted(active):
            if k in visited:
                continue
            q = deque([k])
            visited.add(k)
            cells = []
            while q:
                cur = q.popleft()
                cells.append(cur)
                for nb in neighbors8(cur):
                    if nb in active and nb not in visited:
                        visited.add(nb)
                        q.append(nb)
            raw_cell_clusters.append(sorted(cells))

        cluster_defs = []
        for idx, cells in enumerate(raw_cell_clusters, 1):
            arr = []
            for ccell in cells:
                arr.extend(buckets[ccell])
            if len(arr) < MIN_CLUSTER_PTS:
                continue

            xs = [p[0] for p in arr]
            ys = [p[1] for p in arr]
            bbox = (min(xs), min(ys), max(xs), max(ys))

            cluster_defs.append(
                {"id": f"C{idx:02d}", "cells": cells, "bbox": bbox, "insert_count": len(arr)}
            )

        cluster_defs.sort(key=lambda c: c["insert_count"], reverse=True)

        # -------------------------------------------------
        # 3) Wall candidate line index
        # -------------------------------------------------
        POS = ["WALL", "MURO", "MUR", "DUVAR", "PARETE", "PERIM", "TRAMEZ", "KOLON", "COL", "COLUMN"]
        NEG = [
            "AX", "GRID", "ASSI", "ASSE", "MULLION", "INFISSO", "FURN", "ARRED", "DIM", "QUOTE", "TEXT", "HATCH",
            "SECTION", "SEZ", "DET", "DETAIL", "PROSP", "ELEV", "KOT", "AKS", "LIFT", "DETAILLINE"
        ]

        def layer_score(layer: str) -> int:
            if not layer:
                return -10
            up = layer.upper()
            s = 0
            for k in POS:
                if k in up:
                    s += 3
            for k in NEG:
                if k in up:
                    s -= 5
            return s

        def entity_to_lines(ent):
            t = ent.dxftype()
            out = []
            try:
                if t == "LINE":
                    a = ent.dxf.start
                    b = ent.dxf.end
                    out.append(LineString([(float(a.x), float(a.y)), (float(b.x), float(b.y))]))
                elif t == "LWPOLYLINE":
                    pts = [(float(x), float(y)) for x, y, *_ in ent.get_points()]
                    if len(pts) >= 2:
                        out.append(LineString(pts))
                elif t == "POLYLINE":
                    pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in ent.vertices()]
                    if len(pts) >= 2:
                        out.append(LineString(pts))
            except Exception:
                return []
            return out

        layer_scores = {}
        all_lines = []
        for e in msp:
            if e.dxftype() not in ("LINE", "LWPOLYLINE", "POLYLINE"):
                continue
            layer = str(getattr(e.dxf, "layer", "") or "")
            if layer not in layer_scores:
                layer_scores[layer] = layer_score(layer)
            for ln in entity_to_lines(e):
                all_lines.append((ln, layer))

        WALL_SCORE_MIN = 1
        wall_lines = [(ln, lay) for (ln, lay) in all_lines if layer_scores.get(lay, -10) >= WALL_SCORE_MIN]

        # -------------------------------------------------
        # 4) Cluster bbox -> pick lines -> polygonize -> area + spaces
        # -------------------------------------------------
        PAD = 20.0
        MIN_LINES = 50
        SPACE_LIMIT = 200

        results = []
        for c in cluster_defs:
            cid = c["id"]
            minx, miny, maxx, maxy = c["bbox"]
            region = box(minx - PAD, miny - PAD, maxx + PAD, maxy + PAD)

            picked = []
            picked_layers = Counter()

            for ln, lay in wall_lines:
                if not region.intersects(ln):
                    continue
                clipped = ln.intersection(region)
                if clipped.is_empty:
                    continue
                if clipped.geom_type == "LineString":
                    picked.append(clipped)
                    picked_layers[lay] += 1
                elif clipped.geom_type == "MultiLineString":
                    for g in clipped.geoms:
                        picked.append(g)
                        picked_layers[lay] += 1

            if len(picked) < MIN_LINES:
                results.append(
                    {
                        "id": cid,
                        "bbox": [round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)],
                        "insert_count": int(c.get("insert_count", 0)),
                        "picked_lines": len(picked),
                        "spaces_count": 0,
                        "spaces": [],
                        "net_area_drawing_units2": 0.0,
                        "top_spaces_areas": [],
                        "quality": "low",
                    }
                )
                continue

            mls = MultiLineString([list(g.coords) for g in picked if g.geom_type == "LineString"])
            merged = unary_union(mls)

            polys = list(polygonize(merged))
            polys = [p for p in polys if getattr(p, "area", 0.0) > 0.0]

            # küçükleri adaptif ele
            areas_sorted = sorted([float(p.area) for p in polys])
            med = areas_sorted[len(areas_sorted) // 2] if areas_sorted else 0.0
            min_area = max(1.0, med * 0.25)

            spaces = []
            for p in polys:
                if float(p.area) < min_area:
                    continue
                # boundary'ye yapışanları at (dış çevre / taşmalar)
                try:
                    if p.buffer(0.001).touches(region.boundary):
                        continue
                except Exception:
                    pass
                spaces.append(p)

            areas = sorted([float(p.area) for p in spaces], reverse=True)
            net_area = float(sum(areas))

            # JSON-friendly space summaries
            space_summaries = []
            for p in spaces:
                cpt = p.centroid
                bx1, by1, bx2, by2 = p.bounds
                space_summaries.append(
                    {
                        "area_draw2": round(float(p.area), 4),
                        "confidence": 0.80,
                        "layer": "CLUSTER_INFERRED",
                        "source": f"CLUSTER_{cid}",
                        "poly_centroid_draw": (float(cpt.x), float(cpt.y)),
                        "poly_bounds_draw": (float(bx1), float(by1), float(bx2), float(by2)),
                    }
                )

            space_summaries.sort(key=lambda x: x["area_draw2"], reverse=True)
            space_summaries = space_summaries[:SPACE_LIMIT]

            quality = "ok" if (len(spaces) >= 20 and net_area >= 50) else "low"

            results.append(
                {
                    "id": cid,
                    "bbox": [round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)],
                    "insert_count": int(c.get("insert_count", 0)),
                    "picked_lines": len(picked),
                    "wall_layers_top": sorted(picked_layers.items(), key=lambda kv: kv[1], reverse=True)[:10],
                    "spaces_count": len(spaces),
                    "spaces": space_summaries,
                    "net_area_drawing_units2": round(net_area, 3),
                    "top_spaces_areas": [round(a, 3) for a in areas[:20]],
                    "quality": quality,
                }
            )

        return results