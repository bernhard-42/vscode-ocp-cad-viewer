from math import pi

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_SupportType
from OCP.BRepGProp import BRepGProp_Face
from OCP.BRepTools import BRepTools
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.BRep import BRep_Tool
from OCP.gp import gp_Dir, gp_Pnt, gp_Vec

from ocp_tessellate.ocp_utils import (
    area,
    BoundingBox,
    center_of_geometry,
    center_of_mass,
    downcast,
    dist_shapes,
    get_curve,
    get_point,
    get_surface,
    is_closed,
    is_topods_edge,
    is_topods_face,
    is_topods_solid,
    is_topods_compound,
    is_topods_compsolid,
    is_topods_vertex,
    is_vector,
    length,
    position_at,
    tangent_at,
    vertex,
    volume,
)


def get_shape_type(shape):
    if is_topods_vertex(shape) or is_vector(shape):
        return "Vertex"
    elif is_topods_edge(shape):
        return "Edge"
    elif is_topods_face(shape):
        return "Face"
    elif is_topods_solid(shape):
        return "Solid"
    elif is_topods_compsolid(shape):
        return "CompSolid"
    elif is_topods_compound(shape):
        return "Compound"
    else:
        print(shape, "unknown")
        return "Unknown"


def get_geom_type(shape):
    if is_topods_vertex(shape) or is_vector(shape):
        return "Point"
    elif is_topods_edge(shape):
        return get_curve(shape).GetType().name.split("_")[-1]
    elif is_topods_face(shape):
        return get_surface(shape).GetType().name.split("_")[-1]
    elif (
        is_topods_solid(shape)
        or is_topods_compound(shape)
        or is_topods_compsolid(shape)
    ):
        return "Other"
    else:
        print(shape, "unknown")
        return "Unknown"


def get_properties(shape):
    shape = downcast(shape)
    shape_type = get_shape_type(shape)
    geom_type = get_geom_type(shape)

    refpoint = None
    sections = []

    if shape_type == "Vertex":
        pt = get_point(shape)
        refpoint = pt
        sections.append({"xyz": pt})

    elif shape_type == "Edge":
        shape = downcast(shape)
        geom_section = {}
        pos_section = {}

        if geom_type == "Line":
            pos_section["start"] = get_point(position_at(shape, 0))
            pos_section["middle"] = get_point(position_at(shape, 0.5))
            pos_section["end"] = get_point(position_at(shape, 1))
            refpoint = get_point(position_at(shape, 0.5))

        elif geom_type == "Circle":
            circle = get_curve(shape).Circle()
            geom_section["center"] = get_point(circle.Location())
            geom_section["radius / diam"] = (
                f"{circle.Radius():.3f} /  {2 * circle.Radius():.3f}"
            )
            pos_section["start"] = get_point(position_at(shape, 0))
            if not is_closed(shape):
                pos_section["end"] = get_point(position_at(shape, 1))
                refpoint = get_point(position_at(shape, 0.5))
            else:
                refpoint = get_point(position_at(shape, 0))

        elif geom_type == "Ellipse":
            ellipse = get_curve(shape).Ellipse()
            geom_section["center"] = get_point(ellipse.Location())
            geom_section["major radius / diam"] = (
                f"{ellipse.MajorRadius():.3f} /  {2 * ellipse.MajorRadius():.3f}"
            )
            geom_section["minor radius / diam"] = (
                f"{ellipse.MinorRadius():.3f} /  {2 * ellipse.MinorRadius():.3f}"
            )
            pos_section["start"] = get_point(position_at(shape, 0))
            if not is_closed(shape):
                pos_section["end"] = get_point(position_at(shape, 1))
                refpoint = get_point(position_at(shape, 0.5))
            else:
                refpoint = get_point(position_at(shape, 0))

        elif geom_type == "Hyperbola":
            hyperbola = get_curve(shape).Hyperbola()
            pos_section["start"] = get_point(position_at(shape, 0))
            pos_section["vertex"] = get_point(hyperbola.Location())
            pos_section["end"] = get_point(position_at(shape, 1))
            refpoint = get_point(position_at(shape, 0.5))

        elif geom_type == "Parabola":
            parabola = get_curve(shape).Parabola()
            pos_section["start"] = get_point(position_at(shape, 0))
            pos_section["vertex"] = get_point(parabola.Location())
            pos_section["end"] = get_point(position_at(shape, 1))
            refpoint = get_point(position_at(shape, 0.5))

        elif geom_type in ["Bezier", "Bspline"]:
            pos_section["start"] = get_point(position_at(shape, 0))
            pos_section["middle"] = get_point(position_at(shape, 0.5))
            pos_section["end"] = get_point(position_at(shape, 1))
            refpoint = get_point(position_at(shape, 0.5))

        elif geom_type == "OffsetCurve":
            offset = get_curve(shape).OffsetCurve()
            geom_section["offset"] = offset.Offset()
            pos_section["start"] = get_point(position_at(shape, 0))
            if is_closed(shape):
                pos_section["end"] = get_point(position_at(shape, 1))
            refpoint = get_point(position_at(shape, 0))

        else:
            pos_section["start"] = get_point(position_at(shape, 0))
            pos_section["middle"] = get_point(position_at(shape, 0.5))
            pos_section["end"] = get_point(position_at(shape, 1))
            refpoint = get_point(position_at(shape, 0.5))

        if geom_section:
            sections.append(geom_section)
        if pos_section:
            sections.append(pos_section)

        meas_section = {"length": length(shape)}
        xy_normal = gp_Dir(0, 0, 1)
        for i in [0, 1]:
            try:
                _, tangent_dir = tangent_at(shape, i)
                angle = abs(90 - tangent_dir.Angle(xy_normal) / pi * 180)
                meas_section[f"angle@{i} to XY"] = angle
            except Exception:
                pass
        sections.append(meas_section)

    elif shape_type == "Face":
        shape = downcast(shape)
        geom_section = {}

        if geom_type == "Plane":
            plane = get_surface(shape).Plane()
            geom_section["center"] = get_point(plane.Location())

        elif geom_type == "Cylinder":
            cylinder = get_surface(shape).Cylinder()
            geom_section["center"] = get_point(cylinder.Location())
            geom_section["radius"] = cylinder.Radius()

        elif geom_type == "Cone":
            cone = get_surface(shape).Cone()
            geom_section["center"] = get_point(cone.Location())
            geom_section["base radius"] = cone.RefRadius()
            geom_section["half angle"] = cone.SemiAngle() / pi * 180

        elif geom_type == "Sphere":
            sphere = get_surface(shape).Sphere()
            geom_section["center"] = get_point(sphere.Location())
            geom_section["radius"] = sphere.Radius()

        elif geom_type == "Torus":
            torus = get_surface(shape).Torus()
            geom_section["center"] = get_point(torus.Location())
            geom_section["minor radius"] = torus.MinorRadius()
            geom_section["major radius"] = torus.MajorRadius()

        elif geom_type == "SurfaceOfRevolution":
            revolution = get_surface(shape)
            geom_section["axe loc"] = get_point(
                revolution.AxeOfRevolution().Location()
            )
            geom_section["axe dir"] = get_point(
                revolution.AxeOfRevolution().Direction()
            )
            geom_type = "Revolution"

        elif geom_type == "Bezier":
            ...

        elif geom_type == "Bspline":
            ...

        if geom_section:
            sections.append(geom_section)

        refpoint = center_of_geometry(shape)

        meas_section = {"area": area(shape)}
        try:
            u0, u1, v0, v1 = BRepTools.UVBounds_s(shape)
            pnt, normal = gp_Pnt(), gp_Vec()
            BRepGProp_Face(shape).Normal(
                (u0 + u1) / 2, (v0 + v1) / 2, pnt, normal
            )
            if normal.Magnitude() > 1e-10:
                a = gp_Dir(normal).Angle(gp_Dir(0, 0, 1)) / pi * 180
                meas_section["angle to XY"] = a
        except Exception:
            pass
        sections.append(meas_section)

    elif shape_type in ["Solid", "CompSolid", "Compound"]:
        shape = downcast(shape)
        sections.append({"volume": volume(shape)})
        refpoint = center_of_mass(shape)

    else:
        print(f"unknown shape {type(shape)}")

    if shape_type != "Vertex":
        bb = BoundingBox(shape, optimal=True)
        sections.append({
            "bb": {
                "min": [bb.xmin, bb.ymin, bb.zmin],
                "center": bb.center,
                "max": [bb.xmax, bb.ymax, bb.zmax],
                "size": [bb.xsize, bb.ysize, bb.zsize],
            }
        })

    return {
        "shape_type": shape_type,
        "geom_type": geom_type,
        "refpoint": refpoint,
        "result": sections,
    }


def get_center(shape):
    shape_type = get_shape_type(shape)
    geom_type = get_geom_type(shape)

    if shape_type == "Vertex":
        center = shape

    elif shape_type == "Edge":
        if geom_type == "Circle":
            circle = get_curve(shape).Circle()
            center = circle.Location()

        elif geom_type == "Ellipse":
            ellipse = get_curve(shape).Ellipse()
            center = ellipse.Location()

        elif geom_type == "Hyperbola":
            hyperbola = get_curve(shape).Hyperbola()
            center = hyperbola.Location()

        elif geom_type == "Parabola":
            parabola = get_curve(shape).Parabola()
            center = parabola.Location()

        else:
            center = position_at(shape, 0.5)

    elif shape_type == "Face":
        if geom_type == "Cylinder":
            cylinder = get_surface(shape).Cylinder()
            center = cylinder.Location()

        elif geom_type == "Cone":
            cone = get_surface(shape).Cone()
            center = cone.Location()

        elif geom_type == "Sphere":
            sphere = get_surface(shape).Sphere()
            center = sphere.Location()

        elif geom_type == "Torus":
            torus = get_surface(shape).Torus()
            center = torus.Location()

        elif geom_type == "SurfaceOfRevolution":
            revolution = get_surface(shape)
            center = revolution.AxeOfRevolution().Location()

        else:
            center = center_of_mass(shape)

    elif shape_type == "Solid":
        center = center_of_mass(shape)

    else:
        print(shape_type, shape)

    if is_topods_vertex(center):
        return center
    else:
        return vertex(center)


def calc_distance(shape1, shape2, center=False):
    shape1 = downcast(shape1)
    shape2 = downcast(shape2)

    if center:
        p1 = get_center(shape1)
        p2 = get_center(shape2)
        dist, p1, p2 = dist_shapes(p1, p2)
    else:
        dist, p1, p2 = dist_shapes(shape1, shape2)
    p1 = get_point(p1)
    p2 = get_point(p2)
    xdist = abs(p2[0] - p1[0])
    ydist = abs(p2[1] - p1[1])
    zdist = abs(p2[2] - p1[2])
    return {
        "distance": dist,
        "⇒ X | Y | Z": [xdist, ydist, zdist],
        "point 1": p1,
        "point 2": p2,
        "info": "center" if center else "min",
        "refpoint1": p1,
        "refpoint2": p2,
    }


def _edge_tangent_at(edge, extrema, shape_index):
    """Get tangent direction on an edge at an extrema solution point."""
    if shape_index == 1:
        support_type = extrema.SupportTypeShape1(1)
    else:
        support_type = extrema.SupportTypeShape2(1)

    curve = BRepAdaptor_Curve(edge)

    if support_type == BRepExtrema_SupportType.BRepExtrema_IsOnEdge:
        if shape_index == 1:
            param = extrema.ParOnEdgeS1(1)[0]
        else:
            param = extrema.ParOnEdgeS2(1)[0]
    elif support_type == BRepExtrema_SupportType.BRepExtrema_IsVertex:
        # Determine closest endpoint
        if shape_index == 1:
            pt = extrema.PointOnShape1(1)
        else:
            pt = extrema.PointOnShape2(1)
        d_first = pt.Distance(curve.Value(curve.FirstParameter()))
        d_last = pt.Distance(curve.Value(curve.LastParameter()))
        param = curve.FirstParameter() if d_first <= d_last else curve.LastParameter()
    else:
        return None, None

    pnt = gp_Pnt()
    vec = gp_Vec()
    curve.D1(param, pnt, vec)
    if vec.Magnitude() < 1e-10:
        return None, None
    if get_geom_type(edge) == "Line":
        label = "line"
    else:
        label = f"tangent at P{shape_index}"
    return gp_Dir(vec), label


def _face_normal_at(face, extrema, shape_index):
    """Get surface normal on a face at an extrema solution point."""
    if shape_index == 1:
        support_type = extrema.SupportTypeShape1(1)
    else:
        support_type = extrema.SupportTypeShape2(1)

    if support_type == BRepExtrema_SupportType.BRepExtrema_IsInFace:
        if shape_index == 1:
            uv = extrema.ParOnFaceS1(1)
        else:
            uv = extrema.ParOnFaceS2(1)
        u, v = uv[0], uv[1]
    else:
        # Project the closest point onto the surface to get UV
        if shape_index == 1:
            pt = extrema.PointOnShape1(1)
        else:
            pt = extrema.PointOnShape2(1)
        surface = BRep_Tool.Surface_s(face)
        proj = GeomAPI_ProjectPointOnSurf(pt, surface)
        if proj.NbPoints() == 0:
            return None, None
        u, v = proj.Parameters(1)

    pnt = gp_Pnt()
    normal = gp_Vec()
    BRepGProp_Face(face).Normal(u, v, pnt, normal)
    if normal.Magnitude() < 1e-10:
        return None, None
    if get_geom_type(face) == "Plane":
        label = "face normal"
    else:
        label = f"surface normal at P{shape_index}"
    return gp_Dir(normal), label


def calc_angle(shape1, shape2):
    shape1 = downcast(shape1)
    shape2 = downcast(shape2)

    is_edge1 = is_topods_edge(shape1)
    is_face1 = is_topods_face(shape1)
    is_edge2 = is_topods_edge(shape2)
    is_face2 = is_topods_face(shape2)

    if not (is_edge1 or is_face1) or not (is_edge2 or is_face2):
        return None

    extrema = BRepExtrema_DistShapeShape(shape1, shape2)
    if not extrema.IsDone() or extrema.NbSolution() == 0:
        return None

    if is_edge1:
        dir1, info1 = _edge_tangent_at(shape1, extrema, 1)
    else:
        dir1, info1 = _face_normal_at(shape1, extrema, 1)

    if is_edge2:
        dir2, info2 = _edge_tangent_at(shape2, extrema, 2)
    else:
        dir2, info2 = _face_normal_at(shape2, extrema, 2)

    if dir1 is None or dir2 is None:
        return None

    angle = dir1.Angle(dir2) / pi * 180

    # If exactly one shape is an edge (tangent vs normal), convert to
    # edge-to-surface angle
    if is_edge1 != is_edge2:
        angle = abs(90 - angle)

    def _dir_tuple(d):
        return (d.X(), d.Y(), d.Z())

    response = {"angle": angle}

    response["reference 1"] = info1
    if is_edge1:
        response["direction 1"] = _dir_tuple(dir1)
    else:
        response["normal 1"] = _dir_tuple(dir1)

    response["reference 2"] = info2
    if is_edge2:
        response["direction 2"] = _dir_tuple(dir2)
    else:
        response["normal 2"] = _dir_tuple(dir2)

    return response


def get_distance(shape1, shape2, center):
    dist = calc_distance(shape1, shape2, center)

    result = [
        {
            "distance": dist["distance"],
            "⇒ X | Y | Z": dist["⇒ X | Y | Z"],
            "info": dist["info"],
        },
        {
            "point 1": dist["point 1"],
            "point 2": dist["point 2"],
        },
    ]

    angle = calc_angle(shape1, shape2)

    if angle is not None:
        angle_section = {"angle": angle["angle"]}
        angle_section["reference 1"] = angle["reference 1"]
        if "direction 1" in angle:
            angle_section["direction 1"] = angle["direction 1"]
        if "normal 1" in angle:
            angle_section["normal 1"] = angle["normal 1"]
        angle_section["reference 2"] = angle["reference 2"]
        if "direction 2" in angle:
            angle_section["direction 2"] = angle["direction 2"]
        if "normal 2" in angle:
            angle_section["normal 2"] = angle["normal 2"]
        result.append(angle_section)

    return {
        "result": result,
        "refpoint1": dist["refpoint1"],
        "refpoint2": dist["refpoint2"],
    }
