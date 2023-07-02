# %%
import copy
from functools import reduce

import numpy as np

from build123d import *
from ocp_vscode.animation import Animation, collect_paths
from ocp_vscode import show

thickness = 2
height = 40
width = 65
length = 100
diam = 4
tol = 0.05

# %%

#
# Base and top
#


class Base(Part):
    hinge_x1, hinge_x2 = 0.63, 0.87

    hinges_holes = {
        "right_front": Location((-hinge_x1 * width, -hinge_x1 * length), (0, 0, 195)),
        "right_middle": Location((-hinge_x2 * width, 0), (0, 0, 180)),
        "right_back": Location((-hinge_x1 * width, hinge_x1 * length), (0, 0, 165)),
        "left_front": Location((hinge_x1 * width, -hinge_x1 * length), (0, 0, -15)),
        "left_middle": Location((hinge_x2 * width, 0), (0, 0, 0)),
        "left_back": Location((hinge_x1 * width, hinge_x1 * length), (0, 0, 15)),
    }

    stand_holes = {
        "front_stand": Location((0, -0.8 * length), (0, 0, 180)),
        "back_stand": Location((0, 0.75 * length), (0, 0, 0)),
    }

    def __init__(self, label):
        base = extrude(Ellipse(width, length), thickness)
        base -= Pos(Y=-length + 5) * Box(2 * width, 20, 3 * thickness)

        for pos in self.hinges_holes.values():
            base -= pos * Cylinder(
                diam / 2 + tol,
                thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        for pos in self.stand_holes.values():
            base -= pos * Box(width / 2 + 2 * tol, thickness + 2 * tol, 5 * thickness)

        super().__init__(base.wrapped, label=label)

        # Add joints

        for name, edge in self.hinges_holes.items():
            RigidJoint(f"j_{name}", self, edge)

        for name, pos in self.stand_holes.items():
            RigidJoint(f"j_{name}", self, pos * Rot(0, 0, 90))

        center = self.faces().sort_by().last.center_location
        RigidJoint("j_top", self, center * Pos(Z=height + thickness + 2 * tol))
        RigidJoint("j_bottom", self, center)


base = Base("base")
show(base, render_joints=True)

# %%

#
# Stands
#


class Stand(Part):
    def __init__(self, label):
        self.h = 5

        stand = Box(width / 2 + 10, height + 2 * tol, thickness)
        faces = stand.faces().sort_by(Axis.Y)

        t2 = thickness / 2
        w = height / 2 + tol - self.h / 2
        for i in [-1, 1]:
            rect = Pos(0, i * w, t2) * Rectangle(thickness, self.h)
            block = extrude(rect, self.h)

            m = block.edges().group_by()[-1]
            block = chamfer(
                m.sort_by(Axis.Y).first if i == 1 else m.sort_by(Axis.Y).last,
                length=self.h - 2 * tol,
            )

            stand += block

        for plane in [Plane(faces.first), Plane(faces.last)]:
            stand += plane * Box(
                thickness,
                width / 2,
                thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        super().__init__(stand.wrapped, label=label)

        RigidJoint(
            "j_bottom",
            self,
            self.faces().sort_by(Axis.Y).last.center_location * Rot(0, 180, 0),
        )


stand = Stand("stand")
show(stand, render_joints=True)

# %%

#
# Legs
#


class UpperLeg(Part):
    def __init__(self, label):
        self.l1 = 50
        self.l2 = 80

        leg_hole = Location((self.l2 - 10, 0), (0, 0, 0))

        line = Polyline(
            (0, 0), (0, height / 2), (self.l1, height / 2 - 5), (self.l2, 0)
        )
        line += mirror(line, about=Plane.XZ)
        face = make_face(line)
        upper_leg = extrude(face, thickness, dir=(0, 0, 1))
        upper_leg = fillet(upper_leg.edges().group_by(Axis.X)[-1], radius=4)

        last = upper_leg.edges()
        upper_leg -= leg_hole * Hole(diam / 2 + tol, depth=thickness)
        self.knee_hole = upper_leg.edges().filter_by(GeomType.CIRCLE) - last

        upper_leg += (
            Pos(0, 0, thickness / 2)
            * Rot(90, 0, 0)
            * Cylinder(diam / 2, 2 * (height / 2 + thickness + tol))
        )

        super().__init__(upper_leg.wrapped, label=label)

        RevoluteJoint(
            "j_hinge",
            self,
            axis=-upper_leg.faces().sort_by(Axis.Y).last.center_location.z_axis,
            angular_range=(0, 180),
        )
        RigidJoint(
            "j_knee_front",
            self,
            leg_hole * Rot(180, 0, 0),
        )
        RigidJoint("j_knee_back", self, leg_hole * Pos(0, 0, thickness))


upper_leg = UpperLeg("upper_leg")
show(upper_leg, render_joints=True)

# %%


class LowerLeg(Part):
    def __init__(self, label):
        self.w = 15
        self.l1 = 20
        self.l2 = 120

        leg_hole = Location((self.l1 - 10, 0), (0, 0, 0))

        line = Polyline((0, 0), (self.l1, self.w), (self.l2, 0))
        line += mirror(line, about=Plane.XZ)
        face = make_face(line)
        lower_leg = extrude(face, thickness, dir=(0, 0, 1))
        lower_leg = fillet(lower_leg.edges().filter_by(Axis.Z), radius=4)

        lower_leg -= leg_hole * Hole(diam / 2 + tol, depth=thickness)

        super().__init__(lower_leg.wrapped, label=label)

        RevoluteJoint(
            "j_front",
            self,
            axis=(leg_hole * Pos(0, 0, thickness) * Rot(0, 180, 0)).z_axis,
            angular_range=(-180, 180),
        )
        RevoluteJoint(
            "j_back",
            self,
            axis=(leg_hole * Pos(0, 0, 0)).z_axis,
            angular_range=(-180, 180),
        )


lower_leg = LowerLeg("lower_leg")
show(lower_leg, render_joints=True)

# %%


def reference(obj, label=None, color=None, location=None):
    new_obj = copy.copy(obj)
    if label is not None:
        new_obj.label = label
    if color is not None:
        new_obj.color = color
    if location is None:
        return new_obj
    else:
        return new_obj.move(location)


class Assembly(Compound):
    def __init__(self, label, children, location=None):
        super().__init__(label=label, children=children)
        # The assembly layer will not contain a part, it only needs a location
        self.location = Location() if location is None else location

    def find_object(self, path):
        def _find(obj, path):
            labels = [child.label for child in obj.children]
            top, _, rest = path.lstrip("/").partition("/")

            try:
                ind = labels.index(top)
            except:
                raise RuntimeError(f"Sub path '{path}' is not valid")

            if rest == "":
                return obj.children[ind]
            else:
                return _find(obj.children[ind], rest)

        name, _, rest = path.strip("/").partition("/")
        if name != self.label:
            raise ValueError(f"Path '{path}' not valid")
        elif rest == "":
            return self

        return _find(self, rest)

    def joint_location(self, obj, joint, **kwargs):
        if isinstance(joint, RevoluteJoint):
            loc = obj.location * joint.relative_axis.to_location()
        elif isinstance(joint, RigidJoint):
            loc = obj.location * joint.relative_location
        else:
            raise NotImplementedError()

        if kwargs.get("angle") is not None:
            loc = loc * Rot(0, 0, kwargs["angle"])

        return loc

    def assemble(
        self, path, joint_name, to_path, to_joint_name, animate=False, **kwargs
    ):
        def _relocate(obj, loc):
            if not isinstance(obj, Assembly):
                obj.location = loc.inverse() * obj.location
            for child in obj.children:
                _relocate(child, loc)

        obj = self.find_object(path)
        joint = obj.joints[joint_name]
        loc = self.joint_location(obj, joint, **kwargs)

        to_obj = self.find_object(to_path)
        to_joint = to_obj.joints[to_joint_name]
        to_loc = self.joint_location(to_obj, to_joint, **kwargs)

        if kwargs.get("angle") is not None:
            to_loc = to_loc * Rot(0, 0, kwargs["angle"])

        if animate:
            # relocate to ensure that the joint is used as origin for the animation
            _relocate(obj, loc)

            # Get the parent Assembly layer
            parent_path, _, _ = path.rpartition("/")

            # For sub assemblies, the location gets pushed one level up to the assembly layer
            parent_obj = self.find_object(parent_path)
            parent_obj.location = to_loc
        else:
            # else just use connect_to for flat assemblies
            to_joint.connect_to(joint, **kwargs)


# %%


base = Base("base")
stand = Stand("stand")
upper_leg = UpperLeg("upper_leg")
lower_leg = LowerLeg("lower_leg")

legs = [
    Assembly(
        children=[
            reference(
                upper_leg,
                label="upper_leg",
                location=Pos(i * 200, j * 50, 0),
            ),
            Assembly(
                children=[
                    reference(
                        lower_leg,
                        label="lower_leg",
                        location=Pos(i * 200 + 80, j * 50, 0),
                    )
                ],
                label=f"{side}_{loc}_lower_leg",
            ),
        ],
        label=f"{side}_{loc}_leg",
    )
    for i, side in enumerate(["left", "right"])
    for j, loc in enumerate(["front", "middle", "back"])
]

hexapod = Assembly(
    children=[
        reference(base, label="bottom", color="grey", location=Pos(-100, -100, 0)),
        reference(base, label="top", color="lightgray", location=Pos(-100, 100, 0)),
        reference(stand, label="front_stand", color="skyblue", location=Pos(0, -60, 0)),
        reference(stand, label="back_stand", color="skyblue", location=Pos(0, -120, 0)),
    ]
    + legs,
    label="hexapod",
)

print(hexapod.show_topology())
show(hexapod, render_joints=True)

# %%

hexapod.assemble("/hexapod/back_stand", "j_bottom", "/hexapod/bottom", "j_back_stand")
hexapod.assemble("/hexapod/front_stand", "j_bottom", "/hexapod/bottom", "j_front_stand")
hexapod.assemble("/hexapod/top", "j_bottom", "/hexapod/bottom", "j_top")

for side in ["left", "right"]:
    for loc in ["front", "middle", "back"]:
        hexapod.assemble(
            f"/hexapod/{side}_{loc}_leg/upper_leg",
            "j_hinge",
            f"/hexapod/bottom",
            f"j_{side}_{loc}",
            angle=-90,
            animate=True,
        )
        hexapod.assemble(
            f"/hexapod/{side}_{loc}_leg/{side}_{loc}_lower_leg/lower_leg",
            "j_front",
            f"/hexapod/{side}_{loc}_leg/upper_leg",
            "j_knee_back" if side == "left" else "j_knee_front",
            angle=-105 if side == "left" else 105,
            animate=True,
        )

print(hexapod.show_topology())
show(hexapod, render_joints=False, debug=False)

# %%

#
# Animation
#


def time_range(end, count):
    return np.linspace(0, end, count + 1)


def vertical(count, end, offset):
    ints = [min(180, (90 + i * (360 // count)) % 360) for i in range(count)]
    heights = [round(20 * np.sin(np.deg2rad(x) - 15), 1) for x in ints]
    heights.append(heights[0])
    return time_range(end, count), heights[offset:] + heights[1 : offset + 1]


def horizontal(end, reverse):
    horizontal_angle = 25
    angle = horizontal_angle if reverse else -horizontal_angle
    return time_range(end, 4), [0, angle, 0, -angle, 0]


animation = Animation(hexapod)

for name in Base.hinges_holes.keys():
    times, values = horizontal(4, "middle" not in name)
    animation.add_track(f"/hexapod/{name}_leg", "rz", times, values)

    times, values = vertical(8, 4, 0 if "middle" in name else 4)
    animation.add_track(f"/hexapod/{name}_leg/{name}_lower_leg", "rz", times, values)

animation.animate(2)

# %%
