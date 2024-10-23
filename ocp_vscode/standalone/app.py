import click
import orjson
from flask import Flask, render_template
from flask_sock import Sock
from simple_websocket import ConnectionClosed
from ocp_vscode.backend import ViewerBackend
from ocp_vscode.backend_logo import logo
from ocp_vscode.comms import MessageType


DEBUG = True

app = Flask(__name__)
sock = Sock(app)
backend = None


def config():
    return {"_splash": splash}


def debug_print(*msg):
    if DEBUG:
        print("Debug:", *msg)


python_client = None
javascript_client = None

config = {
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
status = {}
splash = True
port = None


@app.route("/viewer")
def index():
    return render_template("viewer.html", port=port, **config)


@sock.route("/")
def handle_message(ws):
    global python_client, javascript_client, config, status, splash

    try:
        while True:
            data = ws.receive()
            if isinstance(data, bytes):
                data = data.decode("utf-8")

            message_type = data[0]
            data = data[2:]

            if message_type == "C":
                python_client = ws
                cmd = orjson.loads(data)
                if cmd == "status":
                    debug_print("Received status command")
                    python_client.send(orjson.dumps({"text": status}))
                elif cmd == "config":
                    debug_print("Received config command")
                    config["_splash"] = splash
                    python_client.send(orjson.dumps(config))
                elif cmd.type == "screenshot":
                    debug_print("Received screenshot command")
                    python_client(orjson.dumps(cmd))

            elif message_type == "D":
                python_client = ws
                debug_print("Received a new model")
                javascript_client.send(data)
                if splash:
                    splash = False

            elif message_type == "U":
                javascript_client = ws
                debug_print("Received incremental UI changes")
                changes = orjson.loads(data)["text"]
                for key, value in changes.items():
                    status[key] = value
                backend.handle_event(changes, MessageType.UPDATES)

            elif message_type == "S":
                python_client = ws
                debug_print("Received a config")
                javascript_client.send(data)
                debug_print("Posted config to view")

            elif message_type == "L":
                javascript_client = ws
                debug_print("Javascript listener registered", data)

            elif message_type == "B":
                model = orjson.loads(data)["model"]
                backend.handle_event(model, MessageType.DATA)
                debug_print("Model data sent to the backend")

            elif message_type == "R":
                python_client = ws
                javascript_client.send(data)
                debug_print("Backend response received.", data)

            # if message_type == "C" and not (
            #     isinstance(data, dict) and data["type"] == "screenshot"
            # ):
            #     ws.send(orjson.dumps({}))

    except ConnectionClosed:
        debug_print("Client disconnected")
        pass

    except Exception as e:
        print("Error:", e)


def to_camel(s):
    parts = s.split("_")
    return parts[0] + "".join(x.title() for x in parts[1:])


@click.command()
@click.option(
    "--port",
    default=3939,
    help="The port where OCP CAD Viewer will start",
)
@click.option(
    "--debug",
    default=False,
    help="Show debugging information",
)
@click.option(
    "--tree_width",
    default=240,
    help="OCP CAD Viewer navigation tree width (default: 240)",
)
@click.option(
    "--glass",
    default=True,
    help="Use glass mode with transparent navigation tree (default: True)",
)
@click.option(
    "--theme",
    default="light",
    help="Use theme 'light' or 'dark' (default: 'light')",
)
@click.option(
    "--tools",
    default=True,
    help="Show toolbar (default: True)",
)
@click.option(
    "--tree_width", default=240, help="Width of the CAD navigation tree (default: 240)"
)
@click.option(
    "--new_tree_behavior",
    default=True,
    help="With the new behaviour the eye controls both icons, the mesh icon only the mesh behavior (default: True)",
)
@click.option(
    "--dark",
    default=False,
    help="Use dark mode (default: False)",
)
@click.option(
    "--orbit_control",
    default=False,
    help="Use 'orbit' control mode instead of 'trackball' (default: False)",
)
@click.option(
    "--up",
    default="Z",
    help="Provides up direction, 'Z', 'Y' or 'L' (legacy) (default: Z)",
)
@click.option(
    "--rotate_speed",
    default=1,
    help="Rotation speed (default: 1)",
)
@click.option(
    "--zoom_speed",
    default=1,
    help="Zoom speed (default: 1)",
)
@click.option(
    "--pan_speed",
    default=1,
    help="Pan speed (default: 1)",
)
@click.option(
    "--axes",
    default=False,
    help="Show axes (default: False)",
)
@click.option(
    "--axes0",
    default=True,
    help="Show axes at the origin (0, 0, 0) (default: True)",
)
@click.option(
    "--black_edges",
    default=False,
    help="Show edges in black (default: False)",
)
@click.option(
    "--grid_XY",
    default=False,
    help="Show grid on XY plane (default: False)",
)
@click.option(
    "--grid_YZ",
    default=False,
    help="Show grid on YZ plane (default: False)",
)
@click.option(
    "--grid_XZ",
    default=False,
    help="Show grid on XZ plane (default: False)",
)
@click.option(
    "--center_grid",
    default=False,
    help="Show grid planes crossing at center of object or global origin(default: False)",
)
@click.option(
    "--collapse",
    default=1,
    help="leaves: collapse all leaf nodes, all: collapse all nodes, none: expand all nodes, root: expand root only (default: leaves)",
)
@click.option(
    "--ortho",
    default=True,
    help="Use orthographic camera (default: True)",
)
@click.option(
    "--ticks",
    default=10,
    help="Default number of ticks (default: 10)",
)
@click.option(
    "--transparent",
    default=False,
    help="Show objects transparent (default: False)",
)
@click.option(
    "--default_opacity",
    default=0.5,
    help="Default opacity for transparent objects (default: 0.5)",
)
@click.option(
    "--explode",
    default=False,
    help="Turn explode mode on (default: False)",
)
@click.option(
    "--modifier_keys",
    default="{'shift': 'shiftKey', 'ctrl': 'ctrlKey', 'meta': 'metaKey'}",
    help="Mapping of modifier keys shift, ctrl and meta (cmd on Mac, Windows on Windows)",
)
@click.option(
    "--angular_tolerance",
    default=0.2,
    help="Angular tolerance for tessellation algorithm (default: 0.2)",
)
@click.option(
    "--deviation",
    default=0.1,
    help="Deviation of for tessellation algorithm (default: 0.1)",
)
@click.option(
    "--default_color",
    default="#e8b024",
    help="Default shape color, CSS3 color names are allowed (default: #e8b024)",
)
@click.option(
    "--default_edgecolor",
    default="#707070",
    help="Default color of the edges of shapes, CSS3 color names are allowed (default: #707070)",
)
@click.option(
    "--default_thickedgecolor",
    default="MediumOrchid",
    help="Default color of lines, CSS3 color names are allowed (default: MediumOrchid)",
)
@click.option(
    "--default_facecolor",
    default="Violet",
    help="Default color of faces, CSS3 color names are allowed (default: Violet)",
)
@click.option(
    "--default_vertexcolor",
    default="MediumOrchid",
    help="Default color of vertices, CSS3 color names are allowed (default: MediumOrchid)",
)
@click.option(
    "--ambient_intensity",
    default=1,
    help="Intensity of ambient light (default: 1.00)",
)
@click.option(
    "--direct_intensity",
    default=1.1,
    help="Intensity of direct light (default: 1.10)",
)
@click.option(
    "--metalness",
    default=0.3,
    help="Metalness property of material (default: 0.30)",
)
@click.option(
    "--roughness",
    default=0.65,
    help="Roughness property of material (default: 0.65)",
)
def main(*args, **kwargs):
    global port, backend

    for k, v in kwargs.items():
        if k == "port":
            port = v
        elif k not in []:
            if k == "collapse":
                v = str(v)
            config[k] = v

    backend = ViewerBackend(kwargs["port"])
    backend.load_model(logo)
    print("Viewer backend initialized")
    app.run(debug=True, port=kwargs["port"])
    sock.init_app(app)


if __name__ == "__main__":
    main()
