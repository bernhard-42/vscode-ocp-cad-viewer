"use strict";
/* eslint-disable @typescript-eslint/naming-convention */
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
exports.CadqueryController = void 0;
const vscode = require("vscode");
const viewer_1 = require("./viewer");
const display_1 = require("./display");
const http_1 = require("http");
const output = require("./output");
const logo_1 = require("./logo");
var serverStarted = false;
class CadqueryController {
    constructor(context, port, statusController) {
        this.context = context;
        this.port = port;
        this.statusController = statusController;
        if (!serverStarted) {
            if (this.startCommandServer(this.port)) {
                output.info("Starting web server ...");
                serverStarted = true;
                viewer_1.CadqueryViewer.createOrShow(this.context.extensionUri, this);
                viewer_1.CadqueryViewer.currentPanel?.update((0, display_1.template)());
                let panel = viewer_1.CadqueryViewer.currentPanel;
                this.view = panel?.getView();
            }
        }
    }
    isStarted() {
        return serverStarted;
    }
    logo() {
        this.view?.postMessage(logo_1.logo);
    }
    startCommandServer(port) {
        this.server = (0, http_1.createServer)((req, res) => {
            let response = "";
            if (req.method === "GET") {
                response = "Only POST supported\n";
                res.writeHead(200, {
                    "Content-Length": response.length,
                    "Content-Type": "text/plain"
                });
                res.end(response);
            }
            else if (req.method === "POST") {
                var json = "";
                req.on("data", (chunk) => {
                    json += chunk;
                });
                req.on("end", () => {
                    output.debug("Received a new model");
                    this.view?.postMessage(json);
                    output.debug("Posted model to view");
                    response = "done";
                    res.writeHead(201, { "Content-Type": "text/plain" });
                    res.end(response);
                });
            }
        });
        this.server.on("error", (error) => {
            let msg = "";
            if (error.message.indexOf("EADDRINUSE") > 0) {
                output.info(`Port ${this.port} alread in use, please choose another port`);
            }
            else {
                vscode.window.showErrorMessage(`${error}`);
            }
        });
        this.server.on("listening", () => {
            output.info(`OCP CAD Viewer is initialized, command server is running on port ${this.port}`);
        });
        this.server.listen(port);
        return this.server.address() !== null;
    }
    dispose() {
        output.debug("CadqueryController dispose");
        this.server?.close();
        serverStarted = false;
        output.info("Server is shut down");
        this.statusController.refresh("<none>");
    }
}
exports.CadqueryController = CadqueryController;
//# sourceMappingURL=controller.js.map