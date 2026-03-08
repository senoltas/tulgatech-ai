"""
Tests for TulgaTechOrchestrator
"""
from tulgatech.engine.orchestrator import TulgaTechOrchestrator


def test_orchestrator_init():
    """Test orchestrator initialization"""
    orch = TulgaTechOrchestrator()
    assert orch.loader is not None
    assert orch.normalizer is not None
    assert orch.scale_mgr is not None
    assert orch.result["success"] == False


def test_orchestrator_result_structure():
    """Test result structure"""
    orch = TulgaTechOrchestrator()
    result = orch.result
    
    assert "success" in result
    assert "error" in result
    assert "scale" in result
    assert "segments" in result
    assert "walls" in result
    assert "stats" in result


def test_process_nonexistent_file():
    """Test processing non-existent file"""
    orch = TulgaTechOrchestrator()
    result = orch.process("nonexistent_file.dxf")
    
    assert result["success"] == False
    assert result["error"] is not None


def test_get_summary():
    """Test getting summary"""
    orch = TulgaTechOrchestrator()
    summary = orch.get_summary()
    
    assert "success" in summary
    assert "error" in summary
    assert "scale_confidence" in summary
    assert "segments_count" in summary
    assert "walls_count" in summary
    assert "total_wall_length_m" in summary


def test_orchestrator_empty_state():
    """Test orchestrator in empty state"""
    orch = TulgaTechOrchestrator()
    
    summary = orch.get_summary()
    assert summary["success"] == False
    assert summary["segments_count"] == 0
    assert summary["walls_count"] == 0
    assert summary["total_wall_length_m"] == 0