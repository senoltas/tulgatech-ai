import ezdxf
from collections import Counter
from math import inf

DXF_PATH = r"data\test_2.dxf"

# İstersen burada yine kaba bir include tutabiliriz ama şart değil.
# Şimdilik HER INSERT'i değerlendirip "en büyük bbox"ları bulacağız.

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

rows = []
names = []

for e in msp:
    if e.dxftype() != "INSERT":
        continue

    name = str(e.dxf.name)
    names.append(name)

    try:
        bbox = e.bbox()  # ezdxf bbox (works for many inserts)
    except Exception:
        bbox = None

    if not bbox:
        continue

    try:
        ext = bbox.extents  # (min, max)
        minx, miny = float(ext[0].x), float(ext[0].y)
        maxx, maxy = float(ext[1].x), float(ext[1].y)
        w = maxx - minx
        h = maxy - miny
        area = w * h
    except Exception:
        continue

    rows.append((area, w, h, minx, miny, maxx, maxy, name))

rows.sort(key=lambda x: x[0], reverse=True)

print("INSERT_TOTAL =", len(names))
print("ROWS_WITH_BBOX =", len(rows))
print("\nTOP30_BY_BBOX_AREA:")
for i, r in enumerate(rows[:30], 1):
    area, w, h, minx, miny, maxx, maxy, name = r
    print(f"{i:02d}. area={area:.2f}  w={w:.2f} h={h:.2f}  name={name}")

# ayrıca en büyük 30'un isim tekrarlarını da görelim
top_names = [r[-1] for r in rows[:200]]
c = Counter(top_names)
print("\nTOP_NAMES_IN_TOP200 =", c.most_common(20))