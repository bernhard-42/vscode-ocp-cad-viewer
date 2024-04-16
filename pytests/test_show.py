# %%
import pytest
import threading
import unittest

from build123d import *
from ocp_vscode import show, show_all
import build123d as bd
import ocp_tessellate as ot

# %%


class Tests(unittest.TestCase):
    def get(self, result):
        self.result = result

    @property
    def instances(self):
        return self.result[0][0]

    @property
    def shapes(self):
        return self.result[0][1]

    @property
    def parts(self):
        return self.result[0][1]["parts"]

    @property
    def states(self):
        return self.result[0][2]

    @property
    def config(self):
        return self.result[0][3]

    @property
    def count_shapes(self):
        return self.result[0][4]

    @property
    def mapping(self):
        return self.result[1]

    def assertTupleAlmostEquals(self, expected, actual, places, msg=None):
        for i, j in zip(actual, expected):
            self.assertAlmostEqual(i, j, places, msg=msg)

    def assertLocationEqual(self, ind, translation, quaternion, places=6):
        self.assertTupleAlmostEquals(
            self.shapes["parts"][ind]["loc"][0], translation, places
        )
        self.assertTupleAlmostEquals(
            self.shapes["parts"][ind]["loc"][1], quaternion, places
        )

    def assertBboxEqual(self, expected, places=6, msg=None):
        actual = self.shapes["bb"]
        for key in expected.keys():
            self.assertAlmostEqual(expected[key], actual[key], places, msg=msg)

    def assertPartsList(self, key, expected):
        self.assertListEqual([el.get(key) for el in self.shapes["parts"]], expected)

    def assertShapesEqual(self, key, value):
        self.assertEqual(self.shapes[key], value)


class ShowTests(Tests):

    def test_show_simple_box(self):
        obj = Box(1, 1, 1)

        r = show(obj)

        self.get(r)
        self.assertLocationEqual(0, (-0.5, -0.5, -0.5), (0.0, 0.0, 0.0, 1.0))
        self.assertBboxEqual(
            dict(xmin=-0.5, xmax=0.5, ymin=-0.5, ymax=0.5, zmin=-0.5, zmax=0.5)
        )

    def test_show_nested_array(self):
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
            align,  # not to show
            i,  # not to show
            cyl,
            emptyObject,  # test empty object
            [sphere],
            [
                dbox,
                i,  # not to show
                loc,
                pos,
                sphere,
                col,  # not to show
            ],
        )

        r = show(*array)

        self.get(r)
        self.assertEqual(len(self.instances), 4)
        self.assertEqual(self.shapes["version"], 3)
        self.assertEqual(len(self.shapes["parts"]), 5)

        self.assertListEqual(
            [el.get("id") for el in self.shapes["parts"]],
            [
                "/Group/Solid",
                "/Group/Solid(2)",
                "/Group/Object (empty)",
                "/Group/sphere",
                "/Group/List",
            ],
        )
        self.assertListEqual(
            [el.get("color") for el in self.shapes["parts"]],
            ["#000000", "#00ffff", "#7b2d06", "#c0c0c0", None],
        )

        self.assertEqual(len(self.mapping["parts"]), 5)
        self.assertEqual(len(self.mapping["parts"][4]["parts"][1]["parts"]), 25)

    def test_show_nested_array_with_names(self):
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
            align,  # not to show
            i,  # not to show
            cyl,
            emptyObject,  # empty object
            [sphere],
            [
                dbox,
                i,  # not to show
                loc,
                pos,
                sphere,
                col,  # not to show
            ],
        )

        r = show(
            *array,
            names=["box", "align", "i", "cyl", "emptyObject", "sphere", "array"],
        )

        self.get(r)
        self.assertListEqual(
            [el.get("id") for el in self.shapes["parts"]],
            [
                "/Group/box",
                "/Group/cyl",
                "/Group/emptyObject (empty)",
                "/Group/sphere",
                "/Group/array",
            ],
        )


class ShowAllTests(Tests):

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
        i = 42  # not to show
        col = (Color("green"), Color("red"))  # not to show
        align = (Align.CENTER, Align.CENTER)  # not to show
        pos = [Pos(1, 1)]
        loc = GridLocations(1, 1, 5, 5)
        loc.label = "gridloc"
        emptyObject = Circle(1) - Circle(1)  # empty object

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 4)
        self.assertEqual(self.shapes["version"], 3)
        self.assertEqual(len(self.parts), 7)
        self.assertPartsList(
            "id",
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
        self.assertPartsList(
            "color",
            [
                "#000000",
                "#00ffff",
                "#c0c0c0",
                "#006400",
                ["#ff0000", "#008000", "#0000ff"],
                None,
                "#7b2d06",
            ],
        )

        self.assertEqual(len(self.mapping["parts"]), 7)
        self.assertEqual(len(self.mapping["parts"][5]["parts"]), 25)


class SimpleShowTests(Tests):

    def test_show_part(self):
        with BuildPart() as obj:
            Box(1, 2, 3)

        r = show(obj, obj.part, obj.part.wrapped)

        self.get(r)
        self.assertEqual(len(self.parts), 3)
        self.assertEqual(len(self.instances), 1)
        self.assertEqual(self.parts[0]["shape"].get("ref"), 0)
        self.assertEqual(self.parts[1]["shape"].get("ref"), 0)
        self.assertNotEqual(self.parts[2]["shape"].get("ref"), 0)

    def test_show_part_solid(self):
        with BuildPart() as obj:
            Box(1, 2, 3)

        # force the wrapped part to be a solid and not a compound
        r = show(obj, obj.part, obj.part.solid().wrapped)

        self.get(r)
        self.assertEqual(len(self.parts), 3)
        self.assertEqual(len(self.instances), 1)
        self.assertEqual(self.parts[0]["shape"].get("ref"), 0)
        self.assertEqual(self.parts[1]["shape"].get("ref"), 0)
        self.assertEqual(self.parts[2]["shape"].get("ref"), 0)

    def test_show_sketch(self):
        with BuildSketch() as obj:
            Rectangle(1, 2)

        r = show(obj, obj.sketch, obj.sketch.wrapped)

        self.get(r)
        self.assertEqual(len(self.parts), 3)

    def test_show_line(self):
        with BuildLine() as obj:
            Line((0, 1), (2, 3))

        r = show(obj, obj.line, obj.line.wrapped)

        self.get(r)
        self.assertEqual(len(self.parts), 3)


class ConfigTests(Tests):
    def test_name(self):
        b = Box(1, 2, 3)
        b.name = "box"

        r = show(b)

        self.get(r)
        self.assertEqual(self.parts[0]["name"], "box")

    def test_name_list(self):
        b = Box(1, 2, 3)
        c = Cylinder(1, 2)
        b.name = "box"
        c.name = "cyl"

        r = show((b, c))

        self.get(r)
        self.assertEqual(self.parts[0]["name"], "box")
        self.assertEqual(self.parts[1]["name"], "cyl")

    def test_color(self):
        b = Box(1, 2, 3)
        b.color = "blue"

        r = show(b)

        self.get(r)
        self.assertEqual(self.parts[0]["color"], "#0000ff")

    def test_color_list(self):
        b = Box(1, 2, 3)
        c = Cylinder(1, 2)
        s = Sphere(1)
        c2 = Cone(2, 1, 3)
        t = Torus(5, 1)
        b.color = "blue"
        c.color = (0, 255, 255)
        s.color = bd.Color(1, 0.5, 0)
        c2.color = ot.utils.Color((0, 128, 255))
        t.color = ot.utils.Color((0.25, 1, 0.5))

        r = show((b, c, s, c2, t))

        self.get(r)
        self.assertEqual(self.parts[0]["color"], "#0000ff")
        self.assertEqual(self.parts[1]["color"], "#00ffff")
        self.assertEqual(self.parts[2]["color"], "#ff7f00")
        self.assertEqual(self.parts[3]["color"], "#0080ff")
        self.assertEqual(self.parts[4]["color"], "#3fff7f")
