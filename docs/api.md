# Additional Python API

Functions exported from `ocp_vscode` that aren't covered by the dedicated `show*` pages.

## Screenshots

- `save_screenshot(filename, port=None, polling=True, progress_only=False)`

    Save the current viewer view to a PNG. `filename` is taken relative to the current working directory unless it's absolute. With `polling=True` the call returns only after the file has been written; this is what `Animation.save_as_gif` relies on internally.

## Object stack management

- `show_clear(port=None)`

    Clear the viewer (remove all currently shown objects, reset the navigation tree).

- `remove_object(name, call_show=False, port=None, progress="-+*c")`

    Remove a single named object from the incremental object stack used by `push_object` / `show_objects`. If `call_show=True`, immediately re-renders the remaining stack.

- `reset_show()`

    Reset the object stack so the next `show_object(..., clear=True)` starts from a clean slate. Convenience around the same internal registry that `push_object` and `show_objects` work on.

## Defaults

- `set_defaults(**kwargs)`

    Persist values across subsequent `show*` calls in this Python process. Accepts the same viewer keywords as `show` (see [show.md](show.md)). Workspace settings provide the starting values; `set_defaults` overrides them.

- `reset_defaults(port=None)`

    Re-apply the workspace settings on top of the running viewer and clear the in-process defaults set via `set_defaults`.

- `get_default(key, port=None)` / `get_defaults(port=None)`

    Read a single default or the full merged default dict (workspace + `set_defaults`).

## Viewer state

- `status(port=None, viewer=None, debug=False)`

    Return the live state dict of the viewer (camera position, current tab, visibility states, …). With `debug=True` returns only the `_debugStarted` flag.

- `workspace_config(port=None, viewer=None)`

    Return the workspace configuration as the viewer currently sees it. Raises `RuntimeError` if the viewer isn't reachable.

- `combined_config(port=None, viewer=None)`

    `workspace_config` merged with the live `status` and any `set_defaults` overrides — useful for "what will the next `show` actually use?" inspection.

## Port and connection

- `get_port()`, `set_port(port, host="127.0.0.1")`, `find_and_set_port()` — see [ports.md](ports.md) for the full discovery algorithm, the `~/.ocpvscode` state file, and the `OCP_PORT` env var override.

- `set_connection_file()`

    Write the kernel connection file for Jupyter Console integration. Called automatically on first use; only invoke directly if you need to refresh the file.

- `listener(callback)`

    Returns a callable that, when run in a thread, streams `(message, MessageType)` pairs from the viewer (e.g. selection events, config updates). `MessageType` is an `IntEnum` exported alongside the function.

## Imports & utilities

- `ImageFace`

    Re-exported from `ocp_tessellate.cad_objects`. Lets you place a 2-D image as a face in the scene. See `examples/examples.py` for usage.
