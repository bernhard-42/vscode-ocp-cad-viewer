"""Utility functions for ocp_vscode"""

# ruff: noqa: F401
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

import warnings

from ocp_viewer_core.utils import (
    CameraKeepWarning,
    CameraWarning,
    camera_keep_warning,
    camera_warning,
    create_shader_ball,
    ignore_camera_warnings,
)

# The released 4.0.x surface of this module: the two camera-warning names in
# __all__, the rest importable. All of it lives in `ocp_viewer_core.utils` now
# - including the shader ball, whose build123d import happens at the call, so
# importing this package still never asks for build123d.
__all__ = [
    "camera_keep_warning",
    "ignore_camera_warnings",
]

# Warnings


class CommsWarning(UserWarning):
    """Warning for communication issues."""

    pass


_COMMS_WARNING_SHOWN = False


def _warning_on_one_line(message, category, filename, lineno, line=None):
    # `formatwarning` takes (message, category, filename, lineno, line). A
    # `file` parameter here would belong to `showwarning` instead, and would
    # capture what the caller meant as `line`.
    return "%s: %s\n" % (category.__name__, message)


def comms_warning(message):
    """Issue a communication warning (only once per session)"""
    global _COMMS_WARNING_SHOWN  # pylint: disable=global-statement
    if not _COMMS_WARNING_SHOWN:
        warnings.formatwarning = _warning_on_one_line
        warnings.warn(message, CommsWarning, stacklevel=2)
        _COMMS_WARNING_SHOWN = True


