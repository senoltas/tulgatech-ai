"""
DXF file loader
"""
import ezdxf
from typing import Dict, List, Any, Optional


class DXFLoader:
    """Load and parse DXF files"""
    
    def __init__(self):
        self.doc = None
        self.msp = None
    
    def load(self, file_path: str) -> bool:
        """Load DXF file"""
        try:
            self.doc = ezdxf.readfile(file_path)
            self.msp = self.doc.modelspace()
            return True
        except Exception as e:
            print(f"Error loading DXF: {e}")
            return False
    
    def get_entity_count(self) -> int:
        """Get total entity count"""
        if not self.msp:
            return 0
        return len(list(self.msp))
    
    def get_layers(self) -> List[str]:
        """Get all layer names"""
        if not self.doc:
            return []
        return [layer.dxf.name for layer in self.doc.layers]
    
    def get_bbox(self) -> Optional[tuple]:
        """Get bounding box"""
        try:
            bbox = self.msp.bbox()
            if bbox:
                return (bbox.min.x, bbox.min.y, bbox.max.x, bbox.max.y)
        except Exception:
            pass
        return None