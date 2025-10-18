# SSH Key Setup Script for Enterprise Scanner
# This will fix the password authentication issue

Write-Host "`n🔐 SSH KEY SETUP FOR ENTERPRISE SCANNER" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$SERVER = "134.199.147.45"
$SSH_DIR = "$env:USERPROFILE\.ssh"

# Step 1: Check if SSH directory exists
Write-Host "📁 Step 1: Checking SSH directory..." -ForegroundColor Yellow
if (-not (Test-Path $SSH_DIR)) {
    New-Item -ItemType Directory -Path $SSH_DIR | Out-Null
    Write-Host "   ✅ Created $SSH_DIR" -ForegroundColor Green
} else {
    Write-Host "   ✅ SSH directory exists" -ForegroundColor Green
}

# Step 2: Check for existing SSH keys
Write-Host "`n🔑 Step 2: Checking for existing SSH keys..." -ForegroundColor Yellow
$keyExists = Test-Path "$SSH_DIR\id_rsa"
$pubKeyExists = Test-Path "$SSH_DIR\id_rsa.pub"

if ($keyExists -and $pubKeyExists) {
    Write-Host "   ✅ SSH keys already exist!" -ForegroundColor Green
    Write-Host "   Private key: $SSH_DIR\id_rsa" -ForegroundColor Gray
    Write-Host "   Public key: $SSH_DIR\id_rsa.pub" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  SSH keys not found. Generating new keys..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Press Enter for all prompts (or set a passphrase for extra security)" -ForegroundColor Cyan
    Write-Host ""
    
    # Generate SSH key
    ssh-keygen -t rsa -b 4096 -f "$SSH_DIR\id_rsa" -C "enterprisescanner-automation"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n   ✅ SSH keys generated successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n   ❌ Failed to generate SSH keys" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Get the public key
Write-Host "`n📋 Step 3: Getting your public key..." -ForegroundColor Yellow
$publicKey = Get-Content "$SSH_DIR\id_rsa.pub"
Write-Host "   ✅ Public key loaded" -ForegroundColor Green

# Step 4: Display the public key
Write-Host "`n📤 Step 4: Your public key (already copied to clipboard):" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host $publicKey -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray

# Copy to clipboard
$publicKey | Set-Clipboard
Write-Host "`n   ✅ Public key copied to clipboard!" -ForegroundColor Green

# Step 5: Instructions for server
Write-Host "`n🔧 Step 5: ADD KEY TO SERVER (You're already logged in!)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "In your SSH terminal (where you're logged in), run these commands:" -ForegroundColor White
Write-Host ""
Write-Host "mkdir -p ~/.ssh" -ForegroundColor Cyan
Write-Host "chmod 700 ~/.ssh" -ForegroundColor Cyan
Write-Host "nano ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then:" -ForegroundColor White
Write-Host "1. Paste your public key (Ctrl+V or Right-click)" -ForegroundColor White
Write-Host "2. Save with Ctrl+X, then Y, then Enter" -ForegroundColor White
Write-Host "3. Run: chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray

# Step 6: Test instructions
Write-Host "`n✅ Step 6: TEST CONNECTION (after adding key to server)" -ForegroundColor Yellow
Write-Host "Run this command in a NEW PowerShell window:" -ForegroundColor White
Write-Host ""
Write-Host "ssh root@$SERVER `"echo 'SSH key working!'`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "If it works WITHOUT asking for password, you're done! 🎉" -ForegroundColor Green

Write-Host "`n─────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "💡 QUICK REFERENCE:" -ForegroundColor Yellow
Write-Host "Your public key is in clipboard - just paste it on the server!" -ForegroundColor White
Write-Host "After setup, all SCP and SSH commands will work without passwords!" -ForegroundColor White
Write-Host "─────────────────────────────────────────────────────`n" -ForegroundColor Gray
