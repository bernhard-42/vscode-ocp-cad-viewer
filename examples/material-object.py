# %%
import copy

from build123d import *
from ocp_vscode import *
from ocp_vscode.utils import create_shader_ball
from threejs_materials import PbrProperties

ccm = (Align.CENTER, Align.CENTER, Align.MIN)
cMc = (Align.CENTER, Align.MAX, Align.CENTER)
cM = (Align.CENTER, Align.MAX)

car_base = PbrProperties.from_gpuopen("Car Paint")

materials = {
    "car_red": car_base.override(color=(0.5, 0, 0)),
    "car_green": car_base.override(color=(0, 0.5, 0)),
    "bronze": PbrProperties.from_gpuopen("Bronze Oxydized"),
    "chrome": PbrProperties.from_gpuopen("Chrome"),
    "glass": PbrProperties.from_gpuopen("Glass"),
    # "red_wine": PbrProperties.from_gpuopen("Red Wine"),
    "white_wine": PbrProperties.from_gpuopen("White Wine"),
    "gold": PbrProperties.from_gpuopen("Gold"),
    "carbon_coat": PbrProperties.from_gpuopen("Carbon biColor Coat").scale(2, 2),
    "acryl_gp": PbrProperties.from_gpuopen("Acryl Plastic").override(color=(0.5, 0, 0)),
    "steel": PbrProperties.from_gpuopen("Stainless Steel Brushed"),
    "alu": PbrProperties.from_gpuopen("Aluminum Brushed"),
    "bricks": PbrProperties.from_gpuopen("TH Large Red Bricks").scale(2, 2),
    # "alu_matte": PbrProperties.from_gpuopen("Aluminum Matte").scale(2, 2),
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
    "acryl": PbrProperties.from_physicallybased("Plastic (Acrylic)"),
    "plank": PbrProperties.from_polyhaven("Plank Flooring 03"),
    "rock_wall": PbrProperties.from_polyhaven("Rock Wall 16").scale(5, 5),
}

# %%


shader_ball = create_shader_ball("shader_ball")
shader_ball.material = Material("stainless", pbr=materials["tiles2"])
show(
    shader_ball,
    studio_texture_mapping=StudioTextureMapping.PARAMETRIC,
)
set_viewer_config(tab="studio")

export_gltf(shader_ball, "shader_ball.glb")


# %%

a = Pos(-20, 0, 0) * create_shader_ball("sb_a")
b = Pos(20, 0, 0) * create_shader_ball("sb_b")
a.material = Material(
    "aluminum", pbr=PbrProperties.from_gpuopen("Aluminum Hexagon").scale(0.5, 0.5)
)
b.material = Material(
    "aluminum", pbr=PbrProperties.from_gpuopen("Aluminum Hexagon").scale(2, 2)
)
c = Compound(label="sbs", children=[a, b])
show(c)
set_viewer_config(tab="studio")
export_gltf(c, "2_shader_balls.glb")

# %%
shader_ball = create_shader_ball("shader_ball")
objects = []
n = 5
for i in range(n):
    for j in range(n):
        material_name = list(materials.keys())[i * 5 + j]
        sb = Pos(i * 30, j * 30, 0) * copy.copy(shader_ball)
        sb.label = f"ball_{material_name}"

        material = Material.create(material_name, pbr=materials[material_name])
        sb.material = material

        objects.append(sb)

all_sb = Compound(label="shader_balls", children=objects)

show(all_sb)
set_viewer_config(tab="studio")

export_gltf(all_sb, "shader_balls.glb")
