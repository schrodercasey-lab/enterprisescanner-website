#!/bin/bash
# Quick fix: Download microservices directly
# Run this after the deployment script fails at Step 3

echo "Downloading microservices from GitHub..."

cd /opt/enterprisescanner/backend/services

wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/enterprise_chat_system.py
wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/advanced_analytics_dashboard.py
wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/interactive_security_assessment.py
wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/api_documentation_portal.py
wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/partner_portal_system.py
wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/client_onboarding_automation.py
wget -q https://raw.githubusercontent.com/schrodercasey-lab/enterprisescanner-website/main/performance_monitoring_system.py

echo "✅ All services downloaded!"
echo ""
echo "Files in backend/services:"
ls -lh

echo ""
echo "Now run: sudo ./deploy_backend_services.sh"
