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
        string url = Environment.GetEnvironmentVariable("MAINFRAME_URL") ?? "http://100.64.0.1:5000/bridgeHub";

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
                // 1. 시리얼 통신 (이건 물리적인 거라 순차적으로 해야 함)
                string raw = _rs485.SendRequest($"$${boardId}01;");
                if (string.IsNullOrEmpty(raw)) continue;

                var data = _rs485.Parse(raw);
                data.BridgeName = _bridgeName;

                // 2. 🌟 메인프레임 전송을 비동기로 던짐 (await를 빼버림)
                if (_mainframe.IsConnected && !string.IsNullOrEmpty(data.BoardId))
                {
                    // Task.Run을 사용하여 전송 로직을 스캔 루프에서 분리!
                    _ = Task.Run(async () =>
                    {
                        try
                        {
                            // 여기의 await는 Task.Run 내부에서만 기다리므로 
                            // 메인 스캔 루프(foreach)를 멈추지 않습니다.
                            await _mainframe.PushData(data);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"[NET] Push Error: {ex.Message}");
                        }
                    });
                }
            }
            // 3. 루프 끝에 지연 시간도 약간 줄여서 더 기민하게 반응하게 함
            await Task.Delay(500);
        }
    }
    private async Task ScanBoards()
    {
        Console.WriteLine("[SCAN] Starting CommandBoard Discovery...");
        _lcd.UpdateOpCode("Scanning Boards...");
        _activeBoards.Clear(); // 스캔 전 리스트 초기화

        int consecutiveFailCount = 0; // 🌟 연속 실패 카운트

        for (int i = 1; i <= 99; i++)
        {
            string id = i.ToString("D2");

            // 현재 스캔 중인 ID를 LCD에 표시하면 사용자가 안심합니다.
            _lcd.UpdateOpCode($"Scanning ID: {id}...");

            // 장비 식별을 위한 가벼운 요청
            string res = _rs485.SendRequest($"$${id}10;");

            if (!string.IsNullOrEmpty(res) && res.Contains("$" + id))
            {
                _activeBoards.Add(id);
                consecutiveFailCount = 0; // 🌟 성공 시 카운트 리셋
                Console.WriteLine($"[FOUND] CommandBoard {id} Detected.");
            }
            else
            {
                consecutiveFailCount++; // 🌟 실패 시 카운트 증가
                Console.WriteLine($"[MISS] ID {id} No Response ({consecutiveFailCount}/2)");
            }

            // 🌟 핵심: 2개 이상 연속 응답 없으면 스캔 중단
            if (consecutiveFailCount >= 2)
            {
                Console.WriteLine($"[SCAN] Stopping scan at ID {id} (Consecutive failures).");
                break;
            }

            // 시리얼 버퍼 정리를 위한 아주 짧은 휴식
            await Task.Delay(50);
        }

        _lcd.UpdateOpCode($"Scan Done: {_activeBoards.Count} Found");
        Console.WriteLine($"[SCAN] Completed. Total {_activeBoards.Count} boards found.");
    }
}