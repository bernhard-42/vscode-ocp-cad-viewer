import copy
from build123d import *
from ocp_vscode import show, CM, set_colormap, unset_colormap, reset_show, show_object

# %%
from ocp_vscode import get_defaults, set_defaults, get_default


# %%
def reference(obj, loc):
    return copy.copy(obj).move(loc)


sphere = Sphere(1)
spheres = [reference(sphere, loc) for loc in GridLocations(1, 2, 1, 20)]

# %%

set_colormap(CM.tab20, alpha=0.7)

show(*spheres)

# %%

set_colormap(CM.tab20, alpha=0.7, reverse=True)

show(*spheres)

# %%
set_colormap(
    CM.seeded, lower=10, upper=100, seed_value=59798267586177, brightness=2.2, alpha=1.0
)

show(*spheres)

# %%

show(*spheres, colors=CM.seeded(1))

# %%

show(*spheres, colors=CM.tab20(reverse=True))

# %%

show(*spheres, colors=CM.tab20(alpha=0.8))

# %%

show(*spheres, colors=CM.seeded())

# %%

show(*spheres, colors=CM.golden_ratio())

# %%

#
# Only available when Matplotlib is installed.
# These color maps need the number of color instances
#

n = 20
spheres = [reference(sphere, loc) for loc in GridLocations(1, 2, 1, n)]
show(*spheres, colors=CM.matplotlib("YlOrRd", n))

# %%
n = 20
spheres = [reference(sphere, loc) for loc in GridLocations(1, 2, 1, n)]
show(*spheres, colors=CM.matplotlib("hot", n))

# %%
n = 20
spheres = [reference(sphere, loc) for loc in GridLocations(1, 2, 1, n)]
show(*spheres, colors=CM.matplotlib("hot_r", n))

# %%
n = 20
spheres = [reference(sphere, loc) for loc in PolarLocations(12, n)]
show(*spheres, colors=CM.matplotlib("twilight", n))

# %%
n = 40
spheres = [reference(sphere, loc) for loc in PolarLocations(12, n)]
show(*spheres, colors=CM.matplotlib("hsv", n))

# %%

reset_show()
set_colormap(CM.tab20, alpha=0.6)
show(*spheres)

# %%

reset_show()

show_object(spheres[0])
show_object(spheres[1])
show_object(spheres[2])
show_object(spheres[3], options={"color": "black", "alpha": 1.0})
show_object(spheres[4])
show_object(spheres[5])
show_object(spheres[6])
show_object(spheres[7])

# %%
set_colormap(CM.golden_ratio, alpha=1)

show(*Box(1, 1, 1).faces())

# %%
show(*Box(1, 1, 1).edges())
# %%
