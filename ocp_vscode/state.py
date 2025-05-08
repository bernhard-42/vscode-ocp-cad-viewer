"""
state uses "poor man's locking": nodejs does not support fcntl (POSIX) or
LockFileEx (Windows) locking. This module implements a simple locking
mechanism for nodejs and Python leveraging "mkdir" to create locks.

Ideas are taken from the node js library "proper-lockfile"
(https://github.com/moxystudio/node-proper-lockfile)
"""

import json

from filelock import FileLock
from pathlib import Path

STALE_DURATION_MS = 3000  # 3 seconds
RETRIES = 7
INTERVAL_MS = 500  # INTERVAL_MS * RETRIES > STALE_DURATION
CONFIG_FILE = Path.home() / ".ocpvscode"
LOCK_PATH = CONFIG_FILE.with_name(CONFIG_FILE.name + ".lock")


def atomic_operation(callback):
    lock = FileLock(str(LOCK_PATH))
    with lock:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        else:
            config = {"version": 2, "services": {}}

        result = callback(config)
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
