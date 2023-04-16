from build123d import *
from ocp_vscode import show, set_defaults
from ocp_vscode.animation import Animation
import copy


# https://stackoverflow.com/a/6027615


def flatten(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def collect_joints(assembly, path=""):
    result = {}
    for child in assembly.children:
        if len(child.joints) > 0:
            result[child.label] = child.joints
        if len(child.children) > 0:
            result[child.label] = collect_joints(child)
    return flatten(result)


def show_joints(part):
    joints = []
    if len(part.children) == 0:
        show(
            part,
            *[j.symbol for j in part.joints.values()],
            names=["part"] + list(part.joints.keys()),
        )
    else:
        joints = []
        for label, joint in collect_joints(part).items():
            s = copy.deepcopy(joint.symbol)
            s.label = label
            joints.append(s)
        j_group = Compound(label="joints")
        j_group2 = Compound(label="joints")
        j_group2.children = joints
        j_group.children = [j_group2]
        show(
            part,
            j_group,
        )


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
show_joints(base)

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
show_joints(stand)

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
        upper_leg = extrude(face, thickness / 2, both=True)
        upper_leg = fillet(upper_leg.edges().group_by(Axis.X)[-1], radius=4)

        last = upper_leg.edges()
        upper_leg -= leg_hole * Hole(diam / 2 + tol, depth=thickness)
        self.knee_hole = upper_leg.edges().filter_by(GeomType.CIRCLE) - last

        upper_leg += Rot(90, 0, 0) * Cylinder(
            diam / 2, 2 * (height / 2 + thickness + tol)
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
            leg_hole * Location((0, 0, -thickness / 2), (0, 0, 180)),
        )
        RigidJoint(
            "j_knee_back",
            self,
            leg_hole * Location((0, 0, thickness / 2), (0, 0, 180)),
        )


upper_leg = UpperLeg("upper_leg")
show_joints(upper_leg)

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
        lower_leg = extrude(face, amount=thickness / 2, both=True)
        lower_leg = fillet(lower_leg.edges().filter_by(Axis.Z), radius=4)

        lower_leg -= leg_hole * Hole(diam / 2 + tol, depth=thickness)

        super().__init__(lower_leg.wrapped, label=label)

        RevoluteJoint(
            "j_front",
            self,
            axis=(leg_hole * Pos(0, 0, thickness / 2)).z_axis,
            angular_range=(0, 180),
        )
        RevoluteJoint(
            "j_back",
            self,
            axis=(leg_hole * Pos(0, 0, -thickness / 2) * Rot(0, 180, 0)).z_axis,
            angular_range=(0, 180),
        )


lower_leg = LowerLeg("lower_leg")
show_joints(lower_leg)

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


def assembly(children, label):
    compound = Compound(label=label, children=[copy.copy(child) for child in children])
    return compound


def find_object(compound, path):
    labels = [child.label for child in compound.children]
    top, _, rest = path.lstrip("/").partition("/")

    try:
        ind = labels.index(top)
    except:
        return None

    if rest == "":
        return compound.children[ind]
    else:
        return find_object(compound.children[ind], rest)


def assemble(assembly, path, joint, to_path, to_joint, **kwargs):
    print(path, joint, to_path, to_joint)
    j = find_object(assembly, path).joints[joint]
    to_j = find_object(assembly, to_path).joints[to_joint]
    to_j.connect_to(j, **kwargs)


# %%


a_legs = [
    assembly(
        [
            reference(upper_leg, label="upper_leg"),
            reference(lower_leg, label="lower_leg", location=Pos(0, 50, 0)),
        ],
        label=f"{side}_{loc}_leg",
    )
    for i, side in enumerate(["left", "right"])
    for j, loc in enumerate(["front", "middle", "back"])
]

hexapod = assembly(
    children=[
        reference(base, label="bottom", color="grey", location=Pos(0, 100, 0)),
        reference(base, label="top", color="lightgray", location=Pos(0, -100, 0)),
        reference(
            stand, label="front_stand", color="skyblue", location=Pos(-100, 100, 0)
        ),
        reference(
            stand, label="back_stand", color="skyblue", location=Pos(-100, -100, 0)
        ),
    ]
    + a_legs,
    label="hexapod",
)

assemble(hexapod, "back_stand", "j_bottom", "bottom", "j_back_stand")
assemble(hexapod, "front_stand", "j_bottom", "bottom", "j_front_stand")
assemble(hexapod, "top", "j_bottom", "bottom", "j_top")
for side in ["left", "right"]:
    for loc in ["front", "middle", "back"]:
        assemble(
            hexapod,
            f"{side}_{loc}_leg/upper_leg",
            "j_hinge",
            f"bottom",
            f"j_{side}_{loc}",
            angle=180,
        )
        assemble(
            hexapod,
            f"{side}_{loc}_leg/lower_leg",
            "j_front" if side == "left" else "j_back",
            f"{side}_{loc}_leg/upper_leg",
            "j_knee_back" if side == "left" else "j_knee_front",
            angle=105,
        )

print(hexapod.show_topology())
show(hexapod)


# #
# # Animation
# #


# def time_range(end, count):
#     return np.linspace(0, end, count + 1)


# def vertical(count, end, offset):
#     ints = [min(180, (90 + i * (360 // count)) % 360) for i in range(count)]
#     heights = [round(20 * np.sin(np.deg2rad(x) - 15), 1) for x in ints]
#     heights.append(heights[0])
#     return time_range(end, count), heights[offset:] + heights[1 : offset + 1]


# def horizontal(end, reverse):
#     horizontal_angle = 25
#     angle = horizontal_angle if reverse else -horizontal_angle
#     return time_range(end, 4), [0, angle, 0, -angle, 0]


# animation = Animation(hexapod)

# leg_group = ("left_front", "right_middle", "left_back")

# for name in Base.base_hinges.keys():
#     times, values = horizontal(4, "middle" in name)
#     animation.add_track(f"/base/{name}_leg", "rz", times, values)

#     times, values = vertical(8, 4, 0 if name in leg_group else 4)
#     animation.add_track(f"/base/{name}_leg/lower_leg", "rz", times, values)
