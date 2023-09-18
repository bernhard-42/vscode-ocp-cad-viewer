from dataclasses import dataclass, asdict
from multiprocessing.shared_memory import SharedMemory
import pickle
from ocp_vscode.config import SHARED_MEMORY_BLOCK_SIZE
from ocp_vscode.comms import listener, MessageType, send_data
import argparse
from enum import StrEnum
import struct
from build123d import CenterOf, GeomType, Vector, Vertex, Edge, Face, Solid, Shape
import traceback

HEADER_SIZE = 4


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            print("The following error happened, backend still running")
            traceback.print_exc()

    return wrapper


class Tool(StrEnum):
    Distance = "DistanceMeasurement"
    Properties = "PropertiesMeasurement"


@dataclass
class DistanceResponse:
    type: str = "tool_response"
    tool_type: Tool = Tool.Distance
    point1: tuple = None
    point2: tuple = None
    distance: float = None

    def set_precision(self, decimals=2):
        self.distance = (
            round(self.distance, decimals) if self.distance is not None else None
        )


@dataclass
class PropertiesResponse:
    type: str = "tool_response"
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


class ViewerBackend:
    def __init__(self, port: int, block_size: int) -> None:
        self.port = port
        self._shared_memory = SharedMemory(
            name=f"ocp-viewer-{port}", create=True, size=block_size
        )
        self.model = None
        self.activated_tool = None

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

    def load_model(self):
        """Read the transfered model from the shared memory"""
        block_size = self._shared_memory.buf[:HEADER_SIZE]
        data = self._shared_memory.buf[
            HEADER_SIZE : HEADER_SIZE + int.from_bytes(block_size)
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
