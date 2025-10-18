# LIVE DEPLOYMENT - SERVER SIDE COMMANDS
# You are now connected to: root@enterprisescanner-prod-01

# Step 1: Check current status
ls -la /tmp/
systemctl status nginx
systemctl status enterprise-scanner 2>/dev/null || echo "Service not yet installed"

# Step 2: Once the tar.gz file is uploaded to /tmp/, extract it
cd /tmp
tar -xzf enterprise_scanner_live_20251015_114038.tar.gz
ls -la live_deployment_20251015_114038/

# Step 3: Review deployment script before running
cat live_deployment_20251015_114038/deploy.sh

# Step 4: Make executable and run deployment
cd live_deployment_20251015_114038
chmod +x deploy.sh
./deploy.sh

# Step 5: Verify deployment
systemctl status enterprise-scanner
systemctl status nginx
journalctl -u enterprise-scanner -n 10

# Step 6: Test API endpoints
# First generate an API key
curl -X POST https://enterprisescanner.com/api/keys/generate \
     -H "Content-Type: application/json" \
     -d '{"name":"production_key","permissions":"read_write"}'

# Test health endpoint (replace YOUR_API_KEY with the key from above)
curl -H "X-API-Key: YOUR_API_KEY" https://enterprisescanner.com/api/health

# Step 7: Test Live Security Assessment
curl -X POST https://enterprisescanner.com/api/assessment/start \
     -H "X-API-Key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "Test Company",
       "domain": "google.com",
       "email": "test@testcompany.com",
       "company_size": "large",
       "industry": "technology", 
       "scan_types": ["ssl", "dns", "network"]
     }'

# Step 8: Monitor assessment progress
# Use the assessment_id returned from the previous command
curl -H "X-API-Key: YOUR_API_KEY" \
     https://enterprisescanner.com/api/assessment/status/ASSESSMENT_ID

# If you need to troubleshoot:
# Check logs: journalctl -u enterprise-scanner -f
# Check nginx: nginx -t && systemctl status nginx
# Check ports: netstat -tlnp | grep :5000