# Enterprise Scanner - Homepage Upload Script
# Cloud deployment via existing infrastructure

$ErrorActionPreference = "Stop"

Write-Host "Enterprise Scanner Homepage Deployment" -ForegroundColor Cyan
Write-Host "Target: enterprisescanner.com (134.199.147.45)" -ForegroundColor Green
Write-Host ""

# Check if WinSCP is available
if (Get-Command "WinSCP.exe" -ErrorAction SilentlyContinue) {
    Write-Host "Using WinSCP for deployment..." -ForegroundColor Yellow
    
    $winscp = @"
open scp://root@134.199.147.45
put website/index.html /var/www/html/index.html
exit
"@
    
    $winscp | WinSCP.exe /console /script=-
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Homepage uploaded via WinSCP!" -ForegroundColor Green
        exit 0
    }
}

# Check if PowerShell SSH module is available
if (Get-Module -ListAvailable -Name Posh-SSH) {
    Write-Host "Using PowerShell SSH module..." -ForegroundColor Yellow
    
    Import-Module Posh-SSH
    
    # Prompt for credentials
    $credential = Get-Credential -Message "Enter SSH credentials for 134.199.147.45"
    
    try {
        $session = New-SSHSession -ComputerName "134.199.147.45" -Credential $credential
        Set-SCPFile -ComputerName "134.199.147.45" -Credential $credential -LocalFile "website/index.html" -RemotePath "/var/www/html/index.html"
        Remove-SSHSession $session
        
        Write-Host "SUCCESS: Homepage uploaded via PowerShell SSH!" -ForegroundColor Green
        exit 0
    } catch {
        Write-Host "PowerShell SSH upload failed: $_" -ForegroundColor Red
    }
}

# Manual deployment instructions
Write-Host "Manual Deployment Instructions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "OPTION 1: Download WinSCP" -ForegroundColor White
Write-Host "1. Download: https://winscp.net/eng/download.php" -ForegroundColor Gray
Write-Host "2. Install and open WinSCP" -ForegroundColor Gray
Write-Host "3. Connect with settings:" -ForegroundColor Gray
Write-Host "   Protocol: SCP" -ForegroundColor Gray
Write-Host "   Host: 134.199.147.45" -ForegroundColor Gray
Write-Host "   Username: root" -ForegroundColor Gray
Write-Host "   Password: [Your server password]" -ForegroundColor Gray
Write-Host "4. Upload file: website/index.html" -ForegroundColor Gray
Write-Host "5. To remote path: /var/www/html/index.html" -ForegroundColor Gray
Write-Host ""

Write-Host "OPTION 2: Online SSH Clients" -ForegroundColor White
Write-Host "Try these online SSH clients:" -ForegroundColor Gray
Write-Host "• https://shell.cloud.google.com/" -ForegroundColor Gray
Write-Host "• https://gateone.liftoff.github.io/" -ForegroundColor Gray
Write-Host "• https://webconsole.dev/" -ForegroundColor Gray
Write-Host ""
Write-Host "Connection details:" -ForegroundColor Gray
Write-Host "Host: 134.199.147.45" -ForegroundColor Gray
Write-Host "Username: root" -ForegroundColor Gray
Write-Host "Command: nano /var/www/html/index.html" -ForegroundColor Gray
Write-Host ""

Write-Host "OPTION 3: Install PowerShell SSH Module" -ForegroundColor White
Write-Host "Run: Install-Module -Name Posh-SSH -Force" -ForegroundColor Gray
Write-Host "Then run this script again" -ForegroundColor Gray
Write-Host ""

$fileSize = (Get-Item "website/index.html").Length
Write-Host "Homepage file ready: $fileSize bytes" -ForegroundColor Cyan
Write-Host "File location: $((Get-Item 'website/index.html').FullName)" -ForegroundColor Cyan