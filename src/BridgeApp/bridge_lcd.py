import sys
import os
import numpy as np
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
        # 2. 이미지를 넘파이 배열로 변환 (R, G, B 채널 분리)
        img_array = np.array(img, dtype=np.uint16)
        r = img_array[:,:,0]
        g = img_array[:,:,1]
        b = img_array[:,:,2]

        # 3. 🌟 RGB888 -> RGB565 강제 비트 연산
        # R(5비트), G(6비트), B(5비트)로 쪼개서 16비트 하나로 합침
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        
        # 4. 바이트 순서(Endian) 조정 - 만약 화면이 여전히 이상하면 .byteswap() 추가
        raw_data = rgb565.flatten().tobytes()

        with open(FB_PATH, "wb") as f:
            f.write(raw_data)
            f.flush() # 🌟 즉시 기록 강제
    except Exception as e:
        print(f"LCD Error: {e}")
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