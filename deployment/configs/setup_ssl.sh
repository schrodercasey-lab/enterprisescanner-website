#!/bin/bash
# SSL Certificate Setup for Enterprise Scanner
# Uses Let's Encrypt Certbot for free SSL certificates

set -e

DOMAIN="enterprisescanner.com"
EMAIL="admin@enterprisescanner.com"
SSL_DIR="deployment/ssl"

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
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
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
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

echo "✅ SSL certificates configured successfully!"
echo "Certificate location: $SSL_DIR"
echo "Auto-renewal configured via cron"
