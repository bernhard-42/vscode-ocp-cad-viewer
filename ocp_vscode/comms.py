import base64
import enum
import os
import socket

from pathlib import Path

from websockets.sync.client import connect

import orjson
import json
from ocp_tessellate.utils import Timer
from ocp_tessellate.ocp_utils import (
    is_topods_shape,
    is_toploc_location,
    serialize,
    loc_to_tq,
)

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
    data = 1
    command = 2
    updates = 3
    listen = 4
    backend = 5
    backend_response = 6
    config = 7


__all__ = [
    "send_data",
    "send_command",
    "send_response",
    "set_port",
    "get_port",
    "listener",
]


def default(obj):
    if is_topods_shape(obj):
        return base64.b64encode(serialize(obj)).decode("utf-8")
    elif is_toploc_location(obj):
        return loc_to_tq(obj)
    elif isinstance(obj, enum.Enum):
        return obj.value
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_port():
    return CMD_PORT


def set_port(port):
    global CMD_PORT
    CMD_PORT = port


def _send(data, message_type, port=None, timeit=False):
    if port is None:
        port = CMD_PORT
    try:
        with Timer(timeit, "", "json dumps", 1):
            j = orjson.dumps(data, default=default)
            if message_type == MessageType.command:
                j = b"C:" + j
            elif message_type == MessageType.data:
                j = b"D:" + j
            elif message_type == MessageType.listen:
                j = b"L:" + j
            elif message_type == MessageType.backend:
                j = b"B:" + j
            elif message_type == MessageType.backend_response:
                j = b"R:" + j
            elif message_type == MessageType.config:
                j = b"S:" + j

        with Timer(timeit, "", f"websocket send {len(j)/1024/1024:.3f} MB", 1):
            ws = connect(f"{CMD_URL}:{port}")
            ws.send(j)

            result = None
            if message_type == MessageType.command:
                try:
                    result = json.loads(ws.recv())
                except Exception as ex:
                    print(ex)
            try:
                ws.close()
            except:
                pass

            return result

    except Exception as ex:
        print(
            f"Cannot connect to viewer on port {port}, is it running and the right port provided?"
        )
        print(ex)
        return


def send_data(data, port=None, timeit=False):
    return _send(data, MessageType.data, port, timeit)


def send_config(config, port=None, timeit=False):
    return _send(config, MessageType.config, port, timeit)


def send_command(data, port=None, timeit=False):
    return _send(data, MessageType.command, port, timeit)


def send_backend(data, port=None, timeit=False):
    return _send(data, MessageType.backend, port, timeit)


def send_response(data, port=None, timeit=False):
    return _send(data, MessageType.backend_response, port, timeit)


#
# Receive data from the viewer
#


# async listerner for the websocket class
# this will be called when the viewer sends data
# the data is then passed to the callback function
#
def listener(callback):
    def _listen():
        LAST_CONFIG = {}
        with connect(f"{CMD_URL}:{CMD_PORT}", max_size=2**28) as websocket:
            websocket.send(b"L:register")
            while True:
                try:
                    message = websocket.recv()
                    if message is None:
                        continue

                    message = json.loads(message)
                    if "model" in message.keys():
                        callback(message["model"], MessageType.data)

                    if message.get("command") == "status":
                        changes = message["text"]
                        new_changes = {}
                        for k, v in changes.items():
                            if k in LAST_CONFIG and LAST_CONFIG[k] == v:
                                continue
                            new_changes[k] = v
                        LAST_CONFIG = changes
                        callback(new_changes, MessageType.updates)

                except Exception as ex:
                    print(ex)
                    break

    return _listen


def set_port_and_connectionfile():
    def find_config():
        config_path = None
        current_path = Path.cwd()
        for path in [current_path] + list(current_path.parents):
            cur_file_path = path / ".ocp_vscode"
            if cur_file_path.exists():
                config_path = cur_file_path
                break

        return config_path

    port = int(os.environ.get("OCP_PORT", "0"))
    config_path = find_config()

    if port > 0:
        print(f"Using predefined port {port} taken from environment variable OCP_PORT")
    else:
        if config_path is None:
            raise RuntimeError(".ocp_vscode not found")

        with open(config_path, "r", encoding="utf-8") as f:
            port = json.load(f)["port"]
            print(f"Using port {port} taken from {config_path}")
    set_port(port)

    if JCLIENT:
        if config_path is None:
            print(".ocp_vscode not found, Jupyter Console not supported")
        else:
            cf = find_connection_file()
            with open(cf, "r", encoding="utf-8") as f:
                connection_info = json.load(f)

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex(("127.0.0.1", connection_info["iopub_port"]))

            if result == 0:
                print("Jupyter kernel running")
                s.close()

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {"port": port, "connection_file": cf},
                        f,
                        indent=4,
                    )
                print(f"Jupyter Connection file written to {config_path}")
            else:
                print("Jupyter kernel not running")
