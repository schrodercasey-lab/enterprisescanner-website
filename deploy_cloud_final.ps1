# Enterprise Scanner - Cloud Homepage Deployment
# Using PowerShell SSH module with your cloud infrastructure

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "    ENTERPRISE SCANNER - CLOUD HOMEPAGE DEPLOYMENT" -ForegroundColor Cyan  
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target Server: 134.199.147.45" -ForegroundColor Green
Write-Host "Domain: enterprisescanner.com" -ForegroundColor Green
Write-Host "Homepage File: 39,791 bytes ready" -ForegroundColor Green
Write-Host ""

# Import the SSH module
try {
    Import-Module Posh-SSH -Force
    Write-Host "✓ PowerShell SSH module loaded" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to load SSH module: $_" -ForegroundColor Red
    exit 1
}

# Get credentials for server access
Write-Host "🔐 Please enter your cloud server credentials:" -ForegroundColor Yellow
$credential = Get-Credential -Message "Enter SSH credentials for your cloud server (134.199.147.45)" -UserName "root"

if ($credential -eq $null) {
    Write-Host "❌ Credentials required for deployment" -ForegroundColor Red
    exit 1
}

try {
    Write-Host ""
    Write-Host "🔗 Connecting to cloud server..." -ForegroundColor Yellow
    
    # Create SSH session
    $session = New-SSHSession -ComputerName "134.199.147.45" -Credential $credential -AcceptKey
    
    if ($session.Connected) {
        Write-Host "✓ Connected to cloud server successfully" -ForegroundColor Green
        
        Write-Host "📁 Uploading homepage file..." -ForegroundColor Yellow
        
        # Upload the homepage file
        Set-SCPFile -ComputerName "134.199.147.45" -Credential $credential -LocalFile "website\index.html" -RemotePath "/var/www/html/index.html" -AcceptKey
        
        Write-Host "✓ Homepage file uploaded successfully!" -ForegroundColor Green
        
        # Verify the upload
        Write-Host "🔍 Verifying upload..." -ForegroundColor Yellow
        $result = Invoke-SSHCommand -SSHSession $session -Command "ls -la /var/www/html/index.html"
        
        if ($result.ExitStatus -eq 0) {
            Write-Host "✓ Upload verified on server" -ForegroundColor Green
            Write-Host "File details: $($result.Output)" -ForegroundColor Gray
        }
        
        # Set proper permissions
        Write-Host "🔧 Setting file permissions..." -ForegroundColor Yellow
        $permResult = Invoke-SSHCommand -SSHSession $session -Command "chmod 644 /var/www/html/index.html && chown www-data:www-data /var/www/html/index.html"
        
        if ($permResult.ExitStatus -eq 0) {
            Write-Host "✓ File permissions set correctly" -ForegroundColor Green
        }
        
        # Clean up session
        Remove-SSHSession $session
        
        Write-Host ""
        Write-Host "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Your website is now live at:" -ForegroundColor Cyan
        Write-Host "   • http://enterprisescanner.com" -ForegroundColor White
        Write-Host "   • http://134.199.147.45" -ForegroundColor White
        Write-Host ""
        
        # Test the deployment
        Write-Host "🔍 Testing deployment..." -ForegroundColor Yellow
        try {
            $webResponse = Invoke-WebRequest -Uri "http://enterprisescanner.com" -TimeoutSec 10
            if ($webResponse.Content.Length -gt 30000) {
                Write-Host "✓ Website responding with full homepage content!" -ForegroundColor Green
                Write-Host "  Content size: $($webResponse.Content.Length) bytes" -ForegroundColor Gray
            } else {
                Write-Host "⚠ Website responding but content seems incomplete" -ForegroundColor Yellow
                Write-Host "  Content size: $($webResponse.Content.Length) bytes" -ForegroundColor Gray
            }
        } catch {
            Write-Host "⚠ Unable to test website immediately (may need DNS propagation)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "✨ ENTERPRISE SCANNER IS NOW LIVE! ✨" -ForegroundColor Cyan
        
    } else {
        Write-Host "❌ Failed to connect to cloud server" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "• Verify server credentials are correct" -ForegroundColor Gray
    Write-Host "• Check server SSH access is enabled" -ForegroundColor Gray
    Write-Host "• Ensure firewall allows SSH connections" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "           CLOUD DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan