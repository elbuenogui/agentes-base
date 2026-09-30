@echo off
rem Duplo clique: testa a Edge Function "consumo" e a imagem registrando no banco (Etapa 4).
rem Pede e-mail e senha; a senha nao aparece na tela. Sobe um segundo nucleo na porta 8001 (o da 8000
rem nao e tocado) e gera UMA imagem paga - mostra o custo e pede Enter antes.
rem O resultado fica tambem em testar_consumo_e_imagem.log, nesta pasta (sem e-mail, senha, token, prompt nem texto).
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
        "%PY_VENV%" testar_consumo_e_imagem.py %*
        goto fim
    )
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: py -3
    py -3 testar_consumo_e_imagem.py %*
    goto fim
)

python --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: python
    python testar_consumo_e_imagem.py %*
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
