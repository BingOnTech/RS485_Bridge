# from logger import log
from start import booting
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

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


# 소켓 연결 요청
@socketio.on("connect")
def handle_connect():
    user = request.args.get("user")

    if not user:
        return False  # 인증 실패 시 연결 거부

    print(f"User {user} connected")


"""
@socketio.on("request_data")
def handle_request_data():
    emit("message", "실시간 데이터 예제 값")
"""


def run_socketio():
    socketio.run(app, host="0.0.0.0", port=5000)


def req(ser, command):
    try:
        command_bytes = command.encode("utf-8")
        ser.write(command_bytes)
        print(f"\n📤 보낸 데이터: {command}")
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
    # socketio.run(app, host="0.0.0.0", port=5000)
    time.sleep(1)

    while True:
        current_minute = datetime.now().minute

        for num in NUM:
            command = "$$" + num + "01;"

            # 시리얼 통신
            req(ser, command)
            response = res()

            if response == False:
                continue

            # 데이터 처리
            response = response.lstrip("$")
            plc_number, buffer = int(response[:2]), response[2:]
            data_slice(buffer, plc[plc_number])

            for j in range(1, 5):
                plc[plc_number].drum[j].show()

            # 클라이언트에 데이터 전송
            socketio.emit("plc_data", {plc_number: plc[plc_number].to_dict()})

            # DB에 저장
            """
            query = ""
            execute_query()
            """
        while datetime.now().minute == current_minute:
            time.sleep(1)
