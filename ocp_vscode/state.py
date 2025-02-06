"""
state uses "poor man's locking": nodejs does not support fcntl (POSIX) or 
LockFileEx (Windows) locking. This module implements a simple locking 
mechanism for nodejs and Python leveraging "mkdir" to create locks. 

Ideas are taken from the node js library "proper-lockfile"
(https://github.com/moxystudio/node-proper-lockfile)
"""

import json
import os
import time

STALE_DURATION_MS = 3000  # 3 seconds
RETRIES = 7
INTERVAL_MS = 500  # INTERVAL_MS * RETRIES > STALE_DURATION
CONFIG_FILE = "~/.ocpvscode"


def get_config_file():
    """Get the config file"""
    return resolve_path(CONFIG_FILE)


def get_lock_file(file):
    """Get the lock file for the given file"""
    return f"{file}.lock"


def resolve_path(file):
    """Resolve the canonical path of the file"""
    return os.path.realpath(os.path.expanduser(file))


def is_lock_stale(mtime, stale_seconds):
    """Check if the lock is stale"""
    return (time.time() - mtime) > stale_seconds


def remove_lock(lockfile):
    """Remove the lockfile"""
    try:
        os.rmdir(lockfile)
    except FileNotFoundError:
        print(f"Lock file {lockfile} not found")
    except Exception as ex:
        raise RuntimeError(f"Unable to remove lock file {lockfile}") from ex


def acquire_lock(
    lockfile,
    retries=RETRIES,
    interval_ms=INTERVAL_MS,
    stale_duration_ms=STALE_DURATION_MS,
    retry=0,
):
    """Acquire the lock for the given file"""

    # Use mkdir to create the lockfile
    try:
        os.mkdir(lockfile)
        # lock successfully acquired
        # print(f"Lock file {lockfile} aquired")
    except FileExistsError:
        print(f"Lock file {lockfile} already exists")
        if is_lock_stale(os.stat(lockfile).st_mtime, stale_duration_ms / 1000):
            print(f"Lock file {lockfile} is stale")
            try:
                # assume the lockfile is stale and simply remove it
                remove_lock(lockfile)
            except FileNotFoundError:
                pass  # lock seems to be just removed, which is ok
            except Exception as ex:
                raise RuntimeError(
                    f"Unable to remove stale lock file {lockfile}."
                ) from ex

            # try to acquire the lock again
            acquire_lock(lockfile, retries, interval_ms, stale_duration_ms, retry + 1)
        else:
            if retry < retries:
                time.sleep(interval_ms / 1000)
                print("Retrying to acquire lock")
                acquire_lock(
                    lockfile, retries, interval_ms, stale_duration_ms, retry + 1
                )
            else:
                raise RuntimeError(  # pylint: disable=raise-missing-from
                    f"Unable to acquire lock for file {lockfile} after {retries} retries"
                )

    except Exception as ex:
        raise RuntimeError(f"Cannot create lock file {lockfile}.") from ex


def lock(file, retries=RETRIES, interval_ms=INTERVAL_MS):
    """Lock the given file"""
    lockfile = get_lock_file(file)
    acquire_lock(lockfile, retries, interval_ms)


def unlock(file):
    """Unlock the given file"""
    lockfile = get_lock_file(file)
    remove_lock(lockfile)


def update_state(port, key=None, value=None):
    """Update the config file with the given key/value pair"""

    config_file = resolve_path(CONFIG_FILE)
    lock(config_file)
    try:
        # pylint: disable=consider-using-with
        fd = open(config_file, "r+", encoding="utf-8")
        config = fd.read()
        if config == "":
            config = {}
        else:
            config = json.loads(config)
    except FileNotFoundError:
        # pylint: disable=consider-using-with
        fd = open(config_file, "w+", encoding="utf-8")
        config = {}
    except Exception as ex:
        unlock(config_file)
        raise RuntimeError(f"Unable to open config file {config_file}.") from ex
    fd.close()

    port = str(port)
    if config.get(port) is None:
        config[port] = {}

    if key is None:
        del config[port]
    elif value is None:
        del config[port][key]
    elif isinstance(value, str):
        config[port][key] = value.rstrip(os.path.sep)
    else:
        config[port][key] = [v.rstrip(os.path.sep) for v in value]

    try:
        with open(config_file, "w", encoding="utf-8") as fd:
            fd.write(json.dumps(config, indent=2))
    except Exception as ex:
        raise RuntimeError(f"Unable to write config file {config}.") from ex
    finally:
        unlock(config_file)


def get_state():
    """Get the config file"""
    config_file = resolve_path(CONFIG_FILE)
    lock(config_file)
    try:
        with open(config_file, "r", encoding="utf-8") as fd:
            config = fd.read()
            if config == "":
                config = {}
            else:
                config = json.loads(config)
        unlock(config_file)
    except FileNotFoundError as ex:
        with open(config_file, "w") as fd:
            fd.write("{}\n")
        config = {}

    return config
