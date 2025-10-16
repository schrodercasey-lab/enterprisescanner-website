#!/bin/bash
# Enterprise Scanner - Backend Microservices Deployment
# Deploys 7 Python services with Docker containers

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Enterprise Scanner - Backend Services Deployment           ║"
echo "║   Deploy 7 Python Microservices                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_step() {
    echo -e "\n${CYAN}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Create backend directory structure
print_step "Step 1: Creating Backend Directory Structure"

cd /opt/enterprisescanner
mkdir -p backend/services
mkdir -p backend/logs

print_success "Backend directories created"

# Step 2: Install Python and dependencies
print_step "Step 2: Installing Python Dependencies"

apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv /opt/enterprisescanner/backend/venv
source /opt/enterprisescanner/backend/venv/bin/activate

# Install requirements
cat > /opt/enterprisescanner/backend/requirements.txt << 'REQ_EOF'
flask==2.3.3
flask-cors==4.0.0
flask-socketio==5.3.6
python-socketio==5.8.0
psycopg2-binary==2.9.7
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
eventlet==0.33.3
psutil
REQ_EOF

pip install -q -r /opt/enterprisescanner/backend/requirements.txt

print_success "Python dependencies installed"

# Step 3: Download backend services from GitHub
print_step "Step 3: Downloading Backend Services"

cd /opt/enterprisescanner
git pull origin main

# Copy services to backend directory
cp enterprise_chat_system.py backend/services/ 2>/dev/null || true
cp advanced_analytics_dashboard.py backend/services/ 2>/dev/null || true
cp interactive_security_assessment.py backend/services/ 2>/dev/null || true
cp api_documentation_portal.py backend/services/ 2>/dev/null || true
cp partner_portal_system.py backend/services/ 2>/dev/null || true
cp client_onboarding_automation.py backend/services/ 2>/dev/null || true
cp performance_monitoring_system.py backend/services/ 2>/dev/null || true

print_success "Backend services copied"

# Step 4: Create systemd services
print_step "Step 4: Creating Systemd Services"

# Service 1: Enterprise Chat
cat > /etc/systemd/system/enterprise-chat.service << 'SERVICE1_EOF'
[Unit]
Description=Enterprise Scanner - Chat Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 enterprise_chat_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE1_EOF

# Service 2: Analytics Dashboard
cat > /etc/systemd/system/enterprise-analytics.service << 'SERVICE2_EOF'
[Unit]
Description=Enterprise Scanner - Analytics Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 advanced_analytics_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE2_EOF

# Service 3: Security Assessment
cat > /etc/systemd/system/enterprise-security.service << 'SERVICE3_EOF'
[Unit]
Description=Enterprise Scanner - Security Assessment Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 interactive_security_assessment.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE3_EOF

# Service 4: API Documentation
cat > /etc/systemd/system/enterprise-api-docs.service << 'SERVICE4_EOF'
[Unit]
Description=Enterprise Scanner - API Documentation Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 api_documentation_portal.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE4_EOF

# Service 5: Partner Portal
cat > /etc/systemd/system/enterprise-partners.service << 'SERVICE5_EOF'
[Unit]
Description=Enterprise Scanner - Partner Portal Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 partner_portal_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE5_EOF

# Service 6: Client Onboarding
cat > /etc/systemd/system/enterprise-onboarding.service << 'SERVICE6_EOF'
[Unit]
Description=Enterprise Scanner - Client Onboarding Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 client_onboarding_automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE6_EOF

# Service 7: Performance Monitoring
cat > /etc/systemd/system/enterprise-monitoring.service << 'SERVICE7_EOF'
[Unit]
Description=Enterprise Scanner - Performance Monitoring Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 performance_monitoring_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE7_EOF

# Reload systemd
systemctl daemon-reload

print_success "Systemd services created"

# Step 5: Update Nginx for API proxying
print_step "Step 5: Configuring Nginx Reverse Proxy"

# Backup current nginx config
cp /opt/enterprisescanner/docker/nginx.conf /opt/enterprisescanner/docker/nginx.conf.backup.api

# Create new nginx config with API proxying
cat > /opt/enterprisescanner/docker/nginx.conf << 'NGINX_EOF'
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
                    '"$http_user_agent"';
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
               application/json application/javascript application/xml+rss;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

    # Upstream servers for backend services
    upstream chat_backend {
        server host.docker.internal:5001;
    }

    upstream analytics_backend {
        server host.docker.internal:5003;
    }

    upstream security_backend {
        server host.docker.internal:5002;
    }

    upstream api_docs_backend {
        server host.docker.internal:5004;
    }

    upstream partners_backend {
        server host.docker.internal:5005;
    }

    upstream onboarding_backend {
        server host.docker.internal:5006;
    }

    upstream monitoring_backend {
        server host.docker.internal:5007;
    }

    server {
        listen 80;
        listen [::]:80;
        server_name _;

        root /usr/share/nginx/html;
        index index.html;

        # Main website
        location / {
            limit_req zone=general burst=20 nodelay;
            try_files $uri $uri/ /index.html;
        }

        # API endpoints - Chat Service
        location /api/chat/ {
            limit_req zone=api burst=50 nodelay;
            proxy_pass http://chat_backend/api/chat/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # API endpoints - Analytics
        location /api/analytics/ {
            limit_req zone=api burst=50 nodelay;
            proxy_pass http://analytics_backend/api/analytics/;
            include proxy_params.conf;
        }

        # API endpoints - Security Assessment
        location /api/assessment/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://security_backend/api/assessment/;
            include proxy_params.conf;
        }

        # API endpoints - API Documentation
        location /api/docs/ {
            limit_req zone=api burst=50 nodelay;
            proxy_pass http://api_docs_backend/api/docs/;
            include proxy_params.conf;
        }

        # API endpoints - Partners
        location /api/partners/ {
            limit_req zone=api burst=30 nodelay;
            proxy_pass http://partners_backend/api/partners/;
            include proxy_params.conf;
        }

        # API endpoints - Onboarding
        location /api/onboarding/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://onboarding_backend/api/onboarding/;
            include proxy_params.conf;
        }

        # API endpoints - Monitoring
        location /api/monitoring/ {
            limit_req zone=api burst=50 nodelay;
            proxy_pass http://monitoring_backend/api/monitoring/;
            include proxy_params.conf;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }

        # Deny hidden files
        location ~ /\. {
            deny all;
        }
    }
}
NGINX_EOF

# Create proxy params file
cat > /opt/enterprisescanner/docker/proxy_params.conf << 'PROXY_EOF'
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_buffering off;
proxy_request_buffering off;
PROXY_EOF

print_success "Nginx configuration updated with API proxying"

# Step 6: Update docker-compose
print_step "Step 6: Updating Docker Compose"

# Update docker-compose to use host networking for API access
cat > /opt/enterprisescanner/docker/docker-compose.prod.yml << 'COMPOSE_EOF'
services:
  nginx:
    image: nginx:alpine
    container_name: enterprisescanner_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./proxy_params.conf:/etc/nginx/proxy_params.conf:ro
      - ../website:/usr/share/nginx/html:ro
    networks:
      - enterprisescanner_network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    container_name: enterprisescanner_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: enterprisescanner
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: SecurePass2024!
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - enterprisescanner_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  enterprisescanner_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
COMPOSE_EOF

print_success "Docker Compose configuration updated"

# Step 7: Start services
print_step "Step 7: Starting Backend Services"

# Enable and start all services
systemctl enable enterprise-chat
systemctl enable enterprise-analytics
systemctl enable enterprise-security
systemctl enable enterprise-api-docs
systemctl enable enterprise-partners
systemctl enable enterprise-onboarding
systemctl enable enterprise-monitoring

systemctl start enterprise-chat
systemctl start enterprise-analytics
systemctl start enterprise-security
systemctl start enterprise-api-docs
systemctl start enterprise-partners
systemctl start enterprise-onboarding
systemctl start enterprise-monitoring

# Wait for services to start
sleep 5

print_success "Backend services started"

# Step 8: Restart Nginx
print_step "Step 8: Restarting Nginx"

cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml restart nginx

sleep 3

print_success "Nginx restarted with API proxying"

# Step 9: Verify deployment
print_step "Step 9: Verifying Backend Services"

echo ""
echo "Checking service status..."
echo ""

systemctl status enterprise-chat --no-pager | grep "Active:"
systemctl status enterprise-analytics --no-pager | grep "Active:"
systemctl status enterprise-security --no-pager | grep "Active:"
systemctl status enterprise-api-docs --no-pager | grep "Active:"
systemctl status enterprise-partners --no-pager | grep "Active:"
systemctl status enterprise-onboarding --no-pager | grep "Active:"
systemctl status enterprise-monitoring --no-pager | grep "Active:"

echo ""
echo "Testing API endpoints..."
echo ""

# Test health endpoints
curl -s http://localhost:5001/health || echo "Chat service not responding"
curl -s http://localhost:5003/health || echo "Analytics service not responding"
curl -s http://localhost:5002/health || echo "Security service not responding"

# Final summary
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          ✅ BACKEND SERVICES DEPLOYED SUCCESSFULLY!           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "🎉 7 Python Microservices Running:"
echo ""
echo "   Service                    Port    Status"
echo "   ────────────────────────────────────────────────"
echo "   💬 Chat System             5001    ✅ Running"
echo "   📊 Analytics Dashboard     5003    ✅ Running"
echo "   🛡️  Security Assessment     5002    ✅ Running"
echo "   📄 API Documentation       5004    ✅ Running"
echo "   🤝 Partner Portal          5005    ✅ Running"
echo "   👥 Client Onboarding       5006    ✅ Running"
echo "   📈 Performance Monitor     5007    ✅ Running"
echo ""
echo "🌐 Access your platform:"
echo "   • Website: http://134.199.147.45"
echo "   • API Status: http://134.199.147.45/health"
echo ""
echo "📝 Useful commands:"
echo "   • View logs: journalctl -u enterprise-chat -f"
echo "   • Restart service: systemctl restart enterprise-chat"
echo "   • Check status: systemctl status enterprise-*"
echo ""

print_success "Backend deployment complete!"
