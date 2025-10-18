#!/bin/bash
set -e

# Enterprise Scanner SSL Certificate Automation
# Wildcard SSL certificate for enterprisescanner.com

echo "Starting SSL certificate generation for enterprisescanner.com"

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-dns-cloudflare
fi

# Cloudflare DNS credentials (create this file with your API token)
CLOUDFLARE_CONFIG="/etc/letsencrypt/cloudflare.ini"

if [ ! -f "$CLOUDFLARE_CONFIG" ]; then
    echo "Creating Cloudflare configuration..."
    sudo bash -c 'cat > /etc/letsencrypt/cloudflare.ini << EOF
dns_cloudflare_email = admin@enterprisescanner.com
dns_cloudflare_api_key = YOUR_CLOUDFLARE_API_KEY_HERE
EOF'
    sudo chmod 600 /etc/letsencrypt/cloudflare.ini
fi

# Generate wildcard certificate
echo "Generating wildcard SSL certificate..."
sudo certbot certonly \
    --dns-cloudflare \
    --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
    --dns-cloudflare-propagation-seconds 60 \
    -d enterprisescanner.com \
    -d *.enterprisescanner.com \
    --email security@enterprisescanner.com \
    --agree-tos \
    --non-interactive

# Set up auto-renewal
echo "Setting up automatic renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Copy certificates to application directory
echo "Copying certificates..."
sudo cp /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem /opt/enterprise-scanner/ssl/cert.pem
sudo cp /etc/letsencrypt/live/enterprisescanner.com/privkey.pem /opt/enterprise-scanner/ssl/key.pem
sudo chown -R app:app /opt/enterprise-scanner/ssl/
sudo chmod 600 /opt/enterprise-scanner/ssl/*

echo "SSL certificate setup complete!"
echo "Certificate expires: $(sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/enterprisescanner.com/cert.pem)"
