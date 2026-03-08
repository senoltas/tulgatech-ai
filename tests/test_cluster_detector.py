"""
Tests for ClusterDetector
"""
from tulgatech.engine.cluster_detector import Cluster, ClusterDetector


def test_cluster_init():
    """Test Cluster initialization"""
    cluster = Cluster("C01")
    assert cluster.id == "C01"
    assert cluster.count == 0
    assert cluster.points == []


def test_cluster_add_point():
    """Test adding points to cluster"""
    cluster = Cluster("C01")
    cluster.add_point((0, 0))
    cluster.add_point((1, 1))
    
    assert cluster.count == 2
    assert len(cluster.points) == 2


def test_cluster_bbox():
    """Test cluster bounding box"""
    cluster = Cluster("C01")
    cluster.add_point((0, 0))
    cluster.add_point((10, 10))
    
    assert cluster.bbox == (0, 0, 10, 10)


def test_cluster_center():
    """Test cluster center point"""
    cluster = Cluster("C01")
    cluster.add_point((0, 0))
    cluster.add_point((10, 0))
    cluster.add_point((10, 10))
    cluster.add_point((0, 10))
    
    assert cluster.center == (5.0, 5.0)


def test_cluster_to_dict():
    """Test cluster to_dict"""
    cluster = Cluster("C01")
    cluster.add_point((0, 0))
    
    d = cluster.to_dict()
    assert d["id"] == "C01"
    assert d["count"] == 1


def test_detector_init():
    """Test ClusterDetector initialization"""
    detector = ClusterDetector(grid_size=100.0)
    assert detector.grid_size == 100.0
    assert detector.clusters == {}


def test_detect_empty():
    """Test detecting clusters in empty list"""
    detector = ClusterDetector(grid_size=100.0)
    clusters = detector.detect_from_points([])
    assert clusters == []


def test_detect_single_cluster():
    """Test detecting single cluster"""
    detector = ClusterDetector(grid_size=100.0)
    
    # Create 5 points in same grid cell
    points = [
        (10, 10), (20, 20), (30, 30), (40, 40), (50, 50)
    ]
    
    clusters = detector.detect_from_points(points, min_points=5)
    
    assert len(clusters) == 1
    assert clusters[0].count == 5


def test_detect_multiple_clusters():
    """Test detecting multiple clusters"""
    detector = ClusterDetector(grid_size=100.0)
    
    # Two separate clusters
    points = [
        # Cluster 1 (near 0,0)
        (10, 10), (20, 20), (30, 30), (40, 40), (50, 50),
        # Cluster 2 (near 500,500)
        (510, 510), (520, 520), (530, 530), (540, 540), (550, 550),
    ]
    
    clusters = detector.detect_from_points(points, min_points=5)
    
    assert len(clusters) == 2


def test_get_largest_cluster():
    """Test getting largest cluster"""
    detector = ClusterDetector(grid_size=100.0)
    
    points = [
        # Small cluster
        (10, 10), (20, 20),
        # Large cluster
        (510, 510), (520, 520), (530, 530), (540, 540), (550, 550),
    ]
    
    detector.detect_from_points(points, min_points=2)
    largest = detector.get_largest_cluster()
    
    assert largest["count"] == 5


def test_get_cluster_count():
    """Test getting cluster count"""
    detector = ClusterDetector(grid_size=100.0)
    
    points = [
        (10, 10), (20, 20), (30, 30), (40, 40), (50, 50),
        (510, 510), (520, 520), (530, 530), (540, 540), (550, 550),
    ]
    
    detector.detect_from_points(points, min_points=5)
    
    assert detector.get_cluster_count() == 2