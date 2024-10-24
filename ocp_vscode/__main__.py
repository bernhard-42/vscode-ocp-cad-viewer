import click
from ocp_vscode.standalone import Viewer


@click.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="The host to start OCP CAD with",
)
@click.option(
    "--port",
    default=3939,
    help="The port to start OCP CAD with",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Show debugging information",
)
@click.option(
    "--tree_width",
    default=240,
    help="OCP CAD Viewer navigation tree width (default: 240)",
)
@click.option(
    "--no-glass",
    is_flag=True,
    help="Use glass mode with transparent navigation tree",
)
@click.option(
    "--theme",
    default="light",
    help="Use theme 'light' or 'dark' (default: 'light')",
)
@click.option(
    "--no-tools",
    is_flag=True,
    help="Show toolbar",
)
@click.option(
    "--tree_width", default=240, help="Width of the CAD navigation tree (default: 240)"
)
@click.option(
    "--dark",
    is_flag=True,
    help="Use dark mode",
)
@click.option(
    "--orbit_control",
    is_flag=True,
    help="Use 'orbit' control mode instead of 'trackball'",
)
@click.option(
    "--up",
    default="Z",
    help="Provides up direction, 'Z', 'Y' or 'L' (legacy) (default: Z)",
)
@click.option(
    "--rotate_speed",
    default=1,
    help="Rotation speed (default: 1)",
)
@click.option(
    "--zoom_speed",
    default=1,
    help="Zoom speed (default: 1)",
)
@click.option(
    "--pan_speed",
    default=1,
    help="Pan speed (default: 1)",
)
@click.option(
    "--axes",
    is_flag=True,
    help="Show axes",
)
@click.option(
    "--axes0",
    is_flag=True,
    help="Show axes at the origin (0, 0, 0)",
)
@click.option(
    "--black_edges",
    default=False,
    help="Show edges in black",
)
@click.option(
    "--grid_XY",
    is_flag=True,
    help="Show grid on XY plane",
)
@click.option(
    "--grid_YZ",
    is_flag=True,
    help="Show grid on YZ plane",
)
@click.option(
    "--grid_XZ",
    is_flag=True,
    help="Show grid on XZ plane",
)
@click.option(
    "--center_grid",
    is_flag=True,
    help="Show grid planes crossing at center of object or global origin(default: False)",
)
@click.option(
    "--collapse",
    default=1,
    help="leaves: collapse all leaf nodes, all: collapse all nodes, none: expand all nodes, root: expand root only (default: leaves)",
)
@click.option(
    "--perspective",
    is_flag=True,
    help="Use perspective camera",
)
@click.option(
    "--ticks",
    default=10,
    help="Default number of ticks (default: 10)",
)
@click.option(
    "--transparent",
    is_flag=True,
    help="Show objects transparent",
)
@click.option(
    "--default_opacity",
    default=0.5,
    help="Default opacity for transparent objects (default: 0.5)",
)
@click.option(
    "--explode",
    is_flag=True,
    help="Turn explode mode on",
)
@click.option(
    "--modifier_keys",
    default="{'shift': 'shiftKey', 'ctrl': 'ctrlKey', 'meta': 'metaKey'}",
    help="Mapping of modifier keys shift, ctrl and meta (cmd on Mac, Windows on Windows)",
)
@click.option(
    "--angular_tolerance",
    default=0.2,
    help="Angular tolerance for tessellation algorithm (default: 0.2)",
)
@click.option(
    "--deviation",
    default=0.1,
    help="Deviation of for tessellation algorithm (default: 0.1)",
)
@click.option(
    "--default_color",
    default="#e8b024",
    help="Default shape color, CSS3 color names are allowed (default: #e8b024)",
)
@click.option(
    "--default_edgecolor",
    default="#707070",
    help="Default color of the edges of shapes, CSS3 color names are allowed (default: #707070)",
)
@click.option(
    "--default_thickedgecolor",
    default="MediumOrchid",
    help="Default color of lines, CSS3 color names are allowed (default: MediumOrchid)",
)
@click.option(
    "--default_facecolor",
    default="Violet",
    help="Default color of faces, CSS3 color names are allowed (default: Violet)",
)
@click.option(
    "--default_vertexcolor",
    default="MediumOrchid",
    help="Default color of vertices, CSS3 color names are allowed (default: MediumOrchid)",
)
@click.option(
    "--ambient_intensity",
    default=1,
    help="Intensity of ambient light (default: 1.00)",
)
@click.option(
    "--direct_intensity",
    default=1.1,
    help="Intensity of direct light (default: 1.10)",
)
@click.option(
    "--metalness",
    default=0.3,
    help="Metalness property of material (default: 0.30)",
)
@click.option(
    "--roughness",
    default=0.65,
    help="Roughness property of material (default: 0.65)",
)
def main(*args, **kwargs):
    viewer = Viewer(kwargs)

    port = kwargs["port"]
    host = kwargs["host"]

    print(f"\nThe viewer is running at http://{host}:{port}/viewer\n")

    viewer.start()


if __name__ == "__main__":
    main()
