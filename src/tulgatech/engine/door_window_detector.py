"""
Door and window detection from segments
"""
from typing import List, Dict, Tuple
import math

Point2D = Tuple[float, float]


class Opening:
    """Represents a door or window opening"""
    def __init__(self, opening_id: str, opening_type: str):
        self.id = opening_id
        self.type = opening_type  # "DOOR" or "WINDOW"
        self.width_m = 0.0
        self.height_m = 0.0
        self.position = None  # (x, y)
        self.layer = ""
        self.confidence = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "width_m": self.width_m,
            "height_m": self.height_m,
            "position": self.position,
            "layer": self.layer,
            "confidence": self.confidence
        }


class DoorWindowDetector:
    """Detect doors and windows"""
    
    def __init__(self, scale: float = 1.0):
        """Initialize with scale"""
        self.scale = float(scale)
        self.openings: List[Opening] = []
    
    def detect_from_segments(self, segments: List[Dict]) -> List[Opening]:
        """Detect doors/windows from segments"""
        self.openings = []
        
        # Typical dimensions (in meters)
        DOOR_WIDTH = 0.90
        DOOR_HEIGHT = 2.10
        WINDOW_WIDTH = 1.20
        WINDOW_HEIGHT = 1.50
        
        tolerance = 0.2  # 20% tolerance
        
        opening_id = 1
        
        for seg in segments:
            start = seg.get("start")
            end = seg.get("end")
            layer = seg.get("layer", "").upper()
            
            if not start or not end:
                continue
            
            # Calculate segment length
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length_draw = math.hypot(dx, dy)
            length_m = length_draw * self.scale
            
            # Check if matches door width
            if (DOOR_WIDTH * (1 - tolerance) <= length_m <= 
                DOOR_WIDTH * (1 + tolerance)):
                
                opening = Opening(f"D{opening_id:03d}", "DOOR")
                opening.width_m = length_m
                opening.height_m = DOOR_HEIGHT  # Standard door height
                opening.position = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
                opening.layer = layer
                opening.confidence = 0.8
                
                self.openings.append(opening)
                opening_id += 1
            
            # Check if matches window width
            elif (WINDOW_WIDTH * (1 - tolerance) <= length_m <= 
                  WINDOW_WIDTH * (1 + tolerance)):
                
                opening = Opening(f"W{opening_id:03d}", "WINDOW")
                opening.width_m = length_m
                opening.height_m = WINDOW_HEIGHT
                opening.position = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
                opening.layer = layer
                opening.confidence = 0.7
                
                self.openings.append(opening)
                opening_id += 1
        
        return self.openings
    
    def get_doors(self) -> List[Dict]:
        """Get all doors"""
        return [o.to_dict() for o in self.openings if o.type == "DOOR"]
    
    def get_windows(self) -> List[Dict]:
        """Get all windows"""
        return [o.to_dict() for o in self.openings if o.type == "WINDOW"]
    
    def get_opening_count(self) -> int:
        """Get total opening count"""
        return len(self.openings)
    
    def get_door_count(self) -> int:
        """Get door count"""
        return len(self.get_doors())
    
    def get_window_count(self) -> int:
        """Get window count"""
        return len(self.get_windows())
    
    def estimate_door_area_m2(self) -> float:
        """Estimate total door area"""
        doors = self.get_doors()
        return sum(d.get("width_m", 0) * d.get("height_m", 0) for d in doors)
    
    def estimate_window_area_m2(self) -> float:
        """Estimate total window area"""
        windows = self.get_windows()
        return sum(w.get("width_m", 0) * w.get("height_m", 0) for w in windows)