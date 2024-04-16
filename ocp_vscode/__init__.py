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
__version__ = "2.3.0"

from .show import *
from .config import *
from .comms import *

from .colors import *
from .animation import Animation
from ocp_tessellate.cad_objects import ImageFace

try:
    from ocp_tessellate.tessellator import (
        enable_native_tessellator,
        disable_native_tessellator,
        is_native_tessellator_enabled,
    )

    if is_native_tessellator_enabled():
        print(
            "Enabled native tessellator, to disable, call `disable_native_tessellator()`\n"
        )
    else:
        print(
            "Found native tessellator, to ansable, call `enable_native_tessellator()`\n"
        )
except:
    pass
