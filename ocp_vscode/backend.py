from dataclasses import dataclass, asdict, fields
import argparse
import sys
import traceback
import base64
from ocp_vscode.comms import listener, MessageType, send_response
from build123d import (
    Axis,
    CenterOf,
    GeomType,
    Location,
    Plane,
    Vector,
    Vertex,
    Edge,
    Face,
    Solid,
    Shape,
    Compound,
    Location,
)
from build123d.topology import downcast
from ocp_tessellate.tessellator import (
    face_mapper,
    edge_mapper,
    vertex_mapper,
    get_faces,
    get_edges,
    get_vertices,
)
from ocp_tessellate.ocp_utils import make_compound, deserialize, tq_to_loc
from ocp_tessellate.trace import Trace, dump_face, dump_edge, dump_vertex


class SelectedCenterInfo:
    """
    Stores the information message about what as been used as center for the measurement
    """

    vertex = "Reference point has been taken as vertex location"
    circular = "Reference point has been taken as the center of the circle or ellipse"
    geom = "Reference point has been taken as the center of the geometry"
    cylinder = "Reference point has been taken as the center of the cylinder"


def print_to_stdout(*msg):
    """
    Write the given message to the stdout
    """
    print(*msg, flush=True, file=sys.stdout)


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            print_to_stdout(ex)
            traceback.print_exception(*sys.exc_info(), file=sys.stdout)

    return wrapper


@dataclass
class Tool:
    Distance = "DistanceMeasurement"
    Properties = "PropertiesMeasurement"
    Angle = "AngleMeasurement"


def set_precision(instance, decimals=2):
    """
    Set the precision of all float fields of the dataclass to the given number of decimals
    """
    for field in fields(instance):
        if field.type == float:
            value = getattr(instance, field.name)
            if value is not None:
                setattr(instance, field.name, round(value, decimals))
        elif isinstance(getattr(instance, field.name), tuple):
            # Handle tuple fields
            old_tuple = getattr(instance, field.name)
            new_tuple = tuple(
                round(elem, decimals) if isinstance(elem, float) else elem
                for elem in old_tuple
            )
            setattr(instance, field.name, new_tuple)


@dataclass
class Response:
    type: str = "backend_response"


@dataclass
class MeasureReponse(Response):
    center_info: str = ""  # a string telling the frontend how the reference points used for the measurement were chosen
    subtype: str = "tool_response"


@dataclass
class DistanceResponse(MeasureReponse):
    tool_type: Tool = Tool.Distance
    point1: tuple = None
    point2: tuple = None
    distance: float = None


@dataclass
class PropertiesResponse(MeasureReponse):
    tool_type: Tool = Tool.Properties
    center: tuple = None
    vertex_coords: tuple = None
    length: float = None
    width: float = None
    area: float = None
    volume: float = None
    radius: float = None
    geom_type: str = None


@dataclass
class AngleResponse(MeasureReponse):
    tool_type: Tool = Tool.Angle
    angle: float = None
    point1: tuple = None
    point2: tuple = None


class ViewerBackend:
    """
    Represents the backend of the viewer, it listens to the websocket and handles the events
    It's job is to send responses to the vscode extension that goes through the three cad viewer view.
    The reponses holds all the data needed to display the measurements.
    """

    def __init__(self, port: int) -> None:
        self.port = port
        self.model = None
        self.activated_tool = None
        self.filter_type = "none"  # The current active selection filter

    def start(self):
        """
        Start the backend
        """
        print("Viewer backend started")
        listener(self.handle_event)()

    @error_handler
    def handle_event(self, message, event_type: MessageType):
        """
        Handle the event received from the websocket
        Dispatch the event to the appropriate handler
        """
        if event_type == MessageType.data:
            self.load_model(message)
        elif event_type == MessageType.updates:
            changes = message

            if "activeTool" in changes:
                active_tool = changes.get("activeTool")

                if active_tool != "None":
                    self.activated_tool = active_tool
                else:
                    self.activated_tool = None

            if self.activated_tool is not None:
                self.handle_activated_tool(changes)

    def handle_activated_tool(self, changes):
        """
        Handle the activated tool, there is a special behavior for each tool
        """
        if not "selectedShapeIDs" in changes:
            return

        selectedObjs = changes["selectedShapeIDs"]
        if self.activated_tool == Tool.Distance and len(selectedObjs) == 2:
            shape_id1 = changes["selectedShapeIDs"][0]
            shape_id2 = changes["selectedShapeIDs"][1]
            self.handle_distance(shape_id1, shape_id2)

        elif self.activated_tool == Tool.Properties and len(selectedObjs) == 1:
            shape_id = changes["selectedShapeIDs"][0]
            self.handle_properties(shape_id)

        elif self.activated_tool == Tool.Angle and len(selectedObjs) == 2:
            shape_id1 = changes["selectedShapeIDs"][0]
            shape_id2 = changes["selectedShapeIDs"][1]
            self.handle_angle(shape_id1, shape_id2)

    def load_model(self, raw_model):
        """Read the transfered model from websocket"""

        def walk(model, trace):
            for v in model["parts"]:
                if v.get("parts") is not None:
                    walk(v, trace)
                else:
                    id = v["id"]
                    loc = (
                        Location().wrapped if v["loc"] is None else tq_to_loc(*v["loc"])
                    )
                    shape = [
                        deserialize(base64.b64decode(s.encode("utf-8")))
                        for s in v["shape"]
                    ]
                    compound = make_compound(shape) if len(shape) > 1 else shape[0]
                    self.model[id] = Compound(compound.Moved(loc))
                    faces = get_faces(compound)
                    for i, face in enumerate(faces):
                        trace.face(f"{id}/faces/faces_{i}", face)

                        self.model[f"{id}/faces/faces_{i}"] = Face(face.Moved(loc))
                    edges = get_edges(compound)
                    for i, edge in enumerate(edges):
                        trace.edge(f"{id}/edges/edges_{i}", edge)

                        self.model[f"{id}/edges/edges_{i}"] = (
                            Edge(edge) if loc is None else Edge(edge.Moved(loc))
                        )
                    vertices = get_vertices(compound)
                    for i, vertex in enumerate(vertices):
                        trace.vertex(f"{id}/vertices/vertex{i}", vertex)

                        self.model[f"{id}/vertices/vertices{i}"] = (
                            Vertex(vertex)
                            if loc is None
                            else Vertex(downcast(vertex.Moved(loc)))
                        )

        self.model = {}
        trace = Trace("ocp-vscode-backend.log")
        walk(raw_model, trace)
        trace.close()

    def handle_properties(self, shape_id):
        """
        Request the properties of the object with the given id
        """
        print_to_stdout(f"Identifier received '{shape_id}'")

        shape = self.model[shape_id]

        response = PropertiesResponse()

        if isinstance(shape, Vertex):
            response.vertex_coords = shape.to_tuple()

        elif isinstance(shape, Edge):
            response.radius = shape.radius if shape.geom_type() in ["CIRCLE"] else None
            response.length = shape.length

        elif isinstance(shape, Face):
            if shape.geom_type() == "CYLINDER":
                circle = shape.edges().filter_by(GeomType.CIRCLE).first
                response.radius = circle.radius

            response.length = shape.length
            response.width = shape.width
            response.area = shape.area

        elif isinstance(shape, (Solid, Compound)):
            response.volume = shape.volume

        geom_type = shape.geom_type().capitalize()
        response.geom_type = geom_type if geom_type != "Vertex" else None
        center, info = self.get_center(shape, False)
        response.center = center.to_tuple()
        response.vertex_coords = response.center
        response.center_info = f"{shape_id} : {info}"

        set_precision(response)

        send_response(asdict(response), self.port)
        print_to_stdout(f"Data sent {response}")

    def handle_angle(self, id1, id2):
        """
        Request the angle between the two objects that have the given ids
        """
        print_to_stdout(f"Identifiers received '{id1}', '{id2}'")

        shape1: Shape = self.model[id1]
        shape2: Shape = self.model[id2]
        first = (
            Plane(shape1)
            if isinstance(shape1, Face)
            else Plane(shape1 @ 0, z_dir=shape1.normal())
            if isinstance(shape1, Edge) and shape1.geom_type() in ["CIRCLE", "ELLIPSE"]
            else shape1 % 0
        )
        second = (
            Plane(shape2)
            if isinstance(shape2, Face)
            else Plane(shape2 @ 0, z_dir=shape2.normal())
            if isinstance(shape2, Edge) and shape2.geom_type() in ["CIRCLE", "ELLIPSE"]
            else shape2 % 0
        )
        if type(first) == type(second) == Plane:
            angle = first.z_dir.get_angle(second.z_dir)
        elif type(first) == type(second) == Vector:
            angle = first.get_angle(second)
        else:
            vector = first if isinstance(first, Vector) else second
            plane = first if isinstance(first, Plane) else second

            angle = 90 - plane.z_dir.get_angle(vector)
        angle = abs(angle)
        point1, info1 = self.get_center(shape1, True)
        point2, info2 = self.get_center(shape2, True)
        center_info = f"{id1} : {info1}\n{id2} : {info2}"
        response = AngleResponse(
            center_info=center_info,
            angle=angle,
            point1=point1.to_tuple(),
            point2=point2.to_tuple(),
        )
        set_precision(response)
        send_response(asdict(response), self.port)
        print_to_stdout(f"Data sent {response}")

    def get_center(
        self, shape: Shape, for_distance=True
    ) -> tuple[Vector, SelectedCenterInfo]:
        """
        Returns the center vector of the given shape
        Center of the shape depends on the type of the shape and the tool used
        For instance, circle edge center will be on the edge for properties tool
        but at the center of the circle for distance tool
        """
        if isinstance(shape, Vertex):
            return shape.center(), SelectedCenterInfo.vertex
        elif isinstance(shape, Edge):
            if shape.geom_type() in [
                GeomType.CIRCLE,
                GeomType.ELLIPSE,
                "CIRCLE",
                "ELLIPSE",
            ]:
                if for_distance:
                    return shape.arc_center, SelectedCenterInfo.circular
                else:
                    return shape.center(), SelectedCenterInfo.geom

        elif isinstance(shape, Face):
            if shape.geom_type() in [GeomType.CYLINDER, "CYLINDER"]:
                if not for_distance:
                    return shape.center(), SelectedCenterInfo.geom

                extremity_edges = shape.edges().filter_by(GeomType.CIRCLE)
                if len(extremity_edges) == 2:
                    return (
                        extremity_edges.first.arc_center
                        - (
                            extremity_edges.first.arc_center
                            - extremity_edges.last.arc_center
                        )
                        / 2,
                        SelectedCenterInfo.cylinder,
                    )
                else:
                    try:
                        return (
                            extremity_edges.first.arc_center,
                            SelectedCenterInfo.cylinder,
                        )
                    except IndexError:
                        # cylinder might have bspline extremity edges hence the list would be empty
                        # in that case we default to geom center
                        pass

        return shape.center(), SelectedCenterInfo.geom

    def handle_distance(self, id1, id2):
        """
        Request the distance between the two objects that have the given ids
        """
        print_to_stdout(f"Identifiers received '{id1}', '{id2}'")

        shape1: Shape = self.model[id1]
        shape2: Shape = self.model[id2]
        p1, info1 = self.get_center(shape1)
        p2, info2 = self.get_center(shape2)
        center_info = f"{id1} : {info1}\n{id2} : {info2}"
        dist = (p2 - p1).length
        response = DistanceResponse(
            center_info=center_info,
            point1=p1.to_tuple(),
            point2=p2.to_tuple(),
            distance=dist,
        )
        set_precision(response)
        send_response(asdict(response), self.port)
        print_to_stdout(f"Data sent {response}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("OCP Viewer Backend")
    parser.add_argument(
        "--port", type=int, required=True, help="Port the viewer listens to"
    )
    args = parser.parse_args()
    backend = ViewerBackend(args.port)
    try:
        backend.start()
    except Exception as ex:
        print(ex)
