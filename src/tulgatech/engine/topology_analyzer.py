"""
Topology analyzer - room connectivity and adjacency detection
"""
from typing import List, Dict, Set, Tuple
import math

Point2D = Tuple[float, float]


class RoomTopology:
    """Represents room topology and connections"""
    def __init__(self, room_id: str):
        self.id = room_id
        self.adjacent_rooms: Set[str] = set()
        self.connections: List[Dict] = []
        self.perimeter_m = 0.0
        self.area_m2 = 0.0
        self.accessible = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "adjacent_rooms": list(self.adjacent_rooms),
            "connection_count": len(self.connections),
            "perimeter_m": self.perimeter_m,
            "area_m2": self.area_m2,
            "accessible": self.accessible
        }


class TopologyAnalyzer:
    """Analyze room topology and connectivity"""
    
    def __init__(self):
        self.rooms: Dict[str, RoomTopology] = {}
        self.adjacency_matrix: Dict[str, Set[str]] = {}
    
    def analyze_connectivity(self, rooms: List[Dict], 
                           walls: List[Dict]) -> Dict:
        """Analyze room connectivity from walls"""
        self.rooms = {}
        self.adjacency_matrix = {}
        
        # Initialize rooms
        for i, room in enumerate(rooms):
            room_id = room.get("id", f"R{i:02d}")
            topology = RoomTopology(room_id)
            topology.area_m2 = room.get("area_m2", 0.0)
            topology.perimeter_m = room.get("perimeter_m", 0.0)
            self.rooms[room_id] = topology
            self.adjacency_matrix[room_id] = set()
        
        # Detect adjacencies (simplified: rooms sharing walls)
        room_list = list(self.rooms.keys())
        for i, room1_id in enumerate(room_list):
            for room2_id in room_list[i+1:]:
                # Check if rooms are adjacent (simplified logic)
                room1 = rooms[i] if i < len(rooms) else {}
                room2 = rooms[i+1] if i+1 < len(rooms) else {}
                
                # If rooms are close, consider them adjacent
                if self._are_adjacent(room1, room2):
                    self.rooms[room1_id].adjacent_rooms.add(room2_id)
                    self.rooms[room2_id].adjacent_rooms.add(room1_id)
                    self.adjacency_matrix[room1_id].add(room2_id)
                    self.adjacency_matrix[room2_id].add(room1_id)
        
        return {
            "rooms_analyzed": len(self.rooms),
            "adjacencies_found": sum(len(adj) for adj in self.adjacency_matrix.values()) // 2,
            "topology": [r.to_dict() for r in self.rooms.values()]
        }
    
    def _are_adjacent(self, room1: Dict, room2: Dict) -> bool:
        """Check if two rooms are adjacent"""
        if not room1 or not room2:
            return False
        
        bbox1 = room1.get("bbox")
        bbox2 = room2.get("bbox")
        
        if not bbox1 or not bbox2:
            return False
        
        # Simple check: rooms touch or overlap on edges
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        # Check if bboxes are adjacent (tolerance: 1 unit)
        tolerance = 1.0
        
        # Horizontal adjacency
        if abs(x1_max - x2_min) < tolerance or abs(x2_max - x1_min) < tolerance:
            if not (y1_max < y2_min or y2_max < y1_min):
                return True
        
        # Vertical adjacency
        if abs(y1_max - y2_min) < tolerance or abs(y2_max - y1_min) < tolerance:
            if not (x1_max < x2_min or x2_max < x1_min):
                return True
        
        return False
    
    def get_adjacency_matrix(self) -> Dict[str, List[str]]:
        """Get adjacency matrix as dictionary"""
        return {room_id: list(adjacent) 
                for room_id, adjacent in self.adjacency_matrix.items()}
    
    def is_accessible(self, room_id: str) -> bool:
        """Check if room is accessible from main entry"""
        if room_id not in self.rooms:
            return False
        
        # BFS to check connectivity
        visited = set()
        queue = [room_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Add adjacent rooms to queue
            for adjacent in self.rooms[current].adjacent_rooms:
                if adjacent not in visited:
                    queue.append(adjacent)
        
        # Room is accessible if connected to others
        return len(visited) > 1 or len(self.rooms) == 1
    
    def analyze_flow(self) -> Dict:
        """Analyze spatial flow and connectivity"""
        # Calculate average connections per room
        avg_connections = (sum(len(adj) for adj in self.adjacency_matrix.values()) 
                          / len(self.adjacency_matrix) if self.adjacency_matrix else 0)
        
        # Find central rooms (most connections)
        central_rooms = sorted(
            self.rooms.keys(),
            key=lambda r: len(self.rooms[r].adjacent_rooms),
            reverse=True
        )
        
        return {
            "total_rooms": len(self.rooms),
            "average_connections": avg_connections,
            "central_rooms": central_rooms[:3] if central_rooms else [],
            "accessibility": {
                room_id: self.is_accessible(room_id)
                for room_id in self.rooms.keys()
            }
        }