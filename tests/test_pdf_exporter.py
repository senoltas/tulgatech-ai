"""
Tests for PDFExporter
"""
from tulgatech.engine.pdf_exporter import PDFReport, PDFExporter


def test_pdf_report_init():
    """Test PDFReport initialization"""
    report = PDFReport("Test Project")
    assert report.project_name == "Test Project"
    assert report.sections == []


def test_add_section():
    """Test adding section to report"""
    report = PDFReport("Test Project")
    report.add_section("Title", "Content")
    
    assert len(report.sections) == 1
    assert report.sections[0]["title"] == "Title"


def test_report_to_dict():
    """Test report to_dict"""
    report = PDFReport("Test Project")
    report.add_section("Section 1", "Content 1")
    
    d = report.to_dict()
    assert d["project_name"] == "Test Project"
    assert d["section_count"] == 1


def test_exporter_init():
    """Test PDFExporter initialization"""
    exporter = PDFExporter()
    assert exporter.reports == []


def test_create_report():
    """Test creating report"""
    exporter = PDFExporter()
    
    analysis_result = {
        "scale": {
            "value": 0.001,
            "confidence": 0.8,
            "method": "dimension",
            "is_reliable": True
        },
        "walls": [
            {"layer": "DUVAR", "length_m": 10.0, "confidence": 0.8}
        ],
        "stats": {
            "total_segments": 100,
            "wall_candidates": 5,
            "total_wall_length_m": 50.0,
            "high_confidence_walls": 4,
            "bbox": (0, 0, 100, 100),
            "layers": ["DUVAR", "DÖŞEME"]
        }
    }
    
    report = exporter.create_report("My Project", analysis_result)
    
    assert report.project_name == "My Project"
    assert len(report.sections) > 0


def test_export_to_dict():
    """Test exporting to dictionary"""
    exporter = PDFExporter()
    report = PDFReport("Test Project")
    
    exported = exporter.export_to_dict(report)
    
    assert "report" in exported
    assert exported["format"] == "json"


def test_get_report_metadata():
    """Test getting report metadata"""
    exporter = PDFExporter()
    report = PDFReport("Test Project")
    
    metadata = exporter.get_report_metadata(report)
    
    assert metadata["project_name"] == "Test Project"
    assert "timestamp" in metadata


def test_generate_html():
    """Test generating HTML"""
    exporter = PDFExporter()
    report = PDFReport("Test Project")
    report.add_section("Section 1", "Content 1")
    
    html = exporter.generate_html(report)
    
    assert "<!DOCTYPE html>" in html
    assert "Test Project" in html
    assert "Section 1" in html


def test_list_reports():
    """Test listing reports"""
    exporter = PDFExporter()
    report = PDFReport("Test Project")
    exporter.reports.append(report)
    
    reports_list = exporter.list_reports()
    assert len(reports_list) == 1