# Change Log

All notable changes to the "OCP CAD Viewer" extension will be documented in this file.

v1.2.2

-   Replace the boolean values for `reset_camera` with the `Camera` enum; `reset_camera` now supports `Camera.RESET` (works like `True` before), `Camera.CENTER` (works like `False` before) and `Camera.KEEP` (additionally keeps the pan location). See best practices for details.
-   Replace the values for `collapse` with the `Collapse` enum: `Collapse.ALL` (was `"C"`), `Collapse.None` (was `"E"`), `Collapse.LEAVES` (was `"1"` or `1`) and `Collapse.Root` (was `"R"`)
-   Added a button to toggle the output panel for OCP CAD Viewer
-   Visual debug is on by default now (workspace setting `WatchByDefault` to `true`)
-   Changed behavior of ` show` during debug session: `show` will be executed, however, visual debug step omitted
-   Do not show Jupyter variables `_`, `__`, `_1`, `_2`, ... in `show_all`
-   Fix an error where the orientation marker was partly or fully moved outside its view due to panning of the object ([vscode-ocp-cad-viewer issue #22](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/22))

v1.2.1

-   XYZ labels for orientation marker ([vscode-ocp-cad-viewer issue #13](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/13))
-   Support for metalness and roughness ([three-cad-viewer issue #9](https://github.com/bernhard-42/three-cad-viewer/issues/9))
-   New "Material" configurator tab in the viewer UI
-   Port 3939 will automatically incremented by 1 for 2nd, 3rd, ... viewer
-   Fix: OCP_Part can be shown now ([vscode-ocp-cad-viewer issue #20](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/20))
-   Fix: reset_camera respects panning ([vscode-ocp-cad-viewer issue #19](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/19))
-   Fix: `collapse="C"` also collapses single item trees ([vscode-ocp-cad-viewer issue #18](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/18))
-   Fix: Show_all supports having a sketch that uses face as a workplane ([vscode-ocp-cad-viewer issue #17](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/17))
-   Fix: `_config==undefined` is handled properly ([vscode-ocp-cad-viewer issue #12](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/12))

v1.1.3

-   Fix racing conditions that prevented having more than one viewer window
-   No need to add port for next viewer any more. The default port 3939 will be incremented until a free port is found
-   Use ocp-tessellate 1.1.1 (fixes axis helper scale)

v1.1.2

-   Added Visual debugging (including a toggle switch in the status bar)
-   Added function `show_all` and `show_clear` for the visual debugging
-   New (opinonated) Quickstart modes to install ever for build123d or CadQury with one click
-   Websocket communication between Python and the VS Code extension
-   Remove IPython support and introduce Jupyter / ipykernel support
-   Rename ColorMap to BaseColorMap and CM to ColorMap
-   Check versions of the viewer and the Pyhton module ocp_vscode are the same at OCP Viewer start
-   Support OCCT Shells
-   Bump three-cad-viewer 1.7.12
-   Fix two race conditions at viewer start (missing awaits)
