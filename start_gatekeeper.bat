@echo off
SETLOCAL EnableDelayedExpansion
TITLE Gatekeeper System - Starting...
echo ==========================================
echo   🛡️ INICIANDO SISTEMA GATEKEEPER MT5
echo ==========================================
echo.

cd /d "%~dp0"

:: 1. Iniciar MetaTrader 5 si no está abierto
echo [1/3] Verificando MetaTrader 5...
tasklist /FI "IMAGENAME eq terminal64.exe" 2>NUL | find /I /N "terminal64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MetaTrader 5 ya está abierto.
) else (
    echo [INFO] Iniciando MetaTrader 5...
    start "" "C:\Program Files\VT Markets (Pty) MT5 Terminal\terminal64.exe"
    :: Esperar unos segundos a que MT5 cargue
    timeout /t 10 /nobreak > NUL
)

:: 2. Detectar Python
set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo [INFO] Usando entorno virtual detectado.
)

:: 3. Iniciar API
echo [2/3] Iniciando API Bridge (Puerto 8000)...
start "Gatekeeper API" %PYTHON_EXE% scripts\gatekeeper_api.py

:: 4. Iniciar Bot de Telegram (Opcional si usas n8n)
echo [3/3] Iniciando Bot de Telegram...
:: Si prefieres que n8n gestione todo, puedes comentar la línea de abajo con '::'
start "Gatekeeper Bot" %PYTHON_EXE% scripts\gatekeeper_bot.py

echo.
echo ✅ TODO EL SISTEMA ESTA EN MARCHA.
echo 🚀 No cierres las ventanas que se han abierto.
echo.
pause
