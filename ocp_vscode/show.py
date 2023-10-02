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
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import resource_tracker

import json
import pickle
import re
import struct

from build123d import Vertex, Edge, Face
from ocp_tessellate import PartGroup
from ocp_tessellate.convert import (
    tessellate_group,
    get_normal_len,
    combined_bb,
    to_assembly,
    mp_get_results,
    is_topods_shape,
    is_build123d_shape,
    is_cadquery,
    is_vector,
)
from ocp_tessellate.utils import numpy_to_buffer_json, Timer, Color, numpy_to_json
from ocp_tessellate.ocp_utils import (
    is_vector,
    is_topods_shape,
    is_topods_compound,
    is_cadquery,
    is_cadquery_assembly,
    is_cadquery_sketch,
    is_build123d,
    is_topods_edge,
    is_topods_face,
    is_topods_vertex,
    is_build123d_assembly,
    is_toploc_location,
)

from ocp_tessellate.mp_tessellator import init_pool, keymap, close_pool
from ocp_tessellate.cad_objects import (
    OCP_PartGroup,
    OCP_Edges,
    OCP_Faces,
    OCP_Part,
    OCP_Vertices,
)
from ocp_tessellate.convert import to_assembly, conv
import ocp_tessellate.convert as oc

from .config import (
    preset,
    get_changed_config,
    workspace_config,
    combined_config,
    get_default,
    status,
    set_viewer_config,
    Camera,
    Collapse,
    check_deprecated,
)
from .comms import send_data, CMD_PORT
from .colors import *

from .persistence import modify_copyreg
from .backend import HEADER_SIZE

__all__ = ["show", "show_object", "reset_show", "show_all", "show_clear"]

OBJECTS = {"objs": [], "names": [], "colors": [], "alphas": []}

FIRST_CALL = True
LAST_CALL = "other"

modify_copyreg()


def _tessellate(
    *cad_objs, names=None, colors=None, alphas=None, progress=None, **kwargs
):
    global FIRST_CALL

    if workspace_config().get("_splash"):
        conf = combined_config(use_status=False)
    else:
        conf = combined_config(use_status=True)
        if FIRST_CALL:
            conf["reset_camera"] = Camera.RESET.value
            FIRST_CALL = False
        else:
            reset_camera = conf.get("reset_camera", Camera.RESET)
            conf["reset_camera"] = reset_camera.value

    collapse = conf.get("collapse", Collapse.LEAVES)
    conf["collapse"] = collapse.value

    if kwargs.get("default_facecolor") is not None:
        oc.FACE_COLOR = Color(kwargs["default_facecolor"]).percentage
        del kwargs["default_facecolor"]
    else:
        oc.FACE_COLOR = Color(conf["default_facecolor"]).percentage

    if kwargs.get("default_thickedgecolor") is not None:
        oc.THICK_EDGE_COLOR = Color(kwargs["default_thickedgecolor"]).percentage
        del kwargs["default_thickedgecolor"]
    else:
        oc.THICK_EDGE_COLOR = Color(conf["default_thickedgecolor"]).percentage

    if kwargs.get("default_vertexcolor") is not None:
        oc.VERTEX_COLOR = Color(kwargs["default_vertexcolor"]).percentage
        del kwargs["default_vertexcolor"]
    else:
        oc.VERTEX_COLOR = Color(conf["default_vertexcolor"]).percentage

    timeit = preset("timeit", kwargs.get("timeit"))

    if timeit is None:
        timeit = False

    if progress is None:
        progress = Progress([c for c in "-+c"])

    with Timer(timeit, "", "to_assembly", 1):
        changed_config = get_changed_config()
        part_group = to_assembly(
            *cad_objs,
            names=names,
            colors=colors,
            alphas=alphas,
            render_mates=kwargs.get("render_mates", changed_config.get("render_mates")),
            render_joints=kwargs.get(
                "render_joints", changed_config.get("render_joints")
            ),
            helper_scale=kwargs.get("helper_scale", changed_config.get("helper_scale")),
            default_color=kwargs.get(
                "default_color", changed_config.get("default_color")
            ),
            show_parent=kwargs.get("show_parent", changed_config.get("show_parent")),
            progress=progress,
        )

        if len(part_group.objects) == 1 and isinstance(
            part_group.objects[0], PartGroup
        ):
            part_group = part_group.objects[0]

    params = {
        k: v
        for k, v in conf.items()
        if not k
        in (
            "position",
            "rotation",
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


def merge_instances(instances, shapes):
    def walk(obj):
        typ = None
        for attr in obj.keys():
            if attr == "parts":
                for part in obj["parts"]:
                    walk(part)

            elif attr == "type":
                typ = obj["type"]

            elif attr == "shape":
                if typ == "shapes":
                    if obj["shape"].get("ref") is not None:
                        ind = obj["shape"]["ref"]
                        obj["shape"] = instances[ind]

    walk(shapes)


def _convert(
    *cad_objs,
    names=None,
    colors=None,
    alphas=None,
    progress=None,
    decode=False,
    **kwargs,
):
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
    if decode:
        merge_instances(instances, shapes)

    if config.get("dark") is not None:
        config["theme"] = "dark"
    elif config.get("orbit_control") is not None:
        config["control"] = "orbit" if config["control"] else "trackball"

    if config.get("debug") is not None and config["debug"]:
        print("\nconfig:\n", config)

    if kwargs.get("explode") is not None:
        config["explode"] = kwargs["explode"]

    with Timer(timeit, "", "create data obj", 1):
        if decode:
            return json.loads(
                numpy_to_json({"data": dict(shapes=shapes, states=states)})
            )
        else:
            return {
                "data": numpy_to_buffer_json(
                    dict(instances=instances, shapes=shapes, states=states)
                ),
                "type": "data",
                "config": config,
                "count": count_shapes,
            }


class Progress:
    def __init__(self, levels=None):
        if levels is None:
            self.levels = ["+", "c", "-"]
        else:
            self.levels = levels

    def update(self, mark="+"):
        if mark in self.levels:
            print(mark, end="", flush=True)


def align_attrs(attr_list, length, default, tag, explode=True):
    if attr_list is None:
        return [None] * length if explode else None
    elif len(attr_list) < length:
        print(f"Too view {tag}, using defaults to fill")
        return list(attr_list) + [default] * (length - len(attr_list))
    elif len(attr_list) > length:
        print(f"Too many {tag}, trimming to length {length}")
        return attr_list[:length]
    else:
        return attr_list


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
    explode=None,
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
    default_facecolor=None,
    default_thickedgecolor=None,
    default_vertexcolor=None,
    ambient_intensity=None,
    direct_intensity=None,
    metalness=None,
    roughness=None,
    render_edges=None,
    render_normals=None,
    render_mates=None,
    render_joints=None,
    show_parent=None,
    parallel=None,
    helper_scale=None,
    mate_scale=None,  # DEPRECATED
    debug=None,
    timeit=None,
    _force_in_debug=False,
):
    """Show CAD objects in Visual Studio Code
    Parameters
        cad_objs:                All cad objects that should be shown as positional parameters

    Keywords for show:
        names:                   List of names for the cad_objs. Needs to have the same length as cad_objs
        colors:                  List of colors for the cad_objs. Needs to have the same length as cad_objs
        alphas:                  List of alpha values for the cad_objs. Needs to have the same length as cad_objs
        port:                    The port the viewer listens to. Typically use 'set_port(port)' instead
        progress:                Show progress of tessellation with None is no progress indicator. (default="-+c")
                                 for object: "-": is reference, "+": gets tessellated, "c": from cache

    Valid keywords to configure the viewer (**kwargs):
    - UI
        glass:                   Use glass mode where tree is an overlay over the cad object (default=False)
        tools:                   Show tools (default=True)
        tree_width:              Width of the object tree (default=240)

    - Viewer
        axes:                    Show axes (default=False)
        axes0:                   Show axes at (0,0,0) (default=False)
        grid:                    Show grid (default=False)
        ortho:                   Use orthographic projections (default=True)
        transparent:             Show objects transparent (default=False)
        default_opacity:         Opacity value for transparent objects (default=0.5)
        black_edges:             Show edges in black color (default=False)
        orbit_control:           Mouse control use "orbit" control instead of "trackball" control (default=False)
        collapse:                Collapse.LEAVES: collapse all single leaf nodes,
                                 Collapse.ROOT: expand root only,
                                 Collapse.ALL: collapse all nodes,
                                 Collapse.NONE: expand all nodes
                                 (default=Collapse.LEAVES)
        ticks:                   Hint for the number of ticks in both directions (default=10)
        up:                      Use z-axis ('Z') or y-axis ('Y') as up direction for the camera (default="Z")
        explode:                 Turn on explode mode (default=False)

        zoom:                    Zoom factor of view (default=1.0)
        position:                Camera position
        quaternion:              Camera orientation as quaternion
        target:                  Camera look at target
        reset_camera:            Camera.RESET: Reset camera position, rotation, toom and target
                                 Camera.CENTER: Keep camera position, rotation, toom, but look at center
                                 Camera.KEEP: Keep camera position, rotation, toom, and target
                                 (default=Camera.RESET)

        pan_speed:               Speed of mouse panning (default=1)
        rotate_speed:            Speed of mouse rotate (default=1)
        zoom_speed:              Speed of mouse zoom (default=1)

    - Renderer
        deviation:               Shapes: Deviation from linear deflection value (default=0.1)
        angular_tolerance:       Shapes: Angular deflection in radians for tessellation (default=0.2)
        edge_accuracy:           Edges: Precision of edge discretization (default: mesh quality / 100)

        default_color:           Default mesh color (default=(232, 176, 36))
        default_edgecolor:       Default color of the edges of a mesh (default=#707070)
        default_facecolor:       Default color of the edges of a mesh (default=#ee82ee)
        default_thickedgecolor:  Default color of the edges of a mesh (default=#ba55d3)
        default_vertexcolor:     Default color of the edges of a mesh (default=#ba55d3)
        ambient_intensity:       Intensity of ambient light (default=1.00)
        direct_intensity:        Intensity of direct light (default=1.10)
        metalness:               Metalness property of the default material (default=0.30)
        roughness:               Roughness property of the default material (default=0.65)

        render_edges:            Render edges  (default=True)
        render_normals:          Render normals (default=False)
        render_mates:            Render mates for MAssemblies (default=False)
        render_joints:           Render build123d joints (default=False)
        parallel:                Tessellate objects in parallel (default=False)
        show_parent:             Render parent of faces, edges or vertices as wireframe
        helper_scale:              Scale of rendered helpers (locations, axis, mates for MAssemblies) (default=1)

    - Debug
        debug:                   Show debug statements to the VS Code browser console (default=False)
        timeit:                  Show timing information from level 0-3 (default=False)
    """
    global LAST_CALL

    # if sys.gettrace() is not None and not _force_in_debug:
    #     print("\nshow and show_object are ignored in debugging sessions\n")
    #     return

    kwargs = {
        k: v
        for k, v in locals().items()
        if v is not None
        and k
        not in [
            "cad_objs",
            "names",
            "colors",
            "alphas",
            "port",
            "progress",
            "LAST_CALL",
        ]
    }

    kwargs = check_deprecated(kwargs)

    timeit = preset("timeit", timeit)

    names = align_attrs(names, len(cad_objs), None, "names", explode=False)

    # Handle colormaps

    if isinstance(colors, BaseColorMap):
        colors = [next(colors) for _ in range(len(cad_objs))]
        alphas = [None] * len(cad_objs)  # alpha is encoded in colors
    else:
        colors = align_attrs(colors, len(cad_objs), None, "colors")
        alphas = align_attrs(alphas, len(cad_objs), None, "alphas")

    map_colors = None
    colormap = get_colormap()
    if colormap is not None:
        map_colors = [next(colormap) for _ in range(len(cad_objs))]

    for i in range(len(cad_objs)):
        if isinstance(colors[i], str):
            colors[i] = web_to_rgb(colors[i])
        if colors[i] is None and map_colors is not None:
            colors[i] = map_colors[i][:3]
            if alphas[i] is None and len(map_colors[i]) == 4:
                alphas[i] = map_colors[i][3]
        elif colors[i] is not None:
            if alphas[i] is None and len(colors[i]) == 4:
                alphas[i] = colors[i][3]
            colors[i] = colors[i][:3]

    if default_edgecolor is not None:
        default_edgecolor = Color(default_edgecolor).web_color

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

    if not _force_in_debug:
        LAST_CALL = "show"
    else:
        LAST_CALL = "other"

    with Timer(timeit, "", "send"):
        return send_data(data, port=port, timeit=timeit)


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
    default_facecolor=None,
    default_thickedgecolor=None,
    default_vertexcolor=None,
    default_edgecolor=None,
    ambient_intensity=None,
    metalness=None,
    roughness=None,
    direct_intensity=None,
    render_edges=None,
    render_normals=None,
    render_mates=None,
    render_joints=None,
    parallel=None,
    show_parent=None,
    helper_scale=None,
    mate_scale=None,  # DEPRECATED
    debug=None,
    timeit=None,
):
    """Incrementally show CAD objects in Visual Studio Code

    Parameters:
        obj:                     The CAD object to be shown

    Keywords for show_object:
        name:                    The name of the CAD object
        options:                 A dict of color and alpha value: {"alpha":0.5, "color": (64, 164, 223)}
                                 0 <= alpha <= 1.0 and color is a 3-tuple of values between 0 and 255
        parent:                  Add another object, usually the parent of e.g. edges or vertices with alpha=0.25
        clear:                   In interactice mode, clear the stack of objects to be shown
                                 (typically used for the first object)
        port:                    The port the viewer listens to. Typically use 'set_port(port)' instead
        progress:                Show progress of tessellation with None is no progress indicator. (default="-+c")
                                 for object: "-": is reference, "+": gets tessellated, "c": from cache

    Valid keywords to configure the viewer (**kwargs):
    - UI
        glass:                   Use glass mode where tree is an overlay over the cad object (default=False)
        tools:                   Show tools (default=True)
        tree_width:              Width of the object tree (default=240)

    - Viewer
        axes:                    Show axes (default=False)
        axes0:                   Show axes at (0,0,0) (default=False)
        grid:                    Show grid (default=False)
        ortho:                   Use orthographic projections (default=True)
        transparent:             Show objects transparent (default=False)
        default_opacity:         Opacity value for transparent objects (default=0.5)
        black_edges:             Show edges in black color (default=False)
        orbit_control:           Mouse control use "orbit" control instead of "trackball" control (default=False)
        collapse:                Collapse.LEAVES: collapse all single leaf nodes,
                                 Collapse.ROOT: expand root only,
                                 Collapse.ALL: collapse all nodes,
                                 Collapse.NONE: expand all nodes
                                 (default=Collapse.LEAVES)
        ticks:                   Hint for the number of ticks in both directions (default=10)
        up:                      Use z-axis ('Z') or y-axis ('Y') as up direction for the camera (default="Z")

        zoom:                    Zoom factor of view (default=1.0)
        position:                Camera position
        quaternion:              Camera orientation as quaternion
        target:                  Camera look at target
        reset_camera:            Camera.RESET: Reset camera position, rotation, toom and target
                                 Camera.CENTER: Keep camera position, rotation, toom, but look at center
                                 Camera.KEEP: Keep camera position, rotation, toom, and target
                                 (default=Camera.RESET)

        pan_speed:               Speed of mouse panning (default=1)
        rotate_speed:            Speed of mouse rotate (default=1)
        zoom_speed:              Speed of mouse zoom (default=1)

    - Renderer
        deviation:               Shapes: Deviation from linear deflection value (default=0.1)
        angular_tolerance:       Shapes: Angular deflection in radians for tessellation (default=0.2)
        edge_accuracy:           Edges: Precision of edge discretization (default: mesh quality / 100)

        default_color:           Default mesh color (default=(232, 176, 36))
        default_edgecolor:       Default color of the edges of a mesh (default=(128, 128, 128))
        default_facecolor:       Default color of the edges of a mesh (default=#ee82ee / Violet)
        default_thickedgecolor:  Default color of the edges of a mesh (default=#ba55d3 / MediumOrchid)
        default_vertexcolor:     Default color of the edges of a mesh (default=#ba55d3 / MediumOrchid)
        ambient_intensity:       Intensity of ambient light (default=1.00)
        direct_intensity:        Intensity of direct light (default=1.10)
        metalness:               Metalness property of the default material (default=0.30)
        roughness:               Roughness property of the default material (default=0.65)


        render_edges:            Render edges  (default=True)
        render_normals:          Render normals (default=False)
        render_mates:            Render mates for MAssemblies (default=False)
        render_joints:           Render build123d joints (default=False)
        parallel:                Tessellate objects in parallel (default=False)
        show_parent:             Render parent of faces, edges or vertices as wireframe
        helper_scale:            Scale of rendered helpers (locations, axis, mates for MAssemblies) (default=1)

    - Debug
        debug:                   Show debug statements to the VS Code browser console (default=False)
        imeit:                   Show timing information from level 0-3 (default=False)
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
        OBJECTS["colors"].append(None)
        OBJECTS["alphas"].append(None)

    color = None
    alpha = None
    if options is None:
        colormap = get_colormap()
        if colormap is not None:
            for _ in range(len(OBJECTS["names"]) + 1):
                *color, alpha = next(colormap)
    else:
        color = options.get("color")
        alpha = options.get("alpha", 1.0)

    OBJECTS["objs"].append(obj)
    OBJECTS["names"].append(name)
    OBJECTS["colors"].append(color)
    OBJECTS["alphas"].append(alpha)

    show(
        *OBJECTS["objs"],
        names=OBJECTS["names"],
        colors=OBJECTS["colors"],
        alphas=OBJECTS["alphas"],
        port=port,
        progress=progress,
        **kwargs,
    )


def show_clear():
    data = {
        "type": "clear",
    }
    send_data(data)


def show_all(variables=None, exclude=None, **kwargs):
    import inspect

    global FIRST_CALL, LAST_CALL

    if LAST_CALL == "show":
        LAST_CALL = "other"
        print("\nSkip visual debug step after a show() command")
        return

    if variables is None:
        cf = inspect.currentframe()
        variables = cf.f_back.f_locals

    if exclude is None:
        exclude = []

    objects = []
    names = []
    for name, obj in variables.items():
        if (
            isinstance(obj, type)
            or name in ["_", "__", "___"]
            or re.search("_\d+", name) is not None
        ):
            continue  # ignore classes and jupyter variables

        if name not in exclude:
            if hasattr(obj, "_obj") and obj._obj is None:
                continue

            if hasattr(obj, "locations") and hasattr(obj, "local_locations"):
                obj = obj.locations

            if hasattr(obj, "to_location"):
                obj = obj.to_location()

            if (
                (
                    hasattr(obj, "wrapped")
                    and (
                        is_topods_shape(obj.wrapped)
                        or is_topods_compound(obj.wrapped)
                        or is_toploc_location(obj.wrapped)
                    )
                )
                or is_vector(obj)  # Vector
                or is_cadquery(obj)
                or is_build123d(obj)
                or is_cadquery_assembly(obj)
                or (
                    isinstance(obj, (list, tuple))
                    and len(obj) > 0
                    and hasattr(obj[0], "wrapped")
                )
            ):
                objects.append(obj)
                names.append(name)

            elif isinstance(
                obj, (OCP_PartGroup, OCP_Edges, OCP_Faces, OCP_Part, OCP_Vertices)
            ):
                objects.append(obj)
                obj.name = name
                names.append(name)

            elif is_cadquery_sketch(obj):
                pg = to_assembly([obj], names=[name])
                pg.name = name
                objects.append(pg)
                names.append(name)

    if FIRST_CALL:
        kwargs["reset_camera"] = Camera.RESET

    if len(objects) > 0:
        show(
            *objects,
            names=names,
            collapse=Collapse.ROOT,
            _force_in_debug=True,
            **kwargs,
        )
        FIRST_CALL = False
    else:
        show_clear()


def _convert2(obj, name="obj", decode=False, **kwargs):
    def add_geom_type(shapes, mapping):
        for shape in shapes["parts"]:
            if shape.get("parts") is None:
                shape["geomtype"] = mapping[shape["id"]].geom_type()
            else:
                add_geom_type(shape, mapping)

    def to_b123d(obj):
        if is_build123d_shape(obj):
            return obj
        else:
            if is_topods_vertex(obj.wrapped):
                return Vertex(obj.wrapped)
            elif is_topods_edge(obj.wrapped):
                return Edge(obj.wrapped)
            elif is_topods_face(obj.wrapped):
                return Face(obj.wrapped)
            else:
                raise TypeError(f"Cannot convert {type(obj)} to build123d")

    def vals(obj):
        if hasattr(obj, "vals"):
            return obj.vals()
        else:
            return obj

    default_edgecolor = workspace_config()["default_edgecolor"]
    default_facecolor = workspace_config()["default_color"]
    default_vertexcolor = workspace_config()["default_vertexcolor"]

    all_faces = vals(obj.faces())
    all_edges = vals(obj.edges())
    all_vertices = vals(obj.vertices())

    pg = OCP_PartGroup([], name=name)
    mapping = {}

    # Edges
    pg_e = OCP_PartGroup([], name="edges")

    for i, edge in enumerate(all_edges):
        e_name = f"edges_{i}"
        mapping[f"/{name}/edges/{e_name}"] = to_b123d(edge)
        pg_e.add(OCP_Edges([edge.wrapped], name=e_name, color=default_edgecolor))

    if len(all_edges) > 0:
        pg.add(pg_e)

    # Vertices
    pg_v = OCP_PartGroup([], name="vertices")

    for i, vertex in enumerate(all_vertices):
        v_name = f"vertices_{i}"
        mapping[f"/{name}/vertices/{v_name}"] = to_b123d(vertex)
        pg_v.add(
            OCP_Vertices(
                [vertex.wrapped], name=v_name, color=default_vertexcolor, size=2
            )
        )

    if len(all_vertices) > 0:
        pg.add(pg_v)

    # Faces
    pg_f = OCP_PartGroup([], name="faces")

    for i, face in enumerate(all_faces):
        f_name = f"faces_{i}"
        mapping[f"/{name}/faces/{f_name}"] = to_b123d(face)
        faces = OCP_Faces(
            [face.wrapped],
            name=f_name,
            color=default_facecolor if len(all_faces) > 1 else None,
            show_edges=False,
        )
        # Ensure back is not rendered
        if len(all_faces) > 1:
            faces.renderback = False
        pg_f.add(faces)

    if len(all_faces) > 0:
        pg.add(pg_f)

    if not decode:
        shm = SharedMemory(name=f"ocp-viewer-{CMD_PORT}")
        data = pickle.dumps(mapping)
        length = HEADER_SIZE + len(data)
        shm.buf[:length] = struct.pack("I", len(data)) + data
        shm.close()
        resource_tracker.unregister(f"/ocp-viewer-{CMD_PORT}", "shared_memory")

    t = _convert(pg, names=[name], decode=decode)

    add_geom_type(t["data"]["shapes"], mapping)

    # remove edges of faces
    for k, v in t["data"]["states"].items():
        if "/faces/" in k:
            t["data"]["states"][k][1] = 3

    if not decode:
        # collapse faces, edges, vertices
        t["config"]["collapse"] = 3

    return t


def show2(obj, name="obj", **kwargs):
    t = _convert2(obj, name, False, **kwargs)

    send_data(t)


def export_tcv_json(obj, filename="export.json", name="obj", **kwargs):
    t = _convert2(obj, name, True, **kwargs)

    with open(filename, "w") as fd:
        fd.write(json.dumps((t["data"]["shapes"], t["data"]["states"]), indent=2))
