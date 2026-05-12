# Best practices

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

        ![named contexts](../screenshots/context_vars.png)

- **Keep camera orientation** of an object with `reset_camera`

    Sometimes it is helpful to keep the orientation of an object across code changes. This is what `reset_camera` does:
    - `reset_camera=Camera.CENTER` will keep position and rotation, but ignore panning. This means the new object will be repositioned to the center (most robust approach)
    - `reset_camera=Camera.KEEP` will keep position, rotation and panning. However, panning can be problematic. When the next object to be shown is much larger or smaller and the object before was panned, it can happen that nothing is visible (the new object at the pan location is outside of the viewer frustum). OCP CAD Viewer checks whether the bounding box of an object is 2x smaller or larger than the one of the last shown object. If so, it falls back to `Camera.CENTER`. A notification is written to the OCP CAD Viewer output panel.
    - `reset_camera=Camera.RESET` will ensure that position, rotation and panning will be reset to the initial default
