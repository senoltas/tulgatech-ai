"""
3D model generation from 2D analysis
"""
from typing import List, Dict, Tuple
import math

Point2D = Tuple[float, float]
Point3D = Tuple[float, float, float]


class Wall3D:
    """Represents a 3D wall"""
    def __init__(self, wall_id: str):
        self.id = wall_id
        self.start_2d: Point2D = None
        self.end_2d: Point2D = None
        self.height_m = 3.0
        self.thickness_m = 0.25
        self.vertices: List[Point3D] = []
        self.material = "concrete"
    
    def generate_vertices(self) -> List[Point3D]:
        """Generate 3D vertices for wall"""
        if not self.start_2d or not self.end_2d:
            return []
        
        x1, y1 = self.start_2d
        x2, y2 = self.end_2d
        h = self.height_m
        t = self.thickness_m
        
        # Calculate perpendicular direction
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        
        if length == 0:
            return []
        
        # Perpendicular unit vector
        px = -dy / length * t
        py = dx / length * t
        
        # 8 vertices (4 bottom, 4 top)
        self.vertices = [
            # Bottom face
            (x1, y1, 0),
            (x1 + px, y1 + py, 0),
            (x2 + px, y2 + py, 0),
            (x2, y2, 0),
            # Top face
            (x1, y1, h),
            (x1 + px, y1 + py, h),
            (x2 + px, y2 + py, h),
            (x2, y2, h),
        ]
        
        return self.vertices
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "start_2d": self.start_2d,
            "end_2d": self.end_2d,
            "height_m": self.height_m,
            "thickness_m": self.thickness_m,
            "vertices": self.vertices,
            "material": self.material
        }


class Room3D:
    """Represents a 3D room"""
    def __init__(self, room_id: str):
        self.id = room_id
        self.bbox_2d: Tuple = None
        self.height_m = 2.7
        self.floor_vertices: List[Point3D] = []
        self.ceiling_vertices: List[Point3D] = []
        self.volume_m3 = 0.0
    
    def generate_vertices(self) -> Dict:
        """Generate floor and ceiling vertices"""
        if not self.bbox_2d:
            return {}
        
        minx, miny, maxx, maxy = self.bbox_2d
        h = self.height_m
        
        # Floor (z=0)
        self.floor_vertices = [
            (minx, miny, 0),
            (maxx, miny, 0),
            (maxx, maxy, 0),
            (minx, maxy, 0),
        ]
        
        # Ceiling (z=height)
        self.ceiling_vertices = [
            (minx, miny, h),
            (maxx, miny, h),
            (maxx, maxy, h),
            (minx, maxy, h),
        ]
        
        # Calculate volume
        width = maxx - minx
        depth = maxy - miny
        self.volume_m3 = width * depth * h
        
        return {
            "floor": self.floor_vertices,
            "ceiling": self.ceiling_vertices,
            "volume_m3": self.volume_m3
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "bbox_2d": self.bbox_2d,
            "height_m": self.height_m,
            "volume_m3": self.volume_m3,
            "floor_vertices": self.floor_vertices,
            "ceiling_vertices": self.ceiling_vertices
        }


class Model3DGenerator:
    """Generate 3D models from 2D analysis"""
    
    def __init__(self):
        self.walls_3d: List[Wall3D] = []
        self.rooms_3d: List[Room3D] = []
        self.model_format = "obj"  # OBJ, STL, GLTF
    
    def generate_from_2d(self, walls_2d: List[Dict], 
                        rooms_2d: List[Dict]) -> Dict:
        """Generate 3D model from 2D analysis"""
        
        self.walls_3d = []
        self.rooms_3d = []
        
        # Generate 3D walls
        for i, wall in enumerate(walls_2d):
            wall_3d = Wall3D(f"W{i:03d}")
            wall_3d.start_2d = wall.get("start")
            wall_3d.end_2d = wall.get("end")
            wall_3d.height_m = 3.0
            wall_3d.thickness_m = 0.25
            wall_3d.generate_vertices()
            
            self.walls_3d.append(wall_3d)
        
        # Generate 3D rooms
        for i, room in enumerate(rooms_2d):
            room_3d = Room3D(f"R{i:03d}")
            room_3d.bbox_2d = room.get("bbox")
            room_3d.height_m = 2.7
            room_3d.generate_vertices()
            
            self.rooms_3d.append(room_3d)
        
        return {
            "walls_3d_count": len(self.walls_3d),
            "rooms_3d_count": len(self.rooms_3d),
            "total_volume_m3": sum(r.volume_m3 for r in self.rooms_3d),
            "model_format": self.model_format
        }
    
    def get_obj_string(self) -> str:
        """Generate OBJ format string"""
        obj = "# TulgaTech 3D Model\n"
        obj += f"# Walls: {len(self.walls_3d)}, Rooms: {len(self.rooms_3d)}\n\n"
        
        vertex_count = 0
        
        # Write wall vertices
        for wall in self.walls_3d:
            for v in wall.vertices:
                obj += f"v {v[0]:.2f} {v[1]:.2f} {v[2]:.2f}\n"
                vertex_count += 1
        
        # Write room vertices
        for room in self.rooms_3d:
            for v in room.floor_vertices + room.ceiling_vertices:
                obj += f"v {v[0]:.2f} {v[1]:.2f} {v[2]:.2f}\n"
                vertex_count += 1
        
        obj += f"\n# Total vertices: {vertex_count}\n"
        
        return obj
    
    def get_model_stats(self) -> Dict:
        """Get model statistics"""
        total_wall_length = sum(
            math.hypot(w.end_2d[0] - w.start_2d[0], 
                      w.end_2d[1] - w.start_2d[1])
            for w in self.walls_3d if w.start_2d and w.end_2d
        )
        
        return {
            "walls_count": len(self.walls_3d),
            "rooms_count": len(self.rooms_3d),
            "total_wall_length_m": total_wall_length,
            "total_volume_m3": sum(r.volume_m3 for r in self.rooms_3d),
            "total_wall_area_m2": total_wall_length * 3.0,
            "vertex_count": sum(len(w.vertices) for w in self.walls_3d) + 
                           sum(len(r.floor_vertices) + len(r.ceiling_vertices) for r in self.rooms_3d)
        }
    
    def export_to_dict(self) -> Dict:
        """Export model to dictionary"""
        return {
            "walls": [w.to_dict() for w in self.walls_3d],
            "rooms": [r.to_dict() for r in self.rooms_3d],
            "stats": self.get_model_stats(),
            "format": self.model_format
        }