import cadquery as cq
from ocp_vscode import (
    show,
    show_object,
    reset_show,
    set_port,
    set_defaults,
    get_defaults,
)

set_port(3939)

set_defaults(
    axes=True,
    transparent=False,
    collapse="1",
    grid=(True, True, True),
)
# %%
box = cq.Workplane().box(1, 2, 1).edges().chamfer(0.4)

reset_show()
show_object(box, name="box", options={"alpha": 0.5})

# %%
sphere = cq.Workplane().sphere(0.6)

show_object(
    sphere,
    # show_object args
    "sphere",
    {"color": (10, 100, 110)},
    # three-cad-viewer args
    collapse="1",
    reset_camera=False,
    ortho=False,
)

# %%
show_object(
    box,
    # Clear stack of objects
    clear=True,
)
