"""
Tests for Web Dashboard
"""
from tulgatech.engine.web_dashboard import DashboardWidget, DashboardPage, WebDashboard


def test_dashboard_widget_init():
    """Test DashboardWidget initialization"""
    widget = DashboardWidget("w1", "STAT", "Total Projects")
    assert widget.id == "w1"
    assert widget.type == "STAT"


def test_dashboard_page_init():
    """Test DashboardPage initialization"""
    page = DashboardPage("p1", "Overview")
    assert page.id == "p1"
    assert page.name == "Overview"
    assert len(page.widgets) == 0


def test_add_widget_to_page():
    """Test adding widget to page"""
    page = DashboardPage("p1", "Overview")
    widget = DashboardWidget("w1", "STAT", "Total Projects")
    
    page.add_widget(widget)
    
    assert len(page.widgets) == 1


def test_dashboard_init():
    """Test WebDashboard initialization"""
    dashboard = WebDashboard()
    assert dashboard.theme == "light"
    assert len(dashboard.pages) > 0


def test_get_page():
    """Test getting page"""
    dashboard = WebDashboard()
    page = dashboard.get_page("overview")
    
    assert page is not None
    assert page.id == "overview"


def test_get_all_pages():
    """Test getting all pages"""
    dashboard = WebDashboard()
    pages = dashboard.get_all_pages()
    
    assert len(pages) > 0
    assert all("id" in p for p in pages)


def test_switch_page():
    """Test switching pages"""
    dashboard = WebDashboard()
    result = dashboard.switch_page("projects")
    
    assert result["status"] == "switched"
    assert dashboard.current_page == "projects"


def test_set_theme():
    """Test setting theme"""
    dashboard = WebDashboard()
    result = dashboard.set_theme("dark")
    
    assert result["status"] == "updated"
    assert dashboard.theme == "dark"


def test_get_dashboard_config():
    """Test getting dashboard config"""
    dashboard = WebDashboard()
    config = dashboard.get_dashboard_config()
    
    assert config["name"] == "TulgaTech Dashboard"
    assert config["theme"] == "light"
    assert len(config["page_list"]) > 0


def test_export_dashboard_html():
    """Test exporting dashboard as HTML"""
    dashboard = WebDashboard()
    html = dashboard.export_dashboard_html()
    
    assert "<!DOCTYPE html>" in html
    assert "TulgaTech" in html
    assert "dashboard" in html.lower()