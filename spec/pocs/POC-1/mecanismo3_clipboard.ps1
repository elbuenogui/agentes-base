# Mecanismo 3 - area de transferencia (salvar, colar, restaurar)
# Precisa rodar em thread STA: powershell -sta -File mecanismo3_clipboard.ps1 -TituloContem "WhatsApp"
param(
    [Parameter(Mandatory=$true)][string]$TituloContem,
    [string]$TextoPath = "spec/pocs/POC-1/texto_teste.txt"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32Check3 {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [StructLayout(LayoutKind.Sequential)]
    public struct KEYBDINPUT { public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT { public uint type; public KEYBDINPUT ki; public uint padding1; public uint padding2; }
    public const uint INPUT_KEYBOARD = 1;
    public const uint KEYEVENTF_KEYUP = 0x0002;
    public const ushort VK_CONTROL = 0x11;
    public const ushort VK_V = 0x56;

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
}
"@

$h = [Win32Check3]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32Check3]::GetWindowText($h, $sb, 256) | Out-Null
$tituloAtual = $sb.ToString()

if ($tituloAtual -notlike "*$TituloContem*") {
    Write-Host "ABORTADO - janela em foco e '$tituloAtual', nao contem '$TituloContem'. Nada foi colado." -ForegroundColor Red
    exit 1
}
Write-Host "Janela em foco confirmada: '$tituloAtual'." -ForegroundColor Yellow

# 1) Salvar conteudo original do clipboard, por formato
$formatosOriginais = [System.Windows.Forms.Clipboard]::GetDataObject().GetFormats()
Write-Host "Formatos originais no clipboard: $($formatosOriginais -join ', ')"

$origemTexto = $null
$origemImagem = $null
$origemArquivos = $null
if ([System.Windows.Forms.Clipboard]::ContainsText()) {
    $origemTexto = [System.Windows.Forms.Clipboard]::GetText()
} elseif ([System.Windows.Forms.Clipboard]::ContainsImage()) {
    $origemImagem = [System.Windows.Forms.Clipboard]::GetImage()
} elseif ([System.Windows.Forms.Clipboard]::ContainsFileDropList()) {
    $origemArquivos = [System.Windows.Forms.Clipboard]::GetFileDropList()
}

# 2) Colocar texto de teste no clipboard e colar
$texto = Get-Content -Raw -Encoding UTF8 $TextoPath
[System.Windows.Forms.Clipboard]::SetText($texto)
$swExposicao = [System.Diagnostics.Stopwatch]::StartNew()

Start-Sleep -Milliseconds 300
$down1 = New-Object Win32Check3+INPUT; $down1.type = [Win32Check3]::INPUT_KEYBOARD; $down1.ki.wVk = [Win32Check3]::VK_CONTROL
$down2 = New-Object Win32Check3+INPUT; $down2.type = [Win32Check3]::INPUT_KEYBOARD; $down2.ki.wVk = [Win32Check3]::VK_V
$up2   = New-Object Win32Check3+INPUT; $up2.type   = [Win32Check3]::INPUT_KEYBOARD; $up2.ki.wVk   = [Win32Check3]::VK_V;      $up2.ki.dwFlags = [Win32Check3]::KEYEVENTF_KEYUP
$up1   = New-Object Win32Check3+INPUT; $up1.type   = [Win32Check3]::INPUT_KEYBOARD; $up1.ki.wVk   = [Win32Check3]::VK_CONTROL; $up1.ki.dwFlags = [Win32Check3]::KEYEVENTF_KEYUP
$inputs = @($down1, $down2, $up2, $up1)
[Win32Check3]::SendInput(4, $inputs, [System.Runtime.InteropServices.Marshal]::SizeOf([type][Win32Check3+INPUT])) | Out-Null
Write-Host "Ctrl+V enviado."

Start-Sleep -Milliseconds 700

# 3) Restaurar clipboard original
if ($null -ne $origemTexto) {
    [System.Windows.Forms.Clipboard]::SetText($origemTexto)
} elseif ($null -ne $origemImagem) {
    [System.Windows.Forms.Clipboard]::SetImage($origemImagem)
} elseif ($null -ne $origemArquivos) {
    $sc = New-Object System.Collections.Specialized.StringCollection
    foreach ($f in $origemArquivos) { $sc.Add($f) | Out-Null }
    [System.Windows.Forms.Clipboard]::SetFileDropList($sc)
} else {
    [System.Windows.Forms.Clipboard]::Clear()
}
$swExposicao.Stop()
Write-Host "Clipboard restaurado. Texto de teste ficou exposto por $($swExposicao.Elapsed.TotalSeconds) s."

# 4) Verificar fidelidade da restauracao (so para o caso texto)
if ($null -ne $origemTexto) {
    $agora = [System.Windows.Forms.Clipboard]::GetText()
    $bate = ($agora -ceq $origemTexto)
    Write-Host "Restauracao de texto identica ao original: $bate"
}
