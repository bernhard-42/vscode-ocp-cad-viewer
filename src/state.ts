import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { lock } from "proper-lockfile";
import * as output from "./output";

const CONFIG_FILE = path.join(os.homedir(), ".ocpvscode");
const LOCK_PATH = `${CONFIG_FILE}.lock`;
const EMPTY_CONFIG = '{"version":2,"services":{}}';

interface ServiceConfig {
    version: number;
    services: {
        [port: number]: string | null;
    };
}

/**
 * Retrieves the path or name of the configuration file.
 *
 * @returns {string} The configuration file path or name as a string.
 */
export function getConfigFile(): string {
    return CONFIG_FILE;
}

/**
 * Removes a legacy file-based lock if it exists.
 *
 * This function checks for the presence of a legacy lock file at `LOCK_PATH`.
 * If the file exists, it attempts to remove it and logs the migration process.
 * If the file does not exist, the function silently ignores the error.
 * Any other errors encountered during the process are logged, and the user is
 * advised to remove the lock file manually.
 *
 * @async
 * @returns {Promise<void>} Resolves when the migration check is complete.
 */
export async function removeOldLockfile() {
    try {
        const stats = await fs.promises.stat(LOCK_PATH);
        if (stats.isFile()) {
            output.info(`Migrating legacy file lock at ${LOCK_PATH}`);
            await fs.promises.unlink(LOCK_PATH);
            output.info("Successfully removed legacy file lock");
        }
    } catch (error: any) {
        if (error.code !== "ENOENT") {
            // Ignore "file not found" errors
            output.error(
                `Lock migration failed: ${error.message}.\nRemove ${LOCK_PATH} manually!`
            );
        }
    }
}

/**
 * Performs an atomic file operation on the configuration file, ensuring exclusive access using a directory-based lock.
 *
 * This function acquires a lock on the configuration file, reads and parses its contents as a `ServiceConfig` object,
 * and passes it to the provided callback function `fn`. After the callback is executed, the potentially modified
 * configuration is written back to the file. The lock is always released, and the lock directory is cleaned up.
 *
 * If the configuration file does not exist or is invalid, a default configuration is used.
 *
 * @template T The return type of the callback function.
 * @param fn - A function that receives the current `ServiceConfig` and returns a value of type `T`.
 * @returns A promise that resolves to the value returned by the callback function.
 * @throws Any error thrown during file operations or by the callback function.
 */
async function atomicFileOperation<T>(
    fn: (data: ServiceConfig) => T
): Promise<T> {
    // Ensure config file exists
    try {
        const stats = await fs.promises.stat(CONFIG_FILE);
    } catch (error: any) {
        if (error.code === "ENOENT") {
            try {
                // initialize config file
                await fs.promises.writeFile(CONFIG_FILE, EMPTY_CONFIG);
            } catch (error: any) {
                output.error(`Cannot initialize ${CONFIG_FILE}`);
            }
        } else {
            output.error(`Cannot access ${CONFIG_FILE}`);
        }
    }

    // Acquire proper directory-based lock
    const unlock = await lock(CONFIG_FILE, {
        retries: {
            retries: 5,
            factor: 1,
            minTimeout: 1000,
            maxTimeout: 5000
        }
    });
    try {
        // File operation logic
        const data = await fs.promises
            .readFile(CONFIG_FILE, "utf8")
            .catch(() => EMPTY_CONFIG);

        let config: ServiceConfig;
        try {
            config = JSON.parse(data) as ServiceConfig;
        } catch (e) {
            config = { version: 2, services: {} };
        }

        if (config.version !== 2) {
            config = { version: 2, services: {} };
        }
        const result = await fn(config);

        await fs.promises.writeFile(
            CONFIG_FILE,
            JSON.stringify(config, null, 2)
        );
        output.debug("~/.ocpconfig = " + JSON.stringify(config))
        return result;
    } finally {
        await unlock();
        // To be on the safe side: Cleanup empty lock directory
        await fs.promises.rmdir(LOCK_PATH).catch(() => {});
    }
}

/**
 * Get all port configurations from CONFIG_FILE.
 *
 * @returns All port configurations.
 */
export async function getConfig() {
    await atomicFileOperation((config) => {
        return config;
    });    
}

/**
 * Updates the application state by setting the service entry for the specified port to an empty string.
 * This operation is performed atomically to ensure consistency.
 *
 * @param port - The port number whose service entry should be updated.
 * @returns A promise that resolves when the state update is complete.
 */
export async function updateState(port: number, init=true) {
    await atomicFileOperation((config) => {
        if (init || config.services[port] != null) {
            config.services[port] = "";
        }
        return config;
    });
}

/**
 * Removes the state associated with the specified port from the configuration.
 *
 * @param port - The port number whose state should be removed.
 * @returns A promise that resolves when the state has been removed.
 */
export async function removeState(port: number) {
    await atomicFileOperation((config) => {
        delete config.services[`${port}`];
        return config;
    });
}

/**
 * Retrieves the connection file path associated with a given port from the service configuration.
 *
 * This function performs an atomic file operation to read the configuration file,
 * parses its contents, and searches for a service entry matching the specified port.
 * If found, it returns the corresponding connection file path; otherwise, it returns an empty string.
 *
 * @param port - The port number for which to retrieve the connection file path.
 * @returns A promise that resolves to the connection file path as a string, or an empty string if not found.
 */
export async function getConnctionFile(port: number): Promise<string> {
    var connectionFile = await atomicFileOperation(() => {
        output.info(`CONFIG_FILE ${CONFIG_FILE}`);
        let data;
        try {
            data = fs.readFileSync(CONFIG_FILE, "utf8");
        } catch (err) {
            data = EMPTY_CONFIG;
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
