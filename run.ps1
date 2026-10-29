Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Azure Data Analytics Pipeline & BI SQL Workbench       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$pythonExe = "C:\Users\Dell\AppData\Local\Programs\Python\Python39\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "`n[1/2] Running automated test suite..." -ForegroundColor Gray
& $pythonExe test_pipeline.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Tests failed. Please check errors." -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/2] Launching Analytics Web Dashboard on http://127.0.0.1:8001..." -ForegroundColor Green
& $pythonExe -m uvicorn app:app --port 8001 --reload
