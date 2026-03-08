"""
Tests for WallDetector
"""
from tulgatech.engine.wall_detector import WallDetector


def test_wall_detector_init():
    """Test WallDetector initialization"""
    detector = WallDetector(scale=0.001)
    assert detector.scale == 0.001
    assert detector.wall_candidates == []


def test_detect_walls_empty():
    """Test detecting walls in empty list"""
    detector = WallDetector(scale=1.0)
    walls = detector.detect_walls([])
    assert walls == []


def test_detect_walls_single():
    """Test detecting single wall"""
    detector = WallDetector(scale=1.0)
    
    segments = [
        {
            "start": (0, 0),
            "end": (10, 0),
            "layer": "DUVAR",
            "source": "LINE"
        }
    ]
    
    walls = detector.detect_walls(segments, min_length_m=0.5)
    
    assert len(walls) == 1
    assert walls[0]["length_m"] == 10.0
    assert walls[0]["is_wall_layer"] == True


def test_detect_walls_filter_short():
    """Test filtering short segments"""
    detector = WallDetector(scale=1.0)
    
    segments = [
        {
            "start": (0, 0),
            "end": (0.1, 0),
            "layer": "DUVAR",
            "source": "LINE"
        }
    ]
    
    walls = detector.detect_walls(segments, min_length_m=0.5)
    assert len(walls) == 0


def test_get_total_wall_length():
    """Test total wall length"""
    detector = WallDetector(scale=1.0)
    
    segments = [
        {"start": (0, 0), "end": (5, 0), "layer": "DUVAR", "source": "LINE"},
        {"start": (0, 0), "end": (0, 3), "layer": "DUVAR", "source": "LINE"},
    ]
    
    detector.detect_walls(segments, min_length_m=0.5)
    total = detector.get_total_wall_length_m()
    
    assert abs(total - 8.0) < 0.01


def test_get_high_confidence_walls():
    """Test filtering by confidence"""
    detector = WallDetector(scale=1.0)
    
    segments = [
        {"start": (0, 0), "end": (5, 0), "layer": "DUVAR", "source": "LINE"},
        {"start": (0, 0), "end": (0, 3), "layer": "RANDOM", "source": "LINE"},
    ]
    
    detector.detect_walls(segments, min_length_m=0.5)
    high_conf = detector.get_high_confidence_walls(min_confidence=0.7)
    
    # Only DUVAR layer has high confidence (0.8)
    assert len(high_conf) == 1
    assert high_conf[0]["layer"] == "DUVAR"


def test_filter_by_angle():
    """Test filtering by angle"""
    detector = WallDetector(scale=1.0)
    
    segments = [
        {"start": (0, 0), "end": (10, 0), "layer": "DUVAR", "source": "LINE"},  # angle=0
        {"start": (0, 0), "end": (0, 10), "layer": "DUVAR", "source": "LINE"},   # angle=90
    ]
    
    detector.detect_walls(segments, min_length_m=0.5)
    
    # Only horizontal walls (0-45 degrees)
    horizontal = detector.filter_by_angle(0, 45)
    assert len(horizontal) == 1
    assert horizontal[0]["angle"] == 0.0