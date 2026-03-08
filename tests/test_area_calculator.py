"""
Tests for AreaCalculator
"""
from tulgatech.engine.area_calculator import AreaCalculator


def test_area_calculator_init():
    """Test AreaCalculator initialization"""
    calc = AreaCalculator(scale=0.001)
    assert calc.scale == 0.001
    assert calc.calculated_areas == []


def test_polygon_area_triangle():
    """Test polygon area calculation"""
    calc = AreaCalculator()
    
    # Right triangle: base=3, height=4
    points = [(0, 0), (3, 0), (0, 4)]
    area = calc.polygon_area(points)
    
    # Area should be ~6 (3*4/2)
    assert abs(area - 6.0) < 0.1


def test_polygon_area_square():
    """Test square area"""
    calc = AreaCalculator()
    
    # 10x10 square
    points = [(0, 0), (10, 0), (10, 10), (0, 10)]
    area = calc.polygon_area(points)
    
    assert abs(area - 100.0) < 0.1


def test_polygon_area_empty():
    """Test polygon area with no points"""
    calc = AreaCalculator()
    area = calc.polygon_area([])
    assert area == 0.0


def test_estimate_net_area_empty():
    """Test net area with empty segments"""
    calc = AreaCalculator(scale=1.0)
    result = calc.estimate_net_area([])
    
    assert result["net_area_m2"] == 0.0
    assert result["confidence"] == 0.0


def test_estimate_net_area_single():
    """Test net area with segments"""
    calc = AreaCalculator(scale=1.0)
    
    segments = [
        {"start": (0, 0), "end": (10, 0)},
        {"start": (10, 0), "end": (10, 10)},
        {"start": (10, 10), "end": (0, 10)},
        {"start": (0, 10), "end": (0, 0)},
    ]
    
    result = calc.estimate_net_area(segments)
    
    assert result["net_area_m2"] > 0
    assert result["points_count"] == 8


def test_estimate_gross_area():
    """Test gross area calculation"""
    calc = AreaCalculator(scale=1.0)
    
    # 20x30 bbox
    bbox = (0, 0, 20, 30)
    result = calc.estimate_gross_area(bbox)
    
    # Area should be 600 (20*30)
    assert abs(result["gross_area_m2"] - 600.0) < 1.0


def test_estimate_gross_area_empty():
    """Test gross area with empty bbox"""
    calc = AreaCalculator(scale=1.0)
    result = calc.estimate_gross_area(None)
    
    assert result["gross_area_m2"] == 0.0


def test_calculate_room_area():
    """Test room area from walls"""
    calc = AreaCalculator(scale=1.0)
    
    walls = [
        {"length_m": 10},
        {"length_m": 10},
        {"length_m": 10},
        {"length_m": 10},
    ]
    
    result = calc.calculate_room_area(walls)
    
    assert result["room_area_m2"] > 0
    assert result["wall_count"] == 4
    assert result["total_wall_length_m"] == 40.0


def test_get_summary():
    """Test summary"""
    calc = AreaCalculator(scale=1.0)
    
    segments = [
        {"start": (0, 0), "end": (10, 0)},
        {"start": (10, 0), "end": (10, 10)},
    ]
    
    calc.estimate_net_area(segments)
    summary = calc.get_summary()
    
    assert summary["total_calculations"] == 1
    assert summary["average_area_m2"] > 0