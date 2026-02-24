"""
Testleri çalıştır (TulgaTech AI)
"""

import sys
from pathlib import Path


def _add_project_root_to_path():
    root = Path(__file__).resolve().parents[1]  # tulgatech_ai kök
    sys.path.insert(0, str(root))


def run_all_tests():
    print("Running TulgaTech AI Tests...")
    print("=" * 60)

    _add_project_root_to_path()

    try:
        # 1) Import testleri
        print("\n1) Import tests...")
        from engine.quantity_models import QuantityItem, Assumption, ExtractionMethod
        from engine.orchestrator import TulgaTechOrchestrator
        from engine.reporting import ReportGenerator

        print("  ✓ Imports OK")

        # 2) Model smoke test
        print("\n2) Model smoke test...")
        test_item = QuantityItem(
            id="TEST_001",
            name="Test Item",
            category="area",
            value=100.0,
            unit="m²",
            extraction_method=ExtractionMethod.USER_CORRECTION,
            confidence=0.8,
            assumptions=[
                Assumption("test_param", "test_value", "system", 0.9),
            ],
            source_data={"note": "smoke_test"},
            warnings=[]
        )
        d = test_item.to_dict()
        assert d["id"] == "TEST_001"
        print("  ✓ QuantityItem.to_dict OK")

        # 3) Pipeline test (ornek_proje_3)
        print("\n3) Pipeline test (ornek_proje_3)...")
        dxf_path = Path("data") / "ornek_proje_3.dxf"
        if not dxf_path.exists():
            raise FileNotFoundError(f"DXF not found: {dxf_path.resolve()}")

        o = TulgaTechOrchestrator()
        r = o.process_project(str(dxf_path))

        if not r.get("success"):
            raise RuntimeError(f"Pipeline failed: {r.get('error')} | warnings={r.get('warnings')}")

        quantities = (r.get("project", {}) or {}).get("quantities", []) or []
        print(f"  ✓ Pipeline OK | quantities={len(quantities)}")

        # 4) Report generation test
        print("\n4) Report generation test...")
        g = ReportGenerator()
        out = g.generate_all_reports(r)
        if not out:
            raise RuntimeError("No reports generated")
        print(f"  ✓ Reports generated: {list(out.keys())}")

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
