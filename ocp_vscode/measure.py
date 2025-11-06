from math import pi

from ocp_tessellate.ocp_utils import (
    area,
    axis_to_line,
    BoundingBox,
    center_of_geometry,
    center_of_mass,
    downcast,
    dist_shapes,
    get_curve,
    get_plane,
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
    tangent_edge_at,
    rect,
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

    response = {
        "shape_type": shape_type,
        "geom_type": geom_type,
    }

    if shape_type == "Vertex":
        response["XYZ"] = get_point(shape)
        response["refpoint"] = get_point(shape)

    elif shape_type == "Edge":
        shape = downcast(shape)
        if geom_type == "Line":
            response["Start"] = get_point(position_at(shape, 0))
            response["Middle"] = get_point(position_at(shape, 0.5))
            response["End"] = get_point(position_at(shape, 1))
            response["refpoint"] = get_point(position_at(shape, 0.5))

        elif geom_type == "Circle":
            circle = get_curve(shape).Circle()
            response["Center"] = get_point(circle.Location())
            response["Radius"] = circle.Radius()
            response["Start"] = get_point(position_at(shape, 0))
            if not is_closed(shape):
                # response["geom_type"] += " (Arc)"
                response["End"] = get_point(position_at(shape, 1))
                response["refpoint"] = get_point(position_at(shape, 0.5))
            else:
                response["refpoint"] = get_point(position_at(shape, 0))

        elif geom_type == "Ellipse":
            ellipse = get_curve(shape).Ellipse()
            response["Center"] = get_point(ellipse.Location())
            response["Major radius"] = ellipse.MajorRadius()
            response["Minor radius"] = ellipse.MinorRadius()
            # response["focus1"] = get_point(ellipse.Focus1())
            # response["focus2"] = get_point(ellipse.Focus2())
            response["Start"] = get_point(position_at(shape, 0))
            if not is_closed(shape):
                # response["geom_type"] += " (Arc)"
                response["End"] = get_point(position_at(shape, 1))
                response["refpoint"] = get_point(position_at(shape, 0.5))
            else:
                response["refpoint"] = get_point(position_at(shape, 0))

        elif geom_type == "Hyperbola":
            hyperbola = get_curve(shape).Hyperbola()
            response["Start"] = get_point(position_at(shape, 0))
            response["Vertex"] = get_point(hyperbola.Location())
            response["End"] = get_point(position_at(shape, 1))
            # response["focus1"] = get_point(hyperbola.Focus1())
            # response["focus2"] = get_point(hyperbola.Focus2())
            response["refpoint"] = get_point(position_at(shape, 0.5))

        elif geom_type == "Parabola":
            parabola = get_curve(shape).Parabola()
            response["Start"] = get_point(position_at(shape, 0))
            response["Vertex"] = get_point(parabola.Location())
            response["End"] = get_point(position_at(shape, 1))
            # response["focus"] = get_point(parabola.Focus())
            response["refpoint"] = get_point(position_at(shape, 0.5))

        elif geom_type in ["Bezier", "Bspline"]:
            response["Start"] = get_point(position_at(shape, 0))
            response["Middle"] = get_point(position_at(shape, 0.5))
            response["End"] = get_point(position_at(shape, 1))
            response["refpoint"] = get_point(position_at(shape, 0.5))

        elif geom_type == "OffsetCurve":
            offset = get_curve(shape).OffsetCurve()
            response["Offset"] = offset.Offset()
            response["Start"] = get_point(position_at(shape, 0))
            if is_closed(shape):
                response["End"] = get_point(position_at(shape, 1))
            response["refpoint"] = get_point(position_at(shape, 0))

        else:
            response["Start"] = get_point(position_at(shape, 0))
            response["Middle"] = get_point(position_at(shape, 0.5))
            response["End"] = get_point(position_at(shape, 1))
            response["refpoint"] = get_point(position_at(shape, 0.5))

        response["Length"] = length(shape)

        for i in [0, 1]:
            try:
                angle = calc_angle(rect(1, 1), tangent_edge_at(shape, i))
                if angle is not None:
                    response[f"Angle@{i} to XY"] = angle["angle"]
            except Exception:
                pass

    elif shape_type == "Face":
        shape = downcast(shape)
        if geom_type == "Plane":
            plane = get_surface(shape).Plane()
            response["Center"] = get_point(plane.Location())

        elif geom_type == "Cylinder":
            cylinder = get_surface(shape).Cylinder()
            response["Center"] = get_point(cylinder.Location())
            response["Radius"] = cylinder.Radius()

        elif geom_type == "Cone":
            cone = get_surface(shape).Cone()
            response["Center"] = get_point(cone.Location())
            response["Base radius"] = cone.RefRadius()
            response["Half angle"] = cone.SemiAngle() / pi * 180

        elif geom_type == "Sphere":
            sphere = get_surface(shape).Sphere()
            response["Center"] = get_point(sphere.Location())
            response["Radius"] = sphere.Radius()

        elif geom_type == "Torus":
            torus = get_surface(shape).Torus()
            response["Center"] = get_point(torus.Location())
            response["Minor radius"] = torus.MinorRadius()
            response["Major radius"] = torus.MajorRadius()
            response["refpoint"] = get_point(torus.Location())

        elif geom_type == "Bezier":
            ...

        elif geom_type == "Bspline":
            ...

        elif geom_type == "SurfaceOfRevolution":
            revolution = get_surface(shape)
            response["Axe loc"] = get_point(revolution.AxeOfRevolution().Location())
            response["Axe dir"] = get_point(revolution.AxeOfRevolution().Direction())
            response["geom_type"] = "Revolution"

        response["Area"] = area(shape)
        response["refpoint"] = center_of_geometry(shape)

        try:
            angle = calc_angle(rect(1, 1), shape)
            if angle is not None:
                response["Angle to XY"] = angle["angle"]
        except Exception:
            pass

    elif shape_type in ["Solid", "CompSolid", "Compound"]:
        shape = downcast(shape)
        response["Volume"] = volume(shape)
        response["refpoint"] = center_of_mass(shape)

    else:
        print(f"unknown shape {type(shape)}")

    if shape_type != "Vertex":
        bb = BoundingBox(shape, optimal=True)
        response["bb"] = {
            "min": [bb.xmin, bb.ymin, bb.zmin],
            "center": bb.center,
            "max": [bb.xmax, bb.ymax, bb.zmax],
            "size": [bb.xsize, bb.ysize, bb.zsize],
        }

    return response


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
        "Point 1": p1,
        "Point 2": p2,
        "info": "center" if center else "min",
        "refpoint1": p1,
        "refpoint2": p2,
    }


def calc_angle(shape1, shape2):
    shape1 = downcast(shape1)
    shape2 = downcast(shape2)

    shape_type1 = get_shape_type(shape1)
    shape_type2 = get_shape_type(shape2)
    geom_type1 = get_geom_type(shape1)
    geom_type2 = get_geom_type(shape2)

    def angle_line_line(line1, line2):
        if is_topods_edge(line1):
            l1 = get_curve(line1).Line()
        else:
            l1 = line1
        if is_topods_edge(line2):
            l2 = get_curve(line2).Line()
        else:
            l2 = line2
        return l1.Angle(l2) / pi * 180

    def angle_line_plane(line, plane):
        # 90 - angle between line and normal
        axis = plane.Axis()
        line2 = axis_to_line(axis)
        return 90 - angle_line_line(line, line2)

    def angle_plane_plane(plane1, plane2):
        # angle between the two normals
        axis1 = plane1.Axis()
        line1 = axis_to_line(axis1)
        axis2 = plane2.Axis()
        line2 = axis_to_line(axis2)
        return angle_line_line(line1, line2)

    angle = None
    info1 = ""
    info2 = ""

    if geom_type1 == "Line" and geom_type2 == "Line":
        angle = angle_line_line(shape1, shape2)
        info1 = "Line"
        info2 = "Line"

    elif geom_type1 == "Line" and shape_type2 in ["Edge", "Face"]:
        plane2 = get_plane(shape2)
        if plane2 is not None:
            angle = angle_line_plane(shape1, plane2)
            info1 = "Line"
            if shape_type2 == "Edge":
                info2 = f"Plane({shape_type2})"
            else:
                info2 = f"{shape_type2}"

    elif shape_type1 in ["Edge", "Face"] and geom_type2 == "Line":
        plane1 = get_plane(shape1)
        if plane1 is not None:
            angle = angle_line_plane(shape2, plane1)
            if shape_type1 == "Edge":
                info1 = f"Plane({shape_type1})"
            else:
                info1 = f"{shape_type1}"
            info2 = "Line"

    elif shape_type1 in ["Edge", "Face"] and shape_type2 in ["Edge", "Face"]:
        plane1 = get_plane(shape1)
        plane2 = get_plane(shape2)
        if plane1 is not None and plane2 is not None:
            angle = angle_plane_plane(plane1, plane2)
            if shape_type1 == "Edge":
                info1 = f"Plane({shape_type1})"
            else:
                info1 = f"{shape_type1}"
            if shape_type2 == "Edge":
                info2 = f"Plane({shape_type2})"
            else:
                info2 = f"{shape_type2}"

    if angle is None:
        return None
    else:
        return {
            "angle": angle,
            "info1": info1,
            "info2": info2,
        }


def get_distance(shape1, shape2, center):
    response = calc_distance(shape1, shape2, center)

    angle = calc_angle(shape1, shape2)

    if angle is not None:
        response["angle"] = angle["angle"]
        response["info1"] = angle["info1"]
        response["info2"] = angle["info2"]

    return response
