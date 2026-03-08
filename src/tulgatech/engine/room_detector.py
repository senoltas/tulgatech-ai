"""
Room detection from segments and areas
"""
from typing import List, Dict, Tuple, Optional
import math

Point2D = Tuple[float, float]


class Room:
    """Represents a detected room"""
    def __init__(self, room_id: str):
        self.id = room_id
        self.area_m2 = 0.0
        self.perimeter_m = 0.0
        self.bbox = None
        self.center = None
        self.segments: List[Dict] = []
        self.confidence = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "area_m2": self.area_m2,
            "perimeter_m": self.perimeter_m,
            "bbox": self.bbox,
            "center": self.center,
            "segment_count": len(self.segments),
            "confidence": self.confidence
        }


class RoomDetector:
    """Detect rooms from segments"""
    
    def __init__(self, scale: float = 1.0):
        """Initialize with scale"""
        self.scale = float(scale)
        self.rooms: List[Room] = []
        self.min_room_area_m2 = 5.0
        self.max_room_area_m2 = 500.0
    
    def detect_from_walls(self, walls: List[Dict]) -> List[Room]:
        """Detect rooms from wall segments"""
        self.rooms = []
        
        if not walls:
            return []
        
        # Group walls by proximity (simple approach)
        room_id = 1
        used_walls = set()
        
        for i, wall in enumerate(walls):
            if i in used_walls:
                continue
            
            # Start new room
            room = Room(f"R{room_id:02d}")
            room.segments.append(wall)
            used_walls.add(i)
            
            # Find connected walls
            for j, other_wall in enumerate(walls):
                if j in used_walls or j <= i:
                    continue
                
                # Check if walls connect
                if self._walls_connected(wall, other_wall):
                    room.segments.append(other_wall)
                    used_walls.add(j)
            
            # Calculate room properties
            if self._calculate_room_properties(room):
                self.rooms.append(room)
                room_id += 1
        
        return self.rooms
    
    def _walls_connected(self, wall1: Dict, wall2: Dict) -> bool:
        """Check if two walls are connected"""
        e1 = wall1.get("end")
        s2 = wall2.get("start")
        
        if not e1 or not s2:
            return False
        
        # Check if end of wall1 is close to start of wall2
        dist = math.hypot(e1[0] - s2[0], e1[1] - s2[1])
        
        # Tolerance: 1 drawing unit
        return dist < 1.0
    
    def _calculate_room_properties(self, room: Room) -> bool:
        """Calculate room properties and return True if valid"""
        if not room.segments:
            return False
        
        # Calculate perimeter
        total_length = sum(s.get("length_m", 0) for s in room.segments)
        room.perimeter_m = total_length
        
        # Estimate area from perimeter (assume square)
        # Perimeter = 4*side, so Area = side^2
        if total_length > 0:
            side = total_length / 4
            room.area_m2 = side ** 2
        
        # Filter by area
        if room.area_m2 < self.min_room_area_m2:
            return False
        if room.area_m2 > self.max_room_area_m2:
            return False
        
        # Calculate center
        all_points = []
        for seg in room.segments:
            s = seg.get("start")
            e = seg.get("end")
            if s:
                all_points.append(s)
            if e:
                all_points.append(e)
        
        if all_points:
            avg_x = sum(p[0] for p in all_points) / len(all_points)
            avg_y = sum(p[1] for p in all_points) / len(all_points)
            room.center = (avg_x, avg_y)
            
            # Calculate bbox
            xs = [p[0] for p in all_points]
            ys = [p[1] for p in all_points]
            room.bbox = (min(xs), min(ys), max(xs), max(ys))
        
        # Confidence based on wall closure
        room.confidence = min(0.8, room.perimeter_m / 50)  # Max 0.8
        
        return True
    
    def get_rooms(self) -> List[Dict]:
        """Get all rooms as dictionaries"""
        return [r.to_dict() for r in self.rooms]
    
    def get_room_count(self) -> int:
        """Get total room count"""
        return len(self.rooms)
    
    def get_total_area_m2(self) -> float:
        """Get total area of all rooms"""
        return sum(r.area_m2 for r in self.rooms)
    
    def get_largest_room(self) -> Optional[Dict]:
        """Get largest room"""
        if not self.rooms:
            return None
        largest = max(self.rooms, key=lambda r: r.area_m2)
        return largest.to_dict()
    
    def filter_by_area(self, min_area: float, max_area: float) -> List[Dict]:
        """Filter rooms by area range"""
        filtered = [r for r in self.rooms 
                   if min_area <= r.area_m2 <= max_area]
        return [r.to_dict() for r in filtered]