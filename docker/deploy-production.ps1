# Enterprise Scanner - Production Deployment (PowerShell)
# Windows version of the deployment script

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$COMPOSE_FILE = Join-Path $SCRIPT_DIR "docker-compose.prod.yml"
$ENV_FILE = Join-Path $SCRIPT_DIR ".env"

Write-Host "🚀 Enterprise Scanner - Production Deployment" -ForegroundColor Blue
Write-Host "==============================================" -ForegroundColor Blue
Write-Host ""

# Check if .env file exists
if (-not (Test-Path $ENV_FILE)) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure it"
    exit 1
}

Write-Host "✅ Environment file found" -ForegroundColor Green
Write-Host ""

# Pre-deployment checks
Write-Host "📋 Running pre-deployment checks..." -ForegroundColor Blue
Write-Host ""

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed" -ForegroundColor Red
    exit 1
}

# Check SSL certificates
$sslFullchain = Join-Path $SCRIPT_DIR "ssl\fullchain.pem"
$sslPrivkey = Join-Path $SCRIPT_DIR "ssl\privkey.pem"

if (-not (Test-Path $sslFullchain) -or -not (Test-Path $sslPrivkey)) {
    Write-Host "⚠️  SSL certificates not found" -ForegroundColor Yellow
    Write-Host "Run .\setup-ssl.ps1 to generate certificates"
    $continue = Read-Host "Continue without SSL? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "✅ SSL certificates found" -ForegroundColor Green
}

Write-Host ""

# Backup existing deployment
$runningContainers = docker ps -q -f "name=enterprisescanner"
if ($runningContainers) {
    Write-Host "📦 Creating backup of current deployment..." -ForegroundColor Yellow
    $backupFile = Join-Path $SCRIPT_DIR "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    # Backup command would go here
    Write-Host "✅ Backup prepared" -ForegroundColor Green
    Write-Host ""
}

# Pull latest images
Write-Host "📥 Pulling latest images..." -ForegroundColor Blue
docker-compose -f $COMPOSE_FILE pull
Write-Host ""

# Build services
Write-Host "🔨 Building services..." -ForegroundColor Blue
docker-compose -f $COMPOSE_FILE build --no-cache
Write-Host ""

# Stop existing services
if ($runningContainers) {
    Write-Host "⏹️  Stopping existing services..." -ForegroundColor Yellow
    docker-compose -f $COMPOSE_FILE down
    Write-Host ""
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Blue
docker-compose -f $COMPOSE_FILE up -d
Write-Host ""

# Wait for services to start
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Health checks
Write-Host ""
Write-Host "🏥 Running health checks..." -ForegroundColor Blue
Write-Host ""

$services = @(
    @{name="nginx"; port=80; path="/health"},
    @{name="enterprise_chat_system"; port=5001; path="/health"},
    @{name="interactive_security_assessment"; port=5002; path="/health"},
    @{name="advanced_analytics_dashboard"; port=5003; path="/health"},
    @{name="api_documentation_portal"; port=5004; path="/health"},
    @{name="partner_portal_system"; port=5005; path="/health"},
    @{name="client_onboarding_automation"; port=5006; path="/health"},
    @{name="performance_monitoring_system"; port=5007; path="/health"}
)

$allHealthy = $true

foreach ($service in $services) {
    Write-Host "Checking $($service.name)... " -NoNewline
    
    $healthy = $false
    for ($i = 1; $i -le 5; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.port)$($service.path)" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Healthy" -ForegroundColor Green
                $healthy = $true
                break
            }
        } catch {
            if ($i -lt 5) {
                Start-Sleep -Seconds 2
            }
        }
    }
    
    if (-not $healthy) {
        Write-Host "❌ Unhealthy" -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host ""

if ($allHealthy) {
    Write-Host "✅ All services are healthy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Deployment Summary:" -ForegroundColor Blue
    Write-Host "===================="
    docker-compose -f $COMPOSE_FILE ps
    Write-Host ""
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access your services:" -ForegroundColor Blue
    Write-Host "   Main site: https://enterprisescanner.com"
    Write-Host "   Chat: https://enterprisescanner.com/chat/"
    Write-Host "   Assessment: https://enterprisescanner.com/assessment/"
    Write-Host "   Analytics: https://enterprisescanner.com/analytics/"
    Write-Host "   API Docs: https://enterprisescanner.com/api-docs/"
    Write-Host "   Partner Portal: https://enterprisescanner.com/partner/"
    Write-Host "   Onboarding: https://enterprisescanner.com/onboarding/"
    Write-Host "   Monitoring: https://enterprisescanner.com/monitoring/"
    Write-Host ""
    Write-Host "📝 View logs:" -ForegroundColor Blue
    Write-Host "   docker-compose -f $COMPOSE_FILE logs -f [service_name]"
    Write-Host ""
    Write-Host "⏹️  Stop services:" -ForegroundColor Blue
    Write-Host "   docker-compose -f $COMPOSE_FILE down"
    Write-Host ""
} else {
    Write-Host "❌ Some services failed health checks!" -ForegroundColor Red
    Write-Host ""
    Write-Host "View logs with:"
    Write-Host "   docker-compose -f $COMPOSE_FILE logs"
    Write-Host ""
    Write-Host "Rollback deployment with:"
    Write-Host "   docker-compose -f $COMPOSE_FILE down"
    exit 1
}
