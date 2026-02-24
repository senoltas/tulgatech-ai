import ezdxf
from shapely.geometry import LineString, MultiLineString, box, Polygon
from shapely.ops import unary_union, polygonize
from collections import Counter, defaultdict

DXF_PATH = r"data\test_2.dxf"

CLUSTERS = {
    "C01": (-179.6, -479.5, 471.8, -390.5),
    "C02": (-239.8, -220.1, 233.5, 83.8),
}

PAD = 20.0

POS = ["WALL", "MURO", "MUR", "DUVAR", "PARETE", "PERIM", "ESTER", "TRAMEZ", "PIL", "COLUMN", "COL", "KOLON"]
NEG = ["AX", "GRID", "ASSI", "ASSE", "MULLION", "INFISSO", "FURN", "ARRED", "DIM", "QUOTE", "TEXT", "HATCH",
       "SECTION", "SEZ", "DET", "DETAIL", "PROSP", "ELEV", "KOT", "AKS", "LIFT"]

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

def entity_to_lines(e):
    t = e.dxftype()
    out = []
    try:
        if t == "LINE":
            a = e.dxf.start
            b = e.dxf.end
            out.append(LineString([(float(a.x), float(a.y)), (float(b.x), float(b.y))]))
        elif t == "LWPOLYLINE":
            pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
            if len(pts) >= 2:
                out.append(LineString(pts))
        elif t == "POLYLINE":
            pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in e.vertices()]
            if len(pts) >= 2:
                out.append(LineString(pts))
    except Exception:
        pass
    return out

def closed_lwpoly_to_polygon(e):
    """Kapalı LWPOLYLINE -> Polygon (mümkünse)"""
    try:
        if e.dxftype() != "LWPOLYLINE":
            return None
        if not bool(getattr(e, "closed", False)):
            return None
        pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
        if len(pts) < 3:
            return None
        # bazı dxf'lerde son nokta ilk noktaya eşit değil, kapatalım
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        poly = Polygon(pts)
        if poly.is_valid and poly.area > 0:
            return poly
    except Exception:
        return None
    return None

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

layer_counts = Counter()
layer_scores = defaultdict(int)

all_lines = []
area_bndy_polys = []  # BBA-AREA-BNDY gibi kapalı polylineler

for e in msp:
    layer = str(getattr(e.dxf, "layer", "") or "")
    layer_counts[layer] += 1
    layer_scores[layer] = layer_score(layer)

    if e.dxftype() in ("LINE", "LWPOLYLINE", "POLYLINE"):
        for ln in entity_to_lines(e):
            all_lines.append((ln, layer))

    # Kapalı alan sınırı yakalama
    if e.dxftype() == "LWPOLYLINE" and "AREA" in layer.upper():
        poly = closed_lwpoly_to_polygon(e)
        if poly is not None:
            area_bndy_polys.append((poly, layer))

print("ALL_LINE_GEOMS =", len(all_lines))
print("AREA_POLYS (layer contains 'AREA', closed lwpoly) =", len(area_bndy_polys))

WALL_SCORE_MIN = 1
wall_lines = [(ln, lay) for (ln, lay) in all_lines if layer_scores[lay] >= WALL_SCORE_MIN]
print("WALL_CANDIDATE_LINES =", len(wall_lines), f"(score>={WALL_SCORE_MIN})")

def filter_spaces(polys, region):
    """Polygonize çıktısından 'oda' gibi olanları seçmeye çalış."""
    if not polys:
        return []
    # aşırı küçükleri at (adaptif eşik)
    areas = sorted([p.area for p in polys])
    med = areas[len(areas)//2]
    min_area = max(1.0, med * 0.25)  # median'ın %25'i altını at
    good = []
    for p in polys:
        if p.area < min_area:
            continue
        # bbox kenarına yapışan dev dış kabuğu ele (genelde pafta dış sınırına yapışır)
        # not: oda poligonları çoğunlukla region boundary'e dokunmaz
        if p.buffer(0.001).touches(region.boundary):
            continue
        good.append(p)
    return good

for cid, bb in CLUSTERS.items():
    minx, miny, maxx, maxy = bb
    region = box(minx - PAD, miny - PAD, maxx + PAD, maxy + PAD)

    # --- 1) WALL polygonize ---
    picked = []
    for ln, lay in wall_lines:
        if not region.intersects(ln):
            continue
        clipped = ln.intersection(region)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "LineString":
            picked.append(clipped)
        elif clipped.geom_type == "MultiLineString":
            picked.extend(list(clipped.geoms))

    print(f"\n[{cid}] picked_lines =", len(picked))

    spaces_wall = []
    if len(picked) >= 50:
        mls = MultiLineString([list(g.coords) for g in picked if g.geom_type == "LineString"])
        merged = unary_union(mls)
        polys = list(polygonize(merged))
        polys = [p for p in polys if p.area > 0.0]
        spaces_wall = filter_spaces(polys, region)

        total_wall = sum(p.area for p in spaces_wall)
        top_wall = sorted([p.area for p in spaces_wall], reverse=True)[:10]
        print(f"[{cid}] WALL_SPACES =", len(spaces_wall), " total_area=", round(total_wall, 2))
        print(f"[{cid}] WALL_TOP10 =", [round(a, 2) for a in top_wall])
    else:
        print(f"[{cid}] wall lines too few, skipping polygonize")

    # --- 2) AREA layer fallback (kapalı polylineler) ---
    picked_area = []
    for poly, lay in area_bndy_polys:
        if region.intersects(poly):
            clipped = poly.intersection(region)
            if not clipped.is_empty and clipped.geom_type == "Polygon":
                picked_area.append(clipped)

    if picked_area:
        # dış kabuk vs. temizlemek için küçükleri at
        picked_area = [p for p in picked_area if p.area > 1.0]
        picked_area.sort(key=lambda p: p.area, reverse=True)
        total_area = sum(p.area for p in picked_area)
        top10 = [round(p.area, 2) for p in picked_area[:10]]
        print(f"[{cid}] AREA_BNDY_POLYS =", len(picked_area), " total_area=", round(total_area, 2))
        print(f"[{cid}] AREA_BNDY_TOP10 =", top10)
    else:
        print(f"[{cid}] AREA_BNDY_POLYS = 0")