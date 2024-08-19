# %%
from build123d import *
from ocp_vscode import show, set_port
from ocp_vscode.show import _convert
import json
import orjson
from ocp_vscode.comms import default

# %%

# %%
a, b, thickness, distance, fontsize, depth = 13.6, 8.0, 1.0, 0.3, 20, 2

pts = ((-a, 0), (0, b), (a, 0))

o = Text("O", fontsize, "Futura")
cp = Text("CP", fontsize, "Futura")

l1 = ThreePointArc(*pts)
l1 += ThreePointArc(*(l1 @ 1, (0, -b), l1 @ 0))

l2 = offset([l1], thickness)
l3 = offset([l1], thickness + distance)
l4 = offset([l1], -distance)

eye_face = make_face(l2) - make_face(l1)
eye = extrude(eye_face, -2)

eye_mask_face = make_face(l3) - make_face(l4)
eye_mask = extrude(eye_mask_face, -2)

logo_o = extrude(o, -depth)
logo_cp = Pos(22.5, 0, 0) * extrude(cp, -depth)
logo = logo_o + (logo_cp - eye_mask)

center_wire = Wire.make_wire(logo_o.faces().sort_by(Axis.Z).first.edges()[16:])
center = extrude(make_face(center_wire), 2)

eye = eye + center

logo = Plane.XZ * Pos(0, -20, 0) * logo
eye = Plane.XZ * Pos(0, -20, 0) * eye
# %%
# show(
#     logo,
#     eye,
#     colors=[(85, 160, 227), (51,51,51)],
#     names=["OCP", "Eye"],
#     grid=(True, False, False),
#     ortho=False,
#     axes0=True,
#     zoom=0.8,
#     position=[92.4, -99.3, -6.6],
#     quaternion=[0.6047, 0.2156, 0.2603, 0.7212],
# )

c = _convert(
    logo,
    eye,
    colors=[(85, 160, 227), "#333"],
    names=["OCP", "Eye"],
    grid=(True, False, False),
    ortho=False,
    axes0=True,
    zoom=0.8,
    position=[92.4, -99.3, -6.6],
    quaternion=[0.6047, 0.2156, 0.2603, 0.7212],
)

# %%
with open("logo.txt", "w") as fp:
    fp.write(json.dumps(c[0], separators=(",", ":")))

# %%
with open("mapping.txt", "w") as fp:
    fp.write(orjson.dumps(c[1], default=default).decode("utf-8"))
