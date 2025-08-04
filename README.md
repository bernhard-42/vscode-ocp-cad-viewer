# _OCP CAD Viewer_ for VS Code

_OCP CAD Viewer_ for VS Code is an extension to show [CadQuery](https://github.com/cadquery/cadquery) and [build123d](https://github.com/gumyr/build123d) objects in VS Code via the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) viewer component.

## Installation

### Prerequisites

- A fairly recent version of Microsoft VS Code, e.g. 1.85.0 or newer
- The [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) installed in VS Code
- Necessary tools:
  - `python` and `pip` available in the Python environment that will be used for CAD development. Note, even when you use another package manager, `pip ` is needed internally and needs to be available.

**Notes**:

- To use OCP CAD Viewer, start VS Code from the commandline in the Python environment you want to use or select the right Python interpreter in VS Code first. **OCP CAD Viewer depends on VS Code using the right Python interpreter** (i.e. mamba / conda / pyenv / poetry / ... environment).
- For VSCodium, the extension is not available in the VS code market place. You need to download the the vsix file from the [release folder](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) and install it manually.

### Installation

1. Open the VS Code Marketplace, and search and install _OCP CAD Viewer 2.9.0_.

   Afterwards the OCP viewer is available in the VS Code sidebar:

   ![](screenshots/ocp_icon.png)

2. Clicking on it shows the OCP CAD Viewer UI with the viewer manager and the library manager:

   ![](screenshots/init.png)

   You have 3 options:

   - Prepare _OCP CAD Viewer_ for working with [build123d](https://github.com/gumyr/build123d): Press the _Quickstart build123d_ button.

     This will install _OCP_, _build123d_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip`

     ![](screenshots/build123d_installed.png)

   - Prepare _OCP CAD Viewer_ for working with [CadQuery](https://github.com/cadquery/cadquery): Press the _Quickstart CadQuery_ button.

     This will install _OCP_, _CadQuery_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip`

     ![](screenshots/cadquery_installed.png)

   - Ignore the quick starts and use the "Library Manager" to install the libraries via `pip` (per default, this can be changed in the VS Code settings). Install the needed library by pressing the down-arrow behind the library name (hover over the library name to see the button) in the "Library Manager" section of the _OCP CAD Viewer_ sidebar. For more details, see [here](./docs/install.md)

   Quickstart will also

   - (optionally) install the the [Jupyter extension for VS Code from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
   - start the OCP viewer
   - create a demo file in a temporary folder to quickly see a simple usage example


**Notes:** 

- Do not use the _OCP CAD Viewer_ logo to verify your _OCP CAD Viewer_ settings! The logo overwrites all your settings in VS Code with its own settings to always look the same on each instance. Use a simple own model for checking your configuration

- If you run into issues, see [Troubleshooting](#troubleshooting)

## Usage

### Running code using Jupyter

- Start the _OCP CAD Viewer_ by pressing the box-arrow button in the "Viewer Manager" section of the _OCP CAD Viewer_ sidebar (hover over the `ocp_vscode` entry to see the button).
- Import ocp_vscode and the CAD library by using the paste button being the library names in the "Viewer Manager" section
- Use the usual Run menu to run the code

![Running code](screenshots/ocp_vscode_run.png)

### Debugging code with visual debugging

After each step, the debugger checks all variables in `locals()` for being CAD objects and displays them with their variable name.
Note:

- Check that `OCP:on` is visible in the status bar
- It also shows planes, locations and axis, so name your contexts
- It remembers camera position and unselected variables in the tree
- during debugging, `show` and `show_object` are disabled. They interfere with the visual debugging

![Debugging code](screenshots/ocp_vscode_debug.png)

### Library Manager

You can also use "Library Manager" in the _OCP CAD Viewer_ sidebar to manage the Python libraries for _build123d_, _cadquery_, _ipython_ and _ocp_tessellate_ (Press the down-arrow when hovering over a library name to install/upgrade it)

### Extra topics

- [Quickstart experience on Windows](docs/quickstart.md)
- [Use Jupyter to execute code](docs/run.md)
- [Debug code with visual debugging](docs/debug.md)
- [Measure mode](docs/measure.md)
- [Object selection mode](docs/selector.md)
- [Use the `show` command](docs/show.md)
- [Use the `show_object` command](docs/show_object.md)
- [Use the `push_object` and `show_objects` command](docs/push_object.md)
- [Use the `show_all` command](docs/show_all.md)
- [Use the `set_viewer_config` command](docs/set_viewer_config.md)
- [Download examples for build123d or cadquery](docs/examples.md)
- [Use the build123d snippets](docs/snippets.md)

## Standalone mode

Standalone mode allows to use OCP CAD Viewer without VS Code: `python -m ocp_vscode`. This will start a Flask server and the viewer can be reached under `http://127.0.0.1/viewer`. All client side feature of the VS Code variant (i.e. `show*` features) should be available (including measurement mode) except visual debugging (see above) which relies on VS Code.

Use `python -m ocp_vscode --help` to understand the command line args:
```
Usage: python -m ocp_vscode [OPTIONS]

Options:
  --create_configfile            Create the config file .ocpvscode_standalone in
                                 the home directory
  --host TEXT                    The host to start OCP CAD with
  --port INTEGER                 The port to start OCP CAD with
  --debug                        Show debugging information
  --timeit                       Show timing information
  --tree_width TEXT              OCP CAD Viewer navigation tree width
                                 (default: 240)
  --no_glass                     Do not use glass mode with transparent
                                 navigation tree
  --theme TEXT                   Use theme 'light' or 'dark' (default:
                                 'light')
  --no_tools                     Do not show toolbar
  --tree_width INTEGER           Width of the CAD navigation tree (default:
                                 240)
  --control TEXT                 Use control mode 'orbit'or 'trackball'
  --up TEXT                      Provides up direction, 'Z', 'Y' or 'L'
                                 (legacy) (default: Z)
  --rotate_speed INTEGER         Rotation speed (default: 1)
  --zoom_speed INTEGER           Zoom speed (default: 1)
  --pan_speed INTEGER            Pan speed (default: 1)
  --axes                         Show axes
  --axes0                        Show axes at the origin (0, 0, 0)
  --black_edges                  Show edges in black
  --grid_xy                      Show grid on XY plane
  --grid_yz                      Show grid on YZ plane
  --grid_xz                      Show grid on XZ plane
  --center_grid                  Show grid planes crossing at center of object
                                 or global origin(default: False)
  --collapse INTEGER             leaves: collapse all leaf nodes, all:
                                 collapse all nodes, none: expand all nodes,
                                 root: expand root only (default: leaves)
  --perspective                  Use perspective camera
  --ticks INTEGER                Default number of ticks (default: 10)
  --transparent                  Show objects transparent
  --default_opacity FLOAT        Default opacity for transparent objects
                                 (default: 0.5)
  --explode                      Turn explode mode on
  --angular_tolerance FLOAT      Angular tolerance for tessellation algorithm
                                 (default: 0.2)
  --deviation FLOAT              Deviation of for tessellation algorithm
                                 (default: 0.1)
  --default_color TEXT           Default shape color, CSS3 color names are
                                 allowed (default: #e8b024)
  --default_edgecolor TEXT       Default color of the edges of shapes, CSS3
                                 color names are allowed (default: #707070)
  --default_thickedgecolor TEXT  Default color of lines, CSS3 color names are
                                 allowed (default: MediumOrchid)
  --default_facecolor TEXT       Default color of faces, CSS3 color names are
                                 allowed (default: Violet)
  --default_vertexcolor TEXT     Default color of vertices, CSS3 color names
                                 are allowed (default: MediumOrchid)
  --ambient_intensity INTEGER    Intensity of ambient light (default: 1.00)
  --direct_intensity FLOAT       Intensity of direct light (default: 1.10)
  --metalness FLOAT              Metalness property of material (default:
                                 0.30)
  --roughness FLOAT              Roughness property of material (default:
                                 0.65)
  --help                         Show this message and exit.
```

## Standalone mode with Docker

If you are not using vscode and you prefer to keep the standalone web viewer running separated in a container,
then take a look at [docker-vscode-ocp-cad-viewer](https://github.com/nilcons/docker-vscode-ocp-cad-viewer).

## Best practices

- Use the **Jupyter extension** for a more interactive experience. This allows to have one cell (separated by `# %%`) at the beginning to import all libraries

  ```python
  # %%
  from build123d import *
  from ocp_vscode import *

  # %%
  b = Box(1,2,3)
  show(b)
  # %%
  ```

  and then only execute the code in the cell you are currently working on repeatedly.

- The **config system** of OCP CAD Viewer

  There are 3 levels:

  - Workspace configuration (part of the VS Code settings, you can access them e.g. via the gear symbol in OCP CAD Viewer's "Viewer Manager" when you hover over the label "VIEWER MANAGER" to see the button)
  - Defaults set with the command `set_defaults` per Python file
  - Parameters in `show` or `show_object` per command

  `set_defaults` overrides the Workspace settings and parameters in `show` and `show_config` override the other two.

  Note that not all parameters are available in the global Workspace config, since they don't make sense globally (e.g. `helper_scale` which depends on the size of the boundary box of the currently shown object)

  A common setup would be

  ```python
  # %%
  from build123d import *
  import cadquery as cq

  from ocp_vscode import *
  set_port(3939)

  set_defaults(reset_camera=False, helper_scale=5)

  # %%
  ...
  ```

  Explanation

  - The first block imports build123d and CadQuery (omit what you are not interested in).
  - The second block imports all commands for OCP CAD Viewer. `set_port` is only needed when you have more than one viewer open and can be omitted for the first viewer)
  - The third block as an example sets helper_scale and reset_camera as defaults. Then every show_object or show command will respect it as the default

- Debugging build123d with `show_all` and the **visual debugger**

  - If you name your contexts (including `Location` contexts), the visual debugger will show the CAD objects assigned to the context.

  - Use `show_all` to show all cad objects in the current scope (`locals()`) of the Python interpreter (btw. the visual debugger uses `show_all` at each step)

    ```python
    # %%
    from build123d import *
    set_defaults(helper_scale=1, transparent=True)

    with BuildPart() as bp:
        with PolarLocations(3,8) as locs:
            Box(1,1,1)

    show_all()
    # %%
    ```

    ![named contexts](./screenshots/context_vars.png)

- **Keep camera orientation** of an object with `reset_camera`

  Sometimes it is helpful to keep the orientation of an object across code changes. This is what `reset_camera` does:

  - `reset_camera=Camera.Center` will keep position and rotation, but ignore panning. This means the new object will be repositioned to the center (most robust approach)
  - `reset_camera=Camera.KEEP` will keep position, rotation and panning. However, panning can be problematic. When the next object to be shown is much larger or smaller and the object before was panned, it can happen that nothing is visible (the new object at the pan location is outside of the viewer frustum). OCP CAD Viewer checks whether the bounding box of an object is 2x smaller or larger than the one of the last shown object. If so, it falls back to `Camera.CENTER`. A notification is written to the OCP CAD Viewer output panel.
  - `reset_camera=Camera.RESET` will ensure that position, rotation and panning will be reset to the initial default

## Development

Testing:

Native tessellator can be set via `NATIVE_TESSELLATOR=1` and Python tessellator via `NATIVE_TESSELLATOR=0`.

When `OCP_VSCODE_PYTEST=1` is set, `show` will not send the tessellated results to the viewer, but return it to the caller for inspection.

A full test cycle consist of:

```bash
NATIVE_TESSELLATOR=0 OCP_VSCODE_PYTEST=1 pytest -v -s pytests/
NATIVE_TESSELLATOR=1 OCP_VSCODE_PYTEST=1 pytest -v -s pytests/
```

## Troubleshooting

- **Generic ("it doesn't work")**

  1) Confirm that VS Code extension and ocp_vscode have the same version. This can be seen in the OCP CAD Viewer UI. Or alternatively in the Output panel of VS Code:

      ```text
      2025-07-06 14:51:33.418 [info ] extension.check_upgrade: ocp_vscode library version 2.8.6 matches extension version 2.8.6
      ```

  2) Test whether the standalone viewer works, see [Standalone mode](#standalone-mode) (to eliminate VS Code issues)
  3) Open a work folder and not a Python file (to ensure we do not get in Python path problems)
  4) Check the Output panel. Search for:
      - `PythonPath: 'aaa/bbb/python'` **=> right Python environment?**
      - `Server started on port xxxx` (or so) **=> right port? default is 3939**
      - `Starting Websocket server` **=> should not be followed by an error**
      - `OCP Cad Viewer port: xxxx, folder: yyyy zzzz` **=> yyyy should be the right working folder?**
  5) If all looks fine until now, then toggle Developer tools in VS Code and check browser console. Often we see a WebGL error for the browser of VS Code used for the viewer.


- **CAD Models almost always are invisible in the OCP viewer window**

  ```bash
  three-cad-viewer.esm.js:20276 THREE.WebGLProgram: Shader Error 0 - VALIDATE_STATUS false

  Material Name:
  Material Type: LineBasicMaterial

  Program Info Log: Program binary could not be loaded. Binary is not compatible with current driver/hardware combination. Driver build date Mar 19 2024. Please check build information of source that generated the binary.
  Location of variable pc_fragColor conflicts with another variable.
  ```

  VS Code internal browser that renders the viewer component uses a cache for code and other artifacts. This includes WebGL artifacts like compiled shaders. It can happen that e.g. due to a graphic driver update the compiled version in the cache does not fit to the new driver. Then this error message appears.

  **Solution:** [Delete the VS Code browser cache on Linux](https://bobbyhadz.com/blog/vscode-clear-cache) (go to the section for your operating system)

## Changes

### v2.9.0

- The viewer now supports widths of < 815px with shrunken toolbar (using ellipsis). From 815px width the toolbar is fully visible ([#187](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/187))
- The view preset buttons in the toolbar now respect shift and will center the to all visible objects only ([#185](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/185))
- Brought back restoring the OCP Viewer when VS Code is restarted ([#177](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/177))
- Reworked measure mode ([#175](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/175))
  - Changed shift modifier in distance measure mode to distinguish between min and center distance
  - Removed angle measure button, it is integrated in distance measure now, and simplified filter management without angle measure in the UI

### v2.8.9

**Fixes**

- Add a robuts port in use detection to Windows

### v2.8.8

**Fixes**

- Fix regression of wrong level for continue statement leading to show_all crashing

### v2.8.7

**Fixes**

- Startup now checks all visible python files for trigger statements. If any has, autostart kicks in.
- More than two Viewer columns are supported
- Fixed a bug where an empty `~/.ocpvscode` file crashed `show` [#183](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/183)
- Fixed calling jupyter console 
- Moved all `show_all` warnings behind `debug=True` parameter

### v2.8.6

**Features**

- Fixed blank viewer issue by resolving a race condition properly ([#171](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/171))
- Made statements that trigger OCP CAD Viewer to start editable in settings (`Ocp Cad Viewer > Advanced : Autostart Triggers`). They now default to `import ocp_vscode` and `from ocp_vscode import` and don't include "build123d" and "cadquery" any more
- Set backend precision to 3 ([#179](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/179))
- Clicking on a tree label with shift+meta hides all others without change of location ([#178](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/178))
- Hid the `show_all` warnings about non viewable types. Can still be seen with the `debug` parameter
- Added a button to the quickstart welcome screen to change the environment

**Fixes**

- Fix broken check for ocp_vscode when it is installed in user site-packages ([#181](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/181))
- Ensured to refresh library and viewer manager at VS Code start, even when build123d is not imported ([#177](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/177))
- Fix broken helix discretizing ([#176](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/176))
- Ensure that lines and arrows for measurements are initialized once only to remove memory leaks ([#29](https://github.com/bernhard-42/three-cad-viewer/issues/29))  
- Disable text selection of UI elements except info box
- Fix isolate mode when there are only 1-dim objects in the viewer ([#178](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/178))
- Keep camera position when "Isolate element" action is taken ([#174](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/174))

### v2.8.5

**Fixes**

- Clean up viewerStarting flag in error case
- Fix broken handling of mirrored curve in ocp-tessellate ([#170](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/170))
- Remove deviding line deflection by 100 ([#172](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/172))

### v2.8.4

**Fixes**

- Add handling of view log mesage forwarding to standalone mode

### v2.8.3

**Fixes**

- Fix dual stack port detection on Linux ([#171](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/171))
- Close old viewer window if exists on viewer start

### v2.8.2

**Features**

- Add clear and update params to push_object
- Add removal and update of an individual part in show_object
- Introduce shortcuts select_face, select_edge, select_vertex for the selection mode

**Fixes**

- Rewrite port check and add more debug info
- Ensure to wait for all async functions at startup
- Fix grid_xz / grid_yz mix-up in standalone mode
- Improve logging during viewer start

### v2.8.1

***Fixes**

- Fixed typos in doc strings and everywhere else
- Fixed a f-string issue with broken quotes
- Enhanced port running check to tcp4 and tcp6
- Documented visual debugging with pdb ([#164](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/164))

### v2.8.0

**Features**

- Add a color marker behind the node name of the navigation tree showing the object color
- New "select objects" mode that allows to retrieve stable object indices that can be used in python code to select objects
- Removed the need of an open workspace. If the extension cannot identify a Python environment with ocp_vscode, it asks for it. ([#160](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/160), [#163](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/163))
- Simplified port detection. Every viewer stores its port into `~/.ocpvscode`. If mode than one active port is detected, show let's you select the right one  ([#163](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/163))
- Improve startup reliability and performance
- Allow setting port in launch.json
- Add `include` argument to `show_all`
- Add `push_object` and `show_objects` to control showing objects in a lazy manner
- Bump to three-cad-viewer 3.4.0


**Fixes**
- Clean up startup sequence and fix start issues with Jupyter interactive window
- Fix disposing all viewer objects on closing the viewer
- Ensure revive of viewer is not used in autostart mode
- Improve pip list parsing
- Start backend with a temp folder instead of work directory
- Fix naming `vertex0` to `vertex_0` (and so on) in exploded mode (three-cad-viewer)
- Fix clear and dispose behavior (three-cad-viewer [#27](https://github.com/bernhard-42/three-cad-viewer/issues/27))
- Fix `save_screenshot` throwing an error ([#162](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/162))
