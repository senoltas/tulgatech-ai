"""
Basic tests for tulgatech
"""

def test_import():
    """Test that tulgatech can be imported"""
    import tulgatech
    assert tulgatech is not None


def test_core_types():
    """Test core types module"""
    from tulgatech.core.types import ScaleMethod
    assert ScaleMethod.DIMENSION_BASED is not None


def test_geometry():
    """Test geometry utilities"""
    from tulgatech.core.geometry import distance
    
    # Test distance between (0,0) and (3,4) = 5
    d = distance((0, 0), (3, 4))
    assert abs(d - 5.0) < 0.01