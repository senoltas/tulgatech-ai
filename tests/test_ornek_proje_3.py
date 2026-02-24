"""
DXF Processing Testleri (ornek_proje_3)
"""

import sys
from pathlib import Path


def _add_project_root_to_path():
    # tests/ klasöründen tulgatech_ai köküne çık
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))


def test_ornek_proje_3():
    _add_project_root_to_path()

    from engine.orchestrator import TulgaTechOrchestrator
    from engine.reporting import ReportGenerator

    dxf_path = Path("data") / "ornek_proje_3.dxf"

    print("Testing TulgaTech pipeline...")
    print(f"DXF: {dxf_path}")

    if not dxf_path.exists():
        print("✗ File not found:", dxf_path.resolve())
        return

    o = TulgaTechOrchestrator()
    r = o.process_project(str(dxf_path))

    print("success =", r.get("success"))
    if not r.get("success"):
        print("error =", r.get("error"))
        print("warnings =", r.get("warnings"))
        return

    # Özet kontrol
    summary = r.get("summary", {}) or {}
    print("summary keys =", list(summary.keys()))

    # Metraj sayısı kontrol
    quantities = (r.get("project", {}) or {}).get("quantities", []) or []
    print("quantities =", len(quantities))

    # Rapor üret
    g = ReportGenerator()
    out = g.generate_all_reports(r)
    print("reports =", out)

    print("✓ Test completed.")


if __name__ == "__main__":
    test_ornek_proje_3()
