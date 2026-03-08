"""
Tests for SegmentExtractor
"""
from tulgatech.io.segment_extractor import Segment, SegmentExtractor
from tulgatech.io.dxf_loader import DXFLoader


def test_segment_creation():
    """Test Segment creation"""
    seg = Segment((0, 0), (3, 4), "DUVAR", "LINE")
    assert seg.start == (0, 0)
    assert seg.end == (3, 4)
    assert seg.layer == "DUVAR"
    assert seg.source == "LINE"


def test_segment_length():
    """Test Segment length calculation"""
    # 3-4-5 triangle
    seg = Segment((0, 0), (3, 4), "DUVAR", "LINE")
    assert abs(seg.length() - 5.0) < 0.01


def test_segment_extractor_init():
    """Test SegmentExtractor initialization"""
    loader = DXFLoader()
    extractor = SegmentExtractor(loader)
    assert extractor.loader is loader
    assert extractor.segments == []


def test_extract_empty():
    """Test extract on unloaded DXF"""
    loader = DXFLoader()
    extractor = SegmentExtractor(loader)
    segments = extractor.extract()
    assert segments == []


def test_get_segments_by_layer():
    """Test filtering segments by layer"""
    loader = DXFLoader()
    extractor = SegmentExtractor(loader)
    
    # Add test segments
    extractor.segments = [
        Segment((0, 0), (1, 0), "DUVAR", "LINE"),
        Segment((0, 0), (0, 1), "DUVAR", "LINE"),
        Segment((0, 0), (1, 1), "DÖŞEME", "LINE"),
    ]
    
    duvar_segs = extractor.get_segments_by_layer("DUVAR")
    assert len(duvar_segs) == 2
    
    doseme_segs = extractor.get_segments_by_layer("DÖŞEME")
    assert len(doseme_segs) == 1


def test_get_total_length():
    """Test total length calculation"""
    loader = DXFLoader()
    extractor = SegmentExtractor(loader)
    
    # Add test segments
    extractor.segments = [
        Segment((0, 0), (3, 4), "DUVAR", "LINE"),  # length = 5
        Segment((0, 0), (1, 0), "DUVAR", "LINE"),  # length = 1
    ]
    
    total = extractor.get_total_length()
    assert abs(total - 6.0) < 0.01