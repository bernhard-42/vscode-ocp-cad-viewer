"""Communication with the viewer"""

import base64
import enum
import json
import os
import socket

from pathlib import Path

from websockets.sync.client import connect

import orjson
from ocp_tessellate.utils import Timer
from ocp_tessellate.ocp_utils import (
    is_topods_shape,
    is_toploc_location,
    serialize,
    loc_to_tq,
)
from .state import get_state, update_state, get_config_file

try:
    from jupyter_client import find_connection_file

    JCLIENT = True
except:  # pylint: disable=bare-except
    JCLIENT = False

CMD_URL = "ws://127.0.0.1"
CMD_PORT = 3939

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
]


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
    return CMD_PORT


def set_port(port):
    """Set the port"""
    global CMD_PORT  # pylint: disable=global-statement
    CMD_PORT = port


def _send(data, message_type, port=None, timeit=False):
    """Send data to the viewer"""
    if port is None:
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

        with Timer(timeit, "", f"websocket send {len(j)/1024/1024:.3f} MB", 1):
            ws = connect(f"{CMD_URL}:{port}")
            ws.send(j)

            result = None
            if message_type == MessageType.COMMAND:
                try:
                    result = json.loads(ws.recv())
                except Exception as ex:  # pylint: disable=broad-except
                    print(ex)
            try:
                ws.close()
            except:  # pylint: disable=bare-except
                pass

            return result

    except Exception as ex:  # pylint: disable=broad-except
        print(
            f"Cannot connect to viewer on port {port}, is it running and the right port provided?"
        )
        print(ex)
        return


def send_data(data, port=None, timeit=False):
    """Send data to the viewer"""
    return _send(data, MessageType.DATA, port, timeit)


def send_config(config, port=None, timeit=False):
    """Send config to the viewer"""
    return _send(config, MessageType.CONFIG, port, timeit)


def send_command(data, port=None, timeit=False):
    """Send command to the viewer"""
    return _send(data, MessageType.COMMAND, port, timeit)


def send_backend(data, port=None, timeit=False):
    """Send data to the viewer"""
    return _send(data, MessageType.BACKEND, port, timeit)


def send_response(data, port=None, timeit=False):
    """Send data to the viewer"""
    return _send(data, MessageType.BACKEND_RESPONSE, port, timeit)


#
# Receive data from the viewer
#


# async listerner for the websocket class
# this will be called when the viewer sends data
# the data is then passed to the callback function
#
def listener(callback):
    """Listen for data from the viewer"""

    def _listen():
        last_config = {}
        with connect(f"{CMD_URL}:{CMD_PORT}", max_size=2**28) as websocket:
            websocket.send(b"L:register")
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

                except Exception as ex:  # pylint: disable=broad-except
                    print(ex)
                    break

    return _listen


def set_port_and_connectionfile():
    """Set the port and connection file"""

    def find_port():
        port = None
        current_path = Path.cwd()
        for path in [current_path] + list(current_path.parents):
            port = get_state(path)["port"]
            if port is not None:
                break

        return port

    port = int(os.environ.get("OCP_PORT", "0"))

    if port > 0:
        print(f"Using predefined port {port} taken from environment variable OCP_PORT")
    else:
        port = find_port()
        if port is None:
            print("No port found in config file, using default port 3939")
            print("To change the port, use set_port(port) in your code")
            port = 3939
        else:
            port = int(port)
            print(f"Using port {port} taken from config file")

    set_port(port)

    if JCLIENT:
        cf = find_connection_file()
        with open(cf, "r", encoding="utf-8") as f:
            connection_info = json.load(f)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(("127.0.0.1", connection_info["iopub_port"]))

        if result == 0:
            print("Jupyter kernel running")
            s.close()
            update_state(port, "connection_file", cf)
            print(f"Jupyter Connection file written to {get_config_file()}")
        else:
            print("Jupyter kernel not running")
