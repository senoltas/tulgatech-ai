import ezdxf
from collections import Counter

DXF_PATH = r"data\test_2.dxf"

INC = ["KAT PLAN", "PLANI", "ÇATI PLANI", "VAZIYET"]
EXC = ["GRID", "AKS", "SPOT", "ELEVATION", "MULLION", "PARKING", "SECTION", "GIRIS", "GİRİŞ", "OKU"]

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

picked = []
all_names = []

for e in msp:
    if e.dxftype() != "INSERT":
        continue
    n = str(e.dxf.name)
    all_names.append(n)
    up = n.upper()

    if not any(k in up for k in INC):
        continue
    if any(k in up for k in EXC):
        continue

    picked.append(n)

c_all = Counter(all_names)
c_pick = Counter(picked)

print("INSERT_TOTAL =", len(all_names))
print("UNIQUE_BLOCKS =", len(c_all))
print("PICKED =", len(picked))
print("PICKED_UNIQUE =", len(c_pick))
print("TOP20_PICKED =", c_pick.most_common(20))