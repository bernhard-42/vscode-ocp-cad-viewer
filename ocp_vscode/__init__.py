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

from os import environ

try:
    port = int(environ.get("OCP_PORT", "0"))
    if port > 0:
        set_port(port)
    else:
        import os

        cwd = os.getcwd()
        while cwd != "/":
            if os.path.exists(os.path.join(cwd, ".ocp_vscode")):
                break
            cwd = os.path.dirname(cwd)

        with open(os.path.join(cwd, ".ocp_vscode"), "r") as f:
            port = json.load(f)["port"]
        set_port(port)
    print(f"Using OCP_PORT={port}")
except:
    pass

del environ
