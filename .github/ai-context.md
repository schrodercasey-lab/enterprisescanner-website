# AI Assistant Context - Enterprise Scanner
**Last Updated:** October 16, 2025  
**Purpose:** Quick reference for AI assistants working on this project

---

## 📋 PROJECT OVERVIEW

**Enterprise Scanner** is a premium cybersecurity vulnerability assessment platform targeting Fortune 500 companies. We provide automated security scanning, compliance monitoring, and executive-level reporting to help large enterprises identify and remediate security vulnerabilities before they become breaches.

**Live Platform:** https://enterprisescanner.com  
**Status:** Phase 2 Week 1 Complete, targeting $6.5M pipeline  
**Business Model:** Enterprise SaaS with annual contracts ($50K-250K/year)

---

## 🎯 CURRENT PRIORITIES (October 2025)

1. **Fortune 500 Outreach Campaign** - Week 1 in progress, targeting 20 companies
2. **Phase 2 Feature Development** - Case studies, mobile optimization, whitepaper system complete
3. **Infrastructure Optimization** - Redis caching, PgBouncer, Nginx compression deployed
4. **Database Integration** - PostgreSQL production deployment ready
5. **Business Development** - Professional email system, Google Workspace integration

---

## 🛠️ TECH STACK

### **Production Infrastructure**
- **Hosting:** DigitalOcean droplet (134.199.147.45)
- **OS:** Ubuntu 22.04.5 LTS
- **Web Server:** Nginx 1.18.0
- **Database:** PostgreSQL 15.14 (Docker)
- **Cache:** Redis 7.4.6 (Docker)
- **Connection Pooler:** PgBouncer 1.16.1
- **SSL:** Let's Encrypt (A+ rating)

### **Monitoring Stack**
- **Metrics:** Prometheus
- **Dashboards:** Grafana (https://enterprisescanner.com/grafana)
- **Exporters:** Redis, Node, Postgres
- **Performance:** Automated hourly testing

### **Frontend**
- **Languages:** HTML5, CSS3, JavaScript (ES6+)
- **Framework:** Bootstrap 5
- **CDN:** Cloudflare (cdnjs), Google Fonts, jsDelivr
- **Optimization:** Gzip compression (80%), browser caching

### **Backend (Ready, Not Yet Deployed)**
- **Language:** Python 3.x
- **Framework:** Flask/Django
- **ORM:** SQLAlchemy
- **API:** RESTful endpoints
- **Integration:** Redis helper, database repositories

### **Business Tools**
- **Email:** Google Workspace (5 addresses @ $30/month)
- **Repository:** GitHub (schrodercasey-lab/enterprisescanner-website)
- **Domain:** enterprisescanner.com
- **Analytics:** Google Analytics (prepared)

---

## 💰 BUDGET & CONSTRAINTS

### **Current Monthly Costs**
- DigitalOcean: $10/month
- Google Workspace: $30/month
- Domain: ~$1/month
- **Total: ~$40/month**

### **Scaling Budget (When Needed)**
- AWS Infrastructure: $200-500/month (>100 concurrent users)
- Azure Infrastructure: $250-550/month (Fortune 500 Azure requirements)

### **Constraints**
- 💡 Budget is flexible - costs evaluated case-by-case
- ✅ All new features must be DigitalOcean-compatible
- ✅ Prioritize free/open-source solutions when possible
- ✅ Focus on ROI and business value for paid services

---

## 🎨 DESIGN PHILOSOPHY

### **Brand Identity**
- **Target Audience:** Fortune 500 CISOs, CTOs, security executives
- **Tone:** Professional, authoritative, data-driven
- **Visual Style:** Modern, clean, enterprise-grade
- **Colors:** Blue (trust), white (clarity), gray (professionalism)

### **UX Principles**
- **Mobile-First:** All pages responsive (enhanced_homepage_mobile.html)
- **Performance:** <100ms response time goal
- **Accessibility:** WCAG 2.1 compliance
- **Conversion:** Clear CTAs, ROI calculators, social proof

---

## 🔒 SECURITY ARCHITECTURE

### **Core Principles**
- ✅ **Localhost-Only Services:** All backend services bound to 127.0.0.1
- ✅ **No Direct Exposure:** Only Nginx exposed publicly
- ✅ **Container Isolation:** 0.0.0.0 inside containers, 127.0.0.1 on host
- ✅ **SSL Everywhere:** Let's Encrypt with auto-renewal
- ✅ **Fail2ban Active:** Intrusion prevention enabled

### **Port Security**
```
Public:  443 (HTTPS via Nginx)
Private: 6379 (Redis), 5432 (PostgreSQL), 6432 (PgBouncer)
Monitor: 9090 (Prometheus), 3000 (Grafana internal)
Metrics: 9121 (Redis), 9100 (Node), 9187 (Postgres)
```

---

## 📁 PROJECT STRUCTURE

### **Key Directories**
```
workspace/
├── .github/              # Project documentation, AI context
├── website/              # Frontend source code
│   ├── index.html       # Main homepage
│   ├── case_studies.html
│   ├── enhanced_homepage_mobile.html
│   └── whitepaper_download.html
├── backend/              # Backend application (ready, not deployed)
│   ├── app.py           # Main Flask application
│   ├── database/        # PostgreSQL models & repositories
│   └── api/             # API endpoints
├── deployment/           # Deployment scripts & configs
├── business/             # Sales, marketing, research materials
└── docs/                 # Technical documentation
```

### **Critical Files**
- `INFRASTRUCTURE_MAP.md` - Complete infrastructure reference (100% complete)
- `.github/copilot-instructions.md` - Main project context
- `.env.production` - Environment variables (DO NOT COMMIT)
- `docker-compose.yml` - Container orchestration

---

## 🚫 OFF-LIMITS / NEVER DO

### **Production Safety**
- ❌ **NEVER** run `DROP TABLE` or `DELETE FROM` on production DB without explicit confirmation
- ❌ **NEVER** modify production files directly without backup
- ❌ **NEVER** commit credentials, API keys, or passwords to Git
- ❌ **NEVER** expose services on 0.0.0.0 externally (use 127.0.0.1)
- ❌ **NEVER** disable SSL or security headers

### **Code Standards**
- ❌ **NEVER** use inline styles (use external CSS)
- ❌ **NEVER** hardcode credentials in code
- ❌ **NEVER** skip input validation on user data
- ❌ **NEVER** use outdated dependencies with known vulnerabilities

### **Business Guidelines**
- ❌ **NEVER** modify pricing without approval
- ❌ **NEVER** change brand messaging/tone
- ❌ **NEVER** alter Fortune 500 case study metrics
- ❌ **NEVER** send emails from production system without testing

---

## ✅ ALWAYS DO / BEST PRACTICES

### **Development Workflow**
- ✅ **ALWAYS** test changes locally before deploying
- ✅ **ALWAYS** backup before major changes
- ✅ **ALWAYS** check `nginx -t` before reloading Nginx
- ✅ **ALWAYS** verify SSL certificate expiration
- ✅ **ALWAYS** update INFRASTRUCTURE_MAP.md when adding services

### **Code Quality**
- ✅ **ALWAYS** use semantic HTML5
- ✅ **ALWAYS** follow mobile-first responsive design
- ✅ **ALWAYS** optimize images and assets
- ✅ **ALWAYS** maintain accessibility standards
- ✅ **ALWAYS** add comments for complex logic

### **Security**
- ✅ **ALWAYS** validate and sanitize user input
- ✅ **ALWAYS** use parameterized queries (prevent SQL injection)
- ✅ **ALWAYS** implement proper error handling
- ✅ **ALWAYS** log security events
- ✅ **ALWAYS** use HTTPS for all external requests

---

## 🎯 FORTUNE 500 TARGETING STRATEGY

### **Target Companies (Phase 1)**
- Week 1: Healthcare (Johnson & Johnson, UnitedHealth, CVS)
- Week 2: Finance (JPMorgan Chase, Bank of America, Citigroup)
- Week 3: Tech (Apple, Microsoft, Google, Amazon, Meta)
- Week 4: Retail (Walmart, Amazon, Target, Home Depot)

### **Value Propositions**
- **Compliance:** SOC 2, HIPAA, PCI-DSS automated reporting
- **ROI:** Average 87% reduction in security incidents
- **Efficiency:** 156 hours saved per quarter in manual audits
- **Cost Savings:** $3-6M prevented breaches annually

### **Key Messaging**
- "Enterprise-grade security scanning trusted by Fortune 500 companies"
- "Reduce security incidents by 87% with automated vulnerability assessment"
- "Save 156 hours per quarter with AI-powered compliance reporting"

---

## 🔧 COMMON TASKS REFERENCE

### **Quick Commands**
See `COMMON_COMMANDS.md` for detailed command reference

### **Troubleshooting**
See `TROUBLESHOOTING_PLAYBOOK.md` for known issues and solutions

### **Service Dependencies**
See `SERVICE_DEPENDENCIES.md` for architecture diagram

### **Environment Variables**
See `ENV_VARIABLES_REFERENCE.md` for all configuration options

---

## 📊 CURRENT METRICS (As of Oct 16, 2025)

### **Performance**
- **Light Load (5 users):** 530.80 req/s, 9.4ms avg
- **Medium Load (20 users):** 651.68 req/s, 30.7ms avg
- **Heavy Load (50 users):** 771.74 req/s, 64.8ms avg
- **Success Rate:** 100% (0 failed requests)

### **Optimization**
- **Gzip Compression:** 80% reduction (38,995 → 8,273 bytes)
- **Redis Hit Rate:** 0% (not yet integrated with app)
- **Browser Caching:** Active (1 year for static assets)
- **Connection Pooling:** Active (PgBouncer ready)

### **Business**
- **Target Pipeline:** $6.5M (20 Fortune 500 companies)
- **Average Deal Size:** $150K/year
- **Sales Cycle:** 3-6 months (enterprise)
- **Conversion Goal:** 15% (3 clients = $450K ARR)

---

## 🚀 PHASE 2 ROADMAP

### **Week 1 (COMPLETE)** ✅
- Case studies page with Fortune 500 success stories
- Mobile-optimized homepage
- Whitepaper download system with lead capture

### **Week 2 (In Progress)**
- Live chat integration
- Interactive security assessment tool

### **Week 3 (Planned)**
- Advanced analytics dashboard
- API documentation portal

### **Week 4 (Planned)**
- Partner portal
- Client onboarding automation

---

## 💡 AI ASSISTANT TIPS

### **When Helping with Code**
- Reference existing files in `website/` directory
- Use Bootstrap 5 classes (already loaded)
- Follow Fortune 500 professional design standards
- Test responsive design (mobile, tablet, desktop)

### **When Troubleshooting**
- Check `INFRASTRUCTURE_MAP.md` for service details
- Review logs: `/var/log/nginx/`, `docker logs`, `journalctl`
- Verify services: `docker ps`, `systemctl status`
- Check TROUBLESHOOTING_PLAYBOOK.md first

### **When Deploying**
- Backup before changes: `tar -czf backup.tar.gz /var/www/html`
- Test Nginx config: `nginx -t`
- Use SCP for file transfer: `scp file root@134.199.147.45:/var/www/html/`
- Reload gracefully: `systemctl reload nginx`

### **When Suggesting Solutions**
- Prioritize DigitalOcean-compatible solutions
- Consider $40/month budget constraint
- Maintain localhost-only security architecture
- Ensure Fortune 500 enterprise-grade quality

---

## 📞 CONTACT & CREDENTIALS

### **Production Server**
- **SSH:** `root@134.199.147.45`
- **Password:** Schroeder123!

### **Database**
- **PostgreSQL Direct:** `127.0.0.1:5432`
- **Via PgBouncer:** `127.0.0.1:6432`
- **User:** admin
- **Password:** SecurePass2024!

### **Email Addresses**
- info@enterprisescanner.com
- sales@enterprisescanner.com
- support@enterprisescanner.com
- security@enterprisescanner.com
- partnerships@enterprisescanner.com

### **Monitoring**
- **Grafana:** https://enterprisescanner.com/grafana
- **Performance:** https://enterprisescanner.com/performance
- **Prometheus:** http://127.0.0.1:9090 (localhost only)

---

## 🎯 SUCCESS METRICS

### **Technical Goals**
- ✅ 100% uptime (99.9% SLA)
- ✅ <100ms response time
- ✅ A+ SSL rating
- ✅ Zero security vulnerabilities

### **Business Goals**
- 🎯 3 Fortune 500 clients by Q1 2026
- 🎯 $450K ARR minimum
- 🎯 15% conversion rate on outreach
- 🎯 <3% churn rate

### **Development Goals**
- ✅ Phase 2 Week 1 complete
- 🎯 Phase 2 complete by end of Q4 2025
- 🎯 Database fully integrated by November 2025
- 🎯 AWS/Azure scaling ready by Q1 2026

---

## 📚 ADDITIONAL RESOURCES

- **Main Instructions:** `.github/copilot-instructions.md`
- **Infrastructure Map:** `INFRASTRUCTURE_MAP.md` (100% complete)
- **Common Commands:** `COMMON_COMMANDS.md`
- **Troubleshooting:** `TROUBLESHOOTING_PLAYBOOK.md`
- **Service Dependencies:** `SERVICE_DEPENDENCIES.md`
- **Environment Variables:** `ENV_VARIABLES_REFERENCE.md`

---

**This context file enables AI assistants to provide faster, more accurate, and more relevant assistance by understanding the full project context, constraints, and priorities.**

**Last Review:** October 16, 2025  
**Next Review:** After Phase 2 completion
