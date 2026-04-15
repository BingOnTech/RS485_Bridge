using System.Net.NetworkInformation;
using BridgeApp.Services;

namespace BridgeApp;

public class BridgeEngine
{
    private readonly string _bridgeName = Environment.GetEnvironmentVariable("BRIDGE_NAME") ?? "None";
    private readonly Rs485Service _rs485 = new();
    private readonly MainframeClient _mainframe = new();
    private readonly LcdService _lcd = new();
    private List<string> _activeBoards = new();

    public async Task RunAsync()
    {
        Console.WriteLine("[Bridge] Booting...");
        _lcd.Start();

        string port = Environment.GetEnvironmentVariable("RS485_PORT")
                      ?? (OperatingSystem.IsWindows() ? "COM3" : "/dev/rs485");
        string url = Environment.GetEnvironmentVariable("MAINFRAME_URL")
                     ?? "http://100.64.0.1:5000/bridgeHub";

        // ... 상단 생략 ...
        while (true)
        {
            // 1. USB 포트 체크
            bool usbExists = OperatingSystem.IsWindows() || System.IO.File.Exists(port);
            _lcd.Send("USB", usbExists ? "Connected" : "Disconnected");

            var networkInterfaces = NetworkInterface.GetAllNetworkInterfaces();

            // 2. Internet 체크
            bool isNetUp = await CheckInternetConnectivityAsync();
            _lcd.Send("NET", isNetUp ? "Online" : "Offline");

            // 3. VPN 체크
            bool isVpnUp = networkInterfaces.Any(x => (x.Name.Contains("tailscale") || x.Description.Contains("Tailscale"))
                                                      && x.OperationalStatus == OperationalStatus.Up);
            _lcd.Send("VPN", isVpnUp ? "Online" : "Offline");

            // 4. Mainframe 체크 및 연결
            if (isVpnUp && !_mainframe.IsConnected)
            {
                try { await _mainframe.ConnectAsync(url); } catch { }
            }
            _lcd.Send("MAINFRAME", _mainframe.IsConnected ? "Online" : "Offline");

            // 🌟 시리얼 포트 관리 최적화
            if (usbExists && !_rs485.IsOpen) // IsOpen 체크 필수
            {
                try { _rs485.Open(port); } catch { }
            }

            // 장비 폴링 루프
            if (usbExists && _rs485.IsOpen && _activeBoards.Count > 0)
            {
                _lcd.UpdateOpCode("Polling...");
                foreach (var boardId in _activeBoards)
                {
                    string raw = _rs485.SendRequest($"$${boardId}01;");
                    if (string.IsNullOrEmpty(raw)) continue;

                    var data = _rs485.Parse(raw);
                    data.BridgeName = _bridgeName;

                    // 🌟 비동기 데이터 전송 (병목 방지)
                    if (_mainframe.IsConnected && !string.IsNullOrEmpty(data.BoardId))
                    {
                        _ = Task.Run(async () =>
                        {
                            try { await _mainframe.PushData(data); }
                            catch (Exception ex) { Console.WriteLine($"[Push Error] {ex.Message}"); }
                        });
                    }
                }
            }
            else if (usbExists && _rs485.IsOpen && _activeBoards.Count == 0)
            {
                await ScanBoards();
            }

            await Task.Delay(2000); // 2초 간격 유지
        }
    }

    private async Task ScanBoards()
    {
        _lcd.Send("OPCODE", "Scanning...");
        _activeBoards.Clear();
        int failCount = 0;

        for (int i = 1; i <= 99; i++)
        {
            string id = i.ToString("D2");
            string res = _rs485.SendRequest($"$${id}10;");

            if (!string.IsNullOrEmpty(res) && res.Contains("$" + id))
            {
                _activeBoards.Add(id);
                failCount = 0;
            }
            else failCount++;

            if (failCount >= 2) break;
            await Task.Delay(50);
        }
        _lcd.Send("OPCODE", $"Scan Done: {_activeBoards.Count}");
    }

    private async Task<bool> CheckInternetConnectivityAsync()
    {
        try
        {
            using var ping = new Ping();
            var reply = await ping.SendPingAsync("8.8.8.8", 1000); // 8.8.8.8(구글 DNS)로 1초 타임아웃 지정
            return reply.Status == IPStatus.Success;
        }
        catch
        {
            return false; // 네트워크 어댑터가 없거나 핑 전송 실패 시 false
        }
    }
}