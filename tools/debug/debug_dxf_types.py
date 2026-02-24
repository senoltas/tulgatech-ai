import ezdxf

doc = ezdxf.readfile(r"data\test_2.dxf")
msp = doc.modelspace()

c = {}
for e in msp:
    t = e.dxftype()
    c[t] = c.get(t, 0) + 1

items = sorted(c.items(), key=lambda x: -x[1])
print(items[:30])
print("INSERT =", c.get("INSERT", 0))