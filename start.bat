@echo off
setlocal

echo ========================================================
echo        Starting SignBridge ASL Translation System
echo ========================================================

:: Detect Python from virtual environment
if exist "..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=..\.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Using Python: %PYTHON_EXE%

:: Launch run.py with all passed arguments
"%PYTHON_EXE%" "%~dp0run.py" %*

pause
