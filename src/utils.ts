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
import { PythonExtension } from '@vscode/python-extension';
import * as output from "./output";

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
export function getCurrentFilename(): string | undefined {
    const filename = getCurrentFileUri()?.fsPath;
    return filename;
}

export function getCurrentFolder(): string {
    let root: string | undefined;
    if (vscode.workspace?.workspaceFolders?.length === 1) {
        root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    } else {
        let filename = getCurrentFileUri();
        if (filename && filename.fsPath.endsWith(".py")) {
            root = vscode.workspace.getWorkspaceFolder(filename)?.uri.fsPath;
            if (root === undefined) {
                root = path.dirname(filename.fsPath);
            }
        } else {
            root = "";
        }
    }
    if (!root || root === "") {
        vscode.window.showErrorMessage("No workspace folder found. Open a Python file directly or in a workspace folder");
    }
    return root;
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
        const pythonApi: PythonExtension = await PythonExtension.api();
        const environmentPath = pythonApi.environments.getActiveEnvironmentPath();
        const environment = await pythonApi.environments.resolveEnvironment(environmentPath);
        if (environment != null) {
            output.debug(`PythonPath: '${environment.path}', environment: ${environment.environment?.type}, ${environment.environment?.name}`);
            return environment.path;
        } else {
            output.debug(`PythonPath: 'python', environment: DEFAULT`);
            vscode.window.showErrorMessage("No Python environment seems to be selected, falling back to default - might not work!");
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
