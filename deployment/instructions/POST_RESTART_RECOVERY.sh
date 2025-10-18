# POST-RESTART RECOVERY COMMANDS
# The server restarted but the API service may need manual restart

echo "=========================================="
echo "Enterprise Scanner - Post-Restart Recovery"
echo "=========================================="

# Check current service status
echo "1. Checking current service status..."
systemctl status enterprise-scanner --no-pager
systemctl status nginx --no-pager

# Check if our application directory exists
echo "2. Checking application files..."
ls -la /var/www/enterprisescanner.com/
ls -la /var/www/enterprisescanner.com/backend/

# If the service is not running, restart it
echo "3. Restarting Enterprise Scanner service..."
systemctl start enterprise-scanner
systemctl enable enterprise-scanner

# Restart nginx to ensure proxy is working
echo "4. Restarting Nginx..."
systemctl restart nginx

# Wait a moment for services to start
echo "5. Waiting for services to initialize..."
sleep 5

# Test the API
echo "6. Testing API endpoints..."
curl -H 'X-API-Key: es_production_key_12345' http://localhost:5000/api/health
curl -H 'X-API-Key: es_production_key_12345' http://enterprisescanner.com/api/health

# Check logs for any errors
echo "7. Checking recent logs..."
journalctl -u enterprise-scanner -n 10 --no-pager

echo "=========================================="
echo "Recovery commands completed!"
echo "=========================================="