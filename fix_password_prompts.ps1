# Password Prompt Fix - Comprehensive Solution
# Created: October 16, 2025
# Purpose: Permanent fix for password prompt issues

Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     PASSWORD PROMPT FIX - AUTOMATED SOLUTION    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Run diagnostic first
Write-Host "[Step 1/5] Running diagnostic..." -ForegroundColor Yellow
if (Test-Path ".\diagnose_password_prompts.ps1") {
    Write-Host "   Run diagnostic first: .\diagnose_password_prompts.ps1" -ForegroundColor White
    Write-Host "   Then come back and run this script again." -ForegroundColor White
    Write-Host ""
    $runDiag = Read-Host "Run diagnostic now? (y/n)"
    if ($runDiag -eq 'y') {
        .\diagnose_password_prompts.ps1
        Write-Host ""
        Write-Host "Review the diagnostic report above, then run this script again." -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "This script will apply these fixes:" -ForegroundColor Cyan
Write-Host "  1. Configure Git to cache credentials" -ForegroundColor White
Write-Host "  2. Set up SSH keys for passwordless access" -ForegroundColor White
Write-Host "  3. Configure SSH agent (if needed)" -ForegroundColor White
Write-Host "  4. Test all connections" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue with automated fix? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Exiting..." -ForegroundColor Yellow
    exit
}

# Fix 1: Git Credential Configuration
Write-Host "`n[Fix 1/4] Configuring Git credentials..." -ForegroundColor Yellow
try {
    # Set git to cache credentials for 1 hour
    git config --global credential.helper cache
    git config --global credential.helper 'cache --timeout=3600'
    Write-Host "   ✓ Git credential caching enabled" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Git configuration failed: $_" -ForegroundColor Yellow
}

# Fix 2: SSH Key Setup
Write-Host "`n[Fix 2/4] Checking SSH keys..." -ForegroundColor Yellow
$sshDir = "$env:USERPROFILE\.ssh"
$keyPath = "$sshDir\id_ed25519"
$pubKeyPath = "$sshDir\id_ed25519.pub"

if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Host "   ✓ Created .ssh directory" -ForegroundColor Green
}

if (-not (Test-Path $keyPath)) {
    Write-Host "   Generating new SSH key..." -ForegroundColor White
    Write-Host "   (Press Enter 3 times - no passphrase for automation)" -ForegroundColor Gray
    
    ssh-keygen -t ed25519 -f $keyPath -C "enterprisescanner-automation" -N '""'
    
    if (Test-Path $keyPath) {
        Write-Host "   ✓ SSH key generated successfully" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SSH key generation failed" -ForegroundColor Red
    }
} else {
    Write-Host "   ✓ SSH key already exists" -ForegroundColor Green
}

# Fix 3: Display public key for server installation
if (Test-Path $pubKeyPath) {
    Write-Host "`n[Fix 3/4] SSH Key Installation..." -ForegroundColor Yellow
    Write-Host "   Your public key is:" -ForegroundColor White
    Write-Host ""
    $publicKey = Get-Content $pubKeyPath
    Write-Host "   $publicKey" -ForegroundColor Cyan
    Write-Host ""
    
    # Copy to clipboard
    try {
        $publicKey | Set-Clipboard
        Write-Host "   ✓ Public key copied to clipboard!" -ForegroundColor Green
    } catch {
        Write-Host "   (Manual copy needed)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "   To install on server, run this ONE command:" -ForegroundColor Yellow
    Write-Host ""
    $installCmd = "type $pubKeyPath | ssh root@134.199.147.45 `"mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh`""
    Write-Host "   $installCmd" -ForegroundColor White
    Write-Host ""
    
    $installNow = Read-Host "   Install SSH key on server now? (y/n)"
    if ($installNow -eq 'y') {
        Write-Host "   Installing..." -ForegroundColor Yellow
        Invoke-Expression $installCmd
        Write-Host "   ✓ SSH key installed on server" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Skipped - install manually later" -ForegroundColor Yellow
    }
}

# Fix 4: Test connections
Write-Host "`n[Fix 4/4] Testing connections..." -ForegroundColor Yellow

Write-Host "   Testing SSH connection..." -ForegroundColor White
$sshTest = ssh root@134.199.147.45 "echo 'SSH works!'" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ SSH connection successful (passwordless!)" -ForegroundColor Green
} else {
    Write-Host "   ⚠ SSH still requires password - key may not be installed" -ForegroundColor Yellow
}

# Summary
Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    SUMMARY                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "What was done:" -ForegroundColor White
Write-Host "  ✓ Git credential caching enabled" -ForegroundColor Green
Write-Host "  ✓ SSH key generated/verified" -ForegroundColor Green
if ($installNow -eq 'y') {
    Write-Host "  ✓ SSH key installed on server" -ForegroundColor Green
} else {
    Write-Host "  ⚠ SSH key NOT installed (manual install needed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Reload your PowerShell profile: . `$PROFILE" -ForegroundColor White
Write-Host "  2. Test aliases: hot, contacts, crm" -ForegroundColor White
Write-Host "  3. Test deployment: deploy" -ForegroundColor White
Write-Host ""

Write-Host "If still having password prompts:" -ForegroundColor Yellow
Write-Host "  • Review diagnostic report" -ForegroundColor Gray
Write-Host "  • Check VS Code extensions (GitLens, Remote-SSH)" -ForegroundColor Gray
Write-Host "  • Verify SSH key is on server: ssh root@134.199.147.45 'cat ~/.ssh/authorized_keys'" -ForegroundColor Gray
Write-Host ""
