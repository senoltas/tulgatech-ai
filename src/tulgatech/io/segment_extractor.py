"""
Extract segments (lines, polylines) from DXF entities
"""
from typing import List, Dict, Tuple, Any

Point2D = Tuple[float, float]


class Segment:
    """Represents a line segment"""
    def __init__(self, start: Point2D, end: Point2D, layer: str, source: str):
        self.start = start
        self.end = end
        self.layer = layer
        self.source = source  # LINE, LWPOLYLINE, POLYLINE
    
    def length(self) -> float:
        """Calculate segment length"""
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return (dx**2 + dy**2) ** 0.5


class SegmentExtractor:
    """Extract segments from DXF modelspace"""
    
    def __init__(self, dxf_loader):
        """Initialize with DXFLoader instance"""
        self.loader = dxf_loader
        self.segments: List[Segment] = []
    
    def extract(self) -> List[Segment]:
        """Extract all segments from loaded DXF"""
        if not self.loader.msp:
            return []
        
        self.segments = []
        
        for entity in self.loader.msp:
            entity_type = entity.dxftype()
            
            # LINE entities
            if entity_type == "LINE":
                self._extract_line(entity)
            
            # LWPOLYLINE entities
            elif entity_type == "LWPOLYLINE":
                self._extract_lwpolyline(entity)
            
            # POLYLINE entities
            elif entity_type == "POLYLINE":
                self._extract_polyline(entity)
        
        return self.segments
    
    def _extract_line(self, entity):
        """Extract LINE entity"""
        try:
            start = (float(entity.dxf.start.x), float(entity.dxf.start.y))
            end = (float(entity.dxf.end.x), float(entity.dxf.end.y))
            layer = str(entity.dxf.layer)
            
            segment = Segment(start, end, layer, "LINE")
            self.segments.append(segment)
        except Exception:
            pass
    
    def _extract_lwpolyline(self, entity):
        """Extract LWPOLYLINE entity"""
        try:
            points = [(float(x), float(y)) for x, y, *_ in entity.get_points()]
            layer = str(entity.dxf.layer)
            
            # Create segments between consecutive points
            for i in range(len(points) - 1):
                segment = Segment(points[i], points[i+1], layer, "LWPOLYLINE")
                self.segments.append(segment)
        except Exception:
            pass
    
    def _extract_polyline(self, entity):
        """Extract POLYLINE entity"""
        try:
            points = [(float(v.dxf.location.x), float(v.dxf.location.y)) 
                     for v in entity.vertices()]
            layer = str(entity.dxf.layer)
            
            # Create segments between consecutive points
            for i in range(len(points) - 1):
                segment = Segment(points[i], points[i+1], layer, "POLYLINE")
                self.segments.append(segment)
        except Exception:
            pass
    
    def get_segments_by_layer(self, layer: str) -> List[Segment]:
        """Get segments from specific layer"""
        return [s for s in self.segments if s.layer == layer]
    
    def get_total_length(self) -> float:
        """Get total length of all segments"""
        return sum(s.length() for s in self.segments)