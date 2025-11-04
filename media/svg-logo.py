# %%
from build123d import *
from ocp_vscode import *

from ocpsvg import face_to_svg_path, format_svg_path

set_defaults(reset_camera=Camera.KEEP)

# %%

logo_color = "#55a0e3"
eye_color = "#000"
background_color = "#f4f4f4"

a, b, thickness, distance, fontsize, depth = 13.6, 8.0, 1.6, 0.3, 20, 2

pts = ((-a, 0), (0, b), (a, 0))

o = Text("O", fontsize, "Futura")
cp = Text("CP", fontsize, "Futura")

l1 = ThreePointArc(*pts)
l1 += ThreePointArc(*(l1 @ 1, (0, -b), l1 @ 0))

l2 = offset([l1], thickness)
l3 = offset([l1], thickness + distance)
l4 = offset([l1], -distance)

eye_face = make_face(l2) - make_face(l1)
eye = Pos(0, 0.05, 0) * extrude(eye_face, -2)
eye.color = eye_color

eye_mask_face = make_face(l3) - make_face(l4)
eye_mask = extrude(eye_mask_face, -2)

logo_o = extrude(o, -depth)
logo_cp = Pos(22.5, 0, 0) * extrude(cp, -depth)
logo = logo_o + (logo_cp - eye_mask)
logo.color = logo_color

show(eye, logo)

# %%

center_wire = Wire(logo_o.faces().sort_by(Axis.Z).first.edges()[16:])
center = extrude(make_face(center_wire), 2)

eye = eye + center

eye = mirror(eye, Plane.XZ)
logo = mirror(logo, Plane.XZ)

show(eye, logo)

# %%

f_eye = eye.faces().group_by(Axis.Z)[-1]
f_eye.color = eye_color


f_logo = logo.faces().group_by(Axis.Z)[-1]
f_logo.color = logo_color

bb = f_eye[0].bounding_box()
bb = bb.add(f_eye[1].bounding_box())
for face in f_logo:
    bb = bb.add(face.bounding_box())


# background = Pos(bb.center()) * Circle((bb.max.X - bb.min.X) / 2 + 2)
delta_x = 4
delta_y = 8
w = bb.max.X - bb.min.X + 2 * delta_x
h = bb.max.Y - bb.min.Y + 2 * delta_y
background = Pos(w / 2 - delta_x + bb.min.X + 1, 0, 0) * RectangleRounded(w, h, 10)
background = Pos(w / 2 - delta_x + bb.min.X + 1, 0, 0) * Ellipse(w / 2, h / 2)
background.color = background_color

show(background, f_eye, f_logo)

b_bb = background.bounding_box()

# %%

with open("logo.svg", "w") as fd:
    fd.write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{b_bb.min.X} {b_bb.min.Y} {w} {h}" width="512" height="{512 * h / w}" fill="none" stroke="none">\n'
    )

    path = format_svg_path(face_to_svg_path(background.face().wrapped, tolerance=1e-5))
    fd.write(f'    <path d="{path}" fill="{background_color}"/>\n')

    for face in f_eye:
        path = format_svg_path(face_to_svg_path(face.wrapped, tolerance=1e-5))
        fd.write(f'    <path d="{path}" fill="{eye_color}"/>\n')

    for face in f_logo:
        path = format_svg_path(face_to_svg_path(face.wrapped, tolerance=1e-5))
        fd.write(f'    <path d="{path}" fill="{logo_color}"/>\n')

    fd.write("</svg>\n")

# %%
