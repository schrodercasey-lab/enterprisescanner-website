# Production Environment Configuration Script
# Enterprise Scanner - SSL, Security, and Production Settings

"""
Production environment configuration for Enterprise Scanner
Handles SSL certificates, security settings, and production deployment
"""

import os
import sys
import subprocess
import secrets
import string
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_setup.log'),
        logging.StreamHandler()
    ]
)

class ProductionEnvironmentSetup:
    def __init__(self):
        self.domain = 'enterprisescanner.com'
        self.local_domain = 'localhost'
        self.ssl_dir = 'deployment/ssl'
        self.config_dir = 'deployment/configs'
        
    def generate_secure_key(self, length=64):
        """Generate cryptographically secure random key"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_production_env_file(self):
        """Create production environment configuration"""
        try:
            # Generate secure keys
            secret_key = self.generate_secure_key(64)
            api_secret = self.generate_secure_key(32)
            jwt_secret = self.generate_secure_key(32)
            
            production_config = f"""# Enterprise Scanner Production Configuration
# Generated on {datetime.now().isoformat()}
# WARNING: Keep this file secure and never commit to version control

# Application Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# Domain Configuration
DOMAIN_URL=https://{self.domain}
ALLOWED_HOSTS={self.domain},www.{self.domain}

# Database Configuration (Production PostgreSQL)
DATABASE_URL=postgresql://enterprise_user:CHANGE_PASSWORD@localhost:5432/enterprise_scanner
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enterprise_scanner
DB_USER=enterprise_user
DB_PASSWORD=CHANGE_PASSWORD
DB_TYPE=postgresql

# Connection Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True

# Email Configuration (Production Gmail/Google Workspace)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=info@{self.domain}
EMAIL_PASSWORD=CHANGE_EMAIL_PASSWORD
EMAIL_TESTING_MODE=False

# Business Email Addresses
EMAIL_INFO=info@{self.domain}
EMAIL_SALES=sales@{self.domain}
EMAIL_SUPPORT=support@{self.domain}
EMAIL_SECURITY=security@{self.domain}
EMAIL_PARTNERSHIPS=partnerships@{self.domain}

# SSL Configuration
SSL_CERTIFICATE_PATH={self.ssl_dir}/cert.pem
SSL_PRIVATE_KEY_PATH={self.ssl_dir}/private_key.pem
SSL_CHAIN_PATH={self.ssl_dir}/chain.pem
SSL_DHPARAM_PATH={self.ssl_dir}/dhparam.pem

# Security Configuration
SECURITY_HEADERS=True
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=True
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' cdnjs.cloudflare.com
X_FRAME_OPTIONS=DENY
X_CONTENT_TYPE_OPTIONS=nosniff
REFERRER_POLICY=strict-origin-when-cross-origin

# Session Configuration
SESSION_TIMEOUT=3600
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict

# API Configuration
API_SECRET_KEY={api_secret}
API_RATE_LIMIT=1000
API_RATE_LIMIT_WINDOW=3600
API_KEY_EXPIRY_DAYS=365

# Partner Configuration
PARTNER_COMMISSION_BRONZE=25.0
PARTNER_COMMISSION_SILVER=30.0
PARTNER_COMMISSION_GOLD=35.0
PARTNER_APPROVAL_REQUIRED=True

# Monitoring and Logging
LOG_LEVEL=INFO
LOG_FILE=logs/enterprise_scanner.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True
PERFORMANCE_MONITORING=True

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=enterprise-scanner-backups
BACKUP_ENCRYPTION_KEY=CHANGE_BACKUP_KEY

# External Services
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Analytics and Tracking
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
MIXPANEL_TOKEN=CHANGE_MIXPANEL_TOKEN
HOTJAR_ID=CHANGE_HOTJAR_ID

# Payment Processing (for partner commissions)
STRIPE_PUBLISHABLE_KEY=pk_live_CHANGE_STRIPE_KEY
STRIPE_SECRET_KEY=sk_live_CHANGE_STRIPE_SECRET
STRIPE_WEBHOOK_SECRET=whsec_CHANGE_WEBHOOK_SECRET

# Third-party Integrations
SALESFORCE_CLIENT_ID=CHANGE_SALESFORCE_ID
SALESFORCE_CLIENT_SECRET=CHANGE_SALESFORCE_SECRET
HUBSPOT_API_KEY=CHANGE_HUBSPOT_KEY
SLACK_WEBHOOK_URL=CHANGE_SLACK_WEBHOOK

# Production Features
RATE_LIMITING=True
CACHING_ENABLED=True
COMPRESSION_ENABLED=True
MINIFICATION_ENABLED=True
"""
            
            # Write production configuration
            with open('.env.production', 'w') as f:
                f.write(production_config)
            
            logging.info("Production environment configuration created")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create production configuration: {e}")
            return False
    
    def create_ssl_directory_structure(self):
        """Create SSL certificate directory structure"""
        try:
            os.makedirs(self.ssl_dir, exist_ok=True)
            os.makedirs(f"{self.ssl_dir}/backup", exist_ok=True)
            
            # Create SSL configuration template
            ssl_config = f"""# SSL Configuration Template
# Enterprise Scanner SSL Setup

# Certificate Paths
CERT_FILE={self.ssl_dir}/cert.pem
KEY_FILE={self.ssl_dir}/private_key.pem
CHAIN_FILE={self.ssl_dir}/chain.pem
DHPARAM_FILE={self.ssl_dir}/dhparam.pem

# SSL Settings
SSL_PROTOCOLS=TLSv1.2 TLSv1.3
SSL_CIPHERS=ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
SSL_PREFER_SERVER_CIPHERS=on

# Certificate Renewal
CERT_EMAIL=admin@{self.domain}
CERT_DOMAINS={self.domain},www.{self.domain}
"""
            
            with open(f"{self.ssl_dir}/ssl_config.conf", 'w') as f:
                f.write(ssl_config)
            
            logging.info(f"SSL directory structure created: {self.ssl_dir}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create SSL directory: {e}")
            return False
    
    def generate_nginx_config(self):
        """Generate nginx configuration for production"""
        try:
            nginx_config = f"""# Enterprise Scanner Nginx Configuration
# Production deployment with SSL termination

upstream enterprise_scanner {{
    server 127.0.0.1:5000;
    server 127.0.0.1:5001 backup;
}}

# Redirect HTTP to HTTPS
server {{
    listen 80;
    server_name {self.domain} www.{self.domain};
    return 301 https://$server_name$request_uri;
}}

# HTTPS Configuration
server {{
    listen 443 ssl http2;
    server_name {self.domain} www.{self.domain};
    
    # SSL Certificate Configuration
    ssl_certificate {self.ssl_dir}/cert.pem;
    ssl_certificate_key {self.ssl_dir}/private_key.pem;
    ssl_trusted_certificate {self.ssl_dir}/chain.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' cdnjs.cloudflare.com" always;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Client Settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Static Files
    location /static/ {{
        alias /var/www/enterprise_scanner/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # API Endpoints
    location /api/ {{
        proxy_pass http://enterprise_scanner;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Main Application
    location / {{
        proxy_pass http://enterprise_scanner;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Health Check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""
            
            os.makedirs(self.config_dir, exist_ok=True)
            with open(f"{self.config_dir}/nginx.conf", 'w') as f:
                f.write(nginx_config)
            
            logging.info("Nginx configuration generated")
            return True
            
        except Exception as e:
            logging.error(f"Failed to generate nginx config: {e}")
            return False
    
    def create_systemd_service(self):
        """Create systemd service for production deployment"""
        try:
            service_config = f"""[Unit]
Description=Enterprise Scanner - Cybersecurity Platform
After=network.target postgresql.service redis.service
Requires=postgresql.service

[Service]
Type=exec
User=enterprise_scanner
Group=enterprise_scanner
WorkingDirectory=/opt/enterprise_scanner
Environment=PATH=/opt/enterprise_scanner/venv/bin
EnvironmentFile=/opt/enterprise_scanner/.env.production
ExecStart=/opt/enterprise_scanner/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --worker-class gevent --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100 --timeout 30 --keep-alive 5 --preload backend.app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=enterprise_scanner

[Install]
WantedBy=multi-user.target
"""
            
            with open(f"{self.config_dir}/enterprise-scanner.service", 'w') as f:
                f.write(service_config)
            
            logging.info("Systemd service configuration created")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create systemd service: {e}")
            return False
    
    def generate_ssl_certificate_script(self):
        """Generate SSL certificate acquisition script"""
        try:
            ssl_script = f"""#!/bin/bash
# SSL Certificate Setup for Enterprise Scanner
# Uses Let's Encrypt Certbot for free SSL certificates

set -e

DOMAIN="{self.domain}"
EMAIL="admin@{self.domain}"
SSL_DIR="{self.ssl_dir}"

echo "🔒 Setting up SSL certificates for Enterprise Scanner"
echo "Domain: $DOMAIN"
echo "SSL Directory: $SSL_DIR"

# Install Certbot (Ubuntu/Debian)
if command -v apt-get >/dev/null 2>&1; then
    echo "Installing Certbot on Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y snapd
    sudo snap install core; sudo snap refresh core
    sudo snap install --classic certbot
    sudo ln -sf /snap/bin/certbot /usr/bin/certbot
fi

# Install Certbot (CentOS/RHEL)
if command -v yum >/dev/null 2>&1; then
    echo "Installing Certbot on CentOS/RHEL..."
    sudo yum install -y epel-release
    sudo yum install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily for certificate generation
sudo systemctl stop nginx || true

# Generate certificate
echo "Generating SSL certificate..."
sudo certbot certonly --standalone \\
    --email $EMAIL \\
    --agree-tos \\
    --no-eff-email \\
    -d $DOMAIN \\
    -d www.$DOMAIN

# Copy certificates to application directory
echo "Copying certificates to application directory..."
sudo mkdir -p $SSL_DIR
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/private_key.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/chain.pem $SSL_DIR/chain.pem

# Generate DH parameters
echo "Generating DH parameters..."
sudo openssl dhparam -out $SSL_DIR/dhparam.pem 2048

# Set appropriate permissions
sudo chown -R enterprise_scanner:enterprise_scanner $SSL_DIR
sudo chmod 600 $SSL_DIR/private_key.pem
sudo chmod 644 $SSL_DIR/cert.pem $SSL_DIR/chain.pem $SSL_DIR/dhparam.pem

# Setup automatic renewal
echo "Setting up automatic certificate renewal..."
sudo crontab -l | {{ cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; }} | sudo crontab -

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

echo "✅ SSL certificates configured successfully!"
echo "Certificate location: $SSL_DIR"
echo "Auto-renewal configured via cron"
"""
            
            with open(f"{self.config_dir}/setup_ssl.sh", 'w', encoding='utf-8') as f:
                f.write(ssl_script)
            
            # Make script executable
            os.chmod(f"{self.config_dir}/setup_ssl.sh", 0o755)
            
            logging.info("SSL certificate setup script created")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create SSL script: {e}")
            return False
    
    def create_deployment_script(self):
        """Create complete production deployment script"""
        try:
            deployment_script = f"""#!/bin/bash
# Enterprise Scanner Production Deployment Script
# Complete setup for production environment

set -e

echo "🚀 Enterprise Scanner Production Deployment"
echo "=========================================="

# Configuration
DOMAIN="{self.domain}"
APP_USER="enterprise_scanner"
APP_DIR="/opt/enterprise_scanner"
SSL_DIR="{self.ssl_dir}"

# Create application user
echo "Creating application user..."
sudo useradd -r -s /bin/bash -d $APP_DIR $APP_USER || true

# Create application directory
echo "Creating application directory..."
sudo mkdir -p $APP_DIR
sudo mkdir -p $APP_DIR/logs
sudo mkdir -p $APP_DIR/backups

# Copy application files
echo "Copying application files..."
sudo cp -r . $APP_DIR/
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Create Python virtual environment
echo "Setting up Python virtual environment..."
sudo -u $APP_USER python3 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
sudo -u $APP_USER $APP_DIR/venv/bin/pip install gunicorn gevent

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y nginx postgresql postgresql-contrib redis-server

# Setup PostgreSQL
echo "Setting up PostgreSQL..."
sudo -u postgres createuser $APP_USER || true
sudo -u postgres createdb enterprise_scanner || true
sudo -u postgres psql -c "ALTER USER $APP_USER PASSWORD 'CHANGE_PASSWORD';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE enterprise_scanner TO $APP_USER;" || true

# Run database migration
echo "Running database migration..."
sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/deployment/scripts/setup_postgresql.py

# Install SSL certificates
echo "Setting up SSL certificates..."
bash $APP_DIR/{self.config_dir}/setup_ssl.sh

# Configure Nginx
echo "Configuring Nginx..."
sudo cp $APP_DIR/{self.config_dir}/nginx.conf /etc/nginx/sites-available/enterprise_scanner
sudo ln -sf /etc/nginx/sites-available/enterprise_scanner /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Install systemd service
echo "Installing systemd service..."
sudo cp $APP_DIR/{self.config_dir}/enterprise-scanner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable enterprise-scanner

# Start services
echo "Starting services..."
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl start enterprise-scanner
sudo systemctl start nginx

# Setup firewall
echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "✅ Production deployment completed!"
echo "Application URL: https://$DOMAIN"
echo "Health Check: https://$DOMAIN/api/health"
echo ""
echo "Next steps:"
echo "1. Update .env.production with your actual passwords and API keys"
echo "2. Configure your domain DNS to point to this server"
echo "3. Test the application: https://$DOMAIN"
echo "4. Monitor logs: sudo journalctl -u enterprise-scanner -f"
"""
            
            with open(f"{self.config_dir}/deploy_production.sh", 'w', encoding='utf-8') as f:
                f.write(deployment_script)
            
            # Make script executable
            os.chmod(f"{self.config_dir}/deploy_production.sh", 0o755)
            
            logging.info("Production deployment script created")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create deployment script: {e}")
            return False
    
    def setup_production_environment(self):
        """Complete production environment setup"""
        logging.info("Starting production environment configuration...")
        
        success = True
        
        # Create production configuration
        if not self.create_production_env_file():
            success = False
        
        # Create SSL directory structure
        if not self.create_ssl_directory_structure():
            success = False
        
        # Generate nginx configuration
        if not self.generate_nginx_config():
            success = False
        
        # Create systemd service
        if not self.create_systemd_service():
            success = False
        
        # Generate SSL setup script
        if not self.generate_ssl_certificate_script():
            success = False
        
        # Create deployment script
        if not self.create_deployment_script():
            success = False
        
        return success
    
    def print_production_checklist(self):
        """Print production deployment checklist"""
        checklist = f"""
🔐 Enterprise Scanner Production Environment Configuration Complete!

📋 PRODUCTION DEPLOYMENT CHECKLIST:

1. CONFIGURATION FILES CREATED:
   ✅ .env.production - Production environment variables
   ✅ {self.config_dir}/nginx.conf - Nginx reverse proxy configuration
   ✅ {self.config_dir}/enterprise-scanner.service - Systemd service
   ✅ {self.config_dir}/setup_ssl.sh - SSL certificate setup script
   ✅ {self.config_dir}/deploy_production.sh - Complete deployment script

2. REQUIRED UPDATES BEFORE DEPLOYMENT:
   🔧 Edit .env.production and update:
      - DB_PASSWORD (PostgreSQL password)
      - EMAIL_PASSWORD (Gmail/Google Workspace password)
      - All API keys and secrets marked with CHANGE_*
   
3. DOMAIN CONFIGURATION:
   🌐 Point {self.domain} DNS to your production server IP
   🌐 Ensure www.{self.domain} also points to the same IP
   
4. PRODUCTION DEPLOYMENT:
   🚀 Run: sudo bash {self.config_dir}/deploy_production.sh
   
5. POST-DEPLOYMENT VERIFICATION:
   ✅ Test: https://{self.domain}
   ✅ Health check: https://{self.domain}/api/health
   ✅ CRM dashboard: https://{self.domain}/crm-dashboard.html
   ✅ SSL certificate: https://www.ssllabs.com/ssltest/

6. MONITORING AND MAINTENANCE:
   📊 Monitor logs: sudo journalctl -u enterprise-scanner -f
   📊 Check status: sudo systemctl status enterprise-scanner
   📊 Nginx status: sudo systemctl status nginx
   📊 Database status: sudo systemctl status postgresql

7. BUSINESS CONFIGURATION:
   💼 Update Google Workspace email settings
   💼 Configure partner commission payments
   💼 Set up analytics tracking (Google Analytics, etc.)
   💼 Configure backup and monitoring systems

🔒 SECURITY NOTES:
- All sensitive data is stored in .env.production
- SSL certificates will auto-renew via Let's Encrypt
- Security headers are configured for maximum protection
- Database access is restricted to localhost only

📈 PERFORMANCE OPTIMIZATIONS:
- Nginx reverse proxy with compression
- Gunicorn WSGI server with 4 workers
- PostgreSQL connection pooling
- Static file caching and optimization

Enterprise Scanner is now ready for production deployment! 🚀
"""
        print(checklist)
        logging.info("Production deployment checklist provided")

def main():
    """Main setup function"""
    print("🔧 Enterprise Scanner Production Environment Configuration")
    print("=" * 60)
    
    setup = ProductionEnvironmentSetup()
    
    if setup.setup_production_environment():
        setup.print_production_checklist()
        return 0
    else:
        print("\n❌ Production environment setup failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())