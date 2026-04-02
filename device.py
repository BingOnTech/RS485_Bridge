import serial
import time
import json

class DeviceManager:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(
                self.config['port'], 
                baudrate=self.config['baudrate'], 
                timeout=1
            )
            print(f"✅ [Startup] 시리얼 포트({self.config['port']}) 열기 성공")
            return True
        except Exception as e:
            print(f"❌ [Startup] 포트 열기 실패: {e}")
            return False

    def check_health(self):
        """가동 시 기기 상태 확인 (펌웨어 버전 확인 등)"""
        try:
            # 테스트용 명령 (아까 성공한 $$0110; 사용)
            # 만약 FW 버전을 묻는 명령어가 따로 있다면 그걸 쓰세요.
            self.ser.reset_input_buffer()
            self.ser.write(b"$$0110;\r") 
            time.sleep(0.5)
            response = self.ser.readline()
            
            if response:
                print(f"✅ [Startup] 기기 응답 확인: {response.decode('utf-8', errors='ignore').strip()}")
                return True
            else:
                print("❌ [Startup] 기기 무응답")
                return False
        except Exception as e:
            print(f"❌ [Startup] 기기 점검 중 에러: {e}")
            return False

    def read_data(self):
        """데이터 요청 및 파싱"""
        if not self.ser or not self.ser.is_open: return None

        try:
            self.ser.reset_input_buffer()
            self.ser.write(b"$$0110;\r")
            response = self.ser.readline()

            if response:
                raw_str = response.decode('utf-8', errors='ignore').strip()
                # TODO: 실제 데이터 파싱 로직 적용 (아래는 더미 데이터 예시입니다)
                # 선생님의 실제 데이터 프로토콜에 맞춰 비트 연산 등을 여기에 넣으세요.
                # 현재는 테스트를 위해 랜덤/고정값 반환
                return self.parse_packet(raw_str)
            else:
                return None
        except Exception as e:
            print(f"통신 에러: {e}")
            return None

    def parse_packet(self, raw_data):
        """수신된 문자열을 분해하여 4개 통의 정보로 변환"""
        # 예시: raw_data가 "$01000099..." 형태로 온다고 가정
        # 실제로는 이전에 작성하신 data_slice 로직을 여기에 구현합니다.
        
        drums = []
        for i in range(1, 5): # 1~4번 드럼
            drums.append({
                'id': i,
                'temp': 25.0 + i,    # 예시 값
                'level': 'HIGH',     # 예시 값
                'in': 1,             # 예시 값
                'out': 0             # 예시 값
            })
        return drums

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()