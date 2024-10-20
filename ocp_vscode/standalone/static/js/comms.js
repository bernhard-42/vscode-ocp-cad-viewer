function handleMessage(message) {
    console.log("Handling message:", message);
    window.postMessage(message, window.location.origin);
}

function connect() {
    const socket = new WebSocket("ws://127.0.0.1:5000");

    socket.onopen = function (event) {
        console.log("WebSocket connection established");
        sendListening();
    };

    socket.onmessage = function (event) {
        console.log("Message received from server:", event.data);
        handleMessage(event.data);
        sendListening();
    };

    socket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };

    socket.onclose = function (event) {
        console.log("WebSocket connection closed");
    };

    function sendListening() {
        socket.send('L:"listening"');
    }
    return socket;
}

export { connect };
