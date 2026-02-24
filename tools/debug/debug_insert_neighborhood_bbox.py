import ezdxf
import math
from collections import Counter
INC = ["KAT PLAN", "KAT PLANI", "ÇATI PLANI", "VAZIYET", "VAZİYET", "PLAN"]
EXC = ["GÖRÜNÜŞ", "GORUNUS", "ELEVATION", "SECTION", "KESIT", "KESİT"]
DXF_PATH = r"data\test_2.dxf"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# 1) Tüm line segment noktalarını hazırla (hız için)
lines = []
for e in msp:
    t = e.dxftype()
    if t == "LINE":
        s = e.dxf.start
        en = e.dxf.end
        lines.append((float(s.x), float(s.y), float(en.x), float(en.y)))
    elif t == "LWPOLYLINE":
        pts = [(float(x), float(y)) for (x, y, *_r) in e.get_points()]
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            lines.append((x1, y1, x2, y2))

print("TOTAL_SEGMENTS =", len(lines))

def dist2_point_to_seg(px, py, x1, y1, x2, y2):
    # segment projection distance squared
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1
    c1 = vx * wx + vy * wy
    if c1 <= 0:
        return (px - x1) ** 2 + (py - y1) ** 2
    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return (px - x2) ** 2 + (py - y2) ** 2
    b = c1 / c2
    bx, by = x1 + b * vx, y1 + b * vy
    return (px - bx) ** 2 + (py - by) ** 2

# 2) INSERT'ler: PLAN isimli olanları al (görünüş/kesit hariç)
inserts = []
for e in msp:
    if e.dxftype() != "INSERT":
        continue
    name = str(e.dxf.name)
    up = name.upper()

    if not any(k in up for k in INC):
        continue
    if any(k in up for k in EXC):
        continue

    ip = e.dxf.insert
    inserts.append((name, float(ip.x), float(ip.y)))

print("INSERT_TOTAL =", len(inserts))

# 3) Her INSERT için yakın çevrede kaç segment var? bbox ne?
# Yarıçapı çizime göre ayarlayacağız. İlk deneme: 50 metre.
# scale=0.5 olduğu için çizim birimi muhtemelen 1 birim=1m değil; ama debug için yeter.
R = 150.0  # çizim birimi cinsinden (gerekirse 40/120 deneriz)
R2 = R * R

rows = []
for name, ix, iy in inserts:
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    cnt = 0

    for x1, y1, x2, y2 in lines:
        if dist2_point_to_seg(ix, iy, x1, y1, x2, y2) <= R2:
            cnt += 1
            minx = min(minx, x1, x2)
            miny = min(miny, y1, y2)
            maxx = max(maxx, x1, x2)
            maxy = max(maxy, y1, y2)

    if cnt == 0:
        continue

    w = maxx - minx
    h = maxy - miny
    area = w * h
    rows.append((area, cnt, w, h, name, ix, iy))

rows.sort(key=lambda x: (x[0], x[1]), reverse=True)

print("\nTOP30_INSERTS_BY_NEIGHBOR_BBOX:")
for i, r in enumerate(rows[:30], 1):
    area, cnt, w, h, name, ix, iy = r
    print(f"{i:02d}. area={area:.2f}  segs={cnt}  w={w:.2f} h={h:.2f}  name={name}  at=({ix:.1f},{iy:.1f})")

top_names = [r[4] for r in rows[:200]]
c = Counter(top_names)
print("\nTOP_NAMES_IN_TOP200 =", c.most_common(20))
