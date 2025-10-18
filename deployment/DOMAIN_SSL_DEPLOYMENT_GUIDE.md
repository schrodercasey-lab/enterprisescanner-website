# Enterprise Scanner Domain & SSL Deployment Guide

## Overview
Complete guide for deploying enterprisescanner.com with enterprise-grade SSL certificates and professional email system.

## Prerequisites
- Domain registrar access (Namecheap, GoDaddy, etc.)
- Cloudflare account for DNS management and SSL
- Google Workspace account for professional email
- AWS/VPS server for hosting

## Step 1: Domain Registration Verification
1. Verify domain ownership: enterprisescanner.com
2. Ensure domain registrar supports DNS management
3. Gather domain registrar login credentials

## Step 2: Cloudflare Setup
1. **Create Cloudflare Account**
   - Sign up at https://cloudflare.com
   - Add enterprisescanner.com to your account
   - Note the nameservers provided by Cloudflare

2. **Update Nameservers**
   - Log into your domain registrar
   - Change nameservers to Cloudflare's nameservers
   - Wait 24-48 hours for propagation

3. **Configure DNS Records**
   ```bash
   # Import DNS configuration
   cloudflare-cli dns import deployment/dns/dns_records.json
   ```

## Step 3: SSL Certificate Configuration
1. **Let's Encrypt Wildcard Certificate**
   ```bash
   # Run automated SSL setup
   chmod +x deployment/ssl/certbot_setup.sh
   sudo ./deployment/ssl/certbot_setup.sh
   ```

2. **Cloudflare SSL Settings**
   - Set SSL/TLS mode to "Full (strict)"
   - Enable "Always Use HTTPS"
   - Configure security headers
   - Set up HSTS with subdomains

## Step 4: Google Workspace Email Setup
1. **Create Google Workspace Account**
   - Sign up at https://workspace.google.com
   - Verify domain ownership
   - Configure MX records (already in DNS config)

2. **Create Professional Email Addresses**
   - info@enterprisescanner.com
   - sales@enterprisescanner.com
   - support@enterprisescanner.com
   - security@enterprisescanner.com
   - partnerships@enterprisescanner.com
   - investors@enterprisescanner.com
   - admin@enterprisescanner.com
   - legal@enterprisescanner.com

3. **Configure Email Security**
   - Enable 2-factor authentication
   - Set up advanced protection
   - Configure DLP policies
   - Enable audit logging

## Step 5: Web Server Configuration
1. **Install Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Configure SSL**
   ```bash
   # Copy SSL configuration
   sudo cp deployment/ssl/nginx_ssl.conf /etc/nginx/sites-available/enterprisescanner.com
   sudo ln -s /etc/nginx/sites-available/enterprisescanner.com /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## Step 6: Application Deployment
1. **Deploy Enterprise Scanner**
   ```bash
   # Deploy application stack
   docker-compose -f deployment/production/docker/docker-compose.production.yml up -d
   ```

2. **Configure Application**
   - Update environment variables
   - Set database connections
   - Configure Redis cache
   - Enable monitoring

## Step 7: Verification and Testing
1. **Run Domain Verification**
   ```bash
   chmod +x deployment/verification/verify_domain.sh
   ./deployment/verification/verify_domain.sh
   ```

2. **Test All Endpoints**
   - https://enterprisescanner.com
   - https://www.enterprisescanner.com
   - https://api.enterprisescanner.com/health
   - https://app.enterprisescanner.com

3. **Test Email System**
   - Send test emails to all addresses
   - Verify auto-responses
   - Check forwarding rules
   - Test spam filtering

## Step 8: Security Validation
1. **SSL Labs Test**
   - Visit: https://www.ssllabs.com/ssltest/
   - Test: enterprisescanner.com
   - Target: A+ rating

2. **Security Headers Check**
   - Visit: https://securityheaders.com/
   - Test: enterprisescanner.com
   - Verify all security headers

3. **DNS Security Check**
   - Verify CAA records
   - Check DNSSEC if available
   - Validate DMARC policies

## Step 9: Monitoring Setup
1. **Enable Continuous Monitoring**
   ```bash
   # Run monitoring script
   python3 deployment/verification/domain_monitor.py
   ```

2. **Set Up Alerts**
   - Configure Cloudflare alerts
   - Set up uptime monitoring
   - Enable SSL expiration alerts
   - Configure email notifications

## Step 10: Documentation and Handover
1. **Document Configuration**
   - Save all credentials securely
   - Document DNS settings
   - Record SSL certificate details
   - Document email configurations

2. **Team Training**
   - Train team on email system
   - Provide monitoring access
   - Document escalation procedures
   - Set up rotation schedules

## Troubleshooting
### DNS Issues
- Check nameserver propagation: https://www.whatsmydns.net/
- Verify DNS records: dig enterprisescanner.com
- Check TTL settings for faster updates

### SSL Issues
- Verify certificate chain: openssl s_client -connect enterprisescanner.com:443
- Check certificate expiration: openssl x509 -enddate -noout -in cert.pem
- Validate Cloudflare SSL mode settings

### Email Issues
- Check MX record propagation: nslookup -type=MX enterprisescanner.com
- Verify SPF/DKIM/DMARC records
- Test email delivery with mail-tester.com

## Success Criteria
✅ Domain resolves correctly from global DNS
✅ SSL certificate achieves A+ rating
✅ All email addresses operational
✅ Website loads over HTTPS
✅ Security headers properly configured
✅ Monitoring and alerts active

## Support Contacts
- Technical Issues: support@enterprisescanner.com
- Security Matters: security@enterprisescanner.com
- Domain Questions: admin@enterprisescanner.com

---

**Enterprise Scanner Domain Deployment Complete**
**Ready for Fortune 500 operations**
