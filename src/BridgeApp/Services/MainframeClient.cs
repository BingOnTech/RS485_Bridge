using Microsoft.AspNetCore.SignalR.Client;

namespace BridgeApp.Services;

public class MainframeClient
{
    private HubConnection _connection;

    public async Task ConnectAsync(string url)
    {
        _connection = new HubConnectionBuilder()
            .WithUrl(url).WithAutomaticReconnect().Build();

        await _connection.StartAsync();
    }

    public bool IsConnected => _connection?.State == HubConnectionState.Connected;

    public async Task PushData(object data) => await _connection.InvokeAsync("ReceiveData", data);
}