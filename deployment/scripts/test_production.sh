
# Enterprise Scanner - Post-Deployment Testing Commands
# Generated: 2025-10-15 11:45:10

# 1. Test website accessibility
curl -I https://enterprisescanner.com/

# 2. Test API health endpoint
curl -H "X-API-Key: es_prod_live_security_assessment_2025" \
     https://enterprisescanner.com/api/health

# 3. Test security assessment start
curl -X POST https://enterprisescanner.com/api/assessment/start \
     -H "X-API-Key: es_prod_live_security_assessment_2025" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "Test Fortune 500 Company",
       "domain": "microsoft.com",
       "email": "security@testcompany.com",
       "company_size": "large",
       "industry": "technology",
       "scan_types": ["ssl", "dns", "network"]
     }'

# 4. Monitor assessment status (replace ASSESSMENT_ID)
curl -H "X-API-Key: es_prod_live_security_assessment_2025" \
     https://enterprisescanner.com/api/assessment/status/ASSESSMENT_ID

# 5. Download PDF report (replace ASSESSMENT_ID)
curl -H "X-API-Key: es_prod_live_security_assessment_2025" \
     https://enterprisescanner.com/api/assessment/report/ASSESSMENT_ID \
     -o enterprise_security_report.pdf

# 6. Test frontend interface
# Visit: https://enterprisescanner.com/security-assessment.html

echo "Testing commands ready for production validation"
