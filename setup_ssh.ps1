# SSH Key Setup for GitHub (No Admin Required)
# This script generates SSH keys and configures Git to use them

Write-Host "=== GitHub SSH Key Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if .ssh directory exists, create if not
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    Write-Host "Creating .ssh directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

# Generate SSH key (Ed25519 is modern and secure)
$keyPath = "$sshDir\id_ed25519"
$email = "casey@enterprisescanner.com"  # Your GitHub email

Write-Host "Generating SSH key pair..." -ForegroundColor Yellow
if (Test-Path $keyPath) {
    Write-Host "SSH key already exists at: $keyPath" -ForegroundColor Green
    $overwrite = Read-Host "Overwrite existing key? (yes/no)"
    if ($overwrite -ne "yes") {
        Write-Host "Using existing key." -ForegroundColor Green
    } else {
        ssh-keygen -t ed25519 -C $email -f $keyPath -N '""'
    }
} else {
    # Generate key without passphrase (empty string)
    ssh-keygen -t ed25519 -C $email -f $keyPath -N '""'
}

Write-Host ""
Write-Host "=== SSH Key Generated Successfully ===" -ForegroundColor Green
Write-Host ""

# Display the public key
Write-Host "Your PUBLIC SSH key (copy this to GitHub):" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Gray
Get-Content "$keyPath.pub"
Write-Host "================================================" -ForegroundColor Gray
Write-Host ""

# Copy to clipboard if possible
try {
    Get-Content "$keyPath.pub" | Set-Clipboard
    Write-Host "✅ Public key copied to clipboard!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not copy to clipboard, please copy manually above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Go to: https://github.com/settings/ssh/new" -ForegroundColor White
Write-Host "2. Title: 'Enterprise Scanner Workstation'" -ForegroundColor White
Write-Host "3. Paste the public key (already copied to clipboard)" -ForegroundColor White
Write-Host "4. Click 'Add SSH key'" -ForegroundColor White
Write-Host ""
Write-Host "Then press ENTER here to continue..." -ForegroundColor Yellow
Read-Host

# Configure Git to use SSH
Write-Host ""
Write-Host "=== Configuring Git ===" -ForegroundColor Cyan

# Set Git to use SSH instead of HTTPS for GitHub
git config --global url."git@github.com:".insteadOf "https://github.com/"

# Configure SSH to use the key
$sshConfig = "$sshDir\config"
$configContent = @"
Host github.com
    HostName github.com
    User git
    IdentityFile $keyPath
    IdentitiesOnly yes
"@

Write-Host "Creating SSH config file..." -ForegroundColor Yellow
Set-Content -Path $sshConfig -Value $configContent

# Test SSH connection
Write-Host ""
Write-Host "=== Testing GitHub SSH Connection ===" -ForegroundColor Cyan
ssh -T git@github.com

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your repository is now configured to use SSH." -ForegroundColor White
Write-Host "No more password prompts for Git operations!" -ForegroundColor White
Write-Host ""
Write-Host "Current repository SSH URL:" -ForegroundColor Cyan
git remote get-url origin
Write-Host ""
