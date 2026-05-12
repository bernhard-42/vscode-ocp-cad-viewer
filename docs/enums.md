# Enums reference

All enums below are exported from `ocp_vscode` and accepted wherever the underlying string value would also work.

```python
from ocp_vscode import Camera, Collapse, Render, AnalysisTool, UiTab
from ocp_vscode import StudioEnvironment, StudioBackground, StudioToneMapping, StudioTextureMapping
```

## `Camera`

Camera behavior for `reset_camera=` and the workspace setting `OcpCadViewer.view.reset_camera`.

| Member          | Effect                                                                                       |
| --------------- | -------------------------------------------------------------------------------------------- |
| `Camera.RESET`  | Reset position, rotation, zoom, target to defaults                                           |
| `Camera.CENTER` | Keep position, rotation, zoom; recentre look-at on the new object                            |
| `Camera.KEEP`   | Keep position, rotation, zoom, target (falls back to `CENTER` if object size changes >2×)    |
| `Camera.ISO`    | Snap to isometric preset                                                                     |
| `Camera.TOP` / `BOTTOM` / `LEFT` / `RIGHT` / `FRONT` / `BACK` | Snap to the named axis-aligned preset                       |

## `Collapse`

Initial state of the navigation tree.

| Member             | Tree state                  |
| ------------------ | --------------------------- |
| `Collapse.NONE`    | Fully expanded              |
| `Collapse.LEAVES`  | Collapse single-leaf nodes  |
| `Collapse.ALL`     | All nodes collapsed         |
| `Collapse.ROOT`    | Only the root expanded      |

## `Render`

Per-object render mode used with `show_object(..., mode=...)` and `show(..., modes=[...])`.

| Member          | Shows         |
| --------------- | ------------- |
| `Render.ALL`    | Faces + edges |
| `Render.FACES`  | Faces only    |
| `Render.EDGES`  | Edges only    |
| `Render.NONE`   | Hidden        |

## `AnalysisTool`

Active analysis tool — see [measure.md](measure.md).

| Member                     | Tool                                |
| -------------------------- | ----------------------------------- |
| `AnalysisTool.PROPERTIES`  | Properties readout                  |
| `AnalysisTool.DISTANCE`    | Distance / angle measurement        |
| `AnalysisTool.SELECT`      | Object selection — see [selector.md](selector.md) |
| `AnalysisTool.OFF`         | No analysis tool                    |

Mutually exclusive with `explode=True`.

## `UiTab`

Side-panel tab selection — used by `set_viewer_config(tab=...)` and the `tab=` keyword on every `show*` command.

| Member             | Tab        |
| ------------------ | ---------- |
| `UiTab.TREE`       | Object tree |
| `UiTab.CLIP`       | Clipping   |
| `UiTab.ZEBRA`      | Zebra      |
| `UiTab.MATERIAL`   | Material   |
| `UiTab.STUDIO`     | Studio     |

## Studio-mode enums

Used in `set_viewer_config(...)` and the `studio_*=` keywords on every `show*` command.

### `StudioEnvironment`

HDR environment map presets. Members include `PROCEDURAL_STUDIO` (the default), `SOFT_LIGHT`, `HIGH_CONTRAST_STUDIO`, `BRIGHT_NEUTRAL`, `CLEAN_SOFTBOX`, `SPOTLIT_SETUP`, `CONTROLLED_LIGHT`, `HARD_CONTRAST_LIGHT`, `URBAN_OVERCAST`, `OUTDOOR_WARM`, `NEUTRAL_INDUSTRIAL`, `SAN_GIUSEPPE_BRIDGE`. A custom HDR URL is also accepted in place of an enum member.

### `StudioBackground`

`ENVIRONMENT`, `TRANSPARENT`, `GRADIENT`, `GRADIENT_DARK`, `WHITE`, `GREY`, `DARKGREY`.

### `StudioToneMapping`

`NEUTRAL`, `ACES`, `NONE`.

### `StudioTextureMapping`

`TRIPLANAR`, `PARAMETRIC`.
