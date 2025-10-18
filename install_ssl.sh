#!/bin/bash

echo "=== SSL Certificate Installation ==="
echo "Updating Nginx configuration with domain name..."

# Backup current config
cp /etc/nginx/sites-available/enterprisescanner /etc/nginx/sites-available/enterprisescanner.backup

# Create new config with proper server_name
cat > /etc/nginx/sites-available/enterprisescanner << 'EOF'
server {
    listen 80;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    root /opt/enterprisescanner/website;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API Endpoints
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

echo "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
    
    echo "Reloading Nginx..."
    systemctl reload nginx
    
    echo "Installing SSL certificate..."
    certbot install --cert-name enterprisescanner.com --nginx
    
    echo ""
    echo "=== Verification ==="
    echo "Testing HTTPS connection..."
    sleep 2
    curl -I https://enterprisescanner.com
    
    echo ""
    echo "Testing HTTP redirect..."
    curl -I http://enterprisescanner.com
    
    echo ""
    echo "=== SSL Certificate Info ==="
    certbot certificates
else
    echo "✗ Nginx configuration has errors"
    echo "Restoring backup..."
    cp /etc/nginx/sites-available/enterprisescanner.backup /etc/nginx/sites-available/enterprisescanner
    exit 1
fi
