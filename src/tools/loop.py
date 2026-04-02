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
    command = "$0110\r"
    command_bytes = command.encode("ASCII")

    while True:
        ser.write(command_bytes)
        sleep(1)
        
    response = ser.readline().decode()
    print(response)
    ser.close()
