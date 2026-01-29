import { execSync } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";
import * as output from "../output";
import { getCurrentFolder } from "../utils";

export function getAutomationShellConfig(): {
    shellPath?: string;
    shellArgs?: string | string[];
} {
    const platform = os.platform();
    const key =
        platform === "win32"
            ? "windows"
            : platform === "darwin"
              ? "osx"
              : "linux";
    const config = vscode.workspace.getConfiguration("terminal.integrated");

    // 1. automationProfile — explicit automation override
    const automationProfile = config.get<{
        path?: string;
        args?: string | string[];
    }>(`automationProfile.${key}`);
    if (automationProfile?.path) {
        return {
            shellPath: automationProfile.path,
            shellArgs: automationProfile.args
        };
    }

    // 2. defaultProfile → profiles lookup
    const profileName = config.get<string>(`defaultProfile.${key}`);
    if (profileName) {
        const profiles = config.get<
            Record<string, { path?: string; args?: string | string[] }>
        >(`profiles.${key}`);
        const profile = profiles?.[profileName];
        if (profile?.path) {
            return { shellPath: profile.path, shellArgs: profile.args };
        }
    }

    // 3. OS default
    return {
        shellPath: platform === "win32" ? process.env.COMSPEC : undefined
    };
}

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

export function find(dir: string, pattern: string): string[] {
    const regex = new RegExp("^" + pattern.replace(/\*/g, ".*"));
    const result = fs
        .readdirSync(dir)
        .filter((filename) => regex.test(filename))
        .map((filename) => path.join(dir, filename));
    return result;
}

export function pythonVersion(python: string): string {
    try {
        return execSync(`"${python}" --version`).toString();
    } catch (error: any) {
        output.error(error.stderr.toString());
        return "";
    }
}
