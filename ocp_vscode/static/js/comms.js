function handleMessage(message) {
    console.log("Handling message");
    window.postMessage(message, window.location.origin);
}

class Comms {
    constructor(host, port) {
        this.socket = new WebSocket(`ws://${host}:${port}`);
        this.ready = false;

        this.socket.onopen = (event) => {
            console.log("WebSocket connection established");
            this.ready = true;
            this.register();
        };

        this.socket.onmessage = (event) => {
            console.log(
                "Message received from server:",
                event.data.substring(0, 200) + "..."
            );
            handleMessage(event.data);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        this.socket.onclose = (event) => {
            console.log("WebSocket connection closed");
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
