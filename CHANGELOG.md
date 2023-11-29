# Change Log

All notable changes to the "OCP CAD Viewer" extension will be documented in this file.

v2.0.6

-   Add three-cad-viewer 2.1.2 to fix black edges issue in measure mode and remove angle tool resizing

v2.0.4

-   Fix regression of ocp-tessallate version

v2.0.3

-   Fix regression in port detection
-   Added missing dependencies for build123d on Apple Silicon

v2.0.2

-   Fix .ocp_vscode detection on Windows
-   Fix showing ShapeList[Vector]
-   Viewer now starts when VS Code opens with a build123d/cadquery Python file

v2.0.1

-   Introduce a workspace configuration `initialPort` for OCP CAD Viewer
-   Change the warning about used port to an auto vanishing info

v2.0.0

-   Introduce measure mode. Use `set_defaults(measure_tools=True)` or `show(obj, measure_tools=True)` or the global workspace confiv of OCP CAD Viewer to turn it on. This release added a Python backend process that communicates with the viewer for providing correct BRep measurement info.
-   Autostart viewer: When opening or saving a Python file that includes `import cadquery`, `import build123d`, `from cadquery import` or `from build123d import`, the viewer gets started if it is not already running. Use `OcpCadViewer.autostart` configuration of workspace config to turn this feature off.
-   Environment variable OCP_PORT is supported. It will be used by the viewer and the `show*` clients as the port for OCP CAD Viewer. This variable can be set on the command line or in `launch.json` (`"env": {"OCP_PORT": "3999"}`).
-   `CAMERA.KEEP` and `CAMERA.CENTER` now persist the viewer across execution sessions. If you want to reset at every beginning, use `show(objs, reset_camer=Camera.RESET)` as the first show command.
-   Modifier keys can now be remapped `key={"shift": "shiftKey", "ctrl": "ctrlKey", "meta": "metaKey"}`. Valid keys are `shift`, `ctrl` and `meta`. Valid values are `shiftKey`, `ctrlKey`, `metaKey` (command on Mac and Windows on Windows) and `altKey` (option on Mac and Alt on Windows).
-   The tool bar of the viewer is now icons only.
-   The icons of he extension are SVG now, and hence follow the black/white style of VS Code.
-   `show_all` has a parameter `force=True` to override the skipping behavior it has for visual debugging.
-   Apple Silicon build123d install command is updated.

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
