from start import booting

# from logger import log
from data_slice import data_slice
from serial.rs485 import RS485
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

class Drum:
    """드럼통 클래스"""
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
    """PLC 클래스"""
    def __init__(self, plc_id):
        self.plc_id = plc_id
        self.drum = {i: Drum() for i in range(1, 5)}  # 1~4번 통 관리

# class Drum:
#     def __init__(self, id):
#         self.id = id
#         self.temp = 0.0
#         self.is_high = False
#         # ... 나머지 변수들
# 
#     # 데이터를 스스로 업데이트하도록 변경
#     def update(self, status_byte, temp_val):
#         self.is_low = (status_byte >> 0) & 1
#         self.is_high = (status_byte >> 1) & 1
#         self.temp = temp_val
# 
# class PLC:
#     def __init__(self, plc_id):
#         self.plc_id = plc_id
#         self.drums = [Drum(i) for i in range(4)] # List가 더 관리하기 편함
# 
#     # PLC가 받은 raw 데이터를 처리하는 메서드
#     def parse_packet(self, packet_str):
#         # 여기서 data_slice 로직 수행
#         # 예: self.drums[0].update(...)
#         pass


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
