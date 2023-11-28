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
__version__ = "2.0.0"

import json
from .show import *
from .config import *
from .comms import *

from .colors import *
from .animation import Animation

from pathlib import Path
from os import environ

try:
    port = int(environ.get("OCP_PORT", "0"))
    if port > 0:
        set_port(port)
        print(f"Using predefined port {port} taken from environment variable OCP_PORT")
    else:
        current_path = Path.cwd()
        for path in [current_path] + list(current_path.parents):
            file_path = path / ".ocp_vscode"
            if file_path.exists():
                with open(file_path, "r") as f:
                    port = json.load(f)["port"]
                    set_port(port)
                    print(f"Using port {port} taken from {file_path}")
                    break
except:
    pass

del environ
