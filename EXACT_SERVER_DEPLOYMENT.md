# 🚀 JUPITER DEPLOYMENT - EXACT COMMANDS FOR YOUR SERVER

**Current Status:**
- ✅ SSH connected to: enterprisescanner-prod-01
- ✅ In directory: /opt/enterprisescanner/website
- ⚠️ Git not initialized (normal for first time)

---

## 🎯 FASTEST DEPLOYMENT - COPY ALL THESE COMMANDS

**IMPORTANT:** Your repository has a `website/` subfolder. We need to handle this correctly!

### METHOD 1: Simple Clone & Replace (RECOMMENDED - 30 seconds)

```bash
# Go to parent directory
cd /opt/enterprisescanner/

# Backup current website
mv website website-backup-$(date +%Y%m%d)

# Clone Jupiter from GitHub
git clone https://github.com/schrodercasey-lab/enterprisescanner-website.git temp-jupiter

# Move website files to correct location
mv temp-jupiter/website website

# Cleanup
rm -rf temp-jupiter

# Verify Jupiter files
ls -lh website/js/jupiter-wifi-eyes.js

# Set permissions
chown -R www-data:www-data website/
# OR if using different web user:
# chown -R nginx:nginx website/

# Reload web server
systemctl reload nginx

# Done! 🎉
```

---

### METHOD 2: Initialize Git in Current Directory (Alternative)

```bash
# Make sure you're in the right directory
cd /opt/enterprisescanner/website

# Initialize Git
git init

# Add GitHub as remote
git remote add origin https://github.com/schrodercasey-lab/enterprisescanner-website.git

# Fetch all branches
git fetch origin

# Checkout main branch
git checkout -b main origin/main

# This will give error about overwriting files - use force:
git reset --hard origin/main

# Verify Jupiter files
ls -lh js/jupiter-wifi-eyes.js

# Set permissions
chown -R www-data:www-data .

# Reload web server
systemctl reload nginx
```

---

## ⚡ QUICK START - PASTE THIS ENTIRE BLOCK

**This is the complete deployment in one copy-paste:**

```bash
cd /opt/enterprisescanner/ && \
mv website website-backup-$(date +%Y%m%d) && \
git clone https://github.com/schrodercasey-lab/enterprisescanner-website.git temp-jupiter && \
mv temp-jupiter/website website && \
rm -rf temp-jupiter && \
ls -lh website/js/jupiter-wifi-eyes.js && \
chown -R www-data:www-data website/ && \
systemctl reload nginx && \
echo "" && \
echo "🎉 JUPITER IS DEPLOYED! 🎉" && \
echo "Visit: https://enterprisescanner.com"
```

---

## 🔍 VERIFICATION COMMANDS

**After deployment, verify Jupiter is live:**

```bash
# Check Jupiter files exist
ls -lh /opt/enterprisescanner/website/js/jupiter-wifi-eyes.js
ls -lh /opt/enterprisescanner/website/css/jupiter-wifi-eyes.css
ls -lh /opt/enterprisescanner/website/js/theme-controller.js

# Check file dates (should be today)
ls -lt /opt/enterprisescanner/website/js/ | head

# Test website response
curl -I https://enterprisescanner.com

# Check for Jupiter files in response
curl -s https://enterprisescanner.com | grep -i "jupiter"
```

---

## 🌐 TEST IN BROWSER

1. Open: **https://enterprisescanner.com**
2. Press: **Ctrl + Shift + R** (hard refresh to clear cache)
3. Look for:
   - 📹 WiFi Eyes button (camera icon)
   - 💬 Jupiter chat widget (bottom right)
   - 🎨 Dark theme toggle
   - No console errors (F12 to check)

4. Test WiFi Eyes:
   - Click camera icon
   - Browser prompts for permission
   - Allow camera access
   - Camera feed should display! ✨

---

## 🐛 TROUBLESHOOTING

### Issue: "Permission denied" when cloning

**Solution: Use HTTPS (already in commands above)**
- We're using `https://github.com/...` which works without SSH keys

---

### Issue: Files don't appear on website

**Check web server configuration:**
```bash
# Find nginx config
cat /etc/nginx/sites-enabled/default | grep root

# Verify it points to correct directory
# Should be: /opt/enterprisescanner/website
```

**If wrong directory, update nginx:**
```bash
nano /etc/nginx/sites-enabled/default
# Change root to: /opt/enterprisescanner/website
# Save and exit (Ctrl+X, Y, Enter)
systemctl reload nginx
```

---

### Issue: Old files still showing

**Clear browser cache:**
- Hard refresh: Ctrl + Shift + R
- Or clear all cache in browser settings

**Check file permissions:**
```bash
ls -la /opt/enterprisescanner/website/
# Should show www-data or nginx as owner

# Fix if needed:
chown -R www-data:www-data /opt/enterprisescanner/website/
```

---

## 📊 WHAT GETS DEPLOYED

**Jupiter Features (56 files, 31,748 lines):**
- ✨ WiFi Eyes camera system (1,350 lines NEW)
- 🧠 Jupiter AI chat widget
- 🗺️ 3D threat visualization map
- 🎨 Dark AI cyberpunk theme
- 🥽 AR/VR capabilities
- 📱 Mobile responsive design

**Key Files:**
- `js/jupiter-wifi-eyes.js` (700 lines)
- `css/jupiter-wifi-eyes.css` (600 lines)
- `js/jupiter-ai-chat.js`
- `js/3d-threat-map.js`
- `css/dark-ai-theme.css`
- Plus 51 more files!

---

## 🎯 RECOMMENDED: USE THE QUICK START BLOCK

**The safest, fastest method is the complete one-liner above.**

It will:
1. ✅ Backup your current website
2. ✅ Clone Jupiter from GitHub
3. ✅ Move files to correct location
4. ✅ Set proper permissions
5. ✅ Reload nginx
6. ✅ Verify deployment
7. ✅ Print success message

**Just copy the entire Quick Start block and paste into SSH!**

---

## 🎊 AFTER SUCCESSFUL DEPLOYMENT

**You'll see:**
```
🎉 JUPITER IS DEPLOYED! 🎉
Visit: https://enterprisescanner.com
```

**Then:**
1. Open https://enterprisescanner.com in browser
2. Test all Jupiter features
3. Come back to VS Code
4. Type: **"JUPITER IS LIVE!"** 🚀

---

## 💡 IMPORTANT NOTE

Your GitHub repository structure is:
```
enterprisescanner-website/
├── website/           ← Your actual website files are HERE
│   ├── index.html
│   ├── js/
│   ├── css/
│   └── ...
└── (other files like .md docs)
```

**That's why we clone to `temp-jupiter` and then move `temp-jupiter/website/` to the final location!**

---

**COPY THE QUICK START BLOCK ABOVE AND PASTE INTO YOUR SSH TERMINAL NOW! 🚀**
