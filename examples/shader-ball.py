# %%
import copy
from pathlib import Path

from build123d import *
from ocp_vscode import *
from ocp_vscode.utils import create_shader_ball
from threejs_materials import PbrProperties
from pymat import brass

# threejs-material
brass_tm = PbrProperties.from_gpuopen("Brass").scale(4, 4)

# pymat.Material
brass_pymat = brass

# Import threejs-material from GLTF2 (blender export)
here = Path.cwd()
if not here.parts[-1] == "examples":
    here = here / "examples"
brass_gltf = PbrProperties.load_gltf(here / "brass-deco" / "brass_cube.gltf")[
    "Ornamental Design Embossed Brass"
]

show_clear()

shader_ball_1 = Pos(0, 0, 0) * create_shader_ball("shader_ball")
shader_ball_1.label = "shader_ball_tm"
shader_ball_2 = Pos(-20, 20, 0) * copy.copy(shader_ball_1)
shader_ball_2.label = "shader_ball_pymat"
shader_ball_3 = Pos(20, 20, 0) * copy.copy(shader_ball_1)
shader_ball_3.label = "shader_ball_gltf"

show(
    shader_ball_1,
    shader_ball_2,
    shader_ball_3,
    materials=[brass_tm, brass_pymat, brass_gltf],
    studio_texture_mapping=StudioTextureMapping.PARAMETRIC,
    studio_environment=StudioEnvironment.SPOTLIT_SETUP,
)
set_viewer_config(tab="studio")
