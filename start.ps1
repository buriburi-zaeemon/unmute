# PowerShell Launcher for UNMUTE Sign Language Translator
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Starting UNMUTE Sign Language Translator        " -ForegroundColor Yellow
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

Write-Host "[*] Using Python: $pythonExe" -ForegroundColor Green

& $pythonExe "$scriptDir\run.py" $args
