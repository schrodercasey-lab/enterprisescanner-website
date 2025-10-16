#!/bin/bash

echo "========================================"
echo "  BACKEND SERVICES DIAGNOSTICS"
echo "========================================"
echo ""

echo "1. Checking systemd service status..."
echo "--------------------------------------"
systemctl status enterprise-chat --no-pager | head -20
echo ""
systemctl status enterprise-analytics --no-pager | head -20
echo ""
systemctl status enterprise-api-docs --no-pager | head -20
echo ""
systemctl status enterprise-partners --no-pager | head -20
echo ""
systemctl status enterprise-onboarding --no-pager | head -20
echo ""
systemctl status enterprise-monitoring --no-pager | head -20
echo ""

echo "2. Checking which ports are listening..."
echo "--------------------------------------"
netstat -tuln | grep -E ":(5001|5002|5003|5004|5005|5006|5007) "
echo ""

echo "3. Checking recent service logs..."
echo "--------------------------------------"
echo "Chat Service (Port 5001):"
journalctl -u enterprise-chat -n 20 --no-pager
echo ""

echo "Analytics Service (Port 5003):"
journalctl -u enterprise-analytics -n 20 --no-pager
echo ""

echo "API Docs Service (Port 5004):"
journalctl -u enterprise-api-docs -n 20 --no-pager
echo ""

echo "4. Checking if Python processes are running..."
echo "--------------------------------------"
ps aux | grep python | grep -E "(chat|analytics|api|partner|onboard|monitor)" | grep -v grep
echo ""

echo "5. Testing direct service access (if running)..."
echo "--------------------------------------"
for port in 5001 5003 5004 5005 5006 5007; do
    echo "Testing port $port..."
    timeout 2 curl -s http://localhost:$port/ 2>&1 | head -5
    echo ""
done

echo "========================================"
echo "  DIAGNOSTICS COMPLETE"
echo "========================================"
