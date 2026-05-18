@echo off
REM Start AeroA.I desktop UI (Windows)
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe aero_ui.py
) else (
  py -3 aero_ui.py
)
if errorlevel 1 pause
