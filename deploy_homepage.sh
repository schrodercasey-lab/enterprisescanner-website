#!/bin/bash
# Deploy Enterprise Scanner Homepage to Production Server
# Upload the new professional homepage to fix the website

set -e

SERVER="134.199.147.45"
USER="root"
PASSWORD="Schroeder123!"

echo "================================================"
echo " ENTERPRISE SCANNER - HOMEPAGE DEPLOYMENT"
echo "================================================"
echo "🚀 Deploying new professional homepage..."

# Check if sshpass is available on Windows (if running from WSL/Git Bash)
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass not available. Installing via WSL or using PowerShell..."
    echo "Please run this from WSL or install OpenSSH on Windows"
    exit 1
fi

# Deploy HTML homepage
echo "📁 Deploying index.html..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
    website/index.html $USER@$SERVER:/var/www/html/

# Set proper permissions
echo "🔒 Setting file permissions..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'EOF'
chmod 644 /var/www/html/index.html
chown www-data:www-data /var/www/html/index.html
systemctl reload nginx
EOF

# Verify deployment
echo "🧪 Testing deployment..."
sleep 5

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER/)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Homepage deployment successful!"
    echo "🌐 Website: http://enterprisescanner.com"
    echo "🌐 Direct IP: http://$SERVER"
else
    echo "❌ Deployment verification failed (HTTP $RESPONSE)"
    exit 1
fi

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "Enterprise Scanner homepage is now live with:"
echo "• Professional Fortune 500-focused design"
echo "• Interactive ROI calculator"
echo "• Complete navigation and features"
echo "• Mobile-responsive layout"
echo ""
echo "🌐 Visit: http://enterprisescanner.com"