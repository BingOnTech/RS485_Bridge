from start import booting

# from logger import log
from data_slice import data_slice
from serial.rs485 import RS485
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit


class Drum:
    def __init__(self):
        self.low = ""
        self.high = ""
        self.in_valve = ""
        self.out = ""
        self.temp = 0

    def show(self):
        print(
            f"Low: {self.low}, High: {self.high}, IN: {self.in_valve}, OUT: {self.out}, Temp: {self.temp}"
        )


class PLC:
    def __init__(self, plc_id):
        self.plc_id = plc_id
        self.drum = {i: Drum() for i in range(1, 5)}  # 1~4번 통 관리


app = Flask(__name__)

buffer = ""

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@socketio.on("connect")
def handle_connect():
    user = request.args.get("user")
    if not user:
        return False  # 인증 실패 시 연결 거부

    print(f"User {user} connected")
    emit("message", f"Welcome {user}!")


@socketio.on("request_data")
def handle_request_data():
    emit("message", "실시간 데이터 예제 값")


if __name__ == "__main__":
    booting()
    # PLC 객체 생성
    plcs = {i: PLC(i) for i in range(1, 17)}  # 16개의 PLC 생성
    # websocket
    socketio.run(app, host="0.0.0.0", port=5000)

    command = "/1ZR\r"
    buffer = "AABBCCDDEEFF112233445566778899"  # 예제 데이터
    plc_number = 1  # 예제 PLC 번호

    data_slice(buffer, plcs[plc_number])
