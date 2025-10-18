#!/bin/bash
# Enterprise Scanner - Production Deployment Script
# Generated: 2025-10-15 11:45:00

set -e  # Exit on any error

echo "Starting Enterprise Scanner Live Security Assessment Tool Deployment..."
echo "Target: enterprisescanner.com"
echo "Package: enterprise_scanner_live_20251015_114038.tar.gz"

# Create deployment directory
DEPLOY_DIR="/var/www/enterprisescanner.com"
TEMP_DIR="/tmp/enterprise_scanner_deploy"

echo "Setting up deployment environment..."
sudo mkdir -p $DEPLOY_DIR
sudo chown -R $USER:$USER $DEPLOY_DIR

# Extract deployment package
cd /tmp
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR
cd $TEMP_DIR

echo "Extracting deployment package..."
tar -xzf /tmp/enterprise_scanner_live_20251015_114038.tar.gz
cd live_deployment_*

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "Setting up application..."
# Copy application files
cp -r backend $DEPLOY_DIR/
cp -r website $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/

# Create virtual environment
cd $DEPLOY_DIR
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p backend/logs
touch backend/logs/security_events.log
chmod 664 backend/logs/security_events.log

echo "Configuring systemd service..."
sudo tee /etc/systemd/system/enterprise-scanner.service > /dev/null <<EOF
[Unit]
Description=Enterprise Scanner Flask Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$DEPLOY_DIR
Environment=PATH=$DEPLOY_DIR/venv/bin
Environment=FLASK_ENV=production
ExecStart=$DEPLOY_DIR/venv/bin/python backend/app.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/enterprisescanner.com > /dev/null <<EOF
server {
    listen 80;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # Temporary allow HTTP for SSL setup
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect other HTTP to HTTPS after SSL is configured
    location / {
        return 301 https://\$$server_name\$$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # SSL configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/enterprisescanner.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Website files
    location / {
        root $DEPLOY_DIR/website;
        index index.html;
        try_files \$$uri \$$uri/ =404;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \$$host;
        proxy_set_header X-Real-IP \$$remote_addr;
        proxy_set_header X-Forwarded-For \$$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/enterprisescanner.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable enterprise-scanner
sudo systemctl start enterprise-scanner
sudo systemctl reload nginx

echo "Configuring SSL certificates..."
sudo certbot --nginx -d enterprisescanner.com -d www.enterprisescanner.com --non-interactive --agree-tos --email admin@enterprisescanner.com

echo "Final service restart with SSL..."
sudo systemctl restart nginx
sudo systemctl restart enterprise-scanner

echo "Deployment completed successfully!"
echo ""
echo "=== ENTERPRISE SCANNER DEPLOYED ==="
echo "Website: https://enterprisescanner.com"
echo "Security Assessment: https://enterprisescanner.com/security-assessment.html"
echo "API Health: https://enterprisescanner.com/api/health"
echo ""
echo "Next steps:"
echo "1. Generate production API key"
echo "2. Test security assessment workflow"
echo "3. Configure email automation"
echo ""

# Test deployment
sleep 5
echo "Testing deployment..."
curl -I https://enterprisescanner.com/ || echo "Website test failed"
echo "Deployment script completed."
