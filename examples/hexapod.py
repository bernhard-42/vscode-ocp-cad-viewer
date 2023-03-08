from collections import OrderedDict as odict
import numpy as np

import cadquery as cq
from cadquery_massembly import MAssembly, relocate
from jupyter_cadquery import web_color
from jupyter_cadquery.animation import Animation
from ocp_vscode import show

# Parts


class Hexapod:
    def __init__(self):
        self.thickness = 2
        self.height = 40
        self.width = 65
        self.length = 100
        self.diam = 4
        self.tol = 0.05

        self.base_holes_names = []
        self.stand_names = []
        self.leg_names = []

    def create_base(self):
        x1, x2 = 0.63, 0.87
        base_holes = {
            "right_back": (-x1 * self.length, -x1 * self.width),
            "right_middle": (0, -x2 * self.width),
            "right_front": (x1 * self.length, -x1 * self.width),
            "left_back": (-x1 * self.length, x1 * self.width),
            "left_middle": (0, x2 * self.width),
            "left_front": (x1 * self.length, x1 * self.width),
        }
        stand_holes = {
            "front_stand": (0.75 * self.length, 0),
            "back_stand": (-0.8 * self.length, 0),
        }

        self.base_holes_names = list(base_holes.keys())
        self.stand_names = list(stand_holes.keys())

        workplane = cq.Workplane()

        base = (
            workplane.ellipseArc(self.length, self.width, 25, -25, startAtCurrent=False)
            .close()
            .pushPoints(list(base_holes.values()))
            .circle(self.diam / 2 + self.tol)
            .moveTo(*stand_holes["back_stand"])
            .rect(self.thickness + 2 * self.tol, self.width / 2 + 2 * self.tol)
            .moveTo(*stand_holes["front_stand"])
            .rect(self.thickness + 2 * self.tol, self.width / 2 + 2 * self.tol)
            .extrude(self.thickness)
        )

        # tag mating points

        base.faces("<Z").tag("bottom")
        base.faces(">Z").tag("top")

        for name, hole in base_holes.items():
            base.faces("<Z").wires(cq.NearestToPointSelector(hole)).tag(name)

        for name, hole in stand_holes.items():
            base.faces("<Z").wires(cq.NearestToPointSelector(hole)).tag(name)

        return base

    def create_stand(self):
        stand = cq.Workplane().box(self.height, self.width / 2 + 10, self.thickness)
        inset = cq.Workplane().box(self.thickness, self.width / 2, self.thickness)
        backing = (
            cq.Workplane("ZX")
            .polyline([(10, 0), (0, 0), (0, 10)])
            .close()
            .extrude(self.thickness)
        )

        stand = (
            stand.union(inset.translate(((self.height + self.thickness) / 2, 0, 0)))
            .union(inset.translate((-(self.height + self.thickness) / 2, 0, 0)))
            .union(
                backing.translate(
                    (-self.height / 2, -self.thickness / 2, self.thickness / 2)
                )
            )
            .union(
                backing.rotate((0, 0, 0), (0, 1, 0), -90).translate(
                    (self.height / 2, -self.thickness / 2, self.thickness / 2)
                )
            )
        )
        return stand

    def create_upper_leg(self):
        l1, l2 = 50, 80
        pts = [(0, 0), (0, self.height / 2), (l1, self.height / 2 - 5), (l2, 0)]
        upper_leg_hole = (l2 - 10, 0)

        upper_leg = (
            cq.Workplane()
            .polyline(pts)
            .mirrorX()
            .pushPoints([upper_leg_hole])
            .circle(self.diam / 2 + self.tol)
            .extrude(self.thickness)
            .edges("|Z and (not <X)")
            .fillet(4)
        )

        axle = (
            cq.Workplane(
                "XZ",
                origin=(
                    0,
                    self.height / 2 + self.thickness + self.tol,
                    self.thickness / 2,
                ),
            )
            .circle(self.diam / 2)
            .extrude(2 * (self.height / 2 + self.thickness + self.tol))
        )

        upper_leg = upper_leg.union(axle)

        # tag mating points
        upper_leg.faces(">Z").edges(cq.NearestToPointSelector(upper_leg_hole)).tag(
            "top"
        )
        upper_leg.faces("<Z").edges(cq.NearestToPointSelector(upper_leg_hole)).tag(
            "bottom"
        )

        return upper_leg

    def create_lower_leg(self):
        w, l1, l2 = 15, 20, 120
        pts = [(0, 0), (l1, w), (l2, 0)]
        lower_leg_hole = (l1 - 10, 0)

        lower_leg = (
            cq.Workplane()
            .polyline(pts)
            .mirrorX()
            .pushPoints([lower_leg_hole])
            .circle(self.diam / 2 + self.tol)
            .extrude(self.thickness)
            .edges("|Z")
            .fillet(5)
        )

        # tag mating points
        lower_leg.faces(">Z").edges(cq.NearestToPointSelector(lower_leg_hole)).tag(
            "top"
        ),
        lower_leg.faces("<Z").edges(cq.NearestToPointSelector(lower_leg_hole)).tag(
            "bottom"
        )

        return lower_leg

    def create(self):
        leg_angles = {
            "right_back": -105,
            "right_middle": -90,
            "right_front": -75,
            "left_back": 105,
            "left_middle": 90,
            "left_front": 75,
        }
        self.leg_names = list(leg_angles.keys())

        base = self.create_base()
        stand = self.create_stand()
        upper_leg = self.create_upper_leg()
        lower_leg = self.create_lower_leg()

        # Some shortcuts
        L = lambda *args: cq.Location(cq.Vector(*args))
        C = lambda name: web_color(name)

        # Leg assembly
        leg = MAssembly(upper_leg, name="upper", color=C("orange")).add(
            lower_leg, name="lower", color=C("orange"), loc=L(80, 0, 0)
        )
        # Hexapod assembly
        hexapod = (
            MAssembly(
                base, name="bottom", color=C("silver"), loc=L(0, 1.1 * self.width, 0)
            )
            .add(base, name="top", color=C("gainsboro"), loc=L(0, -2.2 * self.width, 0))
            .add(stand, name="front_stand", color=C("SkyBlue"), loc=L(40, 100, 0))
            .add(stand, name="back_stand", color=C("SkyBlue"), loc=L(-40, 100, 0))
        )

        for i, name in enumerate(self.leg_names):
            hexapod.add(leg, name=name, loc=L(100, -55 * (i - 1.7), 0))

        hexapod.mate("bottom?top", name="bottom", origin=True)
        hexapod.mate(
            "top?bottom",
            name="top",
            origin=True,
            transforms=odict(rx=180, tz=-(self.height + 2 * self.tol)),
        )

        for name in self.stand_names:
            hexapod.mate(
                f"bottom?{name}",
                name=f"{name}_bottom",
                transforms=odict(rz=-90 if "f" in name else 90),
            )
            hexapod.mate(
                f"{name}@faces@<X", name=name, origin=True, transforms=odict(rx=180)
            )

        for name in self.base_holes_names:
            hexapod.mate(
                f"bottom?{name}",
                name=f"{name}_hole",
                transforms=odict(rz=leg_angles[name]),
            )

        for name in self.leg_names:
            lower, upper, angle = (
                ("top", "bottom", -75) if "left" in name else ("bottom", "top", -75)
            )
            hexapod.mate(
                f"{name}?{upper}", name=f"leg_{name}_hole", transforms=odict(rz=angle)
            )
            hexapod.mate(
                f"{name}@faces@<Y",
                name=f"leg_{name}_hinge",
                origin=True,
                transforms=odict(rx=180, rz=-90),
            )
            hexapod.mate(
                f"{name}/lower?{lower}", name=f"leg_{name}_lower_hole", origin=True
            )
        self.hexapod = hexapod

    def assemble(self):
        # show(hexapod, reset_camera=False)
        self.hexapod.relocate()

        # Assemble the parts
        for leg in self.leg_names:
            self.hexapod.assemble(f"leg_{leg}_lower_hole", f"leg_{leg}_hole")
            self.hexapod.assemble(f"leg_{leg}_hinge", f"{leg}_hole")

        self.hexapod.assemble("top", "bottom")

        for stand_name in self.stand_names:
            self.hexapod.assemble(f"{stand_name}", f"{stand_name}_bottom")

    def animate(self, speed=3):
        horizontal_angle = 25

        def intervals(count):
            r = [min(180, (90 + i * (360 // count)) % 360) for i in range(count)]
            return r

        def times(end, count):
            return np.linspace(0, end, count + 1)

        def vertical(count, end, offset, reverse):
            ints = intervals(count)
            heights = [round(35 * np.sin(np.deg2rad(x)) - 15, 1) for x in ints]
            heights.append(heights[0])
            return times(end, count), heights[offset:] + heights[1 : offset + 1]

        def horizontal(end, reverse):
            factor = 1 if reverse else -1
            return times(end, 4), [
                0,
                factor * horizontal_angle,
                0,
                -factor * horizontal_angle,
                0,
            ]

        leg_group = ("left_front", "right_middle", "left_back")

        animation = Animation()

        for name in self.leg_names:
            # move upper leg
            animation.add_track(
                f"/bottom/{name}", "rz", *horizontal(4, "middle" in name)
            )

            # move lower leg
            animation.add_track(
                f"/bottom/{name}/lower",
                "rz",
                *vertical(8, 4, 0 if name in leg_group else 4, "left" in name),
            )

        animation.animate(speed=speed)


if __name__ == "__main__":
    hexapod = Hexapod()
    hexapod.create()
    hexapod.assemble()
    show(hexapod.hexapod, render_mates=True, mate_scale=5, reset_camera=True)
    hexapod.animate()
