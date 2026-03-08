"""
Wall detection from segments
"""
import math
from typing import List, Dict, Any, Tuple

Point2D = Tuple[float, float]


class WallDetector:
    """Detect walls from segments"""
    
    def __init__(self, scale: float = 1.0):
        """Initialize with scale (drawing units -> meters)"""
        self.scale = float(scale)
        self.wall_candidates: List[Dict[str, Any]] = []
    
    def detect_walls(self, segments: List[Dict[str, Any]], 
                    min_length_m: float = 0.5) -> List[Dict[str, Any]]:
        """Detect wall segments based on length and layer"""
        self.wall_candidates = []
        
        for seg in segments:
            # Get coordinates
            start = seg.get("start")
            end = seg.get("end")
            layer = seg.get("layer", "").upper()
            
            if not start or not end:
                continue
            
            # Calculate length in meters
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length_draw = math.hypot(dx, dy)
            length_m = length_draw * self.scale
            
            # Filter by length
            if length_m < min_length_m:
                continue
            # Exclude detail layers
            is_detail_layer = any(kw in layer for kw in ["DETL", "DETAIL", "ANNO", "ANNO"])
            if is_detail_layer:
                continue
            # Only accept walls with correct layer names
            is_wall_layer = any(kw in layer for kw in ["M-Duvar", "DUVAR", "WALL", "MUR"])
        
            # Exclude everything else
            is_excluded = any(kw in layer for kw in ["DETL", "ANNO", "FLOR", "LEVL", "AREA", "BEAM"])
        
            if is_excluded or not is_wall_layer:
                continue
            
            # Calculate angle
            angle = math.degrees(math.atan2(dy, dx)) % 180.0
            
            wall = {
                "start": start,
                "end": end,
                "layer": seg.get("layer", ""),
                "source": seg.get("source", ""),
                "length_m": length_m,
                "length_draw": length_draw,
                "angle": angle,
                "is_wall_layer": is_wall_layer,
                "confidence": 0.8 if is_wall_layer else 0.4
            }
            
            self.wall_candidates.append(wall)
        
        # Sort by length (longest first)
        self.wall_candidates.sort(key=lambda w: w["length_m"], reverse=True)
        
        return self.wall_candidates
    
    def get_walls_by_layer(self, layer: str) -> List[Dict[str, Any]]:
        """Get walls from specific layer"""
        return [w for w in self.wall_candidates if w["layer"] == layer]
    
    def get_total_wall_length_m(self) -> float:
        """Get total wall length in meters"""
        return sum(w["length_m"] for w in self.wall_candidates)
    
    def get_high_confidence_walls(self, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """Get walls with high confidence"""
        return [w for w in self.wall_candidates if w["confidence"] >= min_confidence]
    
    def filter_by_angle(self, angle_min: float = 0, angle_max: float = 90) -> List[Dict[str, Any]]:
        """Filter walls by angle range (0-180 degrees)"""
        return [w for w in self.wall_candidates 
                if angle_min <= w["angle"] <= angle_max]