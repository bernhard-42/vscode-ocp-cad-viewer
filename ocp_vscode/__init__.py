"""ocp_vscode - OCC viewer for VSCode"""

# ruff: noqa: F403, F401
#
# Copyright 2025 Bernhard Walter
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
__version__ = "4.0.2"

from .show import *
from .config import *
from .comms import *
from .utils import *

from .colors import *
from .ocp_selectors import *
from ocp_viewer_core.tessellator import (
    ImageFace,
    disable_native_tessellator,
    enable_native_tessellator,
    init_native_tessellator,
    is_native_tessellator_enabled,
)

# The union of the submodules' __all__ plus what is imported by name above, so
# the star surface is chosen rather than accidental - the submodule names stay
# out. The tessellator toggles are part of it now: they come from the core and
# are always defined, where the conditional import they replace left names that
# may not exist, and a name in __all__ that does not exist breaks every star
# import.
__all__ = [
    "AnalysisTool",
    "Animation",
    "BaseColorMap",
    "Camera",
    "camera_keep_warning",
    "check_deprecated",
    "Collapse",
    "ColorMap",
    "combined_config",
    "comms_warning",
    "default",
    "disable_native_tessellator",
    "enable_native_tessellator",
    "find_and_set_port",
    "get_colormap",
    "get_default",
    "get_defaults",
    "get_host",
    "get_port",
    "GoldenRatioColormap",
    "hex_to_rgb",
    "hsv_mapper",
    "ignore_camera_warnings",
    "ImageFace",
    "init_native_tessellator",
    "is_native_tessellator_enabled",
    "is_pytest",
    "ListedColorMap",
    "listener",
    "matplotlib_mapper",
    "MessageType",
    "none_filter",
    "port_check",
    "push_object",
    "random_rgb_mapper",
    "remove_object",
    "Render",
    "reset_defaults",
    "reset_show",
    "save_screenshot",
    "SeededColormap",
    "SegmentedColorMap",
    "select_edge",
    "select_edges",
    "select_face",
    "select_faces",
    "select_vertex",
    "select_vertices",
    "send_backend",
    "send_command",
    "send_config",
    "send_data",
    "set_colormap",
    "set_defaults",
    "set_port",
    "set_viewer_config",
    "show",
    "show_all",
    "show_clear",
    "show_object",
    "show_objects",
    "status",
    "StudioBackground",
    "StudioEnvironment",
    "StudioTextureMapping",
    "StudioToneMapping",
    "UiTab",
    "unset_colormap",
    "VSCodeComms",
    "web_to_rgb",
    "workspace_config",
]


if init_native_tessellator():
    print("Found and enabled native tessellator.")
