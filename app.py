from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)


@app.route("/viewer")
def index():
    return render_template("index.html")


@sock.route("/")
def echo(ws):
    while True:
        data = ws.receive()
        ws.send(data)


if __name__ == "__main__":
    app.run(debug=True)
    sock.init_app(app)
