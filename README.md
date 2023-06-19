# _OCP CAD Viewer_ for VS Code

_OCP CAD Viewer_ for VS Code is an extension to show [CadQuery](https://github.com/cadquery/cadquery) and [build123d](https://github.com/gumyr/build123d) objects in VS Code via the[three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) viewer component.

## Setup

**Prerequisites**

-   A fairly recent version of Microsoft VS Code, e.g. 1.76.0 or newer
-   [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) installed in VS Code
-   `Python` and `pip` available in the Python enviroment that will be used for CAD development

Notes:

-   For VSCodium, the extension is not available in the marketplace. You need to download the the vsix file from the [release folder](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) and install it manually.
-   Currently, on a Silicon Mac (ARM CPU M1 or newer), _OCP_ and _CadQuery_ can only be installed via `mamba` and Python 3.9 or 3.10. Prepare an environment with `mamba create -n code_cad python=3.9` or `mamba create -n code_cad python=3.10`.

**Installation**:

Open the VS Code Marketplace, and search and install _OCP CAD Viewer 1.1.0_. 

Afterwards the OCP viewer is available in the VS Code sidebar: 
    
![](screenshots/ocp_icon.png)

Clicking on it shows the OCP CAD Viewer UI:

![](screenshots/init.png)

You have 3 choices:

-   Prepare _OCP CAD Viewer_ for working with [build123d](https://github.com/gumyr/build123d): Presse the _Quickstart build123d_ button.

    This will install _OCP_, _build123d_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip` (except for Apple Silicon machines that require `mamba`)

    ![](screenshots/build123d_installed.png)

-   Prepare _OCP CAD Viewer_ for working with [CadQuery](https://github.com/cadquery/cadquery): Presse the _Quickstart CadQuery_ button.

    This will install _OCP_, _CadQuery_, _ipykernel_ (_jupyter_client_), _ocp_tessellate_ and _ocp_vscode_ via `pip` (except for Apple Silicon machines that require `mamba`)

    ![](screenshots/cadquery_installed.png)

-   Ignore the quick starts and use the "Library Manager" to install the libraries. Doing so, _OCP CAD Viewer_ let's you select whether to use `pip`, `mamba`, `conda` or `poetry`. Install the needed library by pressing the green down-arrow behind the library name in the "Library Manager" section of the _OCP CAD Viewer_ sidebar. For more details, see [here](./docs/install.md)

The Quickstarts will also 
- (optionally) install the the [Jupyter extension for VS Code from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
- start the OCP viewer
- create a demo file in a temporary folder to quickly see a simple usage

## Usage

### Running code using Jupyter

-   Start the _OCP CAD Viewer_ by pressing the green box-arrow button in the "Viewer Manager" section of the _OCP CAD Viewer_ sidebar
-   Import ocp_vscode and the CAD library by using the paste button behing the library names in the "Viewer Manager" section
-   Use the usual Run menu to run the code

![Use with run](screenshots/run-code.gif)

### Debugging code with visual debugging

After each step, the debugger checks all variables in `locals()` for being CAD objects and displays them with their variable name.
Note:
- Check that `OCP: on` is visible in the status bar
- It also shows planes, locations and axis, so name your contexts
- It remembers camera position and unselected variables in the tree
- during debugging, `show` and `show_object` are disabled. They interfere with the visual debugging

![Use with run](screenshots/debug.gif)

### Library Manager

You can also use "Library Manager" in the _OCP CAD Viewer_ sidebar to manage the Python libraries for _build123d_, _cadquery_, _ipython_ and _ocp_tessellate_ (Presse the green arrow whenhovering over a library to install/upgrade it)

### Extra topics

-   [Use the `show` command](docs/show.md)
-   [Use the `show_object` command](docs/show_object.md)
-   [Download examples for build123d or cadquery](docs/examples.md)
-   [Use the build123d snippets](docs/snippets.md)
