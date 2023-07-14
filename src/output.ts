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

const log = vscode.window.createOutputChannel("OCP CAD Viewer Log");
var is_open = false;

function getPrefix(logLevel?: string) {
    let timestamp = "";
    let level = "";
    if (logLevel) {
        const d = new Date();
        timestamp = `${d.toLocaleTimeString()}.${d
            .getMilliseconds()
            .toString()
            .padStart(3, "0")}} `;
        level = `${logLevel} `;
    }

    return `[${timestamp}${level}] `;
}

export function show() {
    if (is_open) {
        log.hide();
    } else {
        log.show(true);
    }
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

export function set_open(open: boolean) {
    is_open = open;
}
