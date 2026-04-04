from pathlib import Path
from build123d import *
from ocp_vscode import *
from threejs_materials import PbrProperties

try:
    model = import_step(Path.home() / "Downloads" / "Toy Rider S2022 ASM stp.STEP")
except:
    raise RuntimeError(
        "Download STEP file from https://grabcad.com/library/toy-rider-car-1 first to ~/Downloads"
    )

show(Rot(90, 0, 0) * model)
# %%

#
# PbrProperties definition
#

car_red = PbrProperties.from_gpuopen("Car Paint").override(color=(0.5, 0, 0))
chrome = PbrProperties.from_gpuopen("Chrome")
rubber = PbrProperties.from_gpuopen("Rubber").override(color=(0.06, 0.06, 0.06))
glass = PbrProperties.from_gpuopen("Glass")
steel = PbrProperties.from_gpuopen("Stainless Steel Brushed")
fabric = PbrProperties.from_gpuopen("Midnight Blue Heavy Fabric")
alu = PbrProperties.from_gpuopen("Aluminum Brushed")
alu_matte = PbrProperties.from_gpuopen("Aluminum Matte").scale(2, 2)
leather = PbrProperties.from_gpuopen("TH: Brown Leather")
wood = PbrProperties.from_gpuopen("Mahogany Varnished").scale(2, 2)
plastic = PbrProperties.from_ambientcg("Plastic 012 B")
acrylic_white = PbrProperties.from_physicallybased("Plastic (Acrylic)")
acrylic_red = PbrProperties.from_physicallybased("Plastic (Acrylic)").override(
    color="red"
)


# %%

#
# Add materials
#


def convert(model):
    color_mapping = {
        "RiderToy": car_red,
        "Trim": car_red,
        "Hood": car_red,
        "Door": car_red,
        "Cover": plastic,
        "Axle": steel,
        "Supportin": steel,
        "FloorBoards": steel,
        "Trunk_Storage": steel,
        "Grill": chrome,
        "Bumper": chrome,
        "Gear": chrome,
        "Peddle": chrome,
        "Bucket": leather,
        "DashandConsole": wood,
        "Floor": fabric,
        "Radio": plastic,
        "Visor": plastic,
        "Head_Lamp": acrylic_white,
        "TailLamp": acrylic_red,
        "Streeing": leather,
    }

    def assign_material(obj, material):
        obj.material = material
        obj.color = material.interpolate_color()

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
                assign_material(objects[0], chrome)
                assign_material(objects[1], rubber)
                obj = Compound(label=obj.label, children=objects)
            elif "Windshield" in obj.label:
                objects = list(obj)
                objects[0].label = "WindShield"
                objects[1].label = "Frame"
                assign_material(objects[0], glass)
                assign_material(objects[1], chrome)
                obj = Compound(label=obj.label, children=objects)
            elif "WindShield" in obj.label:
                return None
            else:
                for k, v in color_mapping.items():
                    if k in obj.label:
                        assign_material(obj, v)
            return obj

    return walk(model)


model2 = Rot(90, 0, 0) * convert(model)
show(model2)
