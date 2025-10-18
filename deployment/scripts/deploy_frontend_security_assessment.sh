#!/bin/bash

# Deploy Enhanced Frontend Security Assessment Interface
# This script uploads the updated frontend files to production

echo "=== Deploying Enhanced Frontend Security Assessment Interface ==="

# Check if we're in the correct directory
if [ ! -f "security-assessment.html" ]; then
    echo "❌ Error: security-assessment.html not found. Please run from website directory."
    exit 1
fi

# Create backup of existing files
BACKUP_DIR="/var/www/enterprisescanner.com/backup_$(date +%Y%m%d_%H%M%S)"
echo "✅ Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup existing files
if [ -f "/var/www/enterprisescanner.com/security-assessment.html" ]; then
    cp "/var/www/enterprisescanner.com/security-assessment.html" "$BACKUP_DIR/"
    echo "✅ Backed up existing security-assessment.html"
fi

if [ -f "/var/www/enterprisescanner.com/js/security-assessment.js" ]; then
    cp "/var/www/enterprisescanner.com/js/security-assessment.js" "$BACKUP_DIR/"
    echo "✅ Backed up existing security-assessment.js"
fi

# Create necessary directories
echo "✅ Creating frontend directories..."
mkdir -p /var/www/enterprisescanner.com/js
mkdir -p /var/www/enterprisescanner.com/css

# Deploy the enhanced frontend files
echo "✅ Deploying enhanced security assessment interface..."

# Copy HTML file
cp security-assessment.html /var/www/enterprisescanner.com/
chmod 644 /var/www/enterprisescanner.com/security-assessment.html

# Copy JavaScript file
cp js/security-assessment.js /var/www/enterprisescanner.com/js/
chmod 644 /var/www/enterprisescanner.com/js/security-assessment.js

# Set proper ownership
chown -R www-data:www-data /var/www/enterprisescanner.com/

echo "✅ Enhanced frontend deployed successfully!"

# Test the deployment
echo "🧪 Testing frontend deployment..."

# Check if files exist and are readable
if [ -f "/var/www/enterprisescanner.com/security-assessment.html" ] && [ -r "/var/www/enterprisescanner.com/security-assessment.html" ]; then
    echo "✅ security-assessment.html deployed and readable"
else
    echo "❌ security-assessment.html deployment failed"
    exit 1
fi

if [ -f "/var/www/enterprisescanner.com/js/security-assessment.js" ] && [ -r "/var/www/enterprisescanner.com/js/security-assessment.js" ]; then
    echo "✅ security-assessment.js deployed and readable"
else
    echo "❌ security-assessment.js deployment failed"
    exit 1
fi

# Test web server access
curl -s -o /dev/null -w "%{http_code}" http://localhost/security-assessment.html > /tmp/http_test
if [ "$(cat /tmp/http_test)" = "200" ]; then
    echo "✅ Frontend accessible via web server"
else
    echo "❌ Frontend not accessible via web server (HTTP $(cat /tmp/http_test))"
fi

rm -f /tmp/http_test

echo ""
echo "🎉 Enhanced Frontend Security Assessment Interface Deployment Complete!"
echo ""
echo "📊 Deployment Summary:"
echo "   • Enhanced security assessment form with Live API integration"
echo "   • Real-time progress monitoring with phase indicators"  
echo "   • Professional results dashboard with vulnerability breakdown"
echo "   • Interactive security category cards with scoring"
echo "   • Fortune 500-grade user experience and styling"
echo ""
echo "🔗 Access URLs:"
echo "   • Production: https://enterprisescanner.com/security-assessment.html"
echo "   • Local test: http://localhost/security-assessment.html"
echo ""
echo "🚀 Next Steps:"
echo "   1. Test complete assessment workflow end-to-end"
echo "   2. Verify API integration with Live Security Assessment Tool"
echo "   3. Test PDF report download functionality"
echo "   4. Validate mobile responsiveness and user experience"
