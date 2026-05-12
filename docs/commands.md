# VS Code Commands reference

All commands can be invoked from the Command Palette (`Ctrl-Shift-P` / `Cmd-Shift-P`); most are also surfaced as buttons in the _OCP CAD Viewer_ sidebar.

| Command                                  | Title                                                  | Notes                                                                                  |
| ---------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| `ocpCadViewer.ocpCadViewer`              | Open viewer                                            | Bound to `Ctrl-K V` / `Cmd-K V` in Python editors                                      |
| `ocpCadViewer.openViewer`                | Open viewer (button)                                   | Sidebar button variant of the above                                                    |
| `ocpCadViewer.openConsole`               | Open Jupyter Console (button)                          | Requires the Jupyter extension                                                         |
| `ocpCadViewer.toggleWatch`               | Toggle visually watching the CAD model                 | Switches the status bar between `OCP: <port>·DEBUG` and `OCP: <port>`                  |
| `ocpCadViewer.quickstart`                | Quickstart installation                                | Takes one arg: `"cadquery"` or `"build123d"`. Used by the Quickstart sidebar buttons   |
| `ocpCadViewer.installLibrary`            | Install library                                        | Runs the matching entry of `OcpCadViewer.advanced.installCommands`                     |
| `ocpCadViewer.installPythonModule`       | Install `ocp_vscode` library                           | Installs the Python companion at the version that matches the extension               |
| `ocpCadViewer.installJupyterExtension`   | Install Jupyter extension `ms-toolsai.jupyter`         | Convenience for the Jupyter prerequisite                                               |
| `ocpCadViewer.installVscodeSnippets`     | Install CAD snippets into `<project>/.vscode/`         | Writes a `.code-snippets` file built from `OcpCadViewer.snippets.dotVscodeSnippets`    |
| `ocpCadViewer.downloadExamples`          | Download examples for a specific library               | Uses `OcpCadViewer.advanced.exampleDownloads`                                          |
| `ocpCadViewer.pasteSnippet`              | Paste code snippet                                     | Inserts the corresponding `OcpCadViewer.advanced.codeSnippets` entry at the cursor     |
| `ocpCadViewer.refreshLibraries`          | Refresh libraries list                                 | Re-scans the active Python env                                                         |
| `ocpCadViewer.preferences`               | Open preferences                                       | Filters Settings to "OCP CAD Viewer"                                                   |
| `ocpCadViewer.output`                    | Toggle OCP CAD Viewer output panel                     | Shortcut to the extension's `Output` channel                                           |

## Keybindings

| Keybinding       | Command                       | When                                       |
| ---------------- | ----------------------------- | ------------------------------------------ |
| `Ctrl-K V` / `Cmd-K V` | `ocpCadViewer.ocpCadViewer` | Active editor is focused on a Python file  |

Override or add bindings via VS Code's "Preferences: Open Keyboard Shortcuts (JSON)".
