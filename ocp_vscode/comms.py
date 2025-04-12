"""Communication with the viewer"""

import base64
import enum
import json
import os
import socket
import warnings

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


# pylint: disable=unused-import
try:
    from IPython import get_ipython
    import jupyter_console

    JCONSOLE = True
except:  # pylint: disable=bare-except
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
                        timeit, "", f"websocket send {len(j)/1024/1024:.3f} MB", 1
                    ):
                        result = None
                        if message_type == MessageType.COMMAND and not (
                            isinstance(data, dict) and data["type"] == "screenshot"
                        ):
                            try:
                                result = json.loads(ws.recv())
                            except Exception as ex:  # pylint: disable=broad-except
                                print(ex)

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


def find_and_set_port():
    """Set the port and connection file"""

    def find_port():
        port = None
        current_path = Path.cwd()
        states = get_state().items()
        for p, state in states:
            if not port_check(int(p)):
                print(f"Found stale configuration for port {p}, deleting it.")
                update_state(int(p), None, None)
                continue

            roots = state.get("roots", [])
            for root in roots:
                if current_path.is_relative_to(Path(root)):
                    port = int(p)
                    break
        if port is None:
            ports = [port for port, _ in states if port_check(int(port))]
            if len(ports) == 1:
                port = ports[0]
            elif len(ports) > 1:
                raise RuntimeError(
                    f"\nMultiple ports found ({', '.join(ports)}) and the file is outside of any\n"
                    "workspace folder of this VS Code instance:\n"
                    "The right viewer cannot be auto detected, use set_port(port) in your code."
                )
            else:
                print(f"Could not find port in config file {get_config_file()}")

        return port

    port = int(os.environ.get("OCP_PORT", "0"))

    if port > 0:
        print(f"Using predefined port {port} taken from environment variable OCP_PORT")
    else:
        port = find_port()
        if port is not None:
            print(f"Using port {port} taken from config file")
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
            update_state(CMD_PORT, "connection_file", cf)
            print(f"Jupyter connection file path written to {get_config_file()}")
        else:
            print("Jupyter kernel not responding")
    # elif not JCONSOLE:
    #     print("Jupyter console not installed")
    #     pass
    # else:
    #     print("Jupyter kernel not running")
