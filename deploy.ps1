# Awash Bank Issue Tracker — High-Performance Local Deployment & Process Manager
# This script terminates port conflicts, seeds the database, and boots uvicorn bound directly to 127.0.0.1 for instant response times.

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Awash Bank Issue Tracker Auto-DevOps Startup " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 1. Terminate Port Conflicts
Write-Host "[1/4] Clearing port 8000 conflicts..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($processes) {
    foreach ($p in $processes) {
        $owningPid = $p.OwningProcess
        if ($owningPid -gt 0) {
            Write-Host "Killing conflicting process ID $owningPid bound to port 8000..." -ForegroundColor DarkYellow
            Stop-Process -Id $owningPid -Force -ErrorAction SilentlyContinue
        }
    }
}
# Sleep briefly to release port binding
Start-Sleep -Seconds 2

# 2. Sync and Seed Database
Write-Host "[2/4] Initializing and seeding the SQLite database..." -ForegroundColor Yellow
$env:PYTHONIOENCODING="utf-8"
cd backend
python -m app.seed
cd ..

# 3. Start High-Performance Uvicorn Server
Write-Host "[3/4] Starting FastAPI Uvicorn server on http://127.0.0.1:8000/ ..." -ForegroundColor Yellow
Write-Host "--> binding directly to 127.0.0.1 to avoid Windows IPv6 resolution lags!" -ForegroundColor Green

# Launch as a persistent detached background process
Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000" -WorkingDirectory "backend" -WindowStyle Hidden

# 4. Open Default Browser
Write-Host "[4/4] Launching the Issue Tracker..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8000/"

Write-Host "`nAll steps completed! The server is running dynamically in the background." -ForegroundColor Green
Write-Host "You can inspect processes or logs on port 8000 at any time." -ForegroundColor Cyan
