# Enterprise Scanner - Automated Homepage Upload
# Uses PowerShell's built-in capabilities to upload via SSH

param(
    [switch]$Deploy
)

$SERVER = "134.199.147.45"
$USER = "root"  
$PASSWORD = "Schroeder123!"
$LOCAL_FILE = "website\index.html"
$REMOTE_PATH = "/var/www/html/index.html"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " ENTERPRISE SCANNER - AUTOMATED DEPLOYMENT" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan

# Check if file exists
if (-not (Test-Path $LOCAL_FILE)) {
    Write-Host "ERROR: Homepage file not found at $LOCAL_FILE" -ForegroundColor Red
    exit 1
}

Write-Host "Homepage file found: $LOCAL_FILE" -ForegroundColor Green

# Get file size and preview
$fileSize = (Get-Item $LOCAL_FILE).Length
$fileContent = Get-Content $LOCAL_FILE -Head 5 | Out-String
Write-Host "File size: $fileSize bytes" -ForegroundColor Gray
Write-Host "File preview:" -ForegroundColor Gray
Write-Host $fileContent.Substring(0, [Math]::Min(200, $fileContent.Length)) -ForegroundColor Gray

if ($Deploy) {
    # Try using SSH client if available
    Write-Host ""
    Write-Host "Attempting automated deployment..." -ForegroundColor Yellow
    
    try {
        # Check if OpenSSH client is available (Windows 10+)
        $sshPath = Get-Command ssh -ErrorAction SilentlyContinue
        if ($sshPath) {
            Write-Host "OpenSSH client found, attempting SCP upload..." -ForegroundColor Green
            
            # Create temporary expect-like script for password automation
            $scpCommand = "echo '$PASSWORD' | scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '$LOCAL_FILE' '${USER}@${SERVER}:${REMOTE_PATH}'"
            Write-Host "Command: $scpCommand" -ForegroundColor Gray
            
            # Execute SCP (this might not work due to password prompting)
            $result = Start-Process -FilePath "cmd" -ArgumentList "/c", $scpCommand -Wait -PassThru -WindowStyle Hidden
            
            if ($result.ExitCode -eq 0) {
                Write-Host "SUCCESS: File uploaded successfully!" -ForegroundColor Green
            } else {
                Write-Host "SCP upload failed, falling back to manual instructions" -ForegroundColor Yellow
            }
        } else {
            Write-Host "OpenSSH not available, showing manual instructions" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Automated deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Proceeding with manual instructions..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "MANUAL DEPLOYMENT OPTIONS:" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

Write-Host "OPTION 1: WinSCP (Recommended)" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Yellow
Write-Host "1. Download WinSCP from https://winscp.net" -ForegroundColor White
Write-Host "2. Connect with these settings:" -ForegroundColor White
Write-Host "   • Host: $SERVER" -ForegroundColor Green
Write-Host "   • Username: $USER" -ForegroundColor Green  
Write-Host "   • Password: $PASSWORD" -ForegroundColor Green
Write-Host "   • Protocol: SCP or SFTP" -ForegroundColor Green
Write-Host "3. Navigate to: /var/www/html/" -ForegroundColor White
Write-Host "4. Upload: $LOCAL_FILE" -ForegroundColor White
Write-Host "5. Overwrite existing index.html" -ForegroundColor White

Write-Host ""
Write-Host "OPTION 2: Git Bash / WSL" -ForegroundColor Yellow  
Write-Host "------------------------" -ForegroundColor Yellow
Write-Host "scp -o StrictHostKeyChecking=no $LOCAL_FILE ${USER}@${SERVER}:${REMOTE_PATH}" -ForegroundColor Green

Write-Host ""
Write-Host "OPTION 3: PuTTY PSCP" -ForegroundColor Yellow
Write-Host "--------------------" -ForegroundColor Yellow  
Write-Host "pscp -pw $PASSWORD $LOCAL_FILE ${USER}@${SERVER}:${REMOTE_PATH}" -ForegroundColor Green

Write-Host ""
Write-Host "VERIFICATION:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "After upload, test at:" -ForegroundColor White
Write-Host "• http://enterprisescanner.com" -ForegroundColor Green
Write-Host "• http://$SERVER" -ForegroundColor Green
Write-Host ""
Write-Host "Expected result: Professional homepage with ROI calculator" -ForegroundColor Green

Write-Host ""
Write-Host "To run automated deployment (experimental):" -ForegroundColor Yellow
Write-Host ".\deploy_homepage_auto.ps1 -Deploy" -ForegroundColor Green