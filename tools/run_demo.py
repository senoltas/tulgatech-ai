from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path
from datetime import datetime

from engine.project_reader import ProjectReader


def main():
    # Input DXF path (you can change this)
    if len(sys.argv) > 1:
    	dxf_path = Path(sys.argv[1])
    else:
    	dxf_path = Path("data") / "test_2.dxf"

    if not dxf_path.exists():
        print(f"[ERROR] DXF not found: {dxf_path.resolve()}")
        print("Put a sample DXF under /data (but DO NOT commit large DXFs to GitHub).")
        return

    r = ProjectReader().read_dxf(str(dxf_path))

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

    print("[OK] Demo result written:", out_path.as_posix())
    if net:
        print(f"[SUMMARY] Main net area: {net.get('value')} {net.get('unit')} (cluster={net.get('meta',{}).get('cluster_id')})")
    if tot:
        print(f"[SUMMARY] Total OK clusters net area: {tot.get('value')} {tot.get('unit')}")


if __name__ == "__main__":
    main()