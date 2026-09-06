@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo       UNMUTE Environment Setup (Python 3.11 + PyTorch)
echo ========================================================

:: Check if Python 3.11 is available
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python 3.11 was not detected via 'py -3.11'.
    echo [*] Checking for default python...
    python --version
) else (
    echo [+] Detected Python 3.11
    set "PY_CMD=py -3.11"
)

if "%PY_CMD%"=="" set "PY_CMD=python"

echo [*] Initializing virtual environment in .venv...
%PY_CMD% -m venv --clear .venv

if %errorlevel% neq 0 (
    echo [-] Failed to create virtual environment!
    exit /b 1
)

echo [+] Virtual environment created successfully.
echo [*] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo [*] Installing PyTorch with CUDA 12.1 or CPU support...
:: Attempt CUDA installation first; fallback to CPU if needed
.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
if %errorlevel% neq 0 (
    echo [*] Falling back to default PyTorch installation...
    .venv\Scripts\python.exe -m pip install torch torchvision
)

echo [*] Installing remaining dependencies from requirements.txt...
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo ========================================================
echo [*] Verifying Installation:
.venv\Scripts\python.exe -c "import torch, cv2, mediapipe, sklearn; print('PyTorch:', torch.__version__, '| CUDA:', torch.cuda.is_available(), '| OpenCV:', cv2.__version__, '| MediaPipe:', mediapipe.__version__)"
echo ========================================================
echo [+] Setup complete! You can now activate via: .venv\Scripts\activate
pause
