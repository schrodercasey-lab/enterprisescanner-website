
# Enterprise Scanner - Homepage Upload Script
# Cloud deployment via existing infrastructure

$ErrorActionPreference = "Stop"

Write-Host "🚀 Enterprise Scanner Homepage Deployment" -ForegroundColor Cyan
Write-Host "Target: enterprisescanner.com (134.199.147.45)" -ForegroundColor Green
Write-Host ""

# Method 1: Try WinSCP if available
if (Get-Command "WinSCP.exe" -ErrorAction SilentlyContinue) {
    Write-Host "📁 Using WinSCP for deployment..." -ForegroundColor Yellow
    
    $winscp = @"
open scp://root@134.199.147.45
put website/index.html /var/www/html/index.html
exit
"@
    
    $winscp | WinSCP.exe /console /script=-
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Homepage uploaded successfully via WinSCP!" -ForegroundColor Green
        exit 0
    }
}

# Method 2: Use PowerShell SSH module if available
if (Get-Module -ListAvailable -Name Posh-SSH) {
    Write-Host "🔧 Using PowerShell SSH module..." -ForegroundColor Yellow
    
    Import-Module Posh-SSH
    
    # Prompt for credentials
    $credential = Get-Credential -Message "Enter SSH credentials for 134.199.147.45"
    
    try {
        $session = New-SSHSession -ComputerName "134.199.147.45" -Credential $credential
        Set-SCPFile -ComputerName "134.199.147.45" -Credential $credential -LocalFile "website/index.html" -RemotePath "/var/www/html/index.html"
        Remove-SSHSession $session
        
        Write-Host "✅ Homepage uploaded successfully via PowerShell SSH!" -ForegroundColor Green
        exit 0
    } catch {
        Write-Host "❌ PowerShell SSH upload failed: $_" -ForegroundColor Red
    }
}

# Method 3: Manual deployment instructions
Write-Host "📋 Manual Deployment Instructions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Download and install WinSCP: https://winscp.net/eng/download.php" -ForegroundColor White
Write-Host ""
Write-Host "2. Open WinSCP and connect with these settings:" -ForegroundColor White
Write-Host "   Protocol: SCP" -ForegroundColor Gray
Write-Host "   Host: 134.199.147.45" -ForegroundColor Gray
Write-Host "   Username: root" -ForegroundColor Gray
Write-Host "   Password: [Your server password]" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Navigate to remote directory: /var/www/html/" -ForegroundColor White
Write-Host ""
Write-Host "4. Upload local file: website/index.html" -ForegroundColor White
Write-Host "   → Remote file: /var/www/html/index.html" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Verify deployment at: http://enterprisescanner.com" -ForegroundColor White
Write-Host ""

# Method 4: Alternative online tools
Write-Host "🌐 Alternative: Online SSH Clients" -ForegroundColor Yellow
Write-Host ""
Write-Host "Try these online SSH clients:" -ForegroundColor White
Write-Host "• https://shell.cloud.google.com/" -ForegroundColor Gray
Write-Host "• https://gateone.liftoff.github.io/" -ForegroundColor Gray
Write-Host "• https://webconsole.dev/" -ForegroundColor Gray
Write-Host ""
Write-Host "Connection details:" -ForegroundColor White
Write-Host "Host: 134.199.147.45" -ForegroundColor Gray
Write-Host "Username: root" -ForegroundColor Gray
Write-Host "Command: nano /var/www/html/index.html" -ForegroundColor Gray
Write-Host ""

Write-Host "📁 Homepage file location: C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website\index.html" -ForegroundColor Cyan
Write-Host "📊 File size: 39,791 bytes" -ForegroundColor Cyan
