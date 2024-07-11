/*
   Copyright 2023 Bernhard Walter
  
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

import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { OCPCADController } from "./controller";
import * as output from "./output";
import { getCurrentFolder } from "./utils";

export class OCPCADViewer {
    /**
     * Track the currently panel. Only allow a single panel to exist at a time.
     */

    public static currentPanel: OCPCADViewer | undefined;
    public static controller: OCPCADController | undefined;

    public static readonly viewType = "OCPCADViewer";

    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    public static async createOrShow(
        extensionUri: vscode.Uri,
        _controller: OCPCADController
    ) {
        this.controller = _controller;

        if (OCPCADViewer.currentPanel) {
            // If we already have a panel, show it.

            output.debug("Revealing existing webview panel");

            OCPCADViewer.currentPanel._panel.reveal(vscode.ViewColumn.Two);
        } else {
            // Otherwise, create a new panel.

            output.debug("Creating new webview panel");

            // get all current tabs
            const tabs: vscode.Tab[] = vscode.window.tabGroups.all.map(tg => tg.tabs).flat();

            const panel = vscode.window.createWebviewPanel(
                OCPCADViewer.viewType,
                "OCP CAD Viewer",
                vscode.ViewColumn.Two,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );
            OCPCADViewer.currentPanel = new OCPCADViewer(
                panel,
                extensionUri
            );

            // delete old tabs called "OCP CAD Viewer"
            for (var tab of tabs) {
                if (tab.label === "OCP CAD Viewer") {
                    await vscode.window.tabGroups.close(tab);
                }
            }
        }
    }

    public static revive(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        output.debug("Reviving webview panel");

        vscode.commands.executeCommand('ocpCadViewer.ocpCadViewer');
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = "";

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            (message) => {
                // output.debug(`Received message ${message} from Webview panel`);
                switch (message.command) {
                    case "alert":
                        vscode.window.showErrorMessage(message.text);
                        return;
                    case "screenshot":
                        var data;
                        if (typeof message.text.data === 'string' || message.text.data instanceof String){
                            data = Buffer.from(message.text.data.replace('data:image/png;base64,', ''), "base64");
                        } else {
                            data = message.text.data;
                        }
                        var folder = getCurrentFolder()[0];
                        var filename = message.text.filename;
                        fs.writeFileSync(path.join(folder, filename), data);
                        return;
                }
            },
            null,
            this._disposables
        );
    }

    public dispose() {
        output.debug("OCP CAD Viewer dispose");
        OCPCADViewer.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
        OCPCADViewer.controller?.dispose();
    }

    public update(div: string) {
        if (div !== "") {
            output.debug("Updateing webview");
            const webview = this._panel.webview;
            this._panel.title = "OCP CAD Viewer";
            webview.html = div;
        }
    }

    public getView() {
        return this._panel.webview;
    }
}
/*  */