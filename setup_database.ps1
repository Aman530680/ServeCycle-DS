# Sets up the MySQL database for ServeCycle.
# Run ONCE after creating the 'servecycle' database in MySQL.
#
# Usage: .\setup_database.ps1
# You will be prompted for your MySQL password.

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "ServeCycle — MySQL setup" -ForegroundColor Cyan
Write-Host ""

# Ask for MySQL password
$mysqlPassword = Read-Host "Enter your MySQL root password" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword)
)

# Write .env with the password
$envContent = @"
DB_HOST=localhost
DB_PORT=3306
DB_NAME=servecycle
DB_USER=root
DB_PASSWORD=$plainPassword
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
MODEL_PATH=models/random_forest.joblib
MODEL_METADATA_PATH=models/model_metadata.json
RANDOM_STATE=42
DEFAULT_SERVICE_LEVEL=0.90
CLEAN_CSV_PATH=data/processed/clean_events.csv
"@
$envContent | Out-File -FilePath ".env" -Encoding utf8
Write-Host ".env created with your credentials." -ForegroundColor Green

# Apply schema
Write-Host ""
Write-Host "Applying schema to MySQL..." -ForegroundColor Cyan
$schemaPath = Join-Path $projectRoot "backend\db\schema.sql"
& mysql -u root "-p$plainPassword" servecycle -e "source $schemaPath" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Schema applied successfully." -ForegroundColor Green
} else {
    Write-Host "Schema apply failed. Check your password and that MySQL is running." -ForegroundColor Red
    exit 1
}

# Load data
Write-Host ""
Write-Host "Loading data into MySQL..." -ForegroundColor Cyan
python -m src.loader
if ($LASTEXITCODE -eq 0) {
    Write-Host "Data loaded successfully." -ForegroundColor Green
} else {
    Write-Host "Data load failed. Check the error above." -ForegroundColor Red
    exit 1
}

# Verify
Write-Host ""
Write-Host "Verifying load..." -ForegroundColor Cyan
python -m src.verify_load
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Database setup complete. You can now run the backend." -ForegroundColor Green
} else {
    Write-Host "Verification failed. Check the error above." -ForegroundColor Red
}
