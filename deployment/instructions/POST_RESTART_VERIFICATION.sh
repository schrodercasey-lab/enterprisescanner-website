# POST-RESTART VERIFICATION CHECKLIST
# Run these commands after the server restart at 12:34

echo "=========================================="
echo "Enterprise Scanner - Post-Restart Verification"
echo "=========================================="

# Step 1: Check system status
echo "1. Checking system status..."
uptime
systemctl is-system-running

# Step 2: Verify services are running
echo "2. Checking Enterprise Scanner service..."
systemctl status enterprise-scanner --no-pager

echo "3. Checking Nginx service..."
systemctl status nginx --no-pager

# Step 3: Test API endpoints
echo "4. Testing API health endpoint..."
curl -H 'X-API-Key: es_production_key_12345' http://enterprisescanner.com/api/health

# Step 4: Test key generation
echo "5. Testing API key generation..."
curl -X POST http://enterprisescanner.com/api/keys/generate \
     -H 'Content-Type: application/json' \
     -d '{"name":"post_restart_test","permissions":"read_write"}'

# Step 5: Test security assessment endpoint
echo "6. Testing security assessment..."
curl -X POST http://enterprisescanner.com/api/assessment/start \
     -H 'X-API-Key: es_production_key_12345' \
     -H 'Content-Type: application/json' \
     -d '{
       "company_name": "Post-Restart Test",
       "domain": "google.com",
       "email": "test@postresrtart.com",
       "company_size": "medium",
       "industry": "technology",
       "scan_types": ["ssl", "dns"]
     }'

# Step 6: Check logs for any errors
echo "7. Checking recent logs..."
journalctl -u enterprise-scanner -n 10 --no-pager

echo "=========================================="
echo "If all tests pass, Enterprise Scanner is ready!"
echo "=========================================="