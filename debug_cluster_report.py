import ezdxf
from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import unary_union, polygonize
from collections import Counter, defaultdict

DXF_PATH = r"data\test_2.dxf"

CLUSTERS = {
    "C01": (-179.6, -479.5, 471.8, -390.5),
    "C02": (-239.8, -220.1, 233.5, 83.8),
}

PAD = 20.0

POS = ["WALL", "MURO", "MUR", "DUVAR", "PARETE", "PERIM", "TRAMEZ", "KOLON", "COL", "COLUMN"]
NEG = ["AX", "GRID", "ASSI", "ASSE", "MULLION", "INFISSO", "FURN", "ARRED", "DIM", "QUOTE", "TEXT", "HATCH",
       "SECTION", "SEZ", "DET", "DETAIL", "PROSP", "ELEV", "KOT", "AKS", "LIFT", "DETAILLINE"]

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

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

layer_scores = defaultdict(int)
all_lines = []

for e in msp:
    if e.dxftype() not in ("LINE", "LWPOLYLINE", "POLYLINE"):
        continue
    layer = str(getattr(e.dxf, "layer", "") or "")
    layer_scores[layer] = layer_score(layer)
    for ln in entity_to_lines(e):
        all_lines.append((ln, layer))

WALL_SCORE_MIN = 1
wall_lines = [(ln, lay) for (ln, lay) in all_lines if layer_scores[lay] >= WALL_SCORE_MIN]

def spaces_from_region(region):
    picked = []
    picked_layers = Counter()
    for ln, lay in wall_lines:
        if not region.intersects(ln):
            continue
        clipped = ln.intersection(region)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "LineString":
            picked.append(clipped); picked_layers[lay] += 1
        elif clipped.geom_type == "MultiLineString":
            for g in clipped.geoms:
                picked.append(g); picked_layers[lay] += 1

    if len(picked) < 50:
        return [], picked_layers

    mls = MultiLineString([list(g.coords) for g in picked if g.geom_type == "LineString"])
    merged = unary_union(mls)

    polys = list(polygonize(merged))
    polys = [p for p in polys if p.area > 0.0]

    # adaptif küçük filtre + boundary'e yapışanları at
    areas = sorted([p.area for p in polys])
    med = areas[len(areas)//2] if areas else 0.0
    min_area = max(1.0, med * 0.25)

    good = []
    for p in polys:
        if p.area < min_area:
            continue
        if p.buffer(0.001).touches(region.boundary):
            continue
        good.append(p)

    return good, picked_layers

for cid, bb in CLUSTERS.items():
    minx, miny, maxx, maxy = bb
    region = box(minx - PAD, miny - PAD, maxx + PAD, maxy + PAD)

    spaces, layer_ct = spaces_from_region(region)
    areas = sorted([p.area for p in spaces], reverse=True)
    total = sum(areas)

    print(f"\n=== {cid} ===")
    print(f"region=({minx:.1f},{miny:.1f})-({maxx:.1f},{maxy:.1f}) PAD={PAD}")
    print("spaces =", len(spaces), " total_area =", round(total, 2))
    print("top20_areas =", [round(a, 2) for a in areas[:20]])

    print("top_layers_in_region:")
    for lay, cnt in layer_ct.most_common(10):
        print(f" - {lay!r}: {cnt}")