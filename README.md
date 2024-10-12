# _OCP CAD Viewer_ for VS Code

_OCP CAD Viewer_ for VS Code is an extension to show [CadQuery](https://github.com/cadquery/cadquery) and [build123d](https://github.com/gumyr/build123d) objects in VS Code via the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) viewer component.

## Installation

### Prerequisites

- A fairly recent version of Microsoft VS Code, e.g. 1.85.0 or newer
- The [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) installed in VS Code
- Necessary tools:
  - `python` and `pip` available in the Python enviroment that will be used for CAD development
  - The command `git` needs to be available
  - On a Silicon Apple computer the command `mamba` needs to be available. You might want to consider using [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge).

**Notes**:

- To use OCP CAD Viewer, start VS Code from the commandline in the Python environment you want to use or select the right Python interpreter in VS Code first. **OCP CAD Viewer depends on VS Code using the right Python interpreter** (i.e. mamba / conda / pyenv / poetry / ... environment).
- For VSCodium, the extension is not available in the VS code market place. You need to download the the vsix file from the [release folder](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) and install it manually.
- Currently, on a Silicon Mac (ARM CPU), _OCP_ and _CadQuery_ can only be installed via `mamba`, see 3. below.

### Installation

1. Open the VS Code Marketplace, and search and install _OCP CAD Viewer 2.5.0_.

   Afterwards the OCP viewer is available in the VS Code sidebar:

   ![](screenshots/ocp_icon.png)

2. Clicking on it shows the OCP CAD Viewer UI with the viewer manager and the library manager:

   ![](screenshots/init.png)

   You have 3 options:

   - Prepare _OCP CAD Viewer_ for working with [build123d](https://github.com/gumyr/build123d): Presse the _Quickstart build123d_ button.

     This will install _OCP_, _build123d_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip` (except for Apple Silicon machines that require `mamba` and will also install _cadquery_)

     ![](screenshots/build123d_installed.png)

   - Prepare _OCP CAD Viewer_ for working with [CadQuery](https://github.com/cadquery/cadquery): Presse the _Quickstart CadQuery_ button.

     This will install _OCP_, _CadQuery_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip` (except for Apple Silicon machines that require `mamba`)

     ![](screenshots/cadquery_installed.png)

   - Ignore the quick starts and use the "Library Manager" to install the libraries. Doing so, _OCP CAD Viewer_ let's you select whether to use `pip`, `mamba`, `conda` or `poetry`. Install the needed library by pressing the green down-arrow behind the library name in the "Library Manager" section of the _OCP CAD Viewer_ sidebar. For more details, see [here](./docs/install.md)

   The Quickstarts will also

   - (optionally) install the the [Jupyter extension for VS Code from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
   - start the OCP viewer
   - create a demo file in a temporary folder to quickly see a simple usage example

3. On Silicon Macs (ARM CPU)

   - Install Miniforge
     - Option 1: Download and install from the [Miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#download) github page
     - Option 2: Use `homebrew`: `brew install miniforge`
   - Initialize your shell for `mamba`: `mamba init $(basename "$SHELL")`
   - Create an environment, e.g named `code_cad` with Python 3.10: `mamba create -n code_cad python=3.10`
   - Activate the environment: `mamba activate code_cad`
   - Start VS Code from your working folder: `code .`
   - Install the Python extension in VS Code
   - Continue with 1. above

**Note:** Do not use the _OCP CAD Viewer_ logo to verify your _OCP CAD Viewer_ settings! The logo overwrites all your settings in VS Code with its own settings to always look the same on each instance. Use a simple own model for checking your conmfiguration

## Usage

### Running code using Jupyter

- Start the _OCP CAD Viewer_ by pressing the green box-arrow button in the "Viewer Manager" section of the _OCP CAD Viewer_ sidebar
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

You can also use "Library Manager" in the _OCP CAD Viewer_ sidebar to manage the Python libraries for _build123d_, _cadquery_, _ipython_ and _ocp_tessellate_ (Presse the green arrow whenhovering over a library to install/upgrade it)

### Extra topics

- [Quickstart experience on Windows](docs/quickstart.md)
- [Use Jupyter to execute code](docs/run.md)
- [Debug code with visual debugging](docs/debug.md)
- [Measure mode](docs/measure.md)
- [Use the `show` command](docs/show.md)
- [Use the `show_object` command](docs/show_object.md)
- [Use the `set_viewer_config` command](docs/set_viewer_config.md)
- [Download examples for build123d or cadquery](docs/examples.md)
- [Use the build123d snippets](docs/snippets.md)

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

  - Workspace configuration (part of the VS Code settings, you can access them e.g. via the green gear symbol in OCP CAD Viewer's "Viewer Manager")
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

v2.4.1

- Fix colormap handling to keep color of objects when .color attribute is set
- show() ends gracefully and empty lists are treated correctly

v2.4.0

New features

- Removed `measure_tools` parameter and integrated switching between normal and measure mode into the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer/blob/master/src/treeview.js) ([#58](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/58)).
- Rewrote the CAD view tree to use lazy loading (switching to measure mode can increase number of nodes by more then 100 times). This changed the input format for the viewer component (states integrated into object tree now), which is a breaking change if you use threee-cad-viewer directly, but no changes for users of vscode-ocp-cad-viewer.
- Rewrote converter of [ocp-tessellate](https://github.com/bernhard-42/ocp-tessellate/blob/main/ocp_tessellate/convert.py) to be more consistent and easier to maintain. All solids and faces can now be instances. Breaking changes if you use ocp_tessellate directly, but no changes for users of vscode-ocp-cad-viewer.
- Added `center_grid` to workspace configuration to ensure grid planes always go through world origin ([#77](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/77)).
- Added `save_screenshot(filename)` to save a PNG of the currently shown object(s). Canvas only, no CAD tools ([#86](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/86)).
- Support viewing of build123d `LocationList`s.

Fixes

- Fixed the mini-build123d `Location` class used by measurement backend.
- Measure mode cannot work on clipped object, so disabled clipping tab when measure mode is turned on ([#55](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/55), [#70](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/70))
- Removed using `to_tuple` for build123d Color objects ([#69](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/69)).
- Made color handling more consistent (sometime `color` or `alpha` was ignored).
- Fixed opening duplivcate Jupyter notebooks ([#78](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/78)).
- Fixed measure tool related regression. ([#81](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/81), [82](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/82),).
- Fixed ImageFace aspect ratio bug ([#83](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/83)).
- Fixed `show_all` failing on empty ShapeList ([#90](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/90)).
- Fixed to display ShapeList of Compound correctly ([#91](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/91)).
- Fixed ShapeList containing different object types ([#92](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/92)).
- Fixed measure tools to work with 1D objects ([#93](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/93)).

full change log see [CHANGELOG.md](./CHANGELOG.md)
