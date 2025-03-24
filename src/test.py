# 작동 확인
import serial

# RS485 USB 포트 설정
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600  # 장비에 맞는 속도로 변경 필요

PLC_NUM = "01"


def send_command():
    try:
        # 시리얼 포트 열기
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"✅ 연결 성공: {SERIAL_PORT}")

        # 명령어 전송
        command = "$$" + str(PLC_NUM) + "01;"
        command = command.encode("utf-8")
        ser.write(command)
        print(f"📤 보낸 데이터: {command}")

        # 응답 대기
        response = ser.readline().decode("utf-8").strip()
        print(f"📥 받은 응답: {response}")

    except serial.SerialException as e:
        print(f"❌ 시리얼 통신 오류: {e}")

    finally:
        if ser:
            ser.close()
            print("🔌 연결 종료")


# 실행
if __name__ == "__main__":
    send_command()
