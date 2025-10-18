# Password Prompt Fix Guide
**Created:** October 16, 2025

## Problem
Password prompts appearing when reloading PowerShell profile or running commands.

## Root Cause Analysis

### Profile is Clean ✅
`PowerShell_Profile.ps1` contains NO SSH or authentication commands.
- Only contains function definitions
- No scripts executed during load
- Should never prompt for password

### Scripts Contain SSH ⚠️
These scripts DO contain SSH (but aren't run during profile load):
- `simple_deploy.ps1` - Has SSH command for nginx reload
- `simple_backup.ps1` - Has SSH commands for server backup
- Only triggered when you manually run `deploy`, `backup`, or `dt` aliases

## Possible Causes

### 1. Git Credential Helper (Most Likely)
```powershell
# Check if Git is prompting
git config --global credential.helper

# If set to "manager" or "wincred", it might prompt
```

### 2. SSH Agent
```powershell
# Check SSH agent status
Get-Service ssh-agent
```

### 3. OneDrive Sync Authentication
Since your workspace is in `OneDrive\Desktop`, OneDrive might be prompting.

### 4. VS Code Extension
Some VS Code extensions (GitLens, Remote-SSH, etc.) can trigger auth prompts.

## Solutions

### Solution 1: Identify the Exact Source
**Next time you see password prompt:**
1. Note exactly what command triggered it
2. Check the prompt title/text - does it say "SSH", "Git", "OneDrive"?
3. Take screenshot if possible

### Solution 2: Configure SSH Key Authentication
**If SSH prompts are the issue:**
```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key to server
type ~\.ssh\id_ed25519.pub | ssh root@134.199.147.45 "cat >> ~/.ssh/authorized_keys"

# Test passwordless connection
ssh root@134.199.147.45 "echo 'Success!'"
```

### Solution 3: Git Credential Caching
**If Git prompts are the issue:**
```powershell
# Cache Git credentials for 1 hour
git config --global credential.helper cache

# Or use Windows Credential Manager
git config --global credential.helper manager
```

### Solution 4: Disable VS Code Extensions Temporarily
1. Open VS Code
2. Press `Ctrl+Shift+X`
3. Disable extensions one by one:
   - GitLens
   - Remote - SSH
   - Any Git-related extensions

## Quick Test

### Test Profile Load (Should NOT Prompt)
```powershell
# This should load instantly with no password
. $PROFILE
```
**Expected:** Green success message, no password prompt

### Test Aliases That Don't Use SSH (Should NOT Prompt)
```powershell
ws          # Just changes directory
contacts    # Just reads CSV file
hot         # Just reads CSV file
ll          # Just lists files
```
**Expected:** No password prompts

### Test Aliases That DO Use SSH (WILL Prompt)
```powershell
deploy      # Will SSH to server
backup      # Will SSH to server
dt          # Will SSH to server (if -test includes SSH)
```
**Expected:** Password prompt is normal here until SSH keys are set up

## Recommended Action Plan

### Step 1: Test Profile Reload
```powershell
. $PROFILE
```
- If NO password prompt: ✅ Profile is fine
- If password prompt: ⚠️ Something else is running

### Step 2: Identify the Culprit
```powershell
# Check what's running
Get-Process | Where-Object {$_.Name -match "git|ssh|plink"}

# Check VS Code extensions
code --list-extensions | findstr -i "git ssh remote"
```

### Step 3: Set Up SSH Keys (Permanent Fix)
This eliminates ALL password prompts for server access:
1. Generate SSH key
2. Copy to server
3. Test passwordless login
4. Now `deploy`, `backup`, `dt` work without passwords!

### Step 4: Update Profile Load Test
Add this to `PowerShell_Profile.ps1` to verify clean load:
```powershell
# At the very top of profile
Write-Host "Loading profile..." -ForegroundColor Gray

# At the very bottom (after all functions)
Write-Host "Profile loaded successfully - no authentication required!" -ForegroundColor Green
```

## Current Status

### ✅ Working Without Password
- Profile load (`. $PROFILE`)
- `ws`, `web`, `contacts`, `hot`, `ll`, `crm`, `clean`
- All local-only commands

### ⚠️ Requires Password (Expected)
- `deploy` - SSH to server for deployment
- `backup` - SSH to server for backup
- `dt` - May include SSH depending on script

### 🔧 Needs Investigation
- Unexpected password prompts during profile load
- Any prompt that doesn't involve `deploy`, `backup`, or `dt`

## Next Steps

**Tell me:**
1. Which command prompted for password?
2. What did the password prompt say exactly?
3. Do you want to set up SSH keys for passwordless deployment?

**Then I'll:**
1. Fix the specific issue
2. Set up SSH keys if desired
3. Test all aliases work smoothly
4. Update profile to show clean load

---

**Note:** Your PowerShell profile is clean and should NEVER prompt for password during load. If it does, we need to identify what external process (Git, OneDrive, VS Code extension) is causing it.
