import time
from build123d import *
from ocp_vscode import *


class Finder:
    def __init__(self, obj, colormap=CM.tab20()):
        self.obj = obj
        self.colormap = colormap

    def _axis_str(self, axis):
        axis_str = f"Axis({axis.position.to_tuple()}, {axis.direction.to_tuple()})"
        if axis.position.length == 0:
            if axis.direction == Axis.X.direction:
                axis_str = "Axis.X"
            elif axis.direction == Axis.Y.direction:
                axis_str = "Axis.Y"
            elif axis.direction == Axis.Z.direction:
                axis_str = "Axis.Z"
        return axis_str

    def find_face(self, axis=Axis.Z, group=False, var="obj", code=True):
        self.colormap.reset()
        faces = self.obj.faces().sort_by(axis)
        show(
            *faces,
            names=[str(i) for i in range(len(faces))],
            colors=self.colormap,
            show_parent=True,
        )
        _ = input("Press key when you have selected an edge")
        pick = status()["lastPick"]
        ind = int(pick["name"])
        face = faces[ind : ind + 1]

        if group:
            raise NotImplementedError()
        else:
            axis_str = self._axis_str(axis)
            if code:
                # show(face, show_parent=True)
                return f"\n{var}.faces().sort_by({axis_str})[{ind}]"
            else:
                return face

    def find_face_group(self, axis=Axis.Z, var="obj", code=True):
        self.colormap.reset()
        pick = status()["lastPick"]
        axis_str = self._axis_str(axis)

        faces = self.obj.faces().group_by(axis)
        show(
            *faces,
            names=[str(i) for i in range(len(faces))],
            colors=self.colormap,
            default_opacity=0.9,
            progress="",
            collapse=Collapse.ALL,
            show_parent=False,
        )
        while True:
            try:
                time.sleep(0.5)
                new_pick = status()["lastPick"]
                if pick["name"] != new_pick["name"]:
                    ind = int(new_pick["name"])
                    print(f"\n{var}.faces().group_by({axis_str})[{ind}]")
                    pick = new_pick
            except KeyboardInterrupt:
                print("Loop interrupted by user")
                break

    def find_faces_for_edge(self, axis=Axis.Z):
        edges = self.obj.edges().sort_by(axis)
        show(
            *edges,
            names=[str(i) for i in range(len(edges))],
            colors=self.colormap,
            show_parent=True,
        )
        _ = input("Press key when you have selected an edge")
        pick = status()["lastPick"]
        edge = edges[int(pick["name"])]
        faces = self.obj.faces()
        result = []
        for face in faces:
            if edge in face.edges():
                result.append(face)
        show(*result, edge)
        return edge, result


# %%
if __name__ == "__main__":
    a = 55 / 2
    c100 = Circle(100).edges()[0]
    c85 = Circle(85).edges()[0]

    lines = []
    vertices = []
    for sign in (1, -1):
        c = Vector(sign * 31, 0)
        l = PolarLine(c, sign * 6, sign * a)
        l2 = PolarLine(l @ 1, 100, sign * a - 90)
        vertices.append(c100.intersections(Plane.XY, l2.edges()[0])[1])
        lines.append(l2)

    wire = Wire.make_wire(
        [
            Line(lines[0] @ 0, vertices[0]),
            ThreePointArc(vertices[0], Vector(0, -100), vertices[1]),
            Line(vertices[1], lines[1] @ 0),
            Line(lines[1] @ 0, lines[0] @ 0),
        ]
    )
    face = make_face(wire)
    face = fillet(face.vertices().group_by(Axis.Y)[0], 15)

    circles = face.edges().filter_by(GeomType.CIRCLE)
    centers = [circles[0].arc_center, Vector(0, -85), circles[2].arc_center]

    disk = Circle(31)
    for loc in PolarLocations(31, 6):
        disk += loc * Circle(6)

    trip_mount = extrude(disk, 16 / 2, both=True)
    trip_mount = fillet(trip_mount.edges().filter_by(Axis.Z), 8)

    trip_mount += extrude(face, 7 / 2, both=True)
    for center in centers:
        trip_mount += extrude(Pos(*center) * (Circle(15)), 32 / 2, both=True)
        trip_mount -= extrude(Pos(*center) * (Circle(10)), 32 / 2, both=True)

    for loc in PolarLocations(31, 6):
        trip_mount -= loc * Hole(3, depth=32)
    trip_mount -= Hole(20, depth=16)

    f = Finder(trip_mount)
    f.find_face_group(Axis.Z)
