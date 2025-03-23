import serial
import serial.tools.list_ports



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
    """사용자가 포트를 선택할 수 있도록 함"""
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

if __name__ == "__main__":
    selected_port = select_port()  # 포트 선택
    ser = connect_serial(selected_port)  # 포트 연결

    if ser:
        # 추가적인 시리얼 통신 코드 작성 가능
        ser.close()  # 테스트 후 포트 닫기
