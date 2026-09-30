# Cria (ou recria) o atalho "Transcritor" no Menu Iniciar apontando para abrir_transcritor.vbs.
# Rodar uma vez so; rodar de novo apenas atualiza o atalho.
$vbs = Join-Path $PSScriptRoot 'abrir_transcritor.vbs'
$lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'Transcritor.lnk'
$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$s.TargetPath = "$env:SystemRoot\System32\wscript.exe"
$s.Arguments = '"' + $vbs + '"'
$s.WorkingDirectory = $PSScriptRoot
$s.IconLocation = "$env:SystemRoot\System32\SndVol.exe,0"
$s.Description = 'Sobe o nucleo e abre o transcritor'
$s.Save()
Write-Host "Atalho criado: $lnk"
