@echo off
rem Duplo clique: importa o historico do transcritor (consumo.jsonl e transcricoes.jsonl)
rem para o Supabase. Pede e-mail e senha; a senha nao aparece na tela.
rem Pode rodar mais de uma vez: nada duplica. Para so conferir os totais: importar_historico.cmd --simular
rem A saida tambem fica em importar_historico.log, nesta pasta (sem e-mail, senha nem texto).
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
        "%PY_VENV%" importar_historico.py %*
        goto fim
    )
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: py -3
    py -3 importar_historico.py %*
    goto fim
)

python --version >nul 2>nul
if not errorlevel 1 (
    echo Usando: python
    python importar_historico.py %*
    goto fim
)

echo.
echo ERRO: nenhum Python encontrado para rodar o importador.
echo Tentei, nesta ordem: %PY_VENV%, "py -3" e "python".
echo Instale o Python de python.org (marcando "Add python.exe to PATH") ou recrie o
echo ambiente do transcritor, e rode este arquivo de novo.

:fim
echo.
pause
