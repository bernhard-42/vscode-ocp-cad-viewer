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
import * as fs from "fs";

export function template(
    styleSrc: vscode.Uri,
    scriptSrc: vscode.Uri,
    htmlSrc: vscode.Uri
) {
    let options = vscode.workspace.getConfiguration("OcpCadViewer.view");

    var theme: string = options.get("theme") || "browser";
    if (options.get("dark") == true) {
        vscode.window.showWarningMessage(
            "Setting OcpCadViewer.view.dark is " +
                "deprecated, unset it and use OcpCadViewer.view.theme"
        );
        theme = "dark";
    }
    const treeWidth = options.get("tree_width");
    const control = options.get("orbit_control") ? "orbit" : "trackball";
    const up = options.get("up");
    const glass = options.get("glass");
    const tools = options.get("tools");

    let html = fs.readFileSync(htmlSrc.fsPath, "utf8"); // resources/webview.html

    html = html.replace("{{ standalone_scripts|safe }}", "");
    html = html.replace("{{ standalone_imports|safe }}", "");
    html = html.replace(
        "{{ standalone_comms|safe }}",
        "const vscode = acquireVsCodeApi();"
    );
    html = html.replace("{{ standalone_init|safe }}", "");
    html = html.replace("{{ styleSrc }}", styleSrc.toString());
    html = html.replace("{{ scriptSrc }}", scriptSrc.toString());
    html = html.replace("{{ theme }}", theme);
    html = html.replace("{{ treeWidth }}", `${treeWidth}`);
    html = html.replace("{{ control }}", control);
    html = html.replace("{{ up }}", `${up}`);
    html = html.replace(/\{\{ glass\|tojson \}\}/g, `${glass}`);
    html = html.replace(/\{\{ tools\|tojson \}\}/g, `${tools}`);

    return html;
}
