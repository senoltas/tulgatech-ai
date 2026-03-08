"""
Tests for ReportGenerator
"""
from tulgatech.engine.report_generator import ReportGenerator


def test_report_generator_init():
    """Test ReportGenerator initialization"""
    gen = ReportGenerator()
    assert gen.reports == []


def test_generate_summary_report():
    """Test generating summary report"""
    gen = ReportGenerator()
    
    scale_info = {
        "value": 0.001,
        "confidence": 0.8,
        "is_reliable": True,
        "method": "dimension"
    }
    
    walls = [
        {"length_m": 10.0, "confidence": 0.8},
        {"length_m": 15.0, "confidence": 0.7},
    ]
    
    rooms = [
        {"area_m2": 25.0},
        {"area_m2": 30.0},
    ]
    
    areas = {
        "net_area_m2": 50.0,
        "gross_area_m2": 60.0,
        "confidence": 0.75
    }
    
    report = gen.generate_summary_report("Test Project", scale_info, walls, rooms, areas)
    
    assert report["project_name"] == "Test Project"
    assert report["walls"]["total_count"] == 2
    assert report["rooms"]["total_count"] == 2
    assert "summary" in report


def test_summary_text():
    """Test summary text generation"""
    gen = ReportGenerator()
    
    walls = [{"length_m": 10.0, "confidence": 0.8}]
    rooms = [{"area_m2": 25.0}]
    areas = {"net_area_m2": 50.0, "gross_area_m2": 60.0, "confidence": 0.75}
    
    summary = gen._generate_summary_text(walls, rooms, areas)
    
    assert "1 walls detected" in summary
    assert "1 rooms detected" in summary
    assert "60.00m²" in summary


def test_generate_detail_report():
    """Test generating detailed report"""
    gen = ReportGenerator()
    
    data = {
        "scale": {"value": 0.001, "confidence": 0.8, "is_reliable": True},
        "walls": [{"length_m": 10.0}],
        "rooms": [{"area_m2": 25.0}],
        "areas": {"net_area_m2": 50.0, "gross_area_m2": 60.0, "confidence": 0.75}
    }
    
    report = gen.generate_detail_report(data)
    
    assert report["type"] == "detail"
    assert "sections" in report
    assert "scale_analysis" in report["sections"]


def test_export_reports():
    """Test exporting reports"""
    gen = ReportGenerator()
    
    scale_info = {"value": 0.001, "confidence": 0.8, "is_reliable": True, "method": "dimension"}
    walls = [{"length_m": 10.0, "confidence": 0.8}]
    rooms = [{"area_m2": 25.0}]
    areas = {"net_area_m2": 50.0, "gross_area_m2": 60.0, "confidence": 0.75}
    
    gen.generate_summary_report("Test", scale_info, walls, rooms, areas)
    
    reports = gen.export_reports()
    assert len(reports) == 1


def test_get_latest_report():
    """Test getting latest report"""
    gen = ReportGenerator()
    
    assert gen.get_latest_report() is None
    
    scale_info = {"value": 0.001, "confidence": 0.8, "is_reliable": True, "method": "dimension"}
    walls = [{"length_m": 10.0, "confidence": 0.8}]
    rooms = [{"area_m2": 25.0}]
    areas = {"net_area_m2": 50.0, "gross_area_m2": 60.0, "confidence": 0.75}
    
    gen.generate_summary_report("Test", scale_info, walls, rooms, areas)
    
    latest = gen.get_latest_report()
    assert latest is not None
    assert latest["project_name"] == "Test"


def test_scale_section():
    """Test scale section generation"""
    gen = ReportGenerator()
    
    scale_info = {
        "value": 0.001,
        "confidence": 0.8,
        "method": "dimension",
        "is_reliable": True
    }
    
    section = gen._scale_section(scale_info)
    
    assert section["scale_value"] == 0.001
    assert section["is_reliable"] == True


def test_quality_section():
    """Test quality section generation"""
    gen = ReportGenerator()
    
    data = {}
    section = gen._quality_section(data)
    
    assert "overall_confidence" in section
    assert "recommendations" in section
    assert len(section["recommendations"]) > 0