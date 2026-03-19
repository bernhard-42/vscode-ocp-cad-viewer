function handleMessage(message) {
    console.log("Handling message");
    window.postMessage(message, window.location.origin);
}

class Comms {
    constructor(host, port, maxRetries = 300) {
        this.host = host;
        this.port = port;
        this.maxRetries = maxRetries;
        this.retry = 0;
        this.createWebsocket();
    }

    createWebsocket() {
        this.socket = new WebSocket(`ws://${this.host}:${this.port}`);
        this.ready = false;
        this.retry++;

        this.socket.onopen = (event) => {
            console.log("WebSocket connection established");
            this.ready = true;
            this.retry = 0;
            const warning = document.getElementById("connection-warning");
            if (warning) warning.remove();
            this.register();
        };

        this.socket.onmessage = (event) => {
            console.log("Message received from server:", event.data.substring(0, 200) + "...");
            handleMessage(event.data);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        this.socket.onclose = (event) => {
            console.log("WebSocket connection closed");
            this.ready = false;
            if (!document.getElementById("connection-warning")) {
                const warning = document.createElement("div");
                warning.id = "connection-warning";
                warning.textContent = `=== Connection closed ===`;
                warning.style.cssText =
                    "position:fixed;bottom:0;left:0;width:100%;text-align:center;padding:10px;color:#c00;font-weight:bold;font-family:monospace;z-index:10000;";
                document.body.appendChild(warning);
            }
            console.log(`Attempt #${this.retry} to reconnect in 1s`);
            if (this.maxRetries >= 0) {
                if (this.retry < this.maxRetries) {
                    document.getElementById("connection-warning").textContent = `=== Connection closed, trying ${this.maxRetries - this.retry} times to reconnect ... ===`;
                    setTimeout(() => {
                        this.createWebsocket();
                    }, 1000);
                } else {
                    console.log(`Max reconnection attempts reached, giving up.`);
                    document.getElementById("connection-warning").textContent = `=== Connection closed, manually refresh browser to reconnect ===`;
                }
            } else {
                document.getElementById("connection-warning").textContent = `=== Connection closed, trying to reconnect ... ===`;
                setTimeout(() => {
                    this.createWebsocket();
                }, 1000);
            }
        };
    }

    register() {
        const msg = "L:{}";
        this.socket.send(msg);
    }

    sendStatus(status) {
        if (this.ready) {
            const msg = `U:${JSON.stringify(status)}`;
            this.socket.send(msg);
        }
    }
}

export { Comms };
