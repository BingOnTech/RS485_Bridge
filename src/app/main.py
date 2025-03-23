from start import booting

# from logger import log
from serial.rs485 import RS485


from flask import Flask, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)


@app.route("/")
def hello_world():
    return (
        "<p>This is Smart BING-ON tec aging system API server.</p>"
        "<p>You enter worng port to use this server.</p>"
        "<p>Please enter with port 22 Thank you.</p>"
    )


@app.route("/api/v1/aging", methods=["POST"])
def aging():
    data = request.json
    print(data)
    return jsonify(data)
