@echo off
REM Setup AeroA.I environment (Windows)
cd /d "%~dp0"
set "PYTHON_CMD=py -3.8"
py -3.8 --version >nul 2>&1
if errorlevel 1 set "PYTHON_CMD=py -3"
if not exist ".venv" (
  %PYTHON_CMD% -m venv .venv
  call .venv\Scripts\activate
  python -m pip install --upgrade pip
  if exist PyAudio-0.2.11-cp38-cp38-win_amd64.whl pip install PyAudio-0.2.11-cp38-cp38-win_amd64.whl
  pip install -r requirements.txt
  echo Setup complete. Running image helper to place Aero image.
  python write_aero_image.py
  echo Setup complete. Run start_aero.bat to launch AeroA.I
) else (
  echo Virtual environment already exists.
  call .venv\Scripts\activate
  python -m pip install --upgrade pip
  if exist PyAudio-0.2.11-cp38-cp38-win_amd64.whl pip install PyAudio-0.2.11-cp38-cp38-win_amd64.whl
  pip install -r requirements.txt
  echo Ensuring Aero image is present.
  python write_aero_image.py
)
echo Done.
