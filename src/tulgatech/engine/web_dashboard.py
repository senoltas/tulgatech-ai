"""
Web Dashboard for TulgaTech
"""
from typing import Dict, List, Any
from datetime import datetime


class DashboardWidget:
    """Represents a dashboard widget"""
    def __init__(self, widget_id: str, widget_type: str, title: str):
        self.id = widget_id
        self.type = widget_type  # CHART, STAT, TABLE, MAP
        self.title = title
        self.data = {}
        self.refresh_interval = 60  # seconds
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "data": self.data,
            "refresh_interval": self.refresh_interval
        }


class DashboardPage:
    """Represents a dashboard page"""
    def __init__(self, page_id: str, page_name: str):
        self.id = page_id
        self.name = page_name
        self.widgets: List[DashboardWidget] = []
        self.created_at = datetime.now().isoformat()
    
    def add_widget(self, widget: DashboardWidget):
        """Add widget to page"""
        self.widgets.append(widget)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "widget_count": len(self.widgets),
            "widgets": [w.to_dict() for w in self.widgets],
            "created_at": self.created_at
        }


class WebDashboard:
    """Web Dashboard interface"""
    
    def __init__(self):
        self.pages: Dict[str, DashboardPage] = {}
        self.current_page = None
        self.theme = "light"  # light, dark
        self.is_responsive = True
        self._initialize_pages()
    
    def _initialize_pages(self):
        """Initialize dashboard pages"""
        
        # Overview page
        overview = DashboardPage("overview", "Overview")
        
        widget1 = DashboardWidget("w1", "STAT", "Total Projects")
        widget1.data = {"value": 5, "unit": "projects"}
        overview.add_widget(widget1)
        
        widget2 = DashboardWidget("w2", "STAT", "Total Analysis")
        widget2.data = {"value": 42, "unit": "analyses"}
        overview.add_widget(widget2)
        
        widget3 = DashboardWidget("w3", "CHART", "Analysis Trends")
        widget3.data = {"trend": "up", "percentage": 23}
        overview.add_widget(widget3)
        
        self.pages["overview"] = overview
        self.current_page = "overview"
        
        # Projects page
        projects = DashboardPage("projects", "Projects")
        
        widget4 = DashboardWidget("w4", "TABLE", "Recent Projects")
        widget4.data = {
            "columns": ["Name", "Status", "Progress"],
            "rows": []
        }
        projects.add_widget(widget4)
        
        self.pages["projects"] = projects
        
        # Analytics page
        analytics = DashboardPage("analytics", "Analytics")
        
        widget5 = DashboardWidget("w5", "MAP", "Building Footprints")
        widget5.data = {"center": [0, 0], "zoom": 10}
        analytics.add_widget(widget5)
        
        widget6 = DashboardWidget("w6", "CHART", "Cost Distribution")
        widget6.data = {
            "categories": ["Materials", "Labor", "Equipment"],
            "values": [45, 35, 20]
        }
        analytics.add_widget(widget6)
        
        self.pages["analytics"] = analytics
    
    def get_page(self, page_id: str) -> DashboardPage:
        """Get dashboard page"""
        return self.pages.get(page_id)
    
    def get_all_pages(self) -> List[Dict]:
        """Get all pages"""
        return [p.to_dict() for p in self.pages.values()]
    
    def switch_page(self, page_id: str) -> Dict:
        """Switch to different page"""
        if page_id not in self.pages:
            return {"error": "Page not found"}
        
        self.current_page = page_id
        return {
            "status": "switched",
            "current_page": page_id,
            "page_data": self.pages[page_id].to_dict()
        }
    
    def set_theme(self, theme: str) -> Dict:
        """Set dashboard theme"""
        if theme not in ["light", "dark"]:
            return {"error": "Invalid theme"}
        
        self.theme = theme
        return {
            "status": "updated",
            "theme": theme
        }
    
    def get_dashboard_config(self) -> Dict:
        """Get dashboard configuration"""
        return {
            "name": "TulgaTech Dashboard",
            "version": "1.0.0",
            "theme": self.theme,
            "is_responsive": self.is_responsive,
            "pages": len(self.pages),
            "current_page": self.current_page,
            "page_list": [p.id for p in self.pages.values()]
        }
    
    def get_overview_stats(self) -> Dict:
        """Get overview statistics"""
        overview_page = self.pages.get("overview")
        
        if not overview_page:
            return {}
        
        stats = {}
        for widget in overview_page.widgets:
            if widget.type == "STAT":
                stats[widget.title] = widget.data
        
        return stats
    
    def refresh_data(self, page_id: str) -> Dict:
        """Refresh page data"""
        page = self.pages.get(page_id)
        
        if not page:
            return {"error": "Page not found"}
        
        return {
            "status": "refreshed",
            "page": page_id,
            "timestamp": datetime.now().isoformat(),
            "widget_count": len(page.widgets)
        }
    
    def export_dashboard_html(self) -> str:
        """Export dashboard as HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TulgaTech Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #333; color: white; padding: 20px; border-radius: 5px; }}
        .pages {{ display: flex; gap: 10px; margin: 20px 0; }}
        .page-btn {{ padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }}
        .widgets {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .widget {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .widget-title {{ font-weight: bold; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>TulgaTech AI Dashboard</h1>
            <p>Construction Data Intelligence Platform</p>
        </div>
        
        <div class="pages">
"""
        
        for page_id in self.pages.keys():
            html += f'            <button class="page-btn">{page_id.upper()}</button>\n'
        
        html += """
        </div>
        
        <div class="widgets">
"""
        
        # Add widgets from current page
        if self.current_page in self.pages:
            page = self.pages[self.current_page]
            for widget in page.widgets:
                html += f"""
            <div class="widget">
                <div class="widget-title">{widget.title}</div>
                <p>{widget.data}</p>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html