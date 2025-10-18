# Environment Switcher
# Toggle between development, staging, and production environments
# Save 30 minutes per week switching configs

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'staging', 'prod', 'status')]
    [string]$Environment = 'status',
    
    [switch]$Force
)

Write-Host "`n=== Environment Switcher ===" -ForegroundColor Cyan

# Environment configuration paths
$envFiles = @{
    dev = ".env.development"
    staging = ".env.staging"
    prod = ".env.production"
    current = ".env"
}

# Environment details
$environments = @{
    dev = @{
        name = "Development"
        color = "Green"
        database = "localhost:5432/dev_db"
        redis = "localhost:6379"
        apiUrl = "http://localhost:5000"
        webUrl = "http://localhost:8000"
        debug = "True"
        logLevel = "DEBUG"
    }
    staging = @{
        name = "Staging"
        color = "Yellow"
        database = "staging-db.enterprisescanner.com:5432/staging_db"
        redis = "staging-redis.enterprisescanner.com:6379"
        apiUrl = "https://api-staging.enterprisescanner.com"
        webUrl = "https://staging.enterprisescanner.com"
        debug = "False"
        logLevel = "INFO"
    }
    prod = @{
        name = "Production"
        color = "Red"
        database = "db.enterprisescanner.com:5432/production_db"
        redis = "redis.enterprisescanner.com:6379"
        apiUrl = "https://api.enterprisescanner.com"
        webUrl = "https://enterprisescanner.com"
        debug = "False"
        logLevel = "WARNING"
    }
}

# Function to detect current environment
function Get-CurrentEnvironment {
    if (-not (Test-Path $envFiles.current)) {
        return $null
    }
    
    $currentContent = Get-Content $envFiles.current -Raw
    
    # Check which environment file matches
    foreach ($env in @('dev', 'staging', 'prod')) {
        if (Test-Path $envFiles[$env]) {
            $envContent = Get-Content $envFiles[$env] -Raw
            if ($currentContent -eq $envContent) {
                return $env
            }
        }
    }
    
    return "unknown"
}

# Function to create default environment files if they don't exist
function Initialize-EnvironmentFiles {
    Write-Host "[i] Checking environment files..." -ForegroundColor Cyan
    
    # Development .env
    if (-not (Test-Path $envFiles.dev)) {
        Write-Host "[+] Creating $($envFiles.dev)..." -ForegroundColor Green
        $devContent = @"
# Development Environment Configuration
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=dev_db
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Configuration
API_URL=http://localhost:5000
API_KEY=dev_api_key_12345

# Web Application
WEB_URL=http://localhost:8000
SECRET_KEY=dev_secret_key_change_in_production

# Email (Development - Console backend)
EMAIL_BACKEND=console
SMTP_HOST=localhost
SMTP_PORT=1025
EMAIL_FROM=dev@enterprisescanner.local

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Features
ENABLE_ANALYTICS=False
ENABLE_MONITORING=False
ENABLE_RATE_LIMITING=False
"@
        $devContent | Out-File -FilePath $envFiles.dev -Encoding UTF8
    }
    
    # Staging .env
    if (-not (Test-Path $envFiles.staging)) {
        Write-Host "[+] Creating $($envFiles.staging)..." -ForegroundColor Green
        $stagingContent = @"
# Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_HOST=staging-db.enterprisescanner.com
DATABASE_PORT=5432
DATABASE_NAME=staging_db
DATABASE_USER=staging_user
DATABASE_PASSWORD=CHANGE_THIS_STAGING_PASSWORD

# Redis
REDIS_HOST=staging-redis.enterprisescanner.com
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_THIS_REDIS_PASSWORD

# API Configuration
API_URL=https://api-staging.enterprisescanner.com
API_KEY=staging_api_key_CHANGE_THIS

# Web Application
WEB_URL=https://staging.enterprisescanner.com
SECRET_KEY=staging_secret_key_CHANGE_THIS

# Email (Staging - Use test email service)
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=staging_email_user
SMTP_PASSWORD=staging_email_password
EMAIL_FROM=staging@enterprisescanner.com

# Security
ALLOWED_HOSTS=staging.enterprisescanner.com,api-staging.enterprisescanner.com
CORS_ORIGINS=https://staging.enterprisescanner.com

# Features
ENABLE_ANALYTICS=True
ENABLE_MONITORING=True
ENABLE_RATE_LIMITING=True
"@
        $stagingContent | Out-File -FilePath $envFiles.staging -Encoding UTF8
    }
    
    # Production .env
    if (-not (Test-Path $envFiles.prod)) {
        Write-Host "[+] Creating $($envFiles.prod)..." -ForegroundColor Green
        $prodContent = @"
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# Database
DATABASE_HOST=db.enterprisescanner.com
DATABASE_PORT=5432
DATABASE_NAME=production_db
DATABASE_USER=prod_user
DATABASE_PASSWORD=CHANGE_THIS_PRODUCTION_PASSWORD_STRONG

# Redis
REDIS_HOST=redis.enterprisescanner.com
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_THIS_REDIS_PASSWORD_STRONG

# API Configuration
API_URL=https://api.enterprisescanner.com
API_KEY=production_api_key_CHANGE_THIS

# Web Application
WEB_URL=https://enterprisescanner.com
SECRET_KEY=production_secret_key_CHANGE_THIS_VERY_STRONG

# Email (Production - Google Workspace)
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=info@enterprisescanner.com
SMTP_PASSWORD=CHANGE_THIS_GMAIL_APP_PASSWORD
EMAIL_FROM=info@enterprisescanner.com

# Security
ALLOWED_HOSTS=enterprisescanner.com,api.enterprisescanner.com,www.enterprisescanner.com
CORS_ORIGINS=https://enterprisescanner.com,https://www.enterprisescanner.com

# Features
ENABLE_ANALYTICS=True
ENABLE_MONITORING=True
ENABLE_RATE_LIMITING=True

# SSL
SSL_CERTIFICATE=/etc/letsencrypt/live/enterprisescanner.com/fullchain.pem
SSL_CERTIFICATE_KEY=/etc/letsencrypt/live/enterprisescanner.com/privkey.pem
"@
        $prodContent | Out-File -FilePath $envFiles.prod -Encoding UTF8
    }
    
    Write-Host "[+] Environment files ready" -ForegroundColor Green
}

# Initialize environment files if needed
Initialize-EnvironmentFiles

# Get current environment
$currentEnv = Get-CurrentEnvironment

# Display current status
if ($Environment -eq 'status') {
    Write-Host "`n[*] Current Environment: " -NoNewline -ForegroundColor White
    
    if ($currentEnv -and $currentEnv -ne "unknown" -and $environments.ContainsKey($currentEnv)) {
        $envColor = $environments[$currentEnv].color
        $envName = $environments[$currentEnv].name
        Write-Host "$envName ($currentEnv)" -ForegroundColor $envColor
        
        Write-Host "`n[*] Configuration:" -ForegroundColor Cyan
        Write-Host "  Database: $($environments[$currentEnv].database)" -ForegroundColor White
        Write-Host "  Redis: $($environments[$currentEnv].redis)" -ForegroundColor White
        Write-Host "  API URL: $($environments[$currentEnv].apiUrl)" -ForegroundColor White
        Write-Host "  Web URL: $($environments[$currentEnv].webUrl)" -ForegroundColor White
        Write-Host "  Debug: $($environments[$currentEnv].debug)" -ForegroundColor White
        Write-Host "  Log Level: $($environments[$currentEnv].logLevel)" -ForegroundColor White
    }
    elseif ($currentEnv -eq "unknown") {
        Write-Host "Unknown (custom .env file)" -ForegroundColor Yellow
        Write-Host "`n[i] Current .env doesn't match any template" -ForegroundColor Cyan
    }
    else {
        Write-Host "Not Set (no .env file)" -ForegroundColor Yellow
        Write-Host "`n[i] Run with -Environment <dev|staging|prod> to set environment" -ForegroundColor Cyan
    }
    
    Write-Host "`n[*] Available Environments:" -ForegroundColor Cyan
    Write-Host "  dev      - Development (local testing)" -ForegroundColor Green
    Write-Host "  staging  - Staging (pre-production testing)" -ForegroundColor Yellow
    Write-Host "  prod     - Production (live site)" -ForegroundColor Red
    
    Write-Host "`n[*] Usage Examples:" -ForegroundColor Cyan
    Write-Host "  .\switch_env.ps1 -Environment dev" -ForegroundColor White
    Write-Host "  .\switch_env.ps1 -Environment prod -Force" -ForegroundColor White
    Write-Host ""
    
    exit 0
}

# Switching environment
$targetEnv = $Environment
$targetName = $environments[$targetEnv].name
$targetColor = $environments[$targetEnv].color

Write-Host "`n[*] Target Environment: " -NoNewline -ForegroundColor White
Write-Host "$targetName ($targetEnv)" -ForegroundColor $targetColor

# Confirm if switching to production
if ($targetEnv -eq 'prod' -and -not $Force) {
    Write-Host "`n[!] WARNING: Switching to PRODUCTION environment" -ForegroundColor Red
    Write-Host "[!] This will connect to live systems and databases" -ForegroundColor Red
    Write-Host "`n[?] Are you sure? (Type 'yes' to confirm): " -NoNewline -ForegroundColor Yellow
    $confirmation = Read-Host
    
    if ($confirmation -ne 'yes') {
        Write-Host "`n[!] Cancelled - Environment not changed" -ForegroundColor Yellow
        exit 0
    }
}

# Check if target environment file exists
if (-not (Test-Path $envFiles[$targetEnv])) {
    Write-Host "`n[!] Error: $($envFiles[$targetEnv]) not found" -ForegroundColor Red
    exit 1
}

# Backup current .env if it exists
if (Test-Path $envFiles.current) {
    $backupFile = ".env.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "`n[+] Backing up current .env to $backupFile" -ForegroundColor Green
    Copy-Item $envFiles.current $backupFile
}

# Copy target environment file to .env
Write-Host "[+] Switching to $targetName environment..." -ForegroundColor $targetColor
Copy-Item $envFiles[$targetEnv] $envFiles.current -Force

# Verify the switch
$newEnv = Get-CurrentEnvironment
if ($newEnv -eq $targetEnv) {
    Write-Host "[+] Successfully switched to $targetName!" -ForegroundColor Green
    
    Write-Host "`n[*] Active Configuration:" -ForegroundColor Cyan
    Write-Host "  Database: $($environments[$targetEnv].database)" -ForegroundColor White
    Write-Host "  Redis: $($environments[$targetEnv].redis)" -ForegroundColor White
    Write-Host "  API URL: $($environments[$targetEnv].apiUrl)" -ForegroundColor White
    Write-Host "  Web URL: $($environments[$targetEnv].webUrl)" -ForegroundColor White
    Write-Host "  Debug: $($environments[$targetEnv].debug)" -ForegroundColor White
    Write-Host "  Log Level: $($environments[$targetEnv].logLevel)" -ForegroundColor White
    
    # Important reminders
    Write-Host "`n[!] IMPORTANT:" -ForegroundColor Yellow
    if ($targetEnv -eq 'prod') {
        Write-Host "  - You are now connected to PRODUCTION systems" -ForegroundColor Red
        Write-Host "  - All changes will affect live users" -ForegroundColor Red
        Write-Host "  - Double-check all operations before executing" -ForegroundColor Red
    }
    elseif ($targetEnv -eq 'staging') {
        Write-Host "  - You are now connected to STAGING systems" -ForegroundColor Yellow
        Write-Host "  - Use for pre-production testing" -ForegroundColor Yellow
    }
    else {
        Write-Host "  - You are now in DEVELOPMENT mode" -ForegroundColor Green
        Write-Host "  - Safe for testing and experimentation" -ForegroundColor Green
    }
    
    Write-Host "`n[*] Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart your application to load new config" -ForegroundColor White
    Write-Host "  2. Verify database connection" -ForegroundColor White
    Write-Host "  3. Check logs for any configuration errors" -ForegroundColor White
    
    Write-Host "`n=== Complete ===" -ForegroundColor Cyan
}
else {
    Write-Host "[!] Error: Environment switch may have failed" -ForegroundColor Red
    Write-Host "[!] Current environment: $newEnv" -ForegroundColor Red
    Write-Host "[!] Restore from backup if needed: .env.backup_*" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
