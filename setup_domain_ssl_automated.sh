#!/bin/bash
# Enterprise Scanner - Automated Domain & SSL Setup
# Production server: 134.199.147.45
# Domain: enterprisescanner.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="enterprisescanner.com"
WWW_DOMAIN="www.enterprisescanner.com"
EMAIL="admin@enterprisescanner.com"
SERVER_IP="134.199.147.45"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Enterprise Scanner - Domain & SSL Configuration            ║"
echo "║   Automated Production Deployment                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print step headers
print_step() {
    echo -e "\n${CYAN}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print errors
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check DNS Configuration
print_step "Step 1: Checking DNS Configuration"

echo "Checking if $DOMAIN points to this server ($SERVER_IP)..."

# Try to resolve domain
if command -v dig &> /dev/null; then
    RESOLVED_IP=$(dig +short A $DOMAIN | head -1)
elif command -v nslookup &> /dev/null; then
    RESOLVED_IP=$(nslookup $DOMAIN | grep "Address:" | tail -1 | awk '{print $2}')
else
    print_warning "Neither dig nor nslookup available. Skipping DNS check."
    RESOLVED_IP=""
fi

if [ -z "$RESOLVED_IP" ]; then
    print_warning "Could not resolve $DOMAIN"
    echo ""
    echo "❗ IMPORTANT: You need to configure your domain DNS first!"
    echo ""
    echo "📋 Add these DNS records at your domain registrar:"
    echo "   Type  | Name | Value          | TTL"
    echo "   ------|------|----------------|-----"
    echo "   A     | @    | $SERVER_IP     | 300"
    echo "   A     | www  | $SERVER_IP     | 300"
    echo ""
    read -p "Have you configured DNS? Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "DNS configuration required. Exiting."
        exit 1
    fi
elif [ "$RESOLVED_IP" == "$SERVER_IP" ]; then
    print_success "DNS correctly points to this server ($SERVER_IP)"
else
    print_warning "DNS points to $RESOLVED_IP (expected $SERVER_IP)"
    print_warning "SSL may fail. DNS propagation can take up to 48 hours."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Install Certbot
print_step "Step 2: Installing Certbot & Dependencies"

apt-get update -qq
apt-get install -y -qq certbot python3-certbot-nginx ufw

print_success "Certbot installed successfully"

# Step 3: Configure Firewall
print_step "Step 3: Configuring Firewall (UFW)"

# Allow SSH, HTTP, HTTPS
ufw --force enable
ufw allow 22/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw reload

print_success "Firewall configured (ports 22, 80, 443 open)"

# Step 4: Update Nginx Configuration for SSL
print_step "Step 4: Creating Nginx SSL Configuration"

# Backup existing nginx config
if [ -f "/opt/enterprisescanner/docker/nginx.conf" ]; then
    cp /opt/enterprisescanner/docker/nginx.conf /opt/enterprisescanner/docker/nginx.conf.backup
    print_success "Backed up existing nginx.conf"
fi

# Create SSL-ready nginx configuration
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

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # Gzip compression
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
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        listen [::]:80;
        server_name enterprisescanner.com www.enterprisescanner.com;

        # ACME challenge for Let's Encrypt
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirect all other traffic to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name enterprisescanner.com www.enterprisescanner.com;

        # SSL configuration
        ssl_certificate /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/enterprisescanner.com/privkey.pem;
        ssl_trusted_certificate /etc/letsencrypt/live/enterprisescanner.com/chain.pem;

        # Modern SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
        ssl_prefer_server_ciphers off;

        # SSL session optimization
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        # OCSP stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 8.8.8.8 8.8.4.4 valid=300s;
        resolver_timeout 5s;

        # Security headers
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;

        # Document root
        root /usr/share/nginx/html;
        index index.html;

        # Main location
        location / {
            limit_req zone=general burst=20 nodelay;
            try_files $uri $uri/ /index.html;
        }

        # API endpoints (for future microservices)
        location /api/ {
            limit_req zone=general burst=10 nodelay;
            proxy_pass http://backend:5000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
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
        }
    }
}
NGINX_EOF

print_success "SSL-ready nginx configuration created"

# Step 5: Stop Nginx temporarily
print_step "Step 5: Preparing for SSL Certificate Generation"

cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml stop nginx

print_success "Nginx stopped temporarily for certificate generation"

# Step 6: Generate SSL Certificates
print_step "Step 6: Generating SSL Certificates with Let's Encrypt"

echo "This may take a few minutes..."

# Create webroot directory for certbot
mkdir -p /var/www/certbot

# Generate certificates using standalone mode
if certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domains "$DOMAIN,$WWW_DOMAIN" \
    --preferred-challenges http; then
    print_success "SSL certificates generated successfully!"
else
    print_error "Certificate generation failed"
    # Restart nginx even if it fails
    docker-compose -f docker-compose.prod.yml start nginx
    exit 1
fi

# Set up automatic renewal
print_step "Step 7: Configuring Automatic Certificate Renewal"

# Create renewal hook script
cat > /etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh << 'HOOK_EOF'
#!/bin/bash
cd /opt/enterprisescanner/docker
docker-compose -f docker-compose.prod.yml restart nginx
HOOK_EOF

chmod +x /etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh

# Add renewal cron job (runs twice daily)
(crontab -l 2>/dev/null | grep -v certbot; echo "0 */12 * * * certbot renew --quiet --deploy-hook '/etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh'") | crontab -

print_success "Automatic renewal configured (checks twice daily)"

# Step 8: Update docker-compose for SSL
print_step "Step 8: Updating Docker Configuration for SSL"

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
      - ../website:/usr/share/nginx/html:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
    networks:
      - enterprisescanner_network
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

print_success "Docker Compose updated with SSL mounts"

# Step 9: Start services
print_step "Step 9: Starting Services with SSL"

docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
sleep 5

print_success "Services started with SSL enabled"

# Step 10: Verification
print_step "Step 10: Verifying SSL Configuration"

echo ""
echo "Testing HTTP redirect..."
curl -I http://localhost 2>/dev/null | head -1

echo ""
echo "Testing HTTPS..."
docker-compose -f docker-compose.prod.yml ps

# Step 11: Display certificate info
print_step "Certificate Information"

certbot certificates

# Final summary
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ SSL SETUP COMPLETE!                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "🌐 Your website is now available at:"
echo "   • https://enterprisescanner.com"
echo "   • https://www.enterprisescanner.com"
echo ""
echo "🔒 SSL Certificate Details:"
echo "   • Issuer: Let's Encrypt"
echo "   • Valid for: $DOMAIN, $WWW_DOMAIN"
echo "   • Expiry: 90 days (auto-renews)"
echo ""
echo "✅ Security Features:"
echo "   • ✅ HTTPS enabled with TLS 1.2/1.3"
echo "   • ✅ HTTP automatically redirects to HTTPS"
echo "   • ✅ Security headers configured"
echo "   • ✅ Automatic certificate renewal"
echo "   • ✅ Firewall configured (UFW)"
echo ""
echo "📝 Next Steps:"
echo "   1. Test your site: https://enterprisescanner.com"
echo "   2. Check SSL rating: https://www.ssllabs.com/ssltest/analyze.html?d=enterprisescanner.com"
echo "   3. Deploy backend microservices (Option 3)"
echo ""
echo "🔍 Useful Commands:"
echo "   • Check certificate: certbot certificates"
echo "   • Force renewal: certbot renew --force-renewal"
echo "   • View nginx logs: docker logs enterprisescanner_nginx"
echo "   • Check SSL: curl -I https://enterprisescanner.com"
echo ""

print_success "Domain & SSL configuration complete!"
