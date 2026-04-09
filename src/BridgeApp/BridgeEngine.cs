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
        // 1. 초기화 (LCD 및 시리얼)
        Console.WriteLine("[Bridge] Booting...");
        _lcd.Start(); // 🌟 LCD 서비스 시작
        _lcd.UpdateStatus("System", "Initialising...");

        // 1. 초기화
        string port = OperatingSystem.IsWindows() ? "COM3" : "/dev/ttyUSB0";
        _rs485.Open(port);
        _lcd.UpdateOpCode($"Serial Open: {port}");

        // 2. 인터넷 및 메인프레임 연결 시도
        _lcd.UpdateNet(System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable());
        _lcd.UpdateMainframe(false);

        // 환경변수에서 URL 가져오도록 수정 권장
        string url = Environment.GetEnvironmentVariable("MAINFRAME_URL") ?? "http://100.64.x.x:5000/session";

        try
        {
            await _mainframe.ConnectAsync(url);
            _lcd.UpdateMainframe(_mainframe.IsConnected);
        }
        catch
        {
            _lcd.UpdateMainframe(false);
        }

        // 3. 커맨드보드 자동 스캔
        await ScanBoards();

        // 4. 상시 순회 모드
        while (true)
        {
            if (!_mainframe.IsConnected)
            {
                try
                {
                    await _mainframe.ConnectAsync(url);
                    _lcd.UpdateMainframe(true);
                    Console.WriteLine("[NET] Mainframe Reconnected!");
                }
                catch
                {
                    _lcd.UpdateMainframe(false);
                }
            }

            _lcd.UpdateOpCode("Polling Active Boards...");
            foreach (var boardId in _activeBoards)
            {
                string raw = _rs485.SendRequest($"$${boardId}01;");
                if (string.IsNullOrEmpty(raw))
                {
                    _lcd.UpdateOpCode($"Board {boardId} No Resp!"); // 응답 없음 표시
                }

                var data = _rs485.Parse(raw);
                data.BridgeName = _bridgeName;
                if (_mainframe.IsConnected && !string.IsNullOrEmpty(data.BoardId))
                {
                    await _mainframe.PushData(data);
                }
            }
            await Task.Delay(2000);
        }
    }

    private async Task ScanBoards()
    {
        Console.WriteLine("[SCAN] Starting CommandBoard Discovery...");
        _lcd.UpdateOpCode("Scanning Boards...");
        int failCount = 0;
        for (int i = 1; i <= 99; i++)
        {
            string id = i.ToString("D2");
            string res = _rs485.SendRequest($"$${id}10;"); // 펌웨어 체크용

            if (res.Contains("$" + id))
            {
                _activeBoards.Add(id);
                failCount = 0;
                Console.WriteLine($"[FOUND] CommandBoard {id} Detected.");
            }
            else failCount++;

            if (failCount >= 2 && _activeBoards.Count > 0) break;
        }
    }
}