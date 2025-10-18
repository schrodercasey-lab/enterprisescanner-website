# Enterprise Scanner - Deployment Helper Script
# PowerShell script to prepare files for deployment
# Run from: workspace directory

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Enterprise Scanner - Deployment Helper" -ForegroundColor Cyan
Write-Host "  Production Deployment to enterprisescanner.com" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$sourceDir = ".\website"
$deploymentPackage = ".\enterprise-scanner-deployment.zip"

# Check if source directory exists
if (-not (Test-Path $sourceDir)) {
    Write-Host "ERROR: website directory not found!" -ForegroundColor Red
    Write-Host "Expected: $sourceDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/5] Scanning website directory..." -ForegroundColor Green
$allFiles = Get-ChildItem -Path $sourceDir -Recurse -File
$fileCount = $allFiles.Count
Write-Host "      Found $fileCount files ready for deployment" -ForegroundColor White

# Count by type
$htmlFiles = ($allFiles | Where-Object { $_.Extension -eq ".html" }).Count
$cssFiles = ($allFiles | Where-Object { $_.Extension -eq ".css" }).Count
$jsFiles = ($allFiles | Where-Object { $_.Extension -eq ".js" }).Count

Write-Host ""
Write-Host "File Breakdown:" -ForegroundColor Cyan
Write-Host "  HTML files: $htmlFiles" -ForegroundColor White
Write-Host "  CSS files:  $cssFiles" -ForegroundColor White
Write-Host "  JS files:   $jsFiles" -ForegroundColor White
Write-Host "  Other:      $($fileCount - $htmlFiles - $cssFiles - $jsFiles)" -ForegroundColor White

# Verify critical files exist
Write-Host ""
Write-Host "[2/5] Verifying critical files..." -ForegroundColor Green

$criticalFiles = @(
    "$sourceDir\index.html",
    "$sourceDir\css\jupiter-wifi-eyes.css",
    "$sourceDir\css\dark-ai-theme.css",
    "$sourceDir\js\jupiter-wifi-eyes.js",
    "$sourceDir\js\jupiter-ai-chat.js",
    "$sourceDir\js\theme-controller.js"
)

$allCriticalPresent = $true
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Write-Host "      ✓ $fileName" -ForegroundColor Green
    } else {
        $fileName = Split-Path $file -Leaf
        Write-Host "      ✗ $fileName MISSING!" -ForegroundColor Red
        $allCriticalPresent = $false
    }
}

if (-not $allCriticalPresent) {
    Write-Host ""
    Write-Host "ERROR: Some critical files are missing!" -ForegroundColor Red
    Write-Host "Please ensure all files are present before deploying." -ForegroundColor Yellow
    exit 1
}

# Calculate total size
Write-Host ""
Write-Host "[3/5] Calculating deployment size..." -ForegroundColor Green
$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "      Total size: $sizeMB MB" -ForegroundColor White

# Create deployment package
Write-Host ""
Write-Host "[4/5] Creating deployment package..." -ForegroundColor Green

if (Test-Path $deploymentPackage) {
    Remove-Item $deploymentPackage -Force
}

try {
    Compress-Archive -Path "$sourceDir\*" -DestinationPath $deploymentPackage -Force
    Write-Host "      ✓ Package created: enterprise-scanner-deployment.zip" -ForegroundColor Green
    
    $zipSize = [math]::Round((Get-Item $deploymentPackage).Length / 1MB, 2)
    Write-Host "      Package size: $zipSize MB" -ForegroundColor White
} catch {
    Write-Host "      ✗ Failed to create package: $_" -ForegroundColor Red
    exit 1
}

# Display deployment checklist
Write-Host ""
Write-Host "[5/5] Deployment Checklist" -ForegroundColor Green
Write-Host ""
Write-Host "PRE-DEPLOYMENT CHECKS:" -ForegroundColor Cyan
Write-Host "  [ ] SSL/HTTPS configured (required for WiFi Eyes camera)" -ForegroundColor Yellow
Write-Host "  [ ] FTP/hosting credentials ready" -ForegroundColor Yellow
Write-Host "  [ ] Backup of existing site (if any)" -ForegroundColor Yellow
Write-Host "  [ ] DNS points to correct server" -ForegroundColor Yellow
Write-Host ""

Write-Host "FILES READY FOR UPLOAD:" -ForegroundColor Cyan
Write-Host "  Source: .\website\" -ForegroundColor White
Write-Host "  OR: .\enterprise-scanner-deployment.zip" -ForegroundColor White
Write-Host ""

Write-Host "DEPLOYMENT OPTIONS:" -ForegroundColor Cyan
Write-Host "  1. FTP Upload: Use FileZilla to upload .\website\ contents" -ForegroundColor White
Write-Host "  2. cPanel: Upload .zip file and extract in File Manager" -ForegroundColor White
Write-Host "  3. Git: Push to GitHub and pull on server" -ForegroundColor White
Write-Host ""

Write-Host "POST-DEPLOYMENT TESTS:" -ForegroundColor Cyan
Write-Host "  [ ] Visit https://enterprisescanner.com (verify HTTPS)" -ForegroundColor Yellow
Write-Host "  [ ] Test WiFi Eyes camera (click blue button)" -ForegroundColor Yellow
Write-Host "  [ ] Test chat widget (purple button)" -ForegroundColor Yellow
Write-Host "  [ ] Test theme toggle (Ctrl+D)" -ForegroundColor Yellow
Write-Host "  [ ] Check console for errors (F12)" -ForegroundColor Yellow
Write-Host "  [ ] Test on mobile device" -ForegroundColor Yellow
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deployment package ready!" -ForegroundColor Green
Write-Host "  Total files: $fileCount" -ForegroundColor White
Write-Host "  Package: enterprise-scanner-deployment.zip" -ForegroundColor White
Write-Host "  Next: Upload to https://enterprisescanner.com" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "See DEPLOYMENT_GUIDE_STEPBYSTEP.md for detailed instructions." -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to open deployment guide
$response = Read-Host "Open deployment guide now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Start-Process "DEPLOYMENT_GUIDE_STEPBYSTEP.md"
}

Write-Host ""
Write-Host "Good luck with your deployment! 🚀" -ForegroundColor Green
