using System.Diagnostics;

namespace BridgeApp.Services;

public class LcdService
{
    private Process? _pythonProcess;
    private StreamWriter? _inputStream;

    public void Start()
    {
        try
        {
            _pythonProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "python3",
                    Arguments = "bridge_lcd.py",
                    UseShellExecute = false,
                    RedirectStandardInput = true,
                    CreateNoWindow = true
                }
            };
            _pythonProcess.Start();
            _inputStream = _pythonProcess.StandardInput;

            Send("OPCODE", "Booting...");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[LCD Error] Failed to start Python LCD script: {ex.Message}");
        }
    }

    // 파이썬으로 "키|값" 형태의 메시지를 보냄 (표준 메서드)
    public void Send(string key, string value)
    {
        if (_inputStream != null && _pythonProcess != null && !_pythonProcess.HasExited)
        {
            try
            {
                _inputStream.WriteLine($"{key}|{value}");
                _inputStream.Flush();
            }
            catch { /* 프로세스 종료 시 발생할 수 있는 오류 방지 */ }
        }
    }

    // 편의용 래퍼 메서드들
    public void UpdateStatus(string message) => Send("OPCODE", message);
    public void UpdateNet(bool connected) => Send("NET", connected ? "Online" : "Offline");
    public void UpdateServer(bool connected) => Send("SERVER", connected ? "Online" : "Offline");
}