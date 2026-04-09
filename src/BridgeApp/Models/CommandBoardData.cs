using System.Collections.Generic;

namespace BridgeApp.Models;

public class CommandBoardData
{
    public string BridgeName { get; set; } = "";
    public string BoardId { get; set; } = "";
    public List<Chamber> Chambers { get; set; } = new();
    public DateTime CapturedAt { get; set; } = DateTime.Now;
}