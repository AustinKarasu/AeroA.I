# Start AeroA.I Lite (PowerShell)
Set-Location -Path $PSScriptRoot
if (Test-Path ".venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe aero_lite.py
} else {
    py -3 aero_lite.py
}
