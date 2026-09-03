@echo off
setlocal

echo ========================================================
echo        Stopping Unmute ASL Translation Server
echo ========================================================

:: Detect Python from virtual environment
if exist "..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=..\.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" "%~dp0stop.py" %*

pause
