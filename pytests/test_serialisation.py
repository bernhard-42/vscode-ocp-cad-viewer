# pylint: disable=missing-class-docstring,missing-function-docstring

import unittest
import pytest
import json
import math
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir
from ocp_vscode.show import _convert
from ocp_vscode.backend import ViewerBackend
from ocp_vscode.comms import default
from ocp_vscode.build123d import *
from ocp_tessellate.ocp_utils import get_edges, get_faces, get_vertices


class DirectApiTestCase(unittest.TestCase):
    def assertTupleAlmostEquals(self, first, second, places, msg=None):
        """Check Tuples"""
        self.assertEqual(len(second), len(first))
        for i, j in zip(second, first):
            self.assertAlmostEqual(i, j, places, msg=msg)

    def assertTupleOfTupleAlmostEquals(self, first, second, places, msg=None):
        """Check Tuples"""
        self.assertEqual(len(second), len(first))
        for i, j in zip(second, first):
            self.assertTupleAlmostEquals(i, j, places, msg=msg)

    def assertVectorAlmostEquals(self, first, second, places, msg=None):
        second_vector = Vector(second)
        self.assertAlmostEqual(first.X, second_vector.X, places, msg=msg)
        self.assertAlmostEqual(first.Y, second_vector.Y, places, msg=msg)
        self.assertAlmostEqual(first.Z, second_vector.Z, places, msg=msg)


class VectorTests(DirectApiTestCase):
    def test_tuple(self):
        vec = Vector(1, 2, 3)
        vec2 = Vector((1, 2, 3))
        self.assertTupleAlmostEquals(vec.to_tuple(), (1, 2, 3), 6)
        self.assertTupleAlmostEquals(vec2.to_tuple(), (1, 2, 3), 6)

    def test_gp_pnt(self):
        vec = Vector(gp_Pnt(1, 2, 3))
        self.assertTupleAlmostEquals(vec.to_tuple(), (1, 2, 3), 6)

    def test_gp_vec(self):
        vec = Vector(gp_Vec(1, 2, 3))
        self.assertTupleAlmostEquals(vec.to_tuple(), (1, 2, 3), 6)

    def test_gp_dir(self):
        vec = Vector(gp_Dir(1, 2, 3))
        norm = math.sqrt(1**2 + 2**2 + 3**2)
        self.assertTupleAlmostEquals(vec.to_tuple(), (1 / norm, 2 / norm, 3 / norm), 6)

    def test_normalized(self):
        vec = Vector(gp_Vec(1, 2, 3)).normalized()
        vec2 = Vector(gp_Dir(1, 2, 3))
        self.assertTupleAlmostEquals(vec.to_tuple(), vec2.to_tuple(), 6)

    def test_angle(self):
        vec = Vector(1, 0, 0)
        self.assertAlmostEqual(vec.get_angle(Vector(0, 1, 0)), 90, 6)
        self.assertAlmostEqual(vec.get_angle(Vector(1, 1, 0)), 45, 6)
        self.assertAlmostEqual(vec.get_angle(Vector(1, -1, 0)), 45, 6)


class AxisTests(DirectApiTestCase):
    def test_axis(self):
        a = Axis()
        self.assertTupleAlmostEquals(a.position.to_tuple(), (0, 0, 0), 6)
        self.assertTupleAlmostEquals(a.direction.to_tuple(), (0, 0, 1), 6)
        b = Axis((1, 2, 3), (4, 5, 6))
        self.assertTupleAlmostEquals(b.position.to_tuple(), (1, 2, 3), 6)
        self.assertTupleAlmostEquals(b.direction.to_tuple(), (4, 5, 6), 6)

    def test_axis_x(self):
        a = Axis.X
        self.assertTupleAlmostEquals(a.position.to_tuple(), (0, 0, 0), 6)
        self.assertTupleAlmostEquals(a.direction.to_tuple(), (1, 0, 0), 6)

    def test_axis_y(self):
        a = Axis.Y
        self.assertTupleAlmostEquals(a.position.to_tuple(), (0, 0, 0), 6)
        self.assertTupleAlmostEquals(a.direction.to_tuple(), (0, 1, 0), 6)

    def test_axis_z(self):
        a = Axis.Z
        self.assertTupleAlmostEquals(a.position.to_tuple(), (0, 0, 0), 6)
        self.assertTupleAlmostEquals(a.direction.to_tuple(), (0, 0, 1), 6)


class PlaneTests(DirectApiTestCase):
    def test_face(self):
        box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Solid()
        fillet = BRepFilletAPI_MakeFillet(box)
        for edge in get_edges(box):
            fillet.Add(0.2, edge)
        fillet.Build()
        box = Solid(fillet.Shape())

        faces = box.faces()
        p = Plane(faces[0])

        self.assertTupleAlmostEquals(p.origin.to_tuple(), (0.0, 1.0, 1.5), 6)
        self.assertTupleAlmostEquals(p.x_dir.to_tuple(), (0.0, 0.0, 1.0), 6)
        self.assertTupleAlmostEquals(p.z_dir.to_tuple(), (-1.0, 0.0, 0.0), 6)

        p = Plane(faces[23])

        self.assertTupleAlmostEquals(p.origin.to_tuple(), (1.0, 1.0, 1.5), 6)
        self.assertTupleAlmostEquals(p.x_dir.to_tuple(), (0.0, 0.0, 1.0), 6)
        self.assertTupleAlmostEquals(p.z_dir.to_tuple(), (1.0, 0.0, 0.0), 6)

        p = Plane(faces[10])

        self.assertTupleAlmostEquals(p.origin.to_tuple(), (0.5, 1.0, 3), 6)
        self.assertTupleAlmostEquals(p.x_dir.to_tuple(), (1.0, 0.0, 0), 6)
        self.assertTupleAlmostEquals(p.z_dir.to_tuple(), (0.0, 0.0, 1.0), 6)

    def test_edge(self):
        p = Plane(Vector(1, 1, 1), z_dir=(0, 1, 0))

        self.assertTupleAlmostEquals(p.origin.to_tuple(), (1, 1, 1), 6)
        self.assertTupleAlmostEquals(p.x_dir.to_tuple(), (0, 0, 1), 6)
        self.assertTupleAlmostEquals(p.z_dir.to_tuple(), (0, 1, 0), 6)


class ShapeListTests(DirectApiTestCase):
    def test_lists(self):
        box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Solid()
        fillet = BRepFilletAPI_MakeFillet(box)
        for edge in get_edges(box):
            fillet.Add(0.2, edge)
        fillet.Build()
        box = Solid(fillet.Shape())

        faces = box.faces()
        edges = box.edges()
        vertices = box.vertices()

        self.assertEqual(len(faces), 26)
        self.assertEqual(len(edges), 48)
        self.assertEqual(len(vertices), 24)

        self.assertEqual(len(box.edges().filter_by("LINE")), 24)
        self.assertEqual(len(box.edges().filter_by("CIRCLE")), 24)
        self.assertEqual(len(box.edges().filter_by("OTHER")), 0)

        self.assertEqual(len(box.faces().filter_by("PLANE")), 6)
        self.assertEqual(len(box.faces().filter_by("CYLINDER")), 12)
        self.assertEqual(len(box.faces().filter_by("SPHERE")), 8)
        self.assertEqual(len(box.faces().filter_by("OTHER")), 0)


class ObjectTests(DirectApiTestCase):
    def test_load(self):
        box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Solid()
        _, mapping = _convert(box)
        data = {"model": mapping}
        j = json.dumps(data, default=default).encode("utf-8")

        backend = ViewerBackend(9999)
        backend.load_model(json.loads(j)["model"])

        self.assertEqual(
            list(backend.model.keys()),
            [
                "/Group/Solid",
                "/Group/Solid/faces/faces_0",
                "/Group/Solid/faces/faces_1",
                "/Group/Solid/faces/faces_2",
                "/Group/Solid/faces/faces_3",
                "/Group/Solid/faces/faces_4",
                "/Group/Solid/faces/faces_5",
                "/Group/Solid/edges/edges_0",
                "/Group/Solid/edges/edges_1",
                "/Group/Solid/edges/edges_2",
                "/Group/Solid/edges/edges_3",
                "/Group/Solid/edges/edges_4",
                "/Group/Solid/edges/edges_5",
                "/Group/Solid/edges/edges_6",
                "/Group/Solid/edges/edges_7",
                "/Group/Solid/edges/edges_8",
                "/Group/Solid/edges/edges_9",
                "/Group/Solid/edges/edges_10",
                "/Group/Solid/edges/edges_11",
                "/Group/Solid/vertices/vertices0",
                "/Group/Solid/vertices/vertices1",
                "/Group/Solid/vertices/vertices2",
                "/Group/Solid/vertices/vertices3",
                "/Group/Solid/vertices/vertices4",
                "/Group/Solid/vertices/vertices5",
                "/Group/Solid/vertices/vertices6",
                "/Group/Solid/vertices/vertices7",
            ],
        )
        self.assertEqual(
            [isinstance(v, Face) for k, v in backend.model.items()],
            [
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
        )
        self.assertEqual(
            [isinstance(v, Edge) for k, v in backend.model.items()],
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
        )
        self.assertEqual(
            [isinstance(v, Vertex) for k, v in backend.model.items()],
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            ],
        )
        self.assertEqual(
            [isinstance(v, Compound) for k, v in backend.model.items()],
            [
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
        )
        self.assertEqual(
            [v.area for k, v in backend.model.items() if isinstance(v, Face)],
            [6.0, 6.0, 3.0, 3.0, 2.0, 2.0],
        )
        self.assertEqual(
            [v.length for k, v in backend.model.items() if isinstance(v, Edge)],
            [3.0, 2.0, 3.0, 2.0, 3.0, 2.0, 3.0, 2.0, 1.0, 1.0, 1.0, 1.0],
        )
        self.assertEqual(backend.model["/Group/Solid"].volume, 6)

    def test_fillet(self):
        box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Solid()
        fillet = BRepFilletAPI_MakeFillet(box)
        for edge in get_edges(box):
            fillet.Add(0.2, edge)
        fillet.Build()
        box = fillet.Shape()
        _, mapping = _convert(box)
        data = {"model": mapping}
        j = json.dumps(data, default=default).encode("utf-8")

        backend = ViewerBackend(9999)
        backend.load_model(json.loads(j)["model"])

        self.assertEqual(
            [v.geom_type() for k, v in backend.model.items()],
            [
                "Solid",
                "PLANE",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "SPHERE",
                "SPHERE",
                "PLANE",
                "PLANE",
                "SPHERE",
                "PLANE",
                "SPHERE",
                "PLANE",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "CYLINDER",
                "SPHERE",
                "SPHERE",
                "PLANE",
                "SPHERE",
                "SPHERE",
                "LINE",
                "LINE",
                "LINE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "CIRCLE",
                "LINE",
                "OTHER",
                "CIRCLE",
                "OTHER",
                "CIRCLE",
                "LINE",
                "LINE",
                "LINE",
                "LINE",
                "LINE",
                "LINE",
                "OTHER",
                "CIRCLE",
                "LINE",
                "LINE",
                "LINE",
                "OTHER",
                "CIRCLE",
                "LINE",
                "LINE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "CIRCLE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "LINE",
                "CIRCLE",
                "CIRCLE",
                "OTHER",
                "OTHER",
                "OTHER",
                "OTHER",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
                "Vertex",
            ],
        )
        vec = [v.to_tuple() for v in backend.model.values() if isinstance(v, Vertex)]
        self.assertTupleOfTupleAlmostEquals(
            vec,
            [
                (-2.7755575615628914e-17, 0.19999999999999998, 0.19999999999999998),
                (-2.7755575615628914e-17, 0.19999999999999998, 2.8),
                (-2.7755575615628914e-17, 1.8, 0.19999999999999998),
                (-2.7755575615628914e-17, 1.8, 2.8),
                (0.19999999999999998, -2.7755575615628914e-17, 0.19999999999999998),
                (0.19999999999999998, -2.7755575615628914e-17, 2.8),
                (0.19999999999999998, 0.19999999999999998, 0.0),
                (0.19999999999999998, 1.8, 0.0),
                (0.19999999999999998, 0.19999999999999998, 3.0),
                (0.19999999999999998, 1.8, 3.0),
                (0.19999999999999998, 2.0, 0.19999999999999998),
                (0.19999999999999998, 2.0, 2.8),
                (0.8, -2.7755575615628914e-17, 0.19999999999999998),
                (0.8, -2.7755575615628914e-17, 2.8),
                (0.8, 0.19999999999999998, 0.0),
                (0.8, 1.8, 0.0),
                (0.8, 0.19999999999999998, 3.0),
                (0.8, 1.8, 3.0),
                (0.8, 2.0, 0.19999999999999998),
                (0.8, 2.0, 2.8),
                (1.0, 0.19999999999999998, 0.19999999999999998),
                (1.0, 0.19999999999999998, 2.8),
                (1.0, 1.8, 0.19999999999999998),
                (1.0, 1.8, 2.8),
            ],
            6,
        )

        vec = [
            (v.radius if v.geom_type() in ["CIRCLE"] else -1, v.length)
            for v in backend.model.values()
            if isinstance(v, Edge)
        ]
        self.assertTupleOfTupleAlmostEquals(
            vec,
            [
                (-1, 2.5999999999999996),
                (-1, 1.6),
                (-1, 1.6),
                (-1, 2.5999999999999996),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 2.5999999999999996),
                (0.2, 0.3141592653589793),
                (-1, 1.6),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 1.6),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 2.5999999999999996),
                (-1, 1.92367069372179e-17),
                (0.2, 0.3141592653589793),
                (-1, 1.92367069372179e-17),
                (0.2, 0.3141592653589793),
                (-1, 0.6000000000000001),
                (-1, 0.6000000000000001),
                (-1, 2.5999999999999996),
                (-1, 0.6000000000000001),
                (-1, 0.6000000000000001),
                (-1, 1.6),
                (-1, 1.92367069372179e-17),
                (0.2, 0.3141592653589793),
                (-1, 0.6000000000000001),
                (-1, 0.6000000000000001),
                (-1, 1.6),
                (-1, 1.92367069372179e-17),
                (0.2, 0.3141592653589793),
                (-1, 0.6000000000000001),
                (-1, 0.6000000000000001),
                (-1, 2.5999999999999996),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 2.5999999999999996),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 1.6),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 1.6),
                (0.2, 0.3141592653589793),
                (-1, 2.5999999999999996),
                (0.2, 0.3141592653589793),
                (0.2, 0.3141592653589793),
                (-1, 1.92367069372179e-17),
                (-1, 1.92367069372179e-17),
                (-1, 1.92367069372179e-17),
                (-1, 1.92367069372179e-17),
            ],
            6,
        )
        # vec = [
        #     (, v.length, v.width, v.area)
        #     for v in backend.model.values()
        #     if isinstance(v, Face)
        # ]
