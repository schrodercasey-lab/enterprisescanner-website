#!/bin/bash

# Enterprise Scanner Security Hardening Script
# Option B: Comprehensive Server Security
# Date: October 16, 2025

set -e  # Exit on error

echo "=========================================="
echo "  ENTERPRISE SCANNER SECURITY HARDENING  "
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: Keep this SSH session open!"
echo "    Use DigitalOcean console as backup access"
echo ""
echo "This script will:"
echo "  1. Configure UFW firewall"
echo "  2. Install and configure fail2ban"
echo "  3. Add Nginx security headers"
echo "  4. Enable automatic security updates"
echo "  5. Implement API rate limiting"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."

# ============================================
# TASK 1: CONFIGURE UFW FIREWALL
# ============================================

echo ""
echo "=== Task 1: Configuring UFW Firewall ==="
echo ""

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    echo "Installing UFW..."
    apt-get update -qq
    apt-get install -y ufw
fi

# Reset UFW to default
echo "Resetting UFW to defaults..."
ufw --force reset

# Set default policies
echo "Setting default policies (deny incoming, allow outgoing)..."
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (current port 22 - we'll change this later)
echo "Allowing SSH (port 22)..."
ufw allow 22/tcp comment 'SSH'

# Allow HTTP (will redirect to HTTPS)
echo "Allowing HTTP (port 80)..."
ufw allow 80/tcp comment 'HTTP'

# Allow HTTPS
echo "Allowing HTTPS (port 443)..."
ufw allow 443/tcp comment 'HTTPS'

# Enable UFW
echo "Enabling UFW firewall..."
ufw --force enable

echo "✓ UFW Firewall configured and enabled"
ufw status verbose

# ============================================
# TASK 2: INSTALL FAIL2BAN
# ============================================

echo ""
echo "=== Task 2: Installing fail2ban Protection ==="
echo ""

# Install fail2ban
if ! command -v fail2ban-client &> /dev/null; then
    echo "Installing fail2ban..."
    apt-get install -y fail2ban
fi

# Create fail2ban configuration
echo "Configuring fail2ban jails..."

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# Ban for 10 minutes
bantime = 600
# Check for failures in last 10 minutes
findtime = 600
# Ban after 5 failures
maxretry = 5
# Email notifications (optional)
destemail = security@enterprisescanner.com
sender = fail2ban@enterprisescanner.com

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

# Restart fail2ban
echo "Restarting fail2ban..."
systemctl restart fail2ban
systemctl enable fail2ban

echo "✓ fail2ban installed and configured"
fail2ban-client status

# ============================================
# TASK 3: ADD NGINX SECURITY HEADERS
# ============================================

echo ""
echo "=== Task 3: Adding Nginx Security Headers ==="
echo ""

# Backup current config
cp /etc/nginx/sites-available/enterprisescanner /etc/nginx/sites-available/enterprisescanner.backup-security

# Create updated config with security headers
cat > /etc/nginx/sites-available/enterprisescanner << 'EOF'
server {
    listen 80;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # SSL certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/enterprisescanner.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src 'self' data: https:; connect-src 'self';" always;
    
    # Remove server version from headers
    server_tokens off;
    
    root /opt/enterprisescanner/website;
    index index.html;
    
    # Main website
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API Endpoints with rate limiting
    location /api/chat/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/analytics/ {
        proxy_pass http://127.0.0.1:5003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/assessment/ {
        proxy_pass http://127.0.0.1:5002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/docs/ {
        proxy_pass http://127.0.0.1:5004/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/partners/ {
        proxy_pass http://127.0.0.1:5005/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/onboarding/ {
        proxy_pass http://127.0.0.1:5006/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/monitoring/ {
        proxy_pass http://127.0.0.1:5007/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Reloading Nginx..."
    systemctl reload nginx
    echo "✓ Security headers added to Nginx"
else
    echo "✗ Nginx configuration error, restoring backup..."
    cp /etc/nginx/sites-available/enterprisescanner.backup-security /etc/nginx/sites-available/enterprisescanner
    exit 1
fi

# ============================================
# TASK 4: ENABLE AUTOMATIC SECURITY UPDATES
# ============================================

echo ""
echo "=== Task 4: Enabling Automatic Security Updates ==="
echo ""

# Install unattended-upgrades
if ! dpkg -l | grep -q unattended-upgrades; then
    echo "Installing unattended-upgrades..."
    apt-get install -y unattended-upgrades apt-listchanges
fi

# Configure automatic updates
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";
EOF

# Enable automatic updates
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

echo "✓ Automatic security updates enabled"

# ============================================
# TASK 5: IMPLEMENT API RATE LIMITING
# ============================================

echo ""
echo "=== Task 5: Implementing API Rate Limiting ==="
echo ""

# Add rate limiting to main nginx.conf
if ! grep -q "limit_req_zone" /etc/nginx/nginx.conf; then
    echo "Adding rate limiting configuration..."
    
    # Backup nginx.conf
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup-security
    
    # Add rate limiting in http block
    sed -i '/http {/a \    # Rate limiting zones\n    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;\n    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=50r/s;\n    limit_req_status 429;' /etc/nginx/nginx.conf
    
    echo "✓ Rate limiting zones added"
else
    echo "✓ Rate limiting already configured"
fi

# Update site config to use rate limiting
sed -i '/location \/api\//a \        limit_req zone=api_limit burst=20 nodelay;' /etc/nginx/sites-available/enterprisescanner

# Test and reload
nginx -t && systemctl reload nginx

echo "✓ API rate limiting implemented"

# ============================================
# SUMMARY
# ============================================

echo ""
echo "=========================================="
echo "  SECURITY HARDENING COMPLETE!           "
echo "=========================================="
echo ""
echo "✓ UFW Firewall: Active (ports 22, 80, 443)"
echo "✓ fail2ban: Active and monitoring"
echo "✓ Security Headers: Implemented"
echo "✓ Automatic Updates: Enabled"
echo "✓ Rate Limiting: Active on APIs"
echo ""
echo "=== Next Steps ==="
echo "1. Review firewall rules: ufw status"
echo "2. Check fail2ban status: fail2ban-client status"
echo "3. Test security headers: curl -I https://enterprisescanner.com"
echo "4. Optional: Run full security audit"
echo ""
echo "⚠️  SSH Hardening (Task 3) skipped in automated script"
echo "    To complete SSH hardening manually:"
echo "    - Change SSH port in /etc/ssh/sshd_config"
echo "    - Disable root login"
echo "    - Disable password authentication"
echo "    - Update UFW rules for new port"
echo ""
echo "Security hardening completed successfully!"
echo "=========================================="
