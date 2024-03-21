# %%
from build123d import *
from ocp_vscode import *

set_defaults(reset_camera=Camera.KEEP, clip_planes=True, clip_object_colors=True)

# %%

show(Sphere(0.5))
set_viewer_config(tab="clip")
# %%

p2 = Box(1, 1, 1)

show(
    p2,
    debug=True,
    clip_intersection=False,
    clip_planes=True,
    clip_object_colors=False,
    clip_slider_0=0.1,
    clip_slider_1=0.15,
    clip_slider_2=0.2,
    clip_normal_1=(0.12, -0.36, -0.92),
    clip_normal_2=(-0.58, 0.58, -0.58),
)
set_viewer_config(tab="clip")

# %%

show(Sphere(0.5))
set_viewer_config(tab="clip")

# %%

show(Sphere(0.5))
set_viewer_config(tab="clip", clip_object_colors=True)

# %%
show(Sphere(0.5), reset_camera=True)
set_viewer_config(tab="clip")

# %%

show(
    Box(1, 2, 3, align=(Align.MIN, Align.MIN, Align.MIN)),
    center_grid=True,
    grid=(True, False, False),
)
# %%
set_defaults(show_parent=True, reset_camera=Camera.RESET)
show(Box(1, 2, 3).vertices())
# %%
with BuildPart() as p:
    Box(0.1, 0.1, 2)

a = {
    "a": Vector(1, 2, 3),
    "b": [
        Pos(2, 2, 2) * Cylinder(1, 1),
        (1, 2, 3),
        p,
        p.part,
        {"c": Vector(5, 2, 3), "d": Pos(-3, 0, 0) * Box(1, 2, 3), "e": 123},
    ],
}
x = 0
b = [
    Pos(2, 4, 2) * Sphere(1),
    "wert",
    p,
    p.part,
    {"x": Pos(-5, -5, 0) * Box(2, 1, 0.5), "y": 123},
]
show_all()
# %%
