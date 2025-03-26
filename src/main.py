from start import booting
from db import fetch_query, execute_query

# from logger import log
from data_slice import data_slice

import sys
import time
import threading
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

TIMEOUT = 10


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


def run_socketio():
    socketio.run(app, host="0.0.0.0", port=5000)


def req(ser, command):
    try:
        command_bytes = command.encode("utf-8")
        ser.write(command_bytes)
        print(f"📤 보낸 데이터: {command}")
    except BaseException as e:
        print(f"❌ 시리얼 통신 오류: {e}")


def res():
    start_time = time.time()
    response = ""

    while time.time() - start_time < TIMEOUT:
        if ser.in_waiting > 0:  # 수신된 데이터가 있는 경우
            response = ser.readline().decode().strip()
            break
        time.sleep(0.1)  # CPU 점유율 방지 (0.1초 대기)

    if response:
        print(f"📥 받은 응답: {response}")
        return response
    else:
        print("⚠ 응답 없음 (타임아웃)")
        return False


if __name__ == "__main__":
    ser = booting()
    if ser == None:
        print("Serial port Error--")
        sys.exit(1)

    # PLC 객체 생성
    plc = {i: PLC(i) for i in range(1, 17)}  # 16개의 PLC 생성

    # websocket
    thread = threading.Thread(target=run_socketio, daemon=True)
    thread.start()
    time.sleep(1)

    command = "$$0101;"
    while True:
        req(ser, command)
        response = res()

        if response == False:
            continue

        response = response.lstrip("$")
        plc_number, buffer = int(response[:2]), response[2:]
        data_slice(buffer, plc[plc_number])

        for j in range(1, 5):
            plc.drum[j].show()
