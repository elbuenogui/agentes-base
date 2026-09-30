@echo off
rem Duplo clique: roda os cinco casos de teste contra a Edge Function "transcrever-servico" do Supabase.
rem Pede a chave do servico (SERVICO_CHAVE_MARI); ela nao aparece na tela. O caso 4 e uma chamada paga
rem (centavos). O caso 5 pausa e pede que voce crie o segredo SERVICO_TETO_DIARIO_USD = 0 no painel;
rem no fim, APAGUE esse segredo. O resultado fica tambem em testar_servico.log, nesta pasta (sem texto
rem nem chave).
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
        "%PY_VENV%" testar_servico.py %*
        goto fim
    )
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: py -3
    py -3 testar_servico.py %*
    goto fim
)

python --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: python
    python testar_servico.py %*
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
