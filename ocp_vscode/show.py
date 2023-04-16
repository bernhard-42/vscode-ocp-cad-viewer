#
# Copyright 2022 Bernhard Walter
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

from ocp_tessellate import PartGroup
from ocp_tessellate.convert import (
    tessellate_group,
    get_normal_len,
    combined_bb,
    to_assembly,
    mp_get_results,
)
from ocp_tessellate.utils import numpy_to_buffer_json, Timer, Color
from ocp_tessellate.mp_tessellator import init_pool, keymap, close_pool
from ocp_tessellate.cad_objects import OCP_PartGroup

CMD_URL = "http://127.0.0.1"
CMD_PORT = 3939
REQUEST_TIMEOUT = 2000

OBJECTS = {"objs": [], "names": [], "colors": [], "alphas": []}

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

CONFIG_KEYS = CONFIG_WORKSPACE_KEYS + CONFIG_CONTROL_KEYS

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
DEFAULTS = {}


def set_port(port):
    global CMD_PORT
    CMD_PORT = port


def _send(data, port=None, timeit=False):
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
    print(data)
    _send(data)


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
    position=None,
    quaternion=None,
    target=None,
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
    debug=False,
    timeit=False,
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
        if key in CONFIG_SET_KEYS:
            set_viewer_config(key, value)

        elif key in CONFIG_KEYS:
            DEFAULTS[key] = value

        else:
            print(f"'{key}' is an unkown config, ignored!")


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

    print(config)
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


def _tessellate(
    *cad_objs, names=None, colors=None, alphas=None, progress=None, **kwargs
):
    timeit = preset("timeit", kwargs.get("timeit"))

    if progress is None:
        progress = Progress([c for c in "-+c"])

    with Timer(timeit, "", "to_assembly", 1):
        part_group = to_assembly(
            *cad_objs,
            names=names,
            colors=colors,
            alphas=alphas,
            render_mates=kwargs.get("render_mates", get_changed_config("render_mates")),
            mate_scale=kwargs.get("mate_scale", get_changed_config("mate_scale")),
            default_color=kwargs.get(
                "default_color", get_changed_config("default_color")
            ),
            show_parent=kwargs.get("show_parent", get_changed_config("show_parent")),
            progress=progress,
        )

        if len(part_group.objects) == 1 and isinstance(
            part_group.objects[0], PartGroup
        ):
            part_group = part_group.objects[0]

    # Do not send defaults for postion, rotation and zoom unless they are set in kwargs
    if workspace_config().get("_splash"):
        conf = combined_config(use_status=False)
    else:
        conf = combined_config(use_status=True)

    params = {
        k: v
        for k, v in conf.items()
        if not k
        in (
            "position",
            "rotation",
            "zoom",
            "target",
            # controlled by VSCode panel size
            "cad_width",
            "height",
            # controlled by VSCode settings
            "tree_width",
            "theme",
        )
    }

    for k, v in kwargs.items():
        if k in ["cad_width", "height"]:
            print(
                f"Setting {k} cannot be set, it is determined by the VSCode panel size"
            )

        elif k in [
            "tree_width",
            "theme",
        ]:
            print(f"Setting {k} can only be set in VSCode config")

        elif v is not None:
            params[k] = v

    parallel = preset("parallel", params.get("parallel"))
    if parallel and not any(
        [isinstance(obj, OCP_PartGroup) for obj in part_group.objects]
    ):
        print("parallel only works for assemblies, setting it to False")
        parallel = False
        params["parallel"] = False

    if kwargs.get("debug") is not None and kwargs["debug"]:
        print("\ntessellation parameters:\n", params)

    with Timer(timeit, "", "tessellate", 1):
        if parallel:
            init_pool()
            keymap.reset()

        instances, shapes, states = tessellate_group(
            part_group, params, progress, params.get("timeit")
        )

        if parallel:
            instances, shapes = mp_get_results(instances, shapes, progress)
            close_pool()

    params["normal_len"] = get_normal_len(
        preset("render_normals", params.get("render_normals")),
        shapes,
        preset("deviation", params.get("deviation")),
    )

    with Timer(timeit, "", "bb", 1):
        bb = combined_bb(shapes).to_dict()

    # add global bounding box
    shapes["bb"] = bb
    return instances, shapes, states, params, part_group.count_shapes()


def _convert(*cad_objs, names=None, colors=None, alphas=None, progress=None, **kwargs):
    timeit = preset("timeit", kwargs.get("timeit"))

    if progress is None:
        progress = Progress([c for c in "-+c"])

    instances, shapes, states, config, count_shapes = _tessellate(
        *cad_objs,
        names=names,
        colors=colors,
        alphas=alphas,
        progress=progress,
        **kwargs,
    )
    if config.get("dark") is not None:
        config["theme"] = "dark"
    elif config.get("orbit_control") is not None:
        config["control"] = "orbit" if config["control"] else "trackball"
    elif config.get("collapse") is not None:
        mapping = {"1": 1, "E": 0, "C": 2}
        config["collapse"] = mapping.get(config["collapse"], 1)

    if config.get("debug") is not None and config["debug"]:
        print("\nconfig:\n", config)

    with Timer(timeit, "", "create data obj", 1):
        data = {
            "data": numpy_to_buffer_json(
                dict(instances=instances, shapes=shapes, states=states)
            ),
            "type": "data",
            "config": config,
            "count": count_shapes,
        }

    return data


class Progress:
    def __init__(self, levels=None):
        if levels is None:
            self.levels = ["+", "c", "-"]
        else:
            self.levels = levels

    def update(self, mark="+"):
        if mark in self.levels:
            print(mark, end="", flush=True)


def show(
    *cad_objs,
    names=None,
    colors=None,
    alphas=None,
    port=None,
    progress="-+c",
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
    position=None,
    quaternion=None,
    target=None,
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
    debug=False,
    timeit=False,
):
    """Show CAD objects in Visual Studio Code
    Parameters
        cad_objs:          All cad objects that should be shown as positional parameters

    Keywords for show:
        names:             List of names for the cad_objs. Needs to have the same length as cad_objs
        colors:            List of colors for the cad_objs. Needs to have the same length as cad_objs
        alphas:            List of alpha values for the cad_objs. Needs to have the same length as cad_objs
        port:              The port the viewer listens to. Typically use 'set_port(port)' instead
        progress:          Show progress of tessellation with None is no progress indicator. (default="-+c")
                           for object: "-": is reference, "+": gets tessellated, "c": from cache

    Valid keywords to configure the viewer (**kwargs):
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

    timeit = preset("timeit", timeit)

    if names is not None and len(names) != len(cad_objs):
        raise ValueError("Length of cad objects and names need to be the same")

    if colors is not None and len(colors) != len(cad_objs):
        raise ValueError("Length of cad objects and colors need to be the same")

    if alphas is not None and len(alphas) != len(cad_objs):
        raise ValueError("Length of cad objects and alphas need to be the same")

    if default_edgecolor is not None:
        default_edgecolor = Color(default_edgecolor).web_color

    kwargs = {
        k: v
        for k, v in locals().items()
        if v is not None
        and k not in ["cad_objs", "names", "colors", "alphas", "port", "progress"]
    }

    progress = Progress([] if progress is None else [c for c in progress])

    with Timer(timeit, "", "overall"):
        data = _convert(
            *cad_objs,
            names=names,
            colors=colors,
            alphas=alphas,
            progress=progress,
            **kwargs,
        )

    with Timer(timeit, "", "send"):
        return _send(data, port=port, timeit=timeit)


def reset_show():
    global OBJECTS

    OBJECTS = {"objs": [], "names": [], "colors": [], "alphas": []}


def show_object(
    obj,
    name=None,
    options=None,
    parent=None,
    clear=False,
    port=None,
    progress="-+c",
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
    position=None,
    quaternion=None,
    target=None,
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
    debug=False,
    timeit=False,
):
    """Incrementally show CAD objects in Visual Studio Code

    Parameters:
        obj:              The CAD object to be shown

    Keywords for show_object:
        name:              The name of the CAD object
        options:           A dict of color and alpha value: {"alpha":0.5, "color": (64, 164, 223)}
                           0 <= alpha <= 1.0 and color is a 3-tuple of values between 0 and 255
        parent:            Add another object, usually the parent of e.g. edges or vertices with alpha=0.25
        clear:             In interactice mode, clear the stack of objects to be shown
                           (typically used for the first object)
        port:              The port the viewer listens to. Typically use 'set_port(port)' instead
        progress:          Show progress of tessellation with None is no progress indicator. (default="-+c")
                           for object: "-": is reference, "+": gets tessellated, "c": from cache

    Valid keywords to configure the viewer (**kwargs):
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
        imeit:             Show timing information from level 0-3 (default=False)
    """

    kwargs = {
        k: v
        for k, v in locals().items()
        if v is not None
        and k not in ["obj", "name", "options", "parent", "clear", "port", "progress"]
    }

    global OBJECTS

    if clear:
        reset_show()

    if parent is not None:
        OBJECTS["objs"].append(parent)
        OBJECTS["names"].append("parent")
        OBJECTS["colors"].append(get_default("default_color"))
        OBJECTS["alphas"].append(0.25)

    if options is None:
        color = None
        alpha = 1.0
    else:
        color = options.get("color")
        alpha = options.get("alpha", 1.0)

    OBJECTS["objs"].append(obj)
    OBJECTS["names"].append(name)
    OBJECTS["colors"].append(color)
    OBJECTS["alphas"].append(alpha)

    prefix = f"{name} " if name is not None else ""

    print(f"\nshow_object {prefix}<{obj}>")
    show(
        *OBJECTS["objs"],
        names=OBJECTS["names"],
        colors=OBJECTS["colors"],
        alphas=OBJECTS["alphas"],
        port=port,
        progress=progress,
        **kwargs,
    )
