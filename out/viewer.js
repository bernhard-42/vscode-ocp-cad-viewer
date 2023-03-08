"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.CadqueryViewer = void 0;
const vscode = require("vscode");
const display_1 = require("./display");
const output = require("./output");
class CadqueryViewer {
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = "";
        // Update the content based on view changes
        this._panel.onDidChangeViewState((e) => {
            if (this._panel.visible) {
                output.debug("Webview panel changed state");
                this.update((0, display_1.template)());
            }
        }, null, this._disposables);
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage((message) => {
            output.debug(`Received message ${message} from Webview panel`);
            switch (message.command) {
                case "alert":
                    vscode.window.showErrorMessage(message.text);
                    return;
            }
        }, null, this._disposables);
    }
    static createOrShow(extensionUri, _controller) {
        this.controller = _controller;
        if (CadqueryViewer.currentPanel) {
            // If we already have a panel, show it.
            output.debug("Revealing existing webview panel");
            CadqueryViewer.currentPanel._panel.reveal(vscode.ViewColumn.Two);
        }
        else {
            // Otherwise, create a new panel.
            output.debug("Creating new webview panel");
            const panel = vscode.window.createWebviewPanel(CadqueryViewer.viewType, "OCP CAD Viewer", vscode.ViewColumn.Two, {
                enableScripts: true,
                retainContextWhenHidden: true
            });
            CadqueryViewer.currentPanel = new CadqueryViewer(panel, extensionUri);
        }
    }
    static revive(panel, extensionUri) {
        output.debug("Reviving webview panel");
        CadqueryViewer.currentPanel = new CadqueryViewer(panel, extensionUri);
    }
    dispose() {
        output.debug("CadqueryViewer dispose");
        CadqueryViewer.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
        CadqueryViewer.controller?.dispose();
    }
    update(div) {
        if (div !== "") {
            output.debug("Updateing webview");
            const webview = this._panel.webview;
            this._panel.title = "OCP CAD Viewer";
            webview.html = div;
        }
    }
    getView() {
        return this._panel.webview;
    }
}
exports.CadqueryViewer = CadqueryViewer;
CadqueryViewer.viewType = "cadqueryViewer";
//# sourceMappingURL=viewer.js.map