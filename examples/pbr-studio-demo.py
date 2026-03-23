import time

from build123d import *
from ocp_vscode import *
from threejs_materials import Material

mcc = (Align.MIN, Align.CENTER, Align.CENTER)
ccm = (Align.CENTER, Align.CENTER, Align.MIN)
ccM = (Align.CENTER, Align.CENTER, Align.MAX)

#
# Material setup
#

# Use a GPUOpen material
alu_hex = Material.gpuopen.load("Aluminum Hexagon")

# Use a GPUOpen material and override the glass behavior
glass = Material.gpuopen.load("Glass").override(transmission=0.98, thickness=0.8)

# Use an AmbientCG material, and scale the texture to 2 in u and v direction
metal = Material.ambientcg.load("Metal 049 C").scale(2, 2)

# Use a PhysicallyBased material and override color for two material instances
light = Material.physicallybased.load("Plastic (Acrylic)")
red_light = light.override(color=(1, 0, 0))
yellow_light = light.override(color="yellow")

#
# The object
#

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

# Setting material and interpolate colors for CAD view
body.material = metal
body.color = "grey"

inner.material = alu_hex
inner.color = alu_hex.interpolate_color()

window.material = glass
window.color = glass.interpolate_color()

for i, l in enumerate(lights):
    l.material = red_light if i % 2 == 0 else yellow_light
    l.color = l.material.interpolate_color()
#
# Visualisation
#
# %%


# show and use a custom env map, rotated by 180°
show(
    body,
    inner,
    window,
    lights,
    studio_environment="https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/4k/suburban_garden_4k.hdr",
    studio_env_rotation=275,
    position=[53.93, -36.89, 24.07],
    quaternion=[0.49075, 0.26839, 0.38282, 0.73522],
    target=[0.78, -1.22, -1.76],
)

time.sleep(1)
