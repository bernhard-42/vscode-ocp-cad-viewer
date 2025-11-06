"""Communication with the viewer"""

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

import base64
import enum
import json
import os
import socket
import warnings

import questionary

from websockets.sync.client import connect

import orjson
from ocp_tessellate.utils import Timer
from ocp_tessellate.ocp_utils import (
    is_topods_shape,
    is_toploc_location,
    serialize,
    loc_to_tq,
)
from .state import get_ports, update_state, get_config_file

from IPython import get_ipython

# pylint: disable=unused-import
try:
    import jupyter_console  # noqa: F401

    JCONSOLE = True
except Exception:
    JCONSOLE = False

CMD_URL = "ws://127.0.0.1"
CMD_PORT = 3939

INIT_DONE = False


warnings.simplefilter("once", UserWarning)


def warn_once(message):
    def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
        return "%s: %s\n" % (category.__name__, message)

    warnings.formatwarning = warning_on_one_line
    warnings.warn(message, UserWarning)


#
# Send data to the viewer
#


class MessageType(enum.IntEnum):
    """Message types"""

    DATA = 1
    COMMAND = 2
    UPDATES = 3
    LISTEN = 4
    BACKEND = 5
    BACKEND_RESPONSE = 6
    CONFIG = 7


__all__ = [
    "send_data",
    "send_command",
    "send_response",
    "set_port",
    "get_port",
    "listener",
    "is_pytest",
]


def is_pytest():
    return os.environ.get("OCP_VSCODE_PYTEST") == "1"


def port_check(port):
    """Check whether the port is listening"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex((get_host(), port)) == 0
    if result:
        s.close()
    return result


def default(obj):
    """Default JSON serializer."""
    if is_topods_shape(obj):
        return base64.b64encode(serialize(obj)).decode("utf-8")
    elif is_toploc_location(obj):
        return loc_to_tq(obj)
    elif isinstance(obj, enum.Enum):
        return obj.value
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_port():
    """Get the port"""
    if is_pytest():
        return 3939

    if not INIT_DONE:
        find_and_set_port()
        set_connection_file()
    return CMD_PORT


def get_host():
    """Get the host"""
    return CMD_URL[5:]


def set_port(port, host="127.0.0.1"):
    """Set the port"""
    global CMD_PORT, CMD_URL, INIT_DONE  # pylint: disable=global-statement
    CMD_PORT = port
    CMD_URL = f"ws://{host}"
    INIT_DONE = True


def _send(data, message_type, port=None, timeit=False):
    """Send data to the viewer"""
    global WS

    if port is None:
        if not INIT_DONE:
            find_and_set_port()
            set_connection_file()
        port = CMD_PORT
    try:
        with Timer(timeit, "", "json dumps", 1):
            j = orjson.dumps(data, default=default)  # pylint: disable=no-member
            if message_type == MessageType.COMMAND:
                j = b"C:" + j
            elif message_type == MessageType.DATA:
                j = b"D:" + j
            elif message_type == MessageType.LISTEN:
                j = b"L:" + j
            elif message_type == MessageType.BACKEND:
                j = b"B:" + j
            elif message_type == MessageType.BACKEND_RESPONSE:
                j = b"R:" + j
            elif message_type == MessageType.CONFIG:
                j = b"S:" + j

        with Timer(timeit, "", f"websocket connect ({message_type.name})", 1):
            try:
                with connect(f"{CMD_URL}:{port}", close_timeout=0.05) as ws:
                    ws.send(j)

                    with Timer(
                        timeit, "", f"websocket send {len(j) / 1024 / 1024:.3f} MB", 1
                    ):
                        result = None
                        if message_type == MessageType.COMMAND and not (
                            isinstance(data, dict) and data["type"] == "screenshot"
                        ):
                            try:
                                result = json.loads(ws.recv())
                            except Exception as ex:  # pylint: disable=broad-except
                                print(ex)
                        elif message_type == MessageType.COMMAND and (
                            isinstance(data, dict) and data["type"] == "screenshot"
                        ):
                            result = {}

            except Exception as ex:
                warn_once("The viewer doesn't seem to run: " + str(ex))
                # set some dummy values to avoid errors
                return {
                    "collapse": "none",
                    "_splash": False,
                    "default_facecolor": (1, 234, 56),
                    "default_thickedgecolor": (123, 45, 6),
                    "default_vertexcolor": (123, 45, 6),
                }

        return result

    except Exception as ex:  # pylint: disable=broad-except
        print(
            f"Cannot connect to viewer on port {port}, is it running and the right port provided?"
        )
        print(ex)
        return None


def send_data(data, port=None, timeit=False):
    """Send data to the viewer"""
    return _send(data, MessageType.DATA, port, timeit)


def send_config(config, port=None, title=None, timeit=False):
    """Send config to the viewer"""
    return _send(config, MessageType.CONFIG, port, timeit)


def send_command(data, port=None, title=None, timeit=False):
    """Send command to the viewer"""
    result = _send(data, MessageType.COMMAND, port, timeit)
    if result.get("command") == "status":
        return result["text"]
    else:
        return result


def send_backend(data, port=None, timeit=False):
    """Send data to the viewer"""
    return _send(data, MessageType.BACKEND, port, timeit)


def send_response(data, port=None, timeit=False):
    """Send data to the viewer"""
    return _send(data, MessageType.BACKEND_RESPONSE, port, timeit)


#
# Receive data from the viewer
#


# async listener for the websocket class
# this will be called when the viewer sends data
# the data is then passed to the callback function
#
def listener(callback):
    """Listen for data from the viewer"""

    def _listen():
        last_config = {}
        with connect(f"{CMD_URL}:{CMD_PORT}", max_size=2**28) as websocket:
            websocket.send(b"L:Python listener")
            while True:
                try:
                    message = websocket.recv()
                    if message is None:
                        continue

                    message = json.loads(message)
                    if "model" in message.keys():
                        callback(message["model"], MessageType.DATA)

                    if message.get("command") == "status":
                        changes = message["text"]
                        new_changes = {}
                        for k, v in changes.items():
                            if k in last_config and last_config[k] == v:
                                continue
                            new_changes[k] = v
                        last_config = changes
                        callback(new_changes, MessageType.UPDATES)

                    elif message.get("command") == "stop":
                        print("Stopping Python listener")
                        break
                except Exception as ex:  # pylint: disable=broad-except
                    print(ex)
                    break

    return _listen


def find_and_set_port():
    """Set the port and connection file"""

    def find_port():
        port = None
        ports = get_ports()

        valid_ports = []
        for p in ports:
            if port_check(int(p)):
                valid_ports.append(p)

        if len(valid_ports) == 0:
            return None

        elif len(valid_ports) == 1:
            port = valid_ports[0]

        else:
            if get_ipython().__class__.__name__ == "ZMQInteractiveShell":
                print("\n=> Select port in VS Code input box above\n")
                port = input(f"Select port from {[int(p) for p in valid_ports]} ")
            else:
                port = questionary.select(
                    "Multiple viewers found. Select a port:",
                    choices=[str(p) for p in valid_ports],
                ).ask()
            if port is not None and port != "":
                port = int(port)

        return port

    try:
        port = int(os.environ.get("OCP_PORT", "0"))
    except ValueError:
        print(
            f"Port {os.environ.get('OCP_PORT')} taken from environment variable OCP_PORT is invalid"
        )
        port = 0

    if port > 0:
        print(f"Using predefined port {port} taken from environment variable OCP_PORT")
    else:
        port = find_port()
        if port is not None:
            print(f"Using port {port}")
        elif port_check(3939):
            port = 3939
            print(f"Default port {port} is open, using it")

    set_port(port)


def set_connection_file():
    """Set the connection file for Jupyter in the state file .ocpvscode"""
    if JCONSOLE and hasattr(get_ipython(), "kernel"):
        kernel = get_ipython().kernel
        cf = kernel.config["IPKernelApp"]["connection_file"]
        with open(cf, "r", encoding="utf-8") as f:
            connection_info = json.load(f)

        if port_check(connection_info["iopub_port"]):
            print("Jupyter kernel running")
            try:
                _ = int(CMD_PORT)
                update_state(str(CMD_PORT), cf)
                print(f"Jupyter connection file path written to {get_config_file()}")
            except ValueError:
                print(
                    f"Cannot set Jupyter connection file, port {CMD_PORT}' is non-numeric"
                )
        else:
            print("Jupyter kernel not responding")
