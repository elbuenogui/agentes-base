' Abre o transcritor com um clique, sem janela de terminal.
' 1. Sobe o nucleo (transcritor/, porta 8000) se ele ainda nao estiver no ar.
' 2. Abre o app de desktop (desktop/app.py), a menos que ja esteja aberto.
' Chamado pelo atalho "Transcritor" do Menu Iniciar (criado por criar_atalho_menu_iniciar.cmd).
' Excecao de PM autorizada pelo usuario em 2026-09-28 (ver PLANO.md e coleta/).
Option Explicit

Dim sh, fso, pastaDesktop, pastaNucleo, i
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
pastaDesktop = fso.GetParentFolderName(WScript.ScriptFullName)
pastaNucleo = fso.GetParentFolderName(pastaDesktop) & "\transcritor"

' Qualquer resposta HTTP na porta 8000 conta como "no ar".
Function NucleoNoAr()
    Dim h
    On Error Resume Next
    Set h = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    h.setTimeouts 1000, 1000, 1000, 1000
    h.open "GET", "http://127.0.0.1:8000/consumo", False
    h.send
    NucleoNoAr = (Err.Number = 0)
    On Error GoTo 0
End Function

' Procura um python rodando o app.py desta pasta.
Function AppAberto()
    Dim wmi, procs, p
    AppAberto = False
    On Error Resume Next
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Set procs = wmi.ExecQuery("SELECT CommandLine FROM Win32_Process WHERE Name LIKE 'python%'")
    For Each p In procs
        If Not IsNull(p.CommandLine) Then
            If InStr(1, p.CommandLine, "app.py", vbTextCompare) > 0 Then AppAberto = True
        End If
    Next
    On Error GoTo 0
End Function

If Not NucleoNoAr() Then
    sh.CurrentDirectory = pastaNucleo
    sh.Run "cmd /c "".venv\Scripts\uvicorn.exe main:app --app-dir backend --port 8000 >> uvicorn_out.log 2>> uvicorn_err.log""", 0, False
    ' Espera o nucleo responder (ate ~30 s) antes de abrir o app.
    For i = 1 To 30
        WScript.Sleep 1000
        If NucleoNoAr() Then Exit For
    Next
    If Not NucleoNoAr() Then
        MsgBox "O nucleo do transcritor nao subiu em 30 s." & vbCrLf & _
               "Veja transcritor\uvicorn_err.log.", vbExclamation, "Transcritor"
        WScript.Quit 1
    End If
End If

If AppAberto() Then
    MsgBox "O transcritor ja esta aberto.", vbInformation, "Transcritor"
    WScript.Quit 0
End If

sh.CurrentDirectory = pastaDesktop
sh.Run "cmd /c ""python app.py >> saida_app.log 2>> erro_app.log""", 0, False
