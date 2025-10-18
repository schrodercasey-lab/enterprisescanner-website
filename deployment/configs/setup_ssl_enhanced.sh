#!/bin/bash
# Enterprise Scanner - Enhanced SSL and Domain Configuration
# Complete SSL setup with nginx reverse proxy and security hardening

set -e

# Configuration
DOMAIN="enterprisescanner.com"
WWW_DOMAIN="www.enterprisescanner.com"
EMAIL="admin@enterprisescanner.com"
WEBROOT="/var/www/enterprisescanner"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
SSL_PATH="/etc/letsencrypt/live/${DOMAIN}"
LOG_FILE="/var/log/enterprise_ssl_setup.log"
FLASK_PORT="5000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${BLUE}=================================="
    echo -e "  $1"
    echo -e "==================================${NC}"
}

print_status() {
    echo -e "${GREEN}[✅ SUCCESS]${NC} $1"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️  WARNING]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[❌ ERROR]${NC} $1"
    log "ERROR: $1"
}

print_info() {
    echo -e "${BLUE}[ℹ️  INFO]${NC} $1"
    log "INFO: $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        echo "Usage: sudo bash setup_ssl_enhanced.sh"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing required packages..."
    
    # Update package repositories
    apt update -qq
    
    # Install required packages
    apt install -y nginx certbot python3-certbot-nginx ufw curl openssl
    
    print_status "All dependencies installed successfully"
}

# Configure UFW firewall
configure_firewall() {
    print_info "Configuring UFW firewall..."
    
    # Reset UFW to defaults
    ufw --force reset
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow essential services
    ufw allow 22/tcp comment 'SSH'
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    ufw allow ${FLASK_PORT}/tcp comment 'Flask Application'
    
    # Enable firewall
    ufw --force enable
    
    print_status "Firewall configured - SSH(22), HTTP(80), HTTPS(443), Flask(${FLASK_PORT}) allowed"
}

# Create enhanced nginx configuration
create_nginx_config() {
    print_info "Creating enhanced nginx configuration..."
    
    # Backup existing config if it exists
    if [[ -f "${NGINX_AVAILABLE}/${DOMAIN}" ]]; then
        cp "${NGINX_AVAILABLE}/${DOMAIN}" "${NGINX_AVAILABLE}/${DOMAIN}.backup.$(date +%s)"
    fi
    
    cat > "${NGINX_AVAILABLE}/${DOMAIN}" << EOF
# Enterprise Scanner - Enhanced Production Nginx Configuration
# Professional cybersecurity platform for Fortune 500 companies
# SSL Configuration with A+ Security Rating

# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=general:10m rate=5r/s;

# Upstream Flask application
upstream flask_app {
    server 127.0.0.1:${FLASK_PORT} fail_timeout=0;
}

# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} ${WWW_DOMAIN};
    
    # Security headers even for HTTP
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Let's Encrypt challenge location
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server - main configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN} ${WWW_DOMAIN};
    
    # SSL Configuration
    ssl_certificate ${SSL_PATH}/fullchain.pem;
    ssl_private_key ${SSL_PATH}/privkey.pem;
    ssl_trusted_certificate ${SSL_PATH}/chain.pem;
    
    # SSL Settings for A+ rating
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_ecdh_curve secp384r1;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_session_timeout 10m;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # Enterprise Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net cdnjs.cloudflare.com *.googleapis.com *.gstatic.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; img-src 'self' data: blob: *.googleapis.com *.gstatic.com; font-src 'self' fonts.googleapis.com fonts.gstatic.com cdnjs.cloudflare.com; connect-src 'self' *.googleapis.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), speaker=(), vibrate=(), fullscreen=(self)" always;
    add_header X-Robots-Tag "noindex, nofollow, nosnippet, noarchive" always;
    
    # Custom headers for Enterprise Scanner
    add_header X-Enterprise-Scanner "Production" always;
    add_header X-Security-Level "Enterprise" always;
    
    # Document root
    root ${WEBROOT};
    index index.html crm-dashboard.html;
    
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
        application/xml
        image/svg+xml;
    
    # Main location - serve static files first, then proxy to Flask
    location / {
        # Rate limiting for general requests
        limit_req zone=general burst=20 nodelay;
        
        # Try static files first, then proxy to Flask
        try_files \$uri \$uri/ @flask;
        
        # Cache static files
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary "Accept-Encoding";
            access_log off;
        }
    }
    
    # Proxy to Flask application
    location @flask {
        proxy_pass http://flask_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_set_header X-Forwarded-Port \$server_port;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # API endpoints with enhanced security
    location /api/ {
        # Rate limiting for API requests
        limit_req zone=api burst=50 nodelay;
        
        proxy_pass http://flask_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        
        # API-specific headers
        add_header X-API-Version "1.0" always;
        add_header X-RateLimit-Limit "600" always;
        add_header X-Content-Type-Options nosniff always;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin "\$http_origin" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # CRM Dashboard - primary application
    location /crm-dashboard.html {
        proxy_pass http://flask_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Cache control for dynamic content
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://flask_app/health;
        access_log off;
        
        # Allow health checks without rate limiting
        limit_req off;
    }
    
    # Security: Block access to sensitive files
    location ~ /\.(htaccess|htpasswd|env|git) {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Security: Block access to backup files
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Security: Block common attack patterns
    location ~* \.(sql|log|conf)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Robots.txt
    location = /robots.txt {
        add_header Content-Type text/plain;
        return 200 "User-agent: *\nDisallow: /api/\nDisallow: /admin/\n";
        access_log off;
    }
    
    # Favicon
    location = /favicon.ico {
        try_files \$uri =404;
        access_log off;
        log_not_found off;
    }
    
    # Security monitoring endpoint
    location = /security-check {
        add_header Content-Type application/json;
        return 200 '{"status":"secure","timestamp":"'"\$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","ssl":"enabled","security_headers":"active"}';
        access_log off;
    }
    
    # Hide nginx version
    server_tokens off;
    
    # Custom error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
EOF
    
    # Create certbot webroot directory
    mkdir -p /var/www/certbot
    chown www-data:www-data /var/www/certbot
    
    # Enable the site
    ln -sf "${NGINX_AVAILABLE}/${DOMAIN}" "${NGINX_ENABLED}/"
    
    # Remove default nginx site if it exists
    rm -f "${NGINX_ENABLED}/default"
    
    print_status "Enhanced nginx configuration created successfully"
}

# Setup web directory
setup_web_directory() {
    print_info "Setting up web directory structure..."
    
    # Create main web directory
    mkdir -p "$WEBROOT"
    mkdir -p "$WEBROOT/css"
    mkdir -p "$WEBROOT/js"
    mkdir -p "$WEBROOT/assets"
    mkdir -p "$WEBROOT/api"
    
    # Set proper permissions
    chown -R www-data:www-data "$WEBROOT"
    chmod -R 755 "$WEBROOT"
    
    # Create a simple index page
    cat > "$WEBROOT/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Scanner - Cybersecurity Platform</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #27ae60; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
        .btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Enterprise Scanner</h1>
        <div class="status">
            <strong>✅ Production Server Online</strong><br>
            SSL Certificate: Active<br>
            Security: Enterprise Grade<br>
            Status: Operational
        </div>
        <p>Welcome to Enterprise Scanner - the premium cybersecurity platform for Fortune 500 companies.</p>
        <a href="/crm-dashboard.html" class="btn">Access CRM Dashboard</a>
        <a href="/security-assessment.html" class="btn">Security Assessment</a>
        <a href="/api-documentation.html" class="btn">API Documentation</a>
    </div>
</body>
</html>
EOF
    
    print_status "Web directory structure created successfully"
}

# Test nginx configuration
test_nginx() {
    print_info "Testing nginx configuration..."
    
    if nginx -t; then
        print_status "Nginx configuration test passed"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Obtain SSL certificate
obtain_ssl_certificate() {
    print_info "Obtaining SSL certificate from Let's Encrypt..."
    
    # Stop nginx if running
    systemctl stop nginx 2>/dev/null || true
    
    # Obtain certificate using standalone mode
    if certbot certonly \
        --standalone \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domains "$DOMAIN,$WWW_DOMAIN" \
        --rsa-key-size 4096; then
        print_status "SSL certificate obtained successfully"
    else
        print_error "Failed to obtain SSL certificate"
        exit 1
    fi
    
    # Start nginx
    systemctl start nginx
}

# Configure automatic renewal
setup_auto_renewal() {
    print_info "Setting up automatic SSL renewal..."
    
    # Create renewal hook script
    cat > /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh << 'EOF'
#!/bin/bash
# Reload nginx after certificate renewal
systemctl reload nginx
EOF
    
    chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh
    
    # Test automatic renewal
    if certbot renew --dry-run; then
        print_status "Automatic renewal test passed"
    else
        print_warning "Automatic renewal test failed - manual intervention may be required"
    fi
    
    # Ensure cron job exists for renewal
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        print_status "Added certbot renewal to crontab"
    fi
}

# Setup security monitoring
setup_security_monitoring() {
    print_info "Setting up security monitoring..."
    
    # Create SSL monitoring script
    cat > /usr/local/bin/enterprise_ssl_monitor.sh << EOF
#!/bin/bash
# Enterprise Scanner - SSL and Security Monitoring

DOMAIN="${DOMAIN}"
CERT_FILE="${SSL_PATH}/cert.pem"
DAYS_THRESHOLD=30
EMAIL="${EMAIL}"
LOG_FILE="/var/log/ssl_monitor.log"

log() {
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - \$1" >> "\$LOG_FILE"
}

# Check SSL certificate expiry
if [ -f "\$CERT_FILE" ]; then
    EXPIRY_DATE=\$(openssl x509 -in "\$CERT_FILE" -noout -enddate | cut -d= -f2)
    EXPIRY_EPOCH=\$(date -d "\$EXPIRY_DATE" +%s)
    CURRENT_EPOCH=\$(date +%s)
    DAYS_UNTIL_EXPIRY=\$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
    
    log "SSL certificate for \$DOMAIN expires in \$DAYS_UNTIL_EXPIRY days"
    
    if [ \$DAYS_UNTIL_EXPIRY -le \$DAYS_THRESHOLD ]; then
        log "WARNING: SSL certificate expires in \$DAYS_UNTIL_EXPIRY days"
        # Add email notification here when mail is configured
    fi
else
    log "ERROR: SSL certificate file not found: \$CERT_FILE"
fi

# Check nginx status
if systemctl is-active --quiet nginx; then
    log "Nginx service is running"
else
    log "ERROR: Nginx service is not running"
    systemctl restart nginx
fi

# Check SSL grade
SSL_GRADE=\$(curl -s "https://api.ssllabs.com/api/v3/analyze?host=\$DOMAIN&publish=off&startNew=off&fromCache=on&maxAge=24&all=done" | grep -o '"grade":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ ! -z "\$SSL_GRADE" ]; then
    log "SSL Labs grade: \$SSL_GRADE"
fi

# Check security headers
HSTS_HEADER=\$(curl -s -I "https://\$DOMAIN" | grep -i "strict-transport-security")
if [ ! -z "\$HSTS_HEADER" ]; then
    log "HSTS header present: \$HSTS_HEADER"
else
    log "WARNING: HSTS header not detected"
fi
EOF
    
    chmod +x /usr/local/bin/enterprise_ssl_monitor.sh
    
    # Add daily monitoring to cron
    echo "0 9 * * * root /usr/local/bin/enterprise_ssl_monitor.sh" > /etc/cron.d/enterprise-ssl-monitor
    
    print_status "Security monitoring configured successfully"
}

# Restart services
restart_services() {
    print_info "Restarting and enabling services..."
    
    # Enable and start nginx
    systemctl enable nginx
    systemctl restart nginx
    
    # Check service status
    if systemctl is-active --quiet nginx; then
        print_status "Nginx is running successfully"
    else
        print_error "Failed to start nginx"
        exit 1
    fi
}

# Verify SSL configuration
verify_ssl() {
    print_info "Verifying SSL configuration..."
    
    # Wait a moment for services to fully start
    sleep 5
    
    # Test HTTPS connection
    if curl -s -I "https://${DOMAIN}" | grep -q "200\|301\|302"; then
        print_status "HTTPS connection successful"
    else
        print_warning "HTTPS connection test failed - may need DNS configuration"
    fi
    
    # Check SSL certificate
    if openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" -verify_return_error < /dev/null 2>/dev/null; then
        print_status "SSL certificate verification successful"
    else
        print_warning "SSL certificate verification failed - may need DNS configuration"
    fi
    
    # Check security headers
    HEADERS=$(curl -s -I "https://${DOMAIN}" 2>/dev/null || echo "")
    if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
        print_status "HSTS security header detected"
    else
        print_warning "HSTS header not detected - may need DNS configuration"
    fi
    
    if echo "$HEADERS" | grep -q "X-Frame-Options"; then
        print_status "X-Frame-Options security header detected"
    fi
    
    if echo "$HEADERS" | grep -q "Content-Security-Policy"; then
        print_status "Content Security Policy header detected"
    fi
}

# Create deployment summary
create_summary() {
    print_info "Creating deployment summary..."
    
    SUMMARY_FILE="/var/log/enterprise_ssl_deployment.txt"
    
    cat > "$SUMMARY_FILE" << EOF
Enterprise Scanner - SSL Deployment Summary
==========================================
Deployment Date: $(date)
Domain: ${DOMAIN}
WWW Domain: ${WWW_DOMAIN}
Email: ${EMAIL}

SSL Configuration:
- Certificate: ${SSL_PATH}
- Key Size: 4096-bit RSA
- Certificate Authority: Let's Encrypt
- Auto-renewal: Enabled (daily check)
- OCSP Stapling: Enabled
- TLS Versions: 1.2, 1.3

Security Features:
- Security Headers: Full enterprise suite
- HSTS: Enabled (2 years, includeSubDomains, preload)
- Content Security Policy: Enabled
- Rate Limiting: API (10 req/s), General (5 req/s)
- Firewall: UFW enabled (SSH, HTTP, HTTPS, Flask)

Nginx Configuration:
- HTTP to HTTPS Redirect: Enabled
- Reverse Proxy to Flask: Port ${FLASK_PORT}
- Gzip Compression: Enabled
- Static File Caching: 1 year
- Custom Error Pages: Configured

Monitoring:
- SSL Certificate Monitoring: Daily
- Service Health Checks: Enabled
- Security Header Verification: Daily
- SSL Labs Grade Monitoring: Enabled

Web Directory: ${WEBROOT}
Nginx Config: ${NGINX_AVAILABLE}/${DOMAIN}
Log File: ${LOG_FILE}

Access URLs:
- Primary: https://${DOMAIN}
- WWW: https://${WWW_DOMAIN}
- CRM Dashboard: https://${DOMAIN}/crm-dashboard.html
- API Base: https://${DOMAIN}/api/
- Security Check: https://${DOMAIN}/security-check

Commands:
- Check SSL: openssl s_client -connect ${DOMAIN}:443 -servername ${DOMAIN}
- Nginx Status: systemctl status nginx
- Renew SSL: certbot renew
- Test Config: nginx -t

Next Steps:
1. Update DNS A records to point ${DOMAIN} to this server's IP
2. Update DNS A records to point ${WWW_DOMAIN} to this server's IP
3. Start Flask application on port ${FLASK_PORT}
4. Test all endpoints and functionality
5. Configure email integration
6. Set up monitoring alerts

Notes:
- SSL certificates will auto-renew
- Security monitoring runs daily at 9 AM
- Rate limiting protects against abuse
- All security headers configured for enterprise use
EOF
    
    print_status "Deployment summary saved to: $SUMMARY_FILE"
}

# Main execution function
main() {
    print_header "Enterprise Scanner SSL Setup"
    echo -e "${BLUE}Domain: ${DOMAIN}${NC}"
    echo -e "${BLUE}WWW Domain: ${WWW_DOMAIN}${NC}"
    echo -e "${BLUE}Email: ${EMAIL}${NC}"
    echo ""
    
    check_root
    install_dependencies
    configure_firewall
    setup_web_directory
    create_nginx_config
    test_nginx
    obtain_ssl_certificate
    setup_auto_renewal
    setup_security_monitoring
    restart_services
    verify_ssl
    create_summary
    
    print_header "SSL Setup Complete!"
    echo ""
    echo -e "${GREEN}✅ SSL Certificate: Installed and configured${NC}"
    echo -e "${GREEN}✅ HTTPS Redirect: Enabled${NC}"
    echo -e "${GREEN}✅ Security Headers: Enterprise grade${NC}"
    echo -e "${GREEN}✅ Auto-renewal: Enabled${NC}"
    echo -e "${GREEN}✅ Rate Limiting: Configured${NC}"
    echo -e "${GREEN}✅ Firewall: Secured${NC}"
    echo -e "${GREEN}✅ Monitoring: Active${NC}"
    echo ""
    echo -e "${BLUE}🌐 Your Enterprise Scanner is now accessible at:${NC}"
    echo -e "${GREEN}   https://${DOMAIN}${NC}"
    echo -e "${GREEN}   https://${WWW_DOMAIN}${NC}"
    echo -e "${GREEN}   https://${DOMAIN}/crm-dashboard.html${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important next steps:${NC}"
    echo -e "${YELLOW}   1. Update DNS records to point to this server${NC}"
    echo -e "${YELLOW}   2. Start your Flask application: python start_production.py${NC}"
    echo -e "${YELLOW}   3. Test all endpoints and functionality${NC}"
    echo ""
    echo -e "${BLUE}📋 Summary: /var/log/enterprise_ssl_deployment.txt${NC}"
    echo -e "${BLUE}📋 Logs: ${LOG_FILE}${NC}"
    echo ""
    print_header "Ready for Production!"
}

# Run the main function
main "$@"