# Troubleshooting

- **Generic ("it doesn't work")**
    1. Confirm that VS Code extension and ocp_vscode have the same version. This can be seen in the OCP CAD Viewer UI. Or alternatively in the Output panel of VS Code:

        ```text
        2025-07-06 14:51:33.418 [info ] extension.check_upgrade: ocp_vscode library version 2.8.6 matches extension version 2.8.6
        ```

    2. Test whether the standalone viewer works, see [Standalone mode](standalone.md) (to eliminate VS Code issues)
    3. Open a work folder and not a Python file (to ensure we do not get in Python path problems)
    4. Check the Output panel. Search for:
        - `PythonPath: 'aaa/bbb/python'` **=> right Python environment?**
        - `Server started on port xxxx` (or so) **=> right port? default is 3939**
        - `Starting Websocket server` **=> should not be followed by an error**
        - `OCP Cad Viewer port: xxxx, folder: yyyy zzzz` **=> yyyy should be the right working folder?**
    5. If all looks fine until now, then toggle Developer tools in VS Code and check browser console. Often we see a WebGL error for the browser of VS Code used for the viewer.

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
