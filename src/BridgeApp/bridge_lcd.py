import sys
import os
from PIL import Image, ImageDraw, ImageFont

# 환경에 따라 /dev/fb1 또는 /dev/fb0
FB_PATH = "/dev/fb1" if os.path.exists("/dev/fb1") else "/dev/fb0"

def draw_status(data_map):
    # 480x320 해상도 가정 (터치 LCD 표준)
    img = Image.new('RGB', (480, 320), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default() # 필요 시 나눔고딕 등 폰트 경로 지정

    draw.text((10, 10), "=== BRIDGE SYSTEM STATUS ===", fill=(0, 255, 255))
    draw.text((10, 50), f"System: {data_map.get('STATUS', 'N/A')}", fill=(255, 255, 255))
    draw.text((10, 80), f"Internet: {data_map.get('NET', 'Checking...')}", fill=(0, 255, 0))
    draw.text((10, 110), f"Mainframe: {data_map.get('MAINFRAME', 'Offline')}", fill=(255, 255, 0))
    
    draw.line((10, 150, 470, 150), fill=(100, 100, 100))
    
    draw.text((10, 170), "Last OpCode:", fill=(200, 200, 200))
    draw.text((20, 200), data_map.get('OPCODE', 'Idle'), fill=(255, 165, 0))

    try:
        with open(FB_PATH, "wb") as f:
            f.write(img.tobytes())
    except:
        pass

if __name__ == "__main__":
    current_data = {}
    while True:
        line = sys.stdin.readline()
        if not line: break
        
        if "|" in line:
            key, val = line.strip().split("|")
            current_data[key] = val
            draw_status(current_data)