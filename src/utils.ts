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
import { execute, find } from "./system/shell";

export function getEditor() {
    const editor = vscode.window.activeTextEditor;
    // if (editor === undefined) {
    //     vscode.window.showWarningMessage("No editor window open or in focus");
    // }
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
        // vscode.window.showErrorMessage("No workspace folder found. Open a folder and click to focus an editor window.");
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

export function isOcpVscodeEnv(python: String): boolean {
    let valid = false;
    try {
        // check whethre site-packages folder has ocp_vscode package
        var site = execute(
            `${python} -c "import sysconfig; print(sysconfig.get_paths()['purelib'], end='')"`
        ).toString();
        valid = find(site, "ocp_vscode*").length > 0;
    } catch (error) {
        valid = false;
    }
    return valid;
}

export function getPackageManager() {
    let cwd = getCurrentFolder()[0];
    return fs.existsSync(path.join(cwd, "poetry.lock")) ? "poetry" : "pip";
}

type AddressToCheck = { address: string; family: "IPv4" | "IPv6" };

const addresses: AddressToCheck[] = [
    { address: "0.0.0.0", family: "IPv4" }, // all IPv4
    { address: "127.0.0.1", family: "IPv4" }, // loopback IPv4
    { address: "::", family: "IPv6" }, // all IPv6
    { address: "::1", family: "IPv6" } // loopback IPv6
];

export async function isPortInUse(port: number): Promise<boolean> {
    const hosts = [
        "0.0.0.0", // all IPv4
        "::", // all IPv6
        "127.0.0.1", // loopback IPv4
        "::1" // loopback IPv6
    ];

    function checkPort(
        port: number,
        host: string,
        timeout = 1000
    ): Promise<boolean> {
        return new Promise<boolean>((resolve, reject) => {
            const server = net.createServer();

            server.once("error", (err: any) => {
                clearTimeout(timer);
                if (err.code === "EADDRINUSE") {
                    output.debug(`- in use on ${host}`);
                } else {
                    output.debug(
                        `Error ${err.code} checking port ${port} on ${host}`
                    );
                }
                resolve(true); // In any error case, we assume the port is in use
            });

            server.once("listening", () => {
                clearTimeout(timer);
                output.debug(`- free on ${host}`);
                server.close(() => {
                    resolve(false); // port is free
                });
            });

            const timer = setTimeout(() => {
                server.close();
                output.debug(
                    `- check timed out on ${host}, assuming port is free`
                );
                resolve(false); // Assume not in use if timeout
            }, timeout);

            server.listen(port, host);
        });
    }

    // Check all addresses in parallel, resolve true if any are in use
    output.debug(`Checking port ${port}:`);
    const checks = hosts.map((host) => checkPort(port, host));
    return Promise.all(checks).then((results) =>
        results.some((inUse) => inUse)
    );
}

export function getTempFolder() {
    const tempDirPath = os.tmpdir();
    return fs.realpathSync(tempDirPath);
}
