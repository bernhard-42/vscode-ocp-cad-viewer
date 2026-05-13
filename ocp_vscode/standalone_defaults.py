"""Defaults for the standalone OCP CAD Viewer.

Single source of truth. Imported by both ``standalone.py`` (to seed
``Viewer.configure``) and ``__main__.py`` (to render Click ``--help``
default values). Kept in its own tiny module so that importing the
defaults does not pull in Flask, orjson, ViewerBackend, etc.
"""

DEFAULTS = {
    "debug": False,
    "no_glass": False,
    "no_tools": False,
    "tree_width": 240,
    "theme": "browser",
    "control": "trackball",
    "modifier_keys": {
        "shift": "shiftKey",
        "ctrl": "ctrlKey",
        "meta": "metaKey",
        "alt": "altKey",
    },
    "new_tree_behavior": True,
    "pan_speed": 1,
    "rotate_speed": 1,
    "zoom_speed": 1,
    "axes": False,
    "axes0": True,
    "grid_xy": False,
    "grid_xz": False,
    "grid_yz": False,
    "perspective": False,
    "transparent": False,
    "black_edges": False,
    "collapse": "1",
    "reset_camera": "KEEP",
    "up": "Z",
    "ticks": 5,
    "center_grid": False,
    "grid_font_size": 12,
    "default_opacity": 0.5,
    "explode": False,
    "default_edgecolor": "#707070",
    "default_color": "#e8b024",
    "default_thickedgecolor": "MediumOrchid",
    "default_facecolor": "Violet",
    "default_vertexcolor": "MediumOrchid",
    "angular_tolerance": 0.2,
    "deviation": 0.1,
    "ambient_intensity": 1.0,
    "direct_intensity": 1.1,
    "metalness": 0.3,
    "roughness": 0.65,
}
