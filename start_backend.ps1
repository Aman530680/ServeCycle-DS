# Run this script from anywhere — it always starts the backend from the correct folder.
# Usage: right-click -> Run with PowerShell
#        OR in terminal: .\start_backend.ps1

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "Working directory: $projectRoot" -ForegroundColor Cyan
Write-Host "Starting ServeCycle API on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

uvicorn backend.app.main:app --reload --port 8000 --host 0.0.0.0
