#
# Copyright 2023 Bernhard Walter
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
#

import requests
import orjson as json
from ocp_tessellate.utils import Timer


CONFIG_UI_KEYS = [
    "axes",
    "axes0",
    "black_edges",
    "grid",
    "ortho",
    "transparent",
]

CONFIG_WORKSPACE_KEYS = CONFIG_UI_KEYS + [
    # viewer
    "collapse",
    "dark",
    "glass",
    "orbit_control",
    "ticks",
    "tools",
    "tree_width",
    "up",
    # mouse
    "pan_speed",
    "rotate_speed",
    "zoom_speed",
    # render settings
    "ambient_intensity",
    "angular_tolerance",
    "default_color",
    "default_edgecolor",
    "default_opacity",
    "deviation",
    "direct_intensity",
]

CONFIG_CONTROL_KEYS = [
    "edge_accuracy",
    "debug",
    "mate_scale",
    "render_edges",
    "render_mates",
    "render_normals",
    "reset_camera",
    "timeit",
]

CONFIG_KEYS = CONFIG_WORKSPACE_KEYS + CONFIG_CONTROL_KEYS + ["zoom"]

CONFIG_SET_KEYS = [
    "axes",
    "axes0",
    "grid",
    "ortho",
    "transparent",
    "black_edges",
    "zoom",
    "position",
    "quaternion",
    "target",
    "default_edgecolor",
    "default_opacity",
    "ambient_intensity",
    "direct_intensity",
    "zoom_speed",
    "pan_speed",
    "rotate_speed",
    "reset_camera",
    "glass",
    "tools",
    "tree_width",
    "collapse",
]

DEFAULTS = {
    "render_edges": True,
    "render_normals": False,
    "render_mates": False,
    "mate_scale": 1.0,
    "timeit": False,
    "reset_camera": True,
    "debug": False,
}

CMD_URL = "http://127.0.0.1"
CMD_PORT = 3939
REQUEST_TIMEOUT = 2000


def set_port(port):
    global CMD_PORT
    CMD_PORT = port


def send(data, port=None, timeit=False):
    if data.get("config") is not None and data["config"].get("collapse") is not None:
        data["config"]["collapse"] = str(data["config"]["collapse"])

    if port is None:
        port = CMD_PORT
    try:
        with Timer(timeit, "", "json dumps", 1):
            j = json.dumps(data)

        with Timer(timeit, "", "http send", 1):
            r = requests.post(f"{CMD_URL}:{port}", data=j)

    except Exception as ex:
        print("Cannot connect to viewer, is it running and the right port provided?")
        return

    if r.status_code != 201:
        print("Error", r.text)


def set_viewer_config(
    axes=None,
    axes0=None,
    grid=None,
    ortho=None,
    transparent=None,
    black_edges=None,
    zoom=None,
    position=None,
    quaternion=None,
    target=None,
    default_edgecolor=None,
    default_opacity=None,
    ambient_intensity=None,
    direct_intensity=None,
    zoom_speed=None,
    pan_speed=None,
    rotate_speed=None,
    glass=None,
    tools=None,
    tree_width=None,
    collapse=None,
    reset_camera=None,
):
    config = {k: v for k, v in locals().items() if v is not None}
    data = {
        "type": "ui",
        "config": config,
    }
    send(data)


def get_default(key):
    return DEFAULTS.get(key)


def get_defaults():
    return DEFAULTS


def set_defaults(
    glass=None,
    tools=None,
    tree_width=None,
    axes=None,
    axes0=None,
    grid=None,
    ortho=None,
    transparent=None,
    default_opacity=None,
    black_edges=None,
    orbit_control=None,
    collapse=None,
    ticks=None,
    up=None,
    zoom=None,
    reset_camera=None,
    pan_speed=None,
    rotate_speed=None,
    zoom_speed=None,
    deviation=None,
    angular_tolerance=None,
    edge_accuracy=None,
    default_color=None,
    default_edgecolor=None,
    ambient_intensity=None,
    direct_intensity=None,
    render_edges=None,
    render_normals=None,
    render_mates=None,
    mate_scale=None,
    debug=None,
    timeit=None,
):
    """Set viewer defaults
    Keywords to configure the viewer:
    - UI
        glass:             Use glass mode where tree is an overlay over the cad object (default=False)
        tools:             Show tools (default=True)
        tree_width:        Width of the object tree (default=240)

    - Viewer
        axes:              Show axes (default=False)
        axes0:             Show axes at (0,0,0) (default=False)
        grid:              Show grid (default=False)
        ortho:             Use orthographic projections (default=True)
        transparent:       Show objects transparent (default=False)
        default_opacity:   Opacity value for transparent objects (default=0.5)
        black_edges:       Show edges in black color (default=False)
        orbit_control:     Mouse control use "orbit" control instead of "trackball" control (default=False)
        collapse:          1: collapse all leaf nodes, C: collapse all nodes, E: expand all nodes (default=1)
        ticks:             Hint for the number of ticks in both directions (default=10)
        up:                Use z-axis ('Z') or y-axis ('Y') as up direction for the camera (default="Z")

        zoom:              Zoom factor of view (default=1.0)
        position:          Camera position
        quaternion:        Camera orientation as quaternion
        target:            Camera look at target
        reset_camera:      Reset camera position, rotation and zoom to default (default=True)

        pan_speed:         Speed of mouse panning (default=1)
        rotate_speed:      Speed of mouse rotate (default=1)
        zoom_speed:        Speed of mouse zoom (default=1)

    - Renderer
        deviation:         Shapes: Deviation from linear deflection value (default=0.1)
        angular_tolerance: Shapes: Angular deflection in radians for tessellation (default=0.2)
        edge_accuracy:     Edges: Precision of edge discretization (default: mesh quality / 100)

        default_color:     Default mesh color (default=(232, 176, 36))
        default_edgecolor: Default mesh color (default=(128, 128, 128))
        ambient_intensity  Intensity of ambient ligth (default=1.0)
        direct_intensity   Intensity of direct lights (default=0.12)

        render_edges:      Render edges  (default=True)
        render_normals:    Render normals (default=False)
        render_mates:      Render mates for MAssemblies (default=False)
        mate_scale:        Scale of rendered mates for MAssemblies (default=1)

    - Debug
        debug:             Show debug statements to the VS Code browser console (default=False)
        timeit:            Show timing information from level 0-3 (default=False)
    """

    kwargs = {k: v for k, v in locals().items() if v is not None}

    global DEFAULTS
    for key, value in kwargs.items():
        if key in CONFIG_KEYS:
            DEFAULTS[key] = value
        else:
            print(f"'{key}' is an unkown config, ignored!")

    set_viewer_config(**{k: v for k, v in kwargs.items() if k in CONFIG_SET_KEYS})


def preset(key, value):
    return get_default(key) if value is None else value


def ui_filter(conf):
    return {k: v for k, v in conf.items() if k in CONFIG_UI_KEYS}


def status(port=None):
    if port is None:
        port = CMD_PORT
    try:
        conf = requests.get(f"{CMD_URL}:{port}/status").json()["text"]
        return conf

    except Exception as ex:
        print("Error: Cannot access viewer status:", ex)


def workspace_config(port=None):
    if port is None:
        port = CMD_PORT
    try:
        return requests.get(f"{CMD_URL}:{port}/config").json()

    except Exception as ex:
        print("Error: Cannot access viewer config:", ex)


def combined_config(port=None, use_status=True):
    if port is None:
        port = CMD_PORT

    try:
        wspace_config = workspace_config(port)
        wspace_status = status(port)

    except Exception as ex:
        print("Error: Cannot access viewer config:", ex)

    if use_status and wspace_config["_splash"]:
        del wspace_config["_splash"]
        wspace_config["axes"] = False
        wspace_config["axes0"] = True
        wspace_config["grid"] = [True, False, False]
        wspace_config["ortho"] = False
        wspace_config["transparent"] = False
        wspace_config["black_edges"] = False

    wspace_config.update(DEFAULTS)
    if use_status:
        wspace_config.update(ui_filter(wspace_status))
    return wspace_config


def get_changed_config(key):
    wspace_config = workspace_config()
    wspace_config.update(DEFAULTS)
    return wspace_config.get(key)


def reset_defaults():
    """Reset defaults not given in workspace config"""
    global DEFAULTS

    config = {
        key: value
        for key, value in workspace_config().items()
        if key in CONFIG_SET_KEYS
    }
    config["reset_camera"] = True

    set_viewer_config(**config)

    if config.get("transparent") is not None:
        set_viewer_config(transparent=config["transparent"])

    DEFAULTS = {
        "render_edges": True,
        "render_normals": False,
        "render_mates": False,
        "mate_scale": 1.0,
        "timeit": False,
        "reset_camera": True,
        "debug": False,
    }
