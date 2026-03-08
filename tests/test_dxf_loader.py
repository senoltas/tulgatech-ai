"""
Tests for DXF loader
"""
from tulgatech.io.dxf_loader import DXFLoader


def test_dxf_loader_init():
    """Test DXFLoader initialization"""
    loader = DXFLoader()
    assert loader.doc is None
    assert loader.msp is None


def test_get_entity_count_empty():
    """Test entity count on unloaded file"""
    loader = DXFLoader()
    assert loader.get_entity_count() == 0


def test_get_layers_empty():
    """Test get layers on unloaded file"""
    loader = DXFLoader()
    assert loader.get_layers() == []


def test_get_bbox_empty():
    """Test get bbox on unloaded file"""
    loader = DXFLoader()
    assert loader.get_bbox() is None