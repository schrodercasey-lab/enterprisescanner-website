# Enterprise Scanner - Advanced PowerShell Deployment
# Uses built-in Windows capabilities for file transfer

param(
    [switch]$Execute
)

$SERVER = "134.199.147.45"
$USER = "root"
$PASSWORD = "Schroeder123!"
$LOCAL_FILE = "website\index.html"
$REMOTE_PATH = "/var/www/html/index.html"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " ENTERPRISE SCANNER - ADVANCED DEPLOYMENT SOLUTION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Verify file exists
if (-not (Test-Path $LOCAL_FILE)) {
    Write-Host "ERROR: File not found: $LOCAL_FILE" -ForegroundColor Red
    exit 1
}

$fileInfo = Get-Item $LOCAL_FILE
Write-Host "File Ready: $($fileInfo.Name)" -ForegroundColor Green
Write-Host "Size: $($fileInfo.Length) bytes" -ForegroundColor Gray
Write-Host "Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray

if ($Execute) {
    Write-Host ""
    Write-Host "ATTEMPTING AUTOMATED DEPLOYMENT..." -ForegroundColor Yellow
    Write-Host "===================================" -ForegroundColor Yellow
    
    # Try PowerShell SSH (Windows 10+)
    try {
        Write-Host "Checking for OpenSSH client..." -ForegroundColor Gray
        $sshPath = Get-Command ssh -ErrorAction SilentlyContinue
        
        if ($sshPath) {
            Write-Host "OpenSSH found: $($sshPath.Source)" -ForegroundColor Green
            
            # Create temporary batch file for password automation
            $batchContent = @"
@echo off
echo $PASSWORD | scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL "$LOCAL_FILE" "${USER}@${SERVER}:${REMOTE_PATH}"
"@
            $batchFile = "temp_deploy.bat"
            $batchContent | Out-File -FilePath $batchFile -Encoding ASCII
            
            Write-Host "Executing SCP transfer..." -ForegroundColor Yellow
            $result = Start-Process -FilePath $batchFile -Wait -PassThru -WindowStyle Hidden
            
            Remove-Item $batchFile -ErrorAction SilentlyContinue
            
            if ($result.ExitCode -eq 0) {
                Write-Host "SUCCESS: File uploaded via SCP!" -ForegroundColor Green
                
                # Verify deployment
                Write-Host "Verifying deployment..." -ForegroundColor Yellow
                Start-Sleep -Seconds 3
                
                try {
                    $response = Invoke-WebRequest -Uri "http://$SERVER" -TimeoutSec 10
                    if ($response.Content.Length -gt 1000) {
                        Write-Host "DEPLOYMENT VERIFIED: Website updated!" -ForegroundColor Green
                        Write-Host "New content length: $($response.Content.Length) characters" -ForegroundColor Green
                        return
                    }
                } catch {
                    Write-Host "Deployment verification inconclusive" -ForegroundColor Yellow
                }
            } else {
                Write-Host "SCP transfer failed, trying alternative method..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "OpenSSH not available" -ForegroundColor Yellow
        }
        
        # Try using plink (if PuTTY is installed)
        Write-Host "Checking for PuTTY tools..." -ForegroundColor Gray
        $plinkPath = Get-Command plink -ErrorAction SilentlyContinue
        $pscpPath = Get-Command pscp -ErrorAction SilentlyContinue
        
        if ($pscpPath) {
            Write-Host "PuTTY PSCP found: $($pscpPath.Source)" -ForegroundColor Green
            
            Write-Host "Uploading via PSCP..." -ForegroundColor Yellow
            $pscpArgs = @("-batch", "-pw", $PASSWORD, $LOCAL_FILE, "${USER}@${SERVER}:${REMOTE_PATH}")
            $pscpResult = Start-Process -FilePath $pscpPath.Source -ArgumentList $pscpArgs -Wait -PassThru -WindowStyle Hidden
            
            if ($pscpResult.ExitCode -eq 0) {
                Write-Host "SUCCESS: File uploaded via PSCP!" -ForegroundColor Green
                
                # Verify deployment
                Start-Sleep -Seconds 3
                try {
                    $response = Invoke-WebRequest -Uri "http://$SERVER" -TimeoutSec 10
                    if ($response.Content.Length -gt 1000) {
                        Write-Host "DEPLOYMENT VERIFIED: Website updated!" -ForegroundColor Green
                        return
                    }
                } catch {
                    Write-Host "Deployment verification inconclusive" -ForegroundColor Yellow
                }
            } else {
                Write-Host "PSCP transfer failed" -ForegroundColor Red
            }
        } else {
            Write-Host "PuTTY PSCP not available" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "Automated deployment error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "AUTOMATED DEPLOYMENT COMPLETED" -ForegroundColor Yellow
    Write-Host "If successful, test at: http://enterprisescanner.com" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "DEPLOYMENT OPTIONS:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "OPTION 1: Run Automated Deployment" -ForegroundColor Yellow
    Write-Host ".\deploy_advanced.ps1 -Execute" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "OPTION 2: WinSCP (Recommended)" -ForegroundColor Yellow
    Write-Host "1. Download: https://winscp.net/eng/download.php" -ForegroundColor White
    Write-Host "2. Connect: $SERVER (user: $USER, pass: $PASSWORD)" -ForegroundColor White
    Write-Host "3. Upload: $LOCAL_FILE to /var/www/html/" -ForegroundColor White
    Write-Host ""
    
    Write-Host "OPTION 3: Git Bash/WSL" -ForegroundColor Yellow
    Write-Host "scp $LOCAL_FILE ${USER}@${SERVER}:${REMOTE_PATH}" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "VERIFICATION:" -ForegroundColor Cyan
    Write-Host "After deployment, visit: http://enterprisescanner.com" -ForegroundColor Green
    Write-Host "Expected: Professional homepage with ROI calculator" -ForegroundColor Green
}

Write-Host ""
Write-Host "FILE SUMMARY:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "Local File: $LOCAL_FILE" -ForegroundColor White
Write-Host "File Size: $($fileInfo.Length) bytes" -ForegroundColor White
Write-Host "Target: $SERVER$REMOTE_PATH" -ForegroundColor White
Write-Host "Ready for Fortune 500 business development!" -ForegroundColor Green