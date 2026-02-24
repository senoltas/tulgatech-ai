import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from engine.orchestrator import TulgaTechOrchestrator as O

def polygon_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0

o = O()
r = o.process_project(r"data\ornek_proje_3.dxf")
p = r["project"]

sc = float(p.get("scale", 1.0))
pls = p["elements"]["polylines"]

areas = []
by_layer = {}

for pl in pls:
    pts = pl.get("points", [])
    if pl.get("closed") and len(pts) >= 3:
        a_m2 = polygon_area(pts) * (sc ** 2)
        areas.append(a_m2)
        layer = pl.get("layer") or "NONE"
        by_layer[layer] = by_layer.get(layer, 0) + 1

areas_sorted = sorted(areas)

print("CLOSED_CNT =", len(areas_sorted))
print("MIN_m2     =", areas_sorted[0] if areas_sorted else None)
print("MED_m2     =", areas_sorted[len(areas_sorted)//2] if areas_sorted else None)
print("MAX_m2     =", areas_sorted[-1] if areas_sorted else None)

# En çok kapalı polyline olan ilk 10 layer
top = sorted(by_layer.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTOP_CLOSED_LAYERS (first 10):")
for layer, cnt in top:
    print(f"  {cnt:6d}  {layer}")
