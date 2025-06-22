/* eslint-disable @typescript-eslint/naming-convention */
/*
   Copyright 2025 Bernhard Walter
  
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { getCurrentFolder } from "./utils";

const build123d_demo = `# %%

# The markers "# %%" separate code blocks for execution (cells) 
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import *
from ocp_vscode import *

# %%
# Builder mode

with BuildPart() as bp:
    Box(1,1,1)
    fillet(bp.edges(), radius=0.1)

show(bp)

# %%
# Algebra mode

b2 = Box(1,2,3)
b2 = fillet(b2.edges(), 0.1)

show(b2, axes=True, axes0=True, grid=(True, True, True), transparent=True)

# %%

`;

const cadquery_demo = `# %%

# The markers "# %%" separate code blocks for execution (cells) 
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

import cadquery as cq
from ocp_vscode import *

# %%

b = cq.Workplane().box(1,2,3).fillet(0.1)

show(b)
`;

export function createDemoFile(lib: string) {
    return new Promise((resolve, reject) => {
        const current = getCurrentFolder()[0];
        const demoFilePath = path.join(current, "ocp_vscode_demo.py");
        if (lib === "build123d") {
            fs.writeFileSync(demoFilePath, build123d_demo);
        } else {
            fs.writeFileSync(demoFilePath, cadquery_demo);
        }
        try {
            vscode.workspace.openTextDocument(demoFilePath).then((doc) => {
                vscode.window.showTextDocument(doc);
                resolve(true);
            });
        } catch {
            reject(false);
        }
    });
}
