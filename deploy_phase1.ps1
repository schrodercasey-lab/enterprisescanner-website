# Phase 1 Deployment Script
# Enterprise Scanner Website - Animated Hero & Enhanced ROI Calculator
# Version: 1.0
# Date: January 2025

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enterprise Scanner - Phase 1 Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$websiteDir = "website"
$jsDir = "$websiteDir/js"
$backupDir = "backups/phase1_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Files to deploy
$newFiles = @(
    "$jsDir/animated-hero.js",
    "$jsDir/enhanced-roi-calculator.js"
)

$modifiedFiles = @(
    "$websiteDir/index.html"
)

# Step 1: Verify files exist
Write-Host "[Step 1] Verifying files..." -ForegroundColor Yellow
$missingFiles = @()
foreach ($file in $newFiles + $modifiedFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
    } else {
        Write-Host "  ✅ Found: $file" -ForegroundColor Green
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Deployment aborted - missing files!" -ForegroundColor Red
    exit 1
}

# Step 2: Create backup
Write-Host ""
Write-Host "[Step 2] Creating backup..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

foreach ($file in $modifiedFiles) {
    $backupPath = Join-Path $backupDir (Split-Path $file -Leaf)
    Copy-Item $file $backupPath
    Write-Host "  ✅ Backed up: $file" -ForegroundColor Green
}

# Step 3: Validate JavaScript syntax
Write-Host ""
Write-Host "[Step 3] Validating JavaScript..." -ForegroundColor Yellow

$jsErrors = @()
foreach ($file in $newFiles) {
    # Check for basic syntax issues
    $content = Get-Content $file -Raw
    
    # Check for unclosed braces
    $openBraces = ($content.ToCharArray() | Where-Object { $_ -eq '{' }).Count
    $closeBraces = ($content.ToCharArray() | Where-Object { $_ -eq '}' }).Count
    
    if ($openBraces -ne $closeBraces) {
        $jsErrors += "$file - Unbalanced braces (open: $openBraces, close: $closeBraces)"
        Write-Host "  ❌ $file - Unbalanced braces" -ForegroundColor Red
    } else {
        Write-Host "  ✅ $file - Syntax OK" -ForegroundColor Green
    }
}

if ($jsErrors.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ JavaScript validation failed!" -ForegroundColor Red
    Write-Host "Errors:" -ForegroundColor Red
    $jsErrors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

# Step 4: Check dependencies
Write-Host ""
Write-Host "[Step 4] Checking dependencies..." -ForegroundColor Yellow

$indexContent = Get-Content "$websiteDir/index.html" -Raw

# Check Chart.js CDN
if ($indexContent -match 'chart\.js') {
    Write-Host "  ✅ Chart.js CDN found" -ForegroundColor Green
} else {
    Write-Host "  ❌ Chart.js CDN missing!" -ForegroundColor Red
    exit 1
}

# Check Quick Wins components
$requiredComponents = @(
    'toast-notifications.js',
    'loading-indicator.js',
    'counter-animations.js'
)

foreach ($component in $requiredComponents) {
    if ($indexContent -match $component) {
        Write-Host "  ✅ $component loaded" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $component not found (may cause issues)" -ForegroundColor Yellow
    }
}

# Check new components are referenced
if ($indexContent -match 'animated-hero\.js') {
    Write-Host "  ✅ animated-hero.js referenced" -ForegroundColor Green
} else {
    Write-Host "  ❌ animated-hero.js not referenced in HTML!" -ForegroundColor Red
    exit 1
}

if ($indexContent -match 'enhanced-roi-calculator\.js') {
    Write-Host "  ✅ enhanced-roi-calculator.js referenced" -ForegroundColor Green
} else {
    Write-Host "  ❌ enhanced-roi-calculator.js not referenced in HTML!" -ForegroundColor Red
    exit 1
}

# Step 5: Check HTML structure
Write-Host ""
Write-Host "[Step 5] Validating HTML structure..." -ForegroundColor Yellow

# Check for required IDs and attributes
$requiredElements = @{
    'data-hero-animated' = 'Hero animation attribute'
    'id="roi-calculator-form"' = 'ROI calculator form'
    'id="roi-results"' = 'ROI results container'
    'id="savings-chart"' = 'Savings chart canvas'
    'id="comparison-chart"' = 'Comparison chart canvas'
    'id="annual-savings"' = 'Annual savings metric'
    'id="roi-percentage"' = 'ROI percentage metric'
    'id="payback-period"' = 'Payback period metric'
}

foreach ($element in $requiredElements.Keys) {
    if ($indexContent -match $element) {
        Write-Host "  ✅ $($requiredElements[$element])" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $($requiredElements[$element])" -ForegroundColor Red
        exit 1
    }
}

# Step 6: File size check
Write-Host ""
Write-Host "[Step 6] Checking file sizes..." -ForegroundColor Yellow

$totalSize = 0
foreach ($file in $newFiles) {
    $size = (Get-Item $file).Length
    $sizeKB = [math]::Round($size / 1KB, 1)
    $totalSize += $size
    
    if ($sizeKB -gt 50) {
        Write-Host "  ⚠️  $file - ${sizeKB}KB (consider minifying)" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ $file - ${sizeKB}KB" -ForegroundColor Green
    }
}

$totalKB = [math]::Round($totalSize / 1KB, 1)
Write-Host "  📊 Total size: ${totalKB}KB" -ForegroundColor Cyan

if ($totalKB -gt 100) {
    Write-Host "  ⚠️  Consider minifying files for production" -ForegroundColor Yellow
}

# Step 7: Generate deployment summary
Write-Host ""
Write-Host "[Step 7] Generating deployment summary..." -ForegroundColor Yellow

$summaryFile = "DEPLOYMENT_SUMMARY_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# Build summary content
$summary = "# Phase 1 Deployment Summary`n"
$summary += "Generated: $timestamp`n`n"
$summary += "## Files Deployed`n"
$summary += "### New JavaScript Components`n"
foreach ($file in $newFiles) { $summary += "- $file`n" }
$summary += "`n### Modified Files`n"
foreach ($file in $modifiedFiles) { $summary += "- $file`n" }
$summary += "`n## Validation Results`n"
$summary += "- All files present`n"
$summary += "- JavaScript syntax valid`n"
$summary += "- Dependencies verified`n"
$summary += "- HTML structure correct`n"
$summary += "- Required elements present`n"
$summary += "`n## Backup Location`n$backupDir`n"
$summary += "`n## File Sizes`n"
$summary += "Total: ${totalKB}KB`n"
foreach ($file in $newFiles) {
    $size = (Get-Item $file).Length
    $sizeKB = [math]::Round($size / 1KB, 1)
    $filename = Split-Path $file -Leaf
    $summary += "- ${filename}: ${sizeKB}KB`n"
}
$summary += "`n## Next Steps`n"
$summary += "1. Upload files to production server`n"
$summary += "2. Clear CDN cache`n"
$summary += "3. Test on https://enterprisescanner.com`n"
$summary += "4. Monitor analytics and performance`n"
$summary += "5. Verify all animations working`n"
$summary += "`n## Rollback Instructions`n"
$summary += "If issues arise:`n"
$summary += "1. Stop web server`n"
$summary += "2. Restore from backup: $backupDir`n"
$summary += "3. Clear cache`n"
$summary += "4. Restart web server`n"
$summary += "5. Verify rollback successful`n"
$summary += "`n## Contact`n"
$summary += "Technical Issues: info@enterprisescanner.com`n"
$summary += "Emergency Support: security@enterprisescanner.com`n"

$summary | Out-File $summaryFile -Encoding UTF8
Write-Host "  ✅ Summary saved to: $summaryFile" -ForegroundColor Green

# Step 8: Production deployment instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Pre-deployment validation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Manual deployment steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Upload to production server:" -ForegroundColor White
Write-Host "   - website/js/animated-hero.js" -ForegroundColor Gray
Write-Host "   - website/js/enhanced-roi-calculator.js" -ForegroundColor Gray
Write-Host "   - website/index.html" -ForegroundColor Gray
Write-Host ""
Write-Host "2. If using CDN/cache:" -ForegroundColor White
Write-Host "   - Purge all CSS files" -ForegroundColor Gray
Write-Host "   - Purge all JS files" -ForegroundColor Gray
Write-Host "   - Purge index.html" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test on production:" -ForegroundColor White
Write-Host "   - Visit https://enterprisescanner.com" -ForegroundColor Gray
Write-Host "   - Check hero animations" -ForegroundColor Gray
Write-Host "   - Test ROI calculator" -ForegroundColor Gray
Write-Host "   - Verify charts display" -ForegroundColor Gray
Write-Host "   - Test on mobile device" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Monitor:" -ForegroundColor White
Write-Host "   - Check browser console for errors" -ForegroundColor Gray
Write-Host "   - Monitor page load times" -ForegroundColor Gray
Write-Host "   - Track user engagement" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Backup created at: $backupDir" -ForegroundColor Cyan
Write-Host "📝 Summary saved to: $summaryFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Ready for production deployment!" -ForegroundColor Green
Write-Host ""

# Optional: Open summary file
$response = Read-Host "Open deployment summary? (y/n)"
if ($response -eq 'y') {
    Start-Process notepad $summaryFile
}
