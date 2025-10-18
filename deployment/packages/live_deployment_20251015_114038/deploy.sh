#!/bin/bash
# Enterprise Scanner - Production Startup Script

echo "Starting Enterprise Scanner Production Deployment..."

# Update system packages
sudo apt update

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx

# Create application directory
sudo mkdir -p /var/www/enterprisescanner.com
sudo chown -R $USER:$USER /var/www/enterprisescanner.com

# Copy application files
cp -r backend /var/www/enterprisescanner.com/
cp -r website /var/www/enterprisescanner.com/
cp requirements.txt /var/www/enterprisescanner.com/

# Create virtual environment
cd /var/www/enterprisescanner.com
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p backend/logs
touch backend/logs/security_events.log

# Setup systemd service
sudo tee /etc/systemd/system/enterprise-scanner.service > /dev/null <<EOF
[Unit]
Description=Enterprise Scanner Flask Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/www/enterprisescanner.com
Environment=PATH=/var/www/enterprisescanner.com/venv/bin
ExecStart=/var/www/enterprisescanner.com/venv/bin/python backend/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx configuration
sudo tee /etc/nginx/sites-available/enterprisescanner.com > /dev/null <<EOF
server {
    listen 80;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    ssl_certificate /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/enterprisescanner.com/privkey.pem;
    
    # Website files
    location / {
        root /var/www/enterprisescanner.com/website;
        index index.html;
        try_files \$uri \$uri/ =404;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/enterprisescanner.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start services
sudo systemctl daemon-reload
sudo systemctl enable enterprise-scanner
sudo systemctl start enterprise-scanner

echo "Enterprise Scanner deployed successfully!"
echo "Access at: https://enterprisescanner.com"
echo "API available at: https://enterprisescanner.com/api/"
