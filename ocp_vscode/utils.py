"""Utility functions for ocp_vscode"""

#
# Copyright 2025 Bernhard Walter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
import warnings

from ocp_tessellate import OcpGroup

__all__ = [
    "ignore_camera_warnings",
    "camera_keep_warning",
]

# Warnings


class CommsWarning(UserWarning):
    """Warning for communication issues."""

    pass


class CameraWarning(UserWarning):
    """Warning for potential camera visibility issues."""

    pass


class CameraKeepWarning(UserWarning):
    """Warning that reset camera is set to KEEP."""

    pass


# Manual "once" handling below (needed for multi-client jupyter kernels)
warnings.simplefilter("always", CommsWarning)
warnings.simplefilter("always", CameraWarning)
warnings.simplefilter("always", CameraKeepWarning)

_COMMS_WARNING_SHOWN = False
_CAMERA_KEEP_WARNING_SHOWN = False


def _warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return "%s: %s\n" % (category.__name__, message)


def comms_warning(message):
    """Issue a communication warning (only once per session)"""
    global _COMMS_WARNING_SHOWN
    if not _COMMS_WARNING_SHOWN:
        warnings.formatwarning = _warning_on_one_line
        warnings.warn(message, CommsWarning, stacklevel=2)
        _COMMS_WARNING_SHOWN = True


def camera_warning(message):
    """Issue a camera warning"""
    warnings.formatwarning = _warning_on_one_line
    warnings.warn(message, CameraWarning, stacklevel=2)


def camera_keep_warning(message):
    """Issue a reset camera set to KEEP warning (only once per session)"""
    global _CAMERA_KEEP_WARNING_SHOWN
    if not _CAMERA_KEEP_WARNING_SHOWN:
        warnings.formatwarning = _warning_on_one_line
        warnings.warn(message, CameraKeepWarning, stacklevel=2)
        _CAMERA_KEEP_WARNING_SHOWN = True


def ignore_camera_warnings():
    """Suppress all camera visibility warnings."""
    warnings.filterwarnings("ignore", category=CameraWarning)
    warnings.filterwarnings("ignore", category=CameraKeepWarning)


# Last bounding box check

LAST_BBOX_SIZE = None


def get_last_bbox_size():
    return LAST_BBOX_SIZE


def set_last_bbox_size(bbox):
    global LAST_BBOX_SIZE
    LAST_BBOX_SIZE = bbox


def check_camera_warnings(new_bb):
    """Check if new bounding box may cause visibility issues with fixed camera."""

    old_bb = get_last_bbox_size()
    if old_bb is None:
        return

    # Diagonal comparison
    old_diag = math.hypot(
        old_bb["xmax"] - old_bb["xmin"],
        old_bb["ymax"] - old_bb["ymin"],
        old_bb["zmax"] - old_bb["zmin"],
    )
    new_diag = math.hypot(
        new_bb["xmax"] - new_bb["xmin"],
        new_bb["ymax"] - new_bb["ymin"],
        new_bb["zmax"] - new_bb["zmin"],
    )
    if old_diag > 0:
        ratio = new_diag / old_diag
        if ratio < 0.01:
            camera_warning(
                "Object may be too small to see (%.1f%% of previous size). Skip warnings with `ignore_camera_warnings()`"
                % (ratio * 100)
            )
        elif ratio > 1.5:
            camera_warning(
                "Object may extend beyond view (%.1f%% of previous size). Skip warnings with `ignore_camera_warnings()`"
                % (ratio * 100)
            )
    # Overlap check
    overlap = (
        max(old_bb["xmin"], new_bb["xmin"]) < min(old_bb["xmax"], new_bb["xmax"])
        and max(old_bb["ymin"], new_bb["ymin"]) < min(old_bb["ymax"], new_bb["ymax"])
        and max(old_bb["zmin"], new_bb["zmin"]) < min(old_bb["zmax"], new_bb["zmax"])
    )
    if not overlap:
        camera_warning(
            "Object may be outside visible area (no overlap with previous view). Skip warnings with `ignore_camera_warnings()`"
        )


# Save last paths for Animation

LAST_PATHS = []


def set_last_paths(node):
    """Extract all paths from nested OcpGroup/OcpObject structure."""
    global LAST_PATHS

    def collect_paths(node, path):
        results = []
        current_path = f"{path}/{node.name}"

        if isinstance(node, OcpGroup):
            results.append(current_path)
            for obj in node.objects:
                results.extend(collect_paths(obj, current_path))
        else:  # OcpObject
            results.append(current_path)

        return results

    LAST_PATHS = collect_paths(node, "")


def get_last_paths():
    return LAST_PATHS


# To avoid to import from github (pymat)
def is_pymat(material):
    return (
        hasattr(material, "__module__")
        and material.__module__ == "pymat.core"
        and material.__class__.__name__ == "Material"
    )


def create_shader_ball(name="shader_ball"):
    """Requires build123d"""
    from build123d import (
        Align,
        Pos,
        Rot,
        CenterArc,
        SlotArc,
        Triangle,
        Cone,
        Cylinder,
        Sphere,
        Compound,
        extrude,
        fillet,
    )

    ccm = (Align.CENTER, Align.CENTER, Align.MIN)
    cM = (Align.CENTER, Align.MAX)

    r1 = 10
    r2 = 8.5
    r3 = 8
    h = 2
    s1 = Sphere(r1)
    s2 = Sphere(r2)
    s3 = Sphere(r3)
    s = Rot(0, 60, 0) * (s1 - s2 - Pos(0, 0, 14.3) * s3 - Pos(0, 0, -14.3) * s3)

    d = -r1 + 0.0

    c1 = Pos(0, 0, d - h) * Cylinder(7, h, align=ccm)
    c2 = Pos(0, 0, d - 0.1) * Cylinder(6, h, align=ccm)
    c3 = Pos(0, 0, d - 0.2) * Cylinder(5, h, align=ccm)
    c1 = fillet(c1.edges(), 0.2)
    c = c1 - c2 - c3

    b1 = Pos(0, 0, d - h) * (Cylinder(11, 2, align=ccm) - Cylinder(7.4, 2, align=ccm))

    sl1 = Pos(0, 0, d) * SlotArc(CenterArc((0, 0, 0), 10.0, 270 - 35, 70), 0.4)
    sl2 = Pos(0, 0, d) * SlotArc(CenterArc((0, 0, 0), 8.0, 270 - 25, 50), 0.4)
    sl3 = Pos(0, 0, d + 1e-2) * SlotArc(CenterArc((0, 0, 0), 9.0, 270 - 15, 30), 0.4)

    a1 = extrude(sl1, 0.2)
    a1 = fillet(a1.edges().group_by()[-1], 0.05)
    a2 = extrude(sl2, 0.2)
    a2 = fillet(a2.edges().group_by()[-1], 0.05)
    a3 = extrude(sl3, -0.2)
    a3 = fillet(a3.edges().group_by()[0], 0.05)

    b1 = b1 - a3 + a1 + a2

    t = Pos(0, 0, d) * Triangle(a=6, b=12, c=12, align=cM)
    h = 4
    n = 5

    def mask(r):
        return Pos(0, 0, -r1) * Cylinder(r, 20, align=ccm)

    # m = mask(10)

    b2 = Rot(0, 0, 180) * extrude(t, h)
    cn = Pos(0, 0, -r1 + 2.8) * Cone(7, 15, 4, align=ccm)
    b = b1 + (b2 & mask(10) - cn)

    for i in range(1, n):
        for sign in [-1, 1]:
            b += (
                Rot(0, 0, 180 + sign * i * 28.6) * extrude(t, h - 1.5 - i * h / n / 2)
            ) & mask(10 - i * 0.4)

    b -= Cylinder(7.4, 20)
    b &= Cylinder(11, 50)
    b = b.solid()

    b = fillet(b.edges(), 0.1)

    s4 = Rot(0, 0, 90) * Sphere(r2 - 1)

    # %%

    compound = Compound([b, s, c, s4])
    compound.label = name
    return compound
