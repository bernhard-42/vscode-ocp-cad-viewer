# %%
from build123d import *
from ocp_vscode import *

set_defaults(reset_camera=Camera.CENTER)


a = 55 / 2
c100 = Circle(100).edges()[0]

lines = []
vertices = []
for sign in (1, -1):
    c = Vector(sign * 31, 0)
    l = PolarLine(c, sign * 6, sign * a)
    l2 = PolarLine(l @ 1, 100, sign * a - 90)
    vertices.append(c100.find_intersection_points(l2.edge()))
    lines.append(l2)

# combine to a wire and face
wire = Wire.combine(
    [
        Line(lines[0] @ 0, vertices[0]),
        ThreePointArc(vertices[0], Vector(0, -100), vertices[1]),
        Line(vertices[1], lines[1] @ 0),
        Line(lines[1] @ 0, lines[0] @ 0),
    ],
)
face = make_face(wire)
face = fillet(face.vertices().group_by(Axis.Y)[0], 15)

# calculate the centers
circles = face.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.X)
centers = [circles[0].arc_center, Vector(0, -85), circles[2].arc_center]

# extrude and cut holes
disk = Circle(31)
for loc in PolarLocations(31, 6):
    disk += loc * Circle(6)

t = extrude(disk, 16 / 2, both=True)
show(t)
t = fillet(t.edges().filter_by(Axis.Z), 8)
show(t)

t += extrude(face, 7 / 2, both=True)
for center in centers:
    t += Pos(*center) * Cylinder(15, 32)
    t -= Pos(*center) * Cylinder(10, 32)

for loc in PolarLocations(31, 6):
    t -= loc * Hole(3, depth=32)
t -= Hole(20, depth=16)

show(t)

# %%
