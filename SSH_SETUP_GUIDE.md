# GitHub SSH Setup Guide

## Quick Start

Run this command in PowerShell:
```powershell
.\setup_ssh.ps1
```

The script will:
1. ✅ Generate SSH key pair (Ed25519)
2. ✅ Copy public key to clipboard
3. ✅ Configure Git to use SSH
4. ✅ Test connection to GitHub

**No admin privileges required!**

---

## Manual Setup (Alternative)

### Step 1: Generate SSH Key

```powershell
ssh-keygen -t ed25519 -C "casey@enterprisescanner.com"
```

When prompted:
- **File location:** Press ENTER (use default: `C:\Users\schro\.ssh\id_ed25519`)
- **Passphrase:** Press ENTER twice (no passphrase for convenience)

### Step 2: Copy Public Key

```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
```

Or manually open the file and copy:
```
C:\Users\schro\.ssh\id_ed25519.pub
```

### Step 3: Add to GitHub

1. Go to: https://github.com/settings/ssh/new
2. Title: `Enterprise Scanner Workstation`
3. Paste the public key (Ctrl+V)
4. Click **Add SSH key**

### Step 4: Configure Git

```powershell
# Tell Git to use SSH for GitHub
git config --global url."git@github.com:".insteadOf "https://github.com/"

# Update your repository remote URL
cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
git remote set-url origin git@github.com:schrodercasey-lab/enterprisescanner-website.git
```

### Step 5: Test Connection

```powershell
ssh -T git@github.com
```

Expected output:
```
Hi schrodercasey-lab! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## Troubleshooting

### "Permission denied (publickey)"

**Solution:** Key not added to GitHub or wrong key being used.

```powershell
# Verify public key
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

# Copy and add to GitHub again
```

### "Could not resolve hostname"

**Solution:** Check internet connection or DNS.

```powershell
# Test DNS
ping github.com
```

### Git still asking for password

**Solution:** Repository still using HTTPS URL.

```powershell
# Check current URL
git remote get-url origin

# If it shows "https://...", change to SSH
git remote set-url origin git@github.com:schrodercasey-lab/enterprisescanner-website.git
```

---

## Benefits of SSH Keys

✅ **No more password prompts** - Authenticate automatically  
✅ **More secure** - Uses cryptographic keys instead of passwords  
✅ **No admin required** - User-level configuration only  
✅ **Works everywhere** - Git, GitHub CLI, SSH operations  
✅ **Modern encryption** - Ed25519 algorithm (faster than RSA)  

---

## Files Created

- `C:\Users\schro\.ssh\id_ed25519` - Private key (NEVER SHARE!)
- `C:\Users\schro\.ssh\id_ed25519.pub` - Public key (add to GitHub)
- `C:\Users\schro\.ssh\config` - SSH configuration

---

## Security Notes

🔒 **Private key stays on your computer** - Never upload or share  
🔑 **Public key goes to GitHub** - Safe to share publicly  
🚫 **No passphrase** - For convenience (acceptable for low-risk environments)  
✅ **User-level only** - No system-wide changes  

---

## Next Steps After Setup

Once SSH is configured, you can:

```powershell
# Push code without password
git push

# Pull updates without password
git pull

# Clone repositories using SSH
git clone git@github.com:schrodercasey-lab/other-repo.git
```

All Git operations will now use SSH authentication automatically!
