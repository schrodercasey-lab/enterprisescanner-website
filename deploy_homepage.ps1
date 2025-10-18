# Enterprise Scanner Homepage Deployment Script
# PowerShell script to deploy the new homepage to production server

$SERVER = "134.199.147.45"
$USER = "root"
$PASSWORD = "Schroeder123!"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " ENTERPRISE SCANNER - HOMEPAGE DEPLOYMENT" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Deploying new professional homepage..." -ForegroundColor Yellow

# Check if homepage file exists
if (-not (Test-Path "website\index.html")) {
    Write-Host "Homepage file not found: website\index.html" -ForegroundColor Red
    exit 1
}

Write-Host "Homepage file found and ready for deployment" -ForegroundColor Green

# Test server connectivity
Write-Host "Testing server connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$SERVER" -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "Server is reachable" -ForegroundColor Green
        Write-Host "Current response length: $($response.Content.Length) characters" -ForegroundColor Gray
    } else {
        Write-Host "Server connectivity issue" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Server test error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "MANUAL DEPLOYMENT INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "1. Open WinSCP, FileZilla, or similar SFTP client" -ForegroundColor White
Write-Host "2. Connect to: $SERVER" -ForegroundColor White  
Write-Host "3. Username: $USER" -ForegroundColor White
Write-Host "4. Password: $PASSWORD" -ForegroundColor White
Write-Host "5. Navigate to: /var/www/html/" -ForegroundColor White
Write-Host "6. Upload: website\index.html" -ForegroundColor White
Write-Host "7. Overwrite the existing file if prompted" -ForegroundColor White
Write-Host ""
Write-Host "OR use WSL/Git Bash with this command:" -ForegroundColor Cyan
Write-Host "scp -o StrictHostKeyChecking=no website/index.html root@134.199.147.45:/var/www/html/" -ForegroundColor Yellow
Write-Host ""

Write-Host "AFTER MANUAL UPLOAD:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "The website will show:" -ForegroundColor White
Write-Host "• Professional Fortune 500-focused homepage" -ForegroundColor Green
Write-Host "• Interactive ROI calculator" -ForegroundColor Green  
Write-Host "• Complete navigation to all features" -ForegroundColor Green
Write-Host "• Mobile-responsive design" -ForegroundColor Green
Write-Host ""
Write-Host "Test at: http://enterprisescanner.com" -ForegroundColor Cyan
Write-Host "Direct IP: http://$SERVER" -ForegroundColor Cyan