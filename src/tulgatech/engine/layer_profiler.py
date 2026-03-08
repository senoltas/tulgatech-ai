"""
Layer profiler - analyze DXF layers
"""
from typing import Dict, List, Any
from collections import Counter


class LayerProfile:
    """Profile of a single layer"""
    def __init__(self, name: str):
        self.name = name
        self.segment_count = 0
        self.text_count = 0
        self.total_length = 0.0
        self.bbox = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "segment_count": self.segment_count,
            "text_count": self.text_count,
            "total_length": self.total_length,
            "bbox": self.bbox
        }


class LayerProfiler:
    """Profile all layers in DXF"""
    
    def __init__(self):
        self.profiles: Dict[str, LayerProfile] = {}
    
    def profile_segments(self, segments: List[Dict[str, Any]]) -> Dict[str, LayerProfile]:
        """Profile segments by layer"""
        self.profiles = {}
        
        for seg in segments:
            layer = seg.get("layer", "(NO_LAYER)")
            
            if layer not in self.profiles:
                self.profiles[layer] = LayerProfile(layer)
            
            profile = self.profiles[layer]
            profile.segment_count += 1
            
            # Add length
            start = seg.get("start")
            end = seg.get("end")
            if start and end:
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = (dx**2 + dy**2) ** 0.5
                profile.total_length += length
        
        return self.profiles
    
    def profile_texts(self, texts: List[Dict[str, Any]]) -> Dict[str, LayerProfile]:
        """Profile texts by layer"""
        if not self.profiles:
            # Initialize if empty
            for text in texts:
                layer = text.get("layer", "(NO_LAYER)")
                if layer not in self.profiles:
                    self.profiles[layer] = LayerProfile(layer)
        
        for text in texts:
            layer = text.get("layer", "(NO_LAYER)")
            
            if layer not in self.profiles:
                self.profiles[layer] = LayerProfile(layer)
            
            self.profiles[layer].text_count += 1
        
        return self.profiles
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all layers"""
        return {
            "total_layers": len(self.profiles),
            "layers": [p.to_dict() for p in self.profiles.values()],
            "layer_names": list(self.profiles.keys())
        }
    
    def get_top_layers_by_segments(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top layers by segment count"""
        sorted_profiles = sorted(
            self.profiles.values(),
            key=lambda p: p.segment_count,
            reverse=True
        )
        return [p.to_dict() for p in sorted_profiles[:limit]]
    
    def get_top_layers_by_length(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top layers by total length"""
        sorted_profiles = sorted(
            self.profiles.values(),
            key=lambda p: p.total_length,
            reverse=True
        )
        return [p.to_dict() for p in sorted_profiles[:limit]]
    
    def detect_wall_layers(self) -> List[str]:
        """Detect likely wall layers by name"""
        wall_keywords = ["DUVAR", "WALL", "MUR", "PARETE", "MURO"]
        wall_layers = []
        
        for layer_name in self.profiles.keys():
            up = layer_name.upper()
            if any(kw in up for kw in wall_keywords):
                wall_layers.append(layer_name)
        
        return wall_layers
    
    def detect_text_layers(self) -> List[str]:
        """Detect likely text layers by name"""
        text_keywords = ["TEXT", "YAZI", "NOTE", "ETIKET", "MTEXT"]
        text_layers = []
        
        for layer_name in self.profiles.keys():
            up = layer_name.upper()
            if any(kw in up for kw in text_keywords):
                text_layers.append(layer_name)
        
        return text_layers