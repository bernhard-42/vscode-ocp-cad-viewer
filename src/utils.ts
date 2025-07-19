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
import * as os from "os";
import * as net from "net";
import * as path from "path";
import { PythonExtension } from "@vscode/python-extension";
import * as output from "./output";

export function getEditor() {
    const editor = vscode.window.activeTextEditor;
    return editor;
}

export function getCurrentFileUri(): vscode.Uri | undefined {
    const editor = getEditor();
    if (editor) {
        return editor.document.uri;
    }
    return undefined;
}
export function getCurrentFilename(): vscode.Uri | undefined {
    const filename = getCurrentFileUri();
    return filename;
}

export function getCurrentFolder(
    filename: vscode.Uri | undefined = undefined
): [string, boolean] {
    let root: string | undefined = undefined;
    let isWorkspace = false;
    if (filename === undefined) {
        filename = getCurrentFilename();
    }

    if (
        vscode.workspace?.workspaceFolders &&
        vscode.workspace.workspaceFolders.length > 0
    ) {
        for (let i = 0; i < vscode.workspace.workspaceFolders.length; i++) {
            if (
                filename?.fsPath.startsWith(
                    vscode.workspace.workspaceFolders[i].uri.fsPath
                )
            ) {
                root = vscode.workspace.workspaceFolders[i].uri.fsPath;
                isWorkspace = true;
                break;
            }
        }
    }
    if (root === undefined) {
        if (filename?.fsPath.endsWith(".py")) {
            root = vscode.workspace.getWorkspaceFolder(filename)?.uri.fsPath;
            if (root === undefined) {
                root = path.dirname(filename.fsPath);
            }
        }
    }
    if (!root) {
        return ["", false];
    }
    return [root, isWorkspace];
}

export async function inquiry(placeholder: string, options: string[]) {
    const answer = await vscode.window.showQuickPick(options, {
        placeHolder: placeholder
    });
    return answer || "";
}

export function jupyterExtensionInstalled() {
    return vscode.extensions.getExtension("ms-toolsai.jupyter") !== undefined;
}

class PythonPath {
    public static async getPythonPath(
        document?: vscode.TextDocument,
        notify = false
    ): Promise<string> {
        const pythonApi: PythonExtension = await PythonExtension.api();
        const environmentPath =
            pythonApi.environments.getActiveEnvironmentPath();
        const environment = await pythonApi.environments.resolveEnvironment(
            environmentPath
        );
        if (environment != null) {
            if (notify) {
                output.info(
                    `PythonPath: '${environment.path}', environment: ${environment.environment?.type}, ${environment.environment?.name}`
                );
            }
            return environment.path;
        } else {
            output.debug(`PythonPath: 'python', environment: DEFAULT`);
            vscode.window.showErrorMessage(
                "No Python environment seems to be selected, falling back to default - might not work!"
            );
            return "python";
        }
    }

    public static async getPythonEnv(
        document?: vscode.TextDocument,
        notify = false
    ): Promise<string> {
        const pythonApi: PythonExtension = await PythonExtension.api();
        const environmentPath =
            pythonApi.environments.getActiveEnvironmentPath();
        const environment = await pythonApi.environments.resolveEnvironment(
            environmentPath
        );
        if (environment != null) {
            if (notify) {
                output.info(
                    `PythonEnv: ${environment.environment?.type}, '${environment.environment?.name}'`
                );
            }
            return environment.environment?.name || "unknown";
        }
        return "unknown";
    }

    public static getConfiguration(
        section?: string,
        document?: vscode.TextDocument
    ): vscode.WorkspaceConfiguration {
        if (document) {
            return vscode.workspace.getConfiguration(section, document.uri);
        } else {
            return vscode.workspace.getConfiguration(section);
        }
    }
}

export function getPythonPath(notify = false) {
    let editor = getEditor();
    return PythonPath.getPythonPath(editor?.document, notify);
}

export function getPythonEnv() {
    let editor = getEditor();
    return PythonPath.getPythonEnv(editor?.document);
}

export function getPackageManager() {
    let cwd = getCurrentFolder()[0];
    return fs.existsSync(path.join(cwd, "poetry.lock")) ? "poetry" : "pip";
}

export async function isPortInUse(port: number): Promise<boolean> {
    const hosts = [
        "0.0.0.0", // all IPv4
        "::", // all IPv6
        "127.0.0.1", // loopback IPv4
        "::1" // loopback IPv6
    ];

    async function checkPortWindows(
        port: number,
        host: string,
        timeout = 2000
    ): Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            // Connection test first, then bind test fallback
            const connectSocket = new net.Socket();
            let connectResolved = false;

            const connectCleanup = () => {
                if (!connectResolved) {
                    connectResolved = true;
                    try {
                        connectSocket.destroy();
                    } catch (e) {
                        // Ignore cleanup errors
                    }
                }
            };

            connectSocket.setTimeout(timeout);

            connectSocket.on('connect', () => {
                output.debug(`- definitely in use on ${host} (connection successful)`);
                connectCleanup();
                resolve(true);
            });

            connectSocket.on('timeout', () => {
                output.debug(`- connect timeout on ${host}, trying bind test`);
                connectCleanup();
                tryBindTest();
            });

            connectSocket.on('error', (err: any) => {
                connectCleanup();
                
                if (err.code === 'ECONNREFUSED') {
                    output.debug(`- free on ${host} (connection refused)`);
                    resolve(false);
                } else if (err.code === 'ECONNRESET') {
                    output.debug(`- likely in use on ${host} (connection reset)`);
                    resolve(true);
                } else {
                    output.debug(`- connect error ${err.code} on ${host}, trying bind test`);
                    tryBindTest();
                }
            });

            connectSocket.connect(port, host);

            function tryBindTest() {
                const server = net.createServer();
                let bindResolved = false;

                const bindCleanup = () => {
                    if (!bindResolved) {
                        bindResolved = true;
                        try {
                            server.close();
                        } catch (e) {
                            // Ignore cleanup errors
                        }
                    }
                };

                const bindTimer = setTimeout(() => {
                    output.debug(`- bind test timed out on ${host}, assuming in use`);
                    bindCleanup();
                    resolve(true);
                }, timeout);

                server.once("error", (err: any) => {
                    if (bindResolved) return;
                    bindCleanup();
                    clearTimeout(bindTimer);

                    if (err.code === "EADDRINUSE") {
                        output.debug(`- in use on ${host} (bind failed)`);
                        resolve(true);
                    } else {
                        output.debug(`- bind error ${err.code} on ${host}, assuming in use`);
                        resolve(true);
                    }
                });

                server.once("listening", () => {
                    if (bindResolved) return;
                    bindCleanup();
                    clearTimeout(bindTimer);
                    output.debug(`- free on ${host} (bind successful)`);
                    resolve(false);
                });

                server.listen({ 
                    port, 
                    host, 
                    ipv6Only: host === "::",
                    exclusive: true
                });
            }            
        });
    }

    async function checkPortUnix(
        port: number,
        host: string,
        timeout = 2000
    ): Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            const server = net.createServer();
            let resolved = false;

            const cleanup = () => {
                clearTimeout(timer);
                if (!resolved) {
                    resolved = true;
                    server.close();
                }
            };

            const timer = setTimeout(() => {
                output.debug(`- check timed out on ${host}, assuming free`);
                cleanup();
                resolve(false); // Assume not in use if timed out
            }, timeout);

            server.once("error", (err: any) => {
                if (resolved) return;
                cleanup();

                if (err.code === "EADDRINUSE") {
                    output.debug(`- in use on ${host}`);
                    resolve(true);
                } else {
                    output.debug(`Error ${err.code} checking ${host}:${port}`);
                    resolve(true); // Treat unknown errors as in-use
                }
            });

            server.once("listening", () => {
                if (resolved) return;
                cleanup();
                output.debug(`- free on ${host}`);
                server.close(() => resolve(false));
            });

            server.listen({ port, host, ipv6Only: host === "::" });
        });
    }

    output.debug(`Checking port ${port}:`);
    for (const host of hosts) {
        let inUse: boolean;
        if(os.platform() === 'win32') {
            inUse = await checkPortWindows(port, host);
        } else {
            inUse = await checkPortUnix(port, host);
        }
        if (inUse)  return true;
    }
    return false;
}

export function getTempFolder() {
    const tempDirPath = os.tmpdir();
    return fs.realpathSync(tempDirPath);
}

export async function closeOcpCadViewerTab() {
    for (const group of vscode.window.tabGroups.all) {
        for (const tab of group.tabs) {
            if (tab.label === "OCP CAD Viewer") {
                await vscode.window.tabGroups.close(tab);
                return;
            }
        }
    }
}

export function editorColumns(): number {
    const visibleEditors = vscode.window.visibleTextEditors || [];
    const visibleNotebookEditors = vscode.window.visibleNotebookEditors || [];
    var result = 1;

    for (const editor of visibleEditors) {
        if (editor.viewColumn !== undefined) {
            result = Math.max(result, editor.viewColumn);
        }
    }
    for (const editor of visibleNotebookEditors) {
        if (editor.viewColumn !== undefined) {
            result = Math.max(result, editor.viewColumn);
        }
    }
    output.debug(`Number of visible columns: ${result}`);
    return result;
}

export function getEditorColumn(document: vscode.TextDocument) {
    const editor = vscode.window.visibleTextEditors.find(
        (e) => e.document === document
    );
    return editor?.viewColumn ?? 1;
}

export function getViewColumn(label: string): number {
    const tabGroups = vscode.window.tabGroups.all;
    for (const group of tabGroups) {
        for (const tab of group.tabs) {
            if (tab.label === label) {
                return group.viewColumn;
            }
        }
    }
    return 0;
}

export function getViewerColumn(): number {
    return getViewColumn("OCP CAD Viewer");
}

export function focusGroup(n: number) {
    const commands = [
        "workbench.action.focusLastEditorGroup",
        "workbench.action.focusFirstEditorGroup",
        "workbench.action.focusSecondEditorGroup",
        "workbench.action.focusThirdEditorGroup",
        "workbench.action.focusFourthEditorGroup",
        "workbench.action.focusFifthEditorGroup",
        "workbench.action.focusSixthEditorGroup",
        "workbench.action.focusSeventhEditorGroup",
        "workbench.action.focusEightEditorGroup",
        "workbench.action.focusEditorGroup"
    ];
    vscode.commands.executeCommand(commands[n == 0 || n > 8 ? 0 : n]);
}
