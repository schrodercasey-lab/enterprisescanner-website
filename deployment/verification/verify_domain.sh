#!/bin/bash
set -e

echo "Enterprise Scanner Domain Verification"
echo "======================================"

DOMAIN="enterprisescanner.com"

# Check DNS propagation
echo "1. Checking DNS propagation..."
echo "A record for $DOMAIN:"
dig +short A $DOMAIN

echo "MX records for $DOMAIN:"
dig +short MX $DOMAIN

echo "TXT records for $DOMAIN:"
dig +short TXT $DOMAIN

# Check SSL certificate
echo ""
echo "2. Checking SSL certificate..."
echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates

# Check email configuration
echo ""
echo "3. Checking email configuration..."
nslookup -type=MX $DOMAIN

# Check website accessibility
echo ""
echo "4. Checking website accessibility..."
curl -I https://$DOMAIN/ 2>/dev/null | head -1

# Check security headers
echo ""
echo "5. Checking security headers..."
curl -I https://$DOMAIN/ 2>/dev/null | grep -E "(Strict-Transport-Security|X-Content-Type-Options|X-Frame-Options|X-XSS-Protection)"

# SSL Labs test (requires API key)
echo ""
echo "6. SSL Labs security rating:"
echo "Manual check: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"

echo ""
echo "Domain verification complete!"
