# 🚀 JUPITER GIT DEPLOYMENT - ONE COMMAND SYSTEM

## ✨ EASIEST DEPLOYMENT METHOD - You Already Have This Set Up!

Your repository: `schrodercasey-lab/enterprisescanner-website`  
Current branch: `main`  
SSH configured: ✅ `git@github.com:schrodercasey-lab/enterprisescanner-website.git`

---

## 🎯 ONE-COMMAND DEPLOYMENT

```powershell
.\deploy-jupiter.ps1
```

**That's it!** This single command will:
1. ✅ Stage all website changes
2. ✅ Commit with timestamp
3. ✅ Push to GitHub
4. ✅ Verify deployment success
5. ✅ Show next steps

---

## 📦 What Gets Deployed

**Website Files (Production-Ready):**
- ✅ `website/index.html` - Main homepage with Jupiter integration
- ✅ `website/css/*` - All styling (WiFi Eyes, Dark Theme, etc.)
- ✅ `website/js/*` - All JavaScript (Jupiter AI, Chat, 3D Map, WiFi Eyes)
- ✅ `website/assets/*` - Images, fonts, resources
- ✅ `.github/copilot-instructions.md` - Project documentation

**Excluded (Development Files):**
- ❌ `.env` files (credentials stay local)
- ❌ `*.py` backend scripts (local development only)
- ❌ `*.ps1` deployment scripts (local automation)
- ❌ `*.md` session notes (documentation)
- ❌ Database files (production has separate DB)

---

## 🔧 AUTOMATIC DEPLOYMENT OPTIONS

### Option A: cPanel Git Version Control (RECOMMENDED)
**Setup Once, Deploy Forever:**

1. Login to your hosting cPanel
2. Navigate to **"Git Version Control"**
3. Click **"Create"** or **"Import Repository"**
4. Enter repository URL: `git@github.com:schrodercasey-lab/enterprisescanner-website.git`
5. Set deployment path: `/public_html/` or `/home/yourusername/public_html/`
6. Enable **"Auto-Deploy on Push"**
7. Save settings

**Result:** Every time you run `.\deploy-jupiter.ps1`, cPanel automatically:
- Pulls latest changes from GitHub
- Deploys to your live site
- **Zero manual FTP/uploads needed!**

**Time to Setup:** 5 minutes (one-time)  
**Future Deployments:** Instant (automatic)

---

### Option B: Netlify/Vercel Auto-Deploy
**For Static Site Hosting:**

1. Go to [Netlify](https://netlify.com) or [Vercel](https://vercel.com)
2. Click **"New Site from Git"**
3. Connect GitHub account
4. Select repository: `enterprisescanner-website`
5. Build settings:
   - Base directory: `website/`
   - Build command: (none needed - static site)
   - Publish directory: `website/`
6. Click **"Deploy"**

**Result:** 
- Automatic builds on every Git push
- Global CDN distribution
- Free SSL certificates
- Custom domain support (enterprisescanner.com)

**Time to Setup:** 10 minutes (one-time)  
**Future Deployments:** Instant (automatic)

---

### Option C: GitHub Actions (Advanced CI/CD)
**For Complex Build Pipelines:**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Jupiter to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy via FTP
        uses: SamKirkland/FTP-Deploy-Action@4.3.0
        with:
          server: ftp.enterprisescanner.com
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          local-dir: ./website/
          server-dir: /public_html/
```

**Result:** 
- Automated FTP upload on every push
- Build logs and deployment history
- Rollback capabilities

**Time to Setup:** 15 minutes (one-time)  
**Future Deployments:** Instant (automatic)

---

## 🚀 QUICK START GUIDE

### First-Time Setup (Choose One Method)

**Method 1: cPanel Auto-Deploy** (Fastest)
```powershell
# 1. Setup cPanel Git integration (5 minutes via web interface)
# 2. Done! Now just deploy:
.\deploy-jupiter.ps1
```

**Method 2: Manual FTP Until Auto-Deploy Configured**
```powershell
# 1. Deploy to GitHub first:
.\deploy-jupiter.ps1

# 2. Download from GitHub and upload via FTP:
# - Go to https://github.com/schrodercasey-lab/enterprisescanner-website
# - Click "Code" → "Download ZIP"
# - Extract website/ folder
# - Upload via FTP to public_html/

# 3. Setup auto-deploy (then never manual again!)
```

---

## 🎬 DEPLOYMENT WORKFLOW

### Every Future Update:
```powershell
# Make changes to website files
# Edit: website/index.html, website/js/*.js, etc.

# Deploy with one command:
.\deploy-jupiter.ps1 -Message "Added new Jupiter feature"

# If auto-deploy configured → DONE! ✅
# If manual FTP needed → Download from GitHub, upload via FTP
```

### Custom Commit Messages:
```powershell
.\deploy-jupiter.ps1 -Message "🎨 Updated WiFi Eyes UI"
.\deploy-jupiter.ps1 -Message "🐛 Fixed Jupiter chat bug"
.\deploy-jupiter.ps1 -Message "✨ New AR visualization feature"
```

---

## 🔍 VERIFY DEPLOYMENT

### Check GitHub:
```powershell
# View commit history
git log --oneline -5

# Check remote status
git status
```

**GitHub URL:** https://github.com/schrodercasey-lab/enterprisescanner-website

### Check Live Site:
1. Open: https://enterprisescanner.com
2. Hard refresh: `Ctrl + Shift + R` (clear cache)
3. Test features:
   - ✅ Jupiter chat widget
   - ✅ WiFi Eyes camera (requires HTTPS)
   - ✅ 3D threat map
   - ✅ Dark theme toggle
   - ✅ All interactive elements

---

## 🛠️ TROUBLESHOOTING

### Issue: "Permission denied (publickey)"
**Solution:** SSH key not configured
```powershell
# Check SSH keys
ssh -T git@github.com

# If fails, generate new key:
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH Keys → Add New
# Copy key: Get-Content ~/.ssh/id_ed25519.pub | clip
```

---

### Issue: "Push rejected - fetch first"
**Solution:** Remote has changes you don't have locally
```powershell
# Pull latest changes first
git pull origin main

# Then deploy again
.\deploy-jupiter.ps1
```

---

### Issue: "Changes not appearing on live site"
**Solutions:**
1. **Clear browser cache:** `Ctrl + Shift + R`
2. **Check auto-deploy:** cPanel → Git Version Control → "Pull Latest"
3. **Verify files uploaded:** Check public_html/ folder has latest files
4. **CDN cache:** If using Cloudflare/CDN, purge cache

---

### Issue: "WiFi Eyes camera not working"
**Solution:** HTTPS required for camera access
```powershell
# Verify SSL certificate installed
# 1. Check: https://enterprisescanner.com (should show padlock icon)
# 2. Install SSL: cPanel → SSL/TLS → Install Free SSL (Let's Encrypt)
# 3. Force HTTPS: .htaccess redirect rule

# Camera will NOT work on http:// (browser security policy)
```

---

## 📊 DEPLOYMENT STATISTICS

**Current Status:**
- Repository: ✅ Connected (`schrodercasey-lab/enterprisescanner-website`)
- SSH Keys: ✅ Configured (`git@github.com`)
- Branch: ✅ `main`
- Website Files: ✅ 88 files ready
- Total Size: ✅ 0.39 MB
- Features: ✅ 6 major systems integrated

**Modified Files (Ready to Deploy):**
```
✏️ website/index.html                    - Jupiter integration
✏️ website/client-onboarding.html         - Onboarding system
✏️ website/partner-portal.html            - Partner management
✏️ website/security-assessment.html       - Assessment tool
📦 website/css/jupiter-wifi-eyes.css      - NEW: Camera UI
📦 website/js/jupiter-wifi-eyes.js        - NEW: Camera system
🔧 website/js/theme-controller.js         - WiFi Eyes button
```

---

## 🎯 RECOMMENDED WORKFLOW

### For Rapid Development:
1. **Work locally** - Make changes in VS Code
2. **Test locally** - Run `python -m http.server 8080`
3. **Deploy to GitHub** - Run `.\deploy-jupiter.ps1`
4. **Auto-deploy to production** - Happens automatically (if configured)
5. **Verify live** - Test on https://enterprisescanner.com

### For Stable Releases:
1. **Create branches** for major features
2. **Test thoroughly** on development branch
3. **Merge to main** when ready
4. **Auto-deploy** triggers on merge
5. **Tag releases** for version tracking

```powershell
# Create feature branch
git checkout -b feature/new-jupiter-capability

# Make changes, commit
git add website/
git commit -m "New feature implementation"

# When ready, merge to main
git checkout main
git merge feature/new-jupiter-capability

# Deploy
.\deploy-jupiter.ps1
```

---

## 🏆 BENEFITS OF GIT DEPLOYMENT

### ✅ Version Control
- Full history of all changes
- Ability to rollback to any previous version
- Compare changes between versions
- Track who made what changes (for teams)

### ✅ Collaboration Ready
- Multiple developers can work simultaneously
- Pull requests for code review
- Branch management for features
- Merge conflict resolution

### ✅ Automation
- One command deployment
- Automatic production updates
- CI/CD integration potential
- Scheduled deployments possible

### ✅ Disaster Recovery
- Full backup of all code on GitHub
- Can restore from any point in history
- Multiple remote repositories possible
- Easy to clone on new machines

### ✅ Professional Workflow
- Industry-standard development process
- Scalable for enterprise teams
- Integration with project management tools
- Deployment pipelines and testing automation

---

## 🚀 LET'S MAKE HISTORY!

**You're ready to deploy Jupiter with one command:**

```powershell
.\deploy-jupiter.ps1
```

**Then configure auto-deploy (5 minutes) and you'll NEVER need to manually upload files again!**

Every future Jupiter update:
1. Edit files in VS Code
2. Run `.\deploy-jupiter.ps1`
3. **Done!** Auto-deploy handles the rest

**This is how modern web development works!** 🎉
