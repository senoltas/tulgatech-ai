"""
Tests for FrameDetector
"""
from tulgatech.engine.frame_detector import Frame, FrameDetector


def test_frame_init():
    """Test Frame initialization"""
    frame = Frame("F01")
    assert frame.id == "F01"
    assert frame.bbox is None
    assert frame.segments_count == 0


def test_frame_to_dict():
    """Test frame to_dict"""
    frame = Frame("F01")
    frame.width = 100.0
    frame.height = 80.0
    
    d = frame.to_dict()
    assert d["id"] == "F01"
    assert d["width"] == 100.0


def test_detector_init():
    """Test FrameDetector initialization"""
    detector = FrameDetector()
    assert detector.frames == []


def test_detect_empty():
    """Test detecting frames with empty segments"""
    detector = FrameDetector()
    frames = detector.detect_from_segments([])
    assert frames == []


def test_detect_single_frame():
    """Test detecting single frame"""
    detector = FrameDetector()
    
    segments = [
        {"start": (0, 0), "end": (100, 0)},
        {"start": (100, 0), "end": (100, 100)},
        {"start": (100, 100), "end": (0, 100)},
        {"start": (0, 100), "end": (0, 0)},
    ]
    
    frames = detector.detect_from_segments(segments)
    
    assert len(frames) == 1
    assert frames[0].width == 100.0
    assert frames[0].height == 100.0


def test_detect_multiple_frames():
    """Test detecting multiple frames with grid"""
    detector = FrameDetector()
    
    segments = [
        # Frame 1 area (0-50, 0-50)
        {"start": (10, 10), "end": (40, 40)},
        # Frame 2 area (50-100, 0-50)
        {"start": (60, 10), "end": (90, 40)},
        # Frame 3 area (0-50, 50-100)
        {"start": (10, 60), "end": (40, 90)},
        # Frame 4 area (50-100, 50-100)
        {"start": (60, 60), "end": (90, 90)},
    ]
    
    frames = detector.detect_multiple_frames(segments, grid_divisions=2)
    
    assert len(frames) == 4


def test_get_largest_frame():
    """Test getting largest frame"""
    detector = FrameDetector()
    
    segments = [
        {"start": (0, 0), "end": (100, 100)},
    ]
    
    detector.detect_from_segments(segments)
    largest = detector.get_largest_frame()
    
    assert largest is not None
    assert largest["width"] == 100.0


def test_frame_bbox():
    """Test frame bounding box"""
    detector = FrameDetector()
    
    segments = [
        {"start": (10, 20), "end": (80, 90)},
    ]
    
    frames = detector.detect_from_segments(segments)
    
    assert frames[0].bbox == (10, 20, 80, 90)


def test_frame_center():
    """Test frame center point"""
    detector = FrameDetector()
    
    segments = [
        {"start": (0, 0), "end": (100, 100)},
    ]
    
    frames = detector.detect_from_segments(segments)
    
    assert frames[0].center == (50.0, 50.0)