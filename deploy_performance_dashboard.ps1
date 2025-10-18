# Deploy Performance Dashboard to DigitalOcean Droplet
# This creates a permanent monitoring endpoint at https://enterprisescanner.com/performance

Write-Host "Uploading performance dashboard setup script..." -ForegroundColor Cyan
scp c:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\setup_performance_dashboard.sh root@134.199.147.45:/root/

Write-Host "Running setup on droplet..." -ForegroundColor Cyan
ssh root@134.199.147.45 "bash /root/setup_performance_dashboard.sh"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Performance Dashboard Deployed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your dashboard:" -ForegroundColor Yellow
Write-Host "  Dashboard: https://enterprisescanner.com/performance" -ForegroundColor Cyan
Write-Host "  JSON API:  https://enterprisescanner.com/performance/latest.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  - Real-time performance metrics (req/s, response time)" -ForegroundColor White
Write-Host "  - Compression & caching statistics" -ForegroundColor White
Write-Host "  - Service health monitoring (Redis, PostgreSQL, PgBouncer)" -ForegroundColor White
Write-Host "  - Auto-refresh every 60 seconds" -ForegroundColor White
Write-Host "  - Automated tests every hour" -ForegroundColor White
Write-Host ""
