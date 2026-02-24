from engine.orchestrator import TulgaTechOrchestrator as O
from shapely.geometry import LineString
from shapely.ops import unary_union, polygonize

def main():
    o = O()
    r = o.process_project(r"data\test_2.dxf")

    a = r["project"].get("architectural", {})
    pw = a.get("potential_walls", [])
    print("PW_LEN =", len(pw))
    print("ARCH_SPACES_LEN =", len(a.get("spaces", [])))
    print("PW0 =", pw[0] if pw else None)

    # Build lines from potential_walls (supports both schemas)
    lines = []
    for w in pw or []:
        s = (w or {}).get("start")
        e = (w or {}).get("end")
        if s is None or e is None:
            ln = (w or {}).get("line") or {}
            s = s or ln.get("start")
            e = e or ln.get("end")

        if not (isinstance(s, (list, tuple)) and isinstance(e, (list, tuple)) and len(s) >= 2 and len(e) >= 2):
            continue

        try:
            x1, y1 = float(s[0]), float(s[1])
            x2, y2 = float(e[0]), float(e[1])
        except Exception:
            continue

        if x1 == x2 and y1 == y2:
            continue

        lines.append(LineString([(x1, y1), (x2, y2)]))

    print("LINES_LEN =", len(lines))

    if not lines:
        print("NO_LINES -> schema/parse issue")
        return

    merged = unary_union(lines)
    polys = list(polygonize(merged))
    print("POLYS_RAW_LEN =", len(polys))

    if polys:
        areas = sorted([p.area for p in polys], reverse=True)
        print("AREA_DRAW_TOP10 =", [round(x, 4) for x in areas[:10]])
    else:
        print("NO_POLYS -> walls not forming closed loops (or need snap tolerance)")

if __name__ == "__main__":
    main()