"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TerminalExecute = void 0;
const vscode = require("vscode");
const child_process_1 = require("child_process");
const output = require("../output");
const utils_1 = require("../utils");
class TerminalExecute {
    constructor(msg) {
        this.writeEmitter = new vscode.EventEmitter();
        this.errorMsg = "";
        this.stdout = "";
        this.terminalName = "OCP CAD Viewer Terminal";
        this.child = undefined;
        let pty = {
            onDidWrite: this.writeEmitter.event,
            open: () => this.writeEmitter.fire(msg + "\r\n\r\n"),
            close: () => {
                /* noop*/
            },
            handleInput: async (data) => {
                let charCode = data.charCodeAt(0);
                if (data === "\r") {
                    this.writeEmitter.fire("\r\n\r\n");
                }
                else if (charCode < 32) {
                    this.writeEmitter.fire(`^${String.fromCharCode(charCode + 64)}`);
                    if (charCode === 3) {
                        await this.killProcess();
                        this.writeEmitter.fire("\r\n");
                    }
                }
                else {
                    data = data.replace("\r", "\r\n");
                    this.writeEmitter.fire(`${data}`);
                }
            }
        };
        this.terminal = vscode.window.createTerminal({
            name: this.terminalName,
            pty
        });
        this.workspaceFolder = (0, utils_1.getCurrentFolder)();
        vscode.window.onDidCloseTerminal(async (t) => {
            if (t.name === this.terminalName) {
                await this.killProcess();
                this.terminal = undefined;
                this.child = undefined;
            }
        });
    }
    async killProcess() {
        if (this.child && !this.child.killed) {
            this.child.kill();
            vscode.window.showInformationMessage("Process killed");
            output.info("Process killed");
            this.child = undefined;
        }
    }
    async execute(commands) {
        this.terminal?.show();
        this.stdout = "";
        return new Promise((resolve, reject) => {
            let command = commands.join("; ");
            this.child = (0, child_process_1.spawn)(command, {
                stdio: "pipe",
                shell: true,
                cwd: this.workspaceFolder
            });
            output.info(`Running ${command}`);
            this.child.stderr.setEncoding("utf8");
            this.child.stdout?.on("data", (data) => {
                this.stdout += data.toString();
                this.print(data.toString());
            });
            this.child.stderr?.on("data", (data) => {
                this.errorMsg = data.toString();
                this.print(this.errorMsg);
            });
            this.child.on("exit", (code, signal) => {
                if (code === 0) {
                    this.print(`Successfully executed '${command}`);
                    vscode.window.showInformationMessage(`Successfully executed '${command}'`);
                    output.info(`Successfully executed '${command}'`);
                    resolve(this.stdout);
                }
                else {
                    vscode.window.showErrorMessage(`Failed to execute '${command}(${code})'`);
                    output.error(`Failed to execute '${command}(${code})'`);
                    output.error(this.errorMsg);
                    reject(new Error(code?.toString()));
                }
            });
        });
    }
    print(msg) {
        for (let line of msg.split(/\r?\n/)) {
            this.writeEmitter.fire(line + "\r\n");
        }
    }
}
exports.TerminalExecute = TerminalExecute;
//# sourceMappingURL=terminal.js.map