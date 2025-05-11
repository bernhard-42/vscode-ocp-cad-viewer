import { execSync } from "child_process";
import * as output from "../output";
import { getCurrentFolder } from "../utils";

export function execute(cmd: string, needWorkspaceFolder: boolean = true) {
    let currentFolder = "";

    if (needWorkspaceFolder) {
        currentFolder = getCurrentFolder()[0];
    }
    if (currentFolder === "") {
        currentFolder = ".";
    }
    try {
        let result = execSync(cmd, { cwd: currentFolder }).toString();
        return result;
    } catch (error: any) {
        output.error(error.stderr.toString());
        throw Error(error.message);
    }
}

export function pythonVersion(python: string): string {
    try {
        return execSync(`"${python}" --version`).toString();
    } catch (error: any) {
        output.error(error.stderr.toString());
        return "";
    }
}
