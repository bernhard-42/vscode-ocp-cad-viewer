# Install Libraries

The "Library Manager" in the _OCP CAD Viewer_ sidebar manages the Python libraries for _build123d_, _cadquery_, _ipykernel_ and _ocp_tessellate_. Hover over a library and press the down-arrow to install or upgrade it. VS Code will prompt you to confirm that the right environment is selected; if something goes wrong, the message appears in VS Code.

## Default pip config

```json
  "OcpCadViewer.advanced.quickstartCommands": {
    "cadquery":  ["{unset_conda} {pip-install} ocp_vscode~={ocp_vscode_version} cadquery"],
    "build123d": ["{pip-install} ocp_vscode~={ocp_vscode_version} git+https://github.com/gumyr/build123d"]
  },
  "OcpCadViewer.advanced.installCommands": {
    "cadquery":        ["{unset_conda} {pip-install} --upgrade cadquery"],
    "build123d":       ["{pip-install} --upgrade git+https://github.com/gumyr/build123d"],
    "cadquery_ocp":    ["{pip-install} --upgrade cadquery_ocp"],
    "ocp_vscode":      ["{pip-install} --upgrade ocp_vscode~={ocp_vscode_version}"],
    "ocp_tessellate":  ["{pip-install} --upgrade ocp_tessellate"],
    "ipykernel":       ["{pip-install} --upgrade ipykernel"],
    "jupyter_console": ["{pip-install} --upgrade jupyter_console"]
  },
```

**Notes:**

- Due to rapid development of build123d, the install commands use the installation from git. Change to pypi if you want to use the latest published on pypi.
- `uv` envs are auto-detected and `{pip-install}` is replaced by `uv pip install`. If you want to use `uv add`, you need to override the install commands like this:

    ```json
      "OcpCadViewer.advanced.quickstartCommands": {
        "cadquery":  ["uv add -p {python} ocp_vscode~={ocp_vscode_version} cadquery"],
        "build123d": ["uv add -p {python} ocp_vscode~={ocp_vscode_version} git+https://github.com/gumyr/build123d"]
      },
      "OcpCadViewer.advanced.installCommands": {
        "cadquery":        ["uv add -p {python} --upgrade cadquery"],
        "build123d":       ["uv add -p {python} --upgrade git+https://github.com/gumyr/build123d"],
        "ocp_vscode":      ["uv add -p {python} --upgrade ocp_vscode~={ocp_vscode_version}"],
        "ocp_tessellate":  ["uv add -p {python} --upgrade ocp_tessellate"],
        "ipykernel":       ["uv add -p {python} --upgrade ipykernel"],
        "jupyter_console": ["uv add -p {python} --upgrade jupyter_console"]
      }
    ```

## Placeholders

Commands may contain the following placeholders. They are resolved at runtime against the currently selected Python interpreter:

| Placeholder            | Replaced with                                                                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `{python}`             | Absolute path to the selected interpreter (quoted)                                                                                       |
| `{pip-install}`        | `uv pip install -p "{python}"` if the env is a `uv` venv, otherwise `"{python}" -m pip install`                                          |
| `{unset_conda}`        | On macOS/Linux, prefix `env -u CONDA_PREFIX `; on Windows, a temporary `.cmd` file that unsets `CONDA_PREFIX` before running the command |
| `{ocp_vscode_version}` | Version of the currently installed VS Code extension                                                                                     |

## Troubleshooting

- If the install message in VS Code reports a missing `pip` or `uv pip`, confirm the selected Python interpreter actually has either available.
- For conda/mamba/micromamba environments, `pip` (or `uv pip`) must be used — `ocp_vscode` is only published on PyPI, not on conda channels. The default commands handle this via `{unset_conda}`.
- If `python` cannot be found at all, restart VS Code after activating your virtual environment in the terminal, or pick the interpreter via the Python extension's "Select Interpreter" command.
