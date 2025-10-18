#!/bin/bash
# Enterprise Scanner - Production Deployment Script
# Comprehensive deployment with health checks, rollback capability, and monitoring

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.prod.yml"
ENV_FILE="$SCRIPT_DIR/.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Enterprise Scanner - Production Deployment${NC}"
echo "=============================================="
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

echo -e "${GREEN}✅ Environment file found${NC}"
echo ""

# Load environment variables
source "$ENV_FILE"

# Pre-deployment checks
echo -e "${BLUE}📋 Running pre-deployment checks...${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# Check SSL certificates
if [ ! -f "$SCRIPT_DIR/ssl/fullchain.pem" ] || [ ! -f "$SCRIPT_DIR/ssl/privkey.pem" ]; then
    echo -e "${YELLOW}⚠️  SSL certificates not found${NC}"
    echo "Run ./setup-ssl.sh to generate certificates"
    read -p "Continue without SSL? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ SSL certificates found${NC}"
fi

echo ""

# Backup existing deployment
if [ "$(docker ps -q -f name=enterprisescanner)" ]; then
    echo -e "${YELLOW}📦 Creating backup of current deployment...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$SCRIPT_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    echo -e "${GREEN}✅ Database backup created${NC}"
    echo ""
fi

# Pull latest images
echo -e "${BLUE}📥 Pulling latest images...${NC}"
docker-compose -f "$COMPOSE_FILE" pull
echo ""

# Build services
echo -e "${BLUE}🔨 Building services...${NC}"
docker-compose -f "$COMPOSE_FILE" build --no-cache
echo ""

# Stop existing services
if [ "$(docker ps -q -f name=enterprisescanner)" ]; then
    echo -e "${YELLOW}⏹️  Stopping existing services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    echo ""
fi

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d
echo ""

# Wait for services to start
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Health checks
echo ""
echo -e "${BLUE}🏥 Running health checks...${NC}"
echo ""

SERVICES=(
    "nginx:80:/health"
    "enterprise_chat_system:5001:/health"
    "interactive_security_assessment:5002:/health"
    "advanced_analytics_dashboard:5003:/health"
    "api_documentation_portal:5004:/health"
    "partner_portal_system:5005:/health"
    "client_onboarding_automation:5006:/health"
    "performance_monitoring_system:5007:/health"
)

ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port path <<< "$service"
    
    echo -n "Checking $name... "
    
    # Try up to 5 times with 2 second delay
    for i in {1..5}; do
        if curl -f -s "http://localhost:$port$path" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Healthy${NC}"
            break
        fi
        
        if [ $i -eq 5 ]; then
            echo -e "${RED}❌ Unhealthy${NC}"
            ALL_HEALTHY=false
        else
            sleep 2
        fi
    done
done

echo ""

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    echo ""
    echo -e "${BLUE}📊 Deployment Summary:${NC}"
    echo "===================="
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Access your services:${NC}"
    echo "   Main site: https://$DOMAIN_NAME"
    echo "   Chat: https://$DOMAIN_NAME/chat/"
    echo "   Assessment: https://$DOMAIN_NAME/assessment/"
    echo "   Analytics: https://$DOMAIN_NAME/analytics/"
    echo "   API Docs: https://$DOMAIN_NAME/api-docs/"
    echo "   Partner Portal: https://$DOMAIN_NAME/partner/"
    echo "   Onboarding: https://$DOMAIN_NAME/onboarding/"
    echo "   Monitoring: https://$DOMAIN_NAME/monitoring/"
    echo ""
    echo -e "${BLUE}📝 View logs:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE logs -f [service_name]"
    echo ""
    echo -e "${BLUE}⏹️  Stop services:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE down"
    echo ""
else
    echo -e "${RED}❌ Some services failed health checks!${NC}"
    echo ""
    echo "View logs with:"
    echo "   docker-compose -f $COMPOSE_FILE logs"
    echo ""
    echo "Rollback deployment with:"
    echo "   docker-compose -f $COMPOSE_FILE down"
    echo "   # Restore from backup if needed"
    exit 1
fi
