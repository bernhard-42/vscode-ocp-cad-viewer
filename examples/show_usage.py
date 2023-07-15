# %%
from build123d import *
from ocp_vscode import *

b = Box(1, 2, 3)
b = fillet(b.edges(), 0.2)
c = Pos(2, 2, 0) * Cylinder(0.5, 2)

#
# Use config with show for one time setting configurations
#

# %%
# Use default settings
show(b, c)

# %%
# Unset glass mode
show(b, c, glass=False)

# %%
# Remove tools
show(b, c, tools=False)

# %%
# Reset the above settings
show(b, c, tools=True, glass=True)

# %%
show(b, c, orbit_control=True)

# %%
import cadquery as cq

b1 = cq.Workplane().box(1, 2, 3)
b2 = cq.Workplane().box(1, 2, 1)
b3 = cq.Workplane().box(2, 1, 2)
a1 = cq.Assembly(name="a")
b4 = cq.Assembly(name="b")
b4.add(b2, name="b2", loc=Location((-3, -3, -3)))
b4.add(b3, name="b3", loc=Location((3, 3, 3)))
a1.add(b4)
a1.add(b1, name="b1")

show(a1, collapse=Collapse.LEAVES, debug=True)

# %%
show(a1, collapse=Collapse.ALL, debug=True)

# %%
show(a1, collapse=Collapse.ROOT, debug=True)

# %%
show(a1, collapse=Collapse.NONE, debug=True)

# %%
# Provide names to objects

show(b, c, names=["b", "c"])

# %%
# Provide colors to objects

show(b, c, colors=["red", "green"])

# %%
# Provide tranparency to objects

show(b, c, alphas=[0.9, 0.1])

# %%
# Set the progress indicator to only show instances
show(b, c, progress="-")

# %%
# Show axes at center of overall mass

show(b, c, axes=True, axes0=False)

# %%
# Show axes at (0, 0, 0)

show(b, c, axes=True, axes0=True)

# %%
# Show XY grid

show(b, c, grid=(True, True, False))

# %%
# Show XY grid with more ticks

show(b, c, grid=(True, False, True), ticks=20)

# %%
# Show object in perspective mode

show(b, c, ortho=False)

# %%
# Use Y axis as up direction

show(b, c, up="Y")

# %%
# Show all objects with transparency and default opacity level

show(b, c, transparent=True)

# %%
# Show all objects with transparency and set the opacity level

show(b, c, transparent=True, default_opacity=0.1)

# %%
show(b, c, black_edges=True)

# %%
# Change default color to cyan

show(b, c, default_color=(0, 255, 255))

# %%
# Change default color to red (css color name)

show(b, c, default_color="red")


# %%
# Set the default edge color

show(b, c, default_edgecolor="red")

# %%
# Change position and orientation of camera. Use "status()" to get actual values
show(
    b,
    c,
    zoom=0.3,
    position=[15.4, -7.4, 4.3],
    quaternion=[0.3301, 0.2803, 0.7015, 0.5658],
    target=[4.7, -7.7, -4.3],
)

# %%
# Do not reset the camera

show(b, c, reset_camera=Camera.KEEP, colors=["red", "green"], alphas=[0.3, 0.7])

# %%
show(b, c, reset_camera=Camera.CENTER, colors=["blue", "yellow"], alphas=[0.3, 0.7])

# %%
# Suppress rendering edges

show(b, c, render_edges=False)

# %%
# Render vertes normals

show(b, c, render_normals=True)

# %%
# Increase tessellation accuracy (a factor, defaulting to 0.1)

show(b, c, deviation=0.001, debug=True, timeit=True)

# %%
# Increase angular tolerance for tessellation

show(b, c, angular_tolerance=0.02, debug=True, timeit=True)

# %%
# Increase accuracy for discretizing edges

show(*b.edges(), debug=True, timeit=True)

# %%
show(*b.edges(), edge_accuracy=0.02, debug=True, timeit=True)

# %%
# Make the ambinence brighter

show(b, c, ambient_intensity=0.1)

# %%
# Make the direct lights brighter

show(b, c, direct_intensity=0.9)

# %%
# Set pan speed to very fast
show(b, c, pan_speed=10)

# %%
# Set rotate speed to very slow
show(b, c, rotate_speed=0.1)

# %%
# Set zoom speed to very fast
show(b, c, zoom_speed=10)

# %%
# Enable debug output in python nd javascript
show(b, c, debug=True)

# %%
# Time the tesselllation
show(b, c, timeit=3)

# %%

#
# Dynamically set values
#

show(b, c)

# %%
reset_defaults()

set_viewer_config(
    axes=True,
    axes0=True,
    grid=(True, True, False),
    ortho=False,
    transparent=True,
    black_edges=True,
    zoom=0.5,
    position=[2, -12, 6],
    quaternion=[0.46738, -0.02236, 0.16935, 0.86740],
    target=[0.28, -0.66, -1.90],
    default_edgecolor="red",
    default_opacity=0.2,
    zoom_speed=0.1,
    pan_speed=0.1,
    rotate_speed=0.1,
)

# %%

reset_defaults()

# %%
show(b, c)
set_viewer_config(ambient_intensity=0.1)

# %%
set_viewer_config(direct_intensity=10)

# %%

show(b, c)

# %%

set_viewer_config(tools=False)

# %%

set_viewer_config(tree_width=500, tools=True)

# %%

show(b, c)

# %%

# Dynamically set values
#

show(b, c)

# %%

reset_defaults()

set_defaults(
    axes=True,
    axes0=True,
    grid=(True, True, False),
    ortho=False,
    transparent=True,
    black_edges=False,
    zoom=0.5,
    default_edgecolor="red",
    default_opacity=0.2,
    zoom_speed=0.1,
    pan_speed=0.1,
    rotate_speed=0.1,
    glass=True,
)

# %%

show(b, c, transparent=False, timeit=True)

# %%

show(b, c, default_edgecolor="cyan", axes=False)

# %%

reset_defaults()

# %%
set_defaults(reset_camera=Camera.KEEP, timeit=True)

show(b, c)
transparent = False

# %%
transparent = not transparent
show(b, c, transparent=transparent)

# %%

reset_defaults()
show(b, c)
# %%
