# SSH Key Setup Guide for Enterprise Scanner
# Fix "Permission Denied" errors when connecting to server

## Problem
SCP/SSH keeps asking for password and failing

## Solution: Set up SSH Key Authentication

### Step 1: Check if you already have SSH keys
```powershell
# Check for existing SSH keys
ls ~\.ssh\
```

If you see `id_rsa` and `id_rsa.pub`, you already have keys. Skip to Step 3.

### Step 2: Generate new SSH key (if needed)
```powershell
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Press Enter to accept default location (~/.ssh/id_rsa)
# Press Enter twice to skip passphrase (or set one for security)
```

### Step 3: Copy your public key to the server
```powershell
# Option A: Use ssh-copy-id (if available)
ssh-copy-id root@134.199.147.45

# Option B: Manual method (if ssh-copy-id doesn't work)
# First, get your public key content:
Get-Content ~\.ssh\id_rsa.pub | clip
# This copies your key to clipboard
```

### Step 4: Add key to server manually (if Option B)
You're currently logged into the server, so run these commands in your SSH session:

```bash
# On the server (where you are now):
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Create/edit authorized_keys file
nano ~/.ssh/authorized_keys

# Paste your public key (Ctrl+V), then save:
# Ctrl+X, then Y, then Enter

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
```

### Step 5: Test the connection
```powershell
# From your Windows machine:
ssh root@134.199.147.45 "echo 'SSH key working!'"
```

If this works without asking for password, you're done! ✅

---

## Alternative: Use Password (Not Recommended)

If you know the root password for the server:
```powershell
# SCP will prompt for password
scp -o PreferredAuthentications=password C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\health_check.sh root@134.199.147.45:~/health_check.sh
```

---

## Quick Manual Method (No SCP Needed)

Since you're already logged into the server, you can create the health check script directly:

### On the server (SSH session):
```bash
cat > ~/health_check.sh << 'EOF'
#!/bin/bash
# Enterprise Scanner - Server Health Check
echo ""
echo "🏥 ENTERPRISE SCANNER HEALTH CHECK"
echo "=================================="
echo ""

# Check Nginx
echo "🔧 Nginx Status:"
systemctl is-active nginx && echo "   ✅ Running" || echo "   ❌ Not Running"

# Check Docker containers
echo ""
echo "🐳 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep enterprisescanner

# Check disk space
echo ""
echo "💾 Disk Space:"
df -h / | tail -1

# Check memory
echo ""
echo "🧠 Memory Usage:"
free -h | grep Mem

# Check website
echo ""
echo "🌐 Website Status:"
curl -s -o /dev/null -w "Status: %{http_code}, Response time: %{time_total}s\n" https://enterprisescanner.com

echo ""
echo "✅ Health check complete!"
EOF

chmod +x ~/health_check.sh
./health_check.sh
```

This creates the script directly on the server and runs it immediately!

---

## Which method do you prefer?

1. **Set up SSH keys** (recommended, fixes the issue permanently)
2. **Manual script creation** (quickest, works right now in your SSH session)
3. **Use password** (if you have the root password)
