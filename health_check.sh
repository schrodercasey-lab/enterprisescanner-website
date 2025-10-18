#!/bin/bash
# Enterprise Scanner - Server Health Check
# Run on Ubuntu server: ./health_check.sh

echo ""
echo "🏥 ENTERPRISE SCANNER HEALTH CHECK"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Nginx
echo -e "${YELLOW}🔧 Nginx Status:${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "   ${GREEN}✅ Running${NC}"
    echo "   Uptime: $(systemctl show nginx --property=ActiveEnterTimestamp --value | cut -d' ' -f2-3)"
else
    echo -e "   ${RED}❌ Not Running${NC}"
fi

# Check Docker containers
echo ""
echo -e "${YELLOW}🐳 Docker Containers:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep enterprisescanner || echo "   No containers found"

# Check disk space
echo ""
echo -e "${YELLOW}💾 Disk Space:${NC}"
df -h / | tail -1 | awk '{printf "   Used: %s / %s (%s)\n", $3, $2, $5}'

# Check memory
echo ""
echo -e "${YELLOW}🧠 Memory Usage:${NC}"
free -h | grep Mem | awk '{printf "   Used: %s / %s\n", $3, $2}'

# Check SSL certificate
echo ""
echo -e "${YELLOW}🔒 SSL Certificate:${NC}"
certbot certificates 2>&1 | grep "Expiry Date" | head -1 || echo "   Certificate info not available"

# Check website response
echo ""
echo -e "${YELLOW}🌐 Website Status:${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://enterprisescanner.com)
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" https://enterprisescanner.com)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "   ${GREEN}✅ ONLINE${NC} (Status: $HTTP_CODE, Response: ${RESPONSE_TIME}s)"
else
    echo -e "   ${RED}❌ ERROR${NC} (Status: $HTTP_CODE)"
fi

# Check Redis
echo ""
echo -e "${YELLOW}📦 Redis Status:${NC}"
if docker exec enterprisescanner-redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "   ${GREEN}✅ Running${NC}"
    REDIS_MEMORY=$(docker exec enterprisescanner-redis redis-cli info memory 2>/dev/null | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    echo "   Memory: $REDIS_MEMORY"
else
    echo -e "   ${RED}❌ Not responding${NC}"
fi

# Check PostgreSQL
echo ""
echo -e "${YELLOW}🐘 PostgreSQL Status:${NC}"
if docker exec enterprisescanner-postgres pg_isready -U enterprisescanner 2>/dev/null | grep -q "accepting connections"; then
    echo -e "   ${GREEN}✅ Running${NC}"
    DB_SIZE=$(docker exec enterprisescanner-postgres psql -U enterprisescanner -c "SELECT pg_size_pretty(pg_database_size('enterprisescanner'));" -t 2>/dev/null | tr -d ' ')
    echo "   Database size: $DB_SIZE"
else
    echo -e "   ${YELLOW}⚠️  Not responding (may not be deployed yet)${NC}"
fi

# Check PgBouncer
echo ""
echo -e "${YELLOW}🔗 PgBouncer Status:${NC}"
if docker ps | grep -q enterprisescanner-pgbouncer; then
    echo -e "   ${GREEN}✅ Running${NC}"
else
    echo -e "   ${YELLOW}⚠️  Not running (may not be deployed yet)${NC}"
fi

# Check system load
echo ""
echo -e "${YELLOW}⚡ System Load:${NC}"
uptime | awk -F'load average:' '{print "   Load average:" $2}'

# Check for required restart
echo ""
if [ -f /var/run/reboot-required ]; then
    echo -e "${RED}⚠️  SYSTEM RESTART REQUIRED${NC}"
else
    echo -e "${GREEN}✅ No restart required${NC}"
fi

# Summary
echo ""
echo -e "${CYAN}📊 Health Check Complete!${NC}"
echo ""
