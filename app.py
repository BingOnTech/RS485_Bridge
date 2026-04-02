from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
from database import DBManager
from device import DeviceManager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 객체 생성
db = DBManager()
device = DeviceManager()

# 백그라운드 작업 상태
is_running = True

def monitoring_loop():
    """백그라운드에서 계속 도는 녀석"""
    print("🚀 [System] 모니터링 루프 시작")
    
    while is_running:
        # 1. 데이터 읽기 (Device)
        data = device.read_data()
        
        if data:
            # 2. 데이터 저장 (DB)
            db.insert_log(data)
            
            # 3. 웹으로 쏘기 (Real-time)
            socketio.emit('update_data', {'drums': data})
            print(f"[Log] 데이터 수신 및 저장 완료 ({len(data)}개 드럼)")
        
        time.sleep(1) # 1초 주기

# --- 초기화 절차 (Startup Sequence) ---
def system_startup():
    print("\n=== [ 시스템 가동 시작 ] ===")
    
    # 1. DB 연결
    if not db.connect():
        return False
    
    # 2. 시리얼 연결
    if not device.connect():
        return False
        
    # 3. 기기 응답 확인
    if not device.check_health():
        return False
        
    print("=== [ 시스템 가동 준비 완료 ] ===\n")
    return True

# --- Flask 라우팅 ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 시작 전 점검
    if system_startup():
        # 점검 통과 시 백그라운드 스레드 시작
        t = threading.Thread(target=monitoring_loop)
        t.daemon = True
        t.start()
        
        # 웹서버 시작
        try:
            socketio.run(app, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            is_running = False
            device.close()
            db.close()
    else:
        print("❌ 시스템 초기화 실패로 프로그램을 종료합니다.")