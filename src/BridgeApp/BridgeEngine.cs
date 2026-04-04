using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Net.NetworkInformation;
using Microsoft.AspNetCore.SignalR.Client;

public class BridgeEngine
{
    private HubConnection? _connection;
    private SerialPort? _rs485Port;
    private List<string> _detectedNodeIds = new();
    private bool _isScanning = false;

    // --- 부팅 단계 ---

    public async Task StartAsync()
    {
        UpdateLcd("System Booting...");

        // 1. 인터넷 및 Tailscale 확인
        while (!CheckInternet()) {
            UpdateLcd("Waiting for Network...");
            await Task.Delay(3000);
        }

        // 2. 메인프레임 세션 연결 (SignalR)
        _connection = new HubConnectionBuilder()
            .WithUrl("http://100.64.x.x:5000/bridgeHub") // Headscale IP 사용
            .WithAutomaticReconnect()
            .Build();

        await _connection.StartAsync();
        UpdateLcd("Mainframe Connected!");

        // 3. 커맨드보드 스캔
        await ScanCommandBoards();

        // 4. 스캔 결과 보고
        await _connection.InvokeAsync("ReportNodes", _detectedNodeIds);
        
        // --- 상시 모드 진입 ---
        _isScanning = true;
        RunMainLoop();
    }

    private bool CheckInternet() 
    {
        try {
            using var ping = new Ping();
            var reply = ping.Send("8.8.8.8", 2000);
            return reply.Status == IPStatus.Success;
        } catch { return false; }
    }

    // --- 상시 단계 ---

    private async void RunMainLoop()
    {
        while (_isScanning)
        {
            foreach (var id in _detectedNodeIds)
            {
                // 데이터 획득 -> 파싱 -> 전송
                string rawData = SendRs485Request(id);
                if (!string.IsNullOrEmpty(rawData))
                {
                    var parsedData = ParsePacket(id, rawData);
                    await _connection.InvokeAsync("PushData", parsedData);
                }
            }
            await Task.Delay(1000); // 주기 설정
        }
    }

    private void UpdateLcd(string message)
    {
        // LCDWiki 3.5" 디스플레이에 상태 출력 로직
        // CLI 환경이라면 Console.WriteLine과 동시에 
        // /dev/fb1 프레임버퍼에 텍스트를 쓰는 로직이 들어갑니다.
        Console.WriteLine($"[STATUS] {message}");
    }
}