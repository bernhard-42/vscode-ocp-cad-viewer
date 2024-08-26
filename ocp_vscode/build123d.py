"""A minimum subset of build123d to support backend.py"""

# pylint: disable=missing-class-docstring,missing-function-docstring,import-error,no-name-in-module
# pyright: reportMissingModuleSource=false

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#              THIS FILE IS AN EXTRACT OF http://github.com/gumyr/build123d
#                      ALL CREDITS GO TO ROGER MAITLAND
#  THE CODE IS SHORTEND/STREAMLINED TO ONLY SUPPORT THE CONCEPTS NEEDED BY backend.py
#                      ALL NEW BUGS ARE OF COURSE MINE!
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import copy
import math
from enum import Enum, auto
from typing import Iterable

import OCP.GeomAbs as ga
import OCP.TopAbs as ta
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakeVertex
from OCP.BRepGProp import BRepGProp, BRepGProp_Face
from OCP.BRepLib import BRepLib_FindSurface
from OCP.BRepTools import BRepTools
from OCP.GCPnts import GCPnts_AbscissaPoint
from OCP.Geom import Geom_Plane
from OCP.gp import (
    gp_Dir,
    gp_Pnt,
    gp_Trsf,
    gp_Vec,
    gp_GTrsf,
    gp_Ax1,
    gp_Ax3,
    gp_EulerSequence,
    gp_Quaternion,
)
from OCP.GProp import GProp_GProps
from OCP.Standard import Standard_Failure, Standard_NoSuchObject
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Vertex, TopoDS_Iterator
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from ocp_tessellate.ocp_utils import get_faces, get_edges, get_vertices


downcast_LUT = {
    ta.TopAbs_VERTEX: TopoDS.Vertex_s,
    ta.TopAbs_EDGE: TopoDS.Edge_s,
    ta.TopAbs_WIRE: TopoDS.Wire_s,
    ta.TopAbs_FACE: TopoDS.Face_s,
    ta.TopAbs_SHELL: TopoDS.Shell_s,
    ta.TopAbs_SOLID: TopoDS.Solid_s,
    ta.TopAbs_COMPOUND: TopoDS.Compound_s,
    ta.TopAbs_COMPSOLID: TopoDS.CompSolid_s,
}

geom_LUT = {
    ta.TopAbs_VERTEX: "Vertex",
    ta.TopAbs_EDGE: BRepAdaptor_Curve,
    ta.TopAbs_WIRE: "Wire",
    ta.TopAbs_FACE: BRepAdaptor_Surface,
    ta.TopAbs_SHELL: "Shell",
    ta.TopAbs_SOLID: "Solid",
    ta.TopAbs_COMPOUND: "Compound",
    ta.TopAbs_COMPSOLID: "Compound",
}


geom_LUT_FACE = {
    ga.GeomAbs_Plane: "PLANE",
    ga.GeomAbs_Cylinder: "CYLINDER",
    ga.GeomAbs_Cone: "CONE",
    ga.GeomAbs_Sphere: "SPHERE",
    ga.GeomAbs_Torus: "TORUS",
    ga.GeomAbs_BezierSurface: "BEZIER",
    ga.GeomAbs_BSplineSurface: "BSPLINE",
    ga.GeomAbs_SurfaceOfRevolution: "REVOLUTION",
    ga.GeomAbs_SurfaceOfExtrusion: "EXTRUSION",
    ga.GeomAbs_OffsetSurface: "OFFSET",
    ga.GeomAbs_OtherSurface: "OTHER",
}

geom_LUT_EDGE = {
    ga.GeomAbs_Line: "LINE",
    ga.GeomAbs_Circle: "CIRCLE",
    ga.GeomAbs_Ellipse: "ELLIPSE",
    ga.GeomAbs_Hyperbola: "HYPERBOLA",
    ga.GeomAbs_Parabola: "PARABOLA",
    ga.GeomAbs_BezierCurve: "BEZIER",
    ga.GeomAbs_BSplineCurve: "BSPLINE",
    ga.GeomAbs_OffsetCurve: "OFFSET",
    ga.GeomAbs_OtherCurve: "OTHER",
}

shape_properties_LUT = {
    ta.TopAbs_VERTEX: None,
    ta.TopAbs_EDGE: BRepGProp.LinearProperties_s,
    ta.TopAbs_WIRE: BRepGProp.LinearProperties_s,
    ta.TopAbs_FACE: BRepGProp.SurfaceProperties_s,
    ta.TopAbs_SHELL: BRepGProp.SurfaceProperties_s,
    ta.TopAbs_SOLID: BRepGProp.VolumeProperties_s,
    ta.TopAbs_COMPOUND: BRepGProp.VolumeProperties_s,
    ta.TopAbs_COMPSOLID: BRepGProp.VolumeProperties_s,
}


def shapetype(obj):
    """Return TopoDS_Shape's TopAbs_ShapeEnum"""
    if obj.IsNull():
        raise ValueError("Null TopoDS_Shape object")

    return obj.ShapeType()


def downcast(obj):
    """Downcasts a TopoDS object to suitable specialized type

    Args:
      obj: TopoDS_Shape:

    Returns:

    """

    f_downcast = downcast_LUT[shapetype(obj)]
    return_value = f_downcast(obj)

    return return_value


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Vector
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Vector:
    def __init__(self, x, y=None, z=None):
        if isinstance(x, (gp_Pnt, gp_Dir)):
            self.wrapped = gp_Vec(x.XYZ())
        elif isinstance(x, gp_Vec):
            self.wrapped = x
        elif isinstance(x, (list, tuple)):
            self.wrapped = gp_Vec(*x)
        elif isinstance(x, Vector):
            self.wrapped = gp_Vec(x.wrapped.XYZ())
        else:
            self.wrapped = gp_Vec(x, y, z)

        self.X = self.wrapped.X()  # pylint: disable=invalid-name
        self.Y = self.wrapped.Y()  # pylint: disable=invalid-name
        self.Z = self.wrapped.Z()  # pylint: disable=invalid-name

    def normalized(self):
        return Vector(self.wrapped.Normalized())

    def center(self):
        return self

    @property
    def length(self):
        return self.wrapped.Magnitude()

    def sub(self, vec):
        if isinstance(vec, Vector):
            result = Vector(self.wrapped.Subtracted(vec.wrapped))
        elif isinstance(vec, tuple):
            result = Vector(self.wrapped.Subtracted(Vector(vec).wrapped))
        else:
            raise ValueError("Only Vectors or tuples can be subtracted from Vectors")

        return result

    def __sub__(self, vec):
        return self.sub(vec)

    def multiply(self, scale):
        return Vector(self.wrapped.Multiplied(scale))

    def __mul__(self, scale):
        return self.multiply(scale)

    def __truediv__(self, denom):
        return self.multiply(1.0 / denom)

    def __rmul__(self, scale):
        return self.multiply(scale)

    def to_tuple(self):
        return (self.X, self.Y, self.Z)

    def to_pnt(self):
        return gp_Pnt(self.wrapped.XYZ())

    def to_dir(self):
        return gp_Dir(self.wrapped.XYZ())

    def get_angle(self, vec):
        return math.degrees(self.wrapped.Angle(vec.wrapped))

    def __repr__(self):
        return "Vector: " + str((self.X, self.Y, self.Z))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Axis(metaclass=AxisMeta)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class AxisMeta(type):
    @property
    def X(cls):  # pylint: disable=invalid-name
        return Axis((0, 0, 0), (1, 0, 0))

    @property
    def Y(cls):  # pylint: disable=invalid-name
        return Axis((0, 0, 0), (0, 1, 0))

    @property
    def Z(cls):  # pylint: disable=invalid-name
        return Axis((0, 0, 0), (0, 0, 1))


class Axis(metaclass=AxisMeta):
    def __init__(self, position=None, direction=None):
        self.position = Vector(0, 0, 0) if position is None else Vector(position)
        self.direction = Vector(0, 0, 1) if direction is None else Vector(direction)

    def __repr__(self):
        return f"({self.position.to_tuple()},{self.direction.to_tuple()})"

    @property
    def location(self):
        return Location(Plane(self.position, z_dir=self.direction))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Matrix
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Matrix:
    def __init__(self):
        self.wrapped = gp_GTrsf()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Location
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Location:

    @property
    def position(self):
        return Vector(self.to_tuple()[0])

    def __init__(self, *args):
        # pylint: disable=too-many-branches
        transform = gp_Trsf()

        if len(args) == 0:
            pass

        elif len(args) == 1:
            translation = args[0]

            if isinstance(translation, (Vector, Iterable)):
                transform.SetTranslationPart(Vector(translation).wrapped)
            elif isinstance(translation, Plane):
                coordinate_system = gp_Ax3(
                    translation.origin.to_pnt(),
                    translation.z_dir.to_dir(),
                    translation.x_dir.to_dir(),
                )
                transform.SetTransformation(coordinate_system)
                transform.Invert()
            elif isinstance(args[0], Location):
                self.wrapped = translation.wrapped
                return
            elif isinstance(translation, TopLoc_Location):
                self.wrapped = translation
                return
            elif isinstance(translation, gp_Trsf):
                transform = translation
            else:
                raise TypeError("Unexpected parameters")

        elif len(args) == 2:
            if isinstance(args[0], (Vector, Iterable)):
                if isinstance(args[1], (Vector, Iterable)):
                    rotation = [math.radians(a) for a in args[1]]
                    quaternion = gp_Quaternion()
                    quaternion.SetEulerAngles(
                        gp_EulerSequence.gp_Intrinsic_XYZ, *rotation
                    )
                    transform.SetRotation(quaternion)
                elif isinstance(args[0], (Vector, tuple)) and isinstance(
                    args[1], (int, float)
                ):
                    angle = math.radians(args[1])
                    quaternion = gp_Quaternion()
                    quaternion.SetEulerAngles(
                        gp_EulerSequence.gp_Intrinsic_XYZ, 0, 0, angle
                    )
                    transform.SetRotation(quaternion)

                # set translation part after setting rotation (if exists)
                transform.SetTranslationPart(Vector(args[0]).wrapped)
            else:
                translation, origin = args
                coordinate_system = gp_Ax3(
                    Vector(origin).to_pnt(),
                    translation.z_dir.to_dir(),
                    translation.x_dir.to_dir(),
                )
                transform.SetTransformation(coordinate_system)
                transform.Invert()
        elif len(args) == 3:
            if (
                isinstance(args[0], (Vector, Iterable))
                and isinstance(args[1], (Vector, Iterable))
                and isinstance(args[2], (int, float))
            ):
                translation, axis, angle = args
                transform.SetRotation(
                    gp_Ax1(Vector().to_pnt(), Vector(axis).to_dir()),
                    math.radians(angle),
                )
            else:
                raise TypeError("Unsupported argument types for Location")

            transform.SetTranslationPart(Vector(translation).wrapped)
        self.wrapped = TopLoc_Location(transform)

    def inverse(self):
        return Location(self.wrapped.Inverted())

    def __mul__(self, other):
        if hasattr(other, "wrapped") and not isinstance(
            other.wrapped, TopLoc_Location
        ):  # Shape
            result = other.moved(self)
        elif isinstance(other, Iterable) and all(
            isinstance(o, Location) for o in other
        ):
            result = [Location(self.wrapped * loc.wrapped) for loc in other]
        else:
            result = Location(self.wrapped * other.wrapped)
        return result

    def to_tuple(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        transformation = self.wrapped.Transformation()
        trans = transformation.TranslationPart()
        rot = transformation.GetRotation()

        rv_trans = (trans.X(), trans.Y(), trans.Z())
        rv_rot = [
            math.degrees(a)
            for a in rot.GetEulerAngles(gp_EulerSequence.gp_Intrinsic_XYZ)
        ]

        return rv_trans, tuple(rv_rot)

    def __repr__(self):
        position_str = ", ".join((f"{v:.2f}" for v in self.to_tuple()[0]))
        orientation_str = ", ".join((f"{v:.2f}" for v in self.to_tuple()[1]))
        return f"(p=({position_str}), o=({orientation_str}))"

    def __str__(self):
        position_str = ", ".join((f"{v:.2f}" for v in self.to_tuple()[0]))
        orientation_str = ", ".join((f"{v:.2f}" for v in self.to_tuple()[1]))
        return f"Location: (position=({position_str}), orientation=({orientation_str}))"


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Plane
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Plane:
    def __init__(self, obj, x_dir=None, z_dir=None):
        if isinstance(obj, Vector):
            self.origin = obj
            self.z_dir = Vector(z_dir)
            if x_dir:
                self.x_dir = Vector(x_dir)
            else:
                ax3 = gp_Ax3(self.origin.to_pnt(), self.z_dir.to_dir())
                self.x_dir = Vector(ax3.XDirection()).normalized()

        elif isinstance(obj, Face):
            surface = BRep_Tool.Surface_s(obj.wrapped)
            if not isinstance(surface, Geom_Plane):
                raise ValueError("Planes can only be created from planar faces")
            properties = GProp_GProps()
            BRepGProp.SurfaceProperties_s(obj.wrapped, properties)
            self.origin = Vector(properties.CentreOfMass())
            self.x_dir = (
                Vector(x_dir)
                if x_dir
                else Vector(BRep_Tool.Surface_s(obj.wrapped).Position().XDirection())
            )
            self.z_dir = Plane.get_topods_face_normal(obj.wrapped)
        else:
            raise ValueError(f"Unable to create Plane from {type(obj)}")

    @property
    def location(self):
        return Location(self)

    @staticmethod
    def get_topods_face_normal(face):
        gp_pnt = gp_Pnt()
        normal = gp_Vec()
        projector = GeomAPI_ProjectPointOnSurf(gp_pnt, BRep_Tool.Surface_s(face))
        u_val, v_val = projector.LowerDistanceParameters()
        BRepGProp_Face(face).Normal(u_val, v_val, gp_pnt, normal)
        return Vector(normal)

    def to_local_coords(self, obj):
        # simplified version for Face only, not part of the original build123d
        l = Plane(Face(obj.wrapped)).location
        return Face(obj.wrapped.Moved(l.wrapped.Inverted()))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# ShapeList(list)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class ShapeList(list):
    def filter_by(self, geom_type):
        return [obj for obj in self if obj.geom_type == geom_type]

    def sort_by(self, axis, reverse=False):
        axis_as_location = axis.location.inverse()
        objects = sorted(
            self,
            key=lambda o: (axis_as_location * Location(o.center())).position.Z,
            reverse=reverse,
        )
        return ShapeList(objects)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Shape
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Shape:
    def __init__(self, obj):
        self.wrapped = downcast(obj)

    @property
    def geom_type(self):
        shape = shapetype(self.wrapped)

        if shape == ta.TopAbs_EDGE:
            geom = geom_LUT_EDGE[BRepAdaptor_Curve(self.wrapped).GetType()]
        elif shape == ta.TopAbs_FACE:
            geom = geom_LUT_FACE[BRepAdaptor_Surface(self.wrapped).GetType()]
        elif shape == ta.TopAbs_VERTEX:
            geom = "VERTEX"
        elif shape == ta.TopAbs_SOLID:
            geom = "SOLID"
        else:
            geom = "UNKNOWN"

        return geom

    @property
    def area(self):
        properties = GProp_GProps()
        BRepGProp.SurfaceProperties_s(self.wrapped, properties)

        return properties.Mass()

    @staticmethod
    def compute_mass(obj):
        properties = GProp_GProps()
        calc_function = shape_properties_LUT[shapetype(obj.wrapped)]
        calc_function(obj.wrapped, properties)
        return properties.Mass()

    @property
    def volume(self):
        return Shape.compute_mass(self)

    @classmethod
    def cast(cls, obj):
        new_shape = None

        constructor__lut = {
            ta.TopAbs_VERTEX: Vertex,
            ta.TopAbs_EDGE: Edge,
            # ta.TopAbs_WIRE: Wire,
            ta.TopAbs_FACE: Face,
            ta.TopAbs_SHELL: Shell,
            ta.TopAbs_SOLID: Solid,
            ta.TopAbs_COMPOUND: Compound,
        }

        shape_type = shapetype(obj)
        new_shape = constructor__lut[shape_type](downcast(obj))

        return new_shape

    def transform_shape(self, t_matrix):
        if isinstance(self, Vertex):
            new_shape = Vertex(*t_matrix.multiply(Vector(self)))
        else:
            transformed = Shape.cast(
                BRepBuilderAPI_Transform(self.wrapped, t_matrix.wrapped.Trsf()).Shape()
            )
            new_shape = copy.deepcopy(self, None)
            new_shape.wrapped = transformed.wrapped

        return new_shape

    def edges(self):
        return ShapeList(
            [
                Edge(obj)
                for obj in ShapeList(get_edges(self.wrapped))
                if not BRep_Tool.Degenerated_s(TopoDS.Edge_s(obj))
            ]
        )

    def vertices(self):
        return ShapeList([Vertex(obj) for obj in ShapeList(get_vertices(self.wrapped))])

    def faces(self):
        return ShapeList([Face(obj) for obj in ShapeList(get_faces(self.wrapped))])


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Compound(Shape)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def unwrapped_shapetype(obj: Shape):
    """Return Shape's TopAbs_ShapeEnum"""
    if isinstance(obj, Compound):
        shapetypes = set(shapetype(o.wrapped) for o in obj)
        if len(shapetypes) == 1:
            result = shapetypes.pop()
        else:
            result = shapetype(obj)
    else:
        result = shapetype(obj.wrapped)
    return result


class Compound(Shape):
    def center(self):
        properties = GProp_GProps()
        calc_function = shape_properties_LUT[unwrapped_shapetype(self)]
        if calc_function:
            calc_function(self.wrapped, properties)
            middle = Vector(properties.CentreOfMass())
        return middle

    def __iter__(self):
        iterator = TopoDS_Iterator(self.wrapped)

        while iterator.More():
            yield Shape.cast(iterator.Value())
            iterator.Next()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Solid(Shape)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Solid(Shape):
    def center(self):
        properties = GProp_GProps()
        calc_function = shape_properties_LUT[shapetype(self.wrapped)]
        if calc_function:
            calc_function(self.wrapped, properties)
            middle = Vector(properties.CentreOfMass())
        else:
            raise NotImplementedError
        return middle


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Shell(Shape)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Shell(Shape):
    def center(self):
        properties = GProp_GProps()
        BRepGProp.LinearProperties_s(self.wrapped, properties)
        return Vector(properties.CentreOfMass())


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Face(Shape)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Face(Shape):
    def _geom_adaptor(self):
        return BRep_Tool.Surface_s(self.wrapped)

    @property
    def length(self):
        result = None
        if self.geom_type == "PLANE":
            flat_face = Plane(self).to_local_coords(self)
            face_vertices = flat_face.vertices().sort_by(Axis.X)
            result = face_vertices[-1].X - face_vertices[0].X
        return result

    @property
    def width(self):
        result = None
        if self.geom_type == "PLANE":
            flat_face = Plane(self).to_local_coords(self)
            face_vertices = flat_face.vertices().sort_by(Axis.Y)
            result = face_vertices[-1].Y - face_vertices[0].Y
        return result

    def _uv_bounds(self):
        return BRepTools.UVBounds_s(self.wrapped)

    def center(self):
        if self.geom_type == "PLANE":
            properties = GProp_GProps()
            BRepGProp.SurfaceProperties_s(self.wrapped, properties)
            center_point = properties.CentreOfMass()

        else:
            u_val0, u_val1, v_val0, v_val1 = self._uv_bounds()
            u_val = 0.5 * (u_val0 + u_val1)
            v_val = 0.5 * (v_val0 + v_val1)

            center_point = gp_Pnt()
            normal = gp_Vec()
            BRepGProp_Face(self.wrapped).Normal(u_val, v_val, center_point, normal)

        return Vector(center_point)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Edge(Shape)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Edge(Shape):
    def _geom_adaptor(self):
        return BRepAdaptor_Curve(self.wrapped)

    @property
    def radius(self):
        geom = self._geom_adaptor()
        try:
            circ = geom.Circle()
        except (Standard_NoSuchObject, Standard_Failure) as err:
            raise ValueError("Shape could not be reduced to a circle") from err
        return circ.Radius()

    @property
    def length(self):
        return GCPnts_AbscissaPoint.Length_s(self._geom_adaptor())

    def tangent_at(
        self,
        location_param=0.5,
    ):
        curve = self._geom_adaptor()

        tmp = gp_Pnt()
        res = gp_Vec()

        curve.D1(location_param, tmp, res)

        return Vector(res)

    def normal(self):
        curve = self._geom_adaptor()
        gtype = self.geom_type

        if gtype == "CIRCLE":
            circ = curve.Circle()
            return_value = Vector(circ.Axis().Direction())
        elif gtype == "ELLIPSE":
            ell = curve.Ellipse()
            return_value = Vector(ell.Axis().Direction())
        else:
            find_surface = BRepLib_FindSurface(self.wrapped, OnlyPlane=True)
            surf = find_surface.Surface()

            if isinstance(surf, Geom_Plane):
                pln = surf.Pln()
                return_value = Vector(pln.Axis().Direction())
            else:
                raise ValueError("Normal not defined")

        return return_value

    def position_at(self, distance: float) -> Vector:
        curve = self._geom_adaptor()
        param = self.param_at(distance)
        return Vector(curve.Value(param))

    def param_at(self, distance: float) -> float:
        curve = self._geom_adaptor()

        length = GCPnts_AbscissaPoint.Length_s(curve)
        return GCPnts_AbscissaPoint(
            curve, length * distance, curve.FirstParameter()
        ).Parameter()

    def __mod__(self, position):
        return self.tangent_at(position)

    def __matmul__(self, position):
        return self.position_at(position)

    def center(self):
        return self.position_at(0.5)

    @property
    def arc_center(self):
        geom_type = self.geom_type
        geom_adaptor = self._geom_adaptor()

        if geom_type == "CIRCLE":
            return_value = Vector(geom_adaptor.Circle().Position().Location())
        elif geom_type == "ELLIPSE":
            return_value = Vector(geom_adaptor.Ellipse().Position().Location())
        else:
            raise ValueError(f"{geom_type} has no arc center")

        return return_value


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Vertex(Shape)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Vertex(Shape):
    def __init__(self, x, y=None, z=None, ocp_vx=None):
        if isinstance(x, (tuple, list)):
            x, y, z = x
        elif isinstance(self, Vector):
            x, y, z = x.to_tuple()
        elif isinstance(x, Vertex):
            x, y, z = x.X, x.Y, x.Z
        elif isinstance(x, TopoDS_Vertex):
            ocp_vx = x

        ocp_vx = (
            downcast(BRepBuilderAPI_MakeVertex(gp_Pnt(x, y, z)).Vertex())
            if ocp_vx is None
            else ocp_vx
        )

        super().__init__(ocp_vx)
        self.X, self.Y, self.Z = self.to_tuple()  # pylint: disable=invalid-name

    def to_tuple(self):
        geom_point = BRep_Tool.Pnt_s(self.wrapped)
        return (geom_point.X(), geom_point.Y(), geom_point.Z())

    def center(self):
        return Vector(*self.to_tuple())
