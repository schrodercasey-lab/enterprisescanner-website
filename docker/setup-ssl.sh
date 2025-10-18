#!/bin/bash
# Enterprise Scanner - SSL Certificate Setup Script
# Generates self-signed certificates for local development or sets up Let's Encrypt for production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/ssl"
DOMAIN="${DOMAIN_NAME:-enterprisescanner.com}"
EMAIL="${SSL_CERT_EMAIL:-admin@enterprisescanner.com}"

echo "🔒 Enterprise Scanner SSL Certificate Setup"
echo "==========================================="
echo ""

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Check if running in production or development
if [ "$1" == "production" ]; then
    echo "📜 Setting up Let's Encrypt certificates for production..."
    echo "Domain: $DOMAIN"
    echo "Email: $EMAIL"
    echo ""
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo "❌ Certbot is not installed. Installing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot python3-certbot-nginx
        else
            echo "❌ Could not install certbot. Please install manually."
            exit 1
        fi
    fi
    
    echo "✅ Certbot is installed"
    echo ""
    
    # Create certbot directory
    mkdir -p "$SCRIPT_DIR/certbot/www"
    mkdir -p "$SCRIPT_DIR/certbot/conf"
    
    echo "📋 Requesting Let's Encrypt certificate..."
    echo "This will require your server to be accessible on port 80"
    echo ""
    
    # Request certificate using standalone mode
    sudo certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --cert-path "$SSL_DIR/fullchain.pem" \
        --key-path "$SSL_DIR/privkey.pem"
    
    # Copy certificates to SSL directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fullchain.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/privkey.pem"
    sudo chmod 644 "$SSL_DIR/fullchain.pem"
    sudo chmod 600 "$SSL_DIR/privkey.pem"
    
    echo ""
    echo "✅ Let's Encrypt certificates installed successfully!"
    echo "📁 Certificates location: $SSL_DIR"
    echo ""
    echo "📝 To renew certificates automatically, add this to crontab:"
    echo "0 0 * * * certbot renew --quiet --post-hook 'docker-compose -f $SCRIPT_DIR/docker-compose.prod.yml restart nginx'"
    echo ""
    
else
    echo "🔧 Generating self-signed certificates for development..."
    echo "Domain: $DOMAIN"
    echo ""
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/privkey.pem" \
        -out "$SSL_DIR/fullchain.pem" \
        -subj "/C=US/ST=California/L=San Francisco/O=Enterprise Scanner/OU=Development/CN=$DOMAIN" \
        -addext "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN,DNS:localhost"
    
    chmod 644 "$SSL_DIR/fullchain.pem"
    chmod 600 "$SSL_DIR/privkey.pem"
    
    echo ""
    echo "✅ Self-signed certificates generated successfully!"
    echo "📁 Certificates location: $SSL_DIR"
    echo ""
    echo "⚠️  WARNING: These are self-signed certificates for development only!"
    echo "   Browsers will show security warnings. For production, run:"
    echo "   ./setup-ssl.sh production"
    echo ""
fi

echo "🎉 SSL setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with SSL configuration"
echo "2. Start the services with: docker-compose -f docker-compose.prod.yml up -d"
echo "3. Access your site at: https://$DOMAIN"
