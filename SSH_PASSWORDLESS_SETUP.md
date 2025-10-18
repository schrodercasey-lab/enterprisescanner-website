# SSH Passwordless Setup - Manual Guide
**Created:** October 16, 2025  
**Purpose:** Set up SSH keys for passwordless server access

---

## 🎯 Goal
Enable passwordless SSH so `deploy`, `backup`, and `dt` commands work without password prompts.

---

## 📋 Step-by-Step Instructions

### Step 1: Check if SSH Key Exists
**Open a NEW PowerShell window** (not in VS Code), then run:

```powershell
ls ~\.ssh\
```

**What to look for:**
- If you see `id_ed25519` and `id_ed25519.pub` → You already have a key! Skip to Step 3.
- If you see `id_rsa` and `id_rsa.pub` → You have an older key, can use it or create new one.
- If folder doesn't exist or is empty → Continue to Step 2.

---

### Step 2: Generate SSH Key (If Needed)
**In your NEW PowerShell window**, run:

```powershell
ssh-keygen -t ed25519 -C "your_email@enterprisescanner.com"
```

**When prompted:**
1. **File location:** Just press `Enter` (accept default: `C:\Users\schro\.ssh\id_ed25519`)
2. **Passphrase:** Press `Enter` twice (no passphrase for automation)

**Expected output:**
```
Your identification has been saved in C:\Users\schro\.ssh\id_ed25519
Your public key has been saved in C:\Users\schro\.ssh\id_ed25519.pub
```

---

### Step 3: Display Your Public Key
**In your NEW PowerShell window**, run:

```powershell
Get-Content ~\.ssh\id_ed25519.pub
```

**Copy the ENTIRE output** (it looks like this):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... your_email@enterprisescanner.com
```

**Keep this copied to clipboard - you'll need it in Step 4!**

---

### Step 4: Install Key on Server
**Option A: One-Line Command (Easiest)**

In your NEW PowerShell window, run this ONE command (will ask for password ONE last time):

```powershell
type ~\.ssh\id_ed25519.pub | ssh root@134.199.147.45 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
```

**Enter password when prompted:** `Schroeder123!`

**Expected output:** (Nothing means success!)

---

**Option B: Manual Method (If Option A fails)**

1. **SSH to server** (will ask for password):
   ```powershell
   ssh root@134.199.147.45
   ```
   Password: `Schroeder123!`

2. **On the server**, run these commands:
   ```bash
   mkdir -p ~/.ssh
   nano ~/.ssh/authorized_keys
   ```

3. **Paste your public key** (from Step 3) into the file
   - Press `Ctrl+O` to save
   - Press `Enter` to confirm
   - Press `Ctrl+X` to exit

4. **Set correct permissions**:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

5. **Exit server**:
   ```bash
   exit
   ```

---

### Step 5: Test Passwordless Connection
**In your NEW PowerShell window**, run:

```powershell
ssh root@134.199.147.45 "echo 'Passwordless SSH works!'"
```

**Expected result:** 
- Should print: `Passwordless SSH works!`
- Should NOT ask for password
- If it asks for password, see Troubleshooting section below

---

### Step 6: Test Your Aliases
**In your NEW PowerShell window**, navigate to workspace:

```powershell
cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
```

**Test each alias:**

```powershell
# Test deploy (will SSH to server)
.\simple_deploy.ps1 -test

# Should work WITHOUT password prompt!
```

**If successful:** ✅ You're done! All aliases now work passwordless!

---

## 🔧 Troubleshooting

### Issue: Still Asks for Password After Setup

**Check 1: Verify key is on server**
```powershell
ssh root@134.199.147.45 "cat ~/.ssh/authorized_keys"
```
Should show your public key. If not, repeat Step 4.

**Check 2: Check permissions on server**
```powershell
ssh root@134.199.147.45 "ls -la ~/.ssh"
```
Should show:
- `drwx------` (700) for .ssh directory
- `-rw-------` (600) for authorized_keys file

If wrong, fix with:
```powershell
ssh root@134.199.147.45 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

**Check 3: SSH Agent (Windows)**
```powershell
# Start SSH agent
Start-Service ssh-agent

# Add your key
ssh-add ~\.ssh\id_ed25519
```

### Issue: OneDrive Blocking Access to .ssh Folder

**Solution:** Move .ssh folder outside OneDrive
```powershell
# Create .ssh in local user profile (not OneDrive)
mkdir C:\Users\schro\.ssh_local

# Copy your keys
copy ~\.ssh\* C:\Users\schro\.ssh_local\

# Tell SSH to use this location
$env:HOME = "C:\Users\schro"
```

### Issue: PowerShell Profile Still Prompts

**Possible causes:**
1. **Git credential helper** - Run: `git config --global credential.helper manager`
2. **VS Code extension** - Disable GitLens or Remote-SSH temporarily
3. **OneDrive sync** - Pause OneDrive sync temporarily

---

## 📝 What This Fixes

### ✅ After Setup, These Work WITHOUT Password:
- `deploy` - Full deployment to production
- `backup` - Server backup to local
- `dt` - Deploy and test
- Any manual `ssh root@134.199.147.45` commands

### 🎉 Benefits:
- **No more password prompts** during deployment
- **Faster workflow** - instant server access
- **Automation friendly** - scripts can run unattended
- **Secure** - SSH keys more secure than passwords

---

## 🚀 Quick Reference (After Setup)

### Test Connection
```powershell
ssh root@134.199.147.45 "uptime"
```

### Deploy Without Password
```powershell
deploy
```

### Backup Without Password
```powershell
backup
```

### Run Any Server Command
```powershell
ssh root@134.199.147.45 "docker ps"
ssh root@134.199.147.45 "systemctl status nginx"
ssh root@134.199.147.45 "tail -20 /var/log/nginx/error.log"
```

---

## 📞 Need Help?

If you get stuck:
1. Note the exact error message
2. Note which step you're on
3. Tell me what happened and I'll help troubleshoot!

---

## ✅ Success Checklist

- [ ] Step 1: Checked for existing SSH key
- [ ] Step 2: Generated new key (or used existing)
- [ ] Step 3: Copied public key to clipboard
- [ ] Step 4: Installed key on server
- [ ] Step 5: Tested passwordless connection (SUCCESS!)
- [ ] Step 6: Tested deploy/backup aliases (NO PASSWORD!)

**Once all checked:** 🎉 You're set up for passwordless SSH forever!

---

**Next:** Once this is working, reload your PowerShell profile with `. $PROFILE` and it should load without any password prompts!
