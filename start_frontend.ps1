# Run this script to start the React dashboard.
# Usage: .\start_frontend.ps1

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $projectRoot "frontend"
Set-Location $frontendDir

Write-Host "Working directory: $frontendDir" -ForegroundColor Cyan
Write-Host "Starting ServeCycle dashboard on http://localhost:5173" -ForegroundColor Cyan
Write-Host "Make sure the backend is already running on port 8000." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

# Create .env if it doesn't exist
$envFile = Join-Path $frontendDir ".env"
if (-not (Test-Path $envFile)) {
    "VITE_API_URL=http://localhost:8000" | Out-File -FilePath $envFile -Encoding utf8
    Write-Host "Created frontend/.env with VITE_API_URL=http://localhost:8000" -ForegroundColor Green
}

npm run dev
