# %%
import cadquery as cq
from ocp_vscode import *

set_defaults(
    axes=True,
    transparent=False,
    collapse=Collapse.LEAVES,
    reset_camera=Camera.KEEP,
    grid=(True, True, True),
)
# %%
box = cq.Workplane().box(1, 2, 1).edges().chamfer(0.4)

reset_show()
show_object(box, name="Box", options={"alpha": 0.5}, measure_tools=True)

# %%
sphere = cq.Workplane().sphere(0.6)

show_object(
    sphere,
    # show_object args
    "sphere",
    {"color": (10, 100, 110)},
    # three-cad-viewer args
    ortho=False,
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
