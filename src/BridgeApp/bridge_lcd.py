import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FB_PATH = "/dev/fb1" if os.path.exists("/dev/fb1") else "/dev/fb0"


def draw_status(data_map):
    img = Image.new("RGB", (480, 320), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 색상 정의
    C_TITLE = (0, 255, 255)  # 청록
    C_ON = (0, 255, 0)  # 녹색
    C_OFF = (255, 0, 0)  # 빨강
    C_WAIT = (255, 165, 0)  # 주황
    C_WHITE = (255, 255, 255)

    draw.text((10, 10), "=== BINGON BRIDGE STATUS ===", fill=C_TITLE)

    # 1. USB Serial 상태
    usb_stat = data_map.get("USB", "Disconnected")
    draw.text(
        (10, 50),
        f"USB Port  : {usb_stat}",
        fill=C_ON if usb_stat == "Connected" else C_OFF,
    )

    # 2. Internet 상태
    net_stat = data_map.get("NET", "Offline")
    draw.text(
        (10, 85),
        f"Internet  : {net_stat}",
        fill=C_ON if net_stat == "Online" else C_OFF,
    )

    # 3. VPN (Tailscale) 상태
    vpn_stat = data_map.get("VPN", "Offline")
    draw.text(
        (10, 120), f"Network : {vpn_stat}", fill=C_ON if vpn_stat == "Online" else C_OFF
    )

    # 4. Mainframe (SignalR) 상태
    mf_stat = data_map.get("MAINFRAME", "Offline")
    draw.text(
        (10, 155), f"Mainframe : {mf_stat}", fill=C_ON if mf_stat == "Online" else C_OFF
    )

    draw.line((10, 190, 470, 190), fill=(100, 100, 100))

    # 하단 OpCode 표시
    draw.text((10, 210), "Current Action:", fill=(200, 200, 200))
    draw.text((20, 245), data_map.get("OPCODE", "Idle"), fill=C_WAIT)

    img = img.rotate(180)  # 재호님 LCD 방향에 맞춤

    try:
        img_array = np.array(img, dtype=np.uint16)
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        raw_data = rgb565.flatten().tobytes()

        with open(FB_PATH, "wb") as f:
            f.write(raw_data)
            f.flush()
    except:
        pass


if __name__ == "__main__":
    current_data = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if "|" in line:
            key, val = line.strip().split("|")
            current_data[key] = val
            draw_status(current_data)
