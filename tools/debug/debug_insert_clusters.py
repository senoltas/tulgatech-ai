import ezdxf
from collections import defaultdict

DXF_PATH = r"data\test_2.dxf"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# INSERT noktaları
pts = []
for e in msp:
    if e.dxftype() != "INSERT":
        continue
    ip = e.dxf.insert
    pts.append((float(ip.x), float(ip.y), str(e.dxf.name)))

print("INSERT_TOTAL =", len(pts))

# Basit grid clustering:
# Aynı hücreye düşen noktalar aynı cluster adayı.
# cell size = 120 çizim birimi (gerekirse 80/150 deneriz)
CELL = 120.0

buckets = defaultdict(list)
for x, y, name in pts:
    gx = int(x // CELL)
    gy = int(y // CELL)
    buckets[(gx, gy)].append((x, y, name))

print("GRID_BUCKETS =", len(buckets))

# En dolu 20 bucket
items = sorted(buckets.items(), key=lambda kv: len(kv[1]), reverse=True)

print("\nTOP20_BUCKETS (cell=%s):" % CELL)
for i, (k, arr) in enumerate(items[:20], 1):
    xs = [p[0] for p in arr]; ys = [p[1] for p in arr]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    print(f"{i:02d}. bucket={k}  n={len(arr)}  bbox=({minx:.1f},{miny:.1f})-({maxx:.1f},{maxy:.1f})")