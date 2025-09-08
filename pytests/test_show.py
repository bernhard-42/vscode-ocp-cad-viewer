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
        self.assertTupleAlmostEquals(self.parts[ind]["loc"][0], translation, places)
        self.assertTupleAlmostEquals(self.parts[ind]["loc"][1], quaternion, places)

    def assertBboxEqual(self, expected, places=6, msg=None):
        actual = self.shapes["bb"]
        for key in expected.keys():
            self.assertAlmostEqual(expected[key], actual[key], places, msg=msg)

    def assertPartsElementsEqual(self, key, expected):
        self.assertListEqual([el.get(key) for el in self.parts], expected)

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
        self.assertEqual(len(self.shapes["parts"]), 6)

        self.assertPartsElementsEqual(
            "id",
            [
                "/Group/Solid",
                "/Group/List",
                "/Group/Solid(2)",
                "/Group/Object (empty)",
                "/Group/List(2)",
                "/Group/List(3)",
            ],
        )
        self.assertEqual(self.parts[4]["parts"][0]["id"], "/Group/List(2)/sphere")
        self.assertPartsElementsEqual(
            "color",
            ["#000000", None, "#00ffff", "#000000", None, None],
        )
        self.assertEqual(self.parts[4]["parts"][0]["color"], "#c0c0c0")

        self.assertEqual(len(self.mapping["parts"]), 6)
        self.assertEqual(len(self.mapping["parts"][5]["parts"][1]["parts"]), 25)

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
        self.assertPartsElementsEqual(
            "id",
            [
                "/Group/box",
                "/Group/align",
                "/Group/cyl",
                "/Group/emptyObject (empty)",
                "/Group/sphere",
                "/Group/array",
            ],
        )


class ShowAllTests(Tests):
    def test_show_aligns(self):
        MIDDLE = (Align.CENTER, Align.CENTER)

        r = show_all()

        self.get(r)
        self.assertPartsElementsEqual(
            "id",
            [
                "/MIDDLE/MIDDLE (empty)",
            ],
        )

    def test_show_pos_list(self):
        a = [Pos(1, 1)]

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 0)
        self.assertEqual(len(self.parts), 1)
        self.assertEqual(self.parts[0]["name"], "Location")
        self.assertPartsElementsEqual(
            "id",
            ["/a/Location"],
        )

    def test_show_pos(self):
        a = Pos(1, 1)

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 0)
        self.assertEqual(len(self.parts), 1)
        self.assertEqual(self.parts[0]["name"], "a")
        self.assertPartsElementsEqual(
            "id",
            ["/Group/a"],
        )

    def test_show_color(self):
        p = Sphere(1)
        p.color = Color(0x00FF00)

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 1)
        self.assertEqual(len(self.parts), 1)
        self.assertEqual(self.parts[0]["name"], "p")
        self.assertPartsElementsEqual(
            "id",
            ["/Group/p"],
        )
        self.assertPartsElementsEqual(
            "color",
            ["#00ff00"],
        )

    def test_show_color_in_list(self):
        p = Sphere(1)
        p.color = Color(0x00FF00)
        p = [p]

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 1)
        self.assertEqual(len(self.parts), 1)
        self.assertEqual(self.parts[0]["name"], "Solid")
        self.assertPartsElementsEqual(
            "id",
            ["/p/Solid"],
        )
        self.assertPartsElementsEqual(
            "color",
            ["#00ff00"],
        )

    def test_show_tuple(self):
        p = (Circle(1),)

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 1)
        self.assertEqual(len(self.parts), 1)
        self.assertEqual(self.parts[0]["name"], "Face")
        self.assertPartsElementsEqual("id", ["/p/Face"])

    def test_show_gridlocations(self):
        loc = GridLocations(1, 1, 5, 5)

        r = show_all()

        self.get(r)
        self.assertEqual(len(self.instances), 0)
        self.assertEqual(len(self.parts), 25)
        self.assertEqual(self.parts[0]["name"], "Location")
        self.assertPartsElementsEqual(
            "id",
            [
                "/loc/Location",
                "/loc/Location(2)",
                "/loc/Location(3)",
                "/loc/Location(4)",
                "/loc/Location(5)",
                "/loc/Location(6)",
                "/loc/Location(7)",
                "/loc/Location(8)",
                "/loc/Location(9)",
                "/loc/Location(10)",
                "/loc/Location(11)",
                "/loc/Location(12)",
                "/loc/Location(13)",
                "/loc/Location(14)",
                "/loc/Location(15)",
                "/loc/Location(16)",
                "/loc/Location(17)",
                "/loc/Location(18)",
                "/loc/Location(19)",
                "/loc/Location(20)",
                "/loc/Location(21)",
                "/loc/Location(22)",
                "/loc/Location(23)",
                "/loc/Location(24)",
                "/loc/Location(25)",
            ],
        )

    def test_show_empty(self):
        s = Circle(1) - Circle(1)

        r = show_all()
        self.get(r)
        self.assertEqual(len(self.instances), 0)
        self.assertEqual(self.parts[0]["name"], "s (empty)")
        self.assertPartsElementsEqual(
            "id",
            ["/Group/s (empty)"],
        )

    def test_show_multi(self):
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
        self.assertEqual(len(self.parts), 9)
        self.assertPartsElementsEqual(
            "id",
            [
                "/Group/box",
                "/Group/cyl",
                "/Group/sphere",
                "/Group/dbox",
                "/Group/col",
                "/Group/align",
                "/Group/pos",
                "/Group/loc",
                "/Group/emptyObject (empty)",
            ],
        )
        self.assertPartsElementsEqual(
            "color",
            [
                "#000000",
                "#00ffff",
                "#c0c0c0",
                "#006400",
                None,
                None,
                None,
                None,
                "#000000",
            ],
        )
        self.assertListEqual(
            self.parts[6]["parts"][0]["color"], ["#ff0000", "#008000", "#0000ff"]
        )
        self.assertListEqual(
            self.parts[7]["parts"][0]["color"], ["#ff0000", "#008000", "#0000ff"]
        )
        self.assertListEqual(
            self.parts[7]["parts"][24]["color"], ["#ff0000", "#008000", "#0000ff"]
        )
        self.assertEqual(len(self.mapping["parts"]), 9)
        self.assertEqual(len(self.mapping["parts"][7]["parts"]), 25)


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
        self.assertEqual(self.parts[2]["shape"].get("ref"), 0)

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

    def test_show_vector(self):

        r = show(Vector(1, 2, 3), Vector(4, 5, 6), names=["a", "b"])

        self.get(r)
        self.assertEqual(len(self.parts), 2)

    def test_show_vector(self):

        r = show(Vector(1, 2, 3), Vector(4, 5, 6), names=["a"])

        self.get(r)
        self.assertEqual(len(self.parts), 2)
        self.assertPartsElementsEqual(
            "id",
            ["/Group/a", "/Group/Vertex"],
        )

    def test_show_dict(self):

        r = show(dict(b=Box(1, 2, 3), c=Cylinder(0.1, 5)))

        self.get(r)
        self.assertEqual(len(self.parts), 2)
        self.assertPartsElementsEqual(
            "id",
            ["/Dict/b", "/Dict/c"],
        )

    def test_show_named_dict(self):

        r = show(dict(b=Box(1, 2, 3), c=Cylinder(0.1, 5)), names=["boxcyl"])

        self.get(r)
        self.assertEqual(len(self.parts), 2)
        self.assertPartsElementsEqual(
            "id",
            ["/boxcyl/b", "/boxcyl/c"],
        )


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
        c.color = (0, 1, 1)
        s.color = bd.Color(1, 0.5, 0)
        c2.color = ot.utils.Color((0, 128, 255)).percentage
        t.color = ot.utils.Color((0.25, 1, 0.5)).percentage

        r = show((b, c, s, c2, t))

        self.get(r)
        self.assertEqual(self.parts[0]["color"], "#0000ff")
        self.assertEqual(self.parts[1]["color"], "#00ffff")
        self.assertEqual(self.parts[2]["color"], "#ff7f00")
        self.assertEqual(self.parts[3]["color"], "#0080ff")
        self.assertEqual(self.parts[4]["color"], "#3fff7f")
