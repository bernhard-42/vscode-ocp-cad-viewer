/*
state uses "poor man's locking": nodejs does not support fcntl (POSIX) or 
LockFileEx (Windows) locking. This module implements a simple locking 
mechanism for nodejs and Python leveraging "mkdir" to create locks. 

Ideas are taken from the node js library "proper-lockfile"
(https://github.com/moxystudio/node-proper-lockfile)
*/

import { promises as fs } from "fs";
import * as os from "os";
import * as path from "path";
import * as output from "./output";

const STALE_DURATION_MS = 3000; // 3 seconds
const RETRIES = 7;
const INTERVAL_MS = 500; // INTERVAL_MS * RETRIES > STALE_DURATION
const CONFIG_FILE = "~/.ocpvscode"


export async function getConfigFile(): Promise<string> {
    return await resolvePath(CONFIG_FILE);
}

function rtrim(file: string, c: string): string {
    while (file.endsWith(c)) {
        file = file.substring(0, file.length - 1);
    }
    return file;
}

function sleep(msec: number) {
    return new Promise((resolve, _reject) => {
        setTimeout(() => {
            resolve(0);
        }, msec);
    });
}

function getLockFile(file: string): string {
    return `${file}.lock`;
}

async function resolvePath(file: string): Promise<string> {
    if (file.startsWith("~")) {
        const homedir = os.homedir();
        file = path.join(homedir, file.substring(1));
    }
    try {
        return await fs.realpath(file);
    } catch (error) {
        return file;
    }
}

function isLockStale(mtime: number, staleMilliseconds: number): boolean {
    return Date.now() - mtime > staleMilliseconds;
}

async function removeLock(lockfile: string) {
    try {
        await fs.rmdir(lockfile);
        output.debug(`Lockfile ${lockfile} removed`);
    } catch (error: any) {
        if (error.code === "ENOENT") {
            output.debug(`Lock file ${lockfile} not found`);
        } else {
            throw new Error(`Unable to remove lock file ${lockfile}`);
        }
    }
}

async function acquireLock(
    lockfile: string,
    retries: number = RETRIES,
    intervalMs: number = INTERVAL_MS,
    staleDurationMs: number = STALE_DURATION_MS,
    retry: number = 0
) {
    try {
        await fs.mkdir(lockfile);
        output.debug(`Lock ${lockfile} acquired`);
    } catch (error: any) {
        if (error.code === "EEXIST") {
            output.debug(`Lock file ${lockfile} already exists`);
            const stat = await fs.stat(lockfile);
            if (isLockStale(stat.mtimeMs, staleDurationMs)) {
                output.debug(`Lock file ${lockfile} is stale`);
                try {
                    // assume the lockfile is stale and simply remove it
                    await removeLock(lockfile);
                } catch (error) {
                    // lock seems to be just removed, which is ok
                }
                // try to acquire the lock again
                await acquireLock(
                    lockfile,
                    retries,
                    intervalMs,
                    staleDurationMs,
                    retry + 1
                );
            } else {
                if (retry < retries) {
                    await sleep(intervalMs);
                    output.debug("Retrying to acquire lock");
                    await acquireLock(
                        lockfile,
                        retries,
                        intervalMs,
                        staleDurationMs,
                        retry + 1
                    );
                } else {
                    throw new Error(
                        `Unable to acquire lock for file ${lockfile} after ${retries} retries`
                    );
                }
            }
        } else {
            output.debug(error);
        }
    }
}

async function lock(file: string, retries: number = RETRIES, intervalMs: number = INTERVAL_MS) {
    const lockfile = getLockFile(file);
    await acquireLock(lockfile, retries, intervalMs);
}

async function unlock(file: string) {
    const lockfile = getLockFile(file);
    await removeLock(lockfile);
}

export async function updateState(
    port: number, key: string | null, value: string | Array<string> | null, initialize: boolean = false
) {
    let data;
    let fh: fs.FileHandle;

    const config_file = await resolvePath("~/.ocpvscode");
    await lock(config_file);

    try {
        fh = await fs.open(config_file, "r+");
        data = await fh.readFile({ encoding: "utf8" });
        if (data.length > 0) {
            data = JSON.parse(data);
        } else {
            data = {};
        }
    } catch (error) {
        fh = await fs.open(config_file, "w+");
        data = {};
    } finally {
        await unlock(config_file);
    }

    if (data[port] == null || initialize) {
        data[port] = {};
    }
    if (key == null) {
        delete data[port];
    } else if (value == null) {
        delete data[port][key];
    } else if (typeof value === "string") {
        data[port][key] = [rtrim(value, path.sep)];
    } else {
        data[port][key] = value.map((v) => rtrim(v, path.sep));
    }
    let buffer: string = JSON.stringify(data, null, 2);
    try {
        const { bytesWritten } = await fh.write(buffer, 0, "utf-8");
        await fh.truncate(bytesWritten);
        await fh.close();
    } catch (error) {
        output.error(`${error}`);
    } finally {
        await unlock(config_file);
    }
}

interface State {
    roots: string[];
    connection_file: string;
}

interface States {
    [key: string]: State;
}

class ResultState {
    port: number | null;
    state: State | null;

    constructor(port: number | null, state: State | null) {
        this.port = port;
        this.state = state;
    }
}

export async function getState(path: string): Promise<null | ResultState> {
    const config_file = await resolvePath("~/.ocpvscode");

    let data: States;

    await lock(config_file);
    try {
        const config: string = await fs.readFile(config_file, "utf-8");
        unlock(config_file);
        if (config === "") {
            data = {};
        } else {
            data = JSON.parse(config);
        }
    } catch (error) {
        throw new Error(`Unable to open config file ${config_file}.`);
    }

    // exact match
    let port: string | null = null;
    for (const [p, v] of Object.entries(data)) {
        if (v.roots.includes(path)) {
            port = p;
        }
    }

    // else search nearest path
    for (const [p, v] of Object.entries(data)) {
        for (const root of v.roots) {
            if (path.startsWith(root)) {
                port = p;
            }
        }
    }

    // heuristic: if there is only one port, use it
    let ports = Object.keys(data);
    if (ports.length === 1) {
        port = ports[0]
    }

    if (port == null) {
        return new ResultState(null, null);
    }

    return new ResultState(parseInt(port, 10), data[port])
}
