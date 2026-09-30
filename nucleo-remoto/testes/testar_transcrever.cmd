@echo off
rem Duplo clique: roda os seis casos de teste contra a Edge Function "transcrever" do Supabase.
rem Pede e-mail e senha; a senha nao aparece na tela. Os casos 2 e 3 sao chamadas pagas (centavos).
rem O resultado fica tambem em testar_transcrever.log, nesta pasta (sem texto, e-mail, senha nem token).
rem
rem Ordem de busca do Python: o do ambiente do transcritor, depois "py -3", depois "python".
rem Cada um e testado com --version antes (o "python" do atalho da Microsoft Store falha aqui).
chcp 65001 >nul
cd /d "%~dp0"

set "PY_VENV=..\..\transcritor\.venv\Scripts\python.exe"
if exist "%PY_VENV%" (
    "%PY_VENV%" --version >nul 2>nul
    if not errorlevel 1 (
        echo Usando o Python do transcritor: %PY_VENV%
        "%PY_VENV%" testar_transcrever.py %*
        goto fim
    )
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: py -3
    py -3 testar_transcrever.py %*
    goto fim
)

python --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: python
    python testar_transcrever.py %*
    goto fim
)

echo.
echo ERRO: nenhum Python encontrado para rodar o teste.
echo Tentei, nesta ordem: %PY_VENV%, "py -3" e "python".
echo Instale o Python de python.org (marcando "Add python.exe to PATH") ou recrie o
echo ambiente do transcritor, e rode este arquivo de novo.

:fim
echo.
pause
