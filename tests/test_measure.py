"""Tests for ocp_vscode.measure — validates calc_angle, get_properties, get_distance."""

from math import cos, pi, sin, sqrt

import pytest
import build123d as bd

from ocp_vscode.measure import (
    calc_angle,
    calc_distance,
    get_distance,
    get_properties,
    get_shape_type,
    get_geom_type,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _w(obj):
    """Unwrap a build123d object to its TopoDS_Shape."""
    return obj.wrapped


def _approx_angle(value, expected, tol=0.5):
    """Assert angle value is within tol degrees of expected."""
    assert value == pytest.approx(expected, abs=tol), (
        f"expected ~{expected}°, got {value}°"
    )


def _approx_dist(value, expected, tol=0.01):
    """Assert distance is within tol of expected."""
    assert value == pytest.approx(expected, abs=tol), (
        f"expected ~{expected}, got {value}"
    )


def _approx_point(point, expected, tol=0.1):
    """Assert 3D point (tuple) is near expected."""
    for i, (a, b) in enumerate(zip(point, expected)):
        assert a == pytest.approx(b, abs=tol), (
            f"point[{i}]: expected ~{b}, got {a}; full point={point}"
        )


def _find(props, key):
    """Find a key in the sectioned result array of get_properties."""
    for section in props["result"]:
        if key in section:
            return section[key]
    raise KeyError(f"Key '{key}' not found in any section of result")


def _has(props, key):
    """Check if a key exists in any section of the result array."""
    return any(key in section for section in props["result"])


# ---------------------------------------------------------------------------
# Fixtures — edges
# ---------------------------------------------------------------------------

@pytest.fixture
def line_x():
    """Line along X axis, (0,0,0)→(10,0,0)."""
    return bd.Line((0, 0, 0), (10, 0, 0))


@pytest.fixture
def line_y():
    """Line along Y axis, (0,0,0)→(0,10,0)."""
    return bd.Line((0, 0, 0), (0, 10, 0))


@pytest.fixture
def line_z():
    """Line along Z axis, (0,0,0)→(0,0,10)."""
    return bd.Line((0, 0, 0), (0, 0, 10))


@pytest.fixture
def line_45_xy():
    """Line at 45° in XY plane, (0,0,0)→(10,10,0)."""
    return bd.Line((0, 0, 0), (10, 10, 0))


@pytest.fixture
def line_45_xz():
    """Line at 45° in XZ plane, (0,0,0)→(10,0,10)."""
    return bd.Line((0, 0, 0), (10, 0, 10))


@pytest.fixture
def circle_xy():
    """Circle radius 5 in XY plane, center at origin."""
    return bd.Circle(5).edge()


@pytest.fixture
def circle_xz():
    """Circle radius 5 in XZ plane, center at origin."""
    return bd.Rot(90, 0, 0) * bd.Circle(5).edge()


@pytest.fixture
def arc_xz():
    """Semicircular arc in XZ plane: (5,0,0) → (0,0,5) → (-5,0,0)."""
    return bd.Rot(90, 0, 0) * bd.CenterArc((0, 0, 0), 5, 0, 180)


@pytest.fixture
def spline_xy():
    """BSpline lying flat in XY plane."""
    return bd.Edge.make_spline([
        (0, 0, 0), (3, 2, 0), (6, -1, 0), (10, 1, 0),
    ])


# ---------------------------------------------------------------------------
# Fixtures — faces
# ---------------------------------------------------------------------------

@pytest.fixture
def face_xy():
    """20×20 planar face in XY plane (normal = +Z), centered at origin."""
    return bd.Rectangle(20, 20).face()


@pytest.fixture
def face_xz():
    """20×20 planar face in XZ plane (normal = ±Y), centered at origin."""
    return bd.Rot(90, 0, 0) * bd.Rectangle(20, 20).face()


@pytest.fixture
def face_tilted_45():
    """20×20 planar face tilted 45° from XY around the X axis."""
    return bd.Rot(45, 0, 0) * bd.Rectangle(20, 20).face()


@pytest.fixture
def cylinder_z():
    """Lateral face of cylinder along Z axis, radius 5, height 10."""
    return bd.Cylinder(5, 10).faces().sort_by()[1]


# ===========================================================================
# Shape type detection
# ===========================================================================

class TestShapeTypeDetection:
    def test_vertex(self):
        assert get_shape_type(_w(bd.Vertex(0, 0, 0))) == "Vertex"

    def test_edge_line(self, line_x):
        assert get_shape_type(_w(line_x)) == "Edge"
        assert get_geom_type(_w(line_x)) == "Line"

    def test_edge_circle(self, circle_xy):
        assert get_shape_type(_w(circle_xy)) == "Edge"
        assert get_geom_type(_w(circle_xy)) == "Circle"

    def test_face_plane(self, face_xy):
        assert get_shape_type(_w(face_xy)) == "Face"
        assert get_geom_type(_w(face_xy)) == "Plane"

    def test_face_cylinder(self, cylinder_z):
        assert get_shape_type(_w(cylinder_z)) == "Face"
        assert get_geom_type(_w(cylinder_z)) == "Cylinder"

    def test_solid(self):
        assert get_shape_type(_w(bd.Box(1, 1, 1).solid())) == "Solid"


# ===========================================================================
# calc_angle — Line vs Line, intersecting
# ===========================================================================

class TestCalcAngleLineLineIntersecting:
    def test_perpendicular_at_origin(self, line_x, line_y):
        """X-line and Y-line share origin → 90°."""
        result = calc_angle(_w(line_x), _w(line_y))
        assert result is not None
        _approx_angle(result["angle"], 90)
        assert result["reference 1"] == "line"
        assert result["reference 2"] == "line"
        _approx_point(result["direction 1"], (1, 0, 0))
        _approx_point(result["direction 2"], (0, 1, 0))

    def test_45_degrees(self, line_x, line_45_xy):
        """X-line vs 45° line in XY → 45°."""
        result = calc_angle(_w(line_x), _w(line_45_xy))
        assert result is not None
        _approx_angle(result["angle"], 45)

    def test_60_degrees(self):
        """Two lines at 60° sharing origin."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((0, 0, 0), (5, 5 * sqrt(3), 0))
        result = calc_angle(_w(line1), _w(line2))
        assert result is not None
        _approx_angle(result["angle"], 60)

    def test_collinear(self):
        """End-to-end collinear lines → 0°."""
        line1 = bd.Line((0, 0, 0), (5, 0, 0))
        line2 = bd.Line((5, 0, 0), (10, 0, 0))
        result = calc_angle(_w(line1), _w(line2))
        assert result is not None
        _approx_angle(result["angle"], 0)

    def test_antiparallel(self):
        """Opposite-direction lines sharing a point → 0° or 180°."""
        line1 = bd.Line((-5, 0, 0), (0, 0, 0))
        line2 = bd.Line((0, 0, 0), (5, 0, 0))
        result = calc_angle(_w(line1), _w(line2))
        assert result is not None
        assert result["angle"] == pytest.approx(0, abs=0.5) or \
               result["angle"] == pytest.approx(180, abs=0.5)


# ===========================================================================
# calc_angle — Line vs Line, non-intersecting (skew / parallel)
# ===========================================================================

class TestCalcAngleLineLineSkew:
    def test_perpendicular_skew(self):
        """X-line and Z-line offset 5 in Y, don't cross → 90°."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((3, 5, 0), (3, 5, 10))
        result = calc_angle(_w(line1), _w(line2))
        assert result is not None
        _approx_angle(result["angle"], 90)

    def test_parallel_offset(self):
        """Two parallel X-lines 4 apart in Y → 0°."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((0, 4, 0), (10, 4, 0))
        result = calc_angle(_w(line1), _w(line2))
        assert result is not None
        _approx_angle(result["angle"], 0)

    def test_45_degrees_skew(self):
        """X-line and 45° XY-line offset in Z → 45°."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((0, 0, 5), (10, 10, 5))
        result = calc_angle(_w(line1), _w(line2))
        assert result is not None
        _approx_angle(result["angle"], 45)


# ===========================================================================
# calc_angle — Edge vs Face, intersecting
# ===========================================================================

class TestCalcAngleEdgeFaceIntersecting:
    def test_line_perpendicular_through_face(self, face_xy):
        """Z-line pierces XY face → 90°."""
        line = bd.Line((0, 0, -5), (0, 0, 5))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 90)
        assert result["reference 1"] == "line"
        assert result["reference 2"] == "face normal"
        _approx_point(result["direction 1"], (0, 0, 1))
        # XY face normal is ±Z
        assert abs(result["normal 2"][2]) == pytest.approx(1, abs=0.01)

    def test_line_at_30_degrees(self, face_xy):
        """Line at 30° from horizontal piercing XY face → 30°."""
        dx = 10 * cos(30 * pi / 180)
        dz = 10 * sin(30 * pi / 180)
        line = bd.Line((0, 0, -dz / 2), (dx, 0, dz / 2))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 30)

    def test_line_at_45_degrees(self, face_xy):
        """Line at 45° from horizontal piercing XY face → 45°."""
        line = bd.Line((0, 0, -5), (10, 0, 5))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 45)

    def test_line_at_60_degrees(self, face_xy):
        """Line at 60° from horizontal piercing XY face → 60°."""
        dx = 10 * cos(60 * pi / 180)
        dz = 10 * sin(60 * pi / 180)
        line = bd.Line((0, 0, -dz / 2), (dx, 0, dz / 2))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 60)

    def test_line_lying_in_face(self, face_xy):
        """Line in the XY plane → 0° to surface."""
        line = bd.Line((-5, 0, 0), (5, 0, 0))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 0)


# ===========================================================================
# calc_angle — Edge vs Face, non-intersecting
# ===========================================================================

class TestCalcAngleEdgeFaceNonIntersecting:
    def test_line_parallel_above_face(self, face_xy):
        """X-line at z=5 above XY face → 0°."""
        line = bd.Line((0, 0, 5), (10, 0, 5))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 0)

    def test_line_perpendicular_above_face(self, face_xy):
        """Short Z-line high above XY face → 90°."""
        line = bd.Line((0, 0, 10), (0, 0, 20))
        result = calc_angle(_w(line), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 90)

    def test_order_swap_gives_same_angle(self, face_xy):
        """calc_angle(edge, face) == calc_angle(face, edge)."""
        line = bd.Line((0, 0, 5), (10, 0, 5))
        r1 = calc_angle(_w(line), _w(face_xy))
        r2 = calc_angle(_w(face_xy), _w(line))
        assert r1 is not None and r2 is not None
        _approx_angle(r1["angle"], r2["angle"])
        # info fields swap when order swaps
        assert r1["reference 1"] == "line" and r1["reference 2"] == "face normal"
        assert r2["reference 1"] == "face normal" and r2["reference 2"] == "line"
        # direction/normal keys swap too
        assert "direction 1" in r1 and "normal 2" in r1
        assert "normal 1" in r2 and "direction 2" in r2


# ===========================================================================
# calc_angle — Face vs Face, intersecting
# ===========================================================================

class TestCalcAngleFaceFaceIntersecting:
    def test_box_adjacent_faces_90(self):
        """Top and front face of a box share an edge → 90°."""
        box = bd.Box(10, 10, 10)
        top = box.faces().sort_by(bd.Axis.Z)[-1]
        front = box.faces().sort_by(bd.Axis.Y)[-1]
        result = calc_angle(_w(top), _w(front))
        assert result is not None
        _approx_angle(result["angle"], 90)
        assert result["reference 1"] == "face normal"
        assert result["reference 2"] == "face normal"
        # top normal is +Z, front normal is +Y
        assert abs(result["normal 1"][2]) == pytest.approx(1, abs=0.01)
        assert abs(result["normal 2"][1]) == pytest.approx(1, abs=0.01)

    def test_perpendicular_at_origin(self, face_xy, face_xz):
        """XY and XZ faces through origin → 90°."""
        result = calc_angle(_w(face_xy), _w(face_xz))
        assert result is not None
        _approx_angle(result["angle"], 90)

    def test_45_dihedral(self, face_xy, face_tilted_45):
        """XY face and 45°-tilted face → 45°."""
        result = calc_angle(_w(face_xy), _w(face_tilted_45))
        assert result is not None
        _approx_angle(result["angle"], 45)


# ===========================================================================
# calc_angle — Face vs Face, non-intersecting
# ===========================================================================

class TestCalcAngleFaceFaceNonIntersecting:
    def test_parallel_offset_z(self):
        """Two XY faces 7 apart in Z → 0° (or 180° if opposite orientation)."""
        f1 = bd.Rectangle(10, 10).face()
        f2 = bd.Pos(0, 0, 7) * bd.Rectangle(10, 10).face()
        result = calc_angle(_w(f1), _w(f2))
        assert result is not None
        assert result["angle"] == pytest.approx(0, abs=0.5) or \
               result["angle"] == pytest.approx(180, abs=0.5)

    def test_perpendicular_offset(self):
        """XY face and YZ face 20 apart → 90°."""
        f_xy = bd.Rectangle(10, 10).face()
        f_yz = bd.Pos(20, 0, 5) * bd.Rot(0, 90, 0) * bd.Rectangle(10, 10).face()
        result = calc_angle(_w(f_xy), _w(f_yz))
        assert result is not None
        _approx_angle(result["angle"], 90)


# ===========================================================================
# calc_angle — Non-planar edges (new capability)
# ===========================================================================

class TestCalcAngleNonPlanarEdges:
    def test_circles_perpendicular_planes(self, circle_xy, circle_xz):
        """Circles in XY and XZ planes intersect at (±5,0,0).
        At intersection: XY tangent=(0,±1,0), XZ tangent=(0,0,±1) → 90°.
        """
        result = calc_angle(_w(circle_xy), _w(circle_xz))
        assert result is not None
        _approx_angle(result["angle"], 90)
        assert result["reference 1"] == "tangent at P1"
        assert result["reference 2"] == "tangent at P2"

    def test_arc_xz_vs_line_x(self, arc_xz, line_x):
        """Arc in XZ starts at (5,0,0) with tangent (0,0,1).
        Line along X has tangent (1,0,0). They touch at (5,0,0) → 90°.
        """
        result = calc_angle(_w(arc_xz), _w(line_x))
        assert result is not None
        _approx_angle(result["angle"], 90)

    def test_spline_xy_vs_xy_face(self, spline_xy, face_xy):
        """BSpline flat in XY vs XY face: tangent is in XY, normal is Z.
        tangent ⊥ normal → edge-to-surface = |90-90| = 0°.
        """
        result = calc_angle(_w(spline_xy), _w(face_xy))
        assert result is not None
        _approx_angle(result["angle"], 0, tol=1)
        assert result["reference 1"] == "tangent at P1"
        assert result["reference 2"] == "face normal"

    def test_spline_3d_vs_line(self):
        """3D BSpline vs line: must return a result (was None in old code)."""
        spline = bd.Edge.make_spline([
            (0, 0, 0), (3, 2, 1), (7, -1, 3), (10, 1, 0),
        ])
        line = bd.Line((0, 5, 0), (10, 5, 0))
        result = calc_angle(_w(spline), _w(line))
        assert result is not None
        assert result["reference 1"] == "tangent at P1"
        assert result["reference 2"] == "line"
        # Angle is geometry-dependent but must be in valid range
        assert 0 <= result["angle"] <= 180


# ===========================================================================
# calc_angle — Non-planar faces (new capability)
# ===========================================================================

class TestCalcAngleNonPlanarFaces:
    def test_coaxial_cylinders_parallel_normals(self):
        """Two coaxial cylinders (r=3, r=6) along Z.
        Normals both radially outward on same ray → 0°.
        """
        inner = bd.Cylinder(3, 10).faces().sort_by()[1]
        outer = bd.Cylinder(6, 10).faces().sort_by()[1]
        result = calc_angle(_w(inner), _w(outer))
        assert result is not None
        _approx_angle(result["angle"], 0)
        assert result["reference 1"] == "surface normal at P1"
        assert result["reference 2"] == "surface normal at P2"
        # Both normals should be radial (in XY plane, Z≈0)
        assert result["normal 1"][2] == pytest.approx(0, abs=0.01)
        assert result["normal 2"][2] == pytest.approx(0, abs=0.01)

    def test_cylinder_vs_xy_plane(self, cylinder_z):
        """Cylinder (normals horizontal) vs XY plane below (normal vertical) → 90°."""
        plane = bd.Pos(0, 0, -3) * bd.Rectangle(20, 20).face()
        result = calc_angle(_w(cylinder_z), _w(plane))
        assert result is not None
        _approx_angle(result["angle"], 90)

    def test_sphere_vs_yz_plane(self):
        """Sphere at (10,0,0) r=3 vs YZ plane: closest point is on equator
        (avoids pole singularity), normals both along X → 0° or 180°.
        """
        sph = bd.Pos(10, 0, 0) * bd.Sphere(3).face()
        plane = bd.Rot(0, 90, 0) * bd.Rectangle(20, 20).face()
        result = calc_angle(_w(sph), _w(plane))
        assert result is not None
        assert result["angle"] == pytest.approx(0, abs=0.5) or \
               result["angle"] == pytest.approx(180, abs=0.5)

    def test_two_spheres(self):
        """Two spheres on X axis, 14 apart: outward normals are antiparallel → 180°."""
        sph1 = bd.Sphere(3).face()
        sph2 = bd.Pos(20, 0, 0) * bd.Sphere(3).face()
        result = calc_angle(_w(sph1), _w(sph2))
        assert result is not None
        _approx_angle(result["angle"], 180)


# ===========================================================================
# calc_angle — Rejection
# ===========================================================================

class TestCalcAngleRejection:
    def test_vertex_edge(self, line_x):
        assert calc_angle(_w(bd.Vertex(0, 0, 0)), _w(line_x)) is None

    def test_vertex_face(self, face_xy):
        assert calc_angle(_w(bd.Vertex(0, 0, 0)), _w(face_xy)) is None

    def test_solid_edge(self, line_x):
        assert calc_angle(_w(bd.Box(1, 1, 1).solid()), _w(line_x)) is None

    def test_two_vertices(self):
        assert calc_angle(_w(bd.Vertex(0, 0, 0)), _w(bd.Vertex(1, 1, 1))) is None


# ===========================================================================
# calc_distance — concrete distances and point coordinates
# ===========================================================================

class TestCalcDistance:
    def test_vertex_to_line(self, line_x):
        """Vertex (5,3,4) to X-line → dist=5, P1=(5,3,4), P2=(5,0,0)."""
        v = bd.Vertex(5, 3, 4)
        result = calc_distance(_w(v), _w(line_x))
        _approx_dist(result["distance"], 5.0)
        _approx_point(result["point 1"], (5, 3, 4))
        _approx_point(result["point 2"], (5, 0, 0))

    def test_vertex_to_face(self, face_xy):
        """Vertex (3,4,7) to XY face → dist=7, P1=(3,4,7), foot=(3,4,0)."""
        v = bd.Vertex(3, 4, 7)
        result = calc_distance(_w(v), _w(face_xy))
        _approx_dist(result["distance"], 7.0)
        _approx_point(result["point 1"], (3, 4, 7))
        _approx_point(result["point 2"], (3, 4, 0))

    def test_skew_lines_distance_and_points(self):
        """Skew X-line and Z-line offset 5 in Y at x=3: unique closest pair."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((3, 5, 0), (3, 5, 10))
        result = calc_distance(_w(line1), _w(line2))
        _approx_dist(result["distance"], 5.0)
        _approx_point(result["point 1"], (3, 0, 0))
        _approx_point(result["point 2"], (3, 5, 0))

    def test_parallel_lines_distance(self):
        """Two parallel X-lines 4 apart in Y → dist=4."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((0, 4, 0), (10, 4, 0))
        result = calc_distance(_w(line1), _w(line2))
        _approx_dist(result["distance"], 4.0)

    def test_parallel_faces_distance(self):
        """Two XY faces 7 apart in Z → dist=7."""
        f1 = bd.Rectangle(10, 10).face()
        f2 = bd.Pos(0, 0, 7) * bd.Rectangle(10, 10).face()
        result = calc_distance(_w(f1), _w(f2))
        _approx_dist(result["distance"], 7.0)

    def test_coaxial_cylinders_distance(self):
        """Two coaxial cylinders r=3, r=6 → dist=3."""
        inner = bd.Cylinder(3, 10).faces().sort_by()[1]
        outer = bd.Cylinder(6, 10).faces().sort_by()[1]
        result = calc_distance(_w(inner), _w(outer))
        _approx_dist(result["distance"], 3.0)

    def test_sphere_above_plane(self):
        """Sphere at (0,0,10) r=3 above XY plane → dist=7, bottom at (0,0,7)."""
        sph = bd.Pos(0, 0, 10) * bd.Sphere(3).face()
        plane = bd.Rectangle(20, 20).face()
        result = calc_distance(_w(sph), _w(plane))
        _approx_dist(result["distance"], 7.0)
        _approx_point(result["point 1"], (0, 0, 7))
        _approx_point(result["point 2"], (0, 0, 0))

    def test_two_spheres_distance(self):
        """Two spheres r=3 at origin and x=20 → dist=14, points at (3,0,0) and (17,0,0)."""
        sph1 = bd.Sphere(3).face()
        sph2 = bd.Pos(20, 0, 0) * bd.Sphere(3).face()
        result = calc_distance(_w(sph1), _w(sph2))
        _approx_dist(result["distance"], 14.0)
        _approx_point(result["point 1"], (3, 0, 0))
        _approx_point(result["point 2"], (17, 0, 0))

    def test_intersecting_lines_distance_zero(self, line_x, line_y):
        """Intersecting lines → distance = 0."""
        result = calc_distance(_w(line_x), _w(line_y))
        _approx_dist(result["distance"], 0.0)

    def test_xyz_components(self, line_x):
        """Vertex (5,3,4) to X-line: ΔX=0, ΔY=3, ΔZ=4."""
        v = bd.Vertex(5, 3, 4)
        result = calc_distance(_w(v), _w(line_x))
        _approx_dist(result["⇒ X | Y | Z"][0], 0.0)
        _approx_dist(result["⇒ X | Y | Z"][1], 3.0)
        _approx_dist(result["⇒ X | Y | Z"][2], 4.0)

    def test_center_distance(self):
        """Center-to-center distance of two circles 10 apart."""
        c1 = bd.Circle(1).edge()
        c2 = bd.Pos(10, 0, 0) * bd.Circle(1).edge()
        result = calc_distance(_w(c1), _w(c2), center=True)
        _approx_dist(result["distance"], 10.0)
        assert result["info"] == "center"


# ===========================================================================
# get_distance — combined distance + angle
# ===========================================================================

class TestGetDistance:
    def test_perpendicular_lines_intersecting(self, line_x, line_y):
        """X and Y lines at origin → dist=0, angle=90°."""
        resp = get_distance(_w(line_x), _w(line_y), center=False)
        sections = resp["result"]
        assert len(sections) == 3
        _approx_dist(sections[0]["distance"], 0.0)
        _approx_angle(sections[2]["angle"], 90)

    def test_perpendicular_faces(self, face_xy, face_xz):
        resp = get_distance(_w(face_xy), _w(face_xz), center=False)
        _approx_angle(resp["result"][2]["angle"], 90)

    def test_line_above_face(self, face_xy):
        """X-line at z=5 above XY face → dist=5, angle=0°."""
        line = bd.Line((0, 0, 5), (10, 0, 5))
        resp = get_distance(_w(line), _w(face_xy), center=False)
        _approx_dist(resp["result"][0]["distance"], 5.0)
        _approx_angle(resp["result"][2]["angle"], 0)

    def test_vertex_has_no_angle(self, line_x):
        """Vertex + line → distance present, no angle section."""
        v = bd.Vertex(5, 5, 0)
        resp = get_distance(_w(v), _w(line_x), center=False)
        assert len(resp["result"]) == 2
        _approx_dist(resp["result"][0]["distance"], 5.0)

    def test_skew_lines_combined(self):
        """Skew perpendicular lines → dist=5, angle=90°."""
        line1 = bd.Line((0, 0, 0), (10, 0, 0))
        line2 = bd.Line((3, 5, 0), (3, 5, 10))
        resp = get_distance(_w(line1), _w(line2), center=False)
        _approx_dist(resp["result"][0]["distance"], 5.0)
        _approx_angle(resp["result"][2]["angle"], 90)

    def test_sections_structure(self, line_x, face_xy):
        """Verify the response structure: refpoints at top, sections in result."""
        line = bd.Line((0, 0, 5), (10, 0, 5))
        resp = get_distance(_w(line), _w(face_xy), center=False)
        # refpoints at top level
        assert "refpoint1" in resp
        assert "refpoint2" in resp
        sections = resp["result"]
        assert len(sections) == 3
        # Section 0: distance data
        assert "distance" in sections[0]
        assert "⇒ X | Y | Z" in sections[0]
        assert "info" in sections[0]
        # Section 1: points
        assert "point 1" in sections[1]
        assert "point 2" in sections[1]
        # Section 2: angle data
        assert "angle" in sections[2]
        assert "reference 1" in sections[2]
        assert "reference 2" in sections[2]


# ===========================================================================
# get_properties — Edge "Angle@i to XY"
# ===========================================================================

class TestGetPropertiesEdgeAngleToXY:
    def test_horizontal_line(self, line_x):
        """Horizontal line → 0° at both endpoints."""
        props = get_properties(_w(line_x))
        _approx_angle(_find(props, "angle@0 to XY"), 0)
        _approx_angle(_find(props, "angle@1 to XY"), 0)

    def test_vertical_line(self, line_z):
        """Vertical line → 90° at both endpoints."""
        props = get_properties(_w(line_z))
        _approx_angle(_find(props, "angle@0 to XY"), 90)
        _approx_angle(_find(props, "angle@1 to XY"), 90)

    def test_45_line(self, line_45_xz):
        """45° line in XZ → 45° at both endpoints."""
        props = get_properties(_w(line_45_xz))
        _approx_angle(_find(props, "angle@0 to XY"), 45)
        _approx_angle(_find(props, "angle@1 to XY"), 45)

    def test_30_degree_line(self):
        """Line at 30° from horizontal → 30° at both endpoints."""
        dx = 10 * cos(30 * pi / 180)
        dz = 10 * sin(30 * pi / 180)
        line = bd.Line((0, 0, 0), (dx, 0, dz))
        props = get_properties(_w(line))
        _approx_angle(_find(props, "angle@0 to XY"), 30)
        _approx_angle(_find(props, "angle@1 to XY"), 30)

    def test_60_degree_line(self):
        """Line at 60° from horizontal → 60° at both endpoints."""
        dx = 10 * cos(60 * pi / 180)
        dz = 10 * sin(60 * pi / 180)
        line = bd.Line((0, 0, 0), (dx, 0, dz))
        props = get_properties(_w(line))
        _approx_angle(_find(props, "angle@0 to XY"), 60)
        _approx_angle(_find(props, "angle@1 to XY"), 60)

    def test_spline_in_xy_plane(self, spline_xy):
        """BSpline in XY → endpoints near 0° to XY."""
        props = get_properties(_w(spline_xy))
        assert _has(props, "angle@0 to XY")
        assert _has(props, "angle@1 to XY")
        _approx_angle(_find(props, "angle@0 to XY"), 0, tol=5)
        _approx_angle(_find(props, "angle@1 to XY"), 0, tol=5)

    def test_circle_in_xy(self, circle_xy):
        """Circle in XY → tangent always horizontal → 0°."""
        props = get_properties(_w(circle_xy))
        _approx_angle(_find(props, "angle@0 to XY"), 0)


# ===========================================================================
# get_properties — Face "angle to XY"
# ===========================================================================

class TestGetPropertiesFaceAngleToXY:
    def test_xy_face(self, face_xy):
        """XY face → 0°."""
        props = get_properties(_w(face_xy))
        _approx_angle(_find(props, "angle to XY"), 0)

    def test_xz_face(self, face_xz):
        """XZ face → 90°."""
        props = get_properties(_w(face_xz))
        _approx_angle(_find(props, "angle to XY"), 90)

    def test_45_tilted_face(self, face_tilted_45):
        """45° tilted face → 45°."""
        props = get_properties(_w(face_tilted_45))
        _approx_angle(_find(props, "angle to XY"), 45)

    def test_cylinder_along_z(self, cylinder_z):
        """Cylinder along Z: normal at center is horizontal → 90° to XY."""
        props = get_properties(_w(cylinder_z))
        assert _has(props, "angle to XY")
        _approx_angle(_find(props, "angle to XY"), 90)

    def test_sphere(self):
        """Sphere at origin: normal at center-UV exists."""
        sph = bd.Sphere(5).face()
        props = get_properties(_w(sph))
        assert _has(props, "angle to XY")


# ===========================================================================
# get_properties — basic shape info
# ===========================================================================

class TestGetPropertiesBasic:
    def test_vertex_coordinates(self):
        props = get_properties(_w(bd.Vertex(1, 2, 3)))
        assert props["shape_type"] == "Vertex"
        _approx_point(_find(props, "xyz"), (1, 2, 3), tol=0.001)

    def test_line_length(self, line_x):
        props = get_properties(_w(line_x))
        assert props["geom_type"] == "Line"
        _approx_dist(_find(props, "length"), 10.0)

    def test_line_endpoints(self, line_x):
        props = get_properties(_w(line_x))
        _approx_point(_find(props, "start"), (0, 0, 0))
        _approx_point(_find(props, "end"), (10, 0, 0))
        _approx_point(_find(props, "middle"), (5, 0, 0))

    def test_circle_properties(self, circle_xy):
        props = get_properties(_w(circle_xy))
        assert props["geom_type"] == "Circle"
        _approx_dist(_find(props, "radius"), 5.0)
        _approx_point(_find(props, "center"), (0, 0, 0))

    def test_face_area(self):
        props = get_properties(_w(bd.Rectangle(5, 8).face()))
        assert props["shape_type"] == "Face"
        _approx_dist(_find(props, "area"), 40.0)

    def test_solid_volume(self):
        props = get_properties(_w(bd.Box(2, 3, 4).solid()))
        assert props["shape_type"] == "Solid"
        _approx_dist(_find(props, "volume"), 24.0)

    def test_cylinder_face_radius(self, cylinder_z):
        props = get_properties(_w(cylinder_z))
        assert props["geom_type"] == "Cylinder"
        _approx_dist(_find(props, "radius"), 5.0)

    def test_bounding_box(self, line_x):
        props = get_properties(_w(line_x))
        bb = _find(props, "bb")
        _approx_point(bb["min"], (0, 0, 0))
        _approx_point(bb["max"], (10, 0, 0))

    def test_sections_structure_vertex(self):
        """Vertex: 1 section (xyz)."""
        props = get_properties(_w(bd.Vertex(1, 2, 3)))
        assert "result" in props
        assert len(props["result"]) == 1
        assert "xyz" in props["result"][0]

    def test_sections_structure_edge(self, line_x):
        """Line edge: pos section, meas section, bb section."""
        props = get_properties(_w(line_x))
        assert "result" in props
        assert len(props["result"]) == 3
        assert _has(props, "start")
        assert _has(props, "length")
        assert _has(props, "bb")

    def test_sections_structure_face(self, face_xy):
        """Planar face: geom section, meas section, bb section."""
        props = get_properties(_w(face_xy))
        assert "result" in props
        assert _has(props, "area")
        assert _has(props, "bb")

    def test_sections_structure_solid(self):
        """Solid: volume section, bb section."""
        props = get_properties(_w(bd.Box(2, 3, 4).solid()))
        assert "result" in props
        assert len(props["result"]) == 2
        assert _has(props, "volume")
        assert _has(props, "bb")

    def test_top_level_metadata(self, line_x):
        """shape_type, geom_type, refpoint at top level."""
        props = get_properties(_w(line_x))
        assert props["shape_type"] == "Edge"
        assert props["geom_type"] == "Line"
        assert props["refpoint"] is not None
