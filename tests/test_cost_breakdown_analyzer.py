"""
Tests for CostBreakdownAnalyzer
"""
from tulgatech.engine.cost_breakdown_analyzer import CostItem, CostBreakdownAnalyzer


def test_cost_item_init():
    """Test CostItem initialization"""
    item = CostItem("C001", "MATERIALS", "Paint")
    assert item.id == "C001"
    assert item.category == "MATERIALS"


def test_cost_item_calculation():
    """Test cost calculation"""
    item = CostItem("C001", "MATERIALS", "Paint")
    item.quantity = 100
    item.unit_cost = 15.0
    item.markup_percent = 15.0
    
    item.calculate_cost()
    
    # 100 * 15 = 1500, + 15% = 1725
    assert abs(item.final_cost - 1725.0) < 0.1


def test_analyzer_init():
    """Test CostBreakdownAnalyzer initialization"""
    analyzer = CostBreakdownAnalyzer()
    assert analyzer.items == []
    assert analyzer.contingency_percent == 10.0


def test_add_cost_item():
    """Test adding cost item"""
    analyzer = CostBreakdownAnalyzer()
    
    item = CostItem("C001", "MATERIALS", "Paint")
    item.quantity = 100
    item.unit_cost = 15.0
    item.markup_percent = 15.0
    
    analyzer.add_cost_item(item)
    
    assert len(analyzer.items) == 1
    assert "MATERIALS" in analyzer.categories


def test_analyze_materials():
    """Test material cost analysis"""
    analyzer = CostBreakdownAnalyzer()
    
    materials = [
        {"type": "PAINT", "quantity": 100, "unit": "m2", "cost_per_unit": 15.0},
        {"type": "FLOORING", "quantity": 50, "unit": "m2", "cost_per_unit": 50.0},
    ]
    
    result = analyzer.analyze_materials(materials)
    
    assert result["material_items"] == 2
    assert result["material_total"] > 0


def test_analyze_labor():
    """Test labor cost analysis"""
    analyzer = CostBreakdownAnalyzer()
    
    labor = {"total_worker_days": 50}
    result = analyzer.analyze_labor(labor)
    
    assert result["worker_days"] == 50
    assert result["labor_total"] > 0


def test_analyze_equipment():
    """Test equipment cost analysis"""
    analyzer = CostBreakdownAnalyzer()
    
    result = analyzer.analyze_equipment(30)
    
    assert result["duration_days"] == 30
    assert result["equipment_total"] > 0


def test_calculate_contingency():
    """Test contingency calculation"""
    analyzer = CostBreakdownAnalyzer()
    
    item = CostItem("C001", "MATERIALS", "Paint")
    item.quantity = 100
    item.unit_cost = 15.0
    item.markup_percent = 0.0
    
    analyzer.add_cost_item(item)
    
    contingency = analyzer.calculate_contingency()
    # 1500 * 10% = 150
    assert abs(contingency - 150.0) < 0.1


def test_get_detailed_breakdown():
    """Test detailed breakdown"""
    analyzer = CostBreakdownAnalyzer()
    
    item = CostItem("C001", "MATERIALS", "Paint")
    item.quantity = 100
    item.unit_cost = 15.0
    item.markup_percent = 0.0
    
    analyzer.add_cost_item(item)
    
    breakdown = analyzer.get_detailed_breakdown()
    
    assert "items" in breakdown
    assert "total_cost" in breakdown
    assert breakdown["total_cost"] > 0