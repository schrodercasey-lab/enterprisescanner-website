#!/bin/bash
# Fix Nginx Configuration for Enterprise Scanner

echo "🔍 Checking Nginx configuration..."
echo ""

# Check if website directory exists and has files
echo "📁 Website Directory:"
ls -lh /opt/enterprisescanner/website/ | head -20

echo ""
echo "📄 Checking index.html:"
ls -lh /opt/enterprisescanner/website/index.html

echo ""
echo "🔧 Current Nginx Configuration:"
cat /etc/nginx/sites-available/enterprisescanner.com

echo ""
echo "🔗 Nginx Symlink:"
ls -lh /etc/nginx/sites-enabled/ | grep enterprisescanner

echo ""
echo "📝 Testing Nginx Configuration:"
nginx -t

echo ""
echo "🌐 Nginx Status:"
systemctl status nginx --no-pager | head -15
