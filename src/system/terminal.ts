import * as vscode from "vscode";
import { spawn } from "child_process";
import * as output from "../output";
import { getCurrentFolder } from "../utils";

export class TerminalExecute {
    writeEmitter = new vscode.EventEmitter<string>();
    terminal: vscode.Terminal | undefined;
    workspaceFolder: string | undefined;
    errorMsg: string = "";
    stdout: string = "";
    terminalName = "OCP CAD Viewer Terminal";
    child: any = undefined;

    constructor(msg: string) {
        let pty = {
            onDidWrite: this.writeEmitter.event,
            open: () => this.writeEmitter.fire(msg + "\r\n\r\n"),
            close: () => {
                /* noop*/
            },
            handleInput: async (data: string) => {
                let charCode = data.charCodeAt(0);

                if (data === "\r") {
                    this.writeEmitter.fire("\r\n\r\n");
                } else if (charCode < 32) {
                    this.writeEmitter.fire(
                        `^${String.fromCharCode(charCode + 64)}`
                    );
                    if (charCode === 3) {
                        await this.killProcess();
                        this.writeEmitter.fire("\r\n");
                    }
                } else {
                    data = data.replace("\r", "\r\n");
                    this.writeEmitter.fire(`${data}`);
                }
            }
        };
        this.terminal = vscode.window.createTerminal({
            name: this.terminalName,
            pty
        });
        this.workspaceFolder = getCurrentFolder();

        vscode.window.onDidCloseTerminal(async t => {

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

    async execute(commands: string[]): Promise<string> {
        this.terminal?.show();
        this.stdout = "";
        return new Promise((resolve, reject) => {
            let command = commands.join("; ");
            this.child = spawn(command, {
                stdio: "pipe",
                shell: true,
                cwd: this.workspaceFolder
            });
            output.info(`Running ${command}`);
            this.child.stderr.setEncoding("utf8");
            this.child.stdout?.on("data", (data: string) => {
                this.stdout += data.toString();
                this.print(data.toString());
            });
            this.child.stderr?.on("data", (data: string) => {
                this.errorMsg = data.toString();
                this.print(this.errorMsg);
            });
            this.child.on("exit", (code: number, signal: any) => {
                if (code === 0) {
                    this.print(`Successfully executed '${command}`);
                    vscode.window.showInformationMessage(
                        `Successfully executed '${command}'`
                    );
                    output.info(`Successfully executed '${command}'`);
                    resolve(this.stdout);
                } else {
                    vscode.window.showErrorMessage(
                        `Failed to execute '${command}(${code})'`
                    );
                    output.error(`Failed to execute '${command}(${code})'`);
                    output.error(this.errorMsg);

                    reject(new Error(code?.toString()));
                }
            });
        });
    }

    print(msg: string) {
        for (let line of msg.split(/\r?\n/)) {
            this.writeEmitter.fire(line + "\r\n");
        }
    }
}
