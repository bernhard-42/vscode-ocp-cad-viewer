# _OCP CAD Viewer_ for VS Code

_OCP CAD Viewer_ for VS Code is an extension to show [CadQuery](https://github.com/cadquery/cadquery) and [build123d](https://github.com/gumyr/build123d) objects in VS Code via the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) viewer component.

## Installation

### Prerequisites

-   A fairly recent version of Microsoft VS Code, e.g. 1.85.0 or newer
-   The [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) installed in VS Code
-   Necessary tools:
    -   `python` and `pip` available in the Python enviroment that will be used for CAD development
    -   The command `git` needs to be available
    -   On a Silicon Apple computer the command `mamba` needs to be available. You might want to consider using [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge).

**Notes**:

-   To use OCP CAD Viewer, start VS Code from the commandline in the Python environment you want to use or select the right Python interpreter in VS Code first. **OCP CAD Viewer depends on VS Code using the right Python interpreter** (i.e. mamba / conda / pyenv / poetry / ... environment).
-   For VSCodium, the extension is not available in the VS code market place. You need to download the the vsix file from the [release folder](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) and install it manually.
-   Currently, on a Silicon Mac (ARM CPU), _OCP_ and _CadQuery_ can only be installed via `mamba`, see 3. below.

### Installation

1. Open the VS Code Marketplace, and search and install _OCP CAD Viewer 2.2.1_.

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
    - Create an environment, e.g named `code_cad` with Python 3.10:  `mamba create -n code_cad python=3.10`
    - Activate the environment: `mamba activate code_cad`
    - Start VS Code from your working folder: `code .`
    - Install the Python extension in VS Code
    - Continue with 1. above



## Usage

### Running code using Jupyter

-   Start the _OCP CAD Viewer_ by pressing the green box-arrow button in the "Viewer Manager" section of the _OCP CAD Viewer_ sidebar
-   Import ocp_vscode and the CAD library by using the paste button behing the library names in the "Viewer Manager" section
-   Use the usual Run menu to run the code

![Running code](screenshots/ocp_vscode_run.png)

### Debugging code with visual debugging

After each step, the debugger checks all variables in `locals()` for being CAD objects and displays them with their variable name.
Note:

-   Check that `OCP:on` is visible in the status bar
-   It also shows planes, locations and axis, so name your contexts
-   It remembers camera position and unselected variables in the tree
-   during debugging, `show` and `show_object` are disabled. They interfere with the visual debugging

![Debugging code](screenshots/ocp_vscode_debug.png)

### Library Manager

You can also use "Library Manager" in the _OCP CAD Viewer_ sidebar to manage the Python libraries for _build123d_, _cadquery_, _ipython_ and _ocp_tessellate_ (Presse the green arrow whenhovering over a library to install/upgrade it)

### Extra topics

-   [Quickstart experience on Windows](docs/quickstart.md)
-   [Use Jupyter to execute code](docs/run.md)
-   [Debug code with visual debugging](docs/debug.md)
-   [Measure mode](docs/measure.md)
-   [Use the `show` command](docs/show.md)
-   [Use the `show_object` command](docs/show_object.md)
-   [Use the `set_viewer_config` command](docs/set_viewer_config.md)
-   [Download examples for build123d or cadquery](docs/examples.md)
-   [Use the build123d snippets](docs/snippets.md)

## Best practices

-   Use the **Jupyter extension** for a more interactive experience. This allows to have one cell (separated by `# %%`) at the beginning to import all libraries

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

-   The **config system** of OCP CAD Viewer

    There are 3 levels:

    -   Workspace configuration (part of the VS Code settings, you can access them e.g. via the green gear symbol in OCP CAD Viewer's "Viewer Manager")
    -   Defaults set with the command `set_defaults` per Python file
    -   Parameters in `show` or `show_object` per command

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

    -   The first block imports build123d and CadQuery (omit what you are not interested in).
    -   The second block imports all commands for OCP CAD Viewer. `set_port` is only needed when you have more than one viewer open and can be omitted for the first viewer)
    -   The third block as an example sets helper_scale and reset_camera as defaults. Then every show_object or show command will respect it as the default

-   Debugging build123d with `show_all` and the **visual debugger**

    -   If you name your contexts (including `Location` contexts), the visual debugger will show the CAD objects assigned to the context.

    -   Use `show_all` to show all cad objects in the current scope (`locals()`) of the Python interpreter (btw. the visual debugger uses `show_all` at each step)

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

-   **Keep camera orientation** of an object with `reset_camera`

    Sometimes it is helpful to keep the orientation of an object across code changes. This is what `reset_camera` does:

    -   `reset_camera=Camera.Center` will keep position and rotation, but ignore panning. This means the new object will be repositioned to the center (most robust approach)
    -   `reset_camera=Camera.KEEP` will keep position, rotation and panning. However, panning can be problematic. When the next object to be shown is much larger or smaller and the object before was panned, it can happen that nothing is visible (the new object at the pan location is outside of the viewer frustum). OCP CAD Viewer checks whether the bounding box of an object is 2x smaller or larger than the one of the last shown object. If so, it falls back to `Camera.CENTER`. A notification is written to the OCP CAD Viewer output panel.
    -   `reset_camera=Camera.RESET` will ensure that position, rotation and panning will be reset to the initial default

## Development

Testing:

Native tessellator can be set via `NATIVE_TESSELLATOR=1`and Python tessellator via `NATIVE_TESSELLATOR=0`.

When `OCP_VSCODE_PYTEST=1` is set, `show` will not send the tessellated results to the viewer, but return it to the caller for inspection.

A full test cycle consist of:

```bash
NATIVE_TESSELLATOR=0 OCP_VSCODE_PYTEST=1 pytest -v -s pytests/
NATIVE_TESSELLATOR=1 OCP_VSCODE_PYTEST=1 pytest -v -s pytests/
```

## Changes

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
-   Viewer keeps clipping settings when `reset_camera`is set to `Camera.KEEP`or `Camera.CENTER` ([#43](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/43))
-   Material configurator now has a reset button "R" to get back to initial values
-   `show_all` now converts nested dicts and lists into viewer hierarchies
-   `set_viewer_config` is documented in README
-   Fix: `show_parent` now supported by `show_defaults` ([#64](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/64))
-   Fix: `show_all()` now works in non visual debugging mode (removed `force` parameter from `show_all`) 
-   Fix: `show_all()` now doesn't break when an array of `Colors` is in the `locals` variable list ([#45](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/45))
-   Fix: `show_all` now ignores unknown types in lists or dicts without raising an error and only printing a warning ([#67](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/67))
-   Fix: The `serialize` and `deserialize` commands don't crash on Windows any more ([#65](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/65))
-   Fix: Status notifications for grid work again ([#66](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/66))

full change log see [CHANGELOG.md](./CHANGELOG.md)
