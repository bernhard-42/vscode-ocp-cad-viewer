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
exports.debug = exports.error = exports.info = exports.show = void 0;
const vscode = require("vscode");
const log = vscode.window.createOutputChannel("OCP CAD Viewer Log");
function getPrefix(logLevel) {
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
function show() {
    log.show(true);
}
exports.show = show;
function info(msg) {
    const prefix = getPrefix("INFO ");
    log.appendLine(prefix + msg);
}
exports.info = info;
function error(msg) {
    const prefix = getPrefix("ERROR");
    log.appendLine(prefix + msg);
}
exports.error = error;
function debug(msg) {
    const prefix = getPrefix("DEBUG");
    log.appendLine(prefix + msg);
}
exports.debug = debug;
//# sourceMappingURL=output.js.map