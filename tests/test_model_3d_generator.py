"""
Tests for 3D Model Generator
"""
from tulgatech.engine.model_3d_generator import Wall3D, Room3D, Model3DGenerator


def test_wall_3d_init():
    """Test Wall3D initialization"""
    wall = Wall3D("W001")
    assert wall.id == "W001"
    assert wall.height_m == 3.0


def test_wall_3d_vertices():
    """Test generating wall vertices"""
    wall = Wall3D("W001")
    wall.start_2d = (0, 0)
    wall.end_2d = (10, 0)
    
    vertices = wall.generate_vertices()
    
    assert len(vertices) == 8  # 4 bottom + 4 top


def test_room_3d_init():
    """Test Room3D initialization"""
    room = Room3D("R001")
    assert room.id == "R001"
    assert room.height_m == 2.7


def test_room_3d_vertices():
    """Test generating room vertices"""
    room = Room3D("R001")
    room.bbox_2d = (0, 0, 10, 10)
    
    vertices_dict = room.generate_vertices()
    
    assert "floor" in vertices_dict
    assert "ceiling" in vertices_dict
    assert len(vertices_dict["floor"]) == 4


def test_room_3d_volume():
    """Test room volume calculation"""
    room = Room3D("R001")
    room.bbox_2d = (0, 0, 10, 10)  # 10x10 floor
    room.height_m = 2.7
    
    room.generate_vertices()
    
    # Volume should be 10 * 10 * 2.7 = 270
    assert abs(room.volume_m3 - 270.0) < 0.1


def test_generator_init():
    """Test Model3DGenerator initialization"""
    gen = Model3DGenerator()
    assert gen.walls_3d == []
    assert gen.rooms_3d == []


def test_generate_from_2d():
    """Test generating 3D from 2D"""
    gen = Model3DGenerator()
    
    walls_2d = [
        {"start": (0, 0), "end": (10, 0)},
        {"start": (10, 0), "end": (10, 10)},
    ]
    
    rooms_2d = [
        {"bbox": (0, 0, 10, 10)},
    ]
    
    result = gen.generate_from_2d(walls_2d, rooms_2d)
    
    assert result["walls_3d_count"] == 2
    assert result["rooms_3d_count"] == 1


def test_get_obj_string():
    """Test OBJ string generation"""
    gen = Model3DGenerator()
    
    walls_2d = [
        {"start": (0, 0), "end": (10, 0)},
    ]
    rooms_2d = [
        {"bbox": (0, 0, 10, 10)},
    ]
    
    gen.generate_from_2d(walls_2d, rooms_2d)
    obj = gen.get_obj_string()
    
    assert "v " in obj  # Has vertices
    assert "TulgaTech" in obj


def test_get_model_stats():
    """Test model statistics"""
    gen = Model3DGenerator()
    
    walls_2d = [
        {"start": (0, 0), "end": (10, 0)},
    ]
    rooms_2d = [
        {"bbox": (0, 0, 10, 10)},
    ]
    
    gen.generate_from_2d(walls_2d, rooms_2d)
    stats = gen.get_model_stats()
    
    assert "walls_count" in stats
    assert "rooms_count" in stats
    assert stats["total_volume_m3"] > 0