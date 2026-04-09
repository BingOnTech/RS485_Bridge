# 1. 빌드 스테이지 (SDK 포함)
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /app

# 🌟 경로 수정: src/BridgeApp/ 폴더 안의 파일을 찾아야 함
COPY ["src/BridgeApp/BridgeApp.csproj", "./"]
RUN dotnet restore

# 🌟 프로젝트 전체 복사
COPY . .
RUN dotnet publish "src/BridgeApp/BridgeApp.csproj" -c Release -o out

# 2. 실행 스테이지 (가벼운 Runtime만 포함)
FROM mcr.microsoft.com/dotnet/runtime:10.0 AS runtime
WORKDIR /app

# 파이썬 및 라이브러리 설치 (LCD 구동용)
RUN apt-get update && apt-get install -y python3 python3-pip python3-pil

COPY --from=build /app/out .
# 🌟 파이썬 스크립트도 실행 폴더로 복사!
COPY src/BridgeApp/bridge_lcd.py .

# 라즈베리파이의 시리얼 포트 접근 권한을 위해 
# 보통 dialout 그룹에 추가하는 작업이 필요할 수 있습니다.
# 하지만 docker-compose에서 privileged 설정을 주는 것이 가장 확실합니다.

ENTRYPOINT ["dotnet", "BridgeApp.dll"]