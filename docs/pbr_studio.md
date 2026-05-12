## Material setup

PBR (Physically Based Rendering) materials can be defined using the class `PbrProperties` from [threejs-materials](https://github.com/bernhard-42/threejs-materials) (`[uv] pip install threejs-materials`)

There are two sources of materials:

1. **MaterialX providers.** Supported web pages:
    - https://ambientcg.com/list?type=material
    - https://matlib.gpuopen.com/main/materials/all
    - https://polyhaven.com/textures
    - https://physicallybased.info/

    **Installation:** `pip install ocp-vscode[materialx]`

    **Usage:** The class `PbrProperties` allows to convert (typically called "bake") downloaded MaterialX material into a local cache in a format suitable for three-cad-viewer (threejs) and glTF. If the material comes with a texture, one can override PBR parameters, and scale and rotate textures:

    ```python
    from threejs_materials import PbrProperties

    # Use a GPUOpen material
    alu_hex = PbrProperties.from_gpuopen("Aluminum Hexagon")

    # Use a GPUOpen material and override the glass behavior
    glass = PbrProperties.from_gpuopen("Glass").override(transmission=0.98, thickness=0.8)

    # Use an AmbientCG material, and scale the texture to 2 in u and v direction
    metal = PbrProperties.from_ambientcg("Metal 049 C").scale(2, 2)

    # Use a PhysicallyBased material and override color for two material instances
    light = PbrProperties.from_physicallybased("Plastic (Acrylic)")
    red_light = light.override(color=(1, 0, 0))
    yellow_light = light.override(color="yellow")

    ```

    **Note** Python support of `materialx`:

    | Operating system                                                      | Python < 3.14                     | Python 3.14                                                       |
    | --------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------------------------- |
    | Linux, MacOS, Windows (with Microsoft Visual C++ toolchain installed) | `pip` installs binaries from pypi | pip installs sources from pypi and compiles the packages directly |
    | Windows (no compiler)                                                 | `pip` installs binaries from pypi | not directly supported\*                                          |

    \* Use e.g. Python 3.13 and only run `PbrProperties.from_gpuopen("Aluminum Hexagon")` which will cache the material locally. Afterwards the same command under Python 3.14 directly reads from cache and does not need `materialx` and `openexr`.

2. **GLTF2 containing materials** (e.g. exported from Blender)

    **Installation:** `pip install ocp_vscode`

    **Usage:**

    ```python
    from threejs_materials import PbrProperties

    # load all materials in the glTF/glb file as a dict
    materials = PbrProperties.load_gltf(here / "brass-deco" / "brass_cube.gltf")
    # use one of them
    brass = materials["Ornamental Design Embossed Brass"]
    ```

## The object

Let's create a little object to apply the materials later (here with [build123d](https://github.com/gumyr/build123d) algebra mode)

```python
from build123d import *
from ocp_vscode import *

mcc = (Align.MIN, Align.CENTER, Align.CENTER)
ccm = (Align.CENTER, Align.CENTER, Align.MIN)
ccM = (Align.CENTER, Align.CENTER, Align.MAX)

e = Ellipse(10, 3)
e2 = offset(e, -0.2)
e -= e2
e -= Rectangle(12, 6, align=mcc)

e3 = offset(e2, -0.1)
e2 -= e3
e2 -= Rectangle(12, 6, align=mcc)

body = Rot(90, 0, 0) * revolve(e, Axis.Y)
inner = Rot(90, 0, 0) * revolve(e2, Axis.Y)
mask = Cylinder(4, 3, align=ccm)
body = body - mask
inner = inner - mask

window = Pos(0, 0, 2.55) * (
    Rot(0, 90, 0) * (Sphere(4) - Sphere(3.98)) - Box(10, 10, 10, align=ccM)
)
lights = [loc * Rot(0, 0, 180) * Sphere(0.5) for loc in PolarLocations(9.8, 6)]
body -= lights

body.label = "body"
inner.label = "inner"
window.label = "window"
for i, l in enumerate(lights):
    l.label = f"light_{i}"
```

## Assigning materials and interpolating colors for CAD view

`PbrProperties` objects are assigned directly to the `.material` attribute of CAD objects. Use `.interpolate_color()` to derive a representative `color` for the CAD view.

Note: This will change when build123d gets an own `Material` class: `shape.material: build123d.Material`

```python
body.material = metal
body.color = "grey"

inner.material = alu_hex
inner.color = metal.interpolate_color()

window.material = glass
window.color = glass.interpolate_color()

for i, l in enumerate(lights):
    l.material = red_light if i % 2 == 0 else yellow_light
    l.color = l.material.interpolate_color()
```

## Visualisation

Show and use a custom environment map in the Studio tab, rotated by 180°

```python
show(
    body,
    inner,
    window,
    lights,
    studio_environment="https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/4k/suburban_garden_4k.hdr",
    studio_env_rotation=275,
)
```

![cad-view](../screenshots/cad-view.png)

### PBR view

Switch to Studio mode:

```python
set_viewer_config(tab="studio")
```

![cad-view](../screenshots/studio-view.png)

### No tools mode

Tools can now be hidden by clicking on the **> Tools** button above the tools

![cad-view](../screenshots/studio-view-no-tools.png)

### Material Editor

Double click an object to select it and press the little "E" button.

![cad-view](../screenshots/studio-view-material-editor.png)

Changes are marked red, you can apply them as `overrides` in your Python code

## Full code

The complete demo can be found [here](../examples/pbr-studio-demo.py)
