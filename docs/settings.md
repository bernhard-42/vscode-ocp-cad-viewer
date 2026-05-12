# VS Code Settings reference

Every `OcpCadViewer.*` setting can be edited from the VS Code Settings UI (search for "OCP CAD Viewer") or directly in `settings.json`. Workspace settings override user settings. Defaults set here are also the starting point for `set_defaults()` / `set_viewer_config()` from Python.

## OcpCadViewer.view.*

Visual defaults applied to every newly shown object.

| Setting              | Type     | Default            | Description                                                                                                       |
| -------------------- | -------- | ------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `tree_width`         | integer  | `240`              | Navigation tree width in px                                                                                       |
| `glass`              | boolean  | `true`             | Glass mode (tree overlays the canvas)                                                                             |
| `tools`              | boolean  | `true`             | Show toolbar                                                                                                      |
| `new_tree_behavior`  | boolean  | `true`             | Eye icon controls both faces and edges; mesh icon controls only the mesh                                          |
| `dark`               | boolean  | `false`            | **DEPRECATED** — use `theme` instead                                                                              |
| `theme`              | enum     | `browser`          | `browser` / `light` / `dark`                                                                                      |
| `orbit_control`      | boolean  | `false`            | `orbit` control mode instead of `trackball`                                                                       |
| `up`                 | enum     | `Z`                | Up direction: `Z` / `Y` / `L` (legacy)                                                                            |
| `rotate_speed`       | number   | `1`                | Rotation speed                                                                                                    |
| `zoom_speed`         | number   | `1`                | Zoom speed                                                                                                        |
| `pan_speed`          | number   | `1`                | Pan speed                                                                                                         |
| `axes`               | boolean  | `false`            | Show axes                                                                                                         |
| `axes0`              | boolean  | `true`             | Show axes at origin `(0,0,0)`                                                                                     |
| `black_edges`        | boolean  | `false`            | Render edges in black                                                                                             |
| `grid_XY`            | boolean  | `false`            | Show grid on XY plane                                                                                             |
| `grid_YZ`            | boolean  | `false`            | Show grid on YZ plane                                                                                             |
| `grid_XZ`            | boolean  | `false`            | Show grid on XZ plane                                                                                             |
| `center_grid`        | boolean  | `false`            | Center grid at object/origin                                                                                      |
| `collapse`           | enum     | `1` (leaves)       | Tree initial state: `none` / `leaves` / `all` / `root`                                                            |
| `ortho`              | boolean  | `true`             | Orthographic camera                                                                                               |
| `ticks`              | number   | `5`                | Hint for grid tick count                                                                                          |
| `transparent`        | boolean  | `false`            | Show objects transparent                                                                                          |
| `default_opacity`    | number   | `0.5`              | Opacity for transparent objects                                                                                   |
| `explode`            | boolean  | `false`            | Turn explode mode on                                                                                              |
| `reset_camera`       | enum     | `KEEP`             | Camera behavior between `show` calls: `RESET` / `KEEP` / `CENTER` / `ISO` / `TOP` / `BOTTOM` / `LEFT` / `RIGHT` / `FRONT` / `BACK` |
| `modifier_keys`      | object   | see settings.json  | Mapping of `shift` / `ctrl` / `meta` / `alt` to JS modifier key names                                             |

## OcpCadViewer.render.*

Tessellation and material defaults.

| Setting                  | Type   | Default        | Description                          |
| ------------------------ | ------ | -------------- | ------------------------------------ |
| `angular_tolerance`      | number | `0.2`          | Angular deflection for tessellation  |
| `deviation`              | number | `0.1`          | Linear deviation for tessellation    |
| `default_color`          | string | `#e8b024`      | Default shape color (CSS3 names OK)  |
| `default_edgecolor`      | string | `#707070`      | Default edge color                   |
| `default_thickedgecolor` | string | `MediumOrchid` | Default thick-edge / line color      |
| `default_facecolor`      | string | `Violet`       | Default face color                   |
| `default_vertexcolor`    | string | `MediumOrchid` | Default vertex color                 |
| `ambient_intensity`      | number | `1`            | Ambient light intensity              |
| `direct_intensity`       | number | `1.1`          | Direct light intensity               |
| `metalness`              | number | `0.3`          | Material metalness                   |
| `roughness`              | number | `0.65`         | Material roughness                   |

## OcpCadViewer.advanced.*

Behavior of the extension and the Library Manager.

| Setting               | Type    | Default                                          | Description                                                                                            |
| --------------------- | ------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `watchCommands`       | string  | `from ocp_vscode import show_all, get_port; ...` | Command run by the debugger on every step; must call `show_all(locals(), ...)`                         |
| `watchByDefault`      | boolean | `true`                                           | Start visual debugging (`OCP <port>·DEBUG`) by default when the debugger attaches                      |
| `autostart`           | boolean | `true`                                           | Start the viewer automatically when a relevant Python file is opened                                   |
| `autostartTriggers`   | array   | `["from ocp_vscode import", "import ocp_vscode"]`| Lines that, when seen in an open Python file, trigger autostart                                        |
| `autostartDelay`      | number  | `250`                                            | ms to wait before refreshing viewer/library manager on VS Code start                                   |
| `autohideTerminal`    | boolean | `false`                                          | Hide the terminal when the viewer starts                                                               |
| `initialPort`         | number  | `3939`                                           | First port the viewer tries; subsequent ports are scanned if taken                                     |
| `shellCommandPrefix`  | string  | `""`                                             | Prefix added to every shell command run by the extension (e.g. `" "` to suppress shell history)        |
| `terminalDelay`       | number  | `1000`                                           | ms to wait before sending commands to a freshly opened terminal                                        |
| `quickstartCommands`  | object  | see [install.md](install.md)                     | Commands run by the _Quickstart build123d_ / _Quickstart CadQuery_ buttons                             |
| `installCommands`     | object  | see [install.md](install.md)                     | Per-library install/upgrade commands run by the Library Manager                                        |
| `codeSnippets`        | object  | see settings.json                                | Python import snippets pasted by the "paste" button next to each library                               |
| `exampleDownloads`    | object  | see settings.json                                | Per-library archive URL and the path inside the archive that holds the examples                        |

Placeholder substitution (`{python}`, `{pip-install}`, `{unset_conda}`, `{ocp_vscode_version}`) is documented in [install.md](install.md).

## OcpCadViewer.snippets.*

| Setting              | Type   | Default                  | Description                                                                              |
| -------------------- | ------ | ------------------------ | ---------------------------------------------------------------------------------------- |
| `dotVscodeSnippets`  | object | (build123d snippet pack) | Snippets written into `<project>/.vscode/` by the "Install CAD snippets" command. See [snippets.md](snippets.md). |
