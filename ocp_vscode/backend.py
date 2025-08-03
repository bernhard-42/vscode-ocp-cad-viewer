"""Python backend for the OCP Viewer"""

#
# Copyright 2025 Bernhard Walter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import base64
import sys
import traceback
from dataclasses import asdict, dataclass, fields
import os
from math import pi

from ocp_tessellate.ocp_utils import (
    area,
    axis_to_line,
    BoundingBox,
    center_of_mass,
    deserialize,
    dist_shapes,
    get_curve,
    get_plane,
    get_point,
    get_surface,
    is_closed,
    is_topods_edge,
    is_topods_face,
    is_topods_solid,
    is_topods_vertex,
    is_vector,
    length,
    make_compound,
    position_at,
    tq_to_loc,
    vertex,
    identity_location,
    downcast,
)
from ocp_tessellate.tessellator import (
    get_edges,
    get_faces,
    get_vertices,
)
from ocp_tessellate.trace import Trace

from ocp_vscode.backend_logo import logo

if os.environ.get("JUPYTER_CADQUERY") is None:
    is_jupyter_cadquery = False
    from ocp_vscode.comms import send_response
else:
    is_jupyter_cadquery = True

from ocp_vscode.comms import MessageType, listener, set_port


def print_to_stdout(*msg):
    """
    Write the given message to the stdout
    """
    print(*msg, flush=True, file=sys.stdout)


def error_handler(func):
    """Decorator for error handling"""

    def wrapper(*args, **kwargs):  # pylint: disable=redefined-outer-name
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            print_to_stdout(exc)
            traceback.print_exception(*sys.exc_info(), file=sys.stdout)

    return wrapper


@dataclass
class Tool:
    """The tools available in the viewer"""

    Distance = "DistanceMeasurement"
    Properties = "PropertiesMeasurement"
    Angle = "AngleMeasurement"


def get_shape_type(shape):
    if is_topods_vertex(shape) or is_vector(shape):
        return "Vertex"
    elif is_topods_edge(shape):
        return "Edge"
    elif is_topods_face(shape):
        return "Face"
    elif is_topods_solid:
        return "Solid"
    else:
        return "Unknown"


def get_geom_type(shape):
    if is_topods_vertex(shape) or is_vector(shape):
        return "Point"
    elif is_topods_edge(shape):
        return get_curve(shape).GetType().name.split("_")[-1]
    elif is_topods_face(shape):
        return get_surface(shape).GetType().name.split("_")[-1]
    elif is_topods_solid:
        return "Solid"
    else:
        return "Unknown"


class ViewerBackend:
    """
    Represents the backend of the viewer, it listens to the websocket and handles the events
    It's job is to send responses to the vscode extension that goes through the three cad
    viewer view.
    The responses holds all the data needed to display the measurements.
    """

    def __init__(self, port: int, jcv_id=None) -> None:
        self.port = port
        self.model = None
        self.activated_tool = None
        self.filter_type = "none"  # The current active selection filter
        self.jcv_id = jcv_id
        set_port(port)

    def start(self):
        """
        Start the backend
        """
        print("Viewer backend started")
        self.load_model(logo)
        print("Logo model loaded")
        listener(self.handle_event)()

    @error_handler
    def handle_event(self, message, event_type: MessageType):
        """
        Handle the event received from the websocket
        Dispatch the event to the appropriate handler
        """
        print(MessageType, message)
        if event_type == MessageType.DATA:
            self.load_model(message)
        elif event_type == MessageType.UPDATES:
            changes = message

            if "activeTool" in changes:
                active_tool = changes.get("activeTool")

                if active_tool != "None":
                    self.activated_tool = active_tool
                else:
                    self.activated_tool = None

            if self.activated_tool is not None:
                return self.handle_activated_tool(changes)

    def handle_activated_tool(self, changes):
        """
        Handle the activated tool, there is a special behavior for each tool
        """
        if not "selectedShapeIDs" in changes:
            return

        selected_objs = changes["selectedShapeIDs"]
        if self.activated_tool == Tool.Distance and len(selected_objs) == 3:
            shape_id1 = changes["selectedShapeIDs"][0]
            shape_id2 = changes["selectedShapeIDs"][1]
            shift = changes["selectedShapeIDs"][2]

            return self.handle_distance(shape_id1, shape_id2, shift)

        elif self.activated_tool == Tool.Properties and len(selected_objs) == 2:
            shape_id = changes["selectedShapeIDs"][0]
            return self.handle_properties(shape_id)

    def load_model(self, raw_model):
        """Read the transferred model from websocket"""

        def walk(model, trace):
            for v in model["parts"]:
                if v.get("parts") is not None:
                    walk(v, trace)
                else:
                    id_ = v["id"]
                    loc = (
                        identity_location()
                        if v["loc"] is None
                        else tq_to_loc(*v["loc"])
                    )
                    if isinstance(v["shape"], dict):
                        compound = deserialize(
                            base64.b64decode(v["shape"]["obj"].encode("utf-8"))
                        )
                    else:
                        shape = [
                            deserialize(base64.b64decode(s.encode("utf-8")))
                            for s in v["shape"]
                        ]
                        compound = make_compound(shape) if len(shape) > 1 else shape[0]
                    self.model[id_] = compound.Moved(loc)
                    faces = get_faces(compound)
                    for i, face in enumerate(faces):
                        trace.face(f"{id_}/faces/faces_{i}", face)

                        self.model[f"{id_}/faces/faces_{i}"] = downcast(face.Moved(loc))
                    edges = get_edges(compound)
                    for i, edge in enumerate(edges):
                        trace.edge(f"{id_}/edges/edges_{i}", edge)

                        self.model[f"{id_}/edges/edges_{i}"] = (
                            edge if loc is None else downcast(edge.Moved(loc))
                        )
                    vertices = get_vertices(compound)
                    for i, vertex in enumerate(vertices):
                        trace.vertex(f"{id_}/vertices/vertex_{i}", vertex)

                        self.model[f"{id_}/vertices/vertices_{i}"] = (
                            vertex if loc is None else downcast(vertex.Moved(loc))
                        )

        self.model = {}
        trace = Trace("ocp-vscode-backend.log")
        walk(raw_model, trace)
        trace.close()

    def handle_properties(self, shape_id):
        """
        Request the properties of the object with the given id
        """
        if not is_jupyter_cadquery:
            print_to_stdout(f"Identifier received '{shape_id}'")

        shape = self.model[shape_id]

        shape_type = get_shape_type(shape)
        geom_type = get_geom_type(shape)

        response = {
            "shape type": shape_type,
            "geom type": geom_type,
        }

        if shape_type == "Vertex":
            response["coords"] = list(shape)

        elif shape_type == "Edge":
            response["length"] = length(shape)

            if geom_type == "Line":
                response["start"] = get_point(position_at(shape, 0))
                response["center"] = get_point(position_at(shape, 0.5))
                response["end"] = get_point(position_at(shape, 1))

            elif geom_type == "Circle":
                circle = get_curve(shape).Circle()
                response["center"] = get_point(circle.Location())
                response["radius"] = circle.Radius()
                response["start"] = get_point(position_at(shape, 0))
                if not is_closed(shape):
                    response["geom type"] = "Arc"
                    response["end"] = get_point(position_at(shape, 1))

            elif geom_type == "Ellipse":
                ellipse = get_curve(shape).Ellipse()
                response["center"] = get_point(ellipse.Location())
                response["major radius"] = ellipse.MajorRadius()
                response["minor radius"] = ellipse.MinorRadius()
                response["focus1"] = get_point(ellipse.Focus1())
                response["focus2"] = get_point(ellipse.Focus2())
                response["start"] = get_point(position_at(shape, 0))
                if not is_closed(shape):
                    response["geom type"] = "Arc"
                    response["end"] = get_point(position_at(shape, 1))

            elif geom_type == "Hyperbola":
                hyperbola = get_curve(shape).Hyperbola()
                response["start"] = get_point(position_at(shape, 0))
                response["center"] = get_point(position_at(shape, 0.5))
                response["end"] = get_point(position_at(shape, 1))
                response["vertex"] = get_point(hyperbola.Location())
                response["focus1"] = get_point(hyperbola.Focus1())
                response["focus2"] = get_point(hyperbola.Focus2())

            elif geom_type == "Parabola":
                parabola = get_curve(shape).Parabola()
                response["start"] = get_point(position_at(shape, 0))
                response["center"] = get_point(position_at(shape, 0.5))
                response["end"] = get_point(position_at(shape, 1))
                response["vertex"] = get_point(parabola.Location())
                response["focus"] = get_point(parabola.Focus())

            elif geom_type in ["Bezier", "Bspline"]:
                response["start"] = get_point(position_at(shape, 0))
                response["center"] = get_point(position_at(shape, 0.5))
                response["end"] = get_point(position_at(shape, 1))

            elif geom_type == "Offset":
                offset = get_curve(offset_).OffsetCurve()
                response["start"] = get_point(position_at(shape, 0))
                if is_closed(shape):
                    response["end"] = get_point(position_at(shape, 1))
                response["offset"] = offset.Offset()
            else:
                response["start"] = get_point(position_at(shape, 0))
                response["middle"] = get_point(position_at(shape, 0.5))
                response["end"] = get_point(position_at(shape, 1))

        elif shape_type == "Face":
            response["area"] = area(shape)

            if geom_type == "Plane":
                plane = get_surface(shape).Plane()
                response["center"] = get_point(plane.Location())

            elif geom_type == "Cylinder":
                cylinder = get_surface(shape).Cylinder()
                response["center"] = get_point(cylinder.Location())

                response["radius"] = cylinder.Radius()
            elif geom_type == "Cone":
                cone = get_surface(shape).Cone()
                response["center"] = get_point(cone.Location())
                response["ref radius"] = cone.RefRadius()
                response["semi angle"] = cone.SemiAngle() / pi * 180

            elif geom_type == "Sphere":
                sphere = get_surface(shape).Sphere()
                response["center"] = get_point(sphere.Location())
                response["radius"] = sphere.Radius()

            elif geom_type == "Torus":
                torus = get_surface(shape).Torus()
                response["center"] = get_point(torus.Location())
                response["minor radius"] = torus.MinorRadius()
                response["major radius"] = torus.MajorRadius()

            elif geom_type in ["Bezier", "Bspline"]:
                ...

            elif geom_type == "SurfaceOfRevolution":
                revolution = get_surface(shape)
                response["axe loc"] = get_point(revolution.AxeOfRevolution().Location())
                response["axe dir"] = get_point(
                    revolution.AxeOfRevolution().Direction()
                )
                response["geom type"] = "Revolution"

        bb = BoundingBox(shape, optimal=True)
        response["bb"] = {
            "min": [bb.xmin, bb.ymin, bb.zmin],
            "center": bb.center,
            "max": [bb.xmax, bb.ymax, bb.zmax],
            "size": [bb.xsize, bb.ysize, bb.zsize],
        }
        response["type"] = "backend_response"
        response["subtype"] = "tool_response"
        response["tool_type"] = Tool.Properties

        if is_jupyter_cadquery:
            return response
        else:
            send_response(response, self.port)
            print_to_stdout(f"Data sent {response}")

    def get_center(self, shape):
        shape_type = get_shape_type(shape)
        geom_type = get_geom_type(shape)

        if shape_type == "Vertex":
            center = shape

        elif shape_type == "Edge":
            if geom_type == "Circle":
                circle = get_curve(shape).Circle()
                center = circle.Location()

            elif geom_type == "Ellipse":
                ellipse = get_curve(shape).Ellipse()
                center = ellipse.Location()

            elif geom_type == "Hyperbola":
                hyperbola = get_curve(shape).Hyperbola()
                center = hyperbola.Location()

            elif geom_type == "Parabola":
                parabola = get_curve(shape).Parabola()
                center = parabola.Location()

            else:
                center = position_at(shape, 0.5)

        elif shape_type == "Face":
            if geom_type == "Cylinder":
                cylinder = get_surface(shape).Cylinder()
                center = cylinder.Location()

            elif geom_type == "Cone":
                cone = get_surface(shape).Cone()
                center = cone.Location()

            elif geom_type == "Sphere":
                sphere = get_surface(shape).Sphere()
                center = sphere.Location()

            elif geom_type == "Torus":
                torus = get_surface(shape).Torus()
                center = torus.Location()

            elif geom_type == "SurfaceOfRevolution":
                revolution = get_surface(shape)
                center = revolution.AxeOfRevolution().Location()

            else:
                center = center_of_mass(shape)

        if is_topods_vertex(center):
            return center
        else:
            return vertex(center)

    def calc_distance(self, shape1, shape2, center=False):
        if center:
            p1 = self.get_center(shape1)
            p2 = self.get_center(shape2)
            dist, p1, p2 = dist_shapes(p1, p2)
        else:
            dist, p1, p2 = dist_shapes(shape1, shape2)
        return {
            "distance": dist,
            "info": "center" if center else "min",
            "point1": get_point(p1),
            "point2": get_point(p2),
        }

    def calc_angle(self, shape1, shape2):
        shape_type1 = get_shape_type(shape1)
        shape_type2 = get_shape_type(shape2)
        geom_type1 = get_geom_type(shape1)
        geom_type2 = get_geom_type(shape2)

        def angle_line_line(line1, line2):
            if is_topods_edge(line1):
                l1 = get_curve(line1).Line()
            else:
                l1 = line1
            if is_topods_edge(line2):
                l2 = get_curve(line2).Line()
            else:
                l2 = line2
            return l1.Angle(l2) / pi * 180

        def angle_line_plane(line, plane):
            # 90 - angle between line and normal
            axis = plane.Axis()
            line2 = axis_to_line(axis)
            return 90 - angle_line_line(line, line2)

        def angle_plane_plane(plane1, plane2):
            # angle between the two normals
            axis1 = plane1.Axis()
            line1 = axis_to_line(axis1)
            axis2 = plane2.Axis()
            line2 = axis_to_line(axis2)
            return angle_line_line(line1, line2)

        angle = None
        p1 = None
        p2 = None
        info = ""

        if geom_type1 == "Line" and geom_type2 == "Line":
            angle = angle_line_line(shape1, shape2)
            p1 = self.get_center(shape1)
            p2 = self.get_center(shape2)
            info1 = "line"
            info2 = "line"

        elif geom_type1 == "Line" and shape_type2 in ["Edge", "Face"]:
            plane2 = get_plane(shape2)
            if plane2 is not None:
                angle = angle_line_plane(shape1, plane2)
                p1 = self.get_center(shape1)
                p2 = self.get_center(shape2)
                info1 = "line"
                info2 = f"Plane({shape_type1})"

        elif shape_type1 in ["Edge", "Face"] and geom_type2 == "Line":
            plane1 = get_plane(shape1)
            if plane1 is not None:
                angle = angle_line_plane(shape2, plane1)
                p1 = self.get_center(shape1)
                p2 = self.get_center(shape2)
                info1 = f"Plane({shape_type1})"
                info2 = "line"

        elif shape_type1 in ["Edge", "Face"] and shape_type2 in ["Edge", "Face"]:
            plane1 = get_plane(shape1)
            plane2 = get_plane(shape2)
            if plane1 is not None and plane2 is not None:
                angle = angle_plane_plane(plane1, plane2)
                p1 = self.get_center(shape1)
                p2 = self.get_center(shape2)
                info1 = f"Plane({shape_type1})"
                info2 = f"Plane({shape_type2})"

        if angle is None:
            return None
        else:
            return {
                "angle": angle,
                "point on shape1": get_point(p1),
                "point on shape2": get_point(p2),
                "info1": info1,
                "info2": info2,
            }

    def handle_distance(self, id1, id2, center):
        """
        Request the distance between the two objects that have the given ids
        """
        if not is_jupyter_cadquery:
            print_to_stdout(f"Identifiers received '{id1}', '{id2}'")

        shape1 = self.model[id1]
        shape2 = self.model[id2]

        response = self.calc_distance(shape1, shape2, center)
        response["type"] = "backend_response"
        response["subtype"] = "tool_response"
        response["tool_type"] = Tool.Distance

        angle = self.calc_angle(shape1, shape2)

        if angle is not None:
            response["angle"] = angle["angle"]
            response["info1"] = angle["info1"]
            response["info2"] = angle["info2"]

        if is_jupyter_cadquery:
            return response
        else:
            send_response(response, self.port)
            print_to_stdout(f"Data sent {response}")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser("OCP Viewer Backend")
    # parser.add_argument(
    #     "--port", type=int, required=True, help="Port the viewer listens to"
    # )
    # args = parser.parse_args()
    # backend = ViewerBackend(args.port)
    backend = ViewerBackend(3939)
    try:
        backend.start()
    except Exception as ex:  # pylint: disable=broad-except
        print(ex)
