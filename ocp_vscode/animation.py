"""Animation class for the viewer"""

#
# Copyright 2023 Bernhard Walter
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
#

import json

from ocp_tessellate.utils import numpy_to_json
from .comms import send_data


def collect_paths(assembly, path=""):
    """Collect all paths in the assembly tree"""
    result = []
    new_path = f"{path}/{assembly.label}"
    result.append(new_path)
    for child in assembly.children:
        result.extend(collect_paths(child, new_path))
    return result


class Animation:
    """Class to create animations for the viewer"""

    def __init__(self, assembly):
        self.tracks = []
        self.is_cadquery = hasattr(assembly, "mates") and not hasattr(
            assembly, "fq_name"
        )
        self.is_build123d = hasattr(assembly, "joints")
        if self.is_cadquery:
            self.paths = list(assembly.objects.keys())
        else:
            self.paths = collect_paths(assembly)

    def add_track(self, path, action, times, values):
        # pylint: disable=line-too-long
        """
        Adding a three.js animation track.

        Parameters
        ----------
        path : string
            The path (or id) of the cad object for which this track is meant.
            Usually of the form `/top-level/level2/...`
        action : {"t", "tx", "ty", "tz", "q", "rx", "ry", "rz"}
            The action type:

            - "tx", "ty", "tz" for translations along the x, y or z-axis
            - "t" to add a position vector (3-dim array) to the current position of the CAD object
            - "rx", "ry", "rz" for rotations around x, y or z-axis
            - "q" to apply a quaternion to the location of the CAD object
        times : list of float or int
            An array of floats describing the points in time where CAD object (with id `path`) should be at the location
            defined by `action` and `values`
        values : list of float or int
            An array of same length as `times` defining the locations where the CAD objects should be according to the
            `action` provided. Formats:

            - "tx", "ty", "tz": float distance to move
            - "t": 3-dim tuples or lists defining the positions to move to
            - "rx", "ry", "rz": float angle in degrees
            - "q" quaternions of the form (x,y,z,w) the represent the rotation to be applied

        Examples
        --------
        ```
        AnimationTrack(
            '/bottom/left_middle/lower',                                # path
            'rz',                                                       # action
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],              # times (seconds)
            [-15.0, -15.0, -15.0, 9.7, 20.0, 9.7, -15.0, -15.0, -15.0]  # angles
        )

        AnimationTrack(
            'base/link_4_6',                                            # path
            't',                                                        # action
            [0.0, 1.0, 2.0, 3.0, 4.0],                                  # times (seconds)
            [[0.0, 0.0, 0.0], [0.0, 1.9509, 3.9049],
            [0.0 , -3.2974, -16.7545], [0.0 , 0.05894 , -32.0217],
            [0.0 , -3.2212, -13.3424]]                                 # 3-dim positions
        )
        ```

        See also
        --------

        - [three.js NumberKeyframeTrack](https://threejs.org/docs/index.html?q=track#api/en/animation/tracks/NumberKeyframeTrack)
        - [three.js QuaternionKeyframeTrack](https://threejs.org/docs/index.html?q=track#api/en/animation/tracks/QuaternionKeyframeTrack)

        """

        # if path[0] != "/":
        #     path = f"/{path}"

        if len(times) != len(values):
            raise ValueError("Parameters 'times' and 'values' need to have same length")

        if self.is_cadquery:
            root, _, cq_path = path.strip("/").partition("/")

            if root not in self.paths or cq_path not in self.paths + [""]:
                raise ValueError(f"Path '{path}' does not exist in assembly")

        elif self.is_build123d:
            ...
            # if path not in self.paths:
            #     raise ValueError(f"Path '{path}' does not exist in assembly")

        self.tracks.append((path, action, times, values))

    def animate(self, speed):
        """Animate the tracks"""
        data = {"data": self.tracks, "type": "animation", "config": {"speed": speed}}
        send_data(json.loads(numpy_to_json(data)))
