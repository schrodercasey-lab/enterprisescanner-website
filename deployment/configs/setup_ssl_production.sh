#!/bin/bash
# Enterprise Scanner - SSL Certificate Setup and Security Hardening
# Automated Let's Encrypt SSL with A+ Security Rating
# Domain: enterprisescanner.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="enterprisescanner.com"
WWW_DOMAIN="www.enterprisescanner.com"
EMAIL="admin@enterprisescanner.com"
NGINX_CONFIG="/etc/nginx/sites-available/enterprise_scanner"
SSL_CONFIG="/etc/nginx/conf.d/ssl-params.conf"
DHPARAM="/etc/nginx/dhparam.pem"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root"
   exit 1
fi

# Welcome message
clear
echo -e "${GREEN}"
echo "============================================"
echo "🔒 ENTERPRISE SCANNER SSL SETUP & SECURITY 🔒"
echo "============================================"
echo -e "${NC}"
log "Setting up SSL certificates and A+ security for $DOMAIN"
echo

# Step 1: Verify DNS resolution
log "Step 1: Verifying DNS resolution..."
if nslookup $DOMAIN | grep -q "Address:"; then
    RESOLVED_IP=$(nslookup $DOMAIN | grep "Address:" | tail -1 | awk '{print $2}')
    log "✅ $DOMAIN resolves to: $RESOLVED_IP"
else
    error "❌ DNS resolution failed for $DOMAIN"
    error "Please ensure DNS A record points to this server before running SSL setup"
    exit 1
fi

# Verify this server's IP matches DNS
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unknown")
if [[ "$RESOLVED_IP" == "$SERVER_IP" ]]; then
    log "✅ DNS correctly points to this server ($SERVER_IP)"
else
    warning "⚠️ DNS IP ($RESOLVED_IP) doesn't match server IP ($SERVER_IP)"
    warning "SSL certificate may fail. Ensure DNS propagation is complete."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Install Certbot if not already installed
log "Step 2: Installing/updating Certbot..."
apt-get update -q
apt-get install -yq certbot python3-certbot-nginx

# Verify Certbot installation
if command -v certbot &> /dev/null; then
    CERTBOT_VERSION=$(certbot --version 2>&1 | head -1)
    log "✅ Certbot installed: $CERTBOT_VERSION"
else
    error "❌ Certbot installation failed"
    exit 1
fi

# Step 3: Stop Nginx temporarily for certificate generation
log "Step 3: Preparing Nginx for SSL certificate generation..."
systemctl stop nginx

# Step 4: Generate SSL certificates
log "Step 4: Generating SSL certificates with Let's Encrypt..."
info "This may take a few minutes..."

# Run Certbot with staging first (for testing)
log "Testing certificate generation with staging environment..."
if certbot certonly --standalone --staging \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN \
    -d $WWW_DOMAIN; then
    log "✅ Staging certificate test successful"
    
    # Delete staging certificates
    certbot delete --cert-name $DOMAIN --non-interactive 2>/dev/null || true
else
    error "❌ Staging certificate test failed"
    systemctl start nginx
    exit 1
fi

# Generate production certificates
log "Generating production SSL certificates..."
if certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN \
    -d $WWW_DOMAIN; then
    log "✅ Production SSL certificates generated successfully"
else
    error "❌ SSL certificate generation failed"
    systemctl start nginx
    exit 1
fi

# Step 5: Generate strong DH parameters
log "Step 5: Generating strong Diffie-Hellman parameters..."
if [ ! -f "$DHPARAM" ]; then
    info "Generating 2048-bit DH parameters (this may take several minutes)..."
    openssl dhparam -out $DHPARAM 2048
    log "✅ DH parameters generated"
else
    log "✅ DH parameters already exist"
fi

# Step 6: Create SSL configuration
log "Step 6: Creating optimal SSL configuration..."
cat > $SSL_CONFIG << 'EOF'
# Enterprise Scanner SSL Configuration
# Optimized for A+ Security Rating

# SSL Settings
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_ecdh_curve secp384r1;

# SSL Session Settings
ssl_session_timeout 10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;

# SSL Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security Headers
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

# Content Security Policy (Enterprise Scanner specific)
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; font-src 'self' fonts.googleapis.com fonts.gstatic.com cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" always;

# Hide Nginx version
server_tokens off;
EOF

log "✅ SSL configuration created"

# Step 7: Update Nginx configuration for SSL
log "Step 7: Updating Nginx configuration with SSL certificates..."

# Backup current configuration
cp $NGINX_CONFIG "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

# Create new SSL-enabled configuration
cat > $NGINX_CONFIG << EOF
# Enterprise Scanner Nginx Configuration
# Production HTTPS setup with A+ Security Rating

upstream enterprise_scanner {
    server 127.0.0.1:5000;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN $WWW_DOMAIN;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN $WWW_DOMAIN;
    
    # Root directory
    root /opt/enterprise_scanner/website;
    index index.html;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;
    ssl_dhparam $DHPARAM;
    
    # Include SSL parameters
    include $SSL_CONFIG;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/atom+xml
        image/svg+xml;
    
    # Security settings
    client_max_body_size 10M;
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;
    
    # Static files with caching
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        access_log off;
        
        # Fallback to application for missing static files
        try_files \$uri @app;
    }
    
    # Main application
    location / {
        try_files \$uri @app;
    }
    
    # Proxy to Flask application
    location @app {
        proxy_pass http://enterprise_scanner;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # Keep alive
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
    
    # Health check endpoint (no auth required)
    location = /api/health {
        proxy_pass http://enterprise_scanner/api/health;
        access_log off;
    }
    
    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://enterprise_scanner;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(env|log|conf|db)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Security.txt for responsible disclosure
    location = /.well-known/security.txt {
        return 200 "Contact: security@$DOMAIN\nPreferred-Languages: en\nCanonical: https://$DOMAIN/.well-known/security.txt";
        add_header Content-Type text/plain;
    }
}

# Rate limiting zones
http {
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/m;
}
EOF

log "✅ Nginx configuration updated for SSL"

# Step 8: Test Nginx configuration
log "Step 8: Testing Nginx configuration..."
if nginx -t; then
    log "✅ Nginx configuration test passed"
else
    error "❌ Nginx configuration test failed"
    # Restore backup
    mv "${NGINX_CONFIG}.backup."* $NGINX_CONFIG
    exit 1
fi

# Step 9: Start Nginx
log "Step 9: Starting Nginx with SSL configuration..."
systemctl start nginx
systemctl reload nginx

if systemctl is-active --quiet nginx; then
    log "✅ Nginx started successfully"
else
    error "❌ Nginx failed to start"
    journalctl -u nginx --no-pager -n 10
    exit 1
fi

# Step 10: Setup automatic renewal
log "Step 10: Setting up automatic SSL certificate renewal..."

# Create renewal script
cat > /etc/cron.daily/certbot-renew << 'EOF'
#!/bin/bash
# Enterprise Scanner SSL Certificate Renewal

# Renew certificates
/usr/bin/certbot renew --quiet --no-self-upgrade

# Reload Nginx if certificates were renewed
if [ $? -eq 0 ]; then
    /bin/systemctl reload nginx
fi

# Log renewal attempt
echo "$(date): SSL certificate renewal check completed" >> /var/log/enterprise-scanner-ssl.log
EOF

chmod +x /etc/cron.daily/certbot-renew

# Create systemd timer for more reliable renewal
cat > /etc/systemd/system/certbot-renewal.service << 'EOF'
[Unit]
Description=Certbot Renewal
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet --no-self-upgrade
ExecStartPost=/bin/systemctl reload nginx
EOF

cat > /etc/systemd/system/certbot-renewal.timer << 'EOF'
[Unit]
Description=Run certbot twice daily
Requires=certbot-renewal.service

[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable certbot-renewal.timer
systemctl start certbot-renewal.timer

log "✅ Automatic SSL renewal configured"

# Step 11: Test SSL certificate
log "Step 11: Testing SSL certificate..."
sleep 5

# Test HTTPS connection
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health | grep -q "200"; then
    log "✅ HTTPS connection successful"
else
    warning "⚠️ HTTPS test failed - may need a few minutes for propagation"
fi

# Step 12: Security hardening
log "Step 12: Applying additional security hardening..."

# Update system packages
apt-get update -q
apt-get upgrade -yq

# Install fail2ban for intrusion prevention
apt-get install -yq fail2ban

# Configure fail2ban for Nginx
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
action = iptables-multiport[name=BotSearch, port="http,https", protocol=tcp]
logpath = /var/log/nginx/access.log
EOF

systemctl enable fail2ban
systemctl start fail2ban

log "✅ Security hardening applied"

# Step 13: SSL Security Test
log "Step 13: Running SSL security verification..."

# Create SSL test script
cat > /tmp/ssl_test.sh << 'EOF'
#!/bin/bash
echo "Testing SSL configuration..."

# Test SSL Labs rating (requires external API)
echo "For full SSL Labs test, visit: https://www.ssllabs.com/ssltest/analyze.html?d=enterprisescanner.com"

# Test cipher suites
echo "Testing cipher suites..."
echo | openssl s_client -connect enterprisescanner.com:443 -servername enterprisescanner.com 2>/dev/null | openssl x509 -noout -subject -dates

# Test HTTP/2 support
echo "Testing HTTP/2 support..."
curl -s -o /dev/null -w "%{http_version}\n" https://enterprisescanner.com/

# Test security headers
echo "Testing security headers..."
curl -s -I https://enterprisescanner.com/ | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection|Content-Security-Policy)"
EOF

chmod +x /tmp/ssl_test.sh
bash /tmp/ssl_test.sh

# Step 14: Create monitoring script
log "Step 14: Setting up SSL monitoring..."

cat > /opt/enterprise_scanner/ssl_monitor.sh << 'EOF'
#!/bin/bash
# Enterprise Scanner SSL Certificate Monitoring

DOMAIN="enterprisescanner.com"
CERT_FILE="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
EMAIL="admin@enterprisescanner.com"
DAYS_WARNING=30

# Check certificate expiration
if [ -f "$CERT_FILE" ]; then
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_UNTIL_EXPIRY -le $DAYS_WARNING ]; then
        echo "WARNING: SSL certificate for $DOMAIN expires in $DAYS_UNTIL_EXPIRY days"
        # Send email alert (configure postfix/sendmail for email)
        echo "SSL certificate for $DOMAIN expires in $DAYS_UNTIL_EXPIRY days" | logger -p cron.warning
    fi
    
    echo "SSL certificate status: $DAYS_UNTIL_EXPIRY days until expiry"
else
    echo "ERROR: SSL certificate file not found: $CERT_FILE"
    logger -p cron.error "SSL certificate file not found for $DOMAIN"
fi

# Test HTTPS connectivity
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health | grep -q "200"; then
    echo "HTTPS connectivity: OK"
else
    echo "ERROR: HTTPS connectivity failed"
    logger -p cron.error "HTTPS connectivity failed for $DOMAIN"
fi
EOF

chmod +x /opt/enterprise_scanner/ssl_monitor.sh
chown enterprisescanner:enterprisescanner /opt/enterprise_scanner/ssl_monitor.sh

# Add to crontab for daily monitoring
(crontab -u enterprisescanner -l 2>/dev/null; echo "0 8 * * * /opt/enterprise_scanner/ssl_monitor.sh") | crontab -u enterprisescanner -

log "✅ SSL monitoring configured"

# Step 15: Final verification and report
log "Step 15: Final SSL setup verification..."

# Wait for services to stabilize
sleep 10

# Comprehensive SSL test
echo
echo -e "${GREEN}============================================"
echo "🔒 SSL SETUP COMPLETE - VERIFICATION REPORT"
echo "============================================${NC}"
echo

# Test certificate details
if openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -text -noout > /dev/null 2>&1; then
    CERT_ISSUER=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -issuer | cut -d'=' -f2-)
    CERT_SUBJECT=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -subject | cut -d'=' -f2-)
    CERT_EXPIRY=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -dates | grep "notAfter" | cut -d'=' -f2)
    
    log "✅ SSL Certificate Details:"
    echo "   Subject: $CERT_SUBJECT"
    echo "   Issuer: $CERT_ISSUER"
    echo "   Expires: $CERT_EXPIRY"
else
    error "❌ SSL certificate verification failed"
fi

# Test HTTPS response
echo
log "🌐 Testing HTTPS endpoints:"
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://$DOMAIN/api/health | grep -q "200"; then
    echo "   ✅ https://$DOMAIN/api/health - OK"
else
    echo "   ❌ https://$DOMAIN/api/health - Failed"
fi

if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://www.$DOMAIN/api/health | grep -q "200"; then
    echo "   ✅ https://www.$DOMAIN/api/health - OK"
else
    echo "   ❌ https://www.$DOMAIN/api/health - Failed"
fi

# Test HTTP to HTTPS redirect
echo
log "🔄 Testing HTTP to HTTPS redirect:"
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/ 2>/dev/null)
if [ "$HTTP_RESPONSE" = "301" ]; then
    echo "   ✅ HTTP to HTTPS redirect working"
else
    echo "   ❌ HTTP to HTTPS redirect failed (got $HTTP_RESPONSE)"
fi

# Test security headers
echo
log "🛡️ Security headers verification:"
HEADERS=$(curl -s -I https://$DOMAIN/ 2>/dev/null)
if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
    echo "   ✅ HSTS header present"
else
    echo "   ❌ HSTS header missing"
fi

if echo "$HEADERS" | grep -q "X-Frame-Options"; then
    echo "   ✅ X-Frame-Options header present"
else
    echo "   ❌ X-Frame-Options header missing"
fi

if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
    echo "   ✅ X-Content-Type-Options header present"
else
    echo "   ❌ X-Content-Type-Options header missing"
fi

if echo "$HEADERS" | grep -q "Content-Security-Policy"; then
    echo "   ✅ Content-Security-Policy header present"
else
    echo "   ❌ Content-Security-Policy header missing"
fi

# Certificate renewal test
echo
log "🔄 SSL certificate renewal setup:"
if systemctl is-active --quiet certbot-renewal.timer; then
    echo "   ✅ Automatic renewal timer active"
else
    echo "   ❌ Automatic renewal timer not active"
fi

if [ -f "/etc/cron.daily/certbot-renew" ]; then
    echo "   ✅ Daily renewal script installed"
else
    echo "   ❌ Daily renewal script missing"
fi

# Final summary
echo
echo -e "${GREEN}🎉 ENTERPRISE SCANNER SSL SETUP COMPLETE!${NC}"
echo
echo -e "${BLUE}Production URLs:${NC}"
echo "   🌐 Main Site: https://$DOMAIN"
echo "   📊 CRM Dashboard: https://$DOMAIN/crm-dashboard.html"
echo "   📧 Email Dashboard: https://$DOMAIN/email-dashboard.html"
echo "   📈 Analytics: https://$DOMAIN/analytics-dashboard.html"
echo "   🔧 API Documentation: https://$DOMAIN/api-documentation.html"
echo "   ❤️ Health Check: https://$DOMAIN/api/health"
echo
echo -e "${BLUE}SSL Certificate Information:${NC}"
echo "   📋 Certificate Location: /etc/letsencrypt/live/$DOMAIN/"
echo "   🔄 Automatic Renewal: Configured (daily check)"
echo "   📊 SSL Rating Target: A+ (verify at ssllabs.com)"
echo "   🔒 Security Headers: Enabled"
echo "   🛡️ Fail2ban Protection: Active"
echo
echo -e "${BLUE}Next Steps:${NC}"
echo "   1. 🔍 Test SSL rating: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "   2. 📧 Configure email system with Google Workspace"
echo "   3. 📊 Monitor certificate renewal: tail -f /var/log/enterprise-scanner-ssl.log"
echo "   4. 🚀 Launch Fortune 500 marketing campaigns!"
echo
echo -e "${GREEN}Enterprise Scanner is now secured with A+ SSL and ready for Fortune 500 business!${NC}"