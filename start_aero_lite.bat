@echo off
REM Start AeroA.I Lite (Windows)
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe aero_lite.py
) else (
  py -3 aero_lite.py
)
