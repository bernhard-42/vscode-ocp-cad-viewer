# %%
import cadquery as cq
from ocp_vscode import *


set_defaults(
    axes=True,
    transparent=False,
    collapse=Collapse.LEAVES,
    grid=(True, True, True),
    debug=False,
)

custom_location = {
    "position": [-2.5908059247662116, -3.667785685492257, 7.431493897473118],
    "quaternion": [
        0.2205651922144861,
        -0.17024325654880137,
        -0.04619851746028533,
        0.9592882395648944,
    ],
    "target": [0.41813185496285243, -0.134788104086441, 0.10662901649379282],
    "zoom": 0.7551316225623868,
}

# %%
box = cq.Workplane().box(1, 2, 1).edges().chamfer(0.4)

reset_show()
show_object(box, name="Box", options={"alpha": 0.5}, **custom_location)

# %%
sphere = cq.Workplane().sphere(0.6)

show_object(
    sphere,
    # show_object args
    "sphere",
    {"color": (10, 100, 110)},
)

# %%
show_object(
    box,
    # Clear stack of objects
    clear=True,
    center_grid=True,
    grid=(True, False, False),
)

# %%
reset_defaults()

set_viewer_config(reset_camera=Camera.RESET)
# %%
