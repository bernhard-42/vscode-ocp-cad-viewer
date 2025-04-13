import socket
from pathlib import Path

import click
import yaml
from werkzeug.serving import get_interface_ip

from ocp_vscode.backend import ViewerBackend
from ocp_vscode.standalone import CONFIG_FILE, DEFAULTS, Viewer
from ocp_vscode.state import resolve_path


def represent_list(dumper, data):
    """
    Represents a list in YAML format with flow style.

    Args:
        dumper: The YAML dumper instance.
        data: The list to be represented.

    Returns:
        The YAML representation of the list in flow style.
    """
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


yaml.add_representer(list, represent_list)


def track_param(ctx, param, value):
    """
    Tracks and stores the value of a parameter in the context object.

    This function checks if the context object (`ctx`) has an attribute `params_set`.
    If not, it initializes `params_set` as an empty dictionary. It then checks if the
    provided `value` is different from the parameter's default value or if the parameter's
    name is one of ["port", "host", "debug"]. If any of these conditions are met, it stores
    the parameter's name and value in the `params_set` dictionary.

    Args:
        ctx (object): The context object that will store the parameter values.
        param (object): The parameter object which contains the default value and name.
        value (any): The value of the parameter to be tracked.

    Returns:
        any: The value of the parameter.
    """
    if not hasattr(ctx, "params_set"):
        ctx.params_set = {}
    if value != param.default or param.name in ["port", "host", "debug"]:
        ctx.params_set[param.name] = value
    return value


@click.command()
@click.option(
    "--create_configfile",
    is_flag=True,
    help="Create the configlie .ocpvscode_standalone in the home directory",
    callback=track_param,
)
@click.option(
    "--backend",
    is_flag=True,
    help="Run measurement backend",
    callback=track_param,
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="The host to start OCP CAD with",
    callback=track_param,
)
@click.option(
    "--port",
    default=3939,
    help="The port to start OCP CAD with",
    callback=track_param,
)
@click.option(
    "--debug",
    is_flag=True,
    help="Show debugging information",
    callback=track_param,
)
@click.option(
    "--timeit",
    is_flag=True,
    help="Show timing information",
    callback=track_param,
)
@click.option(
    "--tree_width",
    help="OCP CAD Viewer navigation tree width (default: 240)",
    callback=track_param,
)
@click.option(
    "--no_glass",
    is_flag=True,
    help="Do not use glass mode with transparent navigation tree",
    callback=track_param,
)
@click.option(
    "--theme",
    default="light",
    help="Use theme 'light' or 'dark' (default: 'light')",
    callback=track_param,
)
@click.option(
    "--no_tools",
    is_flag=True,
    help="Do not show toolbar",
    callback=track_param,
)
@click.option(
    "--tree_width",
    default=240,
    help="Width of the CAD navigation tree (default: 240)",
    callback=track_param,
)
@click.option(
    "--control",
    default="trackball",
    help="Use control mode 'orbit' or 'trackball'",
    callback=track_param,
)
@click.option(
    "--reset_camera",
    default="reset",
    help="Set camera behavior to 'reset', 'keep' or 'center'",
    callback=track_param,
)
@click.option(
    "--up",
    default="Z",
    help="Provides up direction, 'Z', 'Y' or 'L' (legacy) (default: Z)",
    callback=track_param,
)
@click.option(
    "--rotate_speed",
    default=1,
    help="Rotation speed (default: 1)",
    callback=track_param,
)
@click.option(
    "--zoom_speed",
    default=1,
    help="Zoom speed (default: 1)",
    callback=track_param,
)
@click.option(
    "--pan_speed",
    default=1,
    help="Pan speed (default: 1)",
    callback=track_param,
)
@click.option(
    "--axes",
    is_flag=True,
    help="Show axes",
    callback=track_param,
)
@click.option(
    "--axes0",
    is_flag=True,
    help="Show axes at the origin (0, 0, 0)",
    callback=track_param,
)
@click.option(
    "--black_edges",
    is_flag=True,
    help="Show edges in black",
    callback=track_param,
)
@click.option(
    "--grid_xy",
    is_flag=True,
    help="Show grid on XY plane",
    callback=track_param,
)
@click.option(
    "--grid_yz",
    is_flag=True,
    help="Show grid on YZ plane",
    callback=track_param,
)
@click.option(
    "--grid_xz",
    is_flag=True,
    help="Show grid on XZ plane",
    callback=track_param,
)
@click.option(
    "--center_grid",
    is_flag=True,
    help="Show grid planes crossing at center of object or global origin(default: False)",
    callback=track_param,
)
@click.option(
    "--collapse",
    default=1,
    help="leaves: collapse all leaf nodes, all: collapse all nodes, none: expand all nodes, root: expand root only (default: leaves)",
    callback=track_param,
)
@click.option(
    "--perspective",
    is_flag=True,
    help="Use perspective camera",
    callback=track_param,
)
@click.option(
    "--ticks",
    default=10,
    help="Default number of ticks (default: 10)",
    callback=track_param,
)
@click.option(
    "--transparent",
    is_flag=True,
    help="Show objects transparent",
    callback=track_param,
)
@click.option(
    "--default_opacity",
    default=0.5,
    help="Default opacity for transparent objects (default: 0.5)",
    callback=track_param,
)
@click.option(
    "--explode",
    is_flag=True,
    help="Turn explode mode on",
    callback=track_param,
)
@click.option(
    "--angular_tolerance",
    default=0.2,
    help="Angular tolerance for tessellation algorithm (default: 0.2)",
    callback=track_param,
)
@click.option(
    "--deviation",
    default=0.1,
    help="Deviation of for tessellation algorithm (default: 0.1)",
    callback=track_param,
)
@click.option(
    "--default_color",
    default="#e8b024",
    help="Default shape color, CSS3 color names are allowed (default: #e8b024)",
    callback=track_param,
)
@click.option(
    "--default_edgecolor",
    default="#707070",
    help="Default color of the edges of shapes, CSS3 color names are allowed (default: #707070)",
    callback=track_param,
)
@click.option(
    "--default_thickedgecolor",
    default="MediumOrchid",
    help="Default color of lines, CSS3 color names are allowed (default: MediumOrchid)",
    callback=track_param,
)
@click.option(
    "--default_facecolor",
    default="Violet",
    help="Default color of faces, CSS3 color names are allowed (default: Violet)",
    callback=track_param,
)
@click.option(
    "--default_vertexcolor",
    default="MediumOrchid",
    help="Default color of vertices, CSS3 color names are allowed (default: MediumOrchid)",
    callback=track_param,
)
@click.option(
    "--ambient_intensity",
    default=1,
    help="Intensity of ambient light (default: 1.00)",
    callback=track_param,
)
@click.option(
    "--direct_intensity",
    default=1.1,
    help="Intensity of direct light (default: 1.10)",
    callback=track_param,
)
@click.option(
    "--metalness",
    default=0.3,
    help="Metalness property of material (default: 0.30)",
    callback=track_param,
)
@click.option(
    "--roughness",
    default=0.65,
    help="Roughness property of material (default: 0.65)",
    callback=track_param,
)
@click.pass_context
def main(ctx, **kwargs):
    """
    Main function to either create a configuration file or start the viewer.
    Args:
        ctx: Context object containing parameters.
        **kwargs: Arbitrary keyword arguments for click.

    Returns:
        None
    """

    if kwargs.get("create_configfile"):

        config_file = Path(resolve_path(CONFIG_FILE))
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(yaml.dump(DEFAULTS))
        print(f"Created config file {config_file}")

    elif kwargs.get("backend"):

        port = kwargs["port"]

        backend = ViewerBackend(port)
        try:
            backend.start()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)

    else:
        viewer = Viewer(ctx.params_set)

        port = kwargs["port"]
        host = kwargs["host"]

        if host == "0.0.0.0":
            print("\nThe viewer is running on all addresses:")
            print(f"  - http://127.0.0.1:{port}/viewer")
            try:
                host = get_interface_ip(socket.AF_INET)
                print(f"  - http://{host}:{port}/viewer\n")
            except:  # pylint: disable=bare-except
                pass
        else:
            print(f"\nThe viewer is running on http://{host}:{port}/viewer\n")

        viewer.start()


if __name__ == "__main__":
    main()
