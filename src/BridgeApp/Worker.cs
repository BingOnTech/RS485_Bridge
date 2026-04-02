using System.IO.Ports;

namespace BridgeApp;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private SerialPort _serialPort;

    public Worker(ILogger<Worker> logger)
    {
        _logger = logger;

        string portName = Environment.GetEnvironmentVariable("SERIAL_PORT") ?? "COM4";
        _serialPort = new SerialPort(portName, 9600);
        _serialPort.ReadTimeout = 1000;
    }

    public override Task StartAsync(CancellationToken cancellationToken)
    {
        try
        {
            _serialPort.Open();
            _logger.LogInformation("✅ 시리얼 포트({PortName}) 열기 성공!", _serialPort.PortName);
        }
        catch (Exception ex)
        {
            _logger.LogError("❌ 포트 열기 실패: {Message}", ex.Message);
        }

        return base.StartAsync(cancellationToken);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // 프로그램이 종료(Ctrl+C)될 때까지 무한 루프
        while (!stoppingToken.IsCancellationRequested)
        {
            if (_serialPort != null && _serialPort.IsOpen)
            {
                try
                {
                    // 1. 입력 버퍼 비우기 (파이썬의 reset_input_buffer)
                    _serialPort.DiscardInBuffer();

                    // 2. 명령어 전송 [Tx]
                    string command = "$$0110;\r";
                    _serialPort.Write(command);
                    _logger.LogInformation("[Tx] 보냄: {Command}", command.Trim());

                    // 3. 응답 수신 [Rx]
                    string response = _serialPort.ReadLine();
                    _logger.LogInformation("[Rx] 받음: {Response}", response.Trim());
                }
                catch (TimeoutException)
                {
                    _logger.LogWarning("[Rx] 응답 없음 (Timeout)");
                }
                catch (Exception ex)
                {
                    _logger.LogError("⚠️ 통신 에러: {Message}", ex.Message);
                }
            }

            // 1초 대기 (파이썬의 time.sleep(1)과 동일)
            await Task.Delay(1000, stoppingToken);
        }
    }

    public override Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("🛑 프로그램 종료. 포트를 닫습니다.");
        if (_serialPort != null && _serialPort.IsOpen)
        {
            _serialPort.Close();
        }
        return base.StopAsync(cancellationToken);
    }
}