/* eslint-disable @typescript-eslint/naming-convention */
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
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { IncomingMessage } from "http";
import * as AdmZip from "adm-zip";
import { https } from "follow-redirects";

export async function download(library: string, destination: string) {
    const timeout = 10000;
    const exampleDownloads = vscode.workspace.getConfiguration(
        "OcpCadViewer.advanced"
    )["exampleDownloads"];

    const archiveUrl = exampleDownloads[library]["zip"];
    const examplePath = exampleDownloads[library]["example_path"];
    const filename = path.basename(archiveUrl);
    const targetPath = path.join(destination, `${library}_examples`);

    let request = https.get(archiveUrl, (response: IncomingMessage) => {
        if (response.statusCode === 200) {
            const tempFolder = path.join(os.tmpdir(), "cadquery-viewer");
            fs.mkdtemp(tempFolder, (err, folder) => {
                if (err) {
                    vscode.window.showErrorMessage(
                        `Cannot create temp folder ${folder}`
                    );
                    return;
                }
                const downloadPath = path.join(folder, filename);
                var stream = fs.createWriteStream(downloadPath);
                response.pipe(stream);

                stream.on("finish", () => {
                    stream.close();
                    vscode.window.showInformationMessage(
                        `File "${archiveUrl}" downloaded successfully.`
                    );

                    const zip = new AdmZip(downloadPath);
                    try {
                        zip.extractAllTo(folder, true);
                    } catch (error) {
                        vscode.window.showErrorMessage(
                            `Unzipping "${downloadPath}" failed.`
                        );
                        return;
                    }
                    fs.rename(
                        path.join(folder, examplePath),
                        targetPath,
                        (err) => {
                            if (err) {
                                vscode.window.showErrorMessage(
                                    `Moving examples to "${targetPath}" failed.`
                                );
                            } else {
                                vscode.window.showInformationMessage(
                                    `Examples successfully downloaded to "${targetPath}".`
                                );
                            }
                        }
                    );
                });
            });
        } else {
            vscode.window.showErrorMessage(`Cannot download ${archiveUrl}`);
        }
    });

    request.setTimeout(timeout, function () {
        request.destroy();
    });

    request.on("error", function (e: any) {
        vscode.window.showErrorMessage(`Cannot download ${archiveUrl}`);
    });
}
