"""
Tests for LayerProfiler
"""
from tulgatech.engine.layer_profiler import LayerProfile, LayerProfiler


def test_layer_profile_init():
    """Test LayerProfile initialization"""
    profile = LayerProfile("DUVAR")
    assert profile.name == "DUVAR"
    assert profile.segment_count == 0
    assert profile.text_count == 0
    assert profile.total_length == 0.0


def test_layer_profile_to_dict():
    """Test LayerProfile to_dict"""
    profile = LayerProfile("DUVAR")
    profile.segment_count = 10
    
    d = profile.to_dict()
    assert d["name"] == "DUVAR"
    assert d["segment_count"] == 10


def test_layer_profiler_init():
    """Test LayerProfiler initialization"""
    profiler = LayerProfiler()
    assert profiler.profiles == {}


def test_profile_segments_empty():
    """Test profiling empty segments"""
    profiler = LayerProfiler()
    profiles = profiler.profile_segments([])
    assert profiles == {}


def test_profile_segments_single():
    """Test profiling single segment"""
    profiler = LayerProfiler()
    
    segments = [
        {"start": (0, 0), "end": (10, 0), "layer": "DUVAR"}
    ]
    
    profiles = profiler.profile_segments(segments)
    
    assert "DUVAR" in profiles
    assert profiles["DUVAR"].segment_count == 1
    assert profiles["DUVAR"].total_length == 10.0


def test_profile_texts():
    """Test profiling texts"""
    profiler = LayerProfiler()
    
    texts = [
        {"text": "Plan 1", "x": 0, "y": 0, "layer": "TEXT"},
        {"text": "Plan 2", "x": 10, "y": 10, "layer": "TEXT"},
    ]
    
    profiles = profiler.profile_texts(texts)
    
    assert "TEXT" in profiles
    assert profiles["TEXT"].text_count == 2


def test_get_summary():
    """Test get summary"""
    profiler = LayerProfiler()
    
    segments = [
        {"start": (0, 0), "end": (5, 0), "layer": "DUVAR"},
        {"start": (0, 0), "end": (0, 3), "layer": "DÖŞEME"},
    ]
    
    profiler.profile_segments(segments)
    summary = profiler.get_summary()
    
    assert summary["total_layers"] == 2
    assert len(summary["layers"]) == 2
    assert "DUVAR" in summary["layer_names"]


def test_get_top_layers_by_segments():
    """Test getting top layers by segments"""
    profiler = LayerProfiler()
    
    segments = [
        {"start": (0, 0), "end": (1, 0), "layer": "DUVAR"},
        {"start": (0, 0), "end": (1, 0), "layer": "DUVAR"},
        {"start": (0, 0), "end": (1, 0), "layer": "DÖŞEME"},
    ]
    
    profiler.profile_segments(segments)
    top = profiler.get_top_layers_by_segments(limit=1)
    
    assert len(top) == 1
    assert top[0]["name"] == "DUVAR"
    assert top[0]["segment_count"] == 2


def test_detect_wall_layers():
    """Test detecting wall layers"""
    profiler = LayerProfiler()
    
    segments = [
        {"start": (0, 0), "end": (1, 0), "layer": "DUVAR"},
        {"start": (0, 0), "end": (1, 0), "layer": "WALL"},
        {"start": (0, 0), "end": (1, 0), "layer": "DÖŞEME"},
    ]
    
    profiler.profile_segments(segments)
    wall_layers = profiler.detect_wall_layers()
    
    assert len(wall_layers) == 2
    assert "DUVAR" in wall_layers
    assert "WALL" in wall_layers


def test_detect_text_layers():
    """Test detecting text layers"""
    profiler = LayerProfiler()
    
    texts = [
        {"text": "A", "x": 0, "y": 0, "layer": "TEXT"},
        {"text": "B", "x": 10, "y": 10, "layer": "YAZI"},
    ]
    
    profiler.profile_texts(texts)
    text_layers = profiler.detect_text_layers()
    
    assert len(text_layers) == 2
    assert "TEXT" in text_layers
    assert "YAZI" in text_layers