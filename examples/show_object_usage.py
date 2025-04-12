# %%

from ocp_vscode import *
import cadquery as cq
from build123d import *


set_defaults(show_parent=False)

# %%

box = cq.Workplane().box(1, 2, 3).edges().chamfer(0.1)

# %%

show_object(
    box.faces(">X"), name="green", options={"color": "green", "alpha": 0.2}, clear=True
)
show_object(box.faces("<Y"), name="red", options={"color": "red", "alpha": 0.6})
show_object(box.faces(">Z"), name="blue", options={"color": "blue"})
show_object(box.faces(">>Z[-2]"), name="default", options={"alpha": 0.5}, axes=True)

# %%

show_object(box.wires(">X"), name="green", options={"color": "green"}, clear=True)
show_object(box.wires("<Y"), name="red", options={"color": "red"})
show_object(
    box.wires(">Z"), name="blue", options={"color": "blue"}, grid=(True, False, False)
)

# %%

show_object(box.edges("<X"), name="green", options={"color": "green"}, clear=True)
show_object(box.edges(">Y"), name="red", options={"color": "red"})
show_object(box.edges("<Z"), name="blue", options={"color": "blue"}, center_grid=True)

# %%

show_object(box.vertices("<X"), name="green", options={"color": "green"}, clear=True)
show_object(box.vertices(">Y"), name="red", options={"color": "red"})
show_object(box.vertices("<Z"), name="blue", options={"color": "blue"})

# %%

show_object(box, name="green", options={"color": "green", "alpha": 0.2}, clear=True)
show_object(box.translate((0, -4, 0)), name="red", options={"color": (255, 0, 0, 0.6)})
show_object(box.translate((0, 4, 0)), name="blue", options={"color": "blue"})
show_object(box.translate((4, 0, 0)), name="default", options={"alpha": 0.5})

# %%

with BuildSketch() as s:
    Circle(2)

show_object(s, name="sketch1", options={"color": "green", "alpha": 0.2}, clear=True)
show_object(
    s.sketch.moved(Location(Vector(0, 0, -1))),
    name="sketch2",
    options={"color": "red", "alpha": 0.6},
)
show_object(
    s.sketch.moved(Location(Vector(0, 0, -2))).wrapped,
    name="sketch3",
    options={"color": "blue"},
)

# %%

show_object(
    box.val(), name="green", options={"color": "green", "alpha": 0.2}, clear=True
)
show_object(
    box.translate((0, -4, 0)).val().wrapped,
    name="red",
    options={"color": (255, 0, 0, 0.6)},
)

# %%

with BuildPart() as b:
    Box(1, 1, 2)
    with Locations((0, 2, 0)):
        Box(2, 2, 1)

show_object(
    b.solids()[0], name="green", options={"color": "green", "alpha": 0.7}, clear=True
)
show_object(b.solids()[1], name="default", options={"alpha": 0.3})

# %%


# %%
