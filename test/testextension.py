from build123d import *
from ocp_vscode import *

set_port(3939)
set_defaults(reset_camera=Camera.KEEP, ortho=True)
densa = 7800 / 1e6  # carbon steel density g/mm^3
densb = 2700 / 1e6  # aluminum alloy
densc = 1020 / 1e6  # ABS
LB = 453.592  # g/lb
ms = Mode.SUBTRACT
LMH, LMV = LengthMode.HORIZONTAL, LengthMode.VERTICAL
# %%

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as s:
        with BuildLine(Plane.XZ) as l:
            m1 = Line((3.5 / 2, 0), (5.625 / 2, 0))
            m2 = Line(m1 @ 1, m1 @ 1 + (0, 3))
            m3 = Line(m2 @ 1, m2 @ 1 + (-(5.625 - 3.75) / 2, 0))
            m4 = Line(m3 @ 1, m3 @ 1 + (0, -0.375))
            m5 = Line(m4 @ 1, m4 @ 1 + (-0.75 / 2, 0))
            m6 = Line(m5 @ 1, m5 @ 1 + (0, -3 + 1.75 + 0.375))
            m7 = Line(m6 @ 1, m6 @ 1 + (0.5 / 2, 0))
            m8 = Line(m7 @ 1, m1 @ 0)
        make_face()
    revolve(axis=Axis.Z, revolution_arc=90)

    with BuildSketch(Plane.XZ.rotated((0, 0, -45))) as s2:
        Rectangle(1, 1.5, align=(Align.CENTER, Align.MIN))
        with Locations((0, 1)):
            Rectangle(2, 0.25, align=(Align.CENTER, Align.MIN))
    extrude(amount=-6, mode=ms)

    with Locations(Plane.XY.offset(3)):
        with PolarLocations(4.625 / 2, 1, 45):
            CounterBoreHole(0.375 / 2, 0.625 / 2, 0.25)
    mirror(about=Plane.XZ)
    mirror(about=Plane.YZ)


r = RegularPolygon(100, 5)
pp = extrude(r, 1000)
pp -= Hole(2, 50)


classes = (BuildPart, BuildSketch, BuildLine)  # for OCP-vscode
set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="vscod"))
show2(pp, name="item")

# b = Box(1, 2, 3) - Plane.YZ * Cylinder(0.5, 1)
# b = fillet(b.edges().filter_by(Axis.X), 0.3)
# b = chamfer(b.edges().filter_by(Axis.Y), 0.1)
# c = Pos(3, 0, 0) * Box(1, 1, 1)
# s = Pos(0, 2, 1) * Circle(0.5)

# show2(b, c, s)
print()
print(f"part mass = {p.part.scale(IN).volume*densb/LB}")
