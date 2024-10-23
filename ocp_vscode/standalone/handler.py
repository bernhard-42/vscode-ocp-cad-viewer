import orjson
from flask import Flask, render_template
from flask_sock import Sock
from simple_websocket import ConnectionClosed
from ocp_vscode.comms import MessageType
from ocp_vscode.backend import ViewerBackend
from ocp_vscode.backend_logo import logo


class Viewer:
    def __init__(self, params):
        self.configure(params)

        self.app = Flask(__name__)
        self.sock = Sock(self.app)

        self.backend = ViewerBackend(self.port)

        self.python_client = None
        self.javascript_client = None
        self.status = {}
        self.splash = True

        self.sock.route("/")(self.handle_message)
        self.app.add_url_rule("/viewer", "viewer", self.index)

    def debug_print(self, *msg):
        if self.debug:
            print("Debug:", *msg)

    def configure(self, params):
        self.config = {
            "glass": True,
            "tools": True,
            "treeWidth": 240,
            "axes": False,
            "axes0": False,
            "grid": [False, False, False],
            "ortho": True,
            "transparent": False,
            "blackEdges": False,
            "collapse": "R",
            "clipIntersection": False,
            "clipPlaneHelpers": False,
            "clipObjectColors": False,
            "clipNormal0": [-1, 0, 0],
            "clipNormal1": [0, -1, 0],
            "clipNormal2": [0, 0, -1],
            "clipSlider0": -1,
            "clipSlider1": -1,
            "clipSlider2": -1,
            "control": "orbit",
            "up": "Z",
            "ticks": 10,
            "centerGrid": False,
            "position": None,
            "quaternion": None,
            "target": None,
            "zoom": 1,
            "panSpeed": 0.5,
            "rotateSpeed": 1.0,
            "zoomSpeed": 0.5,
            "timeit": False,
            "default_edgecolor": "#808080",
            "default_color": "#e8b024",
            "debug": False,
        }
        for k, v in params.items():
            print(k, v)
            if k == "port":
                self.config["port"] = self.port = v
            elif k == "debug":
                self.config["debug"] = self.debug = v
            elif k == "collapse":
                self.config["collapse"] = str(v)
            elif k == "no_glass":
                self.config["glass"] = not v
            elif k == "no_tools":
                self.config["tools"] = not v
            elif k == "perspective":
                self.config["ortho"] = not v
            else:
                self.config[k] = v
        print(self.config)
        print(self.debug)

    def start(self):
        self.app.run(debug=self.debug, port=self.port)
        self.sock.init_app(self.app)
        self.backend.load_model(logo)

    def index(self):
        return render_template("viewer.html", **self.config)

    def handle_message(self, ws):

        try:
            while True:
                data = ws.receive()
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                message_type = data[0]
                data = data[2:]

                if message_type == "C":
                    self.python_client = ws
                    cmd = orjson.loads(data)
                    if cmd == "status":
                        self.debug_print("Received status command")
                        self.python_client.send(orjson.dumps({"text": self.status}))
                    elif cmd == "config":
                        self.debug_print("Received config command")
                        self.config["_splash"] = self.splash
                        self.python_client.send(orjson.dumps(self.config))
                    elif cmd.type == "screenshot":
                        self.debug_print("Received screenshot command")
                        self.python_client(orjson.dumps(cmd))

                elif message_type == "D":
                    self.python_client = ws
                    self.debug_print("Received a new model")
                    self.javascript_client.send(data)
                    if self.splash:
                        self.splash = False

                elif message_type == "U":
                    self.javascript_client = ws
                    changes = orjson.loads(data)["text"]
                    self.debug_print("Received incremental UI changes", changes)
                    for key, value in changes.items():
                        self.status[key] = value
                    self.backend.handle_event(changes, MessageType.UPDATES)

                elif message_type == "S":
                    self.python_client = ws
                    self.debug_print("Received a config")
                    self.javascript_client.send(data)
                    self.debug_print("Posted config to view")

                elif message_type == "L":
                    self.javascript_client = ws
                    self.debug_print("Javascript listener registered", data)

                elif message_type == "B":
                    model = orjson.loads(data)["model"]
                    self.backend.handle_event(model, MessageType.DATA)
                    self.debug_print("Model data sent to the backend")

                elif message_type == "R":
                    self.python_client = ws
                    self.javascript_client.send(data)
                    self.debug_print("Backend response received.", data)

        except ConnectionClosed:
            self.debug_print("Client disconnected")
            pass

        except Exception as e:
            print("Error:", e)
