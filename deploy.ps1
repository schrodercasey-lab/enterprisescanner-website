# Enterprise Scanner - Automated Deployment Script
# Quick deployment script for Windows PowerShell
# Usage: .\deploy.ps1 -file "website\index.html" OR .\deploy.ps1 -all

param(
    [string]$file = "website\index.html",
    [switch]$all,
    [switch]$test
)

$SERVER = "root@134.199.147.45"
$WORKSPACE = "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace"

Write-Host "`n🚀 ENTERPRISE SCANNER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test mode (dry run)
if ($test) {
    Write-Host "🧪 TEST MODE - No actual deployment" -ForegroundColor Yellow
    Write-Host ""
}

if ($all) {
    Write-Host "📦 Deploying ENTIRE website..." -ForegroundColor Yellow
    Write-Host "   Source: $WORKSPACE\website\" -ForegroundColor Gray
    Write-Host "   Target: ${SERVER}:/var/www/html/" -ForegroundColor Gray
    Write-Host ""
    
    if (-not $test) {
        # Deploy all files
        scp -r "$WORKSPACE\website\*" "${SERVER}:/var/www/html/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Files uploaded successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ File upload failed!" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "📄 Deploying single file..." -ForegroundColor Yellow
    Write-Host "   File: $file" -ForegroundColor Gray
    
    # Check if file exists
    if (-not (Test-Path "$WORKSPACE\$file")) {
        Write-Host "❌ File not found: $WORKSPACE\$file" -ForegroundColor Red
        exit 1
    }
    
    # Determine target path
    $targetPath = "/var/www/html/"
    if ($file -like "website\*") {
        # Remove 'website\' prefix for target path
        $relativePath = $file -replace "^website\\", ""
        $targetPath = "/var/www/html/$relativePath"
    } else {
        $targetPath = "/var/www/html/$file"
    }
    
    Write-Host "   Target: ${SERVER}:$targetPath" -ForegroundColor Gray
    Write-Host ""
    
    if (-not $test) {
        # Deploy single file
        scp "$WORKSPACE\$file" "${SERVER}:$targetPath"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ File uploaded successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ File upload failed!" -ForegroundColor Red
            exit 1
        }
    }
}

# Test Nginx configuration
Write-Host ""
Write-Host "🔧 Testing Nginx configuration..." -ForegroundColor Yellow

if (-not $test) {
    $nginxTest = ssh $SERVER "nginx -t 2>&1"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Nginx configuration valid!" -ForegroundColor Green
        
        # Reload Nginx
        Write-Host ""
        Write-Host "🔄 Reloading Nginx..." -ForegroundColor Yellow
        ssh $SERVER "systemctl reload nginx"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Nginx reloaded successfully!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Nginx reload warning (check manually)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Nginx configuration error!" -ForegroundColor Red
        Write-Host $nginxTest -ForegroundColor Red
        Write-Host ""
        Write-Host "🔙 Consider rolling back changes..." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   ⏭️  Skipping Nginx test in test mode" -ForegroundColor Gray
}

# Success!
Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "🌐 View at: https://enterprisescanner.com" -ForegroundColor Cyan
Write-Host ""

# Show deployment summary
Write-Host "📊 Deployment Summary:" -ForegroundColor Cyan
Write-Host "   Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
if ($all) {
    Write-Host "   Scope: Full website" -ForegroundColor Gray
} else {
    Write-Host "   Scope: $file" -ForegroundColor Gray
}
Write-Host "   Server: 134.199.147.45" -ForegroundColor Gray
Write-Host ""
