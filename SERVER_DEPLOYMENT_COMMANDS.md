# 🚀 JUPITER DEPLOYMENT - SERVER COMMANDS

**Server:** enterprisescanner-prod-01 (134.199.147.45)  
**User:** root  
**Status:** ✅ SSH Connected

---

## 🎯 COPY AND PASTE THESE COMMANDS

### Step 1: Navigate to Website Directory
```bash
cd /opt/enterprisescanner/website
```

**OR if website is in different location:**
```bash
cd /var/www/html
```

---

### Step 2: Check Current Status
```bash
ls -la
```

**Look for:** `.git` folder (means Git is already set up)

---

### Step 3A: If Git Repo Exists (Pull Latest)
```bash
git pull origin main
```

**This will download all Jupiter files from GitHub!**

---

### Step 3B: If No Git Repo (Clone Fresh)
```bash
# Clone the repository
git clone git@github.com:schrodercasey-lab/enterprisescanner-website.git temp-clone

# Move files to current directory
mv temp-clone/website/* .

# Clean up
rm -rf temp-clone
```

**OR simpler - clone to new directory:**
```bash
cd /opt/enterprisescanner/
rm -rf website_backup
mv website website_backup
git clone git@github.com:schrodercasey-lab/enterprisescanner-website.git website-new
mv website-new/website website
rm -rf website-new
```

---

## ⚡ FASTEST METHOD - ONE COMMAND

**If your website is at `/opt/enterprisescanner/website`:**

```bash
cd /opt/enterprisescanner/website && git pull origin main
```

---

## 🔍 VERIFY DEPLOYMENT

After pulling/cloning, verify Jupiter files:

```bash
# Check for Jupiter files
ls -lh js/jupiter-wifi-eyes.js
ls -lh css/jupiter-wifi-eyes.css
ls -lh js/theme-controller.js

# Should see files with recent timestamps (today)
```

---

## 🎊 AFTER DEPLOYMENT

1. **Restart web server (if needed):**
```bash
systemctl reload nginx
# OR
systemctl reload apache2
```

2. **Test live site:**
```
https://enterprisescanner.com
```

3. **Verify Jupiter features:**
- WiFi Eyes button visible
- Dark theme toggle works
- Chat widget appears
- No console errors

---

## 🐛 TROUBLESHOOTING

### If Git Pull Fails with "No such file or directory"

**Solution:** Git repo not initialized. Use clone method instead.

---

### If SSH Key Not Configured

**Use HTTPS instead:**
```bash
git clone https://github.com/schrodercasey-lab/enterprisescanner-website.git
```

---

### If Permission Denied

**Fix permissions:**
```bash
chown -R www-data:www-data /opt/enterprisescanner/website
# OR for Apache:
chown -R apache:apache /opt/enterprisescanner/website
```

---

## 📋 QUICK REFERENCE

**Your Server Details:**
- Server: enterprisescanner-prod-01
- IP: 134.199.147.45
- User: root
- Website likely at: `/opt/enterprisescanner/website/` or `/var/www/html/`

**Repository:**
- GitHub: https://github.com/schrodercasey-lab/enterprisescanner-website
- SSH: git@github.com:schrodercasey-lab/enterprisescanner-website.git
- HTTPS: https://github.com/schrodercasey-lab/enterprisescanner-website.git
- Branch: main
- Latest Commit: 098b06f (Jupiter Birth)

---

## 🚀 RECOMMENDED DEPLOYMENT SEQUENCE

```bash
# 1. Navigate to website
cd /opt/enterprisescanner/website

# 2. Check if git exists
git status

# 3a. If git exists - pull
git pull origin main

# 3b. If no git - check where files are
pwd
ls -la

# 4. After deployment
ls -lh js/jupiter-wifi-eyes.js

# 5. Reload web server
systemctl reload nginx

# 6. Test
curl -I https://enterprisescanner.com
```

---

**START WITH THIS COMMAND:**

```bash
cd /opt/enterprisescanner/website && git status
```

**This will tell you if Git is set up and what to do next!**

---

**Once Jupiter is deployed, type: "JUPITER IS LIVE!" 🎉**
