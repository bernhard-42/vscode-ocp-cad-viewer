# Config files

OCP CAD Viewer reads two files in your home directory. They serve different purposes and are independent of each other.

| File                       | Format | Purpose                                                                                                |
| -------------------------- | ------ | ------------------------------------------------------------------------------------------------------ |
| `~/.ocpvscode`             | JSON   | Live registry of running viewers and their ports — used by the Python side to find a viewer to talk to |
| `~/.ocpvscode_standalone`  | YAML   | Default options for the standalone CLI (`python -m ocp_vscode`) — analogous to VS Code workspace settings |

## `~/.ocpvscode` — viewer registry

Every running viewer (both the VS Code extension and the standalone CLI) registers its port in this file. The Python side reads it to discover which viewer to send `show*` calls to.

```json
{
  "version": 2,
  "services": {
    "3939": "<jupyter connection file or empty>",
    "3940": ""
  }
}
```

- Maintained automatically by the extension and `python -m ocp_vscode` — you should not need to edit it.
- When a viewer shuts down cleanly, its entry is removed. The discovery code in [ports.md](ports.md) also probes each listed port with a 1-second TCP check, so a stale entry from a crashed viewer is harmless.
- `get_config_file()` (Python) returns the absolute path.

See [ports.md](ports.md) for the full discovery algorithm and how to override it with `OCP_PORT` or `set_port()`.

## `~/.ocpvscode_standalone` — standalone CLI defaults

Stores default values for the standalone server flags (theme, tree width, axes, grids, mouse speeds, modifier keys, …). When `python -m ocp_vscode` starts it merges this file on top of its built-in defaults; any CLI flag you pass on top of that wins.

Precedence (lowest to highest):

1. Built-in defaults compiled into `ocp_vscode/standalone.py`
2. `~/.ocpvscode_standalone` (if present)
3. CLI flags passed to `python -m ocp_vscode`

Create the file (populated with the current built-in defaults) with:

```bash
python -m ocp_vscode --create_configfile
```

It is written as YAML, so it's straightforward to edit by hand:

```yaml
theme: dark
tree_width: 300
axes: true
axes0: true
grid_xy: true
pan_speed: 0.5
rotate_speed: 1.0
zoom_speed: 0.5
```

Only keys that exist in the built-in defaults are honored; everything else is ignored. Delete the file to fall back to the built-in defaults entirely.

This file has no effect on the VS Code extension — VS Code uses its own workspace settings (see [settings.md](settings.md)).
