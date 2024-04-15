import pytest
import unittest

from build123d import *
from ocp_vscode import show, show_all


# pylint: disable=invalid-name
def _assertTupleAlmostEquals(self, expected, actual, places, msg=None):
    for i, j in zip(actual, expected):
        self.assertAlmostEqual(i, j, places, msg=msg)


# pylint: disable=invalid-name
def _assertBboxAlmostEquals(self, expected, actual, places, msg=None):
    for key in expected.keys():
        self.assertAlmostEqual(expected[key], actual[key], places, msg=msg)


unittest.TestCase.assertTupleAlmostEquals = _assertTupleAlmostEquals
unittest.TestCase.assertBboxAlmostEquals = _assertBboxAlmostEquals


class ObjectTests(unittest.TestCase):

    def test_show_simple_box(self):
        obj = Box(1, 1, 1)
        ([instances, shapes, states, config, count_shapes], mapping) = show(
            obj, _test=True
        )
        self.assertTupleAlmostEquals(
            shapes["parts"][0]["loc"][0], (-0.5, -0.5, -0.5), 6
        )
        self.assertTupleAlmostEquals(
            shapes["parts"][0]["loc"][1], (0.0, 0.0, 0.0, 1.0), 6
        )
        self.assertBboxAlmostEquals(
            shapes["bb"],
            dict(xmin=-0.5, xmax=0.5, ymin=-0.5, ymax=0.5, zmin=-0.5, zmax=0.5),
            6,
        )

    def test_show_all(self):
        box = Box(1, 2, 3)
        box.color = "black"
        cyl = Cylinder(0.3, 4)
        cyl.color = "cyan"
        sphere = Sphere(0.7)
        sphere.color = "silver"
        sphere.name = "sphere"
        dbox = Box(2, 0.3, 0.3)
        dbox.label = "dbox"
        dbox.color = "darkgreen"
        i = 42
        col = (Color("green"), Color("red"))
        align = (Align.CENTER, Align.CENTER)
        pos = [Pos(1, 1)]
        loc = GridLocations(1, 1, 5, 5)
        loc.label = "gridloc"
        emptyObject = Circle(1) - Circle(1)

        result = show_all(_test=True)
        instances, shapes, states, config, count_shapes = result[0]
        mapping = result[1]
        self.assertEqual(len(instances), 4)

        self.assertEqual(shapes["version"], 2)
        self.assertEqual(len(shapes["parts"]), 7)
        self.assertListEqual(
            [el.get("id") for el in shapes["parts"]],
            [
                "/Group/box",
                "/Group/cyl",
                "/Group/sphere",
                "/Group/dbox",
                "/Group/pos",
                "/Group/loc",
                "/Group/emptyObject (empty)",
            ],
        )
        self.assertListEqual(
            [el.get("color") for el in shapes["parts"]],
            [
                "#000000",
                "#00ffff",
                "#c0c0c0",
                "#006400",
                ["#ff0000", "#008000", "#0000ff"],
                None,
                "#ba55d3",
            ],
        )
        self.assertEqual(len(mapping["parts"]), 7)
        self.assertEqual(len(mapping["parts"][5]["parts"]), 25)

    def test_show(self):
        box = Box(1, 2, 3)
        box.color = "black"
        cyl = Cylinder(0.3, 4)
        cyl.color = "cyan"
        sphere = Sphere(0.7)
        sphere.color = "silver"
        sphere.name = "sphere"
        dbox = Box(2, 0.3, 0.3)
        dbox.label = "dbox"
        dbox.color = "darkgreen"
        i = 42
        col = (Color("green"), Color("red"))
        align = (Align.CENTER, Align.CENTER)
        pos = [Pos(1, 1)]
        loc = GridLocations(1, 1, 5, 5)
        loc.label = "gridloc"
        emptyObject = Circle(1) - Circle(1)

        array = (
            box,
            align,
            i,
            cyl,
            emptyObject,
            [sphere],
            [dbox, i, loc, pos, sphere, col],
        )

        result = show(
            *array,
            _test=True,
        )
        instances, shapes, states, config, count_shapes = result[0]
        mapping = result[1]
        self.assertEqual(len(instances), 4)

        self.assertEqual(shapes["version"], 2)
        self.assertEqual(len(shapes["parts"]), 5)
        self.assertListEqual(
            [el.get("id") for el in shapes["parts"]],
            [
                "/Group/Solid",
                "/Group/Solid(2)",
                "/Group/Object (empty)",
                "/Group/sphere",
                "/Group/List",
            ],
        )
        self.assertListEqual(
            [el.get("color") for el in shapes["parts"]],
            ["#000000", "#00ffff", "#ba55d3", "#c0c0c0", None],
        )
        self.assertEqual(len(mapping["parts"]), 5)
        self.assertEqual(len(mapping["parts"][4]["parts"][1]["parts"]), 25)

    def test_show_with_names(self):
        box = Box(1, 2, 3)
        box.color = "black"
        cyl = Cylinder(0.3, 4)
        cyl.color = "cyan"
        sphere = Sphere(0.7)
        sphere.color = "silver"
        sphere.name = "sphere"
        dbox = Box(2, 0.3, 0.3)
        dbox.label = "dbox"
        dbox.color = "darkgreen"
        i = 42
        col = (Color("green"), Color("red"))
        align = (Align.CENTER, Align.CENTER)
        pos = [Pos(1, 1)]
        loc = GridLocations(1, 1, 5, 5)
        loc.label = "gridloc"
        emptyObject = Circle(1) - Circle(1)

        array = (
            box,
            align,
            i,
            cyl,
            emptyObject,
            [sphere],
            [dbox, i, loc, pos, sphere, col],
        )

        result = show(
            *array,
            names=["box", "align", "int", "cyl", "emptyObjects", "sphere", "array"],
            _test=True,
        )
        instances, shapes, states, config, count_shapes = result[0]
        mapping = result[1]
        self.assertEqual(len(instances), 4)

        self.assertEqual(shapes["version"], 2)
        self.assertEqual(len(shapes["parts"]), 5)
        self.assertListEqual(
            [el.get("id") for el in shapes["parts"]],
            [
                "/Group/box",
                "/Group/cyl",
                "/Group/emptyObjects (empty)",
                "/Group/sphere",
                "/Group/array",
            ],
        )
        self.assertListEqual(
            [el.get("color") for el in shapes["parts"]],
            ["#000000", "#00ffff", "#ba55d3", "#c0c0c0", None],
        )
        self.assertEqual(len(mapping["parts"]), 5)
        self.assertEqual(len(mapping["parts"][4]["parts"][1]["parts"]), 25)
