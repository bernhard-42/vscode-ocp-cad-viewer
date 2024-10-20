from flask import Flask, render_template
from flask_sock import Sock
from simple_websocket import ConnectionClosed
import orjson

app = Flask(__name__)
sock = Sock(app)
viewer_message = {}
splash = True


def config():
    return {"_splash": splash}


def debug_print(*msg):
    print("Debug:", *msg)


def post_message(msg):
    print("Posted message: " + msg)


def handle_backend(data):
    print("Backend data: " + data)


@app.route("/viewer")
def index():
    return render_template("viewer.html")


@sock.route("/")
def handle_message(ws):
    try:
        while True:
            data = ws.receive().decode("utf-8")

            debug_print("Received data from viewer", data)
            message_type = data[0]
            data = data[2:]
            debug_print("Message type", message_type)
            debug_print("Data", data)
            if message_type == "C":
                cmd = orjson.loads(data)
                if cmd == "status":
                    ws.send(orjson.dumps(viewer_message))
                elif cmd == "config":
                    ws.send(orjson.dumps(config()))
                elif cmd.type == "screenshot":
                    post_message(orjson.dumps(cmd))

            elif message_type == "D":
                debug_print("Received a new model")
                post_message(data)
                debug_print("Posted model to view")
                if splash:
                    splash = False

            elif message_type == "S":
                debug_print("Received a config")
                post_message(data)
                debug_print("Posted config to view")

            elif message_type == "L":
                # pythonListener = socket
                debug_print("Listener registered")

            elif message_type == "B":
                handle_backend(data)
                debug_print("Model data sent to the backend")

            elif message_type == "R":
                post_message(data)
                debug_print("Backend response received.")

            if message_type == "C" and not (
                isinstance(data, dict) and data["type"] == "screenshot"
            ):
                ws.send(orjson.dumps({}))
    except ConnectionClosed:
        print("Client disconnected")


if __name__ == "__main__":
    app.run(debug=True)
    sock.init_app(app)
