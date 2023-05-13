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

import * as vscode from "vscode";
import { CadqueryViewer } from "./viewer";
import { template } from "./display";
import { WebSocket, Server } from "ws";
import * as output from "./output";
import { logo } from "./logo";
import { StatusManagerProvider } from "./statusManager";

var serverStarted = false;

interface Message {
    type: string;
    action: string;
    data: string | undefined;
}

export class CadqueryController {
    server: Server | undefined;
    pythonListener: WebSocket | undefined;
    statusController: StatusManagerProvider;
    view: vscode.Webview | undefined;
    port: number;
    viewer_message = "{}";
    splash: boolean = true;

    constructor(
        private context: vscode.ExtensionContext,
        port: number,
        statusController: StatusManagerProvider
    ) {
        this.port = port;
        this.statusController = statusController;

        if (!serverStarted) {
            serverStarted = this.startCommandServer(this.port);
            if (serverStarted) {
                output.info("Starting websocket server ...");
                CadqueryViewer.createOrShow(this.context.extensionUri, this);
                let panel = CadqueryViewer.currentPanel;
                this.view = panel?.getView();
                if (this.view !== undefined) {
                    const stylePath = vscode.Uri.joinPath(this.context.extensionUri, "node_modules", "three-cad-viewer", "dist", "three-cad-viewer.css");
                    const scriptPath = vscode.Uri.joinPath(this.context.extensionUri, "node_modules", "three-cad-viewer", "dist", "three-cad-viewer.esm.js");
                    const styleSrc = this.view.asWebviewUri(stylePath);
                    const scriptSrc = this.view.asWebviewUri(scriptPath);
                    CadqueryViewer.currentPanel?.update(template(styleSrc, scriptSrc));

                    this.view.onDidReceiveMessage(
                        message => {
                            this.viewer_message = message;
                        });

                }
            }
        }
    }

    public isStarted(): boolean {
        return serverStarted;
    }

    public logo() {
        this.view?.postMessage(logo);
    }

    public config() {
        let options = vscode.workspace.getConfiguration("OcpCadViewer.view");
        let c: Record<string, any> = {
            "theme": options.get("dark") ? "dark" : "light",
            "tree_width": options.get("tree_width"),
            "control": options.get("orbit_control") ? "orbit" : "trackball",
            "up": options.get("up"),
            "glass": options.get("glass"),
            "tools": options.get("tools"),
            "rotate_speed": options.get("rotate_speed"),
            "zoom_speed": options.get("zoom_speed"),
            "pan_speed": options.get("pan_speed"),
            "axes": options.get("axes"),
            "axes0": options.get("axes0"),
            "black_edges": options.get("black_edges"),
            "grid": [options.get("grid_XY"), options.get("grid_XZ"), options.get("grid_YZ")],
            "collapse": options.get("collapse"),
            "ortho": options.get("ortho"),
            "ticks": options.get("ticks"),
            "default_opacity": options.get("default_opacity"),
            "transparent": options.get("transparent"),
            "explode": options.get("explode"),
        }
        options = vscode.workspace.getConfiguration("OcpCadViewer.render");
        c["angular_tolerance"] = options.get("angular_tolerance");
        c["deviation"] = options.get("deviation");
        c["default_color"] = options.get("default_color");
        c["default_edgecolor"] = options.get("default_edgecolor");
        c["default_facecolor"] = options.get("default_facecolor");
        c["default_thickedgecolor"] = options.get("default_thickedgecolor");
        c["default_vertexcolor"] = options.get("default_vertexcolor");
        c["ambient_intensity"] = options.get("ambient_intensity");
        c["direct_intensity"] = options.get("direct_intensity");
        c["_splash"] = this.splash;
        return c
    }

    public startCommandServer(port: number): boolean {

        this.server = new WebSocket.Server({ port: port });
        const server = this.server;
        try {
            server.on('connection', (socket) => {
                console.log('Client connected');

                socket.on('message', (message) => {
                    console.log(`Received message: ${message}`);

                    const raw_data = message.toString()
                    const messageType = raw_data.substring(0, 1)
                    var data = message.toString().substring(2);
                    if (messageType === "C") {
                        data = JSON.parse(data);
                        if (data === "status") {
                            socket.send(this.viewer_message);
                        } else if (data === "config") {
                            socket.send(JSON.stringify(this.config()));
                        }

                    } else if (messageType === "D") {
                        output.debug("Received a new model");
                        this.view?.postMessage(data);
                        output.debug("Posted model to view");
                        if (this.splash) { this.splash = false }

                    } else if (messageType === "L") {
                        this.pythonListener = socket;
                    }
                });

                socket.on('close', () => {
                    output.info('Client disconnected');
                    // if socket is pythonListener, set to undefined
                    if (this.pythonListener === socket) {
                        this.pythonListener = undefined;
                    }
                });
            });
        } catch (error: any) {
            output.error(`Server error: ${error.message}`);
            return false;
        }

        this.server.on('error', (error) => {
            output.error(`Server error: ${error.message}`);
        });

        return true;
    }

    public stopCommandServer() {
        if (this.server !== undefined) {
            this.server.close((error) => {
                if (error) {
                    output.error(`Server error: ${error.message}`);
                }
            });
            return true;
        } else {
            return false;
        }
    }

    public dispose() {
        output.debug("CadqueryController dispose");

        this.stopCommandServer();
        serverStarted = false;
        output.info("Server is shut down");
        this.statusController.refresh("<none>");
    }
}
