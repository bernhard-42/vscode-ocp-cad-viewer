# %%
from build123d import *
import cadquery as cq
from ocp_vscode import *


# %% CadQuery

s = cq.Sketch().trapezoid(4, 3, 90).vertices().circle(0.5, mode="s").reset()
select_vertices(s, [1, 2, 6, 5])

show(s.fillet(0.25).reset().rarray(0.6, 1, 5, 1).slot(1.5, 0.4, mode="s", angle=90))

# %%
b = cq.Workplane().box(1, 2, 3).cut(cq.Workplane().box(0.2, 4, 4))
b2 = select_edges(b, [6, 7, 21, 14]).fillet(0.1)
b3 = select_edges(b2, [2, 12, 30, 23]).fillet(0.15)

show(b3)
# %%

show(select_faces(b, [8, 9, 0, 2, 4, 7]))

# %%

show(select_vertices(b, [2, 14, 5, 11, 9, 1, 7, 12]), show_parent=True)

# %% Build123d

ccm = (Align.CENTER, Align.CENTER, Align.MIN)

b = Box(1, 1, 1)
b -= Cylinder(0.3, 0.5, align=ccm)
b -= Cylinder(0.4, 0.3, align=ccm)
b -= Box(0.3, 1.1, 0.5, align=ccm)

show(b)
# %%

b = fillet(select_edges(b, [38, 40, 35, 37, 28, 26, 44, 42]), 0.05)

show(b)
# %%

b = fillet(select_edges(b, [3, 54]), 0.02)

show(b)
# %%

b = fillet(select_edges(b, [56, 52]), 0.01)

show(b)
# %%

r = RegularPolygon(3, 8)
show(r)

# %%

r2 = fillet(select_vertices(r, [3, 1, 7, 5]), 1)
show(r2)
# %%
