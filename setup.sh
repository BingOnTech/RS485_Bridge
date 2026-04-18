#!/bin/bash

# BingOn Bridge One-Click Setup Script (Final Optimized)
echo "🚀 [BingOn] 브릿지 통합 셋업을 시작합니다..."

# 1. 시스템 업데이트 및 필수 도구 설치
echo "📦 시스템 업데이트 및 필수 패키지 설치 중..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git vim build-essential python3-pip

# 2. Docker 및 Docker Compose 설치 및 자동 시작 설정
if ! command -v docker &> /dev/null; then
    echo "🐳 도커(Docker)를 설치합니다..."
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    # 전원 인가 시 도커 서비스가 자동 시작되도록 설정
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
    echo "✅ 도커 설치 및 자동 시작 설정 완료"
else
    echo "✅ 도커가 이미 설치되어 있습니다."
fi

# 3. RS485 USB 고정 (udev 규칙)
echo "🔌 USB 장치 고정 설정 (udev) 중..."
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="rs485", MODE="0666"' | sudo tee /etc/udev/rules.d/99-rs485.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "✅ /dev/rs485 심볼릭 링크 생성 완료"

# 4. 물리 종료 버튼 설정 (GPIO 21 - 40번 핀 사용)
echo "🔘 물리 종료 버튼 설정 중 (Pin 39-40)..."
# /boot/config.txt (또는 신형 OS의 경우 /boot/firmware/config.txt)에 설정 추가
CONFIG_FILE="/boot/config.txt"
[ ! -f "$CONFIG_FILE" ] && CONFIG_FILE="/boot/firmware/config.txt"

if ! grep -q "gpio-shutdown" "$CONFIG_FILE"; then
    # GPIO 21번을 사용하며, 풀업 저항을 활성화하여 버튼 클릭 시 하이->로우 감지
    echo "dtoverlay=gpio-shutdown,gpio_pin=21,active_low=1,gpio_pull=up" | sudo tee -a "$CONFIG_FILE"
    echo "✅ 종료 버튼 설정 완료 (GPIO 21)"
else
    echo "✅ 종료 버튼 설정이 이미 존재합니다."
fi

# 5. 프로젝트 폴더 구조 생성
echo "📂 작업 디렉토리 생성 중..."
mkdir -p ~/BingOn_Bridge/
cd ~/BingOn_Bridge

# 6. .env 파일 생성 (SignalR/AES 버전으로 업데이트)
if [ ! -f .env ]; then
    echo "📝 .env 파일을 생성합니다."
    cat <<EOT >> .env
BRIDGE_NAME=
MAINFRAME_URL=
AES_KEY=
RS485_PORT=/dev/rs485
EOT
    echo "✅ .env 생성 완료"
fi

echo "------------------------------------------------"
echo "🎉 모든 설정이 완료되었습니다!"
echo "1. 39번(GND)과 40번(GPIO 21) 핀에 푸시 버튼을 연결하세요."
echo "2. 'nano ~/BingOn_Bridge/.env'에서 AES_KEY를 수정하세요."
echo "3. 'docker compose up -d'를 한 번 실행해두면 이후 부팅 시 자동 실행됩니다."
echo "⚠️  설정 적용을 위해 'sudo reboot'를 실행해주세요."
echo "------------------------------------------------"