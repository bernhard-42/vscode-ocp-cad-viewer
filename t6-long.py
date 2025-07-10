# %%
from build123d import *
from ocp_vscode import *

r = Rectangle(20, 40)
b = extrude(r, 10, taper=10)
show(b)
# %%
from ocp_tessellate.stepreader import StepReader

reader = StepReader()
reader.load("/Users/bernhard/Development/CAD/Step-files/WV_TRANSPORTER_T6_V_1.STEP")
# t6 = import_step("/Users/bernhard/Development/CAD/Step-files/Bus-T6.step")

# %%
t6 = Rot(90, 0, 0) * Solid(reader.assemblies[0]["shape"])
# b = Pos(-244, 1010, -2916) * Box(1110 + 1599, 2022, 8 + 5840)
# s = Solid(t6)
show(t6)

# %%
cmm = (Align.CENTER, Align.MIN, Align.MIN)
points = [
    (-829.5, 5060.0, 1188.2),
    (-829.5, 5060.0, 1235.9),
    (-744.2, 5060.0, 1769.0 + 34),
    (-680.0, 5060.0, 1868.1 + 20),
    (-655, 5060, 1882 + 26),
    (-570, 5060.0, 1900 + 28),
]

h = 1500  # 820
b = Pos(0, 2114, 500, 6) * Box(1680, 2825, h, align=cmm)
# b.color = "black"
t6.alpha = 1
s = Spline(points)

s1 = Pos(-9, 0, 0) * s
s2 = mirror(s1, Plane.YZ)
l1 = Line(s1 @ 0, s2 @ 0)
l2 = Line(s1 @ 1, s2 @ 1)
f = make_face(s1 + l1 + s2 + l2)
mask = extrude(f, -3000) + Pos(0, 2000, 0) * Box(2000, 5000, 1189, align=cmm)
mask2 = Rot(-5.3, 0, 0) * Pos(0, 1565, 600) * Box(2000, 500, 2000, align=cmm)
b = b & mask
b = b - mask2

points2 = [
    (900, 5058.3, 1263.1),
    (900, 5044.3, 1463.1),
    (900, 4994.0, 1765.4),
    (900, 4953.8, 1890.2),
    (900, 4907.2, 1954.8),
]
s2 = Spline(points2)
l = (
    s2
    + Line(s2 @ 1, (900, 0, (s2 @ 1).Z))
    + Line((900, 0, (s2 @ 1).Z), (900, 0, 0))
    + Line((900, 0, 0), (900, (s2 @ 0).Y, 0))
    + Line((900, (s2 @ 0).Y, 0), (900, (s2 @ 0).Y, (s2 @ 0).Z))
)
l = Pos(0, -125, 0) * l
f2 = make_face(l)
mask3 = extrude(f2, -2300)
b = b & mask3

c = Pos(-738, 4351.2, 368) * (Plane.YZ * Cylinder(440, 290))
c = fillet(c.edges(), 120)
c2 = mirror(c, Plane.ZY)
c.alpha = 0.5
c2.alpha = 0.5

b = b - c - c2

c = Pos(-910, 4351.2, 368) * (Plane.YZ * Cylinder(492, 280))
c = fillet(c.edges(), 4)
c2 = mirror(c, Plane.ZY)
c.alpha = 0.5
c2.alpha = 0.5
b = b - c - c2

show(b, debug=True)

set_viewer_config(tab="clip")
