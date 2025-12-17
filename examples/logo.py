# %%
import json

import orjson
from bd_ext import clean_text_overlaps
from build123d import *

from ocp_vscode import *
from ocp_vscode.comms import default
from ocp_vscode.show import _convert

# %%

text = clean_text_overlaps(
    Text(
        "OCP",
        20,
        font="Montserrat",
        font_path="/Users/bernhard/Downloads/Montserrat/static/Montserrat-ExtraBold.ttf",
    )
)
ocp = extrude(text, 2)
ocp.color = "#55a0e3"
show(ocp)

# %%
o_edges = ocp.edges().group_by(Axis.Z)[-1].sort_by_distance((-15, 0, 2))[0:16]
center_face = make_face(o_edges)
center = extrude(center_face, -2)
center.color = "#333333"

show(ocp, center)
# %%

center_center = center_face.face().center_location.position
c_x = center_center.X
c_y = center_center.Y

a = 13.6
b = 7.30
thickness = 1.0
distance = 0.3
fontsize = 20
depth = 2

pts = ((-a + c_x, 0), (c_x, b), (a + c_x, 0))
l1 = ThreePointArc(*pts)
l1 += mirror(l1, Plane.XZ)
l1 = Pos(0, c_y) * l1

l2 = offset([l1], thickness)
l3 = offset([l1], thickness + distance)
l4 = offset([l1], -distance)

eye_face = make_face(l2) - make_face(l1)
eye = extrude(eye_face, 2)

eye_mask_face = make_face(l3) - make_face(l4)
eye_mask = extrude(eye_mask_face, 2) & Box(10, 20, 4)


eye += center
eye.color = "#333333"

logo = ocp - eye_mask
show(eye, logo)

# %%

logo_top = Pos(0, 0, -depth) * Compound(logo.faces().group_by()[-1])
logo_top.color = logo.color

eye_top = Pos(0, 0, -depth) * Compound(eye.faces().group_by()[-1])
eye_top.color = eye.color

# %%
logo = Pos(0, 0, 15) * Rot(90, 0, 0) * logo
eye = Pos(0, 0, 15) * Rot(90, 0, 0) * eye

show(eye, logo)


# %%
position = [97.60, -89.83, 30.85]
quaternion = [0.6, 0.27, 0.31, 0.69]
target = [-3.5, -1, 12.83]

show(
    logo,
    eye,
    colors=[(85, 160, 227), (51, 51, 51)],
    names=["OCP", "Eye"],
    center_grid=True,
    grid=(True, False, False),
    ortho=False,
    axes0=True,
    zoom=1,
    position=position,
    quaternion=quaternion,
    target=target,
)
# %%
c = _convert(
    logo,
    eye,
    colors=[(85, 160, 227), "#333"],
    names=["OCP", "Eye"],
    grid=(True, False, False),
    center_grid=True,
    ortho=False,
    axes0=True,
    zoom=0.8,
    position=position,
    quaternion=quaternion,
    target=target,
)

# %%
with open("logo.json", "w") as fp:
    fp.write(json.dumps(c[0], separators=(",", ":")))

# %%
with open("mapping.json", "w") as fp:
    fp.write(orjson.dumps(c[1], default=default).decode("utf-8"))

# %%
max_x = logo_top.bounding_box().max.X
min_x = eye_top.bounding_box().min.X
r = 1.1 * (max_x - min_x) / 2
c = (max_x + min_x) / 2
circle = Pos(c, 0, 0) * Ellipse(r, r * 0.7)
circle -= logo_top
circle -= eye_top
circle.color = "#dddddd"
show(logo_top, eye_top, circle, reset_camera=Camera.TOP)

s = ExportSVG(margin=2)
s.add_layer("black", fill_color=eye.color, line_weight=0)
s.add_shape(eye_top, layer="black")

s.add_layer("blue", fill_color=logo.color, line_weight=0)
s.add_shape(logo_top, layer="blue")

s.add_layer("gray", fill_color=circle.color, line_weight=0)
s.add_shape(circle, "gray")
s.write("ocp-logo.svg")
