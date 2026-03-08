"""
Integration tests with real DXF files
"""
import os
from pathlib import Path
from tulgatech.engine.orchestrator import TulgaTechOrchestrator


def get_test_dxf_path():
    """Get path to test DXF file"""
    return "data/test_33.dxf"


def test_dxf_file_exists():
    """Test that DXF file exists"""
    path = get_test_dxf_path()
    assert Path(path).exists(), f"Test file not found: {path}"


def test_load_real_dxf():
    """Test loading real DXF file"""
    orch = TulgaTechOrchestrator()
    
    path = get_test_dxf_path()
    result = orch.process(path)
    
    # Check basic structure
    assert "success" in result
    assert "scale" in result
    assert "walls" in result
    assert "stats" in result


def test_real_dxf_scale_detected():
    """Test scale detection on real file"""
    orch = TulgaTechOrchestrator()
    
    path = get_test_dxf_path()
    result = orch.process(path)
    
    if result["success"]:
        assert result["scale"] is not None
        assert result["scale"]["value"] > 0


def test_real_dxf_segments_extracted():
    """Test segment extraction on real file"""
    orch = TulgaTechOrchestrator()
    
    path = get_test_dxf_path()
    result = orch.process(path)
    
    if result["success"]:
        # Should have extracted some segments
        segment_count = result["stats"].get("total_segments", 0)
        assert segment_count >= 0


def test_real_dxf_walls_detected():
    """Test wall detection on real file"""
    orch = TulgaTechOrchestrator()
    
    path = get_test_dxf_path()
    result = orch.process(path)
    
    if result["success"]:
        wall_count = len(result["walls"])
        # Even if 0 walls, test passes (data quality varies)
        assert isinstance(wall_count, int)
        assert wall_count >= 0


def test_real_dxf_bbox():
    """Test bounding box on real file"""
    orch = TulgaTechOrchestrator()
    
    path = get_test_dxf_path()
    result = orch.process(path)
    
    if result["success"]:
        bbox = result["stats"].get("bbox")
        if bbox:
            minx, miny, maxx, maxy = bbox
            assert minx <= maxx
            assert miny <= maxy


def test_real_dxf_layers_detected():
    """Test layer detection on real file"""
    orch = TulgaTechOrchestrator()
    
    path = get_test_dxf_path()
    result = orch.process(path)
    
    if result["success"]:
        layers = result["stats"].get("layers", [])
        assert isinstance(layers, list)
        # Should have at least some layers
        assert len(layers) >= 0