"""
System-wide scale management
"""
import math
from enum import Enum
from typing import Optional, Dict, Any


class ScaleEstimate:
    """Scale detection result"""
    def __init__(self, scale: float, confidence: float, method: str, samples: int):
        self.scale = scale
        self.confidence = confidence
        self.method = method
        self.samples = samples
    
    def is_reliable(self) -> bool:
        """True if confidence > 0.7"""
        return self.confidence > 0.7


class ScaleManager:
    """Centralized scale detection"""
    
    def __init__(self):
        self.estimate: Optional[ScaleEstimate] = None
    
    def get_scale(self) -> float:
        """Get current scale (default 1.0 if not detected)"""
        return self.estimate.scale if self.estimate else 1.0
    
    def is_reliable(self) -> bool:
        """True if confidence > 0.7"""
        if self.estimate is None:
            return False
        return self.estimate.confidence > 0.7