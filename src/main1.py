import threading
import time
import queue
from flask import Flask
from flask_socketio import SocketIO
from start import booting, load_config
from serial.rs485 import RS485 # 가정

# 전역 변수 대신 데이터 매니저 클래스 사용 추천
class DataManager:
    def __init__(self):
        self.plcs = {} # PLC 객체들 저장
        self.running = True

manager = DataManager()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- [Thread 1] 시리얼 통신 담당 ---
def serial_worker(serial_port):
    print(">>> 시리얼 통신 스레드 시작")
    while manager.running:
        try:
            # 1. 데이터 요청 (커맨드 전송)
            # serial_port.write(b"...")
            
            # 2. 데이터 수신 (대기)
            # raw_data = serial_port.read(...)
            
            # 3. 파싱 및 데이터 업데이트 (Bitwise 연산 사용!)
            # manager.plcs[1].update(raw_data)
            
            # 4. 웹으로 실시간 푸시 (옵션)
            # socketio.emit('update', {'id': 1, 'temp': 25.5})
            
            time.sleep(0.5) # 주기 조절
        except Exception as e:
            print(f"통신 에러: {e}")
            time.sleep(1)

# --- [Thread 2] 메인 웹 서버 ---
if __name__ == "__main__":
    # 1. 설정 로드 및 시리얼 연결
    config = load_config()
    # input() 대신 config에서 포트 가져오도록 start.py 수정 필요
    ser = booting() 
    
    if ser:
        # 2. 백그라운드 스레드 시작
        t = threading.Thread(target=serial_worker, args=(ser,))
        t.daemon = True # 메인 프로그램 종료 시 같이 종료됨
        t.start()
    
    # 3. 웹 서버 시작 (Blocking)
    print(">>> 웹 서버 시작")
    socketio.run(app, host="0.0.0.0", port=5000)