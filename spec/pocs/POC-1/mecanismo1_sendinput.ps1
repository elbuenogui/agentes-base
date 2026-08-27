# Mecanismo 1 — teclado sintético (SendInput + KEYEVENTF_UNICODE)
# Uso: .\mecanismo1_sendinput.ps1 -TituloContem "WhatsApp"
# Checagem de segurança: só digita se a janela em foco AGORA tiver esse texto no título.
param(
    [Parameter(Mandatory=$true)][string]$TituloContem,
    [string]$TextoPath = "spec/pocs/POC-1/texto_teste.txt"
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32Input {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [StructLayout(LayoutKind.Sequential)]
    public struct KEYBDINPUT {
        public ushort wVk;
        public ushort wScan;
        public uint dwFlags;
        public uint time;
        public IntPtr dwExtraInfo;
    }
    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT {
        public uint type;
        public KEYBDINPUT ki;
        public uint padding1;
        public uint padding2;
    }
    public const uint INPUT_KEYBOARD = 1;
    public const uint KEYEVENTF_UNICODE = 0x0004;
    public const uint KEYEVENTF_KEYUP = 0x0002;

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
}
"@

$h = [Win32Input]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32Input]::GetWindowText($h, $sb, 256) | Out-Null
$tituloAtual = $sb.ToString()

if ($tituloAtual -notlike "*$TituloContem*") {
    Write-Host "ABORTADO - janela em foco e '$tituloAtual', nao contem '$TituloContem'. Nada foi digitado." -ForegroundColor Red
    exit 1
}

Write-Host "Janela em foco confirmada: '$tituloAtual'. Digitando em 2 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$texto = Get-Content -Raw -Encoding UTF8 $TextoPath
$sw = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($ch in $texto.ToCharArray()) {
    $code = [uint16][int]$ch
    $down = New-Object Win32Input+INPUT
    $down.type = [Win32Input]::INPUT_KEYBOARD
    $down.ki.wVk = 0
    $down.ki.wScan = $code
    $down.ki.dwFlags = [Win32Input]::KEYEVENTF_UNICODE
    $up = New-Object Win32Input+INPUT
    $up.type = [Win32Input]::INPUT_KEYBOARD
    $up.ki.wVk = 0
    $up.ki.wScan = $code
    $up.ki.dwFlags = [Win32Input]::KEYEVENTF_UNICODE -bor [Win32Input]::KEYEVENTF_KEYUP

    $inputs = @($down, $up)
    [Win32Input]::SendInput(2, $inputs, [System.Runtime.InteropServices.Marshal]::SizeOf([type][Win32Input+INPUT])) | Out-Null
}

$sw.Stop()
Write-Host "Concluido em $($sw.Elapsed.TotalSeconds) s." -ForegroundColor Green
