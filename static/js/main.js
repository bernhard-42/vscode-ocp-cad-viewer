document.addEventListener("DOMContentLoaded", function () {
    const iframe = document.getElementById("viewer");

    window.addEventListener("message", function (event) {
        console.log("Message received from iframe:", event.data);
        // Handle the message from the iframe
    });

    const socket = new WebSocket("ws://" + location.host + "/");

    socket.addEventListener("message", (ev) => {
        console.log("<<< " + ev.data, "blue");
    });

    socket.onopen = function () {
        console.log("Connection established", "green");
        socket.send("Hello from js");
    };

    function sendMessageToIframe(message) {
        iframe.contentWindow.postMessage(message, "*");
    }

    // Example: Send a message to the iframe after 2 seconds
    // setTimeout(() => {
    //     sendMessageToIframe('Hello from parent page!');
    // }, 2000);
});
