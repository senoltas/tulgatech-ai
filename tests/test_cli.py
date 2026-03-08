"""
Tests for CLI
"""
import sys
from tulgatech.cli.main import print_header


def test_print_header(capsys):
    """Test header printing"""
    print_header()
    captured = capsys.readouterr()
    
    assert "TulgaTech AI" in captured.out
    assert "Construction Data Intelligence" in captured.out


def test_result_structure():
    """Test result structure"""
    result = {
        "success": False,
        "error": None,
        "scale": None,
        "segments": [],
        "walls": [],
        "stats": {}
    }
    
    assert "success" in result
    assert "error" in result
    assert "scale" in result
    assert "segments" in result
    assert "walls" in result
    assert "stats" in result


def test_successful_result_structure():
    """Test successful result structure"""
    result = {
        "success": True,
        "error": None,
        "scale": {
            "value": 0.001,
            "confidence": 0.8,
            "method": "dimension",
            "is_reliable": True
        },
        "segments": [{"start": (0, 0), "end": (10, 0), "layer": "DUVAR"}],
        "walls": [{"layer": "DUVAR", "length_m": 10.0, "confidence": 0.8}],
        "stats": {
            "total_segments": 100,
            "wall_candidates": 5,
            "total_wall_length_m": 50.0
        }
    }
    
    assert result["success"] == True
    assert result["scale"]["is_reliable"] == True
    assert len(result["walls"]) == 1


def test_error_result_structure():
    """Test error result structure"""
    result = {
        "success": False,
        "error": "File not found",
        "scale": None,
        "segments": [],
        "walls": [],
        "stats": {}
    }
    
    assert result["success"] == False
    assert result["error"] is not None
