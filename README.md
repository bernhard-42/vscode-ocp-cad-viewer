# _OCP CAD Viewer_ for VS Code

_OCP CAD Viewer_ for VS Code is an extension to show [CadQuery](https://github.com/cadquery/cadquery) and [build123d](https://github.com/gumyr/build123d) objects in VS Code via the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) viewer component.

## Installation

### Prerequisites

- A fairly recent version of Microsoft VS Code, e.g. 1.85.0 or newer
- The [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) installed in VS Code
- Necessary tools:
  - `python` and `pip` available in the Python enviroment that will be used for CAD development. Note, even when you use another package manager, `pip ` is needed internallyand needs to be available.

**Notes**:

- To use OCP CAD Viewer, start VS Code from the commandline in the Python environment you want to use or select the right Python interpreter in VS Code first. **OCP CAD Viewer depends on VS Code using the right Python interpreter** (i.e. mamba / conda / pyenv / poetry / ... environment).
- For VSCodium, the extension is not available in the VS code market place. You need to download the the vsix file from the [release folder](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) and install it manually.

### Installation

1. Open the VS Code Marketplace, and search and install _OCP CAD Viewer 2.7.0_.

   Afterwards the OCP viewer is available in the VS Code sidebar:

   ![](screenshots/ocp_icon.png)

2. Clicking on it shows the OCP CAD Viewer UI with the viewer manager and the library manager:

   ![](screenshots/init.png)

   You have 3 options:

   - Prepare _OCP CAD Viewer_ for working with [build123d](https://github.com/gumyr/build123d): Presse the _Quickstart build123d_ button.

     This will install _OCP_, _build123d_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip`

     ![](screenshots/build123d_installed.png)

   - Prepare _OCP CAD Viewer_ for working with [CadQuery](https://github.com/cadquery/cadquery): Presse the _Quickstart CadQuery_ button.

     This will install _OCP_, _CadQuery_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip`

     ![](screenshots/cadquery_installed.png)

   - Ignore the quick starts and use the "Library Manager" to install the libraries via `pip` (per default, this can be changed in the VS Code settings). Install the needed library by pressing the down-arrow behind the library name (hover over the library name to see the button) in the "Library Manager" section of the _OCP CAD Viewer_ sidebar. For more details, see [here](./docs/install.md)

   The Quickstarts will also

   - (optionally) install the the [Jupyter extension for VS Code from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
   - start the OCP viewer
   - create a demo file in a temporary folder to quickly see a simple usage example


**Notes:** 

- Do not use the _OCP CAD Viewer_ logo to verify your _OCP CAD Viewer_ settings! The logo overwrites all your settings in VS Code with its own settings to always look the same on each instance. Use a simple own model for checking your configuration

- If you run into issues, see [Troubleshooting](#troubleshooting)

## Usage

### Running code using Jupyter

- Start the _OCP CAD Viewer_ by pressing the box-arrow button in the "Viewer Manager" section of the _OCP CAD Viewer_ sidebar (hover over the `ocp_vscode` entry to see the button).
- Import ocp_vscode and the CAD library by using the paste button behing the library names in the "Viewer Manager" section
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

You can also use "Library Manager" in the _OCP CAD Viewer_ sidebar to manage the Python libraries for _build123d_, _cadquery_, _ipython_ and _ocp_tessellate_ (Presse the down-arrow when hovering over a library name to install/upgrade it)

### Extra topics

- [Quickstart experience on Windows](docs/quickstart.md)
- [Use Jupyter to execute code](docs/run.md)
- [Debug code with visual debugging](docs/debug.md)
- [Measure mode](docs/measure.md)
- [Use the `show` command](docs/show.md)
- [Use the `show_object` command](docs/show_object.md)
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
  --create_configfile            Create the configlie .ocpvscode_standalone in
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

Native tessellator can be set via `NATIVE_TESSELLATOR=1`and Python tessellator via `NATIVE_TESSELLATOR=0`.

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
      [19:56:07.114} INFO  ] ocp_vscode library version 2.6.1 matches extension version 2.6.1
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

  VS Code internal browser that renders the viewer component uses a cache for code and other artifacts. This includes WebGL artefacts like compiled shaders. It can happen that e.g. due to a graphic driver update the compiled version in the cache does not fit to the new driver. Then this error message appears.

  **Solution:** [Delete the VS Code browser cache on Linux](https://bobbyhadz.com/blog/vscode-clear-cache) (go to the section for your operating system)

## Changes

### v2.7.0

**Features**

- Stabilized the panel for measurement and fixed arrow cone size ([#159](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/159))
- Extended measurements to 3 digits ([#159](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/159))
- Adapted backend, config and show modules to also work as client for Jupyter Cadquery
- Support for OCCTs CompSolids (ocp-tessellate)
- Add support for ShapeLists of Compounds ([#149](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/149), ocp-tessellate)
- show_object now needs keyword args for name and options if provided

**Fixes**

- Fixed issue when loading snippets ([#157](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/157))
- Fixed top and bottom view to be exact ([#158](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/158))
- Fixed a bug when the viewer goes blank when a new object is to be shown while the dimension tool is active ([#156](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/156))
- Fixed top level bounding box when clicking on the top level label in the navigstion tree
- Fixed highlighting of cad tree node to prevent scrolling of parent container