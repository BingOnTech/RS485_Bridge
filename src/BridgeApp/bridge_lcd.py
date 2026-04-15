import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# LCD 장치 경로 확인
FB_PATH = "/dev/fb1" if os.path.exists("/dev/fb1") else "/dev/fb0"


def draw_status(data_map):
    # 480x320 캔버스 생성
    img = Image.new("RGB", (480, 320), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 색상 정의
    C_TITLE = (0, 255, 255)  # 청록
    C_ON = (0, 255, 0)  # 녹색
    C_OFF = (255, 0, 0)  # 빨강
    C_WAIT = (255, 165, 0)  # 주황
    C_WHITE = (255, 255, 255)

    # 타이틀
    draw.text((10, 10), "=== BINGON BRIDGE STATUS ===", fill=C_TITLE)

    # 1. USB Serial 상태 (RS485)
    usb_stat = data_map.get("USB", "Disconnected")
    draw.text(
        (10, 60),
        f"RS485 Port : {usb_stat}",
        fill=C_ON if usb_stat == "Connected" else C_OFF,
    )

    # 2. Internet 상태
    net_stat = data_map.get("NET", "Offline")
    draw.text(
        (10, 110),
        f"Internet   : {net_stat}",
        fill=C_ON if net_stat == "Online" else C_OFF,
    )

    # 3. Server (SignalR) 상태 - VPN 대신 배치
    srv_stat = data_map.get("SERVER", "Offline")
    draw.text(
        (10, 160),
        f"Mainframe  : {srv_stat}",
        fill=C_ON if srv_stat == "Online" else C_OFF,
    )

    # 구분선
    draw.line((10, 210, 470, 210), fill=(100, 100, 100))

    # 하단 OpCode 표시
    draw.text((10, 230), "Current Action:", fill=(200, 200, 200))
    # 글자가 길어질 수 있으므로 조금 더 큰 여백 할당
    draw.text((20, 270), data_map.get("OPCODE", "Idle"), fill=C_WAIT)

    # 재호님 LCD 설치 방향에 맞게 180도 회전
    img = img.rotate(180)

    try:
        # RGB888 -> RGB565 변환 로직 (기존 유지)
        img_array = np.array(img, dtype=np.uint16)
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        raw_data = rgb565.flatten().tobytes()

        with open(FB_PATH, "wb") as f:
            f.write(raw_data)
            f.flush()
    except Exception as e:
        # 에러 발생 시 표준 출력으로 출력하여 디버깅 지원
        pass


if __name__ == "__main__":
    current_data = {}
    # C# StandardInput으로부터 실시간 데이터를 한 줄씩 읽음
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if "|" in line:
            try:
                key, val = line.strip().split("|")
                current_data[key] = val
                draw_status(current_data)
            except ValueError:
                pass
