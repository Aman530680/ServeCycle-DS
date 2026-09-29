$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "ServeCycle - MySQL setup" -ForegroundColor Cyan

$plainPassword = Read-Host "Enter your MySQL root password"

$line1  = "DB_HOST=localhost"
$line2  = "DB_PORT=3306"
$line3  = "DB_NAME=servecycle"
$line4  = "DB_USER=root"
$line5  = "DB_PASSWORD=" + $plainPassword
$line6  = "API_HOST=0.0.0.0"
$line7  = "API_PORT=8000"
$line8  = "CORS_ORIGINS=http://localhost:5173"
$line9  = "MODEL_PATH=models/random_forest.joblib"
$line10 = "MODEL_METADATA_PATH=models/model_metadata.json"
$line11 = "RANDOM_STATE=42"
$line12 = "DEFAULT_SERVICE_LEVEL=0.90"
$line13 = "CLEAN_CSV_PATH=data/processed/clean_events.csv"

$lines = @($line1,$line2,$line3,$line4,$line5,$line6,$line7,$line8,$line9,$line10,$line11,$line12,$line13)
$lines | Out-File -FilePath ".env" -Encoding utf8
Write-Host ".env created." -ForegroundColor Green

Write-Host "Applying schema to MySQL..." -ForegroundColor Cyan
$schemaPath = Join-Path $projectRoot "backend\db\schema.sql"
Get-Content $schemaPath | mysql -u root "-p$plainPassword" servecycle
if ($LASTEXITCODE -eq 0) {
    Write-Host "Schema applied." -ForegroundColor Green
} else {
    Write-Host "Schema failed. Check password and that MySQL is running." -ForegroundColor Red
    exit 1
}

Write-Host "Loading data..." -ForegroundColor Cyan
python -m src.loader
if ($LASTEXITCODE -eq 0) {
    Write-Host "Data loaded." -ForegroundColor Green
} else {
    Write-Host "Load failed." -ForegroundColor Red
    exit 1
}

Write-Host "Verifying..." -ForegroundColor Cyan
python -m src.verify_load
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database setup complete." -ForegroundColor Green
} else {
    Write-Host "Verification failed." -ForegroundColor Red
}
