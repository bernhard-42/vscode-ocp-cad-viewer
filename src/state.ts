import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { lock, unlock } from "os-lock";
import * as output from "./output";

const CONFIG_FILE = path.join(os.homedir(), ".ocpvscode");
const LOCK_PATH = `${CONFIG_FILE}.lock`;

interface ServiceConfig {
    version: number;
    services: {
        [port: number]: string | null;
    };
}

export function getConfigFile(): string {
    return CONFIG_FILE;
}

async function atomicFileOperation<T>(
    fn: (data: ServiceConfig) => T
): Promise<T> {
    const lockFile = await fs.promises
        .open(LOCK_PATH, "a+")
        .catch(() => fs.promises.open(LOCK_PATH, "wx"));

    try {
        await lock(lockFile.fd, { exclusive: true });

        const data = await fs.promises
            .readFile(CONFIG_FILE, "utf8")
            .catch(() => '{"version":2,"services":{}}');

        let config: ServiceConfig;
        try {
            config = JSON.parse(data) as ServiceConfig;
        } catch (e) {
            config = { version: 2, services: {} };
        }
        if (config.version !== 2) {
            config = { version: 2, services: {} };
        }

        const result = fn(config);
        await fs.promises.writeFile(
            CONFIG_FILE,
            JSON.stringify(config, null, 2)
        );
        return result;
    } finally {
        await unlock(lockFile.fd);
        await lockFile.close();
    }
}

export async function updateState(port: number) {
    await atomicFileOperation((config) => {
        config.services[port] = "";
        return config;
    });
}

export async function removeState(port: number) {
    await atomicFileOperation((config) => {
        delete config.services[port];
        return config;
    });
}

export async function getConnctionFile(port: number): Promise<string> {
    var connectionFile = await atomicFileOperation(() => {
        output.info(`CONFIG_FILE ${CONFIG_FILE}`);
        let data;
        try {
            data = fs.readFileSync(CONFIG_FILE, "utf8");
        } catch (err) {
            data = '{"version":2,"services":{}}';
        }
        if (data == null) {
            output.error(data);
        }
        output.info(`data ${data}`);
        const config: ServiceConfig = JSON.parse(data);
        output.info(`config ${config}`);
        for (var port2 in config.services) {
            if (port2 == port.toString()) {
                return config.services[port2];
            }
        }
        return "";
    });
    output.info(`connectionFile ${connectionFile}`);
    return connectionFile || "";
}
