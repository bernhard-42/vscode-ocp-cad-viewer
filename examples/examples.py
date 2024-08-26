# %%
from build123d import *
from ocp_vscode import *

import cadquery as cq

from ocp_tessellate.utils import Color


# %% Example "box1"

b = cq.Workplane().box(1, 1, 1)
show(b)


# %% Example "Image Face"

f = ImageFace("examples/object-160x160mm.png", 600 / 912, name="imageplane")
show(f)


# %% Example "orientation box"

b = Box(50, 100, 150)
f = b.faces().sort_by(Axis.Y)[0]
b += extrude(Plane(f) * Rot(0, 0, 0) * Text("ZX / Front", 12), 2)
f = b.faces().sort_by(Axis.Y)[-1]
b += extrude(Plane(f) * Rot(0, 0, 0) * Text("XZ / Back", 12), 2)

f = b.faces().sort_by(Axis.X)[0]
b += extrude(Plane(f) * Rot(0, 0, -90) * Text("ZY / Left", 12), 2)
f = b.faces().sort_by(Axis.X)[-1]
b += extrude(Plane(f) * Rot(0, 0, -90) * Text("YZ / Right", 12), 2)

f = b.faces().sort_by(Axis.Z)[0]
b += extrude(Plane(f) * Rot(0, 0, 90) * Text("XY / Bottom", 12), 2)
f = b.faces().sort_by(Axis.Z)[-1]
b += extrude(Plane(f) * Rot(0, 0, 90) * Text("YX / Top", 12), 2)

show(b)


# %% Example "dir box"

fs = 6
ex = -0.9
b = Box(10, 10, 10)
b = fillet(b.edges().group_by()[-1], 1)
b = chamfer(b.edges().group_by()[0], 1)

f = b.faces().sort_by(Axis.Y)[0]
b -= extrude(Plane(f) * Rot(0, 0, -90) * Text("-Y", fs), ex)
f = b.faces().sort_by(Axis.Y)[-1]
b -= extrude(Plane(f) * Rot(0, 0, -90) * Text("+Y", fs), ex)

f = b.faces().sort_by(Axis.X)[0]
b -= extrude(Plane(f) * Rot(0, 0, -90) * Text("-X", fs), ex)
f = b.faces().sort_by(Axis.X)[-1]
b -= extrude(Plane(f) * Rot(0, 0, -90) * Text("+X", fs), ex)

f = b.faces().sort_by(Axis.Z)[0]
b -= extrude(Plane(f) * Rot(0, 0, 90) * Text("-Z", fs), ex)
f = b.faces().sort_by(Axis.Z)[-1]
b -= extrude(Plane(f) * Rot(0, 0, 90) * Text("+Z", fs), ex)

show(b)


# %% Example Boxes

box1 = cq.Workplane("XY").box(10, 20, 30).edges(">X or <X").chamfer(2)
box1.name = "box1"

box2 = cq.Workplane("XY").box(8, 18, 28).edges(">X or <X").chamfer(2)
box2.name = "box2"

box3 = (
    cq.Workplane("XY")
    .transformed(offset=(0, 15, 7))
    .box(30, 20, 6)
    .edges(">Z")
    .fillet(3)
)
box3.name = "box3"

box4 = box3.mirror("XY").translate((0, -5, 0))
box4.name = "box4"

box1 = box1.cut(box2).cut(box3).cut(box4)

a1 = (
    cq.Assembly(name="ensemble")
    .add(box1, name="red box", color=Color("#d7191c", 0.5))
    .add(box3, name="green box", color=Color("#abdda4"))
    .add(box4, name="blue box", color=Color((43, 131, 186)))
)

show(a1)


# %% Example assembly

s1 = Solid.make_box(1, 1, 1).move(Location((3, 3, 3)))
s1.label, s1.color = "box", "red"

s2 = Solid.make_cone(2, 1, 2).move(Location((-3, 3, 3)))
s2.label, s2.color = "cone", "green"

s3 = Solid.make_cylinder(1, 2).move(Location((-3, -3, 3)))
s3.label, s3.color = "cylinder", "blue"

s4 = Solid.make_sphere(2).move(Location((3, 3, -3)))
s4.label = "sphere"

s5 = Solid.make_torus(3, 1).move(Location((-3, 3, -3)))
s5.label, s5.color = "torus", "cyan"

c2 = Compound(label="c2", children=[s2, s3])
c3 = Compound(label="c3", children=[s4, s5])
c1 = Compound(label="c1", children=[s1, c2, c3])

show(c1)


# %% Example Profile 4040
profile4040 = import_step("examples/profile4040.step")
profile4040.color = "silver"
profile4040.label = "profile 40x40"
show(profile4040)


# %% Example Torus Knot

from math import sin, cos, pi


def points(t0, t1, samples):
    sa = 30
    return [
        Vector(
            sa * (sin(t / samples) + 2 * sin(2 * t / samples)),
            sa * (cos(t / samples) - 2 * cos(2 * t / samples)),
            sa * (-sin(3 * t / samples)),
        )
        for t in range(int(t0), int(t1 * samples))
    ]


zz = points(0, 2 * pi, 200)

with BuildPart() as p:
    with BuildLine() as l:
        m1 = Spline(zz, periodic=False)
        m2 = Line(m1 @ 1, m1 @ 0)  # prevent broken STEP
    pln = Plane(m1 @ 0, z_dir=m1 % 0)
    with BuildSketch(pln) as s:
        Circle(18)
    sweep(is_frenet=True)
p.color = "#852e00"
show(p)


# %% Example faces

b = box1.faces("not(|Z or |X or |Y)")
b.name = "faces"
box1.name = "box1"
show(box1, b, names=["box", "faces"])


# %% Example edges

b = box1.edges("not(|Z or |X or |Y)")
b.name = "edges"
box1.name = "box1"
show(box1, b, names=["box", "edges"])


# %% Example faces

b = box1.vertices("not(|Z or |X or |Y)")
b.name = "vertices"
box1.name = "box1"
show(box1, b, names=["box", "vertices"])


# %% Example drops

b = Box(1, 2, 3) - Plane.YZ * Cylinder(0.5, 1)
b = fillet(b.edges().filter_by(Axis.X), 0.3)
b = chamfer(b.edges().filter_by(Axis.Y), 0.1)
b.label = "drops"
show(b)


# %% Example Single faces
b = Box(1, 2, 3)
b = fillet(b.edges(), 0.2).faces()
show(b)


# %% Example Single edges
b = Box(1, 2, 3)
b = fillet(b.edges(), 0.2).edges()
show(b)


# %% Example Single vertices
b = Box(1, 2, 3)
b = fillet(b.edges(), 0.2).vertices()
show(b)
