"""Tests for set_viewer_config — validates that viewer configuration changes are applied correctly."""

import os
import time

import pytest
import cadquery as cq


@pytest.fixture(scope="module", autouse=True)
def enable_real_viewer():
    """These tests need real viewer interaction, so disable the pytest stub temporarily."""
    old_pytest = os.environ.pop("OCP_VSCODE_PYTEST", None)
    # Set port to avoid interactive prompt when multiple viewers exist
    old_port = os.environ.get("OCP_PORT")
    os.environ["OCP_PORT"] = "3939"
    yield
    if old_pytest is not None:
        os.environ["OCP_VSCODE_PYTEST"] = old_pytest
    if old_port is not None:
        os.environ["OCP_PORT"] = old_port
    else:
        os.environ.pop("OCP_PORT", None)


from ocp_vscode import (
    Camera,
    Collapse,
    combined_config,
    reset_defaults,
    set_defaults,
    set_viewer_config,
    show,
    status,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _approx_eq(x, y, tol=1e-2):
    """Check if two values are approximately equal."""
    if isinstance(x, float) or isinstance(y, float):
        return abs(x - y) < tol
    return x == y


def _equal(a, b):
    """Check equality, with tolerance for floats and element-wise for sequences."""
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_approx_eq(a[i], b[i]) for i in range(len(a)))
    return _approx_eq(a, b)


def get_state():
    """Get combined config with camera state from status."""
    s = combined_config()
    s2 = status()
    for key in ["position", "quaternion", "target", "zoom"]:
        s[key] = s2[key]
    return s


def assert_config(conf, delay=0.1):
    """Assert that all keys in conf match the current viewer state.

    A delay is needed because set_viewer_config is asynchronous - the viewer
    sends status updates via postMessage which is delivered after the current
    execution context yields.
    """
    time.sleep(delay)
    s = get_state()
    for k, v in conf.items():
        assert _equal(s[k], v), f"{k}: expected {v}, got {s[k]}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def assembly():
    """Create a test assembly for viewer tests."""
    box1 = cq.Workplane("XY").box(10, 20, 30).edges(">X or <X").chamfer(2)
    box1.name = "box1"

    box2 = cq.Workplane("XY").box(8, 18, 28).edges(">X or <X").chamfer(2)
    box2.name = "box2"

    box3 = (
        cq
        .Workplane("XY")
        .transformed(offset=(0, 15, 7))
        .box(30, 20, 6)
        .edges(">Z")
        .fillet(3)
    )
    box3.name = "box3"

    box4 = box3.mirror("XY").translate((0, -5, 0))
    box4.name = "box4"

    box1 = box1.cut(box2).cut(box3).cut(box4)

    a1 = (
        cq
        .Assembly(name="ensemble")
        .add(box1, name="red box", color="#d7191c80")
        .add(box3, name="green box", color="#abdda4")
        .add(box4, name="blue box", color=(43, 131, 186, 0.3))
    )
    return a1


@pytest.fixture(autouse=True)
def setup_defaults():
    """Reset defaults before each test and set camera to KEEP."""
    reset_defaults()
    set_defaults(reset_camera=Camera.KEEP)
    yield
    reset_defaults()


# ---------------------------------------------------------------------------
# Tests — Axes and Grid
# ---------------------------------------------------------------------------


class TestAxesAndGrid:
    def test_axes_grid_center(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(
            axes=True,
            axes0=True,
            grid=(True, False, False),
            center_grid=True,
        )
        set_viewer_config(**c)
        assert_config(c)

    def test_reset_defaults_axes(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(
            axes=True, axes0=True, grid=(True, False, False), center_grid=True
        )
        reset_defaults()
        assert_config(
            dict(axes=False, axes0=True, grid=(False, False, False), center_grid=False)
        )

    def test_grid_multiple_planes(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(grid=(True, True, False))
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Transparency and Edges
# ---------------------------------------------------------------------------


class TestTransparencyAndEdges:
    def test_transparent_black_edges(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(transparent=True, black_edges=True)
        set_viewer_config(**c)
        assert_config(c)

    def test_default_opacity_low(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(default_opacity=0.1)
        set_viewer_config(**c)
        assert_config(c)

    def test_default_opacity_high(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(default_opacity=0.9)
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Projection
# ---------------------------------------------------------------------------


class TestProjection:
    def test_ortho_false(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(ortho=False)
        set_viewer_config(**c)
        assert_config(c)

    def test_ortho_true(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(ortho=True)
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Explode
# ---------------------------------------------------------------------------


class TestExplode:
    def test_explode_on(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(explode=True)
        set_viewer_config(**c)
        assert_config(c)

    def test_explode_off(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(explode=True)
        c = dict(explode=False)
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Camera Position
# ---------------------------------------------------------------------------


class TestCameraPosition:
    def test_camera_settings(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(
            zoom=0.5,
            position=(-82.8758620758301, -90.1348297727537, 50.05278713951289),
            quaternion=(
                0.5260854883489195,
                -0.20303675503687996,
                -0.27189350671238977,
                0.7797974455333987,
            ),
            target=(0, 7.5, 0),
        )
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Edge Color and Transparency Combined
# ---------------------------------------------------------------------------


class TestEdgeColorTransparency:
    def test_edgecolor_opacity_transparent(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(default_edgecolor="#008000", default_opacity=0.1, transparent=True)
        set_viewer_config(**c)
        assert_config(c)

    def test_reset_edgecolor_opacity(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(
            default_edgecolor="#008000", default_opacity=0.1, transparent=True
        )
        reset_defaults()
        assert_config(
            dict(default_edgecolor="#707070", default_opacity=0.5, transparent=False)
        )


# ---------------------------------------------------------------------------
# Tests — Material Settings
# ---------------------------------------------------------------------------


class TestMaterialSettings:
    def test_material_properties(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(tab="material")
        c = dict(
            ambient_intensity=1.85, direct_intensity=1.67, metalness=0.9, roughness=0.6
        )
        set_viewer_config(**c)
        assert_config(c)

    def test_material_reset(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(
            ambient_intensity=1,
            direct_intensity=1.1,
            metalness=0.3,
            roughness=0.65,
            tab="tree",
        )


# ---------------------------------------------------------------------------
# Tests — Speed Settings
# ---------------------------------------------------------------------------


class TestSpeedSettings:
    def test_speed_low(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(zoom_speed=0.1, pan_speed=0.1, rotate_speed=0.1)
        set_viewer_config(**c)
        assert_config(c)

    def test_speed_reset(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(zoom_speed=0.1, pan_speed=0.1, rotate_speed=0.1)
        set_viewer_config(zoom_speed=1, pan_speed=1, rotate_speed=1)
        assert_config(dict(zoom_speed=1, pan_speed=1, rotate_speed=1))


# ---------------------------------------------------------------------------
# Tests — Glass and Tools
# ---------------------------------------------------------------------------


class TestGlassAndTools:
    def test_glass_false_tools_true(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(glass=False, tools=True)
        set_viewer_config(**c)
        assert_config(c)

    def test_glass_true_tools_true(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(glass=True, tools=True)
        set_viewer_config(**c)
        assert_config(c)

    def test_tools_false(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(tools=False)
        set_viewer_config(**c)
        assert_config(c)

    def test_tools_glass_combined(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(tools=True, glass=True)
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Collapse
# ---------------------------------------------------------------------------


class TestCollapse:
    def test_collapse_all(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(tab="tree")
        c = dict(collapse=Collapse.ALL)
        set_viewer_config(**c)
        assert_config(c)

    def test_collapse_none(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(collapse=Collapse.NONE)
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Clipping
# ---------------------------------------------------------------------------


class TestClipping:
    def test_clip_sliders_intersection(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(tab="clip")
        c = dict(
            clip_slider_0=2,
            clip_slider_1=-7,
            clip_slider_2=7,
            clip_intersection=True,
            clip_planes=True,
            clip_object_colors=True,
        )
        set_viewer_config(**c)
        assert_config(c)

    def test_clip_with_normals(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(tab="clip")
        c = dict(
            clip_slider_0=9.7,
            clip_slider_1=11.3,
            clip_slider_2=5.3,
            clip_normal_0=(-0.58, 0.58, -0.58),
            clip_normal_1=(0.16, -0.48, -0.87),
            clip_normal_2=(-0.56, 0.47, 0.68),
            clip_intersection=False,
            clip_planes=True,
            clip_object_colors=False,
        )
        set_viewer_config(**c)
        assert_config(c)


# ---------------------------------------------------------------------------
# Tests — Zebra
# ---------------------------------------------------------------------------


class TestZebra:
    def test_zebra_blackwhite_reflection(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(tab="zebra")
        c = dict(
            zebra_count=25,
            zebra_opacity=0.8,
            zebra_direction=45,
            zebra_color_scheme="blackwhite",
            zebra_mapping_mode="reflection",
        )
        set_viewer_config(**c)
        assert_config(c)

    def test_zebra_colorful_normal(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        set_viewer_config(tab="zebra")
        c = dict(
            zebra_count=10,
            zebra_opacity=0.5,
            zebra_direction=30,
            zebra_color_scheme="colorful",
            zebra_mapping_mode="normal",
        )
        set_viewer_config(**c)
        assert_config(c)

    def test_zebra_grayscale_max(self, assembly):
        show(assembly, reset_camera=Camera.RESET)
        c = dict(
            zebra_count=50,
            zebra_opacity=1.0,
            zebra_direction=90,
            zebra_color_scheme="grayscale",
            zebra_mapping_mode="reflection",
        )
        set_viewer_config(**c)
        assert_config(c)
