function handleMessage(message) {
  // Handle the received message here
  console.log("Handling message:", message);
  // Add your custom logic to process the message
}

function connect() {
  const socket = new WebSocket("ws://127.0.0.1:3939");

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

// export function postMessage(message) {
//     window.parent.postMessage(message, '*');
// }

// document.addEventListener("DOMContentLoaded", function () {
//     window.addEventListener("message", function (event) {
//         console.log("Message received from:", event.data);
//     });

//     const socket = new WebSocket("ws://" + location.host + "/");

//     socket.addEventListener("message", (ev) => {
//         console.log("<<< " + ev.data, "blue");
//     });

//     socket.onopen = function () {
//         console.log("Connection established", "green");
//         socket.send("Hello from js");
//     };
// };
