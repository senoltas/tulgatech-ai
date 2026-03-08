"""
Tests for ScaleManager
"""
from tulgatech.core.scale_manager import ScaleManager, ScaleEstimate


def test_scale_manager_init():
    """Test ScaleManager initialization"""
    mgr = ScaleManager()
    assert mgr.estimate is None
    assert mgr.get_scale() == 1.0


def test_scale_estimate_reliable():
    """Test ScaleEstimate reliability"""
    # High confidence
    est1 = ScaleEstimate(scale=0.001, confidence=0.8, method="dimension", samples=10)
    assert est1.is_reliable() == True
    
    # Low confidence
    est2 = ScaleEstimate(scale=0.001, confidence=0.5, method="text", samples=2)
    assert est2.is_reliable() == False


def test_scale_manager_reliable():
    """Test ScaleManager is_reliable method"""
    mgr = ScaleManager()
    assert mgr.is_reliable() == False
    
    # Set estimate
    mgr.estimate = ScaleEstimate(scale=0.001, confidence=0.8, method="dimension", samples=10)
    assert mgr.is_reliable() == True
