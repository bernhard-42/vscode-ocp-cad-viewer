# Change Log

All notable changes to the "OCP CAD Viewer" extension will be documented in this file.

v2.3.1
- Add latest ocp-tessellate to fixed regression with handling instances
- Make native default if ocp-addons exists

v2.3.0
- Add newest ocp-tessellate to allow using native tessellator from ocp_addons
- Fine tune communication to ensure the memory view of buffers will be passed through to javascript for performance
- Use of the new protocol v3 of three-cad-viewer

v2.2.2
- Fix regression in measure tools

v2.2.1
-   Fix: Wrong back material color for faces
-   Improve parameters of Imageface
-   Improve clipping when faces are deselected

v2.2.0
-   Clipping now works with caps (default: red, green, blue cap faces). For assemblies the cap faces can use the associated object colors
-   Grid now can be centered (parameter: `center_grid=True`): 
    With axes0==True centered at the origin `(0,0,0)`, i.e absolute units
    With axes0==False centered at the center of mass, i.e relative units
-   Grid now has numbers at the gridlines serving as a ruler ([#60](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/60))
-   `ocp_vscode` now has a class `ImageFace`. It works like an OCP rectangle, but can get an image path and a location ([#28](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/28)). 
    Usage: `plane = ImageFace(image_path, width, location=Location((x, y, z), (ax, ay, az)))`
-   The CAD tree changed behavior: The eye icon toggles both faces and edges. The mesh icon toggles the mesh (edges) only  ([#56](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/56))
    This can be switched back to old behavior in the VS Code workspace settings _"OCP CAD Viewer > View:New_tree_behavior"_
-   New parameter `show_sketch_local`: when set to `False`, `build123d` local sketches will not be shown (works eith `set_defaults`) ([#59](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/59))
-   New parameter _"OCP CAD Viewer > Advanced:Autohide Terminal"_ in the VS Code workspace settings to control whether terminal will be hid when the viewer starts or not ([#61](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/61))
-   Viewer keeps clipping settings when `reset_camera` is set to `Camera.KEEP`or `Camera.CENTER` ([#43](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/43))
-   Material configurator now has a reset button "R" to get back to initial values
-   `show_all` now converts nested dicts and lists into viewer hierarchies
-   `set_viewer_config` is documented in README
-   Fix: `show_parent` now supported by `show_defaults` ([#64](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/64))
-   Fix: `show_all()` now works in non visual debugging mode (removed `force` parameter from `show_all`) 
-   Fix: `show_all()` now doesn't break when an array of `Colors` is in the `locals` variable list ([#45](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/45))
-   Fix: `show_all` now ignores unknown types in lists or dicts without raising an error and only printing a warning ([#67](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/67))
-   Fix: The `serialize` and `deserialize` commands don't crash on Windows any more ([#65](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/65))
-   Fix: Status notifications for grid work again ([#66](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/66))


v2.1.1
-   Fix Jupyter Console for non-workspace mode
-   Enforce using latest ocp-tesellate 2.0.6

v2.1.0
-   Introduce a minimum version of build123d for backend.py to remove the Python dependency on buidl123d.
-   Changed the state handling: instead of distributed `.ocp_vscode` files, there is now one central `$HOME/.ocpvscode` file.
-   Experimental Jupyter console support: When starting an interacive session, the kernel connection file will be writte to `$HOME/.ocpvscode`.
    This file will be used in the Viewer Manager under *jupyter console* to open the jupyter console as another client for the kernel
-   Use a VS Code Terminal for the backend so that it is no black box any more
-   Enforce using latest ocp-tesellate 2.0.5
-   Streamline the vsix to be <1MB


v2.0.13
-   Fix shortcut boolean parameter for grid
-   Update dependencies for installing build123d on Apple Silicon
-   Ensure terminal is shown during installations
-   Refactor getCurrentFolder
-   Create demo file in current folder instead of temp folder
-   Use new environment API to get Python path
-   Handle showing empty CAD objects with show_all
-   Ensure to set ocp_vscode_version for quick install
-   Add python 3.11 for Apple Silicon machines

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
