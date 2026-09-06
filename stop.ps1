# PowerShell Shutdown Script for UNMUTE Sign Language Translator
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Stopping UNMUTE Sign Language Translator        " -ForegroundColor Red
Write-Host "========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Detect virtual environment python
if (Test-Path "$scriptDir\.venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\.venv\Scripts\python.exe"
} elseif (Test-Path "$scriptDir\..\.venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\..\.venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

& $pythonExe "$scriptDir\stop.py" $args
