from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
from datetime import datetime


class ConfidenceLevel(Enum):
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.3
    VERY_LOW = 0.1


class ExtractionMethod(Enum):
    CLOSED_POLYLINE = "closed_polyline"
    WALL_LINE_DETECTION = "wall_line_detection"
    HATCH_PATTERN = "hatch_pattern"
    TEXT_EXTRACTION = "text_extraction"
    DIMENSION_ANALYSIS = "dimension_analysis"
    USER_CORRECTION = "user_correction"


@dataclass
class Assumption:
    parameter: str
    value: Any
    source: str  # "default", "user", "inferred"
    confidence: float


@dataclass
class QuantityItem:
    id: str
    name: str
    category: str  # "area", "length", "count", "volume"
    value: float
    unit: str
    extraction_method: ExtractionMethod
    confidence: float
    assumptions: List[Assumption] = field(default_factory=list)
    source_data: Dict[str, Any] = field(default_factory=dict)  # Hangi çizim nesnelerinden üretildi?
    warnings: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "value": round(float(self.value), 2),
            "unit": self.unit,
            "confidence": round(float(self.confidence), 2),
            "source": self.extraction_method.value,  # Enum -> str
            "warnings": self.warnings,
            "assumptions": [
                {
                    "parameter": a.parameter,
                    "value": a.value,
                    "source": a.source,
                    "confidence": round(float(a.confidence), 2),
                }
                for a in self.assumptions
            ],
            "source_data": self.source_data,
            "created_at": self.created_at,
        }
