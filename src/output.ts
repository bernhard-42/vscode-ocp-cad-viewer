/*
   Copyright 2025 Bernhard Walter
  
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

var log: vscode.OutputChannel;
var is_open = false;

function getFormattedTimestamp(): string {
    const now = new Date();

    const pad = (n: number, z: number = 2) => n.toString().padStart(z, "0");
    const year = now.getFullYear();
    const month = pad(now.getMonth() + 1); // Months are 0-based
    const day = pad(now.getDate());
    const hours = pad(now.getHours());
    const minutes = pad(now.getMinutes());
    const seconds = pad(now.getSeconds());
    const milliseconds = pad(now.getMilliseconds(), 3);

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}`;
}

function getPrefix(logLevel?: string) {
    let timestamp = "";
    let level = "";
    if (logLevel) {
        timestamp = getFormattedTimestamp();
        level = `${logLevel.toLocaleLowerCase()}`;
    }

    return `${timestamp} [${level}] `;
}

export function open() {
    log = vscode.window.createOutputChannel("OCP CAD Viewer Log", "log");
}

export function hide() {
    log.hide();
    is_open = false;
}

export function show() {
    log.show(true);
    is_open = true;
}

export function toggle() {
    is_open ? hide() : show();
}

export function info(msg: string) {
    const prefix = getPrefix("INFO ");
    log.appendLine(prefix + msg);
}

export function error(msg: string) {
    const prefix = getPrefix("ERROR");
    log.appendLine(prefix + msg);
}

export function debug(msg: string) {
    const prefix = getPrefix("DEBUG");
    log.appendLine(prefix + msg);
}
