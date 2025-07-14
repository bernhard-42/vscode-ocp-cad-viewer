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

import * as fs from "fs";
import * as vscode from "vscode";
import { OCPCADController } from "./controller";
import * as output from "./output";

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
        _controller: OCPCADController,
        column: number
    ) {
        this.controller = _controller;

        if (OCPCADViewer.currentPanel) {
            // If we already have a panel, show it.

            output.debug(
                "OCPCADViewer.createOrShow: Revealing existing webview panel"
            );

            OCPCADViewer.currentPanel._panel.reveal(column);
        } else {
            // Otherwise, create a new panel.

            output.debug(
                "OCPCADViewer.createOrShow: Creating new webview panel"
            );

            // get all current tabs
            const tabs: vscode.Tab[] = vscode.window.tabGroups.all
                .map((tg) => tg.tabs)
                .flat();

            const panel = vscode.window.createWebviewPanel(
                OCPCADViewer.viewType,
                "OCP CAD Viewer",
                column,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );
            OCPCADViewer.currentPanel = new OCPCADViewer(panel, extensionUri);

            // delete old tabs called "OCP CAD Viewer"
            for (var tab of tabs) {
                if (tab.label === "OCP CAD Viewer") {
                    await vscode.window.tabGroups.close(tab);
                }
            }
        }
    }

    public static revive(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        output.debug("OCPCADViewer.revive: Reviving webview panel");
        // vscode.commands.executeCommand("ocpCadViewer.ocpCadViewer");
        OCPCADViewer.currentPanel = new OCPCADViewer(panel, extensionUri) 
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;

        this._panel.onDidDispose(
            () => {
                this.dispose();
            },
            null,
            this._disposables
        );
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
                        if (
                            typeof message.text.data === "string" ||
                            message.text.data instanceof String
                        ) {
                            data = Buffer.from(
                                message.text.data.replace(
                                    "data:image/png;base64,",
                                    ""
                                ),
                                "base64"
                            );
                        } else {
                            data = message.text.data;
                        }
                        var filename = message.text.filename;
                        try {
                            // first write to a temp name to avoid polling is successful before finished ...
                            let suffix = "-temp" + Date.now().toString(16);
                            fs.writeFileSync(filename + suffix, data);
                            // ... and then rename to the actual filename
                            fs.renameSync(filename + suffix, filename);
                            vscode.window.showInformationMessage(
                                `Screenshot saved as\n${filename}`
                            );
                        } catch (error) {
                            vscode.window.showErrorMessage(
                                `Error saving screenshot as\n${filename}`
                            );
                        }
                        return;
                    case "status":
                        if (message.text.selected != null) {
                            vscode.env.clipboard.writeText(
                                message.text.selected.join(",")
                            );
                        }
                }
            },
            null,
            this._disposables
        );
    }

    public async dispose() {
        output.debug("OCPCADViewer.dispose: OCP CAD Viewer dispose");

        OCPCADViewer.currentPanel = undefined;

        await OCPCADViewer.controller?.dispose();

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    public update(div: string) {
        if (div !== "") {
            output.debug("OCPCADViewer.update: Updating webview");
            const webview = this._panel.webview;
            this._panel.title = "OCP CAD Viewer";
            webview.html = div;
        }
    }

    public getView() {
        return this._panel.webview;
    }
}
