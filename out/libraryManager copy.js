"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createLibraryManager = exports.Library = exports.LibraryManagerProvider = void 0;
const vscode = require("vscode");
const version_1 = require("./version");
const output = require("./output");
const utils_1 = require("./utils");
const shell_1 = require("./system/shell");
const path = require("path");
const URL = "https://github.com/bernhard-42/vscode-cadquery-viewer/releases/download";
class LibraryManagerProvider {
    constructor() {
        this.installCommands = {};
        this.importCommands = {};
        this.installed = {};
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.installCommands = vscode.workspace.getConfiguration("CadQueryViewer")["installCommands"];
        this.importCommands = vscode.workspace.getConfiguration("CadQueryViewer")["importCommands"];
    }
    async refresh(manager) {
        await this.getLibVersions(manager);
        this._onDidChangeTreeData.fire();
    }
    addLib(lib, manager, version, path) {
        this.installed[lib] = [manager, version, path];
    }
    getInstallLibs() {
        return Object.keys(this.installCommands);
    }
    getInstallLibMgrs(lib) {
        return Object.keys(this.installCommands[lib]);
    }
    getInstallLibCmds(lib, mgr) {
        let cmds = this.installCommands[lib][mgr];
        if (lib === "cq_vscode") {
            let substCmds = [];
            cmds.forEach((cmd) => {
                substCmds.push(cmd.replace("{cq_vscode_url}", `${URL}/v${version_1.version}/cq_vscode-${version_1.version}-py3-none-any.whl`));
            });
            return substCmds;
        }
        else {
            return cmds;
        }
    }
    async getLibVersions(manager) {
        let installLibs = this.getInstallLibs();
        let python = await (0, utils_1.getPythonPath)();
        let p = python.split(path.sep);
        if (manager === "") {
            manager = (0, utils_1.getPackageManager)();
        }
        this.installed = {};
        try {
            let command = "pip list --format json";
            if (manager === "pip") {
                command = `${python} -m ${command}`;
            }
            else {
                command = `poetry run ${command}`;
            }
            let allLibs = (0, shell_1.execute)(command);
            let libs = JSON.parse(allLibs);
            libs.forEach((lib) => {
                if (installLibs.includes(lib["name"].replace("-", "_"))) {
                    this.installed[lib["name"].replace("-", "_")] = [lib["version"], manager, p[p.length - 3]];
                }
            });
        }
        catch (error) {
            vscode.window.showErrorMessage(error.message);
        }
    }
    getImportLibs() {
        return Object.keys(this.importCommands);
    }
    getImportLibCmds(lib) {
        return this.importCommands[lib];
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element) {
            if (Object.keys(this.installed).includes(element.label)) {
                let version = this.installed[element.label][0];
                let manager = this.installed[element.label][1];
                let path = this.installed[element.label][2];
                let libs = [];
                libs.push(new Library("version", "", version, "", "", vscode.TreeItemCollapsibleState.None));
                libs.push(new Library("manager", "", "", manager, "", vscode.TreeItemCollapsibleState.None));
                libs.push(new Library("path", "", "", "", path, vscode.TreeItemCollapsibleState.None));
                return Promise.resolve(libs);
            }
            else {
                return Promise.resolve([]);
            }
        }
        else {
            let libs = [];
            this.getInstallLibs().forEach((lib) => {
                let flag = (Object.keys(this.installed).includes(lib)) ? "installed" : "n/a";
                let state = (flag === "n/a") ? vscode.TreeItemCollapsibleState.None : vscode.TreeItemCollapsibleState.Expanded;
                libs.push(new Library(lib, flag, "", "", "", state));
            });
            return Promise.resolve(libs);
        }
    }
}
exports.LibraryManagerProvider = LibraryManagerProvider;
class Library extends vscode.TreeItem {
    constructor(label, flag, version, manager, path, collapsibleState) {
        super(label, collapsibleState);
        this.label = label;
        this.flag = flag;
        this.version = version;
        this.manager = manager;
        this.path = path;
        this.collapsibleState = collapsibleState;
        this.contextValue = "info";
        if (version !== "") {
            this.tooltip = `${this.label}-${this.version}`;
            this.description = this.version;
        }
        else if (manager !== "") {
            this.tooltip = this.manager;
            this.description = this.manager;
        }
        else if (path !== "") {
            this.tooltip = this.path;
            this.description = this.path;
        }
        else {
            this.tooltip = `${this.label} is ${this.flag}`;
            this.description = this.flag;
            this.contextValue = "library";
        }
    }
}
exports.Library = Library;
function createLibraryManager() {
    const libraryManager = new LibraryManagerProvider();
    vscode.window.registerTreeDataProvider('cadquerySetup', libraryManager);
    vscode.window.createTreeView('cadquerySetup', { treeDataProvider: libraryManager });
    output.info("Successfully registered CadqueryViewer Library Manager");
    return libraryManager;
}
exports.createLibraryManager = createLibraryManager;
//# sourceMappingURL=libraryManager%20copy.js.map