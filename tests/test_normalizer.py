"""
Tests for EntityNormalizer
"""
from tulgatech.io.normalizer import EntityNormalizer
from tulgatech.io.dxf_loader import DXFLoader


def test_normalize_segment():
    """Test segment normalization"""
    norm = EntityNormalizer()
    seg = norm.normalize_segment((1, 2), (3, 4), "DUVAR", "LINE")
    
    assert seg["start"] == (1.0, 2.0)
    assert seg["end"] == (3.0, 4.0)
    assert seg["layer"] == "DUVAR"
    assert seg["source"] == "LINE"
    assert seg["type"] == "segment"


def test_normalize_text():
    """Test text normalization"""
    norm = EntityNormalizer()
    txt = norm.normalize_text("Plan 1/100", 10.5, 20.3, "TEXT", 2.5)
    
    assert txt["text"] == "Plan 1/100"
    assert txt["x"] == 10.5
    assert txt["y"] == 20.3
    assert txt["layer"] == "TEXT"
    assert txt["height"] == 2.5
    assert txt["type"] == "text"


def test_normalizer_init():
    """Test EntityNormalizer initialization"""
    norm = EntityNormalizer()
    assert norm.normalized_segments == []
    assert norm.normalized_texts == []


def test_get_normalized_segments_empty():
    """Test getting segments when empty"""
    norm = EntityNormalizer()
    segs = norm.get_normalized_segments()
    assert segs == []


def test_get_normalized_texts_empty():
    """Test getting texts when empty"""
    norm = EntityNormalizer()
    txts = norm.get_normalized_texts()
    assert txts == []


def test_filter_by_layer():
    """Test filtering by layer"""
    norm = EntityNormalizer()
    
    # Add test segments
    norm.normalized_segments = [
        norm.normalize_segment((0, 0), (1, 0), "DUVAR", "LINE"),
        norm.normalize_segment((0, 0), (0, 1), "DUVAR", "LINE"),
        norm.normalize_segment((0, 0), (1, 1), "DÖŞEME", "LINE"),
    ]
    
    duvar = norm.filter_by_layer("DUVAR", "segment")
    assert len(duvar) == 2
    
    doseme = norm.filter_by_layer("DÖŞEME", "segment")
    assert len(doseme) == 1


def test_normalize_from_dxf_loader_empty():
    """Test normalizing empty DXF"""
    loader = DXFLoader()
    norm = EntityNormalizer()
    
    result = norm.normalize_from_dxf_loader(loader)
    
    assert result["segments"] == []
    assert result["texts"] == []
    assert result["count"] == 0