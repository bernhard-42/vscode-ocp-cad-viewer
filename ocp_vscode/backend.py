import argparse
from dataclasses import dataclass, asdict
from multiprocessing.shared_memory import SharedMemory
import pickle
import sys
import traceback

from ocp_vscode.config import SHARED_MEMORY_BLOCK_SIZE
from ocp_vscode.comms import listener, MessageType, send_data
from build123d import (
    Axis,
    CenterOf,
    GeomType,
    Plane,
    Vector,
    Vertex,
    Edge,
    Face,
    Solid,
    Shape,
)


HEADER_SIZE = 4


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            print("The following error happened, backend still running")
            traceback.print_exc()

    return wrapper


@dataclass
class Tool:
    Distance = "DistanceMeasurement"
    Properties = "PropertiesMeasurement"
    Angle = "AngleMeasurement"


@dataclass
class Response:
    type: str = "backend_response"


@dataclass
class MeasureReponse(Response):
    subtype: str = "tool_response"


@dataclass
class DistanceResponse(MeasureReponse):
    tool_type: Tool = Tool.Distance
    point1: tuple = None
    point2: tuple = None
    distance: float = None

    def set_precision(self, decimals=2):
        self.distance = (
            round(self.distance, decimals) if self.distance is not None else None
        )


@dataclass
class PropertiesResponse(MeasureReponse):
    tool_type: Tool = Tool.Properties
    center: tuple = None
    vertex_coords: tuple = None
    length: float = None
    area: float = None
    volume: float = None

    def set_precision(self, decimals=2):
        self.length = round(self.length, decimals) if self.length is not None else None
        self.area = round(self.area, decimals) if self.area is not None else None
        self.volume = round(self.volume, decimals) if self.volume is not None else None


@dataclass
class AngleResponse(MeasureReponse):
    tool_type: Tool = Tool.Angle
    angle: float = None
    point1: tuple = None
    point2: tuple = None

    def set_precision(self, decimals=2):
        self.angle = round(self.angle, decimals) if self.angle is not None else None


class ViewerBackend:
    def __init__(self, port: int, block_size: int) -> None:
        self.port = port
        self._shared_memory = SharedMemory(
            name=f"ocp-viewer-{port}", create=True, size=block_size
        )
        self.model = None
        self.activated_tool = None
        self.filter_type = "none"  # The current active selection filter

    def start(self):
        print("Viewer backend started")
        listener(self.handle_event)()

    @error_handler
    def handle_event(self, changes: dict, event_type: MessageType):
        if "activeTool" in changes:
            active_tool = changes.get("activeTool")

            if active_tool != "None":
                self.load_model()
                self.activated_tool = active_tool
            else:
                self.activated_tool = None

        if self.activated_tool is not None:
            self.handle_activated_tool(changes)

    def handle_activated_tool(self, changes):
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

    def load_model(self):
        """Read the transfered model from the shared memory"""
        block_size = self._shared_memory.buf[:HEADER_SIZE]
        data = self._shared_memory.buf[
            HEADER_SIZE : HEADER_SIZE + int.from_bytes(block_size, sys.byteorder)
        ]
        self.model = pickle.loads(data)

    def handle_properties(self, shape_id):
        """
        Request the properties of the object with the given id
        """
        shape = self.model[shape_id]

        if isinstance(shape, Vertex):
            response = PropertiesResponse(vertex_coords=shape.to_tuple())
        elif isinstance(shape, Edge):
            response = PropertiesResponse(length=shape.length)
        elif isinstance(shape, Face):
            response = PropertiesResponse(area=shape.area)
        elif isinstance(shape, Solid):
            response = PropertiesResponse(volume=shape.volume)

        response.center = self.get_center(shape, False).to_tuple()
        response.set_precision()

        send_data(asdict(response), self.port)
        print(f"Data sent {response}")

    def handle_angle(self, id1, id2):
        """
        Request the angle between the two objects that have the given ids
        """
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

        point1 = self.get_center(shape1, True)
        point2 = self.get_center(shape2, True)

        response = AngleResponse(
            angle=angle,
            point1=point1.to_tuple(),
            point2=point2.to_tuple(),
        )
        response.set_precision(3)
        send_data(asdict(response), self.port)
        print(f"Data sent {response}")

    def get_center(self, shape: Shape, for_distance=True) -> Vector:
        """
        Returns the center vector of the given shape
        Center of the shape depends on the type of the shape and the tool used
        For instance, circle edge center will be on the edge for properties tool
        but at the center of the circle for distance tool
        """
        if isinstance(shape, Vertex):
            return shape.center()
        elif isinstance(shape, Edge):
            if shape.geom_type() in [
                GeomType.CIRCLE,
                GeomType.ELLIPSE,
                "CIRCLE",
                "ELLIPSE",
            ]:
                return shape.arc_center if for_distance else shape.center()
        elif isinstance(shape, Face):
            if shape.geom_type() in [GeomType.CYLINDER, "CYLINDER"]:
                if not for_distance:
                    return shape.center()

                extremity_edges = shape.edges().filter_by(GeomType.CIRCLE)
                if len(extremity_edges) == 2:
                    return (
                        extremity_edges.first.arc_center
                        - (
                            extremity_edges.first.arc_center
                            - extremity_edges.last.arc_center
                        )
                        / 2
                    )
                else:
                    return extremity_edges.first.arc_center

        return shape.center()

    def handle_distance(self, id1, id2):
        """
        Request the distance between the two objects that have the given ids
        """
        shape1: Shape = self.model[id1]
        shape2: Shape = self.model[id2]
        p1 = self.get_center(shape1)
        p2 = self.get_center(shape2)
        dist = (p2 - p1).length
        response = DistanceResponse(
            point1=p1.to_tuple(), point2=p2.to_tuple(), distance=dist
        )
        response.set_precision()
        send_data(asdict(response), self.port)
        print(f"Data sent {response}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("OCP Viewer Backend")
    parser.add_argument(
        "--port", type=int, required=True, help="Port the viewer listens to"
    )
    args = parser.parse_args()
    backend = ViewerBackend(args.port, SHARED_MEMORY_BLOCK_SIZE)
    try:
        backend.start()
    except Exception as ex:
        print(ex)
