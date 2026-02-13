"""Animation class for the viewer"""

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
#

import json
import time
import tempfile
from PIL import Image
import numpy as np

from ocp_tessellate.utils import numpy_to_json
from .comms import send_data, send_command
from .show import save_screenshot
from .utils import get_last_paths


class Animation:
    """Class to create animations for the viewer"""

    def __init__(self, assembly=None):
        if assembly is not None:
            print("Deprecation: The parameter `assembly` is not needed any more\n")

        self.tracks = []
        self.paths = get_last_paths()

        print(
            "Note: The paths for animation are only valid for the specific `show` statement"
            "\n(so do not change the objects between `show` and creating the Animation)."
            "\nAvailable paths:"
        )
        for p in self.paths:
            print(f"- {p}")

        self.max_duration = 0

    def add_track(self, path, action, times, values, animate_joints=False):
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

        if path not in self.paths:
            raise ValueError(f"Path '{path}' does not exist in assembly")

        self.tracks.append((path, action, times, values))

        if times[-1] > self.max_duration:
            self.max_duration = float(times[-1])

        if animate_joints:
            self.tracks.append((f"{path}.joints", action, times, values))

    def animate(self, speed):
        """Animate the tracks"""
        if self.max_duration == 0:
            raise RuntimeError("Use add_tracks to add animation tracks")

        data = {"data": self.tracks, "type": "animation", "config": {"speed": speed}}
        send_data(json.loads(numpy_to_json(data)))

    def set_relative_time(self, fraction, port=None):
        """
        Set the animation playback position.

        Parameters
        ----------
        fraction : float
            A value between 0 and 1 representing the relative position
            in the animation timeline (0 = start, 1 = end).
        port : int, optional
            The port to send the command to (default=None).
        """
        send_command({"type": "set_relative_time", "value": float(fraction)}, port=port)

    def save_as_gif(
        self,
        output,
        fps=25,
        loops=0,
        endpoint=False,
        bg_color="white",
        pause=0.02,
    ):
        """
        Save the animation as a GIF file.

        Parameters
        ----------
        output : str
            The output file path for the GIF.
        fps : int, default=25
            Frames per second. GIF format stores frame delays in centiseconds
            (1/100s), so only certain fps values produce exact timing:

            - 10 fps → 100 ms/frame (exact)
            - 20 fps → 50 ms/frame (exact)
            - 25 fps → 40 ms/frame (exact)
            - 50 fps → 20 ms/frame (exact)
            - 100 fps → 10 ms/frame (exact)

            Other values like 30 fps (33.33 ms) or 60 fps (16.67 ms) will be
            rounded, causing the GIF to play faster or slower than expected.
        loops : int, default=0
            Number of times to loop the animation:

            - 0 = loop infinitely
            - N = play N times

            Note: Some viewers might ignore the loop settings for GIFs.
            Typically, web browsers respect the loop count.
        endpoint : bool, default=False
            Whether to include the final frame at t=1.0.
        bg_color : str, default="white"
            Background color for transparent areas.
        pause : float, default=0.02
            Delay in seconds between capturing frames (for rendering stability).
        """
        if fps not in [10, 20, 25, 50, 100]:
            print(
                "For exact duration in gif (using 1/100s), use fps 10, 20, 25, 50, or 100"
            )

        if loops == 0:
            loop = 0
        elif loops == 1:
            loop = None
        elif isinstance(loops, int) and loops > 1:
            loop = loops - 1
        else:
            raise ValueError(f"{loop} is not a positive interger or 0")

        n_frames = int(self.max_duration * fps)
        frame_duration = round(1000 / fps)

        print(n_frames, frame_duration)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            filename = tmp.name
            frames = []
            for i, t in enumerate(np.linspace(0, 1000, n_frames, endpoint=endpoint)):
                self.set_relative_time(t / 1000)
                time.sleep(pause)
                save_screenshot(filename, progress_only=True)
                img = Image.open(filename)
                # Convert RGBA to RGB with white background to avoid transparency issues
                if img.mode == "RGBA":
                    background = Image.new("RGB", img.size, bg_color)
                    background.paste(
                        img, mask=img.split()[3]
                    )  # Use alpha channel as mask
                    img = background
                else:
                    img = img.convert("RGB")
                frames.append(img)
                if i % 20 == 0:
                    print(f"{100 * i / n_frames:3.0f}%", end=" ")
            print()

            print("Saving animation ...")

            frames[0].save(
                output,
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration,
                loop=loop,
            )
        print(f"Animation saved as {output}")
