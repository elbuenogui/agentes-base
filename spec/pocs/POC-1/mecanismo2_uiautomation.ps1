# Mecanismo 2 - API de acessibilidade (UI Automation, ValuePattern/TextPattern)
# Uso: .\mecanismo2_uiautomation.ps1 -TituloContem "WhatsApp"
# Checagem de seguranca: so digita se a janela em foco AGORA tiver esse texto no titulo.
param(
    [Parameter(Mandatory=$true)][string]$TituloContem,
    [string]$TextoPath = "spec/pocs/POC-1/texto_teste.txt"
)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32Check2 {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@

$h = [Win32Check2]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32Check2]::GetWindowText($h, $sb, 256) | Out-Null
$tituloAtual = $sb.ToString()

if ($tituloAtual -notlike "*$TituloContem*") {
    Write-Host "ABORTADO - janela em foco e '$tituloAtual', nao contem '$TituloContem'. Nada foi digitado." -ForegroundColor Red
    exit 1
}

Write-Host "Janela em foco confirmada: '$tituloAtual'." -ForegroundColor Yellow

$focused = [System.Windows.Automation.AutomationElement]::FocusedElement
if ($null -eq $focused) {
    Write-Host "ABORTADO - nao encontrei elemento focado via UI Automation." -ForegroundColor Red
    exit 1
}

$nome = $focused.Current.Name
$tipo = $focused.Current.ControlType.ProgrammaticName
$classe = $focused.Current.ClassName
Write-Host "Elemento focado: Nome='$nome' Tipo='$tipo' Classe='$classe'"

$temValuePattern = $false
$temTextPattern = $false
try {
    $vpObj = $null
    $temValuePattern = $focused.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$vpObj)
} catch {}
try {
    $tpObj = $null
    $temTextPattern = $focused.TryGetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern, [ref]$tpObj)
} catch {}
Write-Host "ValuePattern disponivel: $temValuePattern | TextPattern disponivel: $temTextPattern"

$texto = Get-Content -Raw -Encoding UTF8 $TextoPath
$sw = [System.Diagnostics.Stopwatch]::StartNew()

if ($temValuePattern) {
    try {
        $vp = $vpObj -as [System.Windows.Automation.ValuePattern]
        $vp.SetValue($texto)
        $sw.Stop()
        Write-Host "SUCESSO via ValuePattern.SetValue em $($sw.Elapsed.TotalSeconds) s." -ForegroundColor Green
    } catch {
        $sw.Stop()
        Write-Host "ERRO ao chamar ValuePattern.SetValue: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    $sw.Stop()
    Write-Host "SEM ValuePattern no elemento focado - nao deu para inserir texto por este caminho." -ForegroundColor Red
}
