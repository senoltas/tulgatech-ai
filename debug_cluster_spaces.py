import ezdxf
from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import unary_union, polygonize
from collections import Counter, defaultdict

DXF_PATH = r"data\test_2.dxf"

# Cluster bbox'ları (B4-2 çıktısından)
CLUSTERS = {
    "C01": (-179.6, -479.5, 471.8, -390.5),
    "C02": (-239.8, -220.1, 233.5, 83.8),
    # küçükler (istersen aç)
    # "C03": (660.2, -471.4, 660.5, -458.9),
    # "C04": (1598.0, -475.5, 1606.5, -451.7),
}

# bbox'u biraz şişir, duvarlar sınırda kalmasın
PAD = 20.0

# "duvar gibi" katmanları kabaca yakalamak için kelime listesi
# (senin projelerde layer isimleri karışık, o yüzden geniş tuttum)
POS = ["WALL", "MURO", "MUR", "DUVAR", "PARETE", "PERIM", "ESTER", "TRAMEZ", "PIL", "COLUMN", "COL"]
NEG = ["AX", "GRID", "ASSI", "ASSE", "MULLION", "INFISSO", "FURN", "ARRED", "DIM", "QUOTE", "TEXT", "HATCH",
       "SECTION", "SEZ", "DET", "DETAIL", "PROSP", "ELEV"]

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
    """DXF entity -> list[LineString] (drawing units)"""
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
        # ARC/CIRCLE vb. şimdilik yok sayıyoruz (istersen sonra discretize ederiz)
    except Exception:
        pass
    return out

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# Katman istatistikleri (debug)
layer_counts = Counter()
layer_scores = defaultdict(int)

# Tüm çizgi adaylarını topla (layer skoruna göre filtreleyeceğiz)
all_lines = []
for e in msp:
    t = e.dxftype()
    if t not in ("LINE", "LWPOLYLINE", "POLYLINE"):
        continue
    layer = str(getattr(e.dxf, "layer", "") or "")
    layer_counts[layer] += 1
    layer_scores[layer] = layer_score(layer)
    all_lines.extend([(ln, layer) for ln in entity_to_lines(e)])

print("ALL_LINE_GEOMS =", len(all_lines))
print("\nTOP_LAYERS_BY_COUNT:")
for lay, cnt in layer_counts.most_common(20):
    print(f"- {lay!r}: {cnt}  score={layer_scores[lay]}")

# “duvar adayı” filtre: score >= 1 (gerekirse 2 yaparız)
WALL_SCORE_MIN = 1

wall_lines = [(ln, lay) for (ln, lay) in all_lines if layer_scores[lay] >= WALL_SCORE_MIN]
print("\nWALL_CANDIDATE_LINES =", len(wall_lines), f"(score>={WALL_SCORE_MIN})")

# Cluster bazında polygonize
for cid, bb in CLUSTERS.items():
    minx, miny, maxx, maxy = bb
    region = box(minx - PAD, miny - PAD, maxx + PAD, maxy + PAD)

    picked = []
    picked_layers = Counter()

    for ln, lay in wall_lines:
        # bbox hızlı test
        if not region.intersects(ln):
            continue
        # bölge içinde kırp (çok uzun çizgiler her şeyi bozmasın)
        clipped = ln.intersection(region)
        if clipped.is_empty:
            continue
        # intersection bazen MultiLineString döndürür
        if clipped.geom_type == "LineString":
            picked.append(clipped)
            picked_layers[lay] += 1
        elif clipped.geom_type == "MultiLineString":
            for g in clipped.geoms:
                picked.append(g)
                picked_layers[lay] += 1

    print(f"\n[{cid}] region_bbox=({minx:.1f},{miny:.1f})-({maxx:.1f},{maxy:.1f}) PAD={PAD}")
    print(f"[{cid}] picked_lines =", len(picked))
    print(f"[{cid}] top_picked_layers:")
    for lay, cnt in picked_layers.most_common(10):
        print(f"   - {lay!r}: {cnt}  score={layer_scores[lay]}")

    if len(picked) < 50:
        print(f"[{cid}] TOO_FEW_LINES -> polygonize anlamsız, filter gevşetmek gerek.")
        continue

    mls = MultiLineString([list(g.coords) for g in picked if g.geom_type == "LineString"])
    merged = unary_union(mls)

    polys = list(polygonize(merged))
    # aşırı küçük çöpleri at
    polys = [p for p in polys if p.area > 1.0]

    polys.sort(key=lambda p: p.area, reverse=True)

    total_area = sum(p.area for p in polys)
    print(f"[{cid}] POLYGONS =", len(polys), " total_area=", round(total_area, 2))
    print(f"[{cid}] TOP10_AREAS =", [round(p.area, 2) for p in polys[:10]])