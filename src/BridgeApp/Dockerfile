# 1. 빌드용 환경 (무거운 도구 포함)
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /app

# 프로젝트 파일만 먼저 복사해서 패키지 다운로드 (캐시 최적화)
COPY *.csproj ./
RUN dotnet restore

# 나머지 소스코드 전부 복사 후 최종 빌드
COPY . ./
RUN dotnet publish -c Release -o out

# 2. 실행용 런타임 환경 (최대한 가볍게)
FROM mcr.microsoft.com/dotnet/runtime:10.0
WORKDIR /app
COPY --from=build /app/out .

# 실행 명령어
ENTRYPOINT ["dotnet", "BridgeApp.dll"]