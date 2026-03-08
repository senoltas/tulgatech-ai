"""
Area calculation from segments
"""
import math
from typing import List, Dict, Tuple, Optional

Point2D = Tuple[float, float]


class AreaCalculator:
    """Calculate areas from segments"""
    
    def __init__(self, scale: float = 1.0):
        """Initialize with scale (drawing units -> meters)"""
        self.scale = float(scale)
        self.calculated_areas: List[Dict] = []
    
    def polygon_area(self, points: List[Point2D]) -> float:
        """Calculate polygon area using shoelace formula"""
        if len(points) < 3:
            return 0.0
        
        area = 0.0
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        
        return abs(area) / 2.0
    
    def estimate_net_area(self, segments: List[Dict], 
                         scale: float = None) -> Dict:
        """Estimate net area from segments"""
        if scale is None:
            scale = self.scale
        
        # Get all points from segments
        points = []
        for seg in segments:
            start = seg.get("start")
            end = seg.get("end")
            if start:
                points.append(start)
            if end:
                points.append(end)
        
        if len(points) < 3:
            return {
                "net_area_m2": 0.0,
                "points_count": len(points),
                "confidence": 0.0,
                "method": "insufficient_data"
            }
        
        # Convex hull approach (simplified)
        # For now, use bounding box as approximation
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        
        width_draw = max(xs) - min(xs)
        height_draw = max(ys) - min(ys)
        
        bbox_area_draw = width_draw * height_draw
        bbox_area_m2 = bbox_area_draw * (scale ** 2)
        
        # Estimate: actual area is ~70% of bounding box
        estimated_net = bbox_area_m2 * 0.7
        
        result = {
            "net_area_m2": estimated_net,
            "bbox_area_m2": bbox_area_m2,
            "points_count": len(points),
            "width_m": width_draw * scale,
            "height_m": height_draw * scale,
            "confidence": 0.5,  # Low confidence without proper polygon
            "method": "bounding_box_approximation"
        }
        
        self.calculated_areas.append(result)
        return result
    
    def estimate_gross_area(self, bbox: Tuple) -> Dict:
        """Estimate gross area from bounding box"""
        if not bbox or len(bbox) < 4:
            return {
                "gross_area_m2": 0.0,
                "confidence": 0.0
            }
        
        minx, miny, maxx, maxy = bbox
        width_draw = maxx - minx
        height_draw = maxy - miny
        
        gross_area_draw = width_draw * height_draw
        gross_area_m2 = gross_area_draw * (self.scale ** 2)
        
        return {
            "gross_area_m2": gross_area_m2,
            "width_m": width_draw * self.scale,
            "height_m": height_draw * self.scale,
            "confidence": 0.6,
            "method": "bbox"
        }
    
    def calculate_room_area(self, walls: List[Dict], 
                           wall_thickness_m: float = 0.25) -> Dict:
        """Calculate room area from walls"""
        if not walls:
            return {
                "room_area_m2": 0.0,
                "wall_count": 0,
                "confidence": 0.0
            }
        
        # Simple approach: average wall length * average distance
        lengths = [w.get("length_m", 0) for w in walls]
        total_length = sum(lengths)
        
        # Assume roughly square room
        avg_side = total_length / 4 if total_length > 0 else 0
        room_area = avg_side ** 2
        
        # Subtract wall thickness effect
        perimeter_reduction = wall_thickness_m * 4 * 2
        room_area = max(0, room_area - perimeter_reduction)
        
        return {
            "room_area_m2": room_area,
            "wall_count": len(walls),
            "total_wall_length_m": total_length,
            "confidence": 0.3,  # Low confidence
            "method": "wall_based_approximation"
        }
    
    def get_summary(self) -> Dict:
        """Get summary of all calculations"""
        if not self.calculated_areas:
            return {
                "total_calculations": 0,
                "average_area_m2": 0.0
            }
        
        areas = [a.get("net_area_m2", 0) for a in self.calculated_areas]
        total = sum(areas)
        avg = total / len(areas) if areas else 0
        
        return {
            "total_calculations": len(self.calculated_areas),
            "total_area_m2": total,
            "average_area_m2": avg,
            "areas": [a.get("net_area_m2", 0) for a in self.calculated_areas]
        }