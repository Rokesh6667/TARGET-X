# TARGET-X Backend Launch Script (Windows 11 PowerShell)
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "   TARGET-X: LAUNCHING FASTAPI BACKEND (PORT 8000)" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

& .\venv\Scripts\Activate.ps1
& .\venv\Scripts\uvicorn.exe backend.main:app --host 0.0.0.0 --port 8000 --reload
