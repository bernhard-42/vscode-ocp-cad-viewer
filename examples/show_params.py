# %%

from ocp_vscode import *
from build123d import Box, Pos, fillet, Location
import cadquery as cq

b = Pos(0, 0, -2) * Box(1, 1, 3)
c = cq.Workplane().cylinder(1, 1.5)

# %%

show(
    b,
    c,
    names=["b", "c"],
    colors=["red", "green"],
    alphas=[1.0, 0.5],
)


# %%

show(b, c, Box(0.1, 0.1, 4), progress="+")

# %%

show(b, c, Box(0.1, 0.1, 4), progress="+")

# %%

show(b, c, glass=False, tools=True)


# %%

show(b, c, glass=True, tools=True)

# %%

show(b, c, glass=False, tools=False)

# %%

show(
    b,
    c,
    axes=True,
    axes0=True,
    grid=(True, False, False),
    center_grid=True,
    grid_font_size=10,
    ortho=False,
    transparent=True,
    default_opacity=0.1,
    black_edges=True,
    ticks=20,
)

# %%

show(
    b,
    c,
    axes=True,
    axes0=False,
    grid=(False, True, False),
    center_grid=False,
    grid_font_size=12,
    ortho=True,
    transparent=True,
    default_opacity=0.9,
    black_edges=False,
    ticks=5,
)

# %%

show(
    b,
    c,
    axes=False,
    axes0=False,
    grid=(False, False, False),
    center_grid=True,
    ortho=True,
    transparent=False,
)

# %%

show(b, c, orbit_control=True)


# %%

d = {"all": {"build123d": b, "cadquery": c}}
show(d, collapse=Collapse.NONE)

# %%

show(d, collapse=Collapse.ALL)

# %%

show(b, c, explode=True)

# %%

show(b, c, up="Y", explode=False)

# %%

show(b, c)

# %%

show(
    b,
    c,
    zoom=0.34,
    position=(13.80583141533952, -0.09020534783580703, 6.79732744339162),
    quaternion=(
        0.1311486932382242,
        0.2605863687579187,
        0.3748557574870151,
        0.8799874577278385,
    ),
    target=(5.686972047559481, 0.42661828895286746, -5.298829627954091),
)

# %%

show(
    b,
    c,
    reset_camera=Camera.KEEP,
)

# %%

show(
    b,
    c,
    reset_camera=Camera.CENTER,
)

# %%

show(
    b,
    c,
    reset_camera=Camera.RESET,
)

# %%

show(
    b,
    c,
    position=(13.781132164127966, 2.9053781147768625, 2.260209340583971),
    quaternion=(
        0.29852536103313115,
        0.5309505555794043,
        0.5229306160107792,
        0.5962530395633631,
    ),
    target=(0.0, 0.0, -1.5),
    clip_slider_0=-0.21,
    clip_slider_1=-0.14,
    clip_slider_2=0.33,
    clip_intersection=True,
    clip_planes=True,
    clip_object_colors=True,
)

# %%

set_viewer_config(tab="clip")

# %%

show(
    b,
    c,
    position=(2.86931361687369, 11.762871678108427, 6.617997859840651),
    quaternion=(
        0.15019060411404805,
        0.4460916419362074,
        0.8790721456277766,
        -0.07534714468306618,
    ),
    target=(0.0, 0.0, -1.5),
    clip_slider_0=1.28,
    clip_slider_1=1.42,
    clip_slider_2=1.66,
    clip_normal_0=(-0.94, 0.04, -0.33),
    clip_normal_1=(-0.20, -0.42, -0.88),
    clip_normal_2=(0.48, -0.17, -0.86),
    clip_intersection=False,
    clip_planes=True,
    clip_object_colors=False,
)

# %%

set_viewer_config(tab="clip")

# %%

show(b, c, pan_speed=0.1, rotate_speed=0.1, zoom_speed=0.1)

# %%

show(b, c, pan_speed=1, rotate_speed=1, zoom_speed=1)

# %%

show(
    c.edges(),
    edge_accuracy=0.1,
)

# %%

b2 = fillet(b.edges(), 0.2)
show(
    b2,
    deviation=1,
    angular_tolerance=3,
)

# %%

show(
    b,
    b.edges(),
    c.faces(),
    b.vertices(),
    default_color="red",
    default_edgecolor="yellow",
    default_facecolor="green",
    default_thickedgecolor="blue",
    default_vertexcolor="magenta",
)

# %%

show(
    b,
    c,
    ambient_intensity=1.50,
    direct_intensity=2.70,
    metalness=0.75,
    roughness=0.70,
)

# %%

show(b, render_edges=False)

# %%

show(b, c, render_normals=True)


# %%

show(b, b.faces().sort_by()[-1].center_location, helper_scale=2)

# %%

show(b.edges().group_by()[-1], show_parent=True)

# %%

show(b, c, timeit=True)

# %%
