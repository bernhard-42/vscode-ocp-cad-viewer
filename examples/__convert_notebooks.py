# %%
from pathlib import Path
import orjson

path = Path("../jupyter-cadquery/examples")
notebooks = [
    path / "6-show_object.ipynb",
    path / "7-show.ipynb",
    path / "8-show_all.ipynb",
    path / "9-set_viewer_config.ipynb",
]

target = Path("examples")

# %%


def convert(notebook):
    print(notebook)
    with open(notebook, "r") as fd:
        json_doc = orjson.loads(fd.read())

    with open(target / f"{notebook.stem}.py", "w") as fd:
        fd.write("\n\n# %%\n\n")
        fd.write("from ocp_vscode import *\n")
        for cell in json_doc["cells"]:
            for line in cell["source"]:
                if "cv." in line:
                    fd.write("# ")

                if (
                    "jupyter_cadquery" not in line
                    and "open_viewer" not in line
                    and not "close_viewer" in line
                ):
                    fd.write(line)

            fd.write("\n\n# %%\n\n")


for notebook in notebooks:
    convert(notebook)

# %%
