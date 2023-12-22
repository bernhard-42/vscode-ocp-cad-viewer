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
__version__ = "2.0.13"

import json
import socket

from pathlib import Path
from os import environ

from .show import *
from .config import *
from .comms import *

from .colors import *
from .animation import Animation


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
except Exception as ex:
    print(ex)

try:
    from jupyter_client import find_connection_file

    cf = find_connection_file()
    with open(cf, "r", encoding="utf-8") as f:
        connection_info = json.load(f)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(("127.0.0.1", connection_info["iopub_port"]))

    if result == 0:
        print("Jupyter kernel running")
        s.close()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {"port": port, "connection_file": cf},
                f,
                indent=4,
            )
        print("Jupyter Connection file written to .ocp_vscode")
except Exception as ex:
    print(ex)

del environ
