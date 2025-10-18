# Domain & SSL Setup Guide - Enterprise Scanner

**Goal:** Secure your platform with HTTPS and a professional domain name

**Time Required:** 30 minutes  
**Cost:** $10-15/year for domain  
**SSL Certificate:** Free (Let's Encrypt)

---

## Step 1: Register a Domain Name

### Option A: Use Your Own Domain
If you already have a domain, skip to Step 2.

### Option B: Register a New Domain
Choose a domain registrar and register your domain:

**Recommended Registrars:**
- **Namecheap** (namecheap.com) - $8-12/year
- **Google Domains** (domains.google.com) - $12/year
- **GoDaddy** (godaddy.com) - $10-15/year
- **Cloudflare** (cloudflare.com) - $10/year

**Domain Suggestions:**
- enterprisescanner.com
- enterprisescanner.io
- enterprisescanner.net
- [yourcompany]scanner.com

**Action Required:** Register your chosen domain and note it down.

**Example:** Let's say you register `enterprisescanner.com`

---

## Step 2: Configure DNS Records

Once you have your domain, configure DNS to point to your server.

### DNS Configuration:

**Your Server IP:** `134.199.147.45`

**Required DNS Records:**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 134.199.147.45 | 3600 |
| A | www | 134.199.147.45 | 3600 |

**Or alternatively:**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 134.199.147.45 | 3600 |
| CNAME | www | @ | 3600 |

### How to Add DNS Records:

**For Namecheap:**
1. Log in to Namecheap
2. Go to Domain List → Manage
3. Click "Advanced DNS"
4. Add the A record(s) as shown above

**For Google Domains:**
1. Log in to Google Domains
2. Click your domain → DNS
3. Add custom records as shown above

**For GoDaddy:**
1. Log in to GoDaddy
2. My Products → Domain → DNS
3. Add the A record(s) as shown above

**For Cloudflare:**
1. Log in to Cloudflare
2. Select your domain → DNS
3. Add the A record(s) as shown above

**⏰ DNS Propagation Time:** 5-60 minutes (sometimes up to 24 hours)

### Verify DNS is Working:

On your local computer, run:
```bash
# Windows (PowerShell)
nslookup yourdomain.com

# Should return: 134.199.147.45
```

---

## Step 3: Install Certbot (SSL Certificate Tool)

Once DNS is configured and propagated, run these commands on your server:

```bash
# Update package list
apt update

# Install Certbot and Nginx plugin
apt install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
```

**Expected Output:** `certbot 2.x.x`

---

## Step 4: Obtain SSL Certificate

**IMPORTANT:** Make sure your domain DNS is pointing to your server before running this!

### Automatic SSL Setup (Recommended):

```bash
# Replace with your actual domain and email
certbot --nginx -d yourdomain.com -d www.yourdomain.com --non-interactive --agree-tos --email your@email.com --redirect

# Example:
# certbot --nginx -d enterprisescanner.com -d www.enterprisescanner.com --non-interactive --agree-tos --email admin@enterprisescanner.com --redirect
```

**What this does:**
1. Obtains SSL certificate from Let's Encrypt
2. Automatically configures Nginx for HTTPS
3. Sets up automatic HTTP → HTTPS redirect
4. Configures auto-renewal

### Manual SSL Setup (If automatic fails):

```bash
# Obtain certificate only
certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com --email your@email.com --agree-tos --non-interactive

# Then manually update Nginx config (see Step 5)
```

---

## Step 5: Verify HTTPS Configuration

### Test Your Site:

```bash
# From your server
curl -I https://yourdomain.com

# Should return: HTTP/2 200
# Should see: Strict-Transport-Security header
```

### Test in Browser:
1. Visit `https://yourdomain.com`
2. Look for the padlock icon 🔒
3. Click padlock → Should show "Connection is secure"

### Test All Endpoints:

```bash
echo "Testing HTTPS endpoints..."
echo ""
echo "Website:      $(curl -I https://yourdomain.com 2>&1 | grep HTTP | head -1)"
echo "Chat API:     $(curl -I https://yourdomain.com/api/chat/ 2>&1 | grep HTTP | head -1)"
echo "Analytics:    $(curl -I https://yourdomain.com/api/analytics/ 2>&1 | grep HTTP | head -1)"
echo "Assessment:   $(curl -I https://yourdomain.com/api/assessment/ 2>&1 | grep HTTP | head -1)"
```

**Expected:** All should return `HTTP/2 200` (note: HTTP/2, not HTTP/1.1)

---

## Step 6: Configure Auto-Renewal

Let's Encrypt certificates expire after 90 days. Certbot automatically sets up renewal.

### Verify Auto-Renewal:

```bash
# Test renewal process (dry run)
certbot renew --dry-run

# Check renewal timer
systemctl list-timers | grep certbot

# Expected: certbot.timer should be active
```

### Manual Renewal (if needed):

```bash
certbot renew
systemctl reload nginx
```

---

## Step 7: Update Your Website URLs

If you have any hardcoded URLs in your website, update them:

**Before:**
- `http://134.199.147.45`

**After:**
- `https://yourdomain.com`

No changes needed if you're using relative URLs (`/api/chat/` instead of full URLs).

---

## Nginx Configuration Reference

After Certbot runs, your Nginx config will look like this:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    root /opt/enterprisescanner/website;
    index index.html;
    
    # Your existing API proxy configuration...
    location /api/chat/ {
        proxy_pass http://127.0.0.1:5001/;
        # ... rest of proxy config
    }
    
    # ... other locations
}
```

---

## Troubleshooting

### DNS Not Resolving
```bash
# Check DNS propagation
nslookup yourdomain.com
dig yourdomain.com

# Wait 5-30 minutes and try again
```

### Certbot Fails
```bash
# Check if port 80 is accessible
curl http://yourdomain.com

# If not accessible, check firewall
ufw status
ufw allow 80/tcp
ufw allow 443/tcp
```

### Certificate Not Working
```bash
# Check Nginx config
nginx -t

# View certificate details
certbot certificates

# Reload Nginx
systemctl reload nginx
```

### HTTP Not Redirecting to HTTPS
```bash
# Check Nginx config has redirect
grep "return 301" /etc/nginx/sites-available/enterprisescanner

# If missing, add redirect manually and reload
systemctl reload nginx
```

---

## Security Best Practices

After SSL is set up, add these security headers to your Nginx config:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Success Checklist

- [ ] Domain registered and paid for
- [ ] DNS A record pointing to 134.199.147.45
- [ ] DNS propagated (nslookup works)
- [ ] Certbot installed on server
- [ ] SSL certificate obtained
- [ ] HTTPS working (padlock visible)
- [ ] HTTP → HTTPS redirect working
- [ ] All API endpoints work over HTTPS
- [ ] Auto-renewal configured
- [ ] SSL rating A+ on ssllabs.com

---

## Next Steps After SSL

Once SSL is complete:
1. ✅ Test all endpoints work with HTTPS
2. ✅ Verify auto-renewal is configured
3. ⏸️ **STOP HERE** - You requested to pause and plan before continuing
4. When ready: Choose Option B (Security Hardening), C (Database Integration), or D (Monitoring)

---

## Quick Reference

**Your Current Setup:**
- Server IP: 134.199.147.45
- Current URL: http://134.199.147.45
- After SSL: https://yourdomain.com

**Commands:**
- Install Certbot: `apt install certbot python3-certbot-nginx`
- Get Certificate: `certbot --nginx -d yourdomain.com`
- Test Renewal: `certbot renew --dry-run`
- Reload Nginx: `systemctl reload nginx`

---

**Ready to begin? First step: Do you have a domain name ready, or do you need to register one?**
