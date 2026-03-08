"""
Frame/sheet detection - identify drawing boundaries
"""
from typing import List, Dict, Tuple, Optional

Point2D = Tuple[float, float]


class Frame:
    """Represents a drawing frame/sheet"""
    def __init__(self, frame_id: str):
        self.id = frame_id
        self.bbox = None  # (minx, miny, maxx, maxy)
        self.center = None
        self.width = 0.0
        self.height = 0.0
        self.segments_count = 0
        self.confidence = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "bbox": self.bbox,
            "center": self.center,
            "width": self.width,
            "height": self.height,
            "segments_count": self.segments_count,
            "confidence": self.confidence
        }


class FrameDetector:
    """Detect drawing frames/sheets"""
    
    def __init__(self):
        self.frames: List[Frame] = []
    
    def detect_from_segments(self, segments: List[Dict],
                            min_frame_width: float = 100.0) -> List[Frame]:
        """Detect frames from segment clusters"""
        self.frames = []
        
        if not segments:
            return []
        
        # Get bounding boxes of all segments
        xs = []
        ys = []
        
        for seg in segments:
            start = seg.get("start")
            end = seg.get("end")
            if start:
                xs.append(start[0])
                ys.append(start[1])
            if end:
                xs.append(end[0])
                ys.append(end[1])
        
        if not xs or not ys:
            return []
        
        # Overall bounding box
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        
        width = maxx - minx
        height = maxy - miny
        
        # Create main frame
        frame = Frame("F01")
        frame.bbox = (minx, miny, maxx, maxy)
        frame.width = width
        frame.height = height
        frame.center = ((minx + maxx) / 2, (miny + maxy) / 2)
        frame.segments_count = len(segments)
        frame.confidence = 0.9  # High confidence for detected frame
        
        self.frames.append(frame)
        
        return self.frames
    
    def detect_multiple_frames(self, segments: List[Dict],
                              grid_divisions: int = 2) -> List[Frame]:
        """Detect multiple frames using grid division"""
        self.frames = []
        
        if not segments:
            return []
        
        # Get overall bbox
        xs = []
        ys = []
        
        for seg in segments:
            start = seg.get("start")
            end = seg.get("end")
            if start:
                xs.append(start[0])
                ys.append(start[1])
            if end:
                xs.append(end[0])
                ys.append(end[1])
        
        if not xs or not ys:
            return []
        
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        
        width = maxx - minx
        height = maxy - miny
        
        cell_width = width / grid_divisions
        cell_height = height / grid_divisions
        
        frame_id = 1
        
        # Create grid frames
        for gx in range(grid_divisions):
            for gy in range(grid_divisions):
                x1 = minx + gx * cell_width
                y1 = miny + gy * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                
                # Count segments in this cell
                seg_count = 0
                for seg in segments:
                    start = seg.get("start")
                    if start and x1 <= start[0] <= x2 and y1 <= start[1] <= y2:
                        seg_count += 1
                
                # Only create frame if has segments
                if seg_count > 0:
                    frame = Frame(f"F{frame_id:02d}")
                    frame.bbox = (x1, y1, x2, y2)
                    frame.width = cell_width
                    frame.height = cell_height
                    frame.center = ((x1 + x2) / 2, (y1 + y2) / 2)
                    frame.segments_count = seg_count
                    frame.confidence = min(0.8, seg_count / 100)
                    
                    self.frames.append(frame)
                    frame_id += 1
        
        return self.frames
    
    def get_frames(self) -> List[Dict]:
        """Get all frames as dictionaries"""
        return [f.to_dict() for f in self.frames]
    
    def get_frame_count(self) -> int:
        """Get total frame count"""
        return len(self.frames)
    
    def get_largest_frame(self) -> Optional[Dict]:
        """Get largest frame by area"""
        if not self.frames:
            return None
        largest = max(self.frames, key=lambda f: f.width * f.height)
        return largest.to_dict()