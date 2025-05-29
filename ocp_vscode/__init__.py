"""ocp_vscode - OCC viewer for VSCode"""

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
__version__ = "2.8.0"

import os
import sys

from .show import *
from .config import *
from .comms import *

from .colors import *
from .animation import Animation
from ocp_tessellate.cad_objects import ImageFace
from ocp_tessellate.ocp_utils import get_faces, get_vertices, get_edges

try:
    from ocp_tessellate.tessellator import (
        enable_native_tessellator,
        disable_native_tessellator,
        is_native_tessellator_enabled,
    )

    if os.environ.get("NATIVE_TESSELLATOR") == "0":
        disable_native_tessellator()
    else:
        enable_native_tessellator()

    print(
        "Found and enabled native tessellator.\n"
        "To disable, call `disable_native_tessellator()`\n"
        "To enable, call `enable_native_tessellator()`\n"
    )
except:
    pass


def select_vertices(obj, indices):
    print("Only available for build123d")


def select_edges(obj, indices):
    print("Only available for build123d")


def select_faces(obj, indices):
    print("Only available for build123d")


try:
    from build123d import Edge, Face, Vertex, ShapeList

    def warn_once(message):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not getattr(wrapper, "_warned", False):
                    print(message)
                    wrapper._warned = True
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def _select(obj, indices, cls, getter):
        objects = list(getter(obj.wrapped))
        result = []
        for i in indices:
            object = cls(objects[i])
            object.topo_parent = obj
            result.append(object)

        return ShapeList(result)

    @warn_once(
        "EXPERIMENTAL! The indices for 'select_vertices' are only valid as long the topology before this call will not be changed!"
    )
    def select_vertices(obj, indices):
        return _select(obj, indices, Vertex, get_vertices)

    @warn_once(
        "EXPERIMENTAL! The indices for 'select_edges' are only valid as long the topology before this call will not be changed!"
    )
    def select_edges(obj, indices):
        return _select(obj, indices, Edge, get_edges)

    @warn_once(
        "EXPERIMENTAL! The indices for 'select_faces' are only valid as long the topology before this call will not be changed!"
    )
    def select_faces(obj, indices):
        return _select(obj, indices, Face, get_faces)

except:
    pass
