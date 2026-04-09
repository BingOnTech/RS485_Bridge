namespace BridgeApp.Models;

public class Chamber
{
    public int Index { get; set; }           // 1 ~ 4번 챔버
    public bool LevelHigh { get; set; }      // 수위 H
    public bool LevelLow { get; set; }       // 수위 L
    public bool ValveInOpen { get; set; }    // 급수 밸브
    public bool ValveOutOpen { get; set; }   // 배수 밸브
    public double Temperature { get; set; }  // 온도
}