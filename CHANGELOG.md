# Change Log

All notable changes to the "OCP CAD Viewer" extension will be documented in this file.

## 3.0.1

**Fixes**

-   Bring back explode tool and selection tool
-   Ensure jupyter console can be launched when the path contains spaces
-   Give the 'show' and 'get_defaults' parameter 'port' precedence over asking for a port
-   The standalone server wirtes its port to ~/.ocpvscode for show to pick it up
-   Reduced standalone output without --debug to a bare minimum
-   Streamlined standalone debugging output

## 3.0.0

**Features**

-   Viewer UI
    -   The grids are now dynamic: Fonts rescale when zooming to keep them the same size and grid refines when zoom factor doubles (and vice versa)
    -   Automatic theme switch (dark/bright) when theme of OS or browser is changed => NOTE: Unselect Ocp Cad Viewer > View:Dark in the VS Code settings!
    -   The `tick` hint parameter now only refers to the positive axis and defaults to `5` (so overall it is still `10`), see [migration](./README.md#migration-from-v290-to-v30x)
    -   Help dialog can be closed by clicking outside on the canvas
-   `show` command
    -   `reset_camera` now supports `Camera.ISO`, `Camera.TOP`, `Camera.BOTTOM`, `Camera.LEFT`, `Camera.RIGHT`, `Camera.FRONT`, and `Camera.BACK` as new orientation defaults for the viewer ([#189](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/189))
    -   Joints are now shown with suffix `.joints` on the same level as the object they are attached to, in order to not change the overall assembly hierarchy needed for animation, ([#138](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/138))
    -   Animation of joints now needs to provide `animate_joints` parameter (in synch with `render_joints`), see [migration](./README.md#migration-from-v290-to-v30x)
    -   Trim infinite axes and planes to 10 x `helper_scale` ([#192](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/192))
    -   `helper_scale < 1.0` is treated as a relative scale: the absolute `helper_scale` will be calculated as the relative value times max bounding box size, i.e. `helper_scale`s is a percentage of the max bounding box. For inifinite objects, helper_scale will be set to 1.0
    -   Allow `tree_width` to be changed by each `show` command
    -   List with unviewable objects only are not shown as empty objects any more but ignored
-   Standalone
    -   HTTP root redirect of http://localhost:8080 in standalone mode to show the viewer (no need of using http://localhost:8080/viewer any more)
-   Library manager
    -   The library manager will now install `ocp_vscode~={ocp_vscode_version}` per default, to simplifiy pure Python patch distribution (patch verions are compatible with the viewer). NOTE: Check your user/workspace settings.
    -   Small restructuring of the Library Manager list (`editable` now is only visible when the package is editable, and then shows the project path)
    -   Added `cadquery_ocp` to default install commands
-   Support for pure `uv` environments without `pip`. The viewer now tries `/env/path/to/python -m pip list` for the library manager and if that fails it uses `uv pip list -p /env/path/to/python`. The install commands in the workspace settings need to change to use `uv add -p {python}`, see [here](./README.md#uv-config-for-settings) [#166](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/166)
-   Support for [GDS chip design format](https://en.wikipedia.org/wiki/GDSII)
    -   Add polygon renderer for GDS files
    -   Add a z-scale tool for GDS files

**Fixes**

-   Fix `tree_width` to be respected when `no_glass` is `false` ([#194](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/194))
-   Fix error when project path contains spaces, especially for `pip list` ([#197](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/197))
-   Add back default of 240 to standalone viewer call ([#195](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/195), [#196](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/196))
-   Bump questionary to fix VSplit error
-   Properly add `alt` key to keymap
-   Change body element to respect the selected theme
-   Fix new behavior of VS Code in status bar handling to ensure status bar is always visible
-   Properly check ports vor IPv4 and IPv6 for standalone to avoid using the same port twice, once for IPv4 and once for IPv6
-   three-cad-viewer
    -   Change memory management to a new paradigm using a global function deepDispose which works recursively
    -   Fix setCameraTarget
    -   Fix keymapping regression where keymaps were not used any more

## v2.9.0

-   The viewer now supports widths of < 815px with shrunken toolbar (using ellipsis). From 815px width the toolbar is fully visible ([#187](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/187))
-   The view preset buttons in the toolbar now respect shift and will center the to all visible objects only ([#185](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/185))
-   Brought back restoring the OCP Viewer when VS Code is restarted ([#177](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/177))
-   Reworked measure mode ([#175](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/175))
    -   Changed shift modifier in distance measure mode to distinguish between min and center distance
    -   Removed angle measure button, it is integrated in distance measure now, and simplified filter management without angle measure in the UI

## v2.8.9

**Fixes**

-   Add a robust port-in-use detection to Windows

## v2.8.8

**Fixes**

-   Fix regression of wrong level for continue statement leading to show_all crashing

## v2.8.7

**Fixes**

-   Startup now checks all visible python files for trigger statements. If any has, autostart kicks in.
-   More than two Viewer columns are supported
-   Fixed a bug where an empty `~/.ocpvscode` file crashed `show` [#183](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/183)
-   Fixed calling jupyter console
-   Moved all `show_all` warnings behind `debug=True` parameter

## v2.8.6

**Features**

-   Fixed blank viewer issue by resolving a race condition properly ([#171](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/171))
-   Made statements that trigger OCP CAD Viewer to start editable in settings (`Ocp Cad Viewer > Advanced : Autostart Triggers`). They now default to `import ocp_vscode` and `from ocp_vscode import` and don't include "build123d" and "cadquery" any more
-   Set backend precision to 3 ([#179](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/179))
-   Clicking on a tree label with shift+meta hides all others without change of location ([#178](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/178))
-   Hid the `show_all` warnings about non viewable types. Can still be seen with the `debug` parameter
-   Added a button to the quickstart welcome screen to change the environment

**Fixes**

-   Fix broken check for ocp_vscode when it is installed in user site-packages ([#181](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/181))
-   Ensured to refresh library and viewer manager at VS Code start, even when build123d is not imported ([#177](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/177))
-   Fix broken helix discretizing ([#176](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/176))
-   Ensure that lines and arrows for measurements are initialized once only to remove memory leaks ([#29](https://github.com/bernhard-42/three-cad-viewer/issues/29))
-   Disable text selection of UI elements except info box
-   Fix isolate mode when there are only 1-dim objects in the viewer ([#178](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/178))
-   Keep camera position when "Isolate element" action is taken ([#174](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/174))

## v2.8.5

**Fixes**

-   Clean up viewerStarting flag in error case
-   Fix broken handling of mirrored curve in ocp-tessellate ([#170](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/170))
-   Remove deviding line deflection by 100 ([#172](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/172))

## v2.8.4

**Fixes**

-   Add handling of view log mesage forwarding to standalone mode

## v2.8.3

**Fixes**

-   Fix dual stack port detection on Linux ([#171](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/171))
-   Close old viewer window if exists on viewer start

## v2.8.2

**Features**

-   Add clear and update params to push_object
-   Add removal and update of an individual part in show_object
-   Introduce shortcuts select_face, select_edge, select_vertex for the selection mode

**Fixes**

-   Rewrite port check and add more debug info
-   Ensure to wait for all async functions at startup
-   Fix grid_xz / grid_yz mix-up in standalone mode
-   Improve logging during viewer start

## v2.8.1

**\*Fixes**

-   Fixed typos in doc strings and everywhere else
-   Fixed a f-string issue with broken quotes
-   Enhanced port running check to tcp4 and tcp6
-   Documented visual debugging with pdb ([#164](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/164))

## v2.8.0

**Features**

-   Add a color marker behind the node name of the navigation tree showing the object color
-   New "select objects" mode that allows to retrieve stable object indices that can be used in python code to selct objects
-   Removed the need of an open workspace. If the extension cannot identify a Python environment with ocp_vscode, it asks for it. ([#160](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/160), [#163](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/163))
-   Simplified port detection. Every viewer stores its port into `~/.ocpvscode`. If mode than one active port is detected, show let's you select the right one ([#163](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/163))
-   Improve startup reliability and performance
-   Allow setting port in launch.json
-   Add `include` argument to `show_all`
-   Add `push_object` and `show_objects` to control showing objects in a lazy manner
-   Bump to three-cad-viewer 3.4.0

**Fixes**

-   Clean up startup sequence and fix start issues with Jupyter interactive window
-   Fix disposing all viewer objects on closing the viewer
-   Ensure revive of viewer is not used in autostart mode
-   Improve pip list parsing
-   Start backend with a temp folder instead of work directory
-   Fix naming `vertex0` to `vertex_0` (and so on) in exploded mode (three-cad-viewer)
-   Fix clear and dispose behavior (three-cad-viewer [#27](https://github.com/bernhard-42/three-cad-viewer/issues/27))
-   Fix `save_screenshot` throwing an error ([#162](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/162))

## v2.7.1

**Fixes**

-   Use three-cad-viewer 3.3.4 (omit non used Javacscript packages)
-   Fix is_jupyter_cadquery condition

## v2.7.0

**Features**

-   Stabilized the panel for measurement and fixed arrow cone size ([#159](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/159))
-   Extended measurements to 3 digits ([#159](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/159))
-   Adapted backend, config and show modules to also work as client for Jupyter Cadquery
-   Support for OCCT's CompSolids (ocp-tessellate)
-   Add support for ShapeLists of Compounds ([#149](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/149), ocp-tessellate)
-   `show_object` now needs keyword args for `name` and `options` if provided
-   Measure backend can now be started via `python -m ocp_vscode --backend [--backend 3939]`

**Fixes**

-   Fixed issue when loading snippets ([#157](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/157))
-   Fixed top and bottom view to be exact ([#158](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/158))
-   Fixed a bug when the viewer goes blank when a new object is to be shown while the dimension tool is active ([#156](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/156))
-   Fixed top level bounding box when clicking on the top level label in the navigation tree
-   Fixed highlighting of cad tree node to prevent scrolling of parent container

## v2.6.4

Re-release due to release issues

## v2.6.3

**Fixes:**

-   Bump version of ocp-tessellate in pyproject.toml to >=3.0.10

## v2.6.2

**Fixes:**

-   Installation now uses pip on all platforms - see also "Breaking changes" ([#68](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/68))
-   Removed special handling of installations on Apple Silicon ([#84](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/84))
-   Print enter/return after tessellation ([#120](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/120))
-   Eliminate requirement for `set_port(3939)` in "standalone" mode ([#121](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/121))
-   Started fixing memory leak - about 90% done ([#123](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/123))
-   Remove XYZ axes from bottom left corner of save_screenshot ([#124](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/124))
-   Fixed rendering a compound made of multiple object types ignoring labels and colors ([#125](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/125))
-   Fixed double clicking a vertex or edge throwing an error in Javascript ([#129](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/129))
-   The help dialog is height restricted and uses vertical scrollbars on too small screens ([#131](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/131))
-   Fixed an issue in visual Debugging ([#134](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/134))
-   Fixed an issue that nested compounds did not render properly ([#135](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/135))
-   Ensure objects are properly centered when tools are disabled. ([#136](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/136))
-   ImageFace is shown again with `show_all()` ([#137](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/137))
-   Ensure that `reset_camera=Camera.CENTER` properly centers the object ([#139](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/139))
-   Quickstart and libraries now install from pypi and not any more from git - see also "Breaking changes" ([#143](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/143))
-   Fixed incorrect display of moved compounds ([#145](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/145))
-   Added a warning for standalone when browser hasn't been refresh after restart ([#146](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/146))
-   Fixed `save_screenshot` for standalone server ([#147](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/147))

**New features:**

-   Introduced a VS Code setting for OCP CAD Viewer reset_camera=Camera.KEEP the default behavior ([#144](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/144))

**Docs**

-   Provide better documentation for show_all ([#142](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/142))

**Breaking changes:**

-   The install commands for libraries and the quickstart commands have been simplified. There is just one configurable command now that uses `pip`. For any other package manager, the command needs to be outdated in settings.
    Open `settings.json` and remove the old configuration. Then use the VS Code preferences to change the new defaults to your linking.
    The extension identifies the situation where updated configurations are loaded from the local `settings.json` and provides these error messages:

    -   "Your installCommands are outdated. Please update them in your settings.json ('OcpCadViewer.advanced.installCommands')"

    -   "Your Quickstart is outdated. Please update them in your settings.json ('OcpCadViewer.advanced.quickstartCommands')"

-   Until cadquery 2.6 is on pypy: When you want to install build123d and cadquery in parallel, you first need to change the cadquery install command to

    ```bash
    [
      "{unset_conda} {python} -m pip install --upgrade git+https://github.com/CadQuery/cadquery.git"
    ]
    ```

## v2.6.1

**Fixes:**

-   Standalone viewer can listen to other IP addresses of the machine than 127.0.0.1
-   `show` now uses port 3939 as default when no port could be detected and a service listens to 3939
-   Fixed a bug in ocp-tessellate for cadquery wires ([#116](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/116))
-   Fixed a bug in backend for measures that prevented faces being inspected ([#115](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/115))
-   Fixed a bug that shifted the orientation too high for the logo screen

## v2.6.0

**New features:**

-   Standalone mode without VS Code: `python -m ocp_vscode`. This will start a Flask server and the viewer can be reached under `http://127.0.0.1/viewer`.

**Fixes:**

-   Fix that `show_all` doesn't ignore `_123` and similar variable names

## v2.5.3

-   Fix regression that backend couldn't start on Windows (wrong quotes)

## v2.5.0

**New features**

-   New click-to-center feature: shift-meta left-click at any point will take this point projected on the objects as the viewing target ([#95](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/95))
-   Measure selections can be fully deselected on right mouse click ([#94](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/94))
-   The command `show` now warns only when viewer is not running to allow export objects without viewing ([#98](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/98))

**Fixes:**

-   Change `reset_camera=Camera.KEEP` to adapt zoom so that view doesn not "jump" ([#105](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/105))
-   Use cachetools 5.5.0 to support Python 3.12. Additionally the resize button will now always resize to zoom level 1.0 ([#107](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/107))
-   Python paths in the extension are now quoted to allow paths with spaces ([#102](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/102))
-   The viewer window was slightly shifted to the left and did not fit the VSCode window ([#101](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/101))

## v2.4.1

-   Fix colormap handling to keep color of objects when .color attribute is set
-   show() ends gracefully and empty lists are treated correctly

## v2.4.0

**New features**

-   Removed `measure_tools` parameter and integrated switching between normal and measure mode into the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer/blob/master/src/treeview.js) ([#58](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/58)).
-   Rewrote the CAD view tree to use lazy loading (switching to measure mode can increase number of nodes by more then 100 times). This changed the input format for the viewer component (states integrated into object tree now), which is a breaking change if you use threee-cad-viewer directly, but no changes for users of vscode-ocp-cad-viewer.
-   Rewrote converter of [ocp-tessellate](https://github.com/bernhard-42/ocp-tessellate/blob/main/ocp_tessellate/convert.py) to be more consistent and easier to maintain. All solids and faces can now be instances. Breaking changes if you use ocp_tessellate directly, but no changes for users of vscode-ocp-cad-viewer.
-   Added `center_grid` to workspace configuration to ensure grid planes always go through world origin ([#77](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/77)).
-   Added `save_screenshot(filename)` to save a PNG of the currently shown object(s). Canvas only, no CAD tools ([#86](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/86)).
-   Support viewing of build123d `LocationList`s.

**Fixes**

-   Fixed the mini-build123d `Location` class used by measurement backend.
-   Measure mode cannot work on clipped object, so disabled clipping tab when measure mode is turned on ([#55](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/55), [#70](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/70))
-   Removed using `to_tuple` for build123d Color objects ([#69](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/69)).
-   Made color handling more consistent (sometime `color` or `alpha` was ignored).
-   Fixed opening duplivcate Jupyter notebooks ([#78](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/78)).
-   Fixed measure tool related regression. ([#81](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/81), [82](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/82),).
-   Fixed ImageFace aspect ratio bug ([#83](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/83)).
-   Fixed `show_all` failing on empty ShapeList ([#90](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/90)).
-   Fixed to display ShapeList of Compound correctly ([#91](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/91)).
-   Fixed ShapeList containing different object types ([#92](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/92)).
-   Fixed measure tools to work with 1D objects ([#93](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/93)).

## v2.3.3

-   Fix regression that visual debug hangs
-   Fix regression that build123d sketches are not draw correctly any more (fix in ocp-tessellate)

## v2.3.2

-   Fix regression that Python script hang in threading before exit ([#73](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/60))

## v2.3.1

-   Add latest ocp-tessellate to fixed regression with handling instances
-   Make native default if ocp-addons exists

## v2.3.0

Fine tune communication to ensure the memory view of buffers will be passed through to javascript for performance (\*)
Use of the new protocol v3 of three-cad-viewer
Fix show_all regressions https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/71. It should also properly catch exceptions now to not interrupt viausl debugging
Add newest ocp-tessellate to allow using native tessellator from ocp_addons

## v2.2.2

-   Fix regression in measure tools

## v2.2.1

-   Fix: Wrong back material color for faces
-   Improve parameters of Imageface
-   Improve clipping when faces are deselected

## v2.2.0

-   Clipping now works with caps (default: red, green, blue cap faces). For assemblies the cap faces can use the associated object colors
-   Grid now can be centered (parameter: `center_grid=True`):
    With axes0==True centered at the origin `(0,0,0)`, i.e absolute units
    With axes0==False centered at the center of mass, i.e relative units
-   Grid now has numbers at the gridlines serving as a ruler ([#60](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/60))
-   `ocp_vscode` now has a class `ImageFace`. It works like an OCP rectangle, but can get an image path and a location ([#28](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/28)).
    Usage: `plane = ImageFace(image_path, width, location=Location((x, y, z), (ax, ay, az)))`
-   The CAD tree changed behavior: The eye icon toggles both faces and edges. The mesh icon toggles the mesh (edges) only ([#56](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/56))
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

## v2.1.1

-   Fix Jupyter Console for non-workspace mode
-   Enforce using latest ocp-tesellate 2.0.6

## v2.1.0

-   Introduce a minimum version of build123d for backend.py to remove the Python dependency on buidl123d.
-   Changed the state handling: instead of distributed `.ocp_vscode` files, there is now one central `$HOME/.ocpvscode` file.
-   Experimental Jupyter console support: When starting an interacive session, the kernel connection file will be writte to `$HOME/.ocpvscode`.
    This file will be used in the Viewer Manager under _jupyter console_ to open the jupyter console as another client for the kernel
-   Use a VS Code Terminal for the backend so that it is no black box any more
-   Enforce using latest ocp-tesellate 2.0.5
-   Streamline the vsix to be <1MB

## v2.0.13

-   Fix shortcut boolean parameter for grid
-   Update dependencies for installing build123d on Apple Silicon
-   Ensure terminal is shown during installations
-   Refactor getCurrentFolder
-   Create demo file in current folder instead of temp folder
-   Use new environment API to get Python path
-   Handle showing empty CAD objects with show_all
-   Ensure to set ocp_vscode_version for quick install
-   Add python 3.11 for Apple Silicon machines

## v2.0.6

-   Add three-cad-viewer 2.1.2 to fix black edges issue in measure mode and remove angle tool resizing

## v2.0.4

-   Fix regression of ocp-tessallate version

## v2.0.3

-   Fix regression in port detection
-   Added missing dependencies for build123d on Apple Silicon

## v2.0.2

-   Fix .ocp_vscode detection on Windows
-   Fix showing ShapeList[Vector]
-   Viewer now starts when VS Code opens with a build123d/cadquery Python file

## v2.0.1

-   Introduce a workspace configuration `initialPort` for OCP CAD Viewer
-   Change the warning about used port to an auto vanishing info

## v2.0.0

-   Introduce measure mode. Use `set_defaults(measure_tools=True)` or `show(obj, measure_tools=True)` or the global workspace confiv of OCP CAD Viewer to turn it on. This release added a Python backend process that communicates with the viewer for providing correct BRep measurement info.
-   Autostart viewer: When opening or saving a Python file that includes `import cadquery`, `import build123d`, `from cadquery import` or `from build123d import`, the viewer gets started if it is not already running. Use `OcpCadViewer.autostart` configuration of workspace config to turn this feature off.
-   Environment variable OCP_PORT is supported. It will be used by the viewer and the `show*` clients as the port for OCP CAD Viewer. This variable can be set on the command line or in `launch.json` (`"env": {"OCP_PORT": "3999"}`).
-   `CAMERA.KEEP` and `CAMERA.CENTER` now persist the viewer across execution sessions. If you want to reset at every beginning, use `show(objs, reset_camer=Camera.RESET)` as the first show command.
-   Modifier keys can now be remapped `key={"shift": "shiftKey", "ctrl": "ctrlKey", "meta": "metaKey"}`. Valid keys are `shift`, `ctrl` and `meta`. Valid values are `shiftKey`, `ctrlKey`, `metaKey` (command on Mac and Windows on Windows) and `altKey` (option on Mac and Alt on Windows).
-   The tool bar of the viewer is now icons only.
-   The icons of he extension are SVG now, and hence follow the black/white style of VS Code.
-   `show_all` has a parameter `force=True` to override the skipping behavior it has for visual debugging.
-   Apple Silicon build123d install command is updated.

## v1.2.2

-   Replace the boolean values for `reset_camera` with the `Camera` enum; `reset_camera` now supports `Camera.RESET` (works like `True` before), `Camera.CENTER` (works like `False` before) and `Camera.KEEP` (additionally keeps the pan location). See best practices for details.
-   Replace the values for `collapse` with the `Collapse` enum: `Collapse.ALL` (was `"C"`), `Collapse.None` (was `"E"`), `Collapse.LEAVES` (was `"1"` or `1`) and `Collapse.Root` (was `"R"`)
-   Added a button to toggle the output panel for OCP CAD Viewer
-   Visual debug is on by default now (workspace setting `WatchByDefault` to `true`)
-   Changed behavior of ` show` during debug session: `show` will be executed, however, visual debug step omitted
-   Do not show Jupyter variables `_`, `__`, `_1`, `_2`, ... in `show_all`
-   Fix an error where the orientation marker was partly or fully moved outside its view due to panning of the object ([vscode-ocp-cad-viewer issue #22](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/22))

## v1.2.1

-   XYZ labels for orientation marker ([vscode-ocp-cad-viewer issue #13](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/13))
-   Support for metalness and roughness ([three-cad-viewer issue #9](https://github.com/bernhard-42/three-cad-viewer/issues/9))
-   New "Material" configurator tab in the viewer UI
-   Port 3939 will automatically incremented by 1 for 2nd, 3rd, ... viewer
-   Fix: OCP_Part can be shown now ([vscode-ocp-cad-viewer issue #20](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/20))
-   Fix: reset_camera respects panning ([vscode-ocp-cad-viewer issue #19](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/19))
-   Fix: `collapse="C"` also collapses single item trees ([vscode-ocp-cad-viewer issue #18](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/18))
-   Fix: Show_all supports having a sketch that uses face as a workplane ([vscode-ocp-cad-viewer issue #17](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/17))
-   Fix: `_config==undefined` is handled properly ([vscode-ocp-cad-viewer issue #12](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/12))

## v1.1.3

-   Fix racing conditions that prevented having more than one viewer window
-   No need to add port for next viewer any more. The default port 3939 will be incremented until a free port is found
-   Use ocp-tessellate 1.1.1 (fixes axis helper scale)

## v1.1.2

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
