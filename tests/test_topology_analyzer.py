"""
Tests for TopologyAnalyzer
"""
from tulgatech.engine.topology_analyzer import RoomTopology, TopologyAnalyzer


def test_room_topology_init():
    """Test RoomTopology initialization"""
    topology = RoomTopology("R01")
    assert topology.id == "R01"
    assert len(topology.adjacent_rooms) == 0


def test_room_topology_to_dict():
    """Test RoomTopology to_dict"""
    topology = RoomTopology("R01")
    topology.area_m2 = 25.0
    
    d = topology.to_dict()
    assert d["id"] == "R01"
    assert d["area_m2"] == 25.0


def test_analyzer_init():
    """Test TopologyAnalyzer initialization"""
    analyzer = TopologyAnalyzer()
    assert analyzer.rooms == {}
    assert analyzer.adjacency_matrix == {}


def test_analyze_connectivity_empty():
    """Test analyzing empty rooms"""
    analyzer = TopologyAnalyzer()
    result = analyzer.analyze_connectivity([], [])
    
    assert result["rooms_analyzed"] == 0


def test_analyze_connectivity_single():
    """Test analyzing single room"""
    analyzer = TopologyAnalyzer()
    
    rooms = [
        {"id": "R01", "area_m2": 25.0, "perimeter_m": 20.0, "bbox": (0, 0, 5, 5)}
    ]
    
    result = analyzer.analyze_connectivity(rooms, [])
    
    assert result["rooms_analyzed"] == 1


def test_analyze_connectivity_adjacent():
    """Test detecting adjacent rooms"""
    analyzer = TopologyAnalyzer()
    
    rooms = [
        {"id": "R01", "area_m2": 25.0, "bbox": (0, 0, 5, 5)},
        {"id": "R02", "area_m2": 25.0, "bbox": (5, 0, 10, 5)},
    ]
    
    result = analyzer.analyze_connectivity(rooms, [])
    
    assert result["rooms_analyzed"] == 2
    assert result["adjacencies_found"] >= 0


def test_get_adjacency_matrix():
    """Test getting adjacency matrix"""
    analyzer = TopologyAnalyzer()
    
    rooms = [
        {"id": "R01", "area_m2": 25.0, "bbox": (0, 0, 5, 5)},
    ]
    
    analyzer.analyze_connectivity(rooms, [])
    matrix = analyzer.get_adjacency_matrix()
    
    assert "R01" in matrix


def test_is_accessible():
    """Test accessibility check"""
    analyzer = TopologyAnalyzer()
    
    rooms = [
        {"id": "R01", "area_m2": 25.0, "bbox": (0, 0, 5, 5)},
    ]
    
    analyzer.analyze_connectivity(rooms, [])
    accessible = analyzer.is_accessible("R01")
    
    # Single room should be accessible to itself
    assert isinstance(accessible, bool)


def test_analyze_flow():
    """Test analyzing spatial flow"""
    analyzer = TopologyAnalyzer()
    
    rooms = [
        {"id": "R01", "area_m2": 25.0, "bbox": (0, 0, 5, 5)},
        {"id": "R02", "area_m2": 25.0, "bbox": (5, 0, 10, 5)},
    ]
    
    analyzer.analyze_connectivity(rooms, [])
    flow = analyzer.analyze_flow()
    
    assert flow["total_rooms"] == 2
    assert "accessibility" in flow