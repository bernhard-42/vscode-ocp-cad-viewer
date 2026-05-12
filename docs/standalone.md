# Standalone mode

Standalone mode allows you to use OCP CAD Viewer without VS Code: `python -m ocp_vscode`. This starts a Flask server reachable at `http://127.0.0.1:<port>` (default `http://127.0.0.1:3939`). All client-side features of the VS Code variant (i.e. `show*` features, including measurement mode) are available — except visual debugging, which relies on VS Code.

## Command line options

Use `python -m ocp_vscode --help` to see all options. Current output:

```
Usage: python -m ocp_vscode [OPTIONS]

Options:
  --create_configfile             Create the config file .ocpvscode_standalone
                                  in the home directory
  --backend                       Run measurement backend
  --host TEXT                     The host to start OCP CAD with
  --port INTEGER                  The port to start OCP CAD with
  --debug                         Show debugging information
  --timeit                        Show timing information
  --tree_width INTEGER            OCP CAD Viewer navigation tree width
                                  (default: 240)
  --no_glass                      Do not use glass mode with transparent
                                  navigation tree
  --theme TEXT                    Use theme 'light', 'dark', or 'browser'
                                  (default: 'browser')
  --no_tools                      Do not show toolbar
  --control TEXT                  Use control mode 'orbit' or 'trackball'
  --reset_camera TEXT             Set camera behavior to 'reset', 'keep' or
                                  'center'
  --up TEXT                       Provides up direction, 'Z', 'Y' or 'L'
                                  (legacy) (default: Z)
  --rotate_speed INTEGER          Rotation speed (default: 1)
  --zoom_speed INTEGER            Zoom speed (default: 1)
  --pan_speed INTEGER             Pan speed (default: 1)
  --axes                          Show axes
  --axes0                         Show axes at the origin (0, 0, 0)
  --black_edges                   Show edges in black
  --grid_xy                       Show grid on XY plane
  --grid_yz                       Show grid on YZ plane
  --grid_xz                       Show grid on XZ plane
  --center_grid                   Show grid planes crossing at center of
                                  object or global origin (default: False)
  --grid_font_size INTEGER        Size of grid's axis label font (default: 12)
  --collapse INTEGER              leaves: collapse all leaf nodes, all:
                                  collapse all nodes, none: expand all nodes,
                                  root: expand root only (default: leaves)
  --perspective                   Use perspective camera
  --ticks INTEGER                 Default number of ticks (default: 5)
  --transparent                   Show objects transparent
  --default_opacity FLOAT         Default opacity for transparent objects
                                  (default: 0.5)
  --explode                       Turn explode mode on
  --angular_tolerance FLOAT       Angular tolerance for tessellation algorithm
                                  (default: 0.2)
  --deviation FLOAT               Deviation for tessellation algorithm
                                  (default: 0.1)
  --default_color TEXT            Default shape color, CSS3 color names are
                                  allowed (default: #e8b024)
  --default_edgecolor TEXT        Default color of the edges of shapes, CSS3
                                  color names are allowed (default: #707070)
  --default_thickedgecolor TEXT   Default color of lines, CSS3 color names are
                                  allowed (default: MediumOrchid)
  --default_facecolor TEXT        Default color of faces, CSS3 color names are
                                  allowed (default: Violet)
  --default_vertexcolor TEXT      Default color of vertices, CSS3 color names
                                  are allowed (default: MediumOrchid)
  --ambient_intensity INTEGER     Intensity of ambient light (default: 1.00)
  --direct_intensity FLOAT        Intensity of direct light (default: 1.10)
  --metalness FLOAT               Metalness property of material (default:
                                  0.30)
  --roughness FLOAT               Roughness property of material (default:
                                  0.65)
  --max_reconnect_attempts INTEGER
                                  Maximum number of attempts to reconnect to
                                  the viewer server in standalone mode. Use -1
                                  for infinite attempts (default: 300)
  --help                          Show this message and exit.
```

## Standalone mode with Docker

If you are not using VS Code and prefer to keep the standalone web server running in a container, see [docker-vscode-ocp-cad-viewer](https://github.com/nilcons/docker-vscode-ocp-cad-viewer).
