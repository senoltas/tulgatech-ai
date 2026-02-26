from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse

import json
from pathlib import Path
from datetime import datetime

from engine.project_reader import ProjectReader





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dxf", nargs="?", default=str(Path("data") / "test_2.dxf"))
    parser.add_argument("--scale", type=float, default=None)
    args = parser.parse_args()

    dxf_path = Path(args.dxf)
    # Input DXF path (you can change this)
    

    if not dxf_path.exists():
        print(f"[ERROR] DXF not found: {dxf_path.resolve()}")
        print("Put a sample DXF under /data (but DO NOT commit large DXFs to GitHub).")
        return

    r = ProjectReader().read_dxf(str(dxf_path), scale_override=args.scale)

        # Debug: show all clusters and their quality
    cs = r.get("clusters", []) or []
    if cs:
        print("[DEBUG] clusters (all):")
        for c in cs:
            print(f" - {c.get('id')}: quality={c.get('quality')} net_area_m2={c.get('net_area_m2')} inserts={c.get('insert_count')} spaces={c.get('spaces_count')}")
    out_dir = Path("reports") / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"demo_result_{stamp}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)

    # Human-readable summary
    qs = r.get("quantities", []) or []
    net = next((q for q in qs if q.get("code") == "net_area_main_cluster_m2"), None)
    tot = next((q for q in qs if q.get("code") == "net_area_ok_clusters_total_m2"), None)
    

    # Extra: list cluster areas if present
    per_cluster = [q for q in qs if q.get("code") == "net_area_cluster_m2"]
    if per_cluster:
        print("[CLUSTERS] net_area_cluster_m2:")
        for q in sorted(per_cluster, key=lambda x: (x.get("meta", {}).get("cluster_id", ""))):
            cid = q.get("meta", {}).get("cluster_id")
            val = q.get("value")
            unit = q.get("unit")
            sc = q.get("meta", {}).get("spaces_count")
            area_sum = q.get("meta", {}).get("space_sum_m2")
            print(f" - {cid}: {val} {unit} (spaces_count={sc}, space_sum_m2={area_sum})")
    else:
        print("[CLUSTERS] No per-cluster quantity found (code=net_area_cluster_m2).")
    print("[OK] Demo result written:", out_path.as_posix())
    if net:
        print(f"[SUMMARY] Main net area: {net.get('value')} {net.get('unit')} (cluster={net.get('meta',{}).get('cluster_id')})")
    if tot:
        print(f"[SUMMARY] Total OK clusters net area: {tot.get('value')} {tot.get('unit')}")


if __name__ == "__main__":
    main()






