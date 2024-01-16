import { execSync } from 'child_process';
import * as output from '../output';
import { getCurrentFolder } from '../utils';

function parsePipLibs(jsonData: string) {
    var data = JSON.parse(jsonData);
    let libraries = new Map<string, string>();
    Object.keys(data).forEach(key => {
        libraries.set(data[key]["name"].toLowerCase(), data[key]["version"]);
    });
    return libraries;
}

export function pipList(python: string): Map<string, string> {
    let workspaceFolder = getCurrentFolder()[0];
    try {
        let result = execSync(`"${python}" -m pip list --format json`, { cwd: workspaceFolder }).toString();
        return parsePipLibs(result);
    } catch (error: any) {
        output.error(error.stderr.toString());
        return new Map<string, string>();
    };
}

export function execute(cmd: string) {
    let currentFolder = getCurrentFolder()[0];
    if (currentFolder === "") {
        currentFolder = ".";
    }
    try {
        let result = execSync(cmd, { cwd: currentFolder }).toString();
        return result;
    } catch (error: any) {
        output.error(error.stderr.toString());
        throw Error(error.message);
    };
}

export function pythonVersion(python: string): string {
    try {
        return execSync(`"${python}" --version`).toString();
    } catch (error: any) {
        output.error(error.stderr.toString());
        return "";
    };
}
