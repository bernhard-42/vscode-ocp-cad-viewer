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
exports.createLibraryManager = exports.Library = exports.LibraryManagerProvider = exports.installLib = void 0;
const fs = require("fs");
const process = require("process");
const path = require("path");
const vscode = require("vscode");
const version_1 = require("./version");
const output = require("./output");
const utils_1 = require("./utils");
const shell_1 = require("./system/shell");
const terminal_1 = require("./system/terminal");
const URL = "https://github.com/bernhard-42/vscode-cadquery-viewer/releases/download";
function sanitize(lib) {
    return lib.replace("-", "_");
}
async function installLib(libraryManager, library) {
    let managers = libraryManager.getInstallLibMgrs(library);
    let manager;
    if (managers.length > 1) {
        manager = await (0, utils_1.inquiry)(`Select package manager to install "${library}"`, managers);
        if (manager === "") {
            return;
        }
    }
    else {
        manager = managers[0];
    }
    let python = await (0, utils_1.getPythonPath)();
    let reply = (await vscode.window.showQuickPick(["yes", "no"], {
        placeHolder: `Use python interpreter "${python}"?`
    })) || "";
    if (reply === "" || reply === "no") {
        return;
    }
    python = await (0, utils_1.getPythonPath)();
    if (python === "python") {
        vscode.window.showErrorMessage("Select Python Interpreter first!");
        return;
    }
    let commands = await libraryManager.getInstallLibCmds(library, manager);
    if (libraryManager.terminal?.terminal === undefined) {
        libraryManager.terminal = new terminal_1.TerminalExecute(`Installing ${commands.join(";")} ... `);
    }
    await libraryManager.terminal.execute(commands);
    libraryManager.refresh();
    if (["cadquery", "build123d"].includes(library)) {
        vscode.window.showInformationMessage(`Depending on your os, the first import of ${library} can take several seconds`);
    }
}
exports.installLib = installLib;
class LibraryManagerProvider {
    constructor(statusManger) {
        this.installCommands = {};
        this.exampleDownloads = {};
        this.codeSnippets = {};
        this.installed = {};
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.statusManager = statusManger;
        this.readConfig();
    }
    readConfig() {
        this.installCommands =
            vscode.workspace.getConfiguration("OcpCadViewer")["installCommands"];
        this.codeSnippets =
            vscode.workspace.getConfiguration("OcpCadViewer")["codeSnippets"];
        this.exampleDownloads =
            vscode.workspace.getConfiguration("OcpCadViewer")["exampleDownloads"];
    }
    async refresh(pythonPath = undefined) {
        this.readConfig();
        await this.findInstalledLibraries(pythonPath);
        this._onDidChangeTreeData.fire();
    }
    addLib(lib, manager, version, path) {
        this.installed[lib] = [manager, version, path];
    }
    getInstallLibs() {
        return Object.keys(this.installCommands).sort();
    }
    getInstallLibMgrs(lib) {
        let managers = Object.keys(this.installCommands[lib]);
        let filteredManagers = [];
        managers.forEach((manager) => {
            const cwd = (0, utils_1.getCurrentFolder)();
            const poetryLock = fs.existsSync(path.join(cwd, "poetry.lock"));
            if (manager === "poetry" && !poetryLock) {
                // ignore
            }
            else {
                filteredManagers.push(manager);
            }
        });
        return filteredManagers;
    }
    async getInstallLibCmds(lib, manager) {
        let commands = this.installCommands[lib][manager];
        let python = await (0, utils_1.getPythonPath)();
        let substCmds = [];
        commands.forEach((command) => {
            if (lib === "ocp_vscode") {
                command = command.replace("{ocp_vscode_version}", version_1.version);
            }
            ;
            command = command.replace("{python}", python);
            if (manager === "pip" && command.indexOf("{unset_conda}") >= 0) {
                command = command.replace("{unset_conda}", "");
                if (process.platform === "win32") {
                    let tempPath = process.env["TEMP"] || ".";
                    let code = "set CONDA_PREFIX_1=\n";
                    code = code + command;
                    command = path.join(tempPath, "__inst_with_pip__.cmd");
                    fs.writeFileSync(command, code);
                    output.info(`created batch file ${command} with commands:`);
                    output.info("\n" + code);
                }
                else {
                    command = "env -u CONDA_PREFIX_1 " + command;
                }
                substCmds.push(command);
            }
            else if (manager === "conda" || manager === "mamba") {
                let paths = python.split(path.sep);
                let env = "";
                if (process.platform === "win32") {
                    env = paths[paths.length - 2];
                }
                else {
                    env = paths[paths.length - 3];
                }
                substCmds.push(command.replace("{conda_env}", env));
            }
            else {
                substCmds.push(command);
            }
        });
        return substCmds;
    }
    async findInstalledLibraries(pythonPath) {
        let installLibs = this.getInstallLibs();
        let python;
        if (pythonPath === undefined) {
            python = await (0, utils_1.getPythonPath)();
        }
        else {
            python = pythonPath;
        }
        this.installed = {};
        try {
            let command = `${python} -m pip list -v --format json`;
            let allLibs = (0, shell_1.execute)(command);
            let libs = JSON.parse(allLibs);
            libs.forEach((lib) => {
                if (installLibs.includes(sanitize(lib["name"]))) {
                    let editablePath = lib["editable_project_location"];
                    this.installed[sanitize(lib["name"])] = [
                        lib["version"],
                        lib["installer"],
                        editablePath === undefined
                            ? lib["location"]
                            : editablePath,
                        editablePath !== undefined
                    ];
                }
            });
        }
        catch (error) {
            vscode.window.showErrorMessage(error.message);
        }
    }
    getImportLibs() {
        return Object.keys(this.codeSnippets);
    }
    getImportLibCmds(lib) {
        return this.codeSnippets[lib];
    }
    pasteImport(library) {
        const editor = (0, utils_1.getEditor)();
        if (editor !== undefined) {
            if ((library === "ocp_vscode") && (this.statusManager.getPort() === "")) {
                vscode.window.showErrorMessage("OCP CAD Viewer not running");
            }
            else {
                let importCmd = Object.assign([], this.codeSnippets[library]);
                if (library === "ocp_vscode") {
                    importCmd.push(`set_port(${this.statusManager.getPort()})`);
                }
                let snippet = new vscode.SnippetString(importCmd.join("\n") + "\n");
                editor?.insertSnippet(snippet);
            }
        }
        else {
            vscode.window.showErrorMessage("No editor open");
        }
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element) {
            if (Object.keys(this.installed).includes(element.label)) {
                let editable = this.installed[element.label][3];
                let manager = editable
                    ? "n/a"
                    : this.installed[element.label][1];
                let location = this.installed[element.label][2];
                let p = location.split(path.sep);
                let env = editable ? location : p[p.length - 4];
                let libs = [];
                libs.push(new Library("installer", { "installer": manager }, vscode.TreeItemCollapsibleState.None));
                libs.push(new Library("environment", { "location": location, "env": env }, vscode.TreeItemCollapsibleState.None));
                libs.push(new Library("editable", { "editable": editable }, vscode.TreeItemCollapsibleState.None));
                if (this.exampleDownloads[element.label]) {
                    libs.push(new Library("examples", { "examples": "", "parent": element.label }, vscode.TreeItemCollapsibleState.None));
                }
                return Promise.resolve(libs);
            }
            else {
                return Promise.resolve([]);
            }
        }
        else {
            let libs = [];
            this.getInstallLibs().forEach((lib) => {
                let installed = Object.keys(this.installed).includes(lib);
                let version = installed
                    ? this.installed[sanitize(lib)][0]
                    : "n/a";
                let state = installed
                    ? vscode.TreeItemCollapsibleState.Expanded
                    : vscode.TreeItemCollapsibleState.None;
                libs.push(new Library(lib, { "version": version }, state));
                if (lib === "ocp_vscode") {
                    this.statusManager.installed = version !== "n/a";
                    this.statusManager.setLibraries(Object.keys(this.installed));
                    this.statusManager.refresh(this.statusManager.getPort());
                }
            });
            return Promise.resolve(libs);
        }
    }
}
exports.LibraryManagerProvider = LibraryManagerProvider;
class Library extends vscode.TreeItem {
    constructor(label, options, collapsibleState) {
        super(label, collapsibleState);
        this.label = label;
        this.options = options;
        this.collapsibleState = collapsibleState;
        if (options.version !== undefined) {
            this.tooltip = `${this.label}-${options.version}`;
            this.description = options.version;
            this.contextValue = "library";
        }
        else if (options.installer !== undefined) {
            this.tooltip = options.installer;
            this.description = options.installer;
        }
        else if (options.location !== undefined) {
            this.tooltip = options.location;
            this.description = options.env;
        }
        else if (options.editable !== undefined) {
            this.tooltip = options.editable ? "editable" : "non-editable";
            this.description = options.editable.toString();
        }
        else if (options.examples !== undefined) {
            this.tooltip = "Download examples from github";
            this.description = "(download only)";
            this.contextValue = "examples";
        }
    }
    getParent() {
        return this.options.parent;
    }
}
exports.Library = Library;
function createLibraryManager(statusManager) {
    const libraryManager = new LibraryManagerProvider(statusManager);
    vscode.window.registerTreeDataProvider("ocpCadSetup", libraryManager);
    vscode.window.createTreeView("ocpCadSetup", {
        treeDataProvider: libraryManager
    });
    output.info("Successfully registered CadqueryViewer Library Manager");
    return libraryManager;
}
exports.createLibraryManager = createLibraryManager;
//# sourceMappingURL=libraryManager.js.map