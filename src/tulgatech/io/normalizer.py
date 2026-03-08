"""
Normalize DXF entities to standard format
"""
from typing import List, Dict, Any, Tuple

Point2D = Tuple[float, float]


class EntityNormalizer:
    """Convert DXF entities to normalized format"""
    
    def __init__(self):
        self.normalized_segments: List[Dict[str, Any]] = []
        self.normalized_texts: List[Dict[str, Any]] = []
    
    def normalize_segment(self, start: Point2D, end: Point2D, 
                         layer: str, source: str) -> Dict[str, Any]:
        """Normalize a segment to standard format"""
        return {
            "start": (float(start[0]), float(start[1])),
            "end": (float(end[0]), float(end[1])),
            "layer": str(layer).strip(),
            "source": str(source),
            "type": "segment"
        }
    
    def normalize_text(self, text: str, x: float, y: float, 
                      layer: str, height: float = 0.0) -> Dict[str, Any]:
        """Normalize a text element to standard format"""
        return {
            "text": str(text).strip(),
            "x": float(x),
            "y": float(y),
            "layer": str(layer).strip(),
            "height": float(height),
            "type": "text"
        }
    
    def normalize_from_dxf_loader(self, dxf_loader) -> Dict[str, Any]:
        """Extract and normalize all entities from DXF loader"""
        if not dxf_loader.msp:
            return {"segments": [], "texts": [], "count": 0}
        
        self.normalized_segments = []
        self.normalized_texts = []
        
        for entity in dxf_loader.msp:
            entity_type = entity.dxftype()
            layer = str(entity.dxf.layer)
            
            # Handle LINE
            if entity_type == "LINE":
                try:
                    start = (entity.dxf.start.x, entity.dxf.start.y)
                    end = (entity.dxf.end.x, entity.dxf.end.y)
                    seg = self.normalize_segment(start, end, layer, "LINE")
                    self.normalized_segments.append(seg)
                except Exception:
                    pass
            
            # Handle TEXT
            elif entity_type == "TEXT":
                try:
                    text = str(entity.dxf.text)
                    x, y = entity.dxf.insert.x, entity.dxf.insert.y
                    height = entity.dxf.height
                    txt = self.normalize_text(text, x, y, layer, height)
                    self.normalized_texts.append(txt)
                except Exception:
                    pass
            
            # Handle MTEXT
            elif entity_type == "MTEXT":
                try:
                    text = entity.plain_text()
                    x, y = entity.dxf.insert.x, entity.dxf.insert.y
                    height = entity.dxf.char_height
                    txt = self.normalize_text(text, x, y, layer, height)
                    self.normalized_texts.append(txt)
                except Exception:
                    pass
        
        return {
            "segments": self.normalized_segments,
            "texts": self.normalized_texts,
            "count": len(self.normalized_segments) + len(self.normalized_texts)
        }
    
    def get_normalized_segments(self) -> List[Dict[str, Any]]:
        """Get all normalized segments"""
        return self.normalized_segments
    
    def get_normalized_texts(self) -> List[Dict[str, Any]]:
        """Get all normalized texts"""
        return self.normalized_texts
    
    def filter_by_layer(self, layer: str, entity_type: str = "segment") -> List[Dict[str, Any]]:
        """Filter normalized entities by layer"""
        if entity_type == "segment":
            return [s for s in self.normalized_segments if s["layer"] == layer]
        elif entity_type == "text":
            return [t for t in self.normalized_texts if t["layer"] == layer]
        return []