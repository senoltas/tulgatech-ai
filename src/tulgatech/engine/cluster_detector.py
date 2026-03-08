"""
Cluster detection from INSERT points (blocks)
"""
from typing import List, Dict, Tuple, Set
from collections import defaultdict, deque

Point2D = Tuple[float, float]


class Cluster:
    """Represents a cluster of INSERT points"""
    def __init__(self, cluster_id: str):
        self.id = cluster_id
        self.points: List[Point2D] = []
        self.count = 0
        self.bbox = None
        self.center = None
    
    def add_point(self, point: Point2D):
        """Add point to cluster"""
        self.points.append(point)
        self.count += 1
        self._update_bbox()
        self._update_center()
    
    def _update_bbox(self):
        """Update bounding box"""
        if not self.points:
            return
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        self.bbox = (min(xs), min(ys), max(xs), max(ys))
    
    def _update_center(self):
        """Update center point"""
        if not self.points:
            return
        avg_x = sum(p[0] for p in self.points) / len(self.points)
        avg_y = sum(p[1] for p in self.points) / len(self.points)
        self.center = (avg_x, avg_y)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "count": self.count,
            "bbox": self.bbox,
            "center": self.center,
            "points": self.points
        }


class ClusterDetector:
    """Detect clusters from INSERT points"""
    
    def __init__(self, grid_size: float = 100.0):
        """Initialize with grid size (drawing units)"""
        self.grid_size = float(grid_size)
        self.clusters: Dict[str, Cluster] = {}
    
    def detect_from_points(self, points: List[Point2D], 
                          min_points: int = 5) -> List[Cluster]:
        """Detect clusters from points using grid bucketing"""
        self.clusters = {}
        
        # Step 1: Bucket points into grid cells
        buckets = defaultdict(list)
        for point in points:
            gx = int(point[0] // self.grid_size)
            gy = int(point[1] // self.grid_size)
            buckets[(gx, gy)].append(point)
        
        # Step 2: Find active buckets (with min_points)
        active = {k for k, v in buckets.items() if len(v) >= min_points}
        
        if not active:
            return []
        
        # Step 3: Flood fill to connect adjacent buckets
        visited = set()
        cluster_id = 1
        
        for start_cell in sorted(active):
            if start_cell in visited:
                continue
            
            # BFS to find connected component
            queue = deque([start_cell])
            visited.add(start_cell)
            cluster_cells = [start_cell]
            
            while queue:
                gx, gy = queue.popleft()
                
                # Check 8 neighbors
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        neighbor = (gx + dx, gy + dy)
                        if neighbor in active and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                            cluster_cells.append(neighbor)
            
            # Step 4: Create cluster
            cluster = Cluster(f"C{cluster_id:02d}")
            for cell in cluster_cells:
                for point in buckets[cell]:
                    cluster.add_point(point)
            
            if cluster.count >= min_points:
                self.clusters[cluster.id] = cluster
                cluster_id += 1
        
        # Sort by count (largest first)
        sorted_clusters = sorted(self.clusters.values(), 
                               key=lambda c: c.count, reverse=True)
        
        return sorted_clusters
    
    def get_clusters(self) -> List[Dict]:
        """Get all clusters as dictionaries"""
        return [c.to_dict() for c in self.clusters.values()]
    def get_cluster_count(self) -> int:
        """Get total cluster count"""
        return len(self.clusters)
    
    def get_largest_cluster(self) -> Dict:
        """Get largest cluster"""
        if not self.clusters:
            return None
        largest = max(self.clusters.values(), key=lambda c: c.count)
        return largest.to_dict()