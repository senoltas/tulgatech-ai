"""
Geometry utilities for tulgatech
"""
import math


def distance(p1, p2):
    """Euclidean distance between two points"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.hypot(dx, dy)


def angle_degrees(start, end):
    """Angle of line in degrees (0-180)"""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx)) % 180.0
    return angle
