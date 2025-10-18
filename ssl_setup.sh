#!/bin/bash

echo "🔒 Starting SSL Certificate Setup for enterprisescanner.com"
echo "============================================="

# Step 1: Install Certbot
echo "📦 Step 1: Installing Certbot"
apt update -y
apt install -y certbot python3-certbot-nginx

# Step 2: Stop Nginx temporarily
echo "⏸️  Step 2: Stopping Nginx temporarily"
systemctl stop nginx

# Step 3: Generate SSL Certificate
echo "🔐 Step 3: Generating SSL Certificate"
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@enterprisescanner.com \
    -d enterprisescanner.com \
    -d www.enterprisescanner.com

# Step 4: Configure Nginx for SSL
echo "⚙️  Step 4: Configuring Nginx for SSL"
cat > /etc/nginx/sites-available/default << 'NGINX_CONFIG_END'
server {
    listen 80;
    server_name enterprisescanner.com www.enterprisescanner.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    root /var/www/html;
    index index.html index.htm;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/enterprisescanner.com/privkey.pem;
    
    # Modern SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Cache static assets
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_CONFIG_END

# Step 5: Test and reload Nginx
echo "🧪 Step 5: Testing Nginx configuration"
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    systemctl start nginx
    systemctl reload nginx
else
    echo "❌ Nginx configuration error - please check"
    exit 1
fi

# Step 6: Set up auto-renewal
echo "🔄 Step 6: Setting up SSL auto-renewal"
crontab -l > current_cron 2>/dev/null || true
echo "0 12 * * * /usr/bin/certbot renew --quiet" >> current_cron
crontab current_cron
rm current_cron

# Step 7: Test auto-renewal
echo "🧪 Step 7: Testing auto-renewal"
certbot renew --dry-run

echo ""
echo "============================================="
echo "🎉 SSL SETUP COMPLETED SUCCESSFULLY!"
echo "✅ HTTPS is now enabled for enterprisescanner.com"
echo "✅ HTTP automatically redirects to HTTPS"
echo "✅ Auto-renewal is configured"
echo "🔒 Your site is now secure!"
echo "============================================="

# Final verification
echo "🔍 Final verification:"
echo "HTTP Status:"
curl -I http://enterprisescanner.com 2>/dev/null | head -1
echo "HTTPS Status:"
curl -I https://enterprisescanner.com 2>/dev/null | head -1
echo ""
echo "🚀 Visit https://enterprisescanner.com to see your secure site!"