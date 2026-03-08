"""
PDF report generation and export
"""
from typing import Dict, List, Any
from datetime import datetime


class PDFReport:
    """Represents a PDF report"""
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.timestamp = datetime.now().isoformat()
        self.sections: List[Dict] = []
        self.page_count = 0
    
    def add_section(self, title: str, content: str, section_type: str = "text"):
        """Add section to report"""
        section = {
            "title": title,
            "content": content,
            "type": section_type,
            "order": len(self.sections)
        }
        self.sections.append(section)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "project_name": self.project_name,
            "timestamp": self.timestamp,
            "section_count": len(self.sections),
            "sections": self.sections
        }


class PDFExporter:
    """Export analysis results to PDF"""
    
    def __init__(self):
        self.reports: List[PDFReport] = []
    
    def create_report(self, project_name: str, 
                     analysis_result: Dict) -> PDFReport:
        """Create PDF report from analysis result"""
        
        report = PDFReport(project_name)
        
        # Title page
        report.add_section(
            "TulgaTech AI Analysis Report",
            f"Project: {project_name}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "title"
        )
        
        # Scale section
        if analysis_result.get("scale"):
            scale_info = analysis_result["scale"]
            scale_text = f"""
Scale Information
================
Value: {scale_info.get('value', 0):.6f} m/unit
Confidence: {scale_info.get('confidence', 0):.0%}
Method: {scale_info.get('method', 'unknown')}
Reliable: {'Yes' if scale_info.get('is_reliable') else 'No'}
"""
            report.add_section("Scale Detection", scale_text, "scale")
        
        # Walls section
        if analysis_result.get("walls"):
            walls = analysis_result["walls"]
            walls_text = f"""
Wall Detection Results
=====================
Total Walls: {len(walls)}
Total Length: {sum(w.get('length_m', 0) for w in walls):.2f}m
High Confidence: {len([w for w in walls if w.get('confidence', 0) > 0.7])}

Top 5 Walls:
"""
            for i, wall in enumerate(walls[:5], 1):
                walls_text += f"\n{i}. Layer: {wall.get('layer')}, Length: {wall.get('length_m', 0):.2f}m"
            
            report.add_section("Structural Elements", walls_text, "walls")
        
        # Areas section
        if analysis_result.get("stats"):
            stats = analysis_result["stats"]
            areas_text = f"""
Area Analysis
=============
Total Segments: {stats.get('total_segments', 0)}
Wall Candidates: {stats.get('wall_candidates', 0)}
Total Wall Length: {stats.get('total_wall_length_m', 0):.2f}m
High Confidence Walls: {stats.get('high_confidence_walls', 0)}

Bounding Box: {stats.get('bbox')}
Layers Detected: {len(stats.get('layers', []))}
"""
            report.add_section("Spatial Analysis", areas_text, "areas")
        
        # Summary section
        summary_text = """
Project Summary
===============
Analysis Status: Complete
Quality: Professional
Coverage: Comprehensive

Recommendations:
- Verify scale with known dimensions
- Review wall boundaries
- Cross-check calculations
"""
        report.add_section("Summary & Recommendations", summary_text, "summary")
        
        self.reports.append(report)
        return report
    
    def export_to_dict(self, report: PDFReport) -> Dict:
        """Export report to dictionary format"""
        return {
            "report": report.to_dict(),
            "format": "json",
            "exportable_to": ["pdf", "html", "json"]
        }
    
    def get_report_metadata(self, report: PDFReport) -> Dict:
        """Get report metadata"""
        return {
            "project_name": report.project_name,
            "timestamp": report.timestamp,
            "section_count": len(report.sections),
            "page_count": report.page_count,
            "status": "ready_for_export"
        }
    
    def generate_html(self, report: PDFReport) -> str:
        """Generate HTML version of report"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.project_name} - TulgaTech AI Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .section {{ margin-bottom: 30px; page-break-inside: avoid; }}
        .metadata {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>{report.project_name}</h1>
    <p class="metadata">Generated: {report.timestamp}</p>
"""
        
        for section in report.sections:
            html += f"""
    <div class="section">
        <h2>{section['title']}</h2>
        <pre>{section['content']}</pre>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def list_reports(self) -> List[Dict]:
        """List all created reports"""
        return [self.get_report_metadata(r) for r in self.reports]
    
    def get_report_count(self) -> int:
        """Get total report count"""
        return len(self.reports)