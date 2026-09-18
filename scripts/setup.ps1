# TARGET-X Environment Setup Script (Windows 11 PowerShell)
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "   TARGET-X: ENVIRONMENT SETUP & DEPENDENCY INSTALLATION" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Python Virtual Environment
Write-Host "`n[*] Setting up Python virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
}
& .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. Frontend Dependencies
Write-Host "`n[*] Installing Frontend dependencies..." -ForegroundColor Yellow
cd frontend
npm install
cd ..

# 3. Authentic Model Training
Write-Host "`n[*] Training authentic TARGET-X model from scratch (Zero Pretrained Weights)..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe training\train.py
& .\venv\Scripts\python.exe training\evaluate.py

Write-Host "`n[+] TARGET-X setup completed successfully!" -ForegroundColor Green
Write-Host "[+] Start the system using: .\scripts\start_backend.ps1 and .\scripts\start_frontend.ps1" -ForegroundColor Green
