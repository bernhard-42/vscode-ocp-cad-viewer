---
title: OCP CAD Viewer
description: A 3D CAD viewer for OCP based code CAD objects
---

# OCP CAD Viewer

## The CAD viewer for VS Code

_OCP CAD Viewer_ for [VS Code](https://code.visualstudio.com/) is an extension to show [build123d](https://github.com/gumyr/build123d) and [CadQuery](https://github.com/cadquery/cadquery) objects in VS Code via the [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) viewer component.

![Init screen VS Code](assets/images/ocp-cad-viewer-light.png#only-light){ .center width=95% }
![Init screen VS Code](assets/images/ocp-cad-viewer-dark.png#only-dark){ .center width=95% }

The extension has started the viewer in the right tab, and the left tab is the actual Python file that defines the CAD objects in build123d or CadQuery.

??? info "VSCodium Support"    
    For [VSCodium](https://vscodium.com/), the extension is [not available](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/150) in the VSCodium market place [Open VSX](https://open-vsx.org/). You need to download the the **vsix** file from the [release folder](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) and install it manually.

    ![Manual xsix installation](assets/images/install-vsix-light.png#only-light){ .center width=664px }
    ![Manual xsix installation](assets/images/install-vsix-dark.png#only-dark){ .center width=521px }

## I don't use VS Code

The viewer can run as a [standalone viewer](concepts/index.md#standalone) in the browser and can be used together with any editor of your choice.

![Init screen NeoVim](assets/images/neovim-setup-light.png#only-light){ .center width=95% }
![Init screen NeoVim](assets/images/neovim-setup-dark.png#only-dark){ .center width=95% }

In the left bottom terminal the viewer got started (`python -m ocp_vscode`). Here you can see the URL of the viewer, the one ending with `/viewer`. On the right, a browser window has opened the viewer pager. And top left is a terminal running `neovim` as an example.

## Basic Usage

Assume, the viewer is running either in VS Code or as a standalone viewer (see above). The following code is sufficient to send objects to the viewer:

=== "build123d"

    ```py hl_lines="6"
    from build123d import *   # (1)
    from ocp_vscode import *  # (2)

    b = Box(1,2,3)            # (3)

    show(b)                   # (4)
    ```

    1. Import all symbols from the `build123d` package
    2. Import all symbols from the `ocp_vscode` package
    3. Create a simple box in `build123d`
    4. The `show` command of `ocp_vscode` sends CAD objects as meshes to the viewer.

=== "CadQuery"

    ```py hl_lines="6"
    import cadquery as cq         # (1)
    from ocp_vscode import *      # (2)

    b = cq.Workplane().box(1,2,3) # (3)

    show(b)                       # (4)
    ```

    1. Import the `cadquery` package and alias it to `cq`
    2. Import all symbols from the `ocp_vscode` package
    3. Create a simple box in `CadQuery`
    4. The `show` command of `ocp_vscode` sends CAD objects as meshes to the viewer.

??? info "How does it work?"
        
    The model gets created in Python with build123 or CadQuery (see line 4), but the viewer is a Javascript component. To bridge the two different technologies, the VS Code extension or the standalone viewer start a WebSockets server, per default on port 3939.

    The `ocp_vscode` command `show` (see line 6) will tessellate the objects using [ocp-tessellate](https://github.com/bernhard-42/ocp-tessellate), serialize the resulting meshes, and send them via WebSockets to the VS Code extension or the standalone viewer. From there the meshes will be forwarded to the actual Javascript viewer component to visualize them using [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer)

## Features

### Runtime modes

- Fully integrated into VS Code
    - Supports autostart of the viewer when loading CAD Python files
    - Provides a Library manager to maintain Pythion libraries
    - Provides a Viewer manager for information and starting the viewer

- [Standalone mode](concepts/index.md#standalone)
    - To run from the commandline and show viewer in the browser
    - Supports any editor

### Quickstarts in VS Code runtime

- Quickstart Python module installation of build123 and CadQuery
- Code snippets for build123d
- Download build123d and CadQuery examples

### Code execution

- Supports [build123d](https://github.com/gumyr/build123d), [CadQuery](https://github.com/cadquery/cadquery), and [OCP](https://github.com/cadquery/OCP) objects and OCP objects
- Fully decoupled, Python code sends models via websockets to the viewer
- Supports Jupyter extension to execute code blocks
- Visual debugging to see changes in the model as you step along:
    - Available in VS Code out of the box
    - Configurable for editors support [Debug Protocol Adapter](https://github.com/microsoft/debug-adapter-protocol), e.g. neovim with [neovim-dap](https://neovimcraft.com/plugin/mfussenegger/nvim-dap/index.html)

### CAD Viewer

- Decorators
    - X,Y,Z coordinate system (world origin or center of bounding box centered)
    - Separate XY, YZ, XZ grids
- Experience
    - Object navigation tree supporting hierarchical assemblies
    - Perspective and orthographic views
    - Orbit control (Z always shows up) and non-tumbling trackball control
    - Preset view selectors that can center the view around visible objects
    - Toggle transparency
- Object selection
    - Show/hide objects and hierarchies via the navigation tree and double clicks
    - Isolate and centre single objects via the navigation tree and double clicks
- Screenshot saving


### CAD Tools

- Three configurable clipping planes
- A basic material configurator
- A measurement tool that uses a BRep-enabled Python backend to take exact measurements of the model
- An object selection tool for selecting edges, faces and vertices in the viewer and using their indices in the Python code
- An explode tool to dynamically explode an assembly
- An animation system for animating build123d and CadQuery assemblies
