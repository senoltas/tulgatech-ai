"""
Tests for MaterialEstimator
"""
from tulgatech.engine.material_estimator import MaterialEstimate, MaterialEstimator


def test_material_estimate_init():
    """Test MaterialEstimate initialization"""
    estimate = MaterialEstimate("PAINT")
    assert estimate.type == "PAINT"
    assert estimate.quantity == 0.0


def test_estimator_init():
    """Test MaterialEstimator initialization"""
    estimator = MaterialEstimator()
    assert estimator.estimates == []
    assert "paint" in estimator.unit_costs


def test_estimate_paint():
    """Test paint estimation"""
    estimator = MaterialEstimator()
    
    walls = [
        {"length_m": 10.0},
        {"length_m": 15.0},
    ]
    
    estimate = estimator.estimate_paint(walls)
    
    assert estimate.type == "PAINT"
    assert estimate.quantity > 0
    assert estimate.unit == "m2"
    assert estimate.total_cost > 0


def test_estimate_flooring():
    """Test flooring estimation"""
    estimator = MaterialEstimator()
    
    rooms = [
        {"area_m2": 25.0},
        {"area_m2": 30.0},
    ]
    
    estimate = estimator.estimate_flooring(rooms)
    
    assert estimate.type == "FLOORING"
    assert estimate.quantity > 0


def test_estimate_plaster():
    """Test plaster estimation"""
    estimator = MaterialEstimator()
    
    walls = [
        {"length_m": 10.0},
    ]
    
    estimate = estimator.estimate_plaster(walls)
    
    assert estimate.type == "PLASTER"
    assert estimate.quantity > 0


def test_estimate_tiles():
    """Test tile estimation"""
    estimator = MaterialEstimator()
    
    rooms = [
        {"area_m2": 20.0},
    ]
    
    estimate = estimator.estimate_tiles(rooms)
    
    assert estimate.type == "TILES"
    assert estimate.quantity > 0


def test_get_total_cost():
    """Test total cost calculation"""
    estimator = MaterialEstimator()
    
    walls = [{"length_m": 10.0}]
    rooms = [{"area_m2": 25.0}]
    
    estimator.estimate_paint(walls)
    estimator.estimate_flooring(rooms)
    
    total = estimator.get_total_cost()
    assert total > 0


def test_generate_summary():
    """Test summary generation"""
    estimator = MaterialEstimator()
    
    walls = [{"length_m": 10.0}]
    rooms = [{"area_m2": 25.0}]
    
    estimator.estimate_paint(walls)
    estimator.estimate_flooring(rooms)
    
    summary = estimator.generate_summary()
    
    assert "total_estimated_cost" in summary
    assert "materials" in summary