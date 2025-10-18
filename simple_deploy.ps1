# Simple Deploy Script
param([switch]$test, [switch]$all)

$SERVER = "root@134.199.147.45"
$WORKSPACE = "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace"

Write-Host "Deployment Script" -ForegroundColor Cyan

if ($test) {
    Write-Host "TEST MODE - would deploy files" -ForegroundColor Yellow
} else {
    if ($all) {
        Write-Host "Deploying all files..." -ForegroundColor Yellow
        scp -r "$WORKSPACE\website\*" "${SERVER}:/var/www/html/"
    } else {
        Write-Host "Deploying index.html..." -ForegroundColor Yellow
        scp "$WORKSPACE\website\index.html" "${SERVER}:/var/www/html/"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Upload successful!" -ForegroundColor Green
        ssh $SERVER "nginx -t && systemctl reload nginx"
        Write-Host "Deployment complete!" -ForegroundColor Green
    }
}
