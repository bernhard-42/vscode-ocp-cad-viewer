import base64
import enum
from websockets.sync.client import connect
import orjson as json
from ocp_tessellate.utils import Timer
from ocp_tessellate.ocp_utils import (
    is_topods_shape,
    is_toploc_location,
    serialize,
    loc_to_tq,
)

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
            j = json.dumps(data, default=default)
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
        print("Cannot connect to viewer, is it running and the right port provided?")
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
