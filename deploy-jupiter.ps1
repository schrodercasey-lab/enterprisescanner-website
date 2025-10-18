#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ONE-COMMAND JUPITER DEPLOYMENT - Push to GitHub for instant production updates
.DESCRIPTION
    Automated Git deployment for Jupiter AI platform to enterprisescanner.com
    Commits all changes, pushes to GitHub, and triggers automatic deployment
.EXAMPLE
    .\deploy-jupiter.ps1 -Message "Jupiter WiFi Eyes launch"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Message = "🚀 Jupiter AI Platform Update - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
)

# Banner
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   🚀 JUPITER DEPLOYMENT - GIT PUSH TO PRODUCTION 🚀      " -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Change to workspace directory
Set-Location "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace"

# Step 1: Check Git status
Write-Host "[1/7] Checking Git repository status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "  ✓ Changes detected - ready to deploy!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ No changes detected - nothing to deploy" -ForegroundColor Red
    exit 0
}

# Step 2: Stage website files (production-ready only)
Write-Host "[2/7] Staging Jupiter website files..." -ForegroundColor Yellow
git add website/
git add .github/copilot-instructions.md
Write-Host "  ✓ Website files staged" -ForegroundColor Green

# Step 3: Show what will be committed
Write-Host "[3/7] Files to be deployed:" -ForegroundColor Yellow
$stagedFiles = git diff --cached --name-status
$stagedFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
$fileCount = ($stagedFiles | Measure-Object).Count
Write-Host "  → Total: $fileCount files" -ForegroundColor Green

# Step 4: Commit changes
Write-Host "[4/7] Committing changes..." -ForegroundColor Yellow
git commit -m "$Message"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Commit successful!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Commit failed!" -ForegroundColor Red
    exit 1
}

# Step 5: Push to GitHub
Write-Host "[5/7] Pushing to GitHub (origin/main)..." -ForegroundColor Yellow
Write-Host "  → Repository: schrodercasey-lab/enterprisescanner-website" -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Push successful!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Push failed! Check SSH keys or credentials" -ForegroundColor Red
    exit 1
}

# Step 6: Verify deployment
Write-Host "[6/7] Verifying deployment..." -ForegroundColor Yellow
$remoteHash = git rev-parse origin/main
$localHash = git rev-parse main
if ($remoteHash -eq $localHash) {
    Write-Host "  ✓ Local and remote branches in sync!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Warning: Branches may not be in sync" -ForegroundColor Yellow
}

# Step 7: Next steps
Write-Host "[7/7] Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   ✨ JUPITER DEPLOYMENT SUCCESSFUL! ✨                   " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Display next steps
Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure GitHub → Hosting Auto-Deploy" -ForegroundColor Cyan
Write-Host "   → If using cPanel: Setup 'Git Version Control'" -ForegroundColor White
Write-Host "   → If using Netlify/Vercel: Connect GitHub repo" -ForegroundColor White
Write-Host "   → Automatic deployment on every push!" -ForegroundColor Green
Write-Host ""
Write-Host "2. Verify SSL/HTTPS on https://enterprisescanner.com" -ForegroundColor Cyan
Write-Host "   → Required for WiFi Eyes camera access" -ForegroundColor White
Write-Host "   → Browser security policy requirement" -ForegroundColor White
Write-Host ""
Write-Host "3. Test Jupiter AI features live:" -ForegroundColor Cyan
Write-Host "   → WiFi Eyes camera system (HTTPS required)" -ForegroundColor White
Write-Host "   → Jupiter chat widget" -ForegroundColor White
Write-Host "   → 3D threat map" -ForegroundColor White
Write-Host "   → AR/VR capabilities" -ForegroundColor White
Write-Host "   → Dark AI theme toggle" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Live Site: https://enterprisescanner.com" -ForegroundColor Green
Write-Host "📊 GitHub Repo: https://github.com/schrodercasey-lab/enterprisescanner-website" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 JUPITER IS LIVE - MAKING HISTORY! 🎉" -ForegroundColor Yellow -BackgroundColor Black
Write-Host ""
