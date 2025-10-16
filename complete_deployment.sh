#!/bin/bash
# Complete Backend Deployment - Steps 4-9
# Run this after services are downloaded

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}Continuing backend deployment...${NC}"
echo ""

# Step 4: Create systemd services
echo "▶ Step 4: Creating Systemd Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Service 1: Enterprise Chat (Port 5001)
cat > /etc/systemd/system/enterprise-chat.service << 'EOF'
[Unit]
Description=Enterprise Scanner - Chat Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 enterprise_chat_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service 2: Analytics (Port 5003)
cat > /etc/systemd/system/enterprise-analytics.service << 'EOF'
[Unit]
Description=Enterprise Scanner - Analytics Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 advanced_analytics_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service 3: Security (Port 5002)
cat > /etc/systemd/system/enterprise-security.service << 'EOF'
[Unit]
Description=Enterprise Scanner - Security Assessment Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 interactive_security_assessment.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service 4: API Docs (Port 5004)
cat > /etc/systemd/system/enterprise-api-docs.service << 'EOF'
[Unit]
Description=Enterprise Scanner - API Documentation Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 api_documentation_portal.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service 5: Partners (Port 5005)
cat > /etc/systemd/system/enterprise-partners.service << 'EOF'
[Unit]
Description=Enterprise Scanner - Partner Portal Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 partner_portal_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service 6: Onboarding (Port 5006)
cat > /etc/systemd/system/enterprise-onboarding.service << 'EOF'
[Unit]
Description=Enterprise Scanner - Client Onboarding Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 client_onboarding_automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service 7: Monitoring (Port 5007)
cat > /etc/systemd/system/enterprise-monitoring.service << 'EOF'
[Unit]
Description=Enterprise Scanner - Performance Monitoring Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/enterprisescanner/backend/services
Environment="PATH=/opt/enterprisescanner/backend/venv/bin"
ExecStart=/opt/enterprisescanner/backend/venv/bin/python3 performance_monitoring_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo -e "${GREEN}✅ Systemd services created${NC}"

# Step 5: Start services
echo ""
echo "▶ Step 7: Starting Backend Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

systemctl enable enterprise-chat enterprise-analytics enterprise-security enterprise-api-docs enterprise-partners enterprise-onboarding enterprise-monitoring

systemctl start enterprise-chat
systemctl start enterprise-analytics
systemctl start enterprise-security
systemctl start enterprise-api-docs
systemctl start enterprise-partners
systemctl start enterprise-onboarding
systemctl start enterprise-monitoring

sleep 5
echo -e "${GREEN}✅ Backend services started${NC}"

# Step 6: Verify
echo ""
echo "▶ Step 9: Verifying Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

systemctl status enterprise-chat --no-pager | grep "Active:" || true
systemctl status enterprise-analytics --no-pager | grep "Active:" || true
systemctl status enterprise-security --no-pager | grep "Active:" || true
systemctl status enterprise-api-docs --no-pager | grep "Active:" || true
systemctl status enterprise-partners --no-pager | grep "Active:" || true
systemctl status enterprise-onboarding --no-pager | grep "Active:" || true
systemctl status enterprise-monitoring --no-pager | grep "Active:" || true

echo ""
echo "Testing endpoints..."
sleep 3

curl -s http://localhost:5001/health 2>&1 | head -1 || echo "Chat: Starting..."
curl -s http://localhost:5003/health 2>&1 | head -1 || echo "Analytics: Starting..."
curl -s http://localhost:5002/health 2>&1 | head -1 || echo "Security: Starting..."

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          ✅ BACKEND SERVICES DEPLOYED!                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "🎉 7 Python Microservices:"
echo ""
echo "   💬 Chat System             Port 5001"
echo "   📊 Analytics Dashboard     Port 5003"
echo "   🛡️  Security Assessment     Port 5002"
echo "   📄 API Documentation       Port 5004"
echo "   🤝 Partner Portal          Port 5005"
echo "   👥 Client Onboarding       Port 5006"
echo "   📈 Performance Monitor     Port 5007"
echo ""
echo "🌐 Test your services:"
echo "   curl http://localhost:5001/health"
echo "   curl http://localhost:5003/health"
echo ""
echo "📝 View logs:"
echo "   journalctl -u enterprise-chat -f"
echo ""
echo "Next: Update Nginx to proxy API requests"
echo ""
