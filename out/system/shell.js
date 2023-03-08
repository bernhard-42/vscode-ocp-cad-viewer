"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.pythonVersion = exports.execute = exports.pipList = void 0;
const child_process_1 = require("child_process");
const output = require("../output");
const utils_1 = require("../utils");
function parsePipLibs(jsonData) {
    var data = JSON.parse(jsonData);
    let libraries = new Map();
    Object.keys(data).forEach(key => {
        libraries.set(data[key]["name"].toLowerCase(), data[key]["version"]);
    });
    return libraries;
}
function pipList(python) {
    let workspaceFolder = (0, utils_1.getCurrentFolder)();
    try {
        let result = (0, child_process_1.execSync)(`${python} -m pip list --format json`, { cwd: workspaceFolder }).toString();
        return parsePipLibs(result);
    }
    catch (error) {
        output.error(error.stderr.toString());
        return new Map();
    }
    ;
}
exports.pipList = pipList;
function execute(cmd) {
    let currentFolder = (0, utils_1.getCurrentFolder)();
    if (currentFolder === "") {
        currentFolder = ".";
    }
    try {
        let result = (0, child_process_1.execSync)(cmd, { cwd: currentFolder }).toString();
        return result;
    }
    catch (error) {
        output.error(error.stderr.toString());
        throw Error(error.message);
    }
    ;
}
exports.execute = execute;
function pythonVersion(python) {
    try {
        return (0, child_process_1.execSync)(`${python} --version`).toString();
    }
    catch (error) {
        output.error(error.stderr.toString());
        return "";
    }
    ;
}
exports.pythonVersion = pythonVersion;
//# sourceMappingURL=shell.js.map