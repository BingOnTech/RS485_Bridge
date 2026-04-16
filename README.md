# RS485-Bridge

```sh
sudo usermod -a -G dialout $USER # 포트 접근 오류 발생 시
git clone https://github.com/BingOnTech/RS485_Bridge.git
cd RS485-BRIDGE

sh setup.sh # 첫 설치
docker logs -f rs485-bridge # 실시간 로그 확인
docker compose down # 서비스 종료
sh run.sh # 프로그램 실행
```
