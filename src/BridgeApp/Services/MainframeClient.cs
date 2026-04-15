using Microsoft.AspNetCore.SignalR.Client;

namespace BridgeApp.Services;

public class MainframeClient
{
    private HubConnection? _connection;

    public async Task ConnectAsync(string url)
    {
        _connection = new HubConnectionBuilder()
            .WithUrl(url)
            .WithAutomaticReconnect() // 알아서 끊기면 다시 붙음
            .Build();

        await _connection.StartAsync();
    }

    public bool IsConnected => _connection?.State == HubConnectionState.Connected;

    public async Task PushData(object data)
    {
        if (IsConnected && _connection != null)
        {
            await _connection.InvokeAsync("ReceiveData", data);
        }
    }
}