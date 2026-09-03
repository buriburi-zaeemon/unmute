# PowerShell Shutdown Script for Unmute ASL Translation System
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Stopping Unmute ASL Translation Server       " -ForegroundColor Red
Write-Host "========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Detect virtual environment python
if (Test-Path "$scriptDir\..\.venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\..\.venv\Scripts\python.exe"
} elseif (Test-Path "$scriptDir\.venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\.venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

& $pythonExe "$scriptDir\stop.py" $args
