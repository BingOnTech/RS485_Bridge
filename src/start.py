import sys
import serial
import serial.tools.list_ports
import platform
from db import test_db_connection

def booting():
    # 운영체제 점검
    system = platform.system()
    if system == "Linux":
        print("Linux 운영체제입니다.")
    else:
        print("지원 하지 않는 운영체계입니다")
        sys.exit(1)

    # DB 연결
    if test_db_connection() == False:
        sys.exit(1)

    # 시리얼 포트 연결
    selected_port = select_port()
    print("포트 연결 중")
    serial = connect_serial(selected_port)
    if serial:
        return serial
    else:
        print("시리얼 포트 연결 오류")
        return None


def list_serial_ports():
    """현재 연결된 시리얼 포트 목록을 가져옴"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def wait_for_ports():
    """포트가 연결될 때까지 사용자 입력을 기다림"""
    while True:
        ports = list_serial_ports()
        if ports:
            return ports  # 포트가 감지되면 반환

        print("\n❌ 연결된 시리얼 포트가 없습니다.")
        input("🔄 아무 키나 누르면 다시 검색합니다...")


def select_port():
    """사용자가 포트를 선택"""
    while True:
        ports = wait_for_ports()  # 포트가 감지될 때까지 대기

        print("\n🔌 연결된 포트 목록:")
        for i, port in enumerate(ports):
            print(f"{i + 1}. {port}")

        try:
            choice = int(input("\n연결할 포트 번호를 선택하세요: ")) - 1
            if 0 <= choice < len(ports):
                return ports[choice]
            else:
                print("⚠️ 올바른 번호를 입력하세요.")
        except ValueError:
            print("⚠️ 숫자를 입력하세요.")


def connect_serial(port):
    """선택한 포트로 시리얼 연결"""
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=2)
        print(f"\n✅ {port} 포트에 연결되었습니다!")
        return ser
    except serial.SerialException as e:
        print(f"❌ 포트 연결 실패: {e}")
        return None
