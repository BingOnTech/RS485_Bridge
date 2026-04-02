import time
import serial

ser = serial.Serial("COM4", baudrate=9600, timeout=1)

command = "$$0110;"
command_bytes = command.encode("ASCII")

if __name__ == "__main__":
    print(f"포트 연결됨: {ser.name}, 속도: 9600")

    try:
        while True:
            # Buffer clean
            ser.reset_input_buffer()

            # Tx
            ser.write(command_bytes)
            print(f"[Tx] 보냄: {command.strip()}")

            # Rx
            response = ser.readline()

            if response:
                print(f"[Rx] 받음: {response.decode('utf-8', errors='ignore').strip()}")
            else:
                print("[Rx] 응답 없음")

            print("-" * 30)
            time.sleep(1)

    except KeyboardInterrupt:
        print("종료")
        if ser.is_open:
            ser.close()
    except Exception as e:
        print(f"에러: {e}")
        if ser.is_open:
            ser.close()
