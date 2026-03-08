from tulgatech.engine.orchestrator import TulgaTechOrchestrator

o = TulgaTechOrchestrator()
r = o.process('data/test_33.dxf')
walls = r.get('walls', [])

print('Total walls:', len(walls))
print('High confidence:', len([w for w in walls if w.get('confidence', 0) > 0.7]))
print('\nFirst 5 walls:')
for w in walls[:5]:
    print(f"  Layer: {w.get('layer')}, Length: {w.get('length_m'):.1f}m, Confidence: {w.get('confidence'):.0%}")