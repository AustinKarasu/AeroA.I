# Start AeroA.I (PowerShell)
Set-Location -Path $PSScriptRoot
if (Test-Path ".venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe aero.py
} else {
    Write-Host "Virtual environment not found. Run .\setup_aero.bat first."
    exit 1
}
