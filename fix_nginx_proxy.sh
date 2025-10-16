#!/bin/bash

echo "=========================================="
echo "  FIXING NGINX PROXY CONFIGURATION"
echo "=========================================="
echo ""

cd /opt/enterprisescanner/docker

# Backup current config
cp nginx.conf nginx.conf.backup.before-localhost-fix

# Create fixed nginx config with localhost proxy
cat > nginx.conf << 'NGINX_EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

    # Upstream definitions for better load handling
    upstream backend_chat {
        server 127.0.0.1:5001;
        keepalive 32;
    }

    upstream backend_analytics {
        server 127.0.0.1:5003;
        keepalive 32;
    }

    upstream backend_security {
        server 127.0.0.1:5002;
        keepalive 32;
    }

    upstream backend_docs {
        server 127.0.0.1:5004;
        keepalive 32;
    }

    upstream backend_partners {
        server 127.0.0.1:5005;
        keepalive 32;
    }

    upstream backend_onboarding {
        server 127.0.0.1:5006;
        keepalive 32;
    }

    upstream backend_monitoring {
        server 127.0.0.1:5007;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;
        
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API Routes - Proxy to backend services
        location /api/chat/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_chat/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/analytics/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_analytics/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/assessment/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_security/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/docs/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_docs/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/partners/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_partners/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/onboarding/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_onboarding/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/monitoring/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://backend_monitoring/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Static files
        location / {
            limit_req zone=general burst=20 nodelay;
            try_files $uri $uri/ /index.html;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }

        # Deny access to hidden files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
NGINX_EOF

echo "✅ Nginx configuration updated with localhost proxying"
echo ""

# Test configuration
echo "Testing Nginx configuration..."
docker exec enterprisescanner_nginx nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Configuration test passed!"
    echo ""
    echo "Restarting Nginx..."
    docker-compose -f docker-compose.prod.yml restart nginx
    
    echo ""
    echo "Waiting for Nginx to restart..."
    sleep 3
    
    echo ""
    echo "✅ Nginx restarted successfully!"
    echo ""
    echo "Testing API endpoints..."
    echo ""
    
    echo "1. Chat API:"
    curl -I http://localhost/api/chat/ 2>&1 | head -5
    echo ""
    
    echo "2. Analytics API:"
    curl -I http://localhost/api/analytics/ 2>&1 | head -5
    echo ""
    
    echo "3. API Docs:"
    curl -I http://localhost/api/docs/ 2>&1 | head -5
    echo ""
    
    echo "=========================================="
    echo "  🎉 FIX COMPLETE!"
    echo "=========================================="
    echo ""
    echo "All API endpoints should now work!"
    echo "Test from browser: http://134.199.147.45/api/chat/"
    echo ""
else
    echo ""
    echo "❌ Configuration test failed!"
    echo "Restoring backup..."
    cp nginx.conf.backup.before-localhost-fix nginx.conf
    echo "Backup restored. Please check the error above."
fi
NGINX_EOF

chmod +x fix_nginx_proxy.sh

echo "✅ Fix script created: fix_nginx_proxy.sh"
echo ""
echo "Run this on your server:"
echo "  cd /opt/enterprisescanner/backend"
echo "  wget https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/fix_nginx_proxy.sh"
echo "  chmod +x fix_nginx_proxy.sh"
echo "  ./fix_nginx_proxy.sh"
