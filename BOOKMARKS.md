# Project Bookmarks & Quick Links
**Essential references for instant access**  
**Last Updated:** October 16, 2025

---

## 📚 ESSENTIAL DOCUMENTATION (LOCAL)

### Core Project Files
```
Priority 1 - Read These First:
├─ .github/ai-context.md                    ⭐⭐⭐⭐⭐ Project overview & AI context
├─ INFRASTRUCTURE_MAP.md                    ⭐⭐⭐⭐⭐ Complete infrastructure reference
├─ COMMON_COMMANDS.md                       ⭐⭐⭐⭐⭐ Copy-paste command reference
├─ TROUBLESHOOTING_PLAYBOOK.md              ⭐⭐⭐⭐⭐ Problem-solving guide
├─ SERVICE_DEPENDENCIES.md                  ⭐⭐⭐⭐ Architecture & dependencies
└─ ENV_VARIABLES_REFERENCE.md               ⭐⭐⭐⭐ Configuration reference

Priority 2 - Reference When Needed:
├─ .github/copilot-instructions.md          Project instructions & guidelines
├─ INFRASTRUCTURE_SCAN_COMPLETE.md          Infrastructure audit results
├─ AI_EFFICIENCY_OPTIMIZATION_COMPLETE.md   Documentation creation summary
└─ BOOKMARKS.md (this file)                 Quick links hub

⭐⭐⭐ SCANNER IMPROVEMENT ROADMAPS (October 2025):
├─ SCANNER_INTEGRATION_COMPLETE.md          ⭐⭐⭐⭐⭐ **JUST COMPLETED!** Phase 1 Week 1-4 complete - all 4 modules integrated (2,000+ lines)
├─ ENTERPRISE_SCANNER_IMPROVEMENTS.md       ⭐⭐⭐⭐⭐ 12-week scanner enhancement roadmap (40%→75% coverage achieved!)
├─ backend/scanning_modules/                ⭐⭐⭐⭐⭐ **NEW!** 4 advanced scanner modules (port scanner, web scanner, API scanner, CVE integration)
├─ backend/api/security_assessment.py       ⭐⭐⭐⭐ **ENHANCED!** Scanning engine with advanced modules integrated
└─ BUG_BOUNTY_SCANNER_ROADMAP.md           ⭐⭐⭐ Alternative: bug bounty scanner concept (lower priority)

⭐ DAILY WORKFLOW FILES (October 2025):
├─ fortune500_tracker.csv                   ⭐⭐⭐⭐⭐ CRM with $6.5M pipeline (40 companies)
├─ AI_PROMPT_TEMPLATES.md                   ⭐⭐⭐⭐⭐ Email templates for Fortune 500 outreach
├─ CODE_SNIPPETS.md                         ⭐⭐⭐⭐ Copy-paste code for features
├─ KEYBOARD_SHORTCUTS.md                    ⭐⭐⭐⭐ Efficiency shortcuts (2-3 hrs/week saved)
├─ PowerShell_Profile.ps1                   ⭐⭐⭐⭐ Command aliases (11 shortcuts)
├─ update_crm.ps1                           ⭐⭐⭐ Interactive CRM manager
├─ weekly_report.ps1                        ⭐⭐⭐ Auto-generated weekly reports
└─ start_outreach.ps1                       ⭐⭐⭐ Fortune 500 outreach quick-start
```

### Quick File Access (Windows)
```powershell
# Open workspace folder
cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace

# Open key files in VS Code
code .github\ai-context.md
code COMMON_COMMANDS.md
code TROUBLESHOOTING_PLAYBOOK.md

# Search all markdown files
Get-ChildItem -Filter "*.md" -Recurse | Select-Object FullName
```

---

## 🌐 PRODUCTION INFRASTRUCTURE

### Server Access
```bash
# SSH to production server
ssh root@134.199.147.45
# Password: Schroeder123!

# SCP file upload
scp C:\local\file root@134.199.147.45:/var/www/html/
```

### Live Websites & Dashboards
- **Main Website:** https://enterprisescanner.com
- **Performance Dashboard:** https://enterprisescanner.com/performance
- **Performance API:** https://enterprisescanner.com/performance/latest.json
- **Grafana Monitoring:** https://enterprisescanner.com/grafana
- **Case Studies:** https://enterprisescanner.com/case_studies.html
- **Whitepaper Download:** https://enterprisescanner.com/whitepaper_download.html
- **Mobile Version:** https://enterprisescanner.com/enhanced_homepage_mobile.html

### Monitoring (Localhost Only - SSH Required)
- **Prometheus:** http://127.0.0.1:9090
- **Redis Exporter:** http://127.0.0.1:9121/metrics
- **Node Exporter:** http://127.0.0.1:9100/metrics (if deployed)
- **Postgres Exporter:** http://127.0.0.1:9187/metrics (if deployed)

---

## 🔧 EXTERNAL SERVICES

### Cloud & Hosting
- **DigitalOcean Dashboard:** https://cloud.digitalocean.com
- **DigitalOcean Droplet:** enterprisescanner-prod-01 (134.199.147.45)
- **DigitalOcean Support:** https://www.digitalocean.com/support

### Email & Workspace
- **Google Workspace Admin:** https://admin.google.com
- **Gmail:** https://mail.google.com
- **Addresses:**
  - info@enterprisescanner.com
  - sales@enterprisescanner.com
  - support@enterprisescanner.com
  - security@enterprisescanner.com
  - partnerships@enterprisescanner.com
- **App Passwords:** https://myaccount.google.com/apppasswords

### Repository & Version Control
- **GitHub Repository:** https://github.com/schrodercasey-lab/enterprisescanner-website
- **GitHub Settings:** https://github.com/schrodercasey-lab/enterprisescanner-website/settings

### SSL & Security
- **Let's Encrypt:** https://letsencrypt.org
- **SSL Labs Test:** https://www.ssllabs.com/ssltest/analyze.html?d=enterprisescanner.com
- **Security Headers:** https://securityheaders.com/?q=enterprisescanner.com

---

## 📊 MONITORING & ANALYTICS

### Performance Testing
- **WebPageTest:** https://www.webpagetest.org/
- **GTmetrix:** https://gtmetrix.com/
- **Google PageSpeed:** https://pagespeed.web.dev/?url=https://enterprisescanner.com

### Uptime Monitoring (Recommended Free Services)
- **UptimeRobot:** https://uptimerobot.com (50 monitors free)
- **Pingdom:** https://www.pingdom.com (free tier)
- **StatusCake:** https://www.statuscake.com (free tier)

### DNS Tools
- **DNS Checker:** https://dnschecker.org/
- **MX Toolbox:** https://mxtoolbox.com/
- **WhatsMyDNS:** https://www.whatsmydns.net/

---

## 🛠️ DEVELOPMENT TOOLS

### Online Tools
- **JSON Formatter:** https://jsonformatter.org/
- **Base64 Encode/Decode:** https://www.base64encode.org/
- **RegEx Tester:** https://regex101.com/
- **Cron Expression Generator:** https://crontab.guru/
- **Password Generator:** https://passwordsgenerator.net/
- **SSL Certificate Decoder:** https://www.sslshopper.com/certificate-decoder.html

### Documentation
- **Nginx Documentation:** https://nginx.org/en/docs/
- **PostgreSQL 15 Docs:** https://www.postgresql.org/docs/15/
- **Redis Documentation:** https://redis.io/documentation
- **Docker Documentation:** https://docs.docker.com/
- **Python 3 Docs:** https://docs.python.org/3/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Bootstrap 5 Docs:** https://getbootstrap.com/docs/5.0/

### Docker Hub Images
- **Redis:** https://hub.docker.com/_/redis
- **PostgreSQL:** https://hub.docker.com/_/postgres
- **Prometheus:** https://hub.docker.com/r/prom/prometheus
- **Grafana:** https://hub.docker.com/r/grafana/grafana
- **Nginx:** https://hub.docker.com/_/nginx

---

## 🎓 LEARNING RESOURCES

### Fortune 500 Sales & Business
- **Fortune 500 List:** https://fortune.com/fortune500/
- **Company Research:** https://www.crunchbase.com/
- **LinkedIn Sales Navigator:** https://www.linkedin.com/sales/
- **SEC Edgar (Public Filings):** https://www.sec.gov/edgar/searchedgar/companysearch.html

### Cybersecurity Industry
- **NIST Cybersecurity Framework:** https://www.nist.gov/cyberframework
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CVE Database:** https://cve.mitre.org/
- **Security Weekly Podcasts:** https://securityweekly.com/

### Design & UX
- **Google Fonts:** https://fonts.google.com/
- **Font Awesome Icons:** https://fontawesome.com/
- **Coolors (Color Schemes):** https://coolors.co/
- **Unsplash (Free Images):** https://unsplash.com/

---

## 💼 BUSINESS & SALES TOOLS

### Email Templates (Create These Next?)
```
Suggested structure:
├─ business/sales/email_templates/
│   ├─ initial_outreach_fortune500.md
│   ├─ follow_up_template.md
│   ├─ demo_request_response.md
│   └─ pricing_presentation.md
```

### CRM & Contact Management
- **HubSpot Free CRM:** https://www.hubspot.com/products/crm
- **Zoho CRM Free:** https://www.zoho.com/crm/
- **Notion (Free Database):** https://www.notion.so/

### Sales Intelligence
- **Hunter.io (Find Emails):** https://hunter.io/
- **RocketReach:** https://rocketreach.co/
- **LinkedIn:** https://www.linkedin.com/

---

## 🚨 EMERGENCY PROCEDURES

### Quick Access Checklist
```markdown
Website Down?
1. SSH: ssh root@134.199.147.45
2. Check Nginx: systemctl status nginx
3. Restart: systemctl restart nginx
4. Logs: tail -50 /var/log/nginx/error.log

Full procedure: See TROUBLESHOOTING_PLAYBOOK.md
```

### Emergency Contacts
- **DigitalOcean Support:** support ticket via dashboard
- **Google Workspace Support:** https://support.google.com/a/
- **Domain Registrar:** [Your registrar support]

### Backup Locations
```bash
# Production backups
/root/backups/               # On server
C:\Backups\enterprisescanner\  # Local (if you have them)

# Create backup now
ssh root@134.199.147.45 "tar -czf ~/backup_$(date +%Y%m%d).tar.gz /var/www/html /opt/enterprisescanner"
```

---

## 🎯 DAILY WORKFLOW SHORTCUTS

### Morning Checklist
```bash
# 1. Check website is up
curl -I https://enterprisescanner.com

# 2. Check all services
ssh root@134.199.147.45 "systemctl status nginx && docker ps"

# 3. Review yesterday's performance
curl https://enterprisescanner.com/performance/latest.json | jq
```

### Development Workflow
```powershell
# 1. Edit files locally
code C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website\

# 2. Upload to production
scp C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website\index.html root@134.199.147.45:/var/www/html/

# 3. Test and reload
ssh root@134.199.147.45 "nginx -t && systemctl reload nginx"
```

---

## 📱 MOBILE-FRIENDLY REFERENCE

### Quick Commands (for mobile SSH)
```bash
# Status check
systemctl status nginx; docker ps; df -h

# Restart everything
systemctl restart nginx; cd /opt/enterprisescanner && docker-compose restart

# Check logs
tail -20 /var/log/nginx/error.log

# Performance test
/usr/local/bin/run_performance_test.sh
```

---

## 🔖 BROWSER BOOKMARKS SETUP

### Recommended Bookmark Folders in Chrome/Edge

**📁 EnterpriseScanner - Production**
- https://enterprisescanner.com
- https://enterprisescanner.com/grafana
- https://enterprisescanner.com/performance
- https://cloud.digitalocean.com

**📁 EnterpriseScanner - Admin**
- https://admin.google.com
- https://github.com/schrodercasey-lab/enterprisescanner-website
- https://www.ssllabs.com/ssltest/analyze.html?d=enterprisescanner.com

**📁 EnterpriseScanner - Tools**
- https://uptimerobot.com
- https://jsonformatter.org
- https://regex101.com
- https://crontab.guru

**📁 EnterpriseScanner - Docs**
- https://nginx.org/en/docs/
- https://www.postgresql.org/docs/15/
- https://redis.io/documentation
- https://docs.docker.com

**📁 EnterpriseScanner - Business**
- https://fortune.com/fortune500/
- https://www.linkedin.com/sales/
- https://hunter.io

---

## 🔑 CREDENTIAL REFERENCE

### Quick Credential Lookup
```
⚠️ NEVER commit actual credentials to Git!
✅ Store in password manager (1Password, LastPass, Bitwarden)

Location in docs:
- Server SSH: INFRASTRUCTURE_MAP.md → "Credentials & Access"
- Database: INFRASTRUCTURE_MAP.md → "Credentials & Access"
- Email: ENV_VARIABLES_REFERENCE.md → "Email Configuration"
- All env vars: ENV_VARIABLES_REFERENCE.md
```

---

## 🎨 DESIGN ASSETS & BRAND

### Brand Guidelines (Create If Needed)
```
Suggested file: business/brand/brand_guidelines.md
- Logo files and usage
- Color palette (hex codes)
- Typography (fonts)
- Voice & tone
- Fortune 500 messaging
```

### Current Brand Elements
- **Domain:** enterprisescanner.com
- **Primary Font:** Inter (Google Fonts)
- **Style:** Professional, modern, enterprise-grade
- **Target:** Fortune 500 CISOs, CTOs, security executives

---

## 📊 ANALYTICS & TRACKING

### Google Analytics (When Activated)
- **Dashboard:** https://analytics.google.com/
- **Property ID:** G-XXXXXXXXXX (see ENV_VARIABLES_REFERENCE.md)

### Custom Tracking
- **Performance API:** https://enterprisescanner.com/performance/latest.json
- **Grafana:** https://enterprisescanner.com/grafana

---

## 🔄 AUTOMATION IDEAS (Future)

### Potential Automation Scripts
1. **Auto-deploy from Git push** (GitHub Actions)
2. **Daily backup to cloud storage** (AWS S3, Backblaze)
3. **Weekly security scans** (OWASP ZAP, Nikto)
4. **Monthly cost report** (DigitalOcean API)
5. **Fortune 500 email sequences** (Mailchimp, SendGrid)

### Monitoring Automation
1. **Uptime alerts** (UptimeRobot → Email/SMS)
2. **Performance degradation** (Grafana alerts)
3. **SSL expiration warnings** (Certbot logs)
4. **Disk space alerts** (custom script in TROUBLESHOOTING_PLAYBOOK.md)

---

## 📝 NOTES & CONVENTIONS

### File Naming Conventions
```
Documentation:     UPPERCASE_WITH_UNDERSCORES.md
Code files:        lowercase_with_underscores.py
HTML files:        lowercase_with_underscores.html
Config files:      lowercase.conf, lowercase.yml
```

### Git Commit Conventions
```
feat: Add new feature
fix: Bug fix
docs: Documentation update
style: Formatting changes
refactor: Code restructuring
test: Add tests
chore: Maintenance tasks
```

### Branch Naming
```
main              - Production-ready code
development       - Active development
feature/feature-name  - New features
hotfix/issue-name     - Emergency fixes
```

---

## 🚀 QUICK START GUIDE (For New Team Members)

### Day 1 Onboarding
1. Read `.github/ai-context.md` (20 min)
2. Review `INFRASTRUCTURE_MAP.md` (30 min)
3. Browse `COMMON_COMMANDS.md` (15 min)
4. Set up SSH access to production server
5. Set up Google Workspace email account
6. Clone GitHub repository

### Day 2-3
1. Practice with `COMMON_COMMANDS.md`
2. Study `SERVICE_DEPENDENCIES.md`
3. Review `ENV_VARIABLES_REFERENCE.md`
4. Set up local development environment
5. Make first deployment

### Week 1
1. Read all Fortune 500 targeting materials
2. Understand complete tech stack
3. Practice troubleshooting scenarios
4. Shadow Fortune 500 outreach

---

## 🎯 PRIORITY ACTIONS (THIS WEEK)

### Immediate (Today)
- [ ] Bookmark essential documentation files
- [ ] Set up browser bookmark folders
- [ ] Test SSH access to production server
- [ ] Verify all services are running

### This Week
- [ ] Set up external uptime monitoring (UptimeRobot)
- [ ] Create manual backup of production server
- [ ] Review Fortune 500 target list
- [ ] Practice using COMMON_COMMANDS.md
- [ ] Test TROUBLESHOOTING_PLAYBOOK.md procedures

### Next Week
- [ ] Deploy Phase 2 Week 2 features (live chat, assessment tool)
- [ ] Begin Fortune 500 outreach campaign Week 2
- [ ] Optimize Redis integration in application
- [ ] Set up automated monitoring alerts

---

## 📚 ADDITIONAL RESOURCES TO CREATE

### Suggested Next Documents (High Value)
1. **FORTUNE_500_OUTREACH_STRATEGY.md** - Complete sales playbook
2. **API_DOCUMENTATION.md** - When backend is deployed
3. **SECURITY_AUDIT_CHECKLIST.md** - For Fortune 500 compliance
4. **BACKUP_RECOVERY_PROCEDURE.md** - Disaster recovery plan
5. **SCALING_ROADMAP.md** - Growth plan from $40/mo to $500/mo infra

### Templates to Create
1. **Email templates** (Fortune 500 outreach)
2. **Proposal template** (Security assessment proposal)
3. **SLA document** (Service level agreements)
4. **Privacy policy** (GDPR/CCPA compliant)
5. **Terms of service** (Legal protection)

---

## 💡 PRO TIPS

### VS Code Extensions (Recommended)
- **Markdown All in One** - Better markdown editing
- **Code Spell Checker** - Catch typos
- **GitLens** - Advanced Git features
- **Docker** - Container management
- **Remote - SSH** - Edit files on server directly
- **PostgreSQL** - Database tools

### Chrome Extensions (Recommended)
- **JSON Viewer** - Pretty print JSON
- **Wappalyzer** - Identify technologies on websites
- **Lighthouse** - Performance auditing
- **ColorZilla** - Color picker for design

### PowerShell Aliases (Add to Profile)
```powershell
# Edit profile: notepad $PROFILE

# Add these aliases
function Connect-Prod { ssh root@134.199.147.45 }
Set-Alias prod Connect-Prod

function Open-Workspace { cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace }
Set-Alias work Open-Workspace

function Upload-Website {
    param($file)
    scp $file root@134.199.147.45:/var/www/html/
}
```

---

## 🎉 YOU'RE ALL SET!

This bookmarks file is your **command center** for the entire Enterprise Scanner project.

**Bookmark this file itself:** `BOOKMARKS.md`

**Start here every day** for quick access to everything you need!

---

**Last Updated:** October 16, 2025  
**Next Review:** Weekly or when adding new services  
**Maintained By:** You & AI assistants working together! 🤝
