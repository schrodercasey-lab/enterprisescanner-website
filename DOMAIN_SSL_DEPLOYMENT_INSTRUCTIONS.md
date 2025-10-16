# 🌐 Domain & SSL Setup - Complete Guide

**Status:** Ready to Deploy  
**Domain:** enterprisescanner.com  
**Server:** 134.199.147.45  
**Estimated Time:** 15-30 minutes

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- ✅ Domain name registered (enterprisescanner.com)
- ✅ Access to domain registrar (GoDaddy, Namecheap, etc.)
- ✅ SSH access to DigitalOcean server (134.199.147.45)
- ✅ Website already deployed and working on HTTP

---

## 🚀 Quick Start (3 Steps)

### Step 1: Configure DNS (5 minutes)

**At your domain registrar (GoDaddy, Namecheap, etc.):**

1. Log into your domain registrar account
2. Find DNS settings for `enterprisescanner.com`
3. Add/Update these DNS records:

```
Type  | Name | Value           | TTL
------|------|-----------------|-----
A     | @    | 134.199.147.45  | 300
A     | www  | 134.199.147.45  | 300
```

**Example for GoDaddy:**
- Go to "My Products" → "Domains"
- Click on enterprisescanner.com → "Manage DNS"
- Add A records as shown above

**Example for Namecheap:**
- Go to "Domain List" → click "Manage"
- Advanced DNS tab → Add New Record
- Type: A Record, Host: @, Value: 134.199.147.45

4. **Wait 5-15 minutes** for DNS to propagate

**Verify DNS is working:**
```bash
# On your local machine (PowerShell)
nslookup enterprisescanner.com
# Should show: 134.199.147.45
```

---

### Step 2: Run Automated SSL Setup (10 minutes)

**On your DigitalOcean server via console:**

```bash
# 1. Download the setup script
cd /opt/enterprisescanner
curl -O https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/setup_domain_ssl_automated.sh

# 2. Make it executable
chmod +x setup_domain_ssl_automated.sh

# 3. Run it! (as root)
sudo ./setup_domain_ssl_automated.sh
```

**What the script does:**
- ✅ Checks DNS configuration
- ✅ Installs Certbot (Let's Encrypt)
- ✅ Configures firewall
- ✅ Generates SSL certificates
- ✅ Updates Nginx for HTTPS
- ✅ Sets up automatic renewal
- ✅ Restarts services

**The script will:**
1. Ask if DNS is configured (say YES if you completed Step 1)
2. Install required packages
3. Generate free SSL certificates
4. Configure everything automatically

---

### Step 3: Verify & Test (2 minutes)

**Test your secure website:**

1. **Open in browser:**
   - https://enterprisescanner.com
   - https://www.enterprisescanner.com

2. **Verify HTTPS:**
   - Look for 🔒 lock icon in address bar
   - Click lock → should show "Connection is secure"

3. **Test redirect:**
   - Visit http://enterprisescanner.com (no 's')
   - Should automatically redirect to HTTPS

4. **Check SSL rating:**
   - Visit: https://www.ssllabs.com/ssltest/analyze.html?d=enterprisescanner.com
   - Wait 2-3 minutes for scan
   - Target rating: A or A+

---

## 🎯 Alternative Method (Manual Setup)

If the automated script doesn't work, here's the manual approach:

### Manual DNS Configuration

Same as Step 1 above - configure A records at your registrar.

### Manual SSL Setup

```bash
# 1. Install Certbot
apt-get update
apt-get install -y certbot

# 2. Stop Nginx temporarily
cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml stop nginx

# 3. Generate certificate
certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@enterprisescanner.com \
  -d enterprisescanner.com \
  -d www.enterprisescanner.com

# 4. Update docker-compose.prod.yml
# Add these lines under nginx volumes:
#   - /etc/letsencrypt:/etc/letsencrypt:ro

# 5. Update nginx.conf to listen on port 443
# (See detailed nginx config in automated script)

# 6. Start services
docker-compose -f docker-compose.prod.yml up -d

# 7. Set up auto-renewal
echo "0 */12 * * * certbot renew --quiet" | crontab -
```

---

## 🔍 Troubleshooting

### DNS Issues

**Problem:** Domain doesn't resolve to 134.199.147.45

**Solution:**
```bash
# Check DNS propagation
nslookup enterprisescanner.com
dig enterprisescanner.com

# Wait longer (DNS can take up to 48 hours)
# Check propagation globally:
# Visit: https://www.whatsmydns.net/#A/enterprisescanner.com
```

---

### SSL Certificate Fails

**Problem:** Certbot says "Failed authorization" or "DNS problem"

**Solutions:**

1. **Verify DNS first:**
   ```bash
   nslookup enterprisescanner.com
   # Must return 134.199.147.45
   ```

2. **Check firewall:**
   ```bash
   # Allow HTTP traffic
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw reload
   ```

3. **Verify port 80 is accessible:**
   ```bash
   # On server
   docker-compose -f /opt/enterprisescanner/docker/docker-compose.prod.yml ps
   
   # Should show nginx on port 80
   ```

4. **Check Let's Encrypt rate limits:**
   - You can only request 5 certificates per week per domain
   - Use staging mode first to test: `--staging` flag

---

### Certificate Already Exists

**Problem:** "Certificate already exists"

**Solution:**
```bash
# Delete old certificate
certbot delete --cert-name enterprisescanner.com

# Generate new one
certbot certonly --standalone -d enterprisescanner.com -d www.enterprisescanner.com
```

---

### Nginx Won't Start with SSL

**Problem:** Nginx fails to start after adding SSL

**Solution:**
```bash
# 1. Check nginx config
docker exec enterprisescanner_nginx nginx -t

# 2. Check if certificates exist
ls -la /etc/letsencrypt/live/enterprisescanner.com/

# 3. Check nginx logs
docker logs enterprisescanner_nginx

# 4. Temporarily revert to HTTP-only config
cp /opt/enterprisescanner/docker/nginx.conf.backup /opt/enterprisescanner/docker/nginx.conf
docker-compose -f /opt/enterprisescanner/docker/docker-compose.prod.yml restart nginx
```

---

### HTTP Works but HTTPS Doesn't

**Problem:** Can access http://... but not https://...

**Solutions:**

1. **Check if port 443 is open:**
   ```bash
   netstat -tuln | grep 443
   # Should show nginx listening
   ```

2. **Check firewall:**
   ```bash
   ufw status
   # Should show 443/tcp ALLOW
   ```

3. **Verify certificates are mounted:**
   ```bash
   docker exec enterprisescanner_nginx ls -la /etc/letsencrypt/live/
   ```

---

## 📊 Verification Checklist

After setup, verify everything is working:

- [ ] ✅ https://enterprisescanner.com loads with 🔒 lock icon
- [ ] ✅ https://www.enterprisescanner.com also works
- [ ] ✅ http://enterprisescanner.com redirects to HTTPS
- [ ] ✅ Certificate is valid (not expired)
- [ ] ✅ SSL Labs rating is A or A+ (https://www.ssllabs.com/ssltest/)
- [ ] ✅ No browser security warnings
- [ ] ✅ All website pages load correctly
- [ ] ✅ CSS and JavaScript work properly

---

## 🔐 Security Best Practices

Your setup includes:

- ✅ **TLS 1.2/1.3** - Modern encryption protocols
- ✅ **Strong cipher suites** - Industry-standard encryption
- ✅ **HSTS** - Forces HTTPS connections
- ✅ **Security headers** - Protects against common attacks
- ✅ **Auto-renewal** - Certificate renews automatically
- ✅ **Firewall** - UFW protecting server
- ✅ **Rate limiting** - Prevents abuse

---

## 🔄 Certificate Renewal

Your SSL certificate will automatically renew!

**Certificate details:**
- **Issued by:** Let's Encrypt
- **Valid for:** 90 days
- **Auto-renewal:** Checks twice daily
- **Renewal trigger:** 30 days before expiry

**Manual renewal (if needed):**
```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal

# Restart nginx after renewal
cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml restart nginx
```

**Check certificate expiry:**
```bash
certbot certificates
```

---

## 📈 What's Next?

After SSL is working:

### Option 3: Deploy Backend Microservices
- Deploy 7 Python backend services
- Real-time security scanning
- API endpoints
- Database integration

### Option 4: Monitoring & Backups
- Automated database backups
- Uptime monitoring
- SSL monitoring
- Performance dashboards

---

## 🆘 Need Help?

### Quick Commands

```bash
# Check DNS
nslookup enterprisescanner.com

# Check certificate
certbot certificates

# Check nginx status
docker ps | grep nginx

# View nginx logs
docker logs enterprisescanner_nginx

# Test nginx config
docker exec enterprisescanner_nginx nginx -t

# Restart services
cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml restart

# Check SSL from command line
curl -I https://enterprisescanner.com
```

### Common Files

- **Nginx config:** `/opt/enterprisescanner/docker/nginx.conf`
- **Docker compose:** `/opt/enterprisescanner/docker/docker-compose.prod.yml`
- **SSL certs:** `/etc/letsencrypt/live/enterprisescanner.com/`
- **Website files:** `/opt/enterprisescanner/website/`

---

## 📞 Support Resources

- **Let's Encrypt Status:** https://letsencrypt.status.io/
- **SSL Test:** https://www.ssllabs.com/ssltest/
- **DNS Propagation:** https://www.whatsmydns.net/
- **Certbot Docs:** https://certbot.eff.org/docs/

---

**Ready to get started? Begin with Step 1: Configure DNS at your domain registrar!** 🚀
