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
exports.getPackageManager = exports.getPythonPath = exports.ipythonExtensionInstalled = exports.inquiry = exports.getCurrentFolder = exports.getCurrentFilename = exports.getEditor = void 0;
const vscode = require("vscode");
const fs = require("fs");
const path = require("path");
function getEditor() {
    const editor = vscode.window.activeTextEditor;
    // if (editor === undefined) {
    //     vscode.window.showWarningMessage("No editor window open or in focus");
    // }
    return editor;
}
exports.getEditor = getEditor;
function getCurrentFilename() {
    const editor = getEditor();
    if (editor) {
        return editor.document.fileName;
    }
    return;
}
exports.getCurrentFilename = getCurrentFilename;
function getCurrentFolder() {
    let filename = getCurrentFilename();
    if (filename !== undefined) {
        return path.dirname(filename);
    }
    else {
        return "";
    }
}
exports.getCurrentFolder = getCurrentFolder;
async function inquiry(placeholder, options) {
    const answer = await vscode.window.showQuickPick(options, {
        placeHolder: placeholder
    });
    return answer || "";
}
exports.inquiry = inquiry;
function ipythonExtensionInstalled() {
    return vscode.extensions.getExtension("HoangKimLai.ipython") !== undefined;
}
exports.ipythonExtensionInstalled = ipythonExtensionInstalled;
class PythonPath {
    static async getPythonPath(document) {
        try {
            const extension = vscode.extensions.getExtension("ms-python.python");
            if (!extension) {
                return "python";
            }
            const usingNewInterpreterStorage = extension.packageJSON?.featureFlags?.usingNewInterpreterStorage;
            if (usingNewInterpreterStorage) {
                if (!extension.isActive) {
                    await extension.activate();
                }
                const pythonPath = extension.exports.settings.getExecutionDetails()
                    .execCommand[0];
                return pythonPath;
            }
            else {
                return (this.getConfiguration("python", document).get("defaultInterpreterPath") || "");
            }
        }
        catch (error) {
            return "python";
        }
    }
    static getConfiguration(section, document) {
        if (document) {
            return vscode.workspace.getConfiguration(section, document.uri);
        }
        else {
            return vscode.workspace.getConfiguration(section);
        }
    }
}
function getPythonPath() {
    let editor = getEditor();
    return PythonPath.getPythonPath(editor?.document);
}
exports.getPythonPath = getPythonPath;
function getPackageManager() {
    let cwd = getCurrentFolder();
    return fs.existsSync(path.join(cwd, "poetry.lock")) ? "poetry" : "pip";
}
exports.getPackageManager = getPackageManager;
//# sourceMappingURL=utils.js.map