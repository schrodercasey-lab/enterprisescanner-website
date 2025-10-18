# Quick SSH Key Fix - Step by Step Guide
# Run each command one at a time in PowerShell

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                SSH PASSWORD FIX - QUICK GUIDE                 ║
╚═══════════════════════════════════════════════════════════════╝

STEP 1: Check if you have SSH keys
──────────────────────────────────────────────────────────────

"@ -ForegroundColor Cyan

Write-Host "Run this in PowerShell:" -ForegroundColor Yellow
Write-Host "   ls ~\.ssh\" -ForegroundColor White
Write-Host ""

if (Test-Path "$env:USERPROFILE\.ssh\id_rsa.pub") {
    Write-Host "✅ FOUND: You have SSH keys!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your public key:" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Gray
    Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Gray
    Write-Host ""
    Write-Host "✅ COPIED TO CLIPBOARD!" -ForegroundColor Green
    Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub" | Set-Clipboard
} else {
    Write-Host "❌ NOT FOUND: You need to generate SSH keys" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run this command in PowerShell:" -ForegroundColor Yellow
    Write-Host "   ssh-keygen -t rsa -b 4096" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Enter for ALL prompts (or set a passphrase)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then run this script again!" -ForegroundColor Yellow
    exit
}

Write-Host @"

STEP 2: Add key to server (you're already logged in!)
──────────────────────────────────────────────────────────────

In your SSH terminal, copy/paste these commands:

"@ -ForegroundColor Cyan

Write-Host @"
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "PASTE_YOUR_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

"@ -ForegroundColor White

Write-Host "Replace PASTE_YOUR_KEY_HERE with the key shown above (already in clipboard!)" -ForegroundColor Yellow
Write-Host ""

Write-Host @"

OR use nano editor:
──────────────────────────────────────────────────────────────

"@ -ForegroundColor Cyan

Write-Host @"
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys

"@ -ForegroundColor White

Write-Host "Then:" -ForegroundColor Yellow
Write-Host "1. Paste your key (Ctrl+V or Right-click)" -ForegroundColor White
Write-Host "2. Save: Ctrl+X, then Y, then Enter" -ForegroundColor White
Write-Host "3. Run: chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host ""

Write-Host @"

STEP 3: Test it works
──────────────────────────────────────────────────────────────

Open a NEW PowerShell window and run:

"@ -ForegroundColor Cyan

Write-Host "   ssh root@134.199.147.45 `"echo 'Success!'`"" -ForegroundColor White
Write-Host ""
Write-Host "If it says 'Success!' WITHOUT asking for password, you're done! 🎉" -ForegroundColor Green
Write-Host ""
