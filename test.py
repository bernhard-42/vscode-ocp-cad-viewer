# %%
from build123d import *
from ocp_vscode import *

set_defaults(helper_scale=0.2)

box = Box(1, 2, 3)
box.color = "black"
cyl = Cylinder(0.3, 4)
cyl.color = "cyan"
sphere = Sphere(0.7)
sphere.color = "silver"
sphere.name = "sphere"
dbox = Box(2, 0.3, 0.3)
dbox.label = "dbox"
dbox.color = "darkgreen"
i = 42
col = (Color("green"), Color("red"))
align = (Align.CENTER, Align.CENTER)
pos = [Pos(1, 1)]
pos[0].label = "pos"
loc = GridLocations(1, 1, 5, 5)
loc.label = "gridloc"
emptyObject = Circle(1) - Circle(1)
ddict = dict(
    box=box,
    sphere=sphere,
    dbox=dbox,
    i=i,
    locs=(
        col,
        pos,
        cyl,
        loc,
    ),
    emptyObject=emptyObject,
)
# array = (box, align, i, cyl, [sphere], [dbox, i, pos, sphere, col, loc], box)
# show(
#     *array,
#     names=["box", "align", "int", "cyl", "sphere", "array"],
#     _test=False,
# )
result = show_all(_test=False)

# %%
from build123d import *
from ocp_vscode import *

from ocp_tessellate.cad_objects import ImageFace
from PIL import Image

set_defaults(reset_camera=Camera.KEEP, helper_scale=10)
set_port(3940)
# %%
cMc = (Align.CENTER, Align.MAX, Align.CENTER)

box = Pos(0, -20, 0) * Box(30, 40, 30)
from ocp_tessellate.ocp_utils import BoundingBox

sphere = Pos(0, -20, 0) * Sphere(35)
v = Vertex(0, -20, 0)
n = Vector(0, -20, 0) - Vector(-1, 1, -1).normalized() * 25
pos = Plane((0, -20, 0), z_dir=(1, -1, 1)).move(
    Pos(*(Vector(1, -1, 1).normalized() * 25))
)
f = pos * Rectangle(70, 70)
show(box, sphere, v, n, pos, f)


# %%
# image_path = "/Users/bernhard/Desktop/object-160x160mm.png"
image_path = "/Users/bernhard/Desktop/Hose-port.png"

im = Image.open(image_path)
width, height = im.size
ratio = height / width
w = 15.1
dx = 2.753
dy = -0.863


plane = ImageFace(
    image_path,
    w,
    location=Location((dx, dy, -1), (0, 0, 0)),
)
cyl = Circle(5.75 / 2)
cyl += [loc * Circle(0.5) for loc in PolarLocations(5.75 / 2, 10)]
cyl -= [loc * Circle(0.5 / 2) for loc in PolarLocations(5.75 / 2, 10)]

show(plane, cyl)

# %%
