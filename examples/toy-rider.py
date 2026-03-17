from pathlib import Path
from build123d import *
from ocp_vscode import *
from threejs_materials import Material

try:
    model = import_step(Path.home() / "Downloads" / "Toy Rider S2022 ASM stp.STEP")
except:
    raise RuntimeError(
        "Download STEP file from https://grabcad.com/library/toy-rider-car-1 first to ~/Downloads"
    )

show(Rot(90, 0, 0) * model)
# %%

#
# Material definition
#

car_red = Material.gpuopen.load("Car Paint").override(color=(0.5, 0, 0))
chrome = Material.gpuopen.load("Chrome")
rubber = Material.gpuopen.load("Rubber").override(color=(0.06, 0.06, 0.06))
glass = Material.gpuopen.load("Glass")
steel = Material.gpuopen.load("Stainless Steel Brushed")
fabric = Material.gpuopen.load("Midnight Blue Heavy Fabric")
alu = Material.gpuopen.load("Aluminum Brushed")
alu_matte = Material.gpuopen.load("Aluminum Matte").scale(2, 2)
leather = Material.gpuopen.load("TH: Brown Leather")
wood = Material.gpuopen.load("Mahogany Varnished").scale(2, 2)
plastic = Material.ambientcg.load("Plastic 012 B")
acrylic_white = Material.physicallybased.load("Plastic (Acrylic)")
acrylic_red = Material.physicallybased.load("Plastic (Acrylic)").override(color="red")

material_definitions = {
    "car-red": car_red,
    "chrome": chrome,
    "rubber": rubber,
    "glass": glass,
    "steel": steel,
    "alu": alu,
    "alu-matte": alu_matte,
    "leather": leather,
    "wood": wood,
    "fabric": fabric,
    "plastic": plastic,
    "acrylic_white": acrylic_white,
    "acrylic_red": acrylic_red,
}

# %%

#
# Add materials
#


def convert(model, material_definitions):
    color_mapping = {
        "RiderToy": "car-red",
        "Trim": "car-red",
        "Hood": "car-red",
        "Door": "car-red",
        "Cover": "plastic",
        "Axle": "steel",
        "Supportin": "steel",
        "FloorBoards": "steel",
        "Trunk_Storage": "steel",
        "Grill": "chrome",
        "Bumper": "chrome",
        "Gear": "chrome",
        "Peddle": "chrome",
        "Bucket": "leather",
        "DashandConsole": "wood",
        "Floor": "fabric",
        "Radio": "plastic",
        "Visor": "plastic",
        "Head_Lamp": "acrylic_white",
        "TailLamp": "acrylic_red",
        "Streeing": "leather",
    }

    def assign_material(obj, material):
        obj.material = material
        obj.color = material_definitions[material].interpolate_color()

    def walk(obj, ind=""):
        if hasattr(obj, "children") and obj.children:
            children = []
            for child in obj.children:
                if obj.label == "Windshield_ASM" and child.label == "WindShield":
                    child.label = "Windshield"  # subtle renaming

                sub_assembly = walk(child, ind + "  ")
                if sub_assembly is not None:
                    children.append(sub_assembly)

            return Compound(label=obj.label, children=children)

        else:
            if "wheel" in obj.label:
                objects = list(obj)
                assign_material(objects[0], "chrome")
                assign_material(objects[1], "rubber")
                obj = Compound(label=obj.label, children=objects)
            elif "Windshield" in obj.label:
                objects = list(obj)
                objects[0].label = "WindShield"
                objects[1].label = "Frame"
                assign_material(objects[0], "glass")
                assign_material(objects[1], "chrome")
                obj = Compound(label=obj.label, children=objects)
            elif "WindShield" in obj.label:
                return None
            else:
                for k, v in color_mapping.items():
                    if k in obj.label:
                        assign_material(obj, v)
            return obj

    return walk(model)


model2 = Rot(90, 0, 0) * convert(model, material_definitions)
show(
    model2,
    material_definitions=material_definitions,
)
