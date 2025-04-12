"""Configuration of the viewer"""

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

import os

if os.environ.get("JUPYTER_CADQUERY") is None:
    from ocp_vscode.comms import send_command, send_config, get_port, is_pytest

    is_jupyter_cadquery = False
else:
    from jupyter_cadquery.comms import send_config, send_command

    is_pytest = lambda: False

    is_jupyter_cadquery = True

from ocp_tessellate.utils import Color

from enum import Enum


__all__ = [
    "workspace_config",
    "combined_config",
    "set_viewer_config",
    "set_defaults",
    "reset_defaults",
    "get_default",
    "get_defaults",
    "status",
    "Camera",
    "Collapse",
    "check_deprecated",
]


class Camera(Enum):
    """Camera reset modes"""

    RESET = "reset"
    CENTER = "center"
    KEEP = "keep"


class Collapse(Enum):
    """Collapse modes for the CAD navigation tree"""

    NONE = 0
    LEAVES = 1
    ALL = 2
    ROOT = 3


COLLAPSE_MAPPING = ["E", "1", "C", "R"]

COLLAPSE_REVERSE_MAPPING = {
    "E": Collapse.NONE,
    "1": Collapse.LEAVES,
    "C": Collapse.ALL,
    "R": Collapse.ROOT,
}

CONFIG_UI_KEYS = [
    "axes",
    "axes0",
    "black_edges",
    "grid",
    "ortho",
    "transparent",
    "explode",
    "ambient_intensity",
    "direct_intensity",
    "metalness",
    "roughness",
    "clip_slider_0",
    "clip_slider_1",
    "clip_slider_2",
    "clip_normal_0",
    "clip_normal_1",
    "clip_normal_2",
    "clip_planes",
    "clip_intersection",
    "clip_object_colors",
]

CONFIG_WORKSPACE_KEYS = CONFIG_UI_KEYS + [
    # viewer
    "collapse",
    "dark",
    "glass",
    "orbit_control",
    "ticks",
    "center_grid",
    "tools",
    "tree_width",
    "up",
    # mouse
    "pan_speed",
    "rotate_speed",
    "zoom_speed",
    # render settings
    "ambient_intensity",
    "direct_intensity",
    "metalness",
    "roughness",
    "angular_tolerance",
    "default_color",
    "default_edgecolor",
    "default_facecolor",
    "default_thickedgecolor",
    "default_vertexcolor",
    "default_opacity",
    "deviation",
    "modifier_keys",
]

CONFIG_CONTROL_KEYS = [
    "edge_accuracy",
    "debug",
    "helper_scale",
    "render_edges",
    "render_mates",
    "render_joints",
    "render_normals",
    "reset_camera",
    "show_parent",
    "show_sketch_local",
    "timeit",
]

CONFIG_KEYS = CONFIG_WORKSPACE_KEYS + CONFIG_CONTROL_KEYS + ["zoom"]

CONFIG_SET_KEYS = [
    "axes",
    "axes0",
    "grid",
    "center_grid",
    "ortho",
    "transparent",
    "black_edges",
    "explode",
    "zoom",
    "position",
    "quaternion",
    "target",
    "default_edgecolor",
    "default_opacity",
    "ambient_intensity",
    "direct_intensity",
    "metalness",
    "roughness",
    "zoom_speed",
    "pan_speed",
    "rotate_speed",
    "glass",
    "tools",
    "tree_width",
    "collapse",
    # "tab",
    # "clip_slider_0",
    # "clip_slider_1",
    # "clip_slider_2",
    # "clip_normal_0",
    # "clip_normal_1",
    # "clip_normal_2",
    # "clip_intersection",
    # "clip_planes",
    # "clip_object_colors",
]

DEFAULTS = {
    "render_edges": True,
    "render_normals": False,
    "render_mates": False,
    "render_joints": False,
    "helper_scale": 1.0,
    "show_parent": False,
    "show_sketch_local": True,
    "timeit": False,
    "collapse": Collapse.ROOT,
    "debug": False,
}


# pylint: disable=too-many-arguments,unused-argument,too-many-locals
def set_viewer_config(
    axes=None,
    axes0=None,
    grid=None,
    center_grid=None,
    ortho=None,
    transparent=None,
    black_edges=None,
    explode=None,
    zoom=None,
    position=None,
    quaternion=None,
    target=None,
    default_edgecolor=None,
    default_opacity=None,
    ambient_intensity=None,
    direct_intensity=None,
    metalness=None,
    roughness=None,
    zoom_speed=None,
    pan_speed=None,
    rotate_speed=None,
    glass=None,
    tools=None,
    tree_width=None,
    collapse=None,
    reset_camera=None,
    states=None,
    tab=None,
    clip_slider_0=None,
    clip_slider_1=None,
    clip_slider_2=None,
    clip_normal_0=None,
    clip_normal_1=None,
    clip_normal_2=None,
    clip_intersection=None,
    clip_planes=None,
    clip_object_colors=None,
    port=None,
    viewer=None,
):
    """Set viewer config"""
    if not is_jupyter_cadquery and port is None:
        port = get_port()

    config = {k: v for k, v in locals().items() if v is not None}

    if config.get("collapse") is not None:
        config["collapse"] = COLLAPSE_MAPPING[config["collapse"].value]
    if config.get("default_edgecolor") is not None:
        config["default_edgecolor"] = Color(config["default_edgecolor"]).web_color

    data = {
        "type": "ui",
        "config": config,
    }

    try:
        send_config(data, port=port, title=viewer)

    except Exception as ex:
        raise RuntimeError(
            "Cannot set viewer config. Is the viewer running?\n" + str(ex.args)
        ) from ex


def get_default(key):
    """Get default value for key"""
    return get_defaults().get(key)


def get_defaults():
    """Get all defaults"""
    result = dict(workspace_config())
    result.update(DEFAULTS)
    return result


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
    center_grid=None,
    up=None,
    explode=None,
    zoom=None,
    reset_camera=None,
    clip_slider_0=None,
    clip_slider_1=None,
    clip_slider_2=None,
    clip_normal_0=None,
    clip_normal_1=None,
    clip_normal_2=None,
    clip_intersection=None,
    clip_planes=None,
    clip_object_colors=None,
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
    metalness=None,
    roughness=None,
    render_edges=None,
    render_normals=None,
    render_mates=None,
    render_joints=None,
    show_parent=None,
    show_sketch_local=None,
    helper_scale=None,
    mate_scale=None,  # DEPRECATED
    debug=None,
    timeit=None,
    # Jupyter CadQuery
    viewer=None,
    cad_width=None,
    height=None,
):
    # pylint: disable=line-too-long
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
        collapse:          Collapse.LEAVES: collapse all single leaf nodes,
                           Collapse.ROOT: expand root only,
                           Collapse.ALL: collapse all nodes,
                           Collapse.NONE: expand all nodes
                           (default=Collapse.ROOT)
        ticks:             Hint for the number of ticks in both directions (default=10)
        center_grid:       Center the grid at the origin or center of mass (default=False)
        up:                Use z-axis ('Z') or y-axis ('Y') as up direction for the camera (default="Z")
        explode:           Turn on explode mode (default=False)

        zoom:              Zoom factor of view (default=1.0)
        position:          Camera position
        quaternion:        Camera orientation as quaternion
        target:            Camera look at target
        reset_camera:      Camera.RESET: Reset camera position, rotation, zoom and target
                           Camera.CENTER: Keep camera position, rotation, zoom, but look at center
                           Camera.KEEP: Keep camera position, rotation, zoom, and target
                           (default=Camera.RESET)
        clip_slider_0:     Setting of clipping slider 0 (default=None)
        clip_slider_1:     Setting of clipping slider 1 (default=None)
        clip_slider_2:     Setting of clipping slider 2 (default=None)
        clip_normal_0:     Setting of clipping normal 0 (default=[-1,0,0])
        clip_normal_1:     Setting of clipping normal 1 (default=[0,-1,0])
        clip_normal_2:     Setting of clipping normal 2 (default=[0,0,-1])
        clip_intersection: Use clipping intersection mode (default=[False])
        clip_planes:       Show clipping plane helpers (default=False)
        clip_object_colors: Use object color for clipping caps (default=False)

        pan_speed:         Speed of mouse panning (default=1)
        rotate_speed:      Speed of mouse rotate (default=1)
        zoom_speed:        Speed of mouse zoom (default=1)

    - Renderer
        deviation:         Shapes: Deviation from linear deflection value (default=0.1)
        angular_tolerance: Shapes: Angular deflection in radians for tessellation (default=0.2)
        edge_accuracy:     Edges: Precision of edge discretization (default: mesh quality / 100)

        default_color:     Default mesh color (default=(232, 176, 36))
        default_edgecolor: Default mesh color (default=(128, 128, 128))
        ambient_intensity: Intensity of ambient light (default=1.00)
        direct_intensity:  Intensity of direct light (default=1.10)
        metalness:         Metalness property of the default material (default=0.30)
        roughness:         Roughness property of the default material (default=0.65)

        render_edges:      Render edges  (default=True)
        render_normals:    Render normals (default=False)
        render_mates:      Render mates for MAssemblies (default=False)
        render_joints:     Render mates for MAssemblies (default=False)
        show_parent:       Render parent of faces, edges or vertices as wireframe (default=False)
        show_sketch_local: In build123d show local sketch in addition to relocate sketch (default=True)
        helper_scale:      Scale of rendered helpers (locations, axis, mates for MAssemblies) (default=1)

    - Debug
        debug:             Show debug statements to the VS Code browser console (default=False)
        timeit:            Show timing information from level 0-3 (default=False)

    - Jupyter Cadquery only:
        viewer:            The title of the sidecar in Jupyter CadQuery
        cad_width:         The viewer width in  Jupyter CadQuery
        height:            The viewer height in  Jupyter CadQuery
    """

    kwargs = {k: v for k, v in locals().items() if v is not None}

    kwargs = check_deprecated(kwargs)

    for key, value in kwargs.items():
        if key in CONFIG_KEYS or (
            is_jupyter_cadquery and key in ["viewer", "cad_width", "height"]
        ):
            DEFAULTS[key] = value
        else:
            print(f"'{key}' is an unkown config, ignored!")

    set_viewer_config(
        viewer=viewer, **{k: v for k, v in kwargs.items() if k in CONFIG_SET_KEYS}
    )


def preset(key, value):
    """Set default value for key"""
    return get_default(key) if value is None else value


def ui_filter(conf):
    """Filter out all non-UI keys from the config dict"""
    return {k: v for k, v in conf.items() if k in CONFIG_UI_KEYS}


def workspace_filter(conf):
    """Filter out all non-workspace keys from the config dict"""
    return {k: v for k, v in conf.items() if k in CONFIG_WORKSPACE_KEYS}


def status(port=None, viewer=None, debug=False):
    """Get viewer status"""

    if is_pytest():
        return {}

    if not is_jupyter_cadquery and port is None:
        port = get_port()
    try:
        response = send_command("status", port=port, title=viewer)
        if debug:
            return response.get("_debugStarted", False)
        else:
            if response.get("collapse") is not None:
                response["collapse"] = COLLAPSE_REVERSE_MAPPING[response["collapse"]]
            return dict(sorted(response.items()))

    except Exception as ex:
        raise RuntimeError(
            "Cannot access viewer status. Is the viewer running?\n" + str(ex.args)
        ) from ex


def workspace_config(port=None, viewer=None):
    """Get viewer workspace config"""

    if is_pytest():
        return {
            "_splash": False,
            "default_facecolor": (1, 234, 56),
            "default_thickedgecolor": (123, 45, 6),
            "default_vertexcolor": (123, 45, 6),
        }

    if not is_jupyter_cadquery and port is None:
        port = get_port()
    try:
        conf = send_command("config", port=port, title=viewer)
        mapping = {
            "none": Collapse.NONE,
            "leaves": Collapse.LEAVES,
            "all": Collapse.ALL,
            "root": Collapse.ROOT,
            "E": Collapse.NONE,
            "1": Collapse.LEAVES,
            "C": Collapse.ALL,
            "R": Collapse.ROOT,
        }
        if isinstance(conf.get("collapse"), str):
            conf["collapse"] = mapping[conf.get("collapse", "R")]
        if isinstance(conf.get("reset_camera"), str):
            conf["reset_camera"] = Camera[conf.get("reset_camera", "RESET").upper()]
        return dict(conf)

    except Exception as ex:
        raise RuntimeError(
            "Cannot access viewer config. Is the viewer running?\n" + str(ex.args)
        ) from ex


def combined_config(port=None, viewer=None):
    """Get combined config from workspace and status"""

    if not is_jupyter_cadquery and port is None:
        port = get_port()

    try:
        wspace_config = workspace_config(port=port, viewer=viewer)
        wspace_status = status(port=port, viewer=viewer)

    except Exception as ex:
        raise RuntimeError(
            "Cannot access viewer config. Is the viewer running?\n" + str(ex.args)
        ) from ex

    use_status = not wspace_config.get("_splash", False)

    wspace_config.update(DEFAULTS)

    if use_status:
        wspace_config.update(workspace_filter(wspace_status))
    return dict(sorted(wspace_config.items()))


def get_changed_config(key=None):
    """Get changed config from workspace and status"""
    wspace_config = workspace_config()
    wspace_config.update(DEFAULTS)
    if key is None:
        return wspace_config
    else:
        return wspace_config.get(key)


def reset_defaults():
    """Reset defaults not given in workspace config"""
    global DEFAULTS  # pylint: disable=global-statement

    config = {
        key: value
        for key, value in workspace_config().items()
        if key in CONFIG_SET_KEYS
    }
    config["reset_camera"] = Camera.RESET

    set_viewer_config(**config)

    if config.get("transparent") is not None:
        set_viewer_config(transparent=config["transparent"])

    DEFAULTS = {
        "render_edges": True,
        "render_normals": False,
        "render_mates": False,
        "render_joints": False,
        "helper_scale": 1.0,
        "show_parent": False,
        "show_sketch_local": True,
        "timeit": False,
        "collapse": Collapse.ROOT,
        "debug": False,
        # "reset_camera": Camera.RESET,
    }


def check_deprecated(kwargs):
    """Check for deprecated arguments"""
    if kwargs.get("mate_scale") is not None:
        print("\nmate_scale is deprecated, use helper_scale instead\n")
        kwargs["helper_scale"] = kwargs["mate_scale"]
        del kwargs["mate_scale"]

    if kwargs.get("reset_camera") is True:
        print(
            "\n'reset_camera=True' is deprecated, use 'reset_camera=Camera.RESET' instead\n"
        )
        kwargs["reset_camera"] = Camera.RESET

    if kwargs.get("reset_camera") is False:
        print(
            "\n'reset_camera=False' is deprecated, use 'reset_camera=Camera.CENTER' instead\n"
        )
        kwargs["reset_camera"] = Camera.CENTER

    if kwargs.get("collapse") == "C":
        print("\n'collapse=\"C\"' is deprecated, use 'collapse=Collapse.ALL' instead\n")
        kwargs["collapse"] = Collapse.ALL

    if kwargs.get("collapse") == "1" or kwargs.get("collapse") == 1:
        print(
            "\n'collapse=\"1\"' is deprecated, use 'collapse=Collapse.LEAVES' instead\n"
        )
        kwargs["collapse"] = Collapse.LEAVES

    if kwargs.get("collapse") == "R":
        print(
            "\n'collapse=\"R\"' is deprecated, use 'collapse=Collapse.ROOT' instead\n"
        )
        kwargs["collapse"] = Collapse.ROOT

    if kwargs.get("collapse") == "E":
        print(
            "\n'collapse=\"E\"' is deprecated, use 'collapse=Collapse.NONE' instead\n"
        )
        kwargs["collapse"] = Collapse.NONE

    if kwargs.get("control") is not None:
        print(
            "\n'control=\"orbit\" or \"trackball\"' is deprecated, use 'orbit_control=True' or 'False' instead\n"
        )
        kwargs["orbit_control"] = kwargs["control"] == "orbit"

    return kwargs
