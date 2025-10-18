#!/bin/bash

# Enterprise Scanner Monitoring & Logging Setup
# Option D: Prometheus + Grafana Deployment
# Date: October 16, 2025

set -e

echo "=========================================="
echo "  MONITORING & LOGGING DEPLOYMENT        "
echo "=========================================="
echo ""
echo "This script will deploy:"
echo "  1. Prometheus (metrics collection)"
echo "  2. Grafana (visualization)"
echo "  3. Node Exporter (system metrics)"
echo "  4. PostgreSQL Exporter (database metrics)"
echo "  5. Alert rules and dashboards"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."

# Create monitoring directory
mkdir -p /opt/enterprisescanner/monitoring
cd /opt/enterprisescanner/monitoring

# ==============================================
# TASK 1: CREATE PROMETHEUS CONFIGURATION
# ==============================================

echo ""
echo "=== Task 1: Creating Prometheus Configuration ==="
echo ""

cat > prometheus.yml << 'PROM_EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'enterprisescanner-prod'

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: []

# Load rules once and periodically evaluate them
rule_files:
  - "alert_rules.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # PostgreSQL Exporter
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Backend services (if they expose metrics)
  - job_name: 'backend-services'
    static_configs:
      - targets:
        - 'host.docker.internal:5001'  # Chat
        - 'host.docker.internal:5002'  # Assessment
        - 'host.docker.internal:5003'  # Analytics
        - 'host.docker.internal:5004'  # API Docs
        - 'host.docker.internal:5005'  # Partners
        - 'host.docker.internal:5006'  # Onboarding
        - 'host.docker.internal:5007'  # Monitoring
PROM_EOF

echo "✓ Prometheus configuration created"

# Create alert rules
cat > alert_rules.yml << 'ALERT_EOF'
groups:
  - name: system_alerts
    interval: 30s
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for 5 minutes"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 90%"

      # Low disk space
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space below 10%"

      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} is not responding"
ALERT_EOF

echo "✓ Alert rules created"

# ==============================================
# TASK 2: CREATE DOCKER COMPOSE FOR MONITORING
# ==============================================

echo ""
echo "=== Task 2: Creating Monitoring Stack ==="
echo ""

cat > docker-compose.monitoring.yml << 'COMPOSE_EOF'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml:ro
      - prometheus-data:/prometheus
    extra_hosts:
      - "host.docker.internal:host-gateway"

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=Admin123!
      - GF_SERVER_ROOT_URL=https://enterprisescanner.com/grafana
      - GF_SERVER_SERVE_FROM_SUB_PATH=true
    ports:
      - "127.0.0.1:3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    command:
      - '--path.rootfs=/host'
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "127.0.0.1:9100:9100"
    volumes:
      - '/:/host:ro,rslave'

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres-exporter
    restart: unless-stopped
    environment:
      DATA_SOURCE_NAME: "postgresql://admin:SecurePass2024!@host.docker.internal:5432/enterprisescanner?sslmode=disable"
    ports:
      - "127.0.0.1:9187:9187"
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
COMPOSE_EOF

echo "✓ Docker Compose configuration created"

# ==============================================
# TASK 3: DEPLOY MONITORING STACK
# ==============================================

echo ""
echo "=== Task 3: Deploying Monitoring Stack ==="
echo ""

# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

echo "Waiting for services to start..."
sleep 10

# Check service status
docker ps | grep -E 'prometheus|grafana|exporter'

echo ""
echo "✓ Monitoring stack deployed"

# ==============================================
# TASK 4: CONFIGURE NGINX PROXY FOR GRAFANA
# ==============================================

echo ""
echo "=== Task 4: Configuring Nginx Proxy ==="
echo ""

# Backup current Nginx config
cp /etc/nginx/sites-available/enterprisescanner /etc/nginx/sites-available/enterprisescanner.backup-monitoring

# Add Grafana proxy location
# We'll add it to the existing HTTPS server block
cat > /tmp/grafana_location.conf << 'NGINX_EOF'
    # Grafana monitoring dashboard
    location /grafana/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
NGINX_EOF

# Insert Grafana location before the last closing brace
sed -i '/location \/api\/monitoring\//r /tmp/grafana_location.conf' /etc/nginx/sites-available/enterprisescanner

# Test Nginx configuration
nginx -t

if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo "✓ Nginx proxy configured for Grafana"
else
    echo "✗ Nginx configuration error"
    cp /etc/nginx/sites-available/enterprisescanner.backup-monitoring /etc/nginx/sites-available/enterprisescanner
    exit 1
fi

# ==============================================
# TASK 5: CONFIGURE GRAFANA DATASOURCE
# ==============================================

echo ""
echo "=== Task 5: Configuring Grafana ==="
echo ""

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "✓ Grafana is ready"
        break
    fi
    sleep 2
done

# Add Prometheus datasource to Grafana
curl -X POST -H "Content-Type: application/json" \
    -u admin:Admin123! \
    http://localhost:3000/api/datasources \
    -d '{
        "name":"Prometheus",
        "type":"prometheus",
        "url":"http://prometheus:9090",
        "access":"proxy",
        "isDefault":true
    }' 2>/dev/null || echo "Datasource may already exist"

echo "✓ Grafana datasource configured"

# ==============================================
# TASK 6: CREATE SYSTEM DASHBOARD
# ==============================================

echo ""
echo "=== Task 6: Creating Dashboards ==="
echo ""

# Create simple system overview dashboard
cat > /tmp/dashboard.json << 'DASH_EOF'
{
  "dashboard": {
    "title": "Enterprise Scanner - System Overview",
    "tags": ["system", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memory Usage %"
          }
        ]
      }
    ]
  },
  "overwrite": true
}
DASH_EOF

# Import dashboard
curl -X POST -H "Content-Type: application/json" \
    -u admin:Admin123! \
    http://localhost:3000/api/dashboards/db \
    -d @/tmp/dashboard.json 2>/dev/null

echo "✓ System overview dashboard created"

# ==============================================
# SUMMARY
# ==============================================

echo ""
echo "=========================================="
echo "  MONITORING DEPLOYMENT COMPLETE!        "
echo "=========================================="
echo ""
echo "✓ Prometheus: Running on port 9090"
echo "✓ Grafana: Running on port 3000"
echo "✓ Node Exporter: Collecting system metrics"
echo "✓ PostgreSQL Exporter: Collecting DB metrics"
echo "✓ Alert Rules: Configured"
echo ""
echo "=== Access Information ==="
echo "Grafana URL: https://enterprisescanner.com/grafana"
echo "Username: admin"
echo "Password: Admin123!"
echo ""
echo "Prometheus URL (localhost): http://localhost:9090"
echo ""
echo "=== Metrics Endpoints ==="
echo "Node Exporter: http://localhost:9100/metrics"
echo "PostgreSQL: http://localhost:9187/metrics"
echo ""
echo "=== Next Steps ==="
echo "1. Access Grafana dashboard"
echo "2. Explore pre-configured metrics"
echo "3. Customize dashboards as needed"
echo "4. Configure alert notifications"
echo ""
echo "Monitoring system is now operational!"
echo "=========================================="
