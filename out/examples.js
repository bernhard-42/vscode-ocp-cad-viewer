"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.download = void 0;
const vscode = require("vscode");
const fs = require("fs");
const os = require("os");
const path = require("path");
const AdmZip = require("adm-zip");
const follow_redirects_1 = require("follow-redirects");
async function download(library, destination) {
    const timeout = 10000;
    const exampleDownloads = vscode.workspace.getConfiguration("OcpCadViewer")["exampleDownloads"];
    const archiveUrl = exampleDownloads[library]["zip"];
    const examplePath = exampleDownloads[library]["example_path"];
    const filename = path.basename(archiveUrl);
    const targetPath = path.join(destination, `${library}_examples`);
    let request = follow_redirects_1.https.get(archiveUrl, (response) => {
        if (response.statusCode === 200) {
            const tempFolder = path.join(os.tmpdir(), "cadquery-viewer");
            fs.mkdtemp(tempFolder, (err, folder) => {
                if (err) {
                    vscode.window.showErrorMessage(`Cannot create temp folder ${folder}`);
                    return;
                }
                const downloadPath = path.join(folder, filename);
                var stream = fs.createWriteStream(downloadPath);
                response.pipe(stream);
                stream.on("finish", () => {
                    stream.close();
                    vscode.window.showInformationMessage(`File "${archiveUrl}" downloaded successfully.`);
                    const zip = new AdmZip(downloadPath);
                    try {
                        zip.extractAllTo(folder, true);
                    }
                    catch (error) {
                        vscode.window.showErrorMessage(`Unzipping "${downloadPath}" failed.`);
                        return;
                    }
                    fs.rename(path.join(folder, examplePath), targetPath, (err) => {
                        if (err) {
                            vscode.window.showErrorMessage(`Moving examples to "${targetPath}" failed.`);
                        }
                        else {
                            vscode.window.showInformationMessage(`Examples successfully downloaded to "${targetPath}".`);
                        }
                    });
                });
            });
        }
        else {
            vscode.window.showErrorMessage(`Cannot download ${archiveUrl}`);
        }
    });
    request.setTimeout(timeout, function () {
        request.destroy();
    });
    request.on("error", function (e) {
        vscode.window.showErrorMessage(`Cannot download ${archiveUrl}`);
    });
}
exports.download = download;
//# sourceMappingURL=examples.js.map