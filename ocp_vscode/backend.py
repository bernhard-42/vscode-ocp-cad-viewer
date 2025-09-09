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
from dataclasses import dataclass
import sys
import traceback
import os

from ocp_tessellate.ocp_utils import (
    deserialize,
    make_compound,
    tq_to_loc,
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
from ocp_vscode.measure import get_distance, get_properties


@dataclass
class Tool:
    """The tools available in the viewer"""

    Distance = "DistanceMeasurement"
    Properties = "PropertiesMeasurement"


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
        if "selectedShapeIDs" not in changes:
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

        response = get_properties(shape)

        response["type"] = "backend_response"
        response["subtype"] = "tool_response"
        response["tool_type"] = Tool.Properties

        if is_jupyter_cadquery:
            return response
        else:
            send_response(response, self.port)
            print_to_stdout(f"Data sent {response}")

    def handle_distance(self, id1, id2, center):
        """
        Request the distance between the two objects that have the given ids
        """
        if not is_jupyter_cadquery:
            print_to_stdout(f"Identifiers received '{id1}', '{id2}'")

        shape1 = self.model[id1]
        shape2 = self.model[id2]

        response = get_distance(shape1, shape2, center)

        response["type"] = "backend_response"
        response["subtype"] = "tool_response"
        response["tool_type"] = Tool.Distance

        if is_jupyter_cadquery:
            return response
        else:
            send_response(response, self.port)
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
    except Exception as ex:  # pylint: disable=broad-except
        print(ex)
