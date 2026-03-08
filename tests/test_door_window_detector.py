"""
Tests for DoorWindowDetector
"""
from tulgatech.engine.door_window_detector import Opening, DoorWindowDetector


def test_opening_init():
    """Test Opening initialization"""
    opening = Opening("D001", "DOOR")
    assert opening.id == "D001"
    assert opening.type == "DOOR"


def test_detector_init():
    """Test DoorWindowDetector initialization"""
    detector = DoorWindowDetector(scale=1.0)
    assert detector.scale == 1.0
    assert detector.openings == []


def test_detect_empty():
    """Test detecting with empty segments"""
    detector = DoorWindowDetector(scale=1.0)
    openings = detector.detect_from_segments([])
    assert openings == []


def test_get_door_count():
    """Test getting door count"""
    detector = DoorWindowDetector(scale=1.0)
    assert detector.get_door_count() == 0


def test_get_window_count():
    """Test getting window count"""
    detector = DoorWindowDetector(scale=1.0)
    assert detector.get_window_count() == 0


def test_estimate_door_area():
    """Test estimating door area"""
    detector = DoorWindowDetector(scale=1.0)
    area = detector.estimate_door_area_m2()
    assert area == 0.0


def test_estimate_window_area():
    """Test estimating window area"""
    detector = DoorWindowDetector(scale=1.0)
    area = detector.estimate_window_area_m2()
    assert area == 0.0
