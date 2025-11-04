# Generic 

## "It doesn't work"

1. Confirm that VS Code extension and the Python module `ocp_vscode` have the same version. This can be seen in the OCP CAD Viewer UI. Or alternatively in the Output panel of VS Code:

    ```text
    2025-07-06 14:51:33.418 [info ] extension.check_upgrade: ocp_vscode library version 2.9.0 matches extension version 2.9.0
    ```

2. Test whether the standalone viewer works, see [Standalone mode](../concepts/index.md#standalone) (to eliminate VS Code issues)

3. Open a work folder and not a Python file (to ensure we do not get in Python path problems)

4. Check the Output panel (Use VS Code menu *View -> Output* and select "OCP CAD VIewer Log" from the drop down list). Search for:

    - `PythonPath: 'aaa/bbb/python'`  
        
        **=>** correct Python executable and environment?

    - `OCPCADController.startCommandServer: Server listening on port xxxx` 
    
        **=>** correct port? default is 3939

    - `OCPCADController.start: Starting websocket server ...` 
    
        **=>** should not be followed by an error

    - `ocpCadViewer.ocpCadViewer: OCPCADController started with port 3940 and folders: yyyy zzzz`
    
        **=>** yyyy should be the correct working folder

5. If all looks fine until now, then toggle *Developer tools*[^1] in VS Code to open the browser console. Look for errors in the Console tab of the developer tools related to `three-cad-viewer.esm.js`, `three.js`, or `WebglRenderer.ts`.

[^1]:  Use *shift-cmd-p* (Mac) or *shift-ctrl-p* (Windows/Linux) and select *Developer: Toggle Developer Tools*