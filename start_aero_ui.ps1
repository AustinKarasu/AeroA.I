# Start AeroA.I desktop UI (PowerShell)
Set-Location -Path $PSScriptRoot
if (Test-Path ".venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe aero_ui.py
} else {
    py -3 aero_ui.py
}
if ($LASTEXITCODE -ne 0) {
    Read-Host "Aero UI exited with an error. Press Enter to close"
}
