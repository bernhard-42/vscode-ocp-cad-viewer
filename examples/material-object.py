# %%
import copy

from build123d import *
from ocp_vscode import *
from ocp_vscode.utils import create_shader_ball
from threejs_materials import PbrProperties

import warnings


(
    warnings.warn(
        "\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n"
        "The required type of build123d's shape.material will change"
        "\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n",
        category=FutureWarning,
    )
)

car_base = PbrProperties.from_gpuopen("Car Paint")

materials = {
    "car_red": car_base.override(color=(0.5, 0, 0)),
    "car_green": car_base.override(color=(0, 0.5, 0)),
    "bronze": PbrProperties.from_gpuopen("Bronze Oxydized"),
    "chrome": PbrProperties.from_gpuopen("Chrome"),
    "glass": PbrProperties.from_gpuopen("Glass").override(thickness=10),
    "white_wine": PbrProperties.from_gpuopen("White Wine").override(thickness=100),
    "gold": PbrProperties.from_gpuopen("Gold"),
    "carbon_coat": PbrProperties.from_gpuopen("Carbon biColor Coat").scale(2, 2),
    "acryl": PbrProperties.from_physicallybased("Plastic (Acrylic)").override(
        color=(0.5, 0.0, 0.0), thickness=10
    ),
    "steel": PbrProperties.from_gpuopen("Stainless Steel Brushed").scale(3, 3),
    "alu": PbrProperties.from_gpuopen("Aluminum Brushed"),
    "bricks": PbrProperties.from_gpuopen("TH Large Red Bricks").scale(2, 2),
    "leather": PbrProperties.from_gpuopen("TH Brown Fabric Leather"),
    "alu_corr": PbrProperties.from_gpuopen("Aluminum Corrugated").scale(2, 2),
    "alu_hexagon": PbrProperties.from_gpuopen("Aluminum Hexagon").scale(4, 4),
    "perforated": PbrProperties.from_gpuopen("Perforated Metal"),
    "wood": PbrProperties.from_gpuopen("Ivory Walnut Solid Wood").scale(2, 2),
    "tiles": PbrProperties.from_gpuopen("Iberian Blue Ceramic Tiles").scale(0.5, 0.5),
    "tiles2": PbrProperties.from_gpuopen("Tiles Black Long Variative").scale(2, 2),
    "brass_scratched": PbrProperties.from_ambientcg("Metal 007"),
    "carbon": PbrProperties.from_ambientcg("Fabric 004").scale(2, 2),
    "plates": PbrProperties.from_ambientcg("Metal Plates 006"),
    "floor": PbrProperties.from_gpuopen("Adelie Brown Luxury Flooring").scale(4, 4),
    "plank": PbrProperties.from_polyhaven("Plank Flooring 03"),
    "rock_wall": PbrProperties.from_polyhaven("Rock Wall 16").scale(5, 5),
}

# %%


shader_ball = create_shader_ball("shader_ball")
show(
    shader_ball,
    Pos(20, 0, 0) * shader_ball,
    materials=[materials["floor"], materials["steel"]],
    studio_texture_mapping=StudioTextureMapping.PARAMETRIC,
    reset_camera=Camera.ISO,
)
set_viewer_config(tab="studio")

# export_gltf(shader_ball, "shader_ball.glb")

# %%
shader_ball = create_shader_ball("shader_ball")

n = 5
material_matrix = []
shader_balls = []
for i in range(n):
    for j in range(n):
        material_name = list(materials.keys())[i * 5 + j]
        sb = Pos(i * 30, j * 30, 0) * copy.copy(shader_ball)
        sb.label = f"ball_{material_name}"

        material = materials[material_name]
        sb.color = material.interpolate_color()

        material_matrix.append(material)
        shader_balls.append(sb)

show(
    *shader_balls,
    materials=material_matrix,
    reset_camera=Camera.ISO,
)
set_viewer_config(tab="studio")
