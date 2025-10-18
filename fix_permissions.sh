#!/bin/bash
# Fix 403 Forbidden - Permissions Issue

echo "🔧 Fixing permissions for nginx..."

# Set correct ownership
chown -R www-data:www-data /var/www/html

# Set correct permissions for directories (755)
find /var/www/html -type d -exec chmod 755 {} \;

# Set correct permissions for files (644)
find /var/www/html -type f -exec chmod 644 {} \;

# Verify permissions
echo ""
echo "📁 Directory permissions:"
ls -ld /var/www/html

echo ""
echo "📄 File permissions (index.html):"
ls -lh /var/www/html/index.html

echo ""
echo "🔄 Reloading nginx..."
systemctl reload nginx

echo ""
echo "✅ Permissions fixed! Testing..."
curl -I http://localhost

echo ""
echo "🌐 Test the site now: https://enterprisescanner.com"
