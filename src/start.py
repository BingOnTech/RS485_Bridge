import os
import sys
import json
import socket
import serial
import serial.tools.list_ports
import platform

def booting():
    system = platform.system()
    if system == "Linux":
        print("Linux 운영체제입니다.")
    else:
        print("지원 하지 않는 운영체계입니다")
        sys.exit(1)

    selected_port = select_port()
    print("포트 연결 중")
    serial = connect_serial(selected_port)
    print("환경 설정 파일 읽어오는 중")
    load_config()
    return serial


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
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"\n✅ {port} 포트에 연결되었습니다!")
        return ser
    except serial.SerialException as e:
        print(f"❌ 포트 연결 실패: {e}")
        return None


def load_config(filename="config.json"):
    """JSON 설정 파일을 불러오는 함수 (예외 처리 포함)"""
    if not os.path.exists(filename):
        print(f"⚠️ 설정 파일 '{filename}'이 없습니다. 새로 생성합니다.")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
        print("📄 config.json 내용을 추가해 주세요.")
        sys.exit(1)
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
        """설정파일 읽어서 유효성 검사"""
    except json.JSONDecodeError:
        print(f"❌ 설정 파일 '{filename}'의 JSON 형식이 잘못되었습니다.")
        sys.exit(1)
