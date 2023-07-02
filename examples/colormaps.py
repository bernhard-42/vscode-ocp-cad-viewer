# %%

import copy
from build123d import *
from ocp_vscode import (
    show,
    ColorMap,
    set_colormap,
    unset_colormap,
    reset_show,
    show_object,
)
from ocp_vscode.colors import (
    hsv_mapper,
    matplotlib_mapper,
    ListedColorMap,
    SegmentedColorMap,
    SeededColormap,
    GoldenRatioColormap,
)
import matplotlib as mpl


def reference(obj, loc):
    return copy.copy(obj).move(loc)


sphere = Sphere(1)
spheres = [reference(sphere, loc) for loc in GridLocations(1, 2, 1, 20)]


# %%
show(*spheres, colors=ColorMap.tab20(alpha=0.8))
# %%
show(*spheres, colors=ColorMap.tab20(reverse=True))
# %%
show(*spheres, colors=ColorMap.segmented(20, "mpl:Greens", alpha=0.8))
# %%
show(*spheres, colors=ColorMap.segmented(10, "mpl:Greens", alpha=0.8))
# %%
show(*spheres, colors=ColorMap.golden_ratio("mpl:Greens", alpha=0.8))
# %%
show(*spheres, colors=ColorMap.golden_ratio("mpl:Greens", reverse=True))
# %%
show(*spheres, colors=ColorMap.segmented(10, "mpl:summer", reverse=True))
# %%
show(*spheres, colors=ColorMap.seeded(42, "mpl:summer"))
# %%
show(*spheres, colors=ColorMap.seeded(4242, "mpl:summer"))
# %%
show(*spheres, colors=ColorMap.segmented(20, "hsv", reverse=False))
# %%
show(*spheres, colors=ColorMap.segmented(10, "hsv", reverse=False))
# %%
show(*spheres, colors=ColorMap.golden_ratio("hsv", alpha=0.8))
# %%
show(*spheres, colors=ColorMap.seeded(42, "hsv"))
# %%
show(
    *spheres,
    colors=ColorMap.seeded(59798267586177, "rgb", lower=10, upper=100, brightness=2.2)
)
# %%

set_colormap(ColorMap.golden_ratio("mpl:Blues", alpha=0.8))
show(*spheres)
# %%
show(*spheres[:10])
# %%
set_colormap(ColorMap.tab20(alpha=0.8))
show(*spheres)
# %%
set_colormap(ColorMap.seeded(42, "hsv", alpha=0.8))
show(*spheres)
# %%
set_colormap(ColorMap.segmented(20, "hsv"))
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

# %%

set_colormap(ListedColorMap(["red", "green", "blue"]))
show(*spheres, colors=[None, "yellow"])
# %%

boxes = [loc * Box(1, 1, 1) for loc in [Pos(2 * i, 0, 0) for i in range(20)]]

colors = ColorMap.listed(20, "mpl:turbo", reverse=False)
show(*boxes, colors=colors)

# %%

colors = ColorMap.listed(colors=["red", "green", "blue"])
show(*boxes, colors=colors)

# %%

sphere = Sphere(1)
show(*spheres, colors=ColorMap.segmented(20, "mpl:hot"))

# %%
