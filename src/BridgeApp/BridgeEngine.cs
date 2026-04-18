using System.Net.NetworkInformation;
using BridgeApp.Services;
using BridgeApp.Models;

namespace BridgeApp;

public class BridgeEngine
{
    private readonly string _bridgeName = Environment.GetEnvironmentVariable("BRIDGE_NAME") ?? "None";
    private readonly Rs485Service _rs485 = new();
    private readonly LcdService _lcd = new();
    private readonly MainframeClient _mainframe; // 생성자에서 주입받음

    private List<string> _activeBoards = new();
    private DateTime _lastNetCheckTime = DateTime.MinValue;
    private bool _isNetUpCached = false;
    private bool? _wasMainframeConnected = null;

    // 생성자를 통해 Program.cs에서 초기화된 클라이언트를 전달받습니다.
    public BridgeEngine(MainframeClient mainframe)
    {
        _mainframe = mainframe;
    }

    public async Task RunAsync()
    {
        Console.WriteLine($"[Bridge] Starting Engine: {_bridgeName}");
        _lcd.Start();

        // 환경변수 로드 (하드코딩 제거)
        string port = Environment.GetEnvironmentVariable("RS485_PORT")
                      ?? (OperatingSystem.IsWindows() ? "COM3" : "/dev/rs485");

        Console.WriteLine("[Bridge] Main loop started...");

        while (true)
        {
            // 1. USB(RS485) 하드웨어 체크
            bool usbExists = OperatingSystem.IsWindows() || System.IO.File.Exists(port);
            _lcd.Send("USB", usbExists ? "Connected" : "Disconnected");

            // 2. Internet 체크 (구글 DNS 핑)
            bool isNetUp = await CheckInternetConnectivityAsync();
            _lcd.Send("NET", isNetUp ? "Online" : "Offline");

            // 3. Mainframe 연결 상태 체크 (VPN 체크 로직 삭제)
            // SignalR은 스스로 재접속하므로, 여기선 상태 표시만 합니다.
            bool isConnected = _mainframe.IsConnected;
            _lcd.Send("SERVER", isConnected ? "Online" : "Offline");

            if (isConnected != _wasMainframeConnected)
            {
                Console.WriteLine($"[Mainframe Status] {(isConnected ? "Connected" : "Disconnected")}");
                _wasMainframeConnected = isConnected;
            }

            // 4. RS485 포트 오픈
            if (usbExists && !_rs485.IsOpen)
            {
                try
                {
                    _rs485.Open(port);
                    Console.WriteLine($"[RS485] Opened {port}");
                }
                catch (Exception ex) { Console.WriteLine($"[RS485 Error] {ex.Message}"); }
            }

            // 5. 데이터 폴링 및 전송
            if (usbExists && _rs485.IsOpen && _activeBoards.Count > 0)
            {
                _lcd.Send("OPCODE", "Polling...");
                foreach (var boardId in _activeBoards)
                {
                    string raw = _rs485.SendRequest($"$${boardId}01;");
                    if (string.IsNullOrEmpty(raw)) continue;

                    var data = _rs485.Parse(raw);
                    data.BridgeName = _bridgeName; // 환경변수에서 읽은 브릿지 이름 삽입

                    if (isConnected)
                    {
                        _ = Task.Run(async () =>
                        {
                            try
                            {
                                // 1. 객체를 JSON 문자열로 직렬화
                                string json = System.Text.Json.JsonSerializer.Serialize(data);

                                // 2. AES 암호화
                                string encryptedData = CryptoUtil.Encrypt(json);

                                // 3. 암호화된 문자열 전송 (Hub 메서드 호출)
                                await _mainframe.PushData(encryptedData);
                            }
                            catch (Exception ex) { Console.WriteLine($"[Encrypt Error] {ex.Message}"); }
                        });
                    }
                }
            }
            else if (usbExists && _rs485.IsOpen && _activeBoards.Count == 0)
            {
                await ScanBoards();
            }

            await Task.Delay(2000); // 2초 주기
        }
    }

    private async Task ScanBoards()
    {
        _lcd.Send("OPCODE", "Scanning...");
        _activeBoards.Clear();

        for (int i = 1; i <= 30; i++)
        {
            string id = i.ToString("D2");
            string res = _rs485.SendRequest($"$${id}10;");

            if (!string.IsNullOrEmpty(res) && res.Contains("$" + id))
            {
                _activeBoards.Add(id);
            }
            await Task.Delay(30);
        }
        _lcd.Send("OPCODE", $"Boards: {_activeBoards.Count}");
    }

    private async Task<bool> CheckInternetConnectivityAsync()
    {
        if ((DateTime.UtcNow - _lastNetCheckTime).TotalSeconds < 15)
            return _isNetUpCached;

        try
        {
            using var ping = new Ping();
            var reply = await ping.SendPingAsync("8.8.8.8", 1000);
            _isNetUpCached = reply.Status == IPStatus.Success;
        }
        catch { _isNetUpCached = false; }

        _lastNetCheckTime = DateTime.UtcNow;
        return _isNetUpCached;
    }
}