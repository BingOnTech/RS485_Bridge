using System.Security.Cryptography;
using System.Text;

namespace BridgeApp.Services;

public static class CryptoUtil
{
    private static readonly string? Base64Key = Environment.GetEnvironmentVariable("ENCRYPTION_KEY");

    public static string Encrypt(string plainText)
    {
        if (string.IsNullOrEmpty(Base64Key)) return plainText;

        byte[] key = Convert.FromBase64String(Base64Key);
        using var aes = Aes.Create();
        aes.Key = key;
        aes.GenerateIV(); // 매번 새로운 IV 생성

        using var encryptor = aes.CreateEncryptor(aes.Key, aes.IV);
        using var ms = new MemoryStream();
        
        // IV를 패킷 앞에 붙여서 전송 (복호화 시 필요)
        ms.Write(aes.IV, 0, aes.IV.Length);

        using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
        using (var sw = new StreamWriter(cs))
        {
            sw.Write(plainText);
        }

        return Convert.ToBase64String(ms.ToArray());
    }

    public static string Decrypt(string cipherText)
    {
        if (string.IsNullOrEmpty(Base64Key)) return cipherText;

        byte[] fullCipher = Convert.FromBase64String(cipherText);
        byte[] key = Convert.FromBase64String(Base64Key);
        
        using var aes = Aes.Create();
        aes.Key = key;

        byte[] iv = new byte[aes.BlockSize / 8];
        byte[] cipher = new byte[fullCipher.Length - iv.Length];

        Buffer.BlockCopy(fullCipher, 0, iv, 0, iv.Length);
        Buffer.BlockCopy(fullCipher, iv.Length, cipher, 0, cipher.Length);

        using var decryptor = aes.CreateDecryptor(aes.Key, iv);
        using var ms = new MemoryStream(cipher);
        using var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read);
        using var sr = new StreamReader(cs);

        return sr.ReadToEnd();
    }
}