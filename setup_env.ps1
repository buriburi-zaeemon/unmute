# UNMUTE Environment Setup Script (PowerShell)
# Sets up Python 3.11 with PyTorch (CUDA/CPU), MediaPipe, OpenCV, and project dependencies.

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      UNMUTE Environment Setup (Python 3.11 + PyTorch)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$pyVersion = py -3.11 --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] Detected Python 3.11 ($pyVersion)" -ForegroundColor Green
    $pyCmd = "py -3.11"
} else {
    Write-Host "[!] 'py -3.11' not found, using default 'python' command" -ForegroundColor Yellow
    $pyCmd = "python"
}

Write-Host "[*] Creating virtual environment in .venv..." -ForegroundColor Cyan
& py -3.11 -m venv --clear .venv
if ($LASTEXITCODE -ne 0) {
    & python -m venv --clear .venv
}

if (!(Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[-] Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Virtual environment created." -ForegroundColor Green
Write-Host "[*] Upgrading pip..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "[*] Installing PyTorch with CUDA 12.1 support..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] CUDA wheel install failed, installing standard PyTorch..." -ForegroundColor Yellow
    & .venv\Scripts\python.exe -m pip install torch torchvision
}

Write-Host "[*] Installing remaining dependencies from requirements.txt..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "[*] Verifying Environment:" -ForegroundColor Cyan
& .venv\Scripts\python.exe -c "import torch, cv2, mediapipe, sklearn; print('PyTorch:', torch.__version__, '| CUDA:', torch.cuda.is_available(), '| OpenCV:', cv2.__version__, '| MediaPipe:', mediapipe.__version__)"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "[+] Environment setup complete! Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
