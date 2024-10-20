import orjson
from flask import Flask, render_template
from flask_sock import Sock
from simple_websocket import ConnectionClosed

app = Flask(__name__)
sock = Sock(app)
viewer_message = {}
splash = True


def config():
    return {"_splash": splash}


def debug_print(*msg):
    print("Debug:", *msg)


def handle_backend(data):
    print("Backend data: " + data)


@app.route("/viewer")
def index():
    return render_template("viewer.html")


python_client = None
javascript_client = None


@sock.route("/")
def handle_message(ws):
    global python_client, javascript_client

    try:
        while True:
            data = ws.receive()
            if isinstance(data, bytes):
                data = data.decode("utf-8")

            message_type = data[0]
            data = data[2:]
            debug_print("Received data from viewer", message_type)

            if message_type == "C":
                python_client = ws
                cmd = orjson.loads(data)
                print(cmd)
                if cmd == "status":
                    python_client.send(orjson.dumps({"text": viewer_message}))
                elif cmd == "config":
                    python_client.send(orjson.dumps(config()))
                elif cmd.type == "screenshot":
                    python_client(orjson.dumps(cmd))

            elif message_type == "D":
                python_client = ws
                debug_print("Received a new model")
                javascript_client.send(data)
                debug_print("Posted model to view")
                if splash:
                    splash = False

            elif message_type == "S":
                python_client = ws
                debug_print("Received a config")
                javascript_client.send(data)
                debug_print("Posted config to view")

            elif message_type == "L":
                javascript_client = ws
                debug_print("Listener registered")

            # elif message_type == "B":
            #     handle_backend(data)
            #     debug_print("Model data sent to the backend")

            # elif message_type == "R":
            #     python_client = ws
            #     post_message(data)
            #     debug_print("Backend response received.")

            # if message_type == "C" and not (
            #     isinstance(data, dict) and data["type"] == "screenshot"
            # ):
            #     ws.send(orjson.dumps({}))

    except ConnectionClosed:
        print("Client disconnected")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    app.run(debug=True)
    sock.init_app(app)
