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
import * as output from "./output";
import * as path from "path";
import * as fs from "fs";
import * as os from "os";
import * as net from "net";

import { OCPCADController } from "./controller";
import { OCPCADViewer } from "./viewer";
import {
    createLibraryManager,
    installLib,
    Library,
    LibraryManagerProvider
} from "./libraryManager";
import { createStatusManager } from "./statusManager";
import { download } from "./examples";
import {
    getCurrentFolder,
    jupyterExtensionInstalled,
    isPortInUse,
    getPythonPath,
    closeOcpCadViewerTab,
    editorColumns,
    getEditorColumn,
    getViewColumn,
    getViewerColumn,
    focusGroup
} from "./utils";
import { version } from "./version";
import * as semver from "semver";
import { createDemoFile } from "./demo";

import {
    updateState,
    getConnctionFile,
    getConfigFile,
    removeOldLockfile
} from "./state";

function check_upgrade(libraryManager: LibraryManagerProvider) {
    const ocp_vscode_lib = libraryManager.installed["ocp_vscode"];

    if (ocp_vscode_lib) {
        if (semver.eq(ocp_vscode_lib[0], version)) {
            output.info(
                `extension.check_upgrade: ocp_vscode library version ${ocp_vscode_lib[0]} matches extension version ${version}`
            );
        } else if (semver.gt(ocp_vscode_lib[0], version)) {
            vscode.window.showErrorMessage(
                `ocp_vscode library version ${ocp_vscode_lib[0]} is newer than extension version ${version} ` +
                    `- update your OCP CAD Viewer extension`
            );
        } else {
            vscode.window
                .showInformationMessage(
                    `ocp_vscode library version ${ocp_vscode_lib[0]} is older than extension version ${version} ` +
                        `- update your ocp_vscode library in the Library Manager`,
                    "Cancel",
                    "Install"
                )
                .then(async (selection) => {
                    if (selection === "Install") {
                        await installLib(libraryManager, "ocp_vscode");
                    }
                });
        }
    } else {
        output.info(
            `extension.check_upgrade: ocp_vscode library not installed`
        );
    }
}

var viewerStarting = false;
var jupyterOpen = false;

function shouldAutostart(document: vscode.TextDocument) {
    const autostart = vscode.workspace.getConfiguration(
        "OcpCadViewer.advanced"
    )["autostart"];

    if (!autostart) {
        output.debug("extension.shouldAutostart: Autostart turned off");
        return false;
    }

    if (document.languageId === "python") {
        const autostartTriggers = vscode.workspace.getConfiguration(
            "OcpCadViewer.advanced"
        )["autostartTriggers"];
        for (var trigger of autostartTriggers) {
            if (document.getText().includes(trigger)) {
                output.debug(
                    `extension.shouldAutostart: Python file ${document.fileName} is valid for autostart`
                );
                return true;
            }
        }
    }
    output.debug(
        `extension.shouldAutostart: Python file ${document.fileName} is not valid for autostart`
    );
    return false;
}

async function openViewer(document: vscode.TextDocument, column: number = 1) {
    if (viewerStarting) {
        output.debug("extension.openViewer: Viewer is already starting");
        return;
    } else {
        viewerStarting = true;

        // ensure to reset stale flag
        setTimeout(() => {
            if (viewerStarting) {
                output.debug("Unsetting stale viewerStarting");
                viewerStarting = false;
            }
        }, 5000);

        output.debug(
            `extension.openViewer: Opening viewer for ${document.fileName}`
        );

        await vscode.commands.executeCommand(
            "ocpCadViewer.ocpCadViewer",
            document,
            column
        );
    }
}

async function conditionallyOpenViewer(document: vscode.TextDocument) {
    output.debug(
        `extension.conditionallyOpenViewer: Conditionally open viewer for ${document.fileName}`
    );
    if (shouldAutostart(document)) {
        const column = getEditorColumn(document);
        await openViewer(document, column);
    }
}

export async function activate(context: vscode.ExtensionContext) {
    output.open();
    let controller: OCPCADController;
    let isWatching = false;
    let port = 0;
    let lastPythonPath = "";

    // For migrations
    removeOldLockfile();

    output.debug("extension.activate: OCP CAD Viewer");

    let statusManager = createStatusManager();
    let libraryManager = createLibraryManager(statusManager);

    //	Statusbar

    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );

    const default_watch = vscode.workspace.getConfiguration(
        "OcpCadViewer.advanced"
    )["watchByDefault"];
    if (default_watch) {
        isWatching = true;
        statusBarItem.text = "OCP:on";
        statusBarItem.tooltip = "OCP CAD Viewer: Visual watch on";
    } else {
        isWatching = false;
        statusBarItem.text = "OCP:off";
        statusBarItem.tooltip = "OCP CAD Viewer: Visual watch off";
    }
    statusBarItem.command = "ocpCadViewer.toggleWatch";
    context.subscriptions.push(statusBarItem);

    await statusManager.refresh("");
    var python = await getPythonPath();
    await libraryManager.refresh(python);

    if (vscode.window.visibleTextEditors.length > 0) {
        for (var editor of vscode.window.visibleTextEditors) {
            output.debug(
                `extension.activate: Found open file ${editor.document.fileName}`
            );
            var started = false;
            const auto = shouldAutostart(editor.document);
            if (auto) {
                openViewer(editor.document, editor.viewColumn);
                started = true;
                break;
            }
            if (!started) {
                output.debug(
                    "extension.activate: Viewer not opened, since open Python file doesn't have the autostart trigger statements."
                );
            }
        }
    } else {
        output.debug("extension.activate: No open document visible.");
    }

    // Events

    vscode.workspace.onDidSaveTextDocument(
        async (document: vscode.TextDocument) => {
            output.debug(
                `extension.onDidSaveTextDocument: ${document.fileName}`
            );
            if (!controller || !controller.isStarted()) {
                conditionallyOpenViewer(document);
            }
        }
    );

    vscode.workspace.onDidOpenTextDocument(
        async (document: vscode.TextDocument) => {
            output.debug(
                `extension.onDidOpenTextDocument ${document.fileName}`
            );

            if (document.uri.scheme === "vscode-interactive-input") {
                if (jupyterOpen) {
                    return;
                }
                jupyterOpen = true;
                const viewerColumn = getViewerColumn();
                const jupyterColumn = getViewColumn(
                    document.fileName.replace(
                        path.sep + "InteractiveInput",
                        "Interactive"
                    )
                );
                if (viewerColumn === 0) return;

                focusGroup(jupyterColumn);
                for (
                    var c = 0;
                    c < Math.abs(viewerColumn - jupyterColumn);
                    c++
                ) {
                    await vscode.commands.executeCommand(
                        viewerColumn < jupyterColumn
                            ? "workbench.action.moveEditorToLeftGroup"
                            : "workbench.action.moveEditorToRightGroup"
                    );
                }

                await vscode.commands.executeCommand(
                    "workbench.action.moveEditorToBelowGroup"
                );

                const autohide = vscode.workspace.getConfiguration(
                    "OcpCadViewer.advanced"
                )["autohideTerminal"];
                if (autohide) {
                    vscode.commands.executeCommand(
                        "workbench.action.closePanel"
                    );
                }
                jupyterOpen = false;
            } else if (
                document.uri.scheme === "output" &&
                document.uri.path.endsWith("OCP CAD Viewer Log")
            ) {
                output.set_open(true);
            } else if (
                document.uri.scheme === "file" &&
                document.uri.path.endsWith("OCP CAD Viewer Log")
            ) {
                if (!controller || !controller.isStarted()) {
                    conditionallyOpenViewer(document);
                }
            }
        }
    );

    vscode.workspace.onDidCloseTextDocument(async (e: vscode.TextDocument) => {
        if (e.uri.scheme === "vscode-interactive-input") {
            if (controller?.port) {
                // remove the connection_file from the state
                await updateState(controller.port, false);
            }
        } else if (
            e.uri.scheme === "output" &&
            e.uri.path.endsWith("OCP CAD Viewer Log")
        ) {
            output.set_open(false);
        }
    });

    vscode.workspace.onDidChangeConfiguration(async (event: any) => {
        let affected = event.affectsConfiguration(
            "python.defaultInterpreterPath"
        );
        if (affected) {
            let pythonPath = await getPythonPath();
            output.debug(
                `extension.onDidChangeConfiguration: Python = ${pythonPath}`
            );
            if (lastPythonPath !== pythonPath) {
                lastPythonPath = pythonPath;
                libraryManager.refresh(pythonPath);
                controller.dispose();
                OCPCADViewer.currentPanel?.dispose();
            }
        }
    });

    vscode.window.onDidChangeActiveTextEditor(async (editor) => {
        output.debug(
            `extension.onDidChangeActiveTextEditor: ${editor?.document.fileName}`
        );
        if (
            editor &&
            editor.document.fileName &&
            editor.document.fileName.endsWith(".py")
        ) {
            if (!controller || !controller.isStarted()) {
                conditionallyOpenViewer(editor.document);
            }
        }
    });

    //	Commands

    context.subscriptions.push(
        vscode.commands.registerCommand("ocpCadViewer.toggleWatch", () => {
            if (statusBarItem.text === "OCP:on") {
                isWatching = false;
                statusBarItem.text = "OCP:off";
                statusBarItem.tooltip = "OCP CAD Viewer: Visual debug off";
            } else {
                isWatching = true;
                statusBarItem.text = "OCP:on";
                statusBarItem.tooltip = "OCP CAD Viewer: Visual debug on";
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.ocpCadViewer",
            async (
                document: vscode.TextDocument | undefined,
                column: number = vscode.ViewColumn.One
            ) => {
                output.debug(
                    `ocpCadViewer.ocpCadViewer: file=${document?.fileName}, column=${column}`
                );
                if (controller?.isStarted()) {
                    output.debug(
                        "ocpCadViewer.ocpCadViewer: Viewer already running"
                    );
                    return;
                }
                output.debug(
                    "ocpCadViewer.ocpCadViewer: Setting viewerStarting"
                );
                viewerStarting = true;

                function cleanup() {
                    viewerStarting = false;
                    output.debug(
                        "ocpCadViewer.ocpCadViewer: Unsetting viewerStarting"
                    );
                }

                output.debug(
                    `ocpCadViewer.ocpCadViewer: Start viewer for ${document?.fileName}`
                );
                let preset_port = false;

                try {
                    port = parseInt(process.env.OCP_PORT || "0", 10);
                    if (port === 0) {
                        port = vscode.workspace.getConfiguration(
                            "OcpCadViewer.advanced"
                        )["initialPort"];
                    } else {
                        preset_port = true;
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(
                        `Error occurred while parsing the port: ${process.env.OCP_PORT}`
                    );
                    cleanup();
                    return;
                }

                statusBarItem.show();

                var python = await getPythonPath(true);
                if (!libraryManager.installed.ocp_vscode) {
                    let reply =
                        (await vscode.window.showQuickPick(["yes", "no"], {
                            placeHolder: `OCP VS Code not found for "${python}". Select another Python interpreter?`
                        })) || "";
                    if (reply === "" || reply === "no") {
                        cleanup();
                        return;
                    } else {
                        await vscode.commands.executeCommand(
                            "python.setInterpreter"
                        );
                        python = await getPythonPath();
                    }
                }

                await statusManager.refresh("");
                await libraryManager.refresh(python);
                check_upgrade(libraryManager);

                if (preset_port) {
                    if (await isPortInUse(port)) {
                        vscode.window.showErrorMessage(
                            `ocpCadViewer.ocpCadViewer: OCP CAD Viewer could not start on port ${port}` +
                                "preconfigured in settings.json or env variable OCP_PORT"
                        );
                        cleanup();
                        return;
                    }
                    output.debug(
                        `ocpCadViewer.ocpCadViewer: Using preset port ${port}`
                    );
                } else {
                    while (port < 49152) {
                        if (await isPortInUse(port)) {
                            output.info(
                                `ocpCadViewer.ocpCadViewer: Port ${port} already in use`
                            );
                            port++;
                        } else {
                            output.debug(
                                `ocpCadViewer.ocpCadViewer: Using detected port ${port}`
                            );
                            break;
                        }
                    }
                }
                output.debug(
                    "ocpCadViewer.ocpCadViewer: Starting OCPCADController"
                );

                await closeOcpCadViewerTab();

                var newColumn = editorColumns();

                controller = new OCPCADController(
                    context,
                    port,
                    statusManager,
                    statusBarItem
                );

                await controller.start(
                    newColumn < 9 ? newColumn + 1 : newColumn
                );

                if (controller.isStarted()) {
                    var folder: string = "";
                    if (document) {
                        var isWorkspace: boolean;
                        vscode.window.showTextDocument(document, column);
                        [folder, isWorkspace] = getCurrentFolder();
                        output.debug(
                            `ocpCadViewer.ocpCadViewer: OCPCADController started with port ${port} ` +
                                `and folders: ${folder}, ${path.dirname(
                                    document.fileName
                                )}`
                        );
                        if (fs.existsSync(path.join(folder, ".ocp_vscode"))) {
                            vscode.window.showInformationMessage(
                                `Found .ocp_vscode in ${folder}. ` +
                                    `This file will be ignored and ${getConfigFile()} used instead!`
                            );
                        }
                    }
                    await updateState(port);
                    await statusManager.refresh(port.toString());

                    vscode.window.showInformationMessage(
                        `Using port ${port} and "show" should detect it automatically. ` +
                            `If not, call ocp_vscode's "set_port(${port})" in Python first`
                    );
                } else {
                    vscode.window.showErrorMessage(
                        `OCP CAD Viewer could not start on port ${port}`
                    );
                }
                cleanup();
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.installLibrary",
            async (library: Library) => {
                await installLib(libraryManager, library.label);
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.installVscodeSnippets",
            async () => {
                let snippets = vscode.workspace.getConfiguration(
                    "OcpCadViewer.snippets"
                )["dotVscodeSnippets"];
                let libs = Object.keys(snippets);
                let lib = await vscode.window.showQuickPick(libs, {
                    placeHolder: `Select the CAD library`
                });
                if (lib === undefined) {
                    return;
                }

                let dotVscode;
                let curFolder = getCurrentFolder();
                if (curFolder[1]) {
                    dotVscode = await vscode.window.showInputBox({
                        prompt: "Location of the .vscode folder",
                        value: `${curFolder[0]}/.vscode`
                    });
                } else {
                    return;
                }
                if (dotVscode === undefined) {
                    return;
                }

                let prefix = await vscode.window.showInputBox({
                    prompt: `Do you use a import alias (import ${lib} as xy)? Just press return if not.`,
                    placeHolder: `xy`
                });
                if (prefix === undefined) {
                    return;
                }
                if (prefix !== "" && prefix[prefix.length - 1] !== ".") {
                    prefix = prefix + ".";
                }

                let filename = path.join(dotVscode, `${lib}.code-snippets`);
                if (!fs.existsSync(dotVscode)) {
                    fs.mkdirSync(dotVscode, { recursive: true });
                }

                let snippetCode = JSON.stringify(snippets[lib], null, 2);
                snippetCode = snippetCode.replace(/\{prefix\}/g, prefix);
                fs.writeFileSync(filename, snippetCode);
                vscode.window.showInformationMessage(
                    `Installed snippets for ${lib} into ${dotVscode}`
                );
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.downloadExamples",
            async (library: Library) => {
                let root = getCurrentFolder()[0];
                if (root === "") {
                    vscode.window.showInformationMessage(
                        "First open a file in your project"
                    );
                    return;
                }
                const input = await vscode.window.showInputBox({
                    prompt: "Select target folder",
                    value: root
                });
                if (input === undefined) {
                    return;
                }
                await download(library.getParent(), input);
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.installJupyterExtension",
            async (library: Library) => {
                let reply =
                    (await vscode.window.showQuickPick(["yes", "no"], {
                        placeHolder: `Install the VS Code extension "ms-toolsai.jupyter"?`
                    })) || "";
                if (reply === "" || reply === "no") {
                    return;
                }

                vscode.window.showInformationMessage(
                    "Installing VS Code extension 'ms-toolsai.jupyter' ..."
                );

                await vscode.commands.executeCommand(
                    "workbench.extensions.installExtension",
                    "ms-toolsai.jupyter"
                );

                vscode.window.showInformationMessage(
                    "VS Code extension 'ms-toolsai.jupyter' installed"
                );
                statusManager.hasJupyterExtension = true;
                statusManager.refresh(statusManager.port);
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.installPythonModule",
            async () => {
                await installLib(libraryManager, "ocp_vscode");
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.pasteSnippet",
            (library: Library) => {
                libraryManager.pasteImport(library.label);
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("ocpCadViewer.refreshLibraries", () =>
            libraryManager.refresh()
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("ocpCadViewer.preferences", () =>
            vscode.commands.executeCommand(
                "workbench.action.openSettings",
                "OCP CAD Viewer"
            )
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("ocpCadViewer.output", () =>
            output.toggle()
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("ocpCadViewer.refreshStatus", () =>
            statusManager.refresh("")
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("ocpCadViewer.openViewer", async () => {
            await vscode.commands.executeCommand("ocpCadViewer.ocpCadViewer");
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.openConsole",
            async () => {
                output.debug("Trying to open Jupyter console");

                const connectionFile = await getConnctionFile(port);

                output.debug(`connectionFile: ${connectionFile}`);
                if (connectionFile) {
                    if (fs.existsSync(connectionFile)) {
                        let iopubPort = JSON.parse(
                            fs.readFileSync(connectionFile).toString()
                        )["iopub_port"];
                        output.debug(`iopubPort: ${iopubPort}`);
                        net.createConnection(iopubPort, "localhost")
                            .on("connect", () => {
                                let terminal = vscode.window.createTerminal({
                                    name: "Jupyter Console",
                                    location: vscode.TerminalLocation.Editor,
                                    shellPath:
                                        os.platform() === "win32"
                                            ? process.env.COMSPEC
                                            : undefined
                                });
                                terminal.show();
                                const delay = vscode.workspace.getConfiguration(
                                    "OcpCadViewer.advanced"
                                )["terminalDelay"];
                                setTimeout(async () => {
                                    var python = await getPythonPath(true);
                                    terminal.sendText(
                                        `${python} -m jupyter console --existing ${connectionFile}`
                                    );
                                    output.debug(
                                        `${python} -m jupyter --existing ${connectionFile} started`
                                    );
                                }, delay);
                            })
                            .on("error", function (e) {
                                vscode.window.showErrorMessage(
                                    `Kernel not running. Is the Interactive Window open and initialized?`
                                );
                            });
                    } else {
                        vscode.window.showErrorMessage(
                            `Connection file ${connectionFile} not found`
                        );
                    }
                } else {
                    vscode.window.showErrorMessage(
                        `Connection file not found. Is the Interactive Window open and initialized?`
                    );
                }
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            "ocpCadViewer.quickstart",
            async (arg) => {
                const conf = vscode.workspace.getConfiguration(
                    "OcpCadViewer.advanced"
                );
                let commands = conf["quickstartCommands"][arg];
                if (Object.keys(commands).includes("appleSilicon")) {
                    vscode.window.showErrorMessage(
                        "Your Quickstart is outdated.\nPlease update them in your settings.json ('OcpCadViewer.advanced.quickstartCommands')"
                    );
                    return;
                }
                let requiredPythonVersion = "";
                await installLib(
                    libraryManager,
                    "",
                    commands,
                    requiredPythonVersion,
                    async () => {
                        if (!jupyterExtensionInstalled()) {
                            await vscode.commands.executeCommand(
                                "ocpCadViewer.installJupyterExtension"
                            );
                        }
                        let reply =
                            (await vscode.window.showQuickPick(["yes", "no"], {
                                placeHolder: `Create a demo file ocp_vscode_demo.py?`
                            })) || "";
                        if (reply === "yes") {
                            createDemoFile(arg).then(async (b) => {
                                if (b) {
                                    await new Promise((resolve) =>
                                        setTimeout(resolve, 400)
                                    );
                                    await vscode.commands.executeCommand(
                                        "ocpCadViewer.ocpCadViewer"
                                    );
                                }
                            });
                        }
                    }
                );
            }
        )
    );

    vscode.debug.registerDebugAdapterTrackerFactory("*", {
        async createDebugAdapterTracker(session) {
            var expr = "";

            output.info("Debug session started");

            return {
                async onDidSendMessage(message) {
                    if (message.event === "stopped" && isWatching) {
                        // load the watch commands from the settings
                        expr = vscode.workspace.getConfiguration(
                            "OcpCadViewer.advanced"
                        )["watchCommands"];

                        // get the current stack trace, line number and frame id
                        const trace = await session.customRequest(
                            "stackTrace",
                            { threadId: 1 }
                        );
                        const frameId = trace.stackFrames[0].id;

                        // call the visual debug command
                        await session.customRequest("evaluate", {
                            expression: expr,
                            context: "repl",
                            frameId: frameId
                        });
                    } else if (message.event === "terminated") {
                        output.info("Debug session terminated");
                    }
                }
            };
        }
    });

    //	Register Web view

    vscode.window.registerWebviewPanelSerializer(OCPCADViewer.viewType, {
        async deserializeWebviewPanel(
            webviewPanel: vscode.WebviewPanel,
            state: any
        ) {
            OCPCADViewer.revive(webviewPanel, context.extensionUri);
        }
    });

    const extension = vscode.extensions.getExtension("ms-python.python")!;
    await extension.activate();
    extension?.exports.settings.onDidChangeExecutionDetails((event: any) => {
        let pythonPath =
            extension.exports.settings.getExecutionDetails().execCommand[0];
        lastPythonPath = pythonPath;
        libraryManager.refresh(pythonPath);
        controller?.dispose();
        OCPCADViewer.currentPanel?.dispose();
        statusBarItem.hide();
    });
}

export async function deactivate() {
    output.debug("OCP CAD Viewer extension deactivated");
    await OCPCADViewer.controller?.dispose();
    await OCPCADViewer.currentPanel?.dispose();
}
