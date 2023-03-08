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
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const output = require("./output");
const path = require("path");
const fs = require("fs");
const controller_1 = require("./controller");
const viewer_1 = require("./viewer");
const libraryManager_1 = require("./libraryManager");
const statusManager_1 = require("./statusManager");
const examples_1 = require("./examples");
const utils_1 = require("./utils");
async function activate(context) {
    let controller;
    let statusManager = (0, statusManager_1.createStatusManager)();
    statusManager.refresh("");
    let libraryManager = (0, libraryManager_1.createLibraryManager)(statusManager);
    libraryManager.refresh();
    //	Commands
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.ocpCadViewer", async () => {
        output.show();
        let useDefault = true;
        let port = 3939;
        while (true) {
            if (!useDefault) {
                let value = await vscode.window.showInputBox({
                    prompt: `Port ${port} in use, select another port`,
                    placeHolder: "1024 .. 49152",
                    validateInput: (text) => {
                        let port = Number(text);
                        if (Number.isNaN(port)) {
                            return "Not a valid number";
                        }
                        else if (port < 1024 || port > 49151) {
                            return "Number out of range";
                        }
                        return null;
                    }
                });
                if (value === undefined) {
                    output.error("Cancelling");
                    break;
                }
                port = Number(value);
            }
            const editor = vscode.window?.activeTextEditor?.document;
            if (editor === undefined) {
                output.error("No editor open");
                vscode.window.showErrorMessage("No editor open");
                break;
            }
            const column = vscode.window?.activeTextEditor?.viewColumn;
            controller = new controller_1.CadqueryController(context, port, statusManager);
            if (controller.isStarted()) {
                vscode.window.showTextDocument(editor, column);
                if (port !== 3939) {
                    vscode.window.showWarningMessage(`In Python first call ocp_vscode's "set_port(${port})"`);
                }
                statusManager.refresh(port.toString());
                output.show();
                output.debug("Command cadqueryViewer registered");
                controller.logo();
                break;
            }
            else {
                output.info(`Restarting ...`);
                useDefault = false;
            }
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.installLibrary", async (library) => {
        await (0, libraryManager_1.installLib)(libraryManager, library.label);
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.installVscodeSnippets", async () => {
        let snippets = vscode.workspace.getConfiguration("OcpCadViewer")["dotVscodeSnippets"];
        let libs = Object.keys(snippets);
        let lib = (await vscode.window.showQuickPick(libs, {
            placeHolder: `Select CAD library"?`
        }));
        if (lib === undefined) {
            return;
        }
        let dotVscode = await vscode.window.showInputBox({
            prompt: "Location of the .vscode folder",
            value: `${(0, utils_1.getCurrentFolder)()}/.vscode`
        });
        let prefix = await vscode.window.showInputBox({
            prompt: "Do you use a import alias, just press return if not?",
            placeHolder: `xy.`
        }) || "";
        if (prefix !== "" && prefix[prefix.length - 1] !== ".") {
            prefix = prefix + ".";
        }
        if (dotVscode === undefined) {
            return;
        }
        let filename = path.join(dotVscode, `${lib}.code-snippets`);
        if (!fs.existsSync(dotVscode)) {
            fs.mkdirSync(dotVscode, { recursive: true });
        }
        let snippetCode = JSON.stringify(snippets[lib], null, 2);
        snippetCode = snippetCode.replace(/\{prefix\}/g, prefix);
        fs.writeFileSync(filename, snippetCode);
        vscode.window.showInformationMessage(`Installed snippets for ${lib} into ${dotVscode}`);
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.downloadExamples", async (library) => {
        let root = (0, utils_1.getCurrentFolder)();
        if (root === "") {
            vscode.window.showInformationMessage("First open a file in your project");
            return;
        }
        const input = await vscode.window.showInputBox({ "prompt": "Select target folder", "value": root });
        if (input === undefined) {
            return;
        }
        await (0, examples_1.download)(library.getParent(), input);
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.installIPythonExtension", async (library) => {
        let reply = (await vscode.window.showQuickPick(["yes", "no"], {
            placeHolder: `Install the VS Code extension "HoangKimLai.ipython"?`
        })) || "";
        if (reply === "" || reply === "no") {
            return;
        }
        vscode.window.showInformationMessage("Installing VS Code extension 'HoangKimLai.ipython' ...");
        await vscode.commands.executeCommand("workbench.extensions.installExtension", "HoangKimLai.ipython");
        vscode.window.showInformationMessage("VS Code extension 'HoangKimLai.ipython' installed");
        statusManager.hasIpythonExtension = true;
        statusManager.refresh(statusManager.port);
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.installPythonModule", async () => {
        await (0, libraryManager_1.installLib)(libraryManager, "ocp_vscode");
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.pasteSnippet", (library) => {
        libraryManager.pasteImport(library.label);
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.ipythonRunCell", () => {
        vscode.commands.executeCommand("ipython.runCellAndMoveToNext");
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.refreshLibraries", () => libraryManager.refresh()));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.preferences", () => vscode.commands.executeCommand("workbench.action.openSettings", "OCP CAD Viewer")));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.refreshStatus", () => statusManager.refresh("")));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.openViewer", async () => {
        statusManager.openViewer();
    }));
    context.subscriptions.push(vscode.commands.registerCommand("ocpCadViewer.restartIpython", async () => {
        let terminals = vscode.window.terminals;
        terminals.forEach((terminal) => {
            if (terminal.name === "IPython") {
                terminal.dispose();
            }
        });
        if (!statusManager.hasIpythonExtension) {
            vscode.window.showErrorMessage("Extension 'HoangKimLai.ipython' not installed");
        }
        else {
            vscode.commands.executeCommand("ipython.createTerminal");
        }
    }));
    //	Register Web view
    vscode.window.registerWebviewPanelSerializer(viewer_1.CadqueryViewer.viewType, {
        async deserializeWebviewPanel(webviewPanel, state) {
            viewer_1.CadqueryViewer.revive(webviewPanel, context.extensionUri);
        }
    });
    vscode.workspace.onDidChangeConfiguration((event) => {
        let affected = event.affectsConfiguration("python.defaultInterpreterPath");
        if (affected) {
            let pythonPath = vscode.workspace.getConfiguration("python")["defaultInterpreterPath"];
            libraryManager.refresh(pythonPath);
            controller.dispose();
            viewer_1.CadqueryViewer.currentPanel?.dispose();
        }
    });
    const extension = vscode.extensions.getExtension('ms-python.python');
    await extension.activate();
    extension?.exports.settings.onDidChangeExecutionDetails((event) => {
        let pythonPath = extension.exports.settings.getExecutionDetails().execCommand[0];
        libraryManager.refresh(pythonPath);
        controller.dispose();
        viewer_1.CadqueryViewer.currentPanel?.dispose();
    });
}
exports.activate = activate;
function deactivate() {
    output.debug("OCP CAD Viewer extension deactivated");
    viewer_1.CadqueryViewer.currentPanel?.dispose();
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map