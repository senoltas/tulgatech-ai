from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
from collections import Counter, defaultdict

from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import unary_union, polygonize

@dataclass
class ClusterSpaceResult:
    cluster_id: str
    bbox: Tuple[float,float,float,float]
    pad: float
    picked_lines: int
    wall_layers: Dict[str,int]
    spaces_count: int
    net_area: float
    top_spaces_areas: List[float]

def layer_score(layer: str) -> int:
    if not layer:
        return -10
    up = layer.upper()
    POS = ["WALL","MURO","MUR","DUVAR","PARETE","PERIM","TRAMEZ","KOLON","COL","COLUMN"]
    NEG = ["AX","GRID","ASSI","ASSE","MULLION","INFISSO","FURN","ARRED","DIM","QUOTE","TEXT","HATCH",
           "SECTION","SEZ","DET","DETAIL","PROSP","ELEV","KOT","AKS","LIFT","DETAILLINE"]
    s = 0
    for k in POS:
        if k in up: s += 3
    for k in NEG:
        if k in up: s -= 5
    return s

def _entity_to_lines(e) -> List[LineString]:
    t = e.dxftype()
    out = []
    try:
        if t == "LINE":
            a = e.dxf.start; b = e.dxf.end
            out.append(LineString([(float(a.x), float(a.y)), (float(b.x), float(b.y))]))
        elif t == "LWPOLYLINE":
            pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
            if len(pts) >= 2: out.append(LineString(pts))
        elif t == "POLYLINE":
            pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in e.vertices()]
            if len(pts) >= 2: out.append(LineString(pts))
    except Exception:
        return []
    return out

def build_wall_line_index(msp, wall_score_min: int = 1):
    """
    modelspace'ten (LineString, layer) listesi çıkarır ve layer score >= wall_score_min olanları duvar adayı sayar.
    """
    layer_scores = defaultdict(int)
    all_lines = []
    for e in msp:
        if e.dxftype() not in ("LINE","LWPOLYLINE","POLYLINE"):
            continue
        layer = str(getattr(e.dxf, "layer", "") or "")
        layer_scores[layer] = layer_score(layer)
        for ln in _entity_to_lines(e):
            all_lines.append((ln, layer))
    wall_lines = [(ln, lay) for (ln, lay) in all_lines if layer_scores[lay] >= wall_score_min]
    return wall_lines, dict(layer_scores)

def extract_spaces_for_cluster(
    cluster_id: str,
    bbox: Tuple[float,float,float,float],
    wall_lines,
    layer_scores: Dict[str,int],
    pad: float = 20.0,
    min_lines: int = 50,
) -> ClusterSpaceResult:
    minx, miny, maxx, maxy = bbox
    region = box(minx - pad, miny - pad, maxx + pad, maxy + pad)

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

    if len(picked) < min_lines:
        return ClusterSpaceResult(
            cluster_id=cluster_id, bbox=bbox, pad=pad,
            picked_lines=len(picked),
            wall_layers=dict(picked_layers),
            spaces_count=0, net_area=0.0, top_spaces_areas=[]
        )

    mls = MultiLineString([list(g.coords) for g in picked if g.geom_type == "LineString"])
    merged = unary_union(mls)

    polys = list(polygonize(merged))
    polys = [p for p in polys if p.area > 0.0]

    # adaptif min_area + region boundary'e yapışanları at
    areas_sorted = sorted([p.area for p in polys])
    med = areas_sorted[len(areas_sorted)//2] if areas_sorted else 0.0
    min_area = max(1.0, med * 0.25)

    spaces = []
    for p in polys:
        if p.area < min_area:
            continue
        if p.buffer(0.001).touches(region.boundary):
            continue
        spaces.append(p)

    areas = sorted([p.area for p in spaces], reverse=True)
    net_area = float(sum(areas))

    return ClusterSpaceResult(
        cluster_id=cluster_id, bbox=bbox, pad=pad,
        picked_lines=len(picked),
        wall_layers=dict(picked_layers),
        spaces_count=len(spaces),
        net_area=net_area,
        top_spaces_areas=[float(a) for a in areas[:20]]
    )