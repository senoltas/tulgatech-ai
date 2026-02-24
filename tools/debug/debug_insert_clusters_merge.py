import ezdxf
from collections import defaultdict, deque

DXF_PATH = r"data\test_2.dxf"
CELL = 120.0

# Kaç insert olursa “ciddiye alalım”
MIN_BUCKET_N = 20       # bucket içinde en az kaç insert olmalı
MIN_CLUSTER_PTS = 80    # cluster toplamında en az kaç insert olmalı (pafta adayı)

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

# Grid bucket
buckets = defaultdict(list)
for x, y, name in pts:
    gx = int(x // CELL)
    gy = int(y // CELL)
    buckets[(gx, gy)].append((x, y, name))

print("GRID_BUCKETS =", len(buckets))

# Sadece “yoğun” bucket’lar üzerinden cluster üretelim (gürültü azalır)
active = {k for k, arr in buckets.items() if len(arr) >= MIN_BUCKET_N}
print("ACTIVE_BUCKETS (n>=%d) =" % MIN_BUCKET_N, len(active))

def neighbors8(k):
    gx, gy = k
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            yield (gx + dx, gy + dy)

# Flood-fill ile cluster (8-komşuluk)
visited = set()
clusters = []
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
    clusters.append(cells)

print("CLUSTERS =", len(clusters))

# Cluster özetleri
summaries = []
for idx, cells in enumerate(clusters, 1):
    # cluster içindeki tüm noktaları topla
    arr = []
    for c in cells:
        arr.extend(buckets[c])
    npts = len(arr)
    xs = [p[0] for p in arr]
    ys = [p[1] for p in arr]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    # bucket bbox da raporlayalım (kaç hücre kaplıyor)
    gxs = [c[0] for c in cells]
    gys = [c[1] for c in cells]
    grid_bbox = (min(gxs), min(gys), max(gxs), max(gys))

    summaries.append({
        "id": idx,
        "npts": npts,
        "ncells": len(cells),
        "bbox": (minx, miny, maxx, maxy),
        "grid_bbox": grid_bbox,
        "cells": sorted(cells),
    })

# Büyükten küçüğe sırala
summaries.sort(key=lambda s: s["npts"], reverse=True)

print("\nTOP_CLUSTERS (cell=%s, bucket_n>=%d):" % (CELL, MIN_BUCKET_N))
for s in summaries[:20]:
    minx, miny, maxx, maxy = s["bbox"]
    gb = s["grid_bbox"]
    mark = " <-- PAFTA_ADAYI" if s["npts"] >= MIN_CLUSTER_PTS else ""
    print(
        f"- C{s['id']:02d}: pts={s['npts']:4d}  cells={s['ncells']:2d}  "
        f"grid_bbox={gb}  "
        f"bbox=({minx:.1f},{miny:.1f})-({maxx:.1f},{maxy:.1f}){mark}"
    )

# İstersen cluster cell listesini de dök (debug)
print("\nCLUSTER_CELLS (first 10):")
for s in summaries[:10]:
    print(f"C{s['id']:02d} cells:", s["cells"])