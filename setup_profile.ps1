# PowerShell Profile Setup Script
# Run this to install the profile automatically

Write-Host "`n=== PowerShell Profile Setup ===" -ForegroundColor Cyan

# Get profile path
$profilePath = $PROFILE
Write-Host "`nProfile location: $profilePath" -ForegroundColor White

# Check if profile exists
if (Test-Path $profilePath) {
    Write-Host "[!] Profile already exists" -ForegroundColor Yellow
    $backup = "${profilePath}.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $profilePath $backup
    Write-Host "[+] Backed up to: $backup" -ForegroundColor Green
}

# Copy our profile
$sourcePath = ".\PowerShell_Profile.ps1"
if (Test-Path $sourcePath) {
    Copy-Item $sourcePath $profilePath -Force
    Write-Host "[+] Profile installed successfully!" -ForegroundColor Green
} else {
    Write-Host "[!] Error: PowerShell_Profile.ps1 not found" -ForegroundColor Red
    exit 1
}

# Reload profile
Write-Host "`n[*] Loading profile..." -ForegroundColor Cyan
. $PROFILE

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nTest your aliases:" -ForegroundColor Cyan
Write-Host "  ws          - Navigate to workspace" -ForegroundColor White
Write-Host "  hot         - View high-priority Fortune 500 leads" -ForegroundColor White
Write-Host "  crm         - Update CRM" -ForegroundColor White
Write-Host "  contacts    - View all contacts" -ForegroundColor White
Write-Host "  deploy      - Deploy website" -ForegroundColor White
Write-Host ""
