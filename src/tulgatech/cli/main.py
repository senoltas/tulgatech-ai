"""
Command-line interface for TulgaTech AI
"""
import sys
from pathlib import Path
from tulgatech.engine.orchestrator import TulgaTechOrchestrator


def print_header():
    """Print CLI header"""
    print("\n" + "="*60)
    print("  TulgaTech AI - Construction Data Intelligence")
    print("="*60 + "\n")


def print_result(result):
    """Pretty print result"""
    print("\n" + "-"*60)
    
    if not result["success"]:
        print(f"❌ ERROR: {result['error']}")
        return
    
    print("✅ SUCCESS!\n")
    
    # Scale info
    if result["scale"]:
        scale = result["scale"]
        print(f"📏 SCALE:")
        print(f"   Value: {scale['value']:.6f} m/unit")
        print(f"   Confidence: {scale['confidence']:.0%}")
        print(f"   Method: {scale['method']}")
        print(f"   Reliable: {'Yes ✅' if scale['is_reliable'] else 'No ❌'}\n")
    
    # Statistics
    stats = result["stats"]
    print(f"📊 STATISTICS:")
    print(f"   Total segments: {stats.get('total_segments', 0)}")
    print(f"   Normalized entities: {stats.get('normalized_entities', 0)}")
    print(f"   Wall candidates: {stats.get('wall_candidates', 0)}")
    print(f"   High confidence walls: {stats.get('high_confidence_walls', 0)}")
    print(f"   Total wall length: {stats.get('total_wall_length_m', 0):.2f}m\n")
    
    # Walls
    if result["walls"]:
        print(f"🧱 TOP 5 WALLS:")
        for i, wall in enumerate(result["walls"][:5], 1):
            print(f"   {i}. Layer: {wall['layer']}, Length: {wall['length_m']:.2f}m, Confidence: {wall['confidence']:.0%}")
        print()
    
    # Layers
    if stats.get("layers"):
        print(f"🗂️  LAYERS: {len(stats['layers'])} found")
        print(f"   {', '.join(stats['layers'][:10])}")
        if len(stats['layers']) > 10:
            print(f"   ... and {len(stats['layers']) - 10} more")
        print()
    
    print("-"*60 + "\n")


def main():
    """Main CLI entry point"""
    print_header()
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: tulgatech <dxf_file_path>\n")
        print("Example:")
        print("  tulgatech my_project.dxf\n")
        sys.exit(1)
    
    dxf_file = sys.argv[1]
    
    # Check file exists
    if not Path(dxf_file).exists():
        print(f"❌ File not found: {dxf_file}\n")
        sys.exit(1)
    
    # Process
    print(f"Processing: {dxf_file}\n")
    orch = TulgaTechOrchestrator()
    result = orch.process(dxf_file)
    
    # Print result
    print_result(result)
    
    # Exit code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()