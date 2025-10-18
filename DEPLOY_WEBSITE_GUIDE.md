# Website Deployment Guide - Enterprise Scanner

## Current Status
- ✅ Test page deployed and working
- ⏳ Full website ready for deployment (21 HTML files + CSS/JS)
- 📦 Archive created: `website-full.tar.gz` (0.15 MB)

---

## Method 1: GitHub Repository (RECOMMENDED) ⭐

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `enterprisescanner-website`
3. Set to **Public** (for easy wget access)
4. Click "Create repository"

### Step 2: Push Website Files
```powershell
# On Windows:
cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace

# Initialize git (if not already done)
git init
git add website/
git commit -m "Enterprise Scanner production website"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/enterprisescanner-website.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Server
```bash
# On DigitalOcean server:
cd /opt/enterprisescanner
rm -rf website-temp
git clone https://github.com/YOUR_USERNAME/enterprisescanner-website.git website-temp
rm -rf website/*
cp -r website-temp/website/* website/
rm -rf website-temp
ls -lah website/
cd docker
docker-compose -f docker-compose.prod.yml restart nginx
sleep 2
curl http://localhost | head -20
```

---

## Method 2: DigitalOcean Spaces (Alternative)

### Step 1: Upload to Spaces
1. Go to DigitalOcean → Spaces
2. Create a Space (if needed)
3. Upload `website-full.tar.gz`
4. Make file public
5. Get public URL

### Step 2: Download on Server
```bash
cd /opt/enterprisescanner/website
wget https://your-space.nyc3.digitaloceanspaces.com/website-full.tar.gz
tar -xzf website-full.tar.gz
ls -lah
cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## Method 3: Manual File Creation (For Small Updates)

### Create Individual Files
```bash
# On server - example for one file:
cd /opt/enterprisescanner/website

cat > analytics-dashboard.html << 'HTMLEOF'
[PASTE HTML CONTENT HERE]
HTMLEOF

# Repeat for each file
```

---

## Method 4: SCP (When on Same Network)

```powershell
# From Windows (requires same network/VPN):
scp -r C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website\* root@134.199.147.45:/opt/enterprisescanner/website/
```

---

## Verification Steps

After deployment, verify:

```bash
# Check files
ls -lah /opt/enterprisescanner/website/
ls -lah /opt/enterprisescanner/website/css/
ls -lah /opt/enterprisescanner/website/js/

# Test homepage
curl http://localhost | grep -i "enterprise scanner"

# Test from browser
# Visit: http://134.199.147.45
```

---

## Expected Website Structure on Server

```
/opt/enterprisescanner/website/
├── index.html
├── analytics-dashboard.html
├── api-documentation.html
├── api-security.html
├── client-onboarding.html
├── crm-dashboard.html
├── email-dashboard.html
├── enterprise-chat-demo.html
├── enterprise_chat_widget.html
├── partner-portal.html
├── pdf-reports.html
├── performance-monitoring.html
├── security-assessment.html
├── security-compliance.html
├── threat-intelligence.html
├── trial-management.html
├── user-management.html
├── alerts-dashboard.html
├── css/
│   ├── analytics-dashboard.css
│   ├── api-documentation.css
│   ├── api-security.css
│   ├── crm-dashboard.css
│   ├── enterprise-chat.css
│   ├── partner-portal.css
│   ├── security-assessment.css
│   ├── threat-intelligence.css
│   └── user-management.css
└── js/
    ├── analytics-dashboard.js
    ├── api-documentation.js
    ├── api-security.js
    ├── crm-dashboard.js
    ├── enterprise-chat.js
    ├── partner-portal.js
    ├── pdf-reports.js
    ├── security-assessment.js
    ├── threat-intelligence.js
    └── user-management.js
```

---

## Quick Test Commands

```bash
# On server:
cd /opt/enterprisescanner

# Count files
find website -type f | wc -l
# Expected: 40 files (21 HTML + 9 CSS + 10 JS)

# Check file sizes
du -sh website/
du -sh website/css/
du -sh website/js/

# Restart nginx
cd docker
docker-compose -f docker-compose.prod.yml restart nginx

# Test all pages
for page in website/*.html; do
  echo "Testing: $(basename $page)"
  curl -I http://localhost/$(basename $page) | head -1
done
```

---

## Troubleshooting

### Files Not Showing
```bash
# Check permissions
ls -la /opt/enterprisescanner/website/
chmod -R 755 /opt/enterprisescanner/website/

# Check nginx can see them
docker exec enterprisescanner_nginx ls -la /usr/share/nginx/html/
```

### 404 Errors
```bash
# Check nginx logs
docker logs enterprisescanner_nginx --tail 50

# Verify file exists
ls -la /opt/enterprisescanner/website/[filename]
```

### CSS/JS Not Loading
```bash
# Check MIME types in nginx
docker exec enterprisescanner_nginx cat /etc/nginx/mime.types | grep -E "css|js"

# Test directly
curl http://localhost/css/analytics-dashboard.css | head -10
curl http://localhost/js/enterprise-chat.js | head -10
```

---

## Which Method Should You Use?

- ✅ **GitHub** - Best for version control, easy updates, most reliable
- ⚠️ **DigitalOcean Spaces** - Good if you already use Spaces
- ❌ **SCP** - Network issues prevent this currently
- ❌ **Manual** - Too many files (40 total)

**Recommendation: Use GitHub (Method 1)**

---

## Next Steps After Deployment

1. ✅ Upload full website files
2. 🔒 Configure SSL certificates
3. 🌐 Point domain to server
4. 🚀 Deploy Python microservices
5. 📊 Set up monitoring

---

**Created:** October 16, 2025  
**Status:** Ready for deployment
