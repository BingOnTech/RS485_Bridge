using BridgeApp;
using BridgeApp.Services;
using BridgeApp.Models;

// 1. 환경변수에서 설정값 읽기 (하드코딩 완전 제거)
string? serverUrl = Environment.GetEnvironmentVariable("MAINFRAME_URL");
string? bridgeName = Environment.GetEnvironmentVariable("BRIDGE_NAME") ?? "Unknown_Bridge";

if (string.IsNullOrEmpty(serverUrl))
{
    Console.WriteLine("오류: 환경변수 MAINFRAME_URL이 설정되지 않았습니다.");
    return;
}

// 2. 클라이언트 초기화 및 접속
var client = new MainframeClient();
Console.WriteLine($"메인프레임 연결 시도: {serverUrl}");

try
{
    await client.ConnectAsync(serverUrl);
    Console.WriteLine($"[{bridgeName}] 메인프레임에 성공적으로 연결되었습니다.");
}
catch (Exception ex)
{
    // 연결 실패해도 엔진은 돌아가야 하므로 로그만 남김 (SignalR이 자동 재접속 시도함)
    Console.WriteLine($"초기 연결 실패 (재접속 대기): {ex.Message}");
}

// 3. 엔진 실행 (이제 정상적으로 호출됩니다)
// 팁: 필요하다면 client 객체를 엔진에 넘겨서 실시간 데이터를 쏘게 할 수 있습니다.
var engine = new BridgeEngine(client);
await engine.RunAsync();