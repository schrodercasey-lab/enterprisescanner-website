#!/bin/bash
# SSL Certificate Monitoring Script
# Monitors certificate expiration and renewal

DOMAIN="enterprisescanner.com"
CERT_FILE="deployment/ssl/cert.pem"
ALERT_EMAIL="security@enterprisescanner.com"
WARNING_DAYS=30

    echo "SSL Certificate Monitoring for $DOMAIN"

# Check if certificate file exists
if [ ! -f "$CERT_FILE" ]; then
    echo "❌ Certificate file not found: $CERT_FILE"
    exit 1
fi

# Get certificate expiration date
EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_TIMESTAMP=$(date +%s)

# Calculate days until expiration
DAYS_UNTIL_EXPIRY=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))

echo "Certificate expires: $EXPIRY_DATE"
echo "Days until expiry: $DAYS_UNTIL_EXPIRY"

# Check certificate validity
if [ $DAYS_UNTIL_EXPIRY -lt 0 ]; then
    echo "CRITICAL: Certificate has expired!"
    # Send critical alert
    echo "Subject: CRITICAL: SSL Certificate Expired for $DOMAIN" | sendmail "$ALERT_EMAIL"
    exit 2
elif [ $DAYS_UNTIL_EXPIRY -lt $WARNING_DAYS ]; then
    echo "WARNING: Certificate expires in $DAYS_UNTIL_EXPIRY days"
    # Send warning alert
    echo "Subject: WARNING: SSL Certificate expiring soon for $DOMAIN" | sendmail "$ALERT_EMAIL"
    exit 1
else
    echo "Certificate is valid for $DAYS_UNTIL_EXPIRY more days"
fi

# Test SSL configuration
echo "Testing SSL configuration..."
SSL_TEST_RESULT=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates)

if [ $? -eq 0 ]; then
    echo "SSL connection test successful"
else
    echo "❌ SSL connection test failed"
    exit 3
fi

# Check certificate chain
echo "Verifying certificate chain..."
CHAIN_VALID=$(openssl verify -CAfile deployment/ssl/chain.pem $CERT_FILE)

if [[ $CHAIN_VALID == *"OK"* ]]; then
    echo "Certificate chain is valid"
else
    echo "❌ Certificate chain validation failed"
    exit 4
fi

echo "SSL monitoring completed successfully"
