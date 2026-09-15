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

import * as fs from "fs";
import * as os from "os";
import * as vscode from "vscode";
import { OCPCADViewer } from "./viewer";
import { createServer, Server } from "http";
import { WebSocket, WebSocketServer } from "ws";
import * as output from "./output";
import { StatusManagerProvider } from "./statusManager";
import { getPythonPath, getTempFolder } from "./utils";
import { removeState, getConfig } from "./state";
import { getAutomationShellConfig } from "./system/shell";

/**
 * The modifier keys for the platform VS Code runs on - where the keys are
 * pressed, which with a remote kernel is not where Python runs.
 *
 * The setting holds one map per platform, "macOS" and "default", so that one
 * settings.json serves every machine Settings Sync copies it to, and so that
 * whoever reads it sees which platform gets what. `meta` rotates, hides and
 * isolates, and `metaKey` is the Win/Super key on Windows and Linux, which
 * the desktop takes for itself, so there `meta` and `alt` swap physical keys.
 * A flat map - the setting's shape before this - is taken as it is, on every
 * platform, as it always was.
 */
function modifierKeys(options: vscode.WorkspaceConfiguration): Record<string, string> {
    const configured = options.get<Record<string, any>>("modifier_keys") ?? {};
    if (configured["default"] == null && configured["macOS"] == null) {
        return configured;
    }
    if (process.platform === "darwin" && configured["macOS"] != null) {
        return configured["macOS"];
    }
    return configured["default"] ?? configured["macOS"];
}

var serverStarted = false;

interface Message {
    type: string;
    action: string;
    data: string | undefined;
}

export class OCPCADController {
    server: Server | undefined;
    wss: WebSocketServer | undefined;
    pythonListener: WebSocket | undefined;
    pythonBackendTerminal: vscode.Terminal | undefined;
    statusController: StatusManagerProvider;
    statusBarItem: vscode.StatusBarItem;
    view: vscode.Webview | undefined;
    port: number;
    // An object, not the string "{}": it is JSON.stringify'd into the status
    // reply, and a string would arrive in Python as a str where a dict is
    // expected - a show() before the webview has pushed its first status
    // would fail on it. An empty object is the honest answer instead: no
    // viewer has reported anything changed yet.
    viewer_message: Record<string, any> = {};
    splash: boolean = true;
    private backendHasRegistered = false;

    constructor(
        private context: vscode.ExtensionContext,
        port: number,
        statusController: StatusManagerProvider,
        statusBarItem: vscode.StatusBarItem
    ) {
        this.port = port;
        this.statusController = statusController;
        this.statusBarItem = statusBarItem;
    }

    public isStarted(): boolean {
        return serverStarted;
    }

    public async logo() {
        // Everything the webview cannot work out for itself, in one message:
        // where the resources are, and what the settings say. The page is a
        // static file - nothing is substituted into it - so this is the whole
        // of the handshake, and it ends with the splash on screen.
        //
        // The names are the renderer's, like everything else that crosses this
        // boundary. The splash model itself is ocp-viewer-core's and does not
        // travel: the webview has the core loaded and asks it by name.
        var conf = this.config();
        return await this.view?.postMessage({
            type: "init",
            paths: {
                style: this.resourceUri("three-cad-viewer", "dist", "three-cad-viewer.css"),
                renderer: this.resourceUri(
                    "three-cad-viewer",
                    "dist",
                    "three-cad-viewer.esm.js"
                ),
                core: this.resourceUri("ocp-viewer-core", "src", "index.js")
            },
            settings: {
                keymap: conf["modifier_keys"],
                theme: conf["theme"],
                treeWidth: conf["tree_width"],
                glass: conf["glass"],
                tools: conf["tools"],
                up: conf["up"],
                control: conf["control"]
            }
        });
    }

    private resourceUri(...segments: string[]): string {
        return this.view!.asWebviewUri(
            vscode.Uri.joinPath(this.context.extensionUri, "node_modules", ...segments)
        ).toString();
    }

    public config() {
        let options = vscode.workspace.getConfiguration("OcpCadViewer.view");

        const theme = options.get("theme");

        let c: Record<string, any> = {
            theme: theme,
            tree_width: options.get("tree_width"),
            control: options.get("orbit_control") ? "orbit" : "trackball",
            up: options.get("up"),
            glass: options.get("glass"),
            new_tree_behavior: options.get("new_tree_behavior"),
            tools: options.get("tools"),
            rotate_speed: options.get("rotate_speed"),
            zoom_speed: options.get("zoom_speed"),
            pan_speed: options.get("pan_speed"),
            axes: options.get("axes"),
            axes0: options.get("axes0"),
            black_edges: options.get("black_edges"),
            grid: [options.get("grid_XY"), options.get("grid_XZ"), options.get("grid_YZ")],
            center_grid: options.get("center_grid"),
            grid_font_size: options.get("grid_font_size"),
            collapse: options.get("collapse"),
            ortho: options.get("ortho"),
            ticks: options.get("ticks"),
            default_opacity: options.get("default_opacity"),
            reset_camera: options.get("reset_camera"),
            transparent: options.get("transparent"),
            explode: options.get("explode"),
            modifier_keys: modifierKeys(options)
        };
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
        c["metalness"] = options.get("metalness");
        c["roughness"] = options.get("roughness");
        c["_splash"] = this.splash;
        return c;
    }

    async start(column: number) {
        if (!serverStarted) {
            serverStarted = await this.startCommandServer();
            if (serverStarted) {
                output.debug("OCPCADController.start: Starting websocket server ...");
                await OCPCADViewer.createOrShow(this.context.extensionUri, this, column);
                let panel = OCPCADViewer.currentPanel;
                this.view = panel?.getView();
                if (this.view !== undefined) {
                    // The page is a static file: nothing is substituted into
                    // it, and what it cannot know arrives in the `init` message
                    // below. display.ts existed to do that substituting.
                    const htmlPath = vscode.Uri.joinPath(
                        this.context.extensionUri,
                        "resources",
                        "viewer.html"
                    );
                    OCPCADViewer.currentPanel?.update(
                        fs.readFileSync(htmlPath.fsPath, "utf8")
                    );

                    this.view.onDidReceiveMessage((message) => {
                        const msg = message;
                        if (msg.command === "status") {
                            this.viewer_message = message;
                        } else if (msg.command === "log") {
                            output.debug("Viewer.log: " + (msg.text ? msg.text : ""));
                        } else if (msg.command === "started") {
                            this.logo();
                            output.info("OCPCADController.start: Logo displayed ...");
                        } else {
                            output.info("OCPCADController.start: " + msg.text);
                        }
                        if (this.pythonListener !== undefined) {
                            output.debug("Sending message to python: " + message);
                            this.pythonListener.send(JSON.stringify(message));
                        } else {
                            this.notifyBackendMissing(msg);
                        }
                    });
                }
                output.debug("OCPCADController.start: Starting backend ...");
                await this.startBackend();
            }
        }
    }

    public startCommandServer(): Promise<boolean> {
        return new Promise<boolean>((resolve, reject) => {
            output.debug("OCPCADController.startCommandServer: Starting websocket server");
            const httpServer = createServer();
            const wss = new WebSocketServer({
                server: httpServer,
                maxPayload: 256 * 1024 * 1024
            });
            this.wss = wss;

            wss.on("connection", (socket) => {
                // output.info("OCPCADController.connection: Client connected");

                socket.on("message", (message) => {
                    try {
                        const raw_data = message.toString();
                        const messageType = raw_data.substring(0, 1);
                        output.debug(`OCPCADController.messages: message ${messageType} received`);
                        var data = message.toString().substring(2);
                        if (messageType === "C") {
                            var cmd = JSON.parse(data);
                            if (cmd === "status") {
                                socket.send(JSON.stringify(this.viewer_message));
                            } else if (cmd === "config") {
                                socket.send(JSON.stringify(this.config()));
                            } else if (cmd.type === "screenshot") {
                                this.view?.postMessage(JSON.stringify(cmd));
                            } else if (cmd.type === "set_relative_time") {
                                this.view?.postMessage(JSON.stringify(cmd));
                            }
                        } else if (messageType === "D") {
                            output.debug("OCPCADController.messages: Received a new model");
                            output.debug(
                                "OCPCADController.messages: config=" + JSON.stringify(getConfig())
                            );
                            this.view?.postMessage(data);
                            output.debug("OCPCADController.messages: Posted model to view");
                            if (this.splash) {
                                this.splash = false;
                            }
                        } else if (messageType === "S") {
                            output.debug("OCPCADController.messages: Received a config");
                            this.view?.postMessage(data);
                            output.debug("OCPCADController.messages: Posted config to view");
                        } else if (messageType === "L") {
                            this.pythonListener = socket;
                            this.backendHasRegistered = true;
                            output.debug(`OCPCADController.messages: ${data} registered`);
                        } else if (messageType === "B") {
                            if (this.pythonListener !== undefined) {
                                this.pythonListener.send(data);
                                socket.send(JSON.stringify({ ok: true }));
                                output.debug(
                                    "OCPCADController.messages: Model data sent to the backend"
                                );
                            } else {
                                socket.send(JSON.stringify({ ok: false, reason: "no_backend" }));
                                output.debug(
                                    "OCPCADController.messages: B-message dropped — no backend listener"
                                );
                            }
                        } else if (messageType === "R") {
                            this.view?.postMessage(data);
                            output.debug("OCPCADController.messages: Backend response received.");
                        }
                    } catch (error: any) {
                        output.error(`Server error: ${error.message}`);
                    }
                });

                socket.on("close", () => {
                    // output.info(
                    //     "OCPCADController.connection: Client disconnected"
                    // );
                    if (this.pythonListener === socket) {
                        this.pythonListener = undefined;
                        output.debug("Listener deregistered");
                    }
                });
            });

            wss.on("error", (error) => {
                output.error(
                    `OCPCADController.startCommandServer: : Server error: ${error.message}`
                );
            });

            httpServer.on("error", (error) => {
                output.error(
                    `OCPCADController.startCommandServer: : Server error: ${error.message}`
                );
                resolve(false);
            });

            httpServer.listen(this.port, () => {
                output.info(
                    `OCPCADController.startCommandServer: Server listening on port ${this.port}`
                );
                this.server = httpServer;
                resolve(true);
            });
        });
    }

    /**
     * Starts the python backend server
     */
    public async startBackend() {
        let cwd = getTempFolder();
        output.debug(`Backend.startBackend: Use folder ${cwd}`);

        let python = await getPythonPath();
        output.debug(`Backend.startBackend: Use python interpeter ${python}`);

        const shellConfig = getAutomationShellConfig();
        let pythonBackendTerminal = vscode.window.createTerminal({
            name: "OCP backend",
            cwd: cwd,
            // Prevent VS Code from restoring this terminal across window
            // reloads. Without this, the panel reappears with replayed
            // scrollback and a fresh shell, looking like a leftover backend.
            isTransient: true,
            ...shellConfig
        });
        pythonBackendTerminal.show();
        output.debug("Backend.startBackend: Terminal started");

        const delay = vscode.workspace.getConfiguration("OcpCadViewer.advanced")["terminalDelay"];
        const autohide =
            vscode.workspace.getConfiguration("OcpCadViewer.advanced")["autohideTerminal"];
        setTimeout(() => {
            output.debug(`Backend.startBackend: Starting Python backend with delay ${delay}`);
            const shellCommandPrefix =
                vscode.workspace.getConfiguration("OcpCadViewer.advanced")["shellCommandPrefix"];
            pythonBackendTerminal.sendText(
                `${shellCommandPrefix}"${python}" -m ocp_vscode --backend --port ${this.port}`
            );
            if (autohide) {
                pythonBackendTerminal.hide();
            }
            output.info("Backend.startBackend: Python backend running");
        }, delay);
        this.pythonBackendTerminal = pythonBackendTerminal;
    }

    private notifyBackendMissing(message: any) {
        const command = message?.command;

        // log/started are viewer-internal events; never relevant.
        if (command === "log" || command === "started") {
            return;
        }

        // Suppress until the backend has connected at least once: avoids the
        // false alarm during the startup window where the viewer is up but
        // the python backend hasn't yet sent its "L" registration.
        if (!this.backendHasRegistered) {
            return;
        }

        // `status` is dual-purpose: it carries camera updates (every frame
        // while the user pans/orbits) AND click/tool events (activeTool,
        // selectedShapeIDs). Only the latter is a backend request. Without
        // this discrimination we'd dialog-spam on every camera frame.
        if (command === "status") {
            const text = message?.text;
            const isClickIntent =
                text !== null &&
                typeof text === "object" &&
                ("activeTool" in text || "selectedShapeIDs" in text);
            if (!isClickIntent) {
                return;
            }
        }

        vscode.window.showErrorMessage(
            `OCP CAD Viewer: backend on port ${this.port} is not connected. ` +
                `Restart it in the OCP backend terminal, or reopen the viewer.`
        );
    }

    public async stopCommandServer(): Promise<boolean> {
        // Force-terminate live WS clients first; otherwise httpServer.close()
        // waits forever for long-lived connections to drain.
        if (this.wss !== undefined) {
            for (const client of this.wss.clients) {
                try {
                    client.terminate();
                } catch {
                    /* ignore */
                }
            }
            await new Promise<void>((resolve) => this.wss!.close(() => resolve()));
            this.wss = undefined;
        }

        if (this.server === undefined) {
            return false;
        }
        return new Promise<boolean>((resolve) => {
            this.server!.close((error) => {
                if (error) {
                    output.error(
                        `OCPCADController.stopCommandServer: Server error ${error.message}`
                    );
                    resolve(false);
                } else {
                    resolve(true);
                }
            });
            this.server = undefined;
        });
    }

    public async dispose() {
        if (!serverStarted) {
            return;
        }
        serverStarted = false;
        output.debug("OCPCADController.dispose");

        // Polite stop is best-effort; closing the WS below is what actually
        // unblocks Python's recv() and lets it exit cleanly via its
        // `except Exception: break` path in comms.py.
        try {
            this.pythonListener?.send('{"command": "stop"}');
        } catch {
            /* ignore */
        }

        await this.stopCommandServer();

        this.pythonBackendTerminal?.dispose();
        this.pythonBackendTerminal = undefined;

        await removeState(this.port);
        this.statusController.refresh("<none>");
        this.statusBarItem.hide();
        output.info("OCPCADController.dispose: Server is shut down");
    }
}
