# 2025.03.24 작동 확인
import sys
import time
import os

# 현재 파일의 경로를 기준으로 상위 디렉토리(`../start` 경로 추가)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from start import booting  # start.py에서 booting 함수 가져오기

PLC_NUM = "01"

command = "$$" + str(PLC_NUM) + "01;"
command = command.encode("utf-8")

if __name__ == "__main__":
    ser = booting()
    if ser is None:
        print(f"❌ 시리얼 통신 오류")
        sys.exit(1)
    while True:
        try:
            # 명령어 전송

            ser.write(command)
            print(f"📤 보낸 데이터: {command}")

            timeout = 10  # 최대 대기 시간 (초)
            start_time = time.time()
            response = ""

            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:  # 수신된 데이터가 있는 경우
                    response = ser.readline().decode().strip()
                    break
                time.sleep(0.1)  # CPU 점유율 방지 (0.1초 대기)

            if response:
                print(f"📥 받은 응답: {response}")
            else:
                print("⚠ 응답 없음 (타임아웃)")

        except BaseException as e:
            print(f"❌ 시리얼 통신 오류: {e}")
            break
        finally:
            time.sleep(1)
    if ser:
        ser.close()
        print("🔌 연결 종료")
        time.sleep(1)
