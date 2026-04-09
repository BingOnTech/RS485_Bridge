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
            // 라즈베리파이 경로에 맞는 파이썬 스크립트 실행
            _pythonProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "python3",
                    Arguments = "bridge_lcd.py", // 파이썬 파일명
                    UseShellExecute = false,
                    RedirectStandardInput = true,
                    CreateNoWindow = true
                }
            };
            _pythonProcess.Start();
            _inputStream = _pythonProcess.StandardInput;
            UpdateStatus("System", "Booting...");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[LCD Error] Failed to start Python LCD script: {ex.Message}");
        }
    }

    // 파이썬으로 "키:값" 형태의 메시지를 보냄
    private void SendToPython(string key, string value)
    {
        if (_inputStream != null && _pythonProcess != null && !_pythonProcess.HasExited)
        {
            _inputStream.WriteLine($"{key}|{value}");
            _inputStream.Flush();
        }
    }

    public void UpdateStatus(string category, string message) => SendToPython("STATUS", $"{category}: {message}");
    public void UpdateNet(bool connected) => SendToPython("NET", connected ? "Connected" : "Disconnected");
    public void UpdateMainframe(bool connected) => SendToPython("MAINFRAME", connected ? "Online" : "Offline");
    public void UpdateOpCode(string code) => SendToPython("OPCODE", code);
}