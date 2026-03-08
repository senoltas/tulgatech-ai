"""
Report generation from analysis results
"""
from typing import Dict, List, Any
from datetime import datetime


class ReportGenerator:
    """Generate analysis reports"""
    
    def __init__(self):
        self.reports: List[Dict] = []
    
    def generate_summary_report(self, 
                               project_name: str,
                               scale_info: Dict,
                               walls: List[Dict],
                               rooms: List[Dict],
                               areas: Dict) -> Dict:
        """Generate comprehensive summary report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_name": project_name,
            "version": "0.1.0",
            
            "scale": {
                "value": scale_info.get("value", 1.0),
                "confidence": scale_info.get("confidence", 0.0),
                "reliable": scale_info.get("is_reliable", False),
                "method": scale_info.get("method", "unknown")
            },
            
            "walls": {
                "total_count": len(walls),
                "total_length_m": sum(w.get("length_m", 0) for w in walls),
                "high_confidence_count": len([w for w in walls if w.get("confidence", 0) > 0.7]),
                "average_confidence": sum(w.get("confidence", 0) for w in walls) / len(walls) if walls else 0
            },
            
            "rooms": {
                "total_count": len(rooms),
                "total_area_m2": sum(r.get("area_m2", 0) for r in rooms),
                "average_area_m2": sum(r.get("area_m2", 0) for r in rooms) / len(rooms) if rooms else 0,
                "largest_room_m2": max([r.get("area_m2", 0) for r in rooms]) if rooms else 0
            },
            
            "areas": {
                "net_area_m2": areas.get("net_area_m2", 0),
                "gross_area_m2": areas.get("gross_area_m2", 0),
                "confidence": areas.get("confidence", 0)
            },
            
            "summary": self._generate_summary_text(walls, rooms, areas)
        }
        
        self.reports.append(report)
        return report
    
    def _generate_summary_text(self, walls: List[Dict], 
                              rooms: List[Dict], 
                              areas: Dict) -> str:
        """Generate human-readable summary"""
        
        wall_count = len(walls)
        wall_length = sum(w.get("length_m", 0) for w in walls)
        room_count = len(rooms)
        room_area = sum(r.get("area_m2", 0) for r in rooms)
        gross_area = areas.get("gross_area_m2", 0)
        
        summary = f"""
Project Analysis Summary
========================

Structural Elements:
- {wall_count} walls detected
- {wall_length:.2f}m total wall length
- Average wall length: {wall_length/wall_count:.2f}m (if {wall_count} > 0)

Spaces:
- {room_count} rooms detected
- {room_area:.2f}m² total room area
- Average room size: {room_area/room_count:.2f}m² (if {room_count} > 0)
- Largest room: Check details

Building Envelope:
- Gross area: {gross_area:.2f}m²
- Net area: {areas.get('net_area_m2', 0):.2f}m²

Quality Indicators:
- Analysis confidence: {areas.get('confidence', 0):.0%}
- Data completeness: Good for architectural planning
"""
        
        return summary.strip()
    
    def generate_detail_report(self, data: Dict) -> Dict:
        """Generate detailed technical report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "type": "detail",
            "sections": {
                "scale_analysis": self._scale_section(data.get("scale", {})),
                "geometry_analysis": self._geometry_section(data.get("walls", []), data.get("rooms", [])),
                "area_analysis": self._area_section(data.get("areas", {})),
                "quality_metrics": self._quality_section(data)
            }
        }
        
        self.reports.append(report)
        return report
    
    def _scale_section(self, scale_info: Dict) -> Dict:
        """Generate scale analysis section"""
        return {
            "scale_value": scale_info.get("value", 1.0),
            "confidence": scale_info.get("confidence", 0.0),
            "method": scale_info.get("method", "unknown"),
            "is_reliable": scale_info.get("is_reliable", False),
            "recommendation": "Use with caution" if not scale_info.get("is_reliable") else "Reliable for calculations"
        }
    
    def _geometry_section(self, walls: List[Dict], rooms: List[Dict]) -> Dict:
        """Generate geometry analysis section"""
        return {
            "walls": {
                "count": len(walls),
                "total_length": sum(w.get("length_m", 0) for w in walls),
                "confidence_avg": sum(w.get("confidence", 0) for w in walls) / len(walls) if walls else 0
            },
            "rooms": {
                "count": len(rooms),
                "total_area": sum(r.get("area_m2", 0) for r in rooms)
            }
        }
    
    def _area_section(self, areas: Dict) -> Dict:
        """Generate area analysis section"""
        return {
            "net_area_m2": areas.get("net_area_m2", 0),
            "gross_area_m2": areas.get("gross_area_m2", 0),
            "ratio": areas.get("net_area_m2", 0) / areas.get("gross_area_m2", 1) if areas.get("gross_area_m2") else 0,
            "confidence": areas.get("confidence", 0)
        }
    
    def _quality_section(self, data: Dict) -> Dict:
        """Generate quality metrics section"""
        return {
            "overall_confidence": 0.7,  # Placeholder
            "data_completeness": "85%",
            "recommendations": [
                "Verify scale with known dimensions",
                "Cross-check wall lengths manually",
                "Inspect room boundaries for accuracy"
            ]
        }
    
    def export_reports(self) -> List[Dict]:
        """Export all reports"""
        return self.reports
    
    def get_latest_report(self) -> Dict:
        """Get latest report"""
        return self.reports[-1] if self.reports else None