#!/bin/bash

# BingOn Bridge One-Click Setup Script
echo "🚀 [BingOn] 브릿지 셋업을 시작합니다..."

# 1. 시스템 업데이트 및 필수 도구 설치
echo "📦 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git vim build-essential

# 2. Docker 및 Docker Compose 설치
if ! command -v docker &> /dev/null; then
    echo "🐳 도커(Docker)를 설치합니다..."
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✅ 도커 설치 완료 (재부팅 후 권한이 적용됩니다)"
else
    echo "✅ 도커가 이미 설치되어 있습니다."
fi

# 3. RS485 USB 고정 (udev 규칙)
echo "🔌 USB 장치 고정 설정 (udev) 중..."
# 재호님의 장치 ID(0403:6001)를 기반으로 작성되었습니다.
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="rs485", MODE="0666"' | sudo tee /etc/udev/rules.d/99-rs485.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "✅ /dev/rs485 심볼릭 링크 생성 완료"

# 4. 프로젝트 폴더 구조 생성
echo "📂 작업 디렉토리 생성 중..."
mkdir -p ~/BingOn_Bridge/tailscale-data
cd ~/BingOn_Bridge

# 5. 기본 .env 파일 생성 (템플릿)
if [ ! -f .env ]; then
    echo "📝 기본 .env 파일을 생성합니다. (나중에 실제 값으로 수정하세요)"
    cat <<EOT >> .env
BRIDGE_NAME=
MAINFRAME_URL=
ENCRYPTION_KEY=
RS485_PORT=/dev/rs485
EOT
    echo "✅ .env 생성 완료"
fi

echo "------------------------------------------------"
echo "🎉 모든 설정이 완료되었습니다!"
echo "1. 'cd ~/BingOn_Bridge' 이동"
echo "2. 'nano .env'를 실행해 TS_AUTHKEY를 입력하세요."
echo "3. 'docker compose up -d'로 실행하세요."
echo "⚠️  도커 권한 적용을 위해 'sudo reboot'를 권장합니다."
echo "------------------------------------------------"