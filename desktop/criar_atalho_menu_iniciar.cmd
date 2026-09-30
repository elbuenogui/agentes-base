@echo off
rem Duplo clique aqui uma vez: cria o atalho "Transcritor" no Menu Iniciar.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_menu_iniciar.ps1"
pause
