# %%
import build123d as bd
from ocp_vscode import *

set_defaults(reset_camera=Camera.KEEP)
set_colormap(ColorMap.tab20())

# %%

# geom_type_EDGE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Line
line = bd.Line((0, 0, 0), (1, 1, 1))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Circle
circle = bd.Pos(1, 0, 0) * bd.Circle(0.4).edge()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Arc
arc = bd.CenterArc((1, 1, 0), 0.5, -30, 70)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Ellipse
ellipse = bd.Pos(2, 0, 0) * bd.Ellipse(0.4, 0.2).edge()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Ellipse
ellipse_arc = (
    bd.Pos(2, -1, 0) * bd.Ellipse(0.4, 0.2).edge()
    - bd.Pos(0.8, -1, 0) * bd.Rectangle(2, 2)
)[0]
ellipse_arc2 = bd.Pos(1, -1, 0) * bd.Ellipse(0.4, 0.2).edge() - bd.Pos(
    1.8, -1, 0
) * bd.Rectangle(2, 2)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Hyperbola
c = bd.Cone(1, 0.2, 1)
s = bd.split(c, bd.Plane.YZ.offset(-0.3))
hyperbola = bd.Pos(0, 1, -0.3) * bd.Rot(0, 90, 0) * select_edge(s, 2)
del s, c

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Parabola
c = bd.Cone(1, 0.2, 1)
e = select_edge(c, 1)
l = (
    bd.Plane(e @ 0, x_dir=(0, 1, 0), z_dir=bd.Axis(e).direction)
    .rotated((0, 90, 0))
    .offset(-0.8)
)
s = bd.split(c, l)
parabola = select_edge(s, 2)
del c, e, s, l

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Bezier
bezier2d = bd.Pos(0, 2, 0) * bd.Bezier((0, 0, 0), (1, 2, 0), (3, 0, 0)).edge()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Bspline
bspline2d = bd.Pos(4, 1.5, 0) * bd.Edge.make_spline(
    [
        (-2, 0, 0),
        (0, 0, 0),
        (1, -2, 0),
        (2, 0, 0),
        (1, 1, 0),
    ]
)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Offset
from OCP.Geom import Geom_OffsetCurve
from OCP.gp import gp_Dir
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

BRepBuilderAPI_MakeEdge
e_offset = bd.Pos(4, 4, 0) * bd.Ellipse(1, 2).edge()
c = BRep_Tool.Curve_s(e_offset.wrapped, 0, 1)

o = Geom_OffsetCurve(c, -0.3, gp_Dir(0, 0, 1))
offset_ = bd.Edge(BRepBuilderAPI_MakeEdge(o).Edge())
del c, o, e_offset


# geom_type FACE

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Plane/Circle
circle2d = bd.Pos(8, 0, 0) * bd.Circle(0.6).face()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Plane/Ellipse
ellipse2d = bd.Pos(8, 1, 0) * bd.Ellipse(0.6, 0.2).face()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Plane/EllipseArc
# ellipse_arc2d = bd.Pos(8, 1, 0) * (bd.Ellipse(0.6, 0.2).face() - bd.Pos((0.5,0,0) * bd.Rectangle(2,2)))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Cylinder
cylinder = bd.Pos(10, 0, 0) * bd.Cylinder(0.5, 1).faces().sort_by()[1]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Cone
cone = bd.Pos(10, 2, 0) * bd.Cone(1, 0.2, 1).faces().sort_by()[1]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Sphere
sphere = bd.Pos(8, 4, 0) * bd.Sphere(1).face()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Torus
torus = bd.Pos(10, 4, 0) * bd.Torus(0.7, 0.2).face()
l = bd.CenterArc((0.3, 0, 0), 0.2, 0, 360)
torus2 = bd.Pos(12, 4, 0) * bd.Face.revolve(l, 150, bd.Axis.Y)
del l

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Bezier
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
from OCP.Geom import Geom_BezierSurface
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace

poles = TColgp_Array2OfPnt(1, 3, 1, 3)

poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
poles.SetValue(1, 2, gp_Pnt(0, 1, 0))
poles.SetValue(1, 3, gp_Pnt(0, 2, 0))

poles.SetValue(2, 1, gp_Pnt(1, 0, 0.5))
poles.SetValue(2, 2, gp_Pnt(1, 1, 1.5))
poles.SetValue(2, 3, gp_Pnt(1, 2, 0.5))

poles.SetValue(3, 1, gp_Pnt(2, 0, 0))
poles.SetValue(3, 2, gp_Pnt(2, 1, 0))
poles.SetValue(3, 3, gp_Pnt(2, 2, 0))

bezierSurf = Geom_BezierSurface(poles)

bezier3d = bd.Pos(12, 1, 0) * bd.Face(BRepBuilderAPI_MakeFace(bezierSurf, 1e-6).Face())

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Bspline
from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
from OCP.Geom import Geom_BSplineSurface

poles = TColgp_Array2OfPnt(1, 3, 1, 3)

poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
poles.SetValue(1, 2, gp_Pnt(0, 1, 0))
poles.SetValue(1, 3, gp_Pnt(0, 2, 0))

poles.SetValue(2, 1, gp_Pnt(1, 0, 1))
poles.SetValue(2, 2, gp_Pnt(1, 1, 2))
poles.SetValue(2, 3, gp_Pnt(1, 2, 1))

poles.SetValue(3, 1, gp_Pnt(2, 0, 0))
poles.SetValue(3, 2, gp_Pnt(2, 1, 0))
poles.SetValue(3, 3, gp_Pnt(2, 2, 0))

u_knots = TColStd_Array1OfReal(1, 2)
u_knots.SetValue(1, 0.0)
u_knots.SetValue(2, 1.0)
u_mults = TColStd_Array1OfInteger(1, 2)
u_mults.SetValue(1, 3)
u_mults.SetValue(2, 3)

v_knots = TColStd_Array1OfReal(1, 2)
v_knots.SetValue(1, 0.0)
v_knots.SetValue(2, 1.0)
v_mults = TColStd_Array1OfInteger(1, 2)
v_mults.SetValue(1, 3)
v_mults.SetValue(2, 3)

bsplineSurf = Geom_BSplineSurface(
    poles, u_knots, v_knots, u_mults, v_mults, 2, 2  # degree in U and V
)

# Step 4: Wrap the surface into a face for topology
bspline3d = bd.Pos(15, 0, 0) * bd.Face(
    BRepBuilderAPI_MakeFace(bsplineSurf, 1e-6).Face()
)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Revolution
l = bd.CenterArc((0.1, 0, 0), 0.6, -30, 50)
revolution = bd.Pos(12, 0, 0) * bd.Face.revolve(l, 360, bd.Axis.Y)
del l

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Extrusion
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from OCP.TopoDS import TopoDS

r = bd.Face(bd.Rectangle(0.5, 0.8).wire())
e = BRepPrimAPI_MakePrism(r.wrapped, gp_Vec(0, 0, 1))
e.Build()

del r

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Offset
offset3d = None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Reference face

rect = bd.Location((0, 4, 0), (20, 30, 60)) * bd.Rectangle(1, 2).face()


show_all(exclude=["all_shapes"])


# %%

all_shapes = {
    "line": line,
    "circle": circle,
    "arc": arc,
    "ellipse": ellipse,
    "ellipse_arc": ellipse_arc,
    "ellipse_arc2": ellipse_arc2,
    "hyperbola": hyperbola,
    "parabola": parabola,
    "bezier2d": bezier2d,
    "bspline2d": bspline2d,
    "offset_": offset_,
    "circle2d": circle2d,
    "ellipse2d": ellipse2d,
    "cylinder": cylinder,
    "cone": cone,
    "sphere": sphere,
    "torus": torus,
    "torus2": torus2,
    "bezier3d": bezier3d,
    "bspline3d": bspline3d,
    "revolution": revolution,
    "rect": rect,
}

# %%

from ocp_vscode.measure import get_distance, get_properties
import pprint

pp = pprint.PrettyPrinter(depth=4)


for name, shape in all_shapes.items():
    print(name)
    pp.pprint(get_properties(shape.wrapped))

# %%
for name1, obj1 in [["line", line], ["rect", rect]]:  # all_shapes.items():
    for name2, obj2 in all_shapes.items():
        result = get_distance(obj1.wrapped, obj2.wrapped, False)
        print(name1, name2, "=>")
        pp.pprint(result)
        if result is not None:
            p1 = result["point1"]
            p2 = result["point2"]
            show(obj1, obj2, bd.Vector(p1), bd.Vector(p2))

# %%
from math import pi
import build123d as bd

from ocp_tessellate.ocp_utils import (
    area,
    axis_to_line,
    BoundingBox,
    center_of_mass,
    dist_shapes,
    get_curve,
    get_plane,
    get_point,
    get_surface,
    is_closed,
    is_topods_edge,
    is_topods_face,
    is_topods_solid,
    is_topods_vertex,
    is_vector,
    length,
    position_at,
    vertex,
)


def get_shape_type(shape):
    if is_topods_vertex(shape) or is_vector(shape):
        return "Vertex"
    elif is_topods_edge(shape):
        return "Edge"
    elif is_topods_face(shape):
        return "Face"
    elif is_topods_solid:
        return "Solid"
    else:
        return "Unknown"


def get_geom_type(shape):
    if is_topods_vertex(shape) or is_vector(shape):
        return "Point"
    elif is_topods_edge(shape):
        return get_curve(shape).GetType().name.split("_")[-1]
    elif is_topods_face(shape):
        return get_surface(shape).GetType().name.split("_")[-1]
    elif is_topods_solid:
        return "Solid"
    else:
        return "Unknown"


def properties(shape):
    shape_type = get_shape_type(shape)
    geom_type = get_geom_type(shape)

    props = {
        "shape_type": shape_type,
        "geom_type": geom_type,
    }

    if shape_type == "Vertex":
        props["coords"] = list(shape)

    elif shape_type == "Edge":
        props["length"] = length(shape)

        if geom_type == "Line":
            props["start"] = get_point(position_at(shape, 0))
            props["middle"] = get_point(position_at(shape, 0.5))
            props["end"] = get_point(position_at(shape, 1))

        elif geom_type == "Circle":
            circle = get_curve(shape).Circle()
            props["center"] = get_point(circle.Location())
            props["radius"] = circle.Radius()
            props["start"] = get_point(position_at(shape, 0))
            if not is_closed(shape):
                props["geom_type"] = "Arc"
                props["end"] = get_point(position_at(shape, 1))

        elif geom_type == "Ellipse":
            ellipse = get_curve(shape).Ellipse()
            props["center"] = get_point(ellipse.Location())
            props["major radius"] = ellipse.MajorRadius()
            props["minor radius"] = ellipse.MinorRadius()
            props["focus1"] = get_point(ellipse.Focus1())
            props["focus2"] = get_point(ellipse.Focus2())
            props["start"] = get_point(position_at(shape, 0))
            if not is_closed(shape):
                props["geom_type"] = "Arc"
                props["end"] = get_point(position_at(shape, 1))

        elif geom_type == "Hyperbola":
            hyperbola = get_curve(shape).Hyperbola()
            props["start"] = get_point(position_at(shape, 0))
            props["end"] = get_point(position_at(shape, 1))
            props["vertex"] = get_point(hyperbola.Location())
            props["focus1"] = get_point(hyperbola.Focus1())
            props["focus2"] = get_point(hyperbola.Focus2())

        elif geom_type == "Parabola":
            parabola = get_curve(shape).Parabola()
            props["start"] = get_point(position_at(shape, 0))
            props["end"] = get_point(position_at(shape, 1))
            props["vertex"] = get_point(parabola.Location())
            props["focus"] = get_point(parabola.Focus())

        elif geom_type in ["Bezier", "Bspline"]:
            props["start"] = get_point(position_at(shape, 0))
            props["end"] = get_point(position_at(shape, 1))

        elif geom_type == "Offset":
            offset = get_curve(offset_).OffsetCurve()
            props["start"] = get_point(position_at(shape, 0))
            if is_closed(shape):
                props["end"] = get_point(position_at(shape, 1))
            props["offset"] = offset.Offset()
        else:
            props["start"] = get_point(position_at(shape, 0))
            props["middle"] = get_point(position_at(shape, 0.5))
            props["end"] = get_point(position_at(shape, 1))

    elif shape_type == "Face":
        props["area"] = area(shape)

        if geom_type == "Plane":
            ...
        elif geom_type == "Cylinder":
            cylinder = get_surface(shape).Cylinder()
            props["center"] = get_point(cylinder.Location())

            props["radius"] = cylinder.Radius()
        elif geom_type == "Cone":
            cone = get_surface(shape).Cone()
            props["center"] = get_point(cone.Location())
            props["ref radius"] = cone.RefRadius()
            props["semi angle"] = cone.SemiAngle() / pi * 180

        elif geom_type == "Sphere":
            sphere = get_surface(shape).Sphere()
            props["center"] = get_point(sphere.Location())
            props["radius"] = sphere.Radius()

        elif geom_type == "Torus":
            torus = get_surface(shape).Torus()
            props["center"] = get_point(torus.Location())
            props["minor radius"] = torus.MinorRadius()
            props["major radius"] = torus.MajorRadius()

        elif geom_type in ["Bezier", "Bspline"]:
            ...

        elif geom_type == "SurfaceOfRevolution":
            revolution = get_surface(shape)
            props["axe loc"] = get_point(revolution.AxeOfRevolution().Location())
            props["axe dir"] = get_point(revolution.AxeOfRevolution().Direction())
            props["geom_type"] = "Revolution"
    
    elif shape_type == "Solid":
        
    bb = BoundingBox(shape, optimal=True)
    props["bb"] = {
        "min": [bb.xmin, bb.ymin, bb.zmin],
        "center": bb.center,
        "max": [bb.xmax, bb.ymax, bb.zmax],
        "size": [bb.xsize, bb.ysize, bb.zsize],
    }
    return props


import pprint

pp = pprint.PrettyPrinter(depth=4)

for name, shape in all_shapes.items():
    print(name)
    pp.pprint(properties(shape.wrapped))

# %%


def get_center(shape):
    shape_type = get_shape_type(shape)
    geom_type = get_geom_type(shape)

    if shape_type == "Vertex":
        center = shape

    elif shape_type == "Edge":
        if geom_type == "Circle":
            circle = get_curve(shape).Circle()
            center = circle.Location()

        elif geom_type == "Ellipse":
            ellipse = get_curve(shape).Ellipse()
            center = ellipse.Location()

        elif geom_type == "Hyperbola":
            hyperbola = get_curve(shape).Hyperbola()
            center = hyperbola.Location()

        elif geom_type == "Parabola":
            parabola = get_curve(shape).Parabola()
            center = parabola.Location()

        else:
            center = position_at(shape, 0.5)

    elif shape_type == "Face":
        if geom_type == "Cylinder":
            cylinder = get_surface(shape).Cylinder()
            center = cylinder.Location()

        elif geom_type == "Cone":
            cone = get_surface(shape).Cone()
            center = cone.Location()

        elif geom_type == "Sphere":
            sphere = get_surface(shape).Sphere()
            center = sphere.Location()

        elif geom_type == "Torus":
            torus = get_surface(shape).Torus()
            center = torus.Location()

        elif geom_type == "SurfaceOfRevolution":
            revolution = get_surface(shape)
            center = revolution.AxeOfRevolution().Location()

        else:
            center = center_of_mass(shape)

    if is_topods_vertex(center):
        return center
    else:
        return vertex(center)


def calc_distance(shape1, shape2, center=False):
    if center:
        p1 = get_center(shape1)
        p2 = get_center(shape2)
        dist, p1, p2 = dist_shapes(p1, p2)
    else:
        dist, p1, p2 = dist_shapes(shape1, shape2)
    return {
        "distance": dist,
        "point on shape1": get_point(p1),
        "point on shape2": get_point(p2),
    }


def calc_angle(shape1, shape2):
    shape_type1 = get_shape_type(shape1)
    shape_type2 = get_shape_type(shape2)
    geom_type1 = get_geom_type(shape1)
    geom_type2 = get_geom_type(shape2)

    def angle_line_line(line1, line2):
        if is_topods_edge(line1):
            l1 = get_curve(line1).Line()
        else:
            l1 = line1
        if is_topods_edge(line2):
            l2 = get_curve(line2).Line()
        else:
            l2 = line2
        return l1.Angle(l2) / pi * 180

    def angle_line_plane(line, plane):
        # 90 - angle between line and normal
        axis = plane.Axis()
        line2 = axis_to_line(axis)
        return 90 - angle_line_line(line, line2)

    def angle_plane_plane(plane1, plane2):
        # angle between the two normals
        axis1 = plane1.Axis()
        line1 = axis_to_line(axis1)
        axis2 = plane2.Axis()
        line2 = axis_to_line(axis2)
        return angle_line_line(line1, line2)

    angle = None
    p1 = None
    p2 = None
    info = ""

    if geom_type1 == "Line" and geom_type2 == "Line":
        angle = angle_line_line(shape1, shape2)
        p1 = get_center(shape1)
        p2 = get_center(shape2)
        info1 = "line"
        info2 = "line"

    elif geom_type1 == "Line" and shape_type2 in ["Edge", "Face"]:
        plane2 = get_plane(shape2)
        if plane2 is not None:
            angle = angle_line_plane(shape1, plane2)
            p1 = get_center(shape1)
            p2 = get_center(shape2)
            info1 = "line"
            info2 = f"Plane({shape_type1})"

    elif shape_type1 in ["Edge", "Face"] and geom_type2 == "Line":
        plane1 = get_plane(shape1)
        if plane1 is not None:
            angle = angle_line_plane(shape2, plane1)
            p1 = get_center(shape1)
            p2 = get_center(shape2)
            info1 = f"Plane({shape_type1})"
            info2 = "line"

    elif shape_type1 in ["Edge", "Face"] and shape_type2 in ["Edge", "Face"]:
        plane1 = get_plane(shape1)
        plane2 = get_plane(shape2)
        if plane1 is not None and plane2 is not None:
            angle = angle_plane_plane(plane1, plane2)
            p1 = get_center(shape1)
            p2 = get_center(shape2)
            info1 = f"Plane({shape_type1})"
            info2 = f"Plane({shape_type2})"

    if angle is None:
        return None
    else:
        return {
            "angle": angle,
            "point on shape1": get_point(p1),
            "point on shape2": get_point(p2),
            "info1": info1,
            "info2": info2,
        }


def measure(shape1, shape2, center=False):
    measurement = calc_distance(shape1, shape2, center)
    angle = calc_angle(shape1, shape2)
    if angle is not None:
        measurement["angle"] = angle["angle"]
        measurement["info1"] = angle["info1"]
        measurement["info2"] = angle["info2"]
    return measurement


# %%

print(calc_angle(line.wrapped, bspline2d.wrapped))
# %%
for name1, obj1 in [["line", line], ["rect", rect]]:  # all_shapes.items():
    for name2, obj2 in all_shapes.items():
        result = measure(obj1.wrapped, obj2.wrapped)
        print(name1, name2, "=>")
        pp.pprint(result)
        if result is not None:
            p1 = result["point_on_shape1"]
            p2 = result["point_on_shape2"]
            show(obj1, obj2, bd.Vector(p1), bd.Vector(p2))
