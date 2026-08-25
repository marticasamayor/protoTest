@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [setup] Creant entorn virtual...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo [error] No s'ha pogut crear l'entorn virtual. Cal Python instal·lat.
        pause
        exit /b 1
    )
    echo [setup] Instal·lant dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

".venv\Scripts\python.exe" main.py

if errorlevel 1 pause
