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
