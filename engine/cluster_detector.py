from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Iterable

@dataclass
class Cluster:
    id: str
    cells: List[Tuple[int,int]]
    bbox: Tuple[float,float,float,float]
    insert_count: int

def grid_cluster_inserts(
    insert_pts: List[Tuple[float,float,str]],
    cell: float = 120.0,
    min_bucket_n: int = 20,
    min_cluster_pts: int = 80,
) -> List[Cluster]:
    """
    INSERT noktalarını grid bucket'a atar, komşu bucket'ları birleştirir (8-neighborhood),
    cluster bbox ve insert_count çıkarır.
    """
    buckets: Dict[Tuple[int,int], List[Tuple[float,float,str]]] = defaultdict(list)
    for x, y, name in insert_pts:
        gx = int(x // cell)
        gy = int(y // cell)
        buckets[(gx, gy)].append((x, y, name))

    active = {k for k, arr in buckets.items() if len(arr) >= min_bucket_n}

    def neighbors8(k):
        gx, gy = k
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                yield (gx + dx, gy + dy)

    visited = set()
    raw_clusters: List[List[Tuple[int,int]]] = []
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
        raw_clusters.append(sorted(cells))

    clusters: List[Cluster] = []
    # cluster bbox hesapla
    for idx, cells in enumerate(raw_clusters, 1):
        arr = []
        for c in cells:
            arr.extend(buckets[c])
        if len(arr) < min_cluster_pts:
            continue
        xs = [p[0] for p in arr]
        ys = [p[1] for p in arr]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        clusters.append(Cluster(
            id=f"C{idx:02d}",
            cells=cells,
            bbox=bbox,
            insert_count=len(arr)
        ))

    # büyükten küçüğe
    clusters.sort(key=lambda c: c.insert_count, reverse=True)
    return clusters