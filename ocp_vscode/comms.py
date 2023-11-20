import enum
from websockets.sync.client import connect
import orjson as json
from ocp_tessellate.utils import Timer
import os

CMD_URL = "ws://127.0.0.1"
CMD_PORT = 3939

try:
    CMD_PORT = int(os.environ["ocp_port"])
except (ValueError, KeyError):
    pass

#
# Send data to the viewer
#


class MessageType(enum.IntEnum):
    data = 1
    command = 2
    updates = 3
    listen = 4


__all__ = ["send_data", "send_command", "set_port", "get_port", "listener"]


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
            j = json.dumps(data)
            if message_type == MessageType.command:
                j = b"C:" + j
            elif message_type == MessageType.data:
                j = b"D:" + j

        with Timer(timeit, "", "websocket send", 1):
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


def send_command(data, port=None, timeit=False):
    return _send(data, MessageType.command, port, timeit)


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
        with connect(f"{CMD_URL}:{CMD_PORT}") as websocket:
            websocket.send(b"L:register")
            while True:
                try:
                    message = websocket.recv()
                    if message is None:
                        continue

                    message = json.loads(message)
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
