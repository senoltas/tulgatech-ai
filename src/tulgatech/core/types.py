"""
Shared data types for tulgatech
"""
from enum import Enum


class ScaleMethod(Enum):
    """Scale detection method"""
    DIMENSION_BASED = "dimension"
    TEXT_BASED = "text"
    HEURISTIC = "heuristic"
    USER_PROVIDED = "user"
    UNKNOWN = "unknown"