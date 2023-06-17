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
import * as fs from "fs";
import * as path from "path";

export function getEditor() {
    const editor = vscode.window.activeTextEditor;
    // if (editor === undefined) {
    //     vscode.window.showWarningMessage("No editor window open or in focus");
    // }
    return editor;
}

export function getCurrentFilename() {
    const editor = getEditor();
    if (editor) {
        return editor.document.fileName;
    }
    return;
}

export function getCurrentFolder(): string {
    let filename = getCurrentFilename();
    if (filename !== undefined) {
        return path.dirname(filename);
    } else {
        return "";
    }
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
        document?: vscode.TextDocument
    ): Promise<string> {
        try {
            const extension =
                vscode.extensions.getExtension("ms-python.python");
            if (!extension) {
                return "python";
            }
            const usingNewInterpreterStorage =
                extension.packageJSON?.featureFlags?.usingNewInterpreterStorage;
            if (usingNewInterpreterStorage) {
                if (!extension.isActive) {
                    await extension.activate();
                }
                const pythonPath =
                    extension.exports.settings.getExecutionDetails()
                        .execCommand[0];
                return pythonPath;
            } else {
                return (
                    this.getConfiguration("python", document).get<string>(
                        "defaultInterpreterPath"
                    ) || ""
                );
            }
        } catch (error) {
            return "python";
        }
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

export function getPythonPath() {
    let editor = getEditor();
    return PythonPath.getPythonPath(editor?.document);
}

export function getPackageManager() {
    let cwd = getCurrentFolder();
    return fs.existsSync(path.join(cwd, "poetry.lock")) ? "poetry" : "pip";
}
