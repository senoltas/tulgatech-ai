"""
Main orchestrator - coordinates all modules
"""
from typing import Dict, Any, Optional
from tulgatech.io.dxf_loader import DXFLoader
from tulgatech.io.segment_extractor import SegmentExtractor
from tulgatech.io.normalizer import EntityNormalizer
from tulgatech.core.scale_manager import ScaleManager
from tulgatech.engine.wall_detector import WallDetector


class TulgaTechOrchestrator:
    """Main orchestrator for TulgaTech pipeline"""
    
    def __init__(self):
        self.loader = DXFLoader()
        self.extractor = None
        self.normalizer = EntityNormalizer()
        self.scale_mgr = ScaleManager()
        self.wall_detector = None
        
        self.result: Dict[str, Any] = {
            "success": False,
            "error": None,
            "scale": None,
            "segments": [],
            "walls": [],
            "stats": {}
        }
    
    def process(self, dxf_file_path: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        try:
            # Step 1: Load DXF
            print(f"📁 Loading DXF: {dxf_file_path}")
            if not self.loader.load(dxf_file_path):
                self.result["error"] = "Failed to load DXF file"
                return self.result
            
            # Step 2: Extract segments
            print("🔍 Extracting segments...")
            self.extractor = SegmentExtractor(self.loader)
            segments = self.extractor.extract()
            print(f"   Found {len(segments)} segments")
            
            # Step 3: Detect scale
            print("📏 Detecting scale...")
            scale_est = self.scale_mgr.detect(self.loader.doc)
            self.result["scale"] = {
                "value": scale_est.scale,
                "confidence": scale_est.confidence,
                "method": scale_est.method,
                "samples": scale_est.samples,
                "is_reliable": scale_est.is_reliable()
            }
            print(f"   Scale: {scale_est.scale:.6f} (confidence: {scale_est.confidence:.0%})")
            
            # Step 4: Normalize segments
            print("✨ Normalizing segments...")
            normalized = self.normalizer.normalize_from_dxf_loader(self.loader)
            self.result["segments"] = normalized["segments"]
            print(f"   Normalized {normalized['count']} entities")
            
            # Step 5: Detect walls
            print("🧱 Detecting walls...")
            self.wall_detector = WallDetector(scale=scale_est.scale)
            walls = self.wall_detector.detect_walls(
                normalized["segments"],
                min_length_m=0.5
            )
            self.result["walls"] = walls
            print(f"   Found {len(walls)} wall candidates")
            print(f"   Total wall length: {self.wall_detector.get_total_wall_length_m():.2f}m")
            
            # Step 6: Stats
            self.result["stats"] = {
                "total_segments": len(segments),
                "normalized_entities": normalized["count"],
                "wall_candidates": len(walls),
                "total_wall_length_m": self.wall_detector.get_total_wall_length_m(),
                "high_confidence_walls": len(self.wall_detector.get_high_confidence_walls()),
                "bbox": self.loader.get_bbox(),
                "layers": self.loader.get_layers()
            }
            
            self.result["success"] = True
            print("✅ Processing complete!")
            
            return self.result
            
        except Exception as e:
            self.result["error"] = str(e)
            print(f"❌ Error: {e}")
            return self.result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of processing"""
        return {
            "success": self.result["success"],
            "error": self.result["error"],
            "scale_confidence": self.result["scale"]["confidence"] if self.result["scale"] else 0,
            "segments_count": len(self.result["segments"]),
            "walls_count": len(self.result["walls"]),
            "total_wall_length_m": self.result["stats"].get("total_wall_length_m", 0)
        }