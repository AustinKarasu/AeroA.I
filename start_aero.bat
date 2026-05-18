@echo off
REM Start AeroA.I (Windows)
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe aero.py --no-auth
) else (
  echo Virtual environment not found. Run setup_aero.bat first.
  pause
  exit /b 1
)
