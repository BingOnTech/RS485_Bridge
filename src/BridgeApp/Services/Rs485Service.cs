using System.IO.Ports;
using BridgeApp.Models;

namespace BridgeApp.Services;

public class Rs485Service
{
    private SerialPort? _port;

    // 🌟 외부에서 포트 상태를 확인할 수 있도록 공개!
    public bool IsOpen => _port != null && _port.IsOpen;

    public void Open(string portName)
    {
        if (_port != null && _port.IsOpen) _port.Close();

        _port = new SerialPort(portName, 9600, Parity.None, 8, StopBits.One);
        _port.ReadTimeout = 500;
        _port.WriteTimeout = 500;
        _port.Open();
    }

    public string SendRequest(string command)
    {
        // 🌟 _port가 null일 경우를 대비한 체크
        if (_port == null || !_port.IsOpen) return "";

        try
        {
            _port.DiscardInBuffer();
            _port.Write(command);

            // 🌟 1.2초는 꽤 긴 시간입니다. 장비가 빠르다면 200~500ms로 줄여보세요!
            Thread.Sleep(1200);

            return _port.ReadExisting();
        }
        catch
        {
            return "";
        }
    }
    public CommandBoardData Parse(string raw)
    {
        var data = new CommandBoardData();
        // 최소 길이 검증 ($ + ID(2) + Level(2) + Valve(2) + Temp(5*4) + Checksum(2) = 29자 이상)
        if (string.IsNullOrEmpty(raw) || raw.Length < 27) return data;

        data.BoardId = raw.Substring(1, 2);
        byte levelByte = Convert.ToByte(raw.Substring(3, 2), 16);
        byte valveByte = Convert.ToByte(raw.Substring(5, 2), 16);

        for (int i = 0; i < 4; i++)
        {
            int shift = i * 2;
            var chamber = new Chamber { Index = i + 1 };

            // 비트 추출 (파이썬 로직 이식)
            chamber.LevelLow = ((levelByte >> shift) & 1) == 1;
            chamber.LevelHigh = ((levelByte >> (shift + 1)) & 1) == 1;
            chamber.ValveInOpen = ((valveByte >> shift) & 1) == 1;
            chamber.ValveOutOpen = ((valveByte >> (shift + 1)) & 1) == 1;

            // 온도 파싱
            string tempStr = raw.Substring(7 + (i * 5), 5);
            if (double.TryParse(tempStr, out double t)) chamber.Temperature = t;

            data.Chambers.Add(chamber);
        }
        return data;
    }
}