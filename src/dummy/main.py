import serial
import time

# RS485 시리얼 포트 설정
ser = serial.Serial(
    port="/dev/ttyUSB0",  # Windows: 'COM3', Linux: '/dev/ttyUSB0'
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
)


# RS485 송신 함수
def send_data(data: str):
    ser.write(data.encode())  # 문자열을 바이트로 변환하여 전송
    print(f"Sent: {data}")


# RS485 수신 함수
def receive_data():
    if ser.in_waiting > 0:  # 읽을 데이터가 있는지 확인
        data = ser.read(ser.in_waiting).decode()
        print(f"Received: {data}")
        return data
    return None


try:
    while True:
        send_data("Hello RS485")  # 데이터 전송
        time.sleep(1)  # 1초 대기
        received = receive_data()  # 데이터 수신
        time.sleep(1)

except KeyboardInterrupt:
    print("프로그램 종료")
    ser.close()  # 포트 닫기
