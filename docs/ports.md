# Ports and connecting to a viewer

The Python side (`show`, `show_object`, `set_viewer_config`, …) talks to the viewer over a WebSocket on a single port. This page explains how that port is chosen.

## The state file `~/.ocpvscode`

Each running viewer registers itself in the JSON file `~/.ocpvscode`:

```json
{
  "version": 2,
  "services": {
    "3939": "<connection file>",
    "3940": ""
  }
}
```

- The **VS Code extension** writes its port there when it starts a viewer, together with the Jupyter kernel connection file if Jupyter is in use.
- The **standalone CLI** (`python -m ocp_vscode`) registers its port there too (empty connection file).
- When a viewer shuts down cleanly, its entry is removed.

`get_config_file()` returns the absolute path to this file.

## Discovery algorithm

On the **first** `show*` call in a Python process, `find_and_set_port()` runs the following:

1. **`OCP_PORT` env var.** If set to a non-zero integer, that port is used directly. No state-file lookup, no probing — useful in CI or to point at a specific viewer:

    ```bash
    OCP_PORT=3940 python my_script.py
    ```

2. **Read `~/.ocpvscode`** and probe every listed port with a 1-second TCP connection check. Ports that don't respond are dropped (a stale entry from a viewer that crashed).
3. The remaining live ports decide what happens:
    - **0 live ports** — fall back to `3939` if that port is open; otherwise discovery fails and `show` will error.
    - **1 live port** — use it silently.
    - **2+ live ports** — prompt:
        - In a terminal / standard Python process: a `questionary` "Select a port" list.
        - In a Jupyter kernel (`ZMQInteractiveShell`): a `Select port in VS Code input box above` message; pick the port in the input box that VS Code pops up.

Once chosen, the port is cached for the rest of the Python process — subsequent `show*` calls reuse it without re-running discovery.

## Manual control

### `set_port(port, host="127.0.0.1")`

Skip discovery entirely and pin to a specific viewer:

```python
from ocp_vscode import set_port
set_port(3940)
```

After this call, all `show*` commands talk to port `3940`. This is the recommended approach when you routinely run multiple viewers.

### `find_and_set_port()`

Re-run the discovery algorithm above. Useful after closing/opening viewers within the same Python session, or to reset a previous `set_port` choice.

### `get_port()`

Return the currently selected port (triggering discovery on first call). Used internally by every `show*` command; also exposed for callers that want to pass `port=get_port()` explicitly.

### Per-call `port=` keyword

Every `show*` command accepts an explicit `port=` kwarg. Passing it overrides the cached port for that single call only — handy for one-off pushes to a different viewer.

## Status bar

The VS Code extension shows the active viewer's port in the status bar:

- `OCP: <port>` — viewer running, visual debugging off
- `OCP: <port>·DEBUG` — viewer running, visual debugging on

See [debug.md](debug.md) for the toggle behavior.

## Common situations

| Situation                                  | What to do                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Only one viewer running                    | Nothing — discovery picks it automatically                                                       |
| Multiple viewers, same project             | `set_port(<port>)` at the top of the script, or pick from the prompt on first `show`             |
| Switching between VS Code and standalone   | Either `set_port(...)` explicitly, or let the prompt handle it                                   |
| Running tests / CI                         | `OCP_PORT=<port>` in the environment                                                             |
| Stale entry in `~/.ocpvscode` after a crash | The 1-second probe drops it automatically; if you want to clean it up by hand, edit the JSON     |
| "Cannot access viewer config"              | The Python side picked a port nothing is listening on. Run `find_and_set_port()` or `set_port(...)` |
