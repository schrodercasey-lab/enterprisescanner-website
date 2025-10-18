
# Enterprise Scanner - Live Security Assessment Tool Deployment Instructions

## Deployment Package: enterprise_scanner_live_20251015_114038.tar.gz
## Target Server: enterprisescanner.com (134.199.147.45)
## Deployment Date: 2025-10-15 11:40:39

### DEPLOYMENT STEPS

1. **Upload Archive to Server**
   ```bash
   scp deployment/archives/enterprise_scanner_live_20251015_114038.tar.gz user@134.199.147.45:/tmp/
   ```

2. **Connect to Server**
   ```bash
   ssh user@134.199.147.45
   ```

3. **Extract and Deploy**
   ```bash
   cd /tmp
   tar -xzf enterprise_scanner_live_20251015_114038.tar.gz
   cd live_deployment_20251015_114038
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Verify Deployment**
   ```bash
   # Check service status
   sudo systemctl status enterprise-scanner
   
   # Check logs
   sudo journalctl -u enterprise-scanner -f
   
   # Test API
   curl -H "X-API-Key: YOUR_API_KEY" https://enterprisescanner.com/api/health
   ```

### POST-DEPLOYMENT CONFIGURATION

1. **Generate Production API Key**
   ```bash
   curl -X POST https://enterprisescanner.com/api/keys/generate \
        -H "Content-Type: application/json" \
        -d '{"name":"production_key","permissions":"read_write"}'
   ```

2. **Test Live Security Assessment**
   ```bash
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
   ```

3. **Monitor Assessment Progress**
   ```bash
   curl -H "X-API-Key: YOUR_API_KEY" \
        https://enterprisescanner.com/api/assessment/status/ASSESSMENT_ID
   ```

4. **Download PDF Report**
   ```bash
   curl -H "X-API-Key: YOUR_API_KEY" \
        https://enterprisescanner.com/api/assessment/report/ASSESSMENT_ID \
        -o security_report.pdf
   ```

### FEATURES DEPLOYED

[X] **Live Security Assessment Tool**
   - Real-time vulnerability scanning
   - SSL/TLS security analysis
   - DNS security checks
   - Network security assessment
   - Progress tracking with live updates
   - Professional PDF report generation

[X] **API Authentication System**
   - API key-based authentication
   - Usage tracking and monitoring
   - Secure endpoint access

[X] **Production Infrastructure**
   - Nginx reverse proxy configuration
   - SSL/HTTPS termination
   - Systemd service management
   - Log rotation and monitoring

### ACCESS POINTS

- **Website**: https://enterprisescanner.com
- **Security Assessment**: https://enterprisescanner.com/security-assessment.html
- **API Health**: https://enterprisescanner.com/api/health
- **API Documentation**: https://enterprisescanner.com/api-documentation.html

### SECURITY NOTES

- All API endpoints require valid API key in X-API-Key header
- SSL certificates configured for HTTPS-only access
- Assessment data stored securely with encryption
- Logs monitored for security events

### SUPPORT

For deployment support or issues:
- Email: support@enterprisescanner.com
- Technical: security@enterprisescanner.com

---
Deployment ID: live_20251015_114038
Generated: 2025-10-15 11:40:39
