@echo off
setlocal

echo ========================================================
echo        Starting UNMUTE Sign Language Translator
echo ========================================================

:: Detect Python from virtual environment
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else if exist "%~dp0..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Using Python: %PYTHON_EXE%

:: Launch run.py with all passed arguments
"%PYTHON_EXE%" "%~dp0run.py" %*

if %errorlevel% neq 0 (
    echo [-] Error starting UNMUTE server.
    pause
)
