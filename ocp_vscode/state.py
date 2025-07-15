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

import errno
import json
import os
import time

from pathlib import Path

CONFIG_FILE = Path.home() / ".ocpvscode"


class ProperLockfile:
    def __init__(self, filepath, stale_timeout=5):
        self.lock_dir = f"{filepath}.lock"
        self.stale_timeout = stale_timeout

    def acquire(self):
        while True:
            try:
                os.mkdir(self.lock_dir)
                return True
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise RuntimeError(f"Locking issue, remove {CONFIG_FILE}.lock")

                try:
                    stat = os.stat(self.lock_dir)
                    if (time.time() - stat.st_mtime) > self.stale_timeout:
                        print("Stale lock detected, removing")
                        os.rmdir(self.lock_dir)
                    else:
                        time.sleep(0.1)
                except OSError:
                    raise RuntimeError(f"Locking issue, remove {CONFIG_FILE}.lock")

    def release(self):
        try:
            os.rmdir(self.lock_dir)
        except OSError:
            pass


def atomic_operation(callback):
    lock = ProperLockfile(CONFIG_FILE)
    result = None
    try:
        if lock.acquire():
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    try:
                        config = json.load(f)
                    except json.JSONDecodeError:
                        config = {"version": 2, "services": {}}
            else:
                config = {"version": 2, "services": {}}

            result = callback(config)

    finally:
        lock.release()

    return result


def get_config_file():
    """Get the config file"""
    return str(CONFIG_FILE)


def update_state(port, connectionFile):
    """Update the config file with the given key/value pair"""

    def callback(config):
        config["services"][port] = connectionFile
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    return atomic_operation(callback)


def get_ports():
    """Get the config file"""

    def callback(config):
        services = config.get("services")
        if services is None:
            return []
        else:
            return list(services.keys())

    return atomic_operation(callback)
