# %%

from ocp_vscode import *
import cadquery as cq


def state(*attr):
    s = combined_config()
    s2 = status()
    for key in ["position", "quaternion", "target", "zoom"]:
        s[key] = s2[key]

    for a in attr:
        print(f"{a} = {s.get(a)}")


def check(conf):
    def _eq(x, y):
        if isinstance(x, float) or isinstance(y, float):
            return abs(x - y) < 1e-2
        else:
            return x == y

    def equal(a, b):
        if isinstance(a, (list, tuple)):
            return len(a) == len(b) and all([_eq(a[i], b[i]) for i in range(len(a))])
        else:
            return _eq(a, b)

    s = combined_config()
    s2 = status()
    for key in ["position", "quaternion", "target", "zoom"]:
        s[key] = s2[key]

    error = False
    for k, v in conf.items():
        if not equal(s[k], v):
            print(f"ERROR: {k} is not {v}, but {s[k]}")
            error = True
    if not error:
        print("OK")


set_defaults(reset_camera=Camera.KEEP)

# %%

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
    .add(box1, name="red box", color="#d7191c80")  # transparent alpha = 0x80/0xFF
    .add(box3, name="green box", color="#abdda4")
    .add(box4, name="blue box", color=(43, 131, 186, 0.3))  # transparent, alpha = 0.3
)

show(a1, debug=True, reset_camera=Camera.RESET)


# %%

state("axes", "axes0", "grid", "center_grid")

# %%

c = dict(
    axes=True,
    axes0=True,
    grid=(True, False, False),
    center_grid=True,
)

set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

reset_defaults()

# %%

check(dict(axes=False, axes0=True, grid=(False, False, False), center_grid=False))

# %%

state("axes", "axes0", "grid", "center_grid")

# %%

c = dict(grid=(True, True, False))
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

state("transparent", "black_edges")

# %%
c = dict(transparent=True, black_edges=True)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

state("default_opacity")

# %%

c = dict(default_opacity=0.1)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

c = dict(default_opacity=0.9)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

state("ortho")

# %%
c = dict(ortho=False)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)


# %%

c = dict(ortho=True)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

state("explode")

# %%
c = dict(explode=True)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

state("explode")

# %%
c = dict(explode=False)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

state("position", "quaternion", "target", "zoom")

# %%

c = dict(
    zoom=0.5,
    position=(-82.8758620758301, -90.1348297727537, 50.05278713951289),
    quaternion=(
        0.5260854883489195,
        -0.20303675503687996,
        -0.27189350671238977,
        0.7797974455333987,
    ),
    target=(0, 7.5, 0),
)
set_viewer_config(**c)

# %%
state(*c.keys())
check(c)

# %%

reset_defaults()

# %%

state("default_edgecolor", "default_opacity", "transparent")

# %%

c = dict(default_edgecolor="#008000", default_opacity=0.1, transparent=True)
set_viewer_config(**c)


# %%

state(*c.keys())
check(c)

# %%

reset_defaults()

# %%

state("default_edgecolor", "default_opacity", "transparent")

# %%

check(dict(default_edgecolor="#707070", default_opacity=0.5, transparent=False))

# %%

set_viewer_config(tab="material")

# %%

state("ambient_intensity", "direct_intensity", "metalness", "roughness")

# %%

c = dict(ambient_intensity=1.85, direct_intensity=1.67, metalness=0.9, roughness=0.6)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%
set_viewer_config(
    ambient_intensity=1, direct_intensity=1.1, metalness=0.3, roughness=0.65, tab="tree"
)
# %%
state("zoom_speed", "pan_speed", "rotate_speed")

# %%

c = dict(zoom_speed=0.1, pan_speed=0.1, rotate_speed=0.1)
set_viewer_config(**c)

# %%
set_viewer_config(zoom_speed=1, pan_speed=1, rotate_speed=1)

# %%

state(*c.keys())
check(c)

# %%

state("glass", "tools")

# %%

c = dict(glass=False, tools=True)

set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

c = dict(glass=True, tools=True)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

c = dict(tools=False)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

c = dict(tools=True, glass=True)

set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

set_viewer_config(tab="tree")

# %%

state("collapse")

# %%

c = dict(collapse=Collapse.ALL)

set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

c = dict(collapse=Collapse.NONE)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%

show(a1, debug=True)

# %%

set_viewer_config(tab="clip")

# %%

state(
    "clip_slider_0",
    "clip_slider_1",
    "clip_slider_2",
    "clip_intersection",
    "clip_planes",
    "clip_object_colors",
)

# %%

c = dict(
    clip_slider_0=2,
    clip_slider_1=-7,
    clip_slider_2=7,
    clip_intersection=True,
    clip_planes=True,
    clip_object_colors=True,
)
set_viewer_config(**c)

# %%

state(*c.keys())
check(c)


# %%

show(a1, debug=True)

# %%

set_viewer_config(tab="clip")

# %%

(
    state(
        "clip_slider_0",
        "clip_slider_1",
        "clip_slider_2",
        "clip_normal_0",
        "clip_normal_1",
        "clip_normal_2",
        "clip_intersection",
        "clip_planes",
        "clip_object_colors",
    ),
    ("clip_normal_0", "clip_normal_1", "clip_normal_2"),
)

# %%

c = dict(
    clip_slider_0=9.7,
    clip_slider_1=11.3,
    clip_slider_2=5.3,
    clip_normal_0=(-0.58, 0.58, -0.58),
    clip_normal_1=(0.16, -0.48, -0.87),
    clip_normal_2=(-0.56, 0.47, 0.68),
    clip_intersection=False,
    clip_planes=True,
    clip_object_colors=False,
)

set_viewer_config(**c)

# %%

state(*c.keys())
check(c)

# %%
