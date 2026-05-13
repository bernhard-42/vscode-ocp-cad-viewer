# Animation

The `Animation` class drives three.js animation tracks on the objects you previously sent to the viewer with `show`.

```python
from ocp_vscode import show, Animation
```

## Workflow

1. `show(...)` the assembly you want to animate.
2. Construct `Animation()` — this reads the paths of all objects from the last `show` call. It prints the available paths so you know what's addressable.
3. Add one or more tracks via `add_track(path, action, times, values)`.
4. Call `animate(speed)` to play the animation in the viewer.

Animation paths are only valid for the most recent `show` call. Don't change the objects between `show` and constructing the `Animation`.

## `add_track(path, action, times, values, animate_joints=False)`

Adds a three.js keyframe track for one CAD object.

| Parameter        | Description                                                                                                                                                                         |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`           | Path of the CAD object, usually `/top-level/level2/...` — must match one of the paths printed when `Animation` was constructed                                                      |
| `action`         | One of `"tx"`, `"ty"`, `"tz"` (translation along an axis), `"t"` (translation vector), `"rx"`, `"ry"`, `"rz"` (rotation around an axis, degrees), `"q"` (quaternion `(x, y, z, w)`) |
| `times`          | List of floats — points in time (seconds) where the object should be at the given location                                                                                          |
| `values`         | Same length as `times`. Floats for `"tx" / "ty" / "tz" / "rx" / "ry" / "rz"`; 3-tuples for `"t"`; 4-tuples for `"q"`                                                                |
| `animate_joints` | If `True`, also adds a parallel track on `<path>.joints` so attached build123d joints animate with the object                                                                       |

Raises `ValueError` if `times` and `values` differ in length, or if `path` is not in the registered paths.

### Examples

Rotate around z by varying angles:

```python
animation.add_track(
    '/bottom/left_middle/lower',
    'rz',
    [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
    [-15.0, -15.0, -15.0, 9.7, 20.0, 9.7, -15.0, -15.0, -15.0],
)
```

Translate along a 3-D path:

```python
animation.add_track(
    'base/link_4_6',
    't',
    [0.0, 1.0, 2.0, 3.0, 4.0],
    [
        [0.0, 0.0, 0.0],
        [0.0, 1.9509, 3.9049],
        [0.0, -3.2974, -16.7545],
        [0.0, 0.05894, -32.0217],
        [0.0, -3.2212, -13.3424],
    ],
)
```

See also: [three.js NumberKeyframeTrack](https://threejs.org/docs/index.html?q=track#api/en/animation/tracks/NumberKeyframeTrack), [three.js QuaternionKeyframeTrack](https://threejs.org/docs/index.html?q=track#api/en/animation/tracks/QuaternionKeyframeTrack).

## Animate

`animate(speed)`

Plays the registered tracks in the viewer. `speed` is the playback multiplier (`1.0` = real-time). Raises `RuntimeError` if no tracks have been added.

## Set relative time

`set_relative_time(fraction, port=None)`

Jump the animation timeline to a fractional position between `0` (start) and `1` (end). Useful for scrubbing or for rendering specific frames.

## Save as gif

`save_as_gif(output, fps=25, loops=0, endpoint=False, bg_color="white", pause=0.02)`

Renders the animation to a GIF by stepping `set_relative_time` and capturing screenshots.

| Parameter  | Default    | Description                                                                                                    |
| ---------- | ---------- | -------------------------------------------------------------------------------------------------------------- |
| `output`   | _required_ | Output file path                                                                                               |
| `fps`      | `25`       | Frames per second. GIF stores delays in centiseconds, so only `10`, `20`, `25`, `50`, `100` yield exact timing |
| `loops`    | `0`        | `0` = infinite, `N` = play `N` times                                                                           |
| `endpoint` | `False`    | Include the final frame at `t=1.0`                                                                             |
| `bg_color` | `"white"`  | Background color for transparent areas                                                                         |
| `pause`    | `0.02`     | Seconds to wait between frame captures (gives the renderer time to settle)                                     |
