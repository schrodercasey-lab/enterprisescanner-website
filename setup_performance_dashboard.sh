#!/bin/bash
# Performance Monitoring Dashboard Setup
# Creates a permanent web endpoint at https://enterprisescanner.com/performance

echo "======================================"
echo "Setting Up Performance Dashboard"
echo "======================================"

# Create performance monitoring directory
mkdir -p /var/www/html/performance
cd /var/www/html/performance

# Install tools
echo "[1/4] Installing benchmarking tools..."
apt-get update -qq
apt-get install -y apache2-utils wrk curl jq bc -qq

# Create performance test script
echo "[2/4] Creating benchmark script..."
cat > /usr/local/bin/run_performance_test.sh << 'BENCHMARK_SCRIPT'
#!/bin/bash
# Automated Performance Testing

OUTPUT_FILE="/var/www/html/performance/latest.json"
HTML_FILE="/var/www/html/performance/index.html"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Run Apache Bench tests
echo "Running performance tests..."

# Test 1: Light load
AB_LIGHT=$(ab -n 50 -c 5 -g /tmp/ab_light.tsv https://enterprisescanner.com/ 2>&1)
RPS_LIGHT=$(echo "$AB_LIGHT" | grep "Requests per second" | awk '{print $4}')
TIME_LIGHT=$(echo "$AB_LIGHT" | grep "Time per request" | head -1 | awk '{print $4}')

# Test 2: Medium load
AB_MEDIUM=$(ab -n 200 -c 20 -g /tmp/ab_medium.tsv https://enterprisescanner.com/ 2>&1)
RPS_MEDIUM=$(echo "$AB_MEDIUM" | grep "Requests per second" | awk '{print $4}')
TIME_MEDIUM=$(echo "$AB_MEDIUM" | grep "Time per request" | head -1 | awk '{print $4}')

# Test 3: Heavy load
AB_HEAVY=$(ab -n 500 -c 50 -g /tmp/ab_heavy.tsv https://enterprisescanner.com/ 2>&1)
RPS_HEAVY=$(echo "$AB_HEAVY" | grep "Requests per second" | awk '{print $4}')
TIME_HEAVY=$(echo "$AB_HEAVY" | grep "Time per request" | head -1 | awk '{print $4}')
FAILED=$(echo "$AB_HEAVY" | grep "Failed requests" | awk '{print $3}')

# Test compression
SIZE_UNCOMPRESSED=$(curl -s -w "%{size_download}" -H "Accept-Encoding: identity" https://enterprisescanner.com/ -o /dev/null)
SIZE_COMPRESSED=$(curl -s -w "%{size_download}" -H "Accept-Encoding: gzip" https://enterprisescanner.com/ -o /dev/null)
COMPRESSION_RATIO=$(echo "scale=1; (1 - $SIZE_COMPRESSED / $SIZE_UNCOMPRESSED) * 100" | bc)

# Get cache headers
CACHE_CONTROL=$(curl -s -I https://enterprisescanner.com/ | grep -i "cache-control" | cut -d: -f2 | xargs)

# Redis stats
REDIS_HITS=$(docker exec enterprisescanner_redis redis-cli INFO stats 2>/dev/null | grep "keyspace_hits" | cut -d: -f2 | tr -d '\r')
REDIS_MISSES=$(docker exec enterprisescanner_redis redis-cli INFO stats 2>/dev/null | grep "keyspace_misses" | cut -d: -f2 | tr -d '\r')
REDIS_TOTAL=$((REDIS_HITS + REDIS_MISSES))
if [ $REDIS_TOTAL -gt 0 ]; then
    REDIS_HIT_RATE=$(echo "scale=1; $REDIS_HITS * 100 / $REDIS_TOTAL" | bc)
else
    REDIS_HIT_RATE="0"
fi

# PgBouncer stats
PGBOUNCER_POOLS=$(PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d pgbouncer -t -c "SHOW POOLS;" 2>/dev/null | head -1 | awk '{print $5}')

# Docker status
REDIS_STATUS=$(docker ps --filter "name=enterprisescanner_redis" --format "{{.Status}}" | grep -o "Up.*" || echo "Down")
POSTGRES_STATUS=$(docker ps --filter "name=enterprisescanner_postgres" --format "{{.Status}}" | grep -o "Up.*" || echo "Down")
PGBOUNCER_STATUS=$(ps aux | grep -v grep | grep "pgbouncer" > /dev/null && echo "Running" || echo "Down")

# Create JSON output
cat > $OUTPUT_FILE << JSON
{
  "timestamp": "$TIMESTAMP",
  "performance": {
    "light_load": {
      "requests_per_second": ${RPS_LIGHT:-0},
      "avg_response_time_ms": ${TIME_LIGHT:-0},
      "concurrent_users": 5
    },
    "medium_load": {
      "requests_per_second": ${RPS_MEDIUM:-0},
      "avg_response_time_ms": ${TIME_MEDIUM:-0},
      "concurrent_users": 20
    },
    "heavy_load": {
      "requests_per_second": ${RPS_HEAVY:-0},
      "avg_response_time_ms": ${TIME_HEAVY:-0},
      "concurrent_users": 50,
      "failed_requests": ${FAILED:-0}
    }
  },
  "optimization": {
    "compression": {
      "original_size_bytes": ${SIZE_UNCOMPRESSED:-0},
      "compressed_size_bytes": ${SIZE_COMPRESSED:-0},
      "reduction_percent": ${COMPRESSION_RATIO:-0}
    },
    "caching": {
      "browser_cache_control": "$CACHE_CONTROL"
    },
    "redis": {
      "hits": ${REDIS_HITS:-0},
      "misses": ${REDIS_MISSES:-0},
      "hit_rate_percent": ${REDIS_HIT_RATE:-0}
    },
    "database": {
      "pgbouncer_idle_connections": ${PGBOUNCER_POOLS:-0}
    }
  },
  "services": {
    "redis": "$REDIS_STATUS",
    "postgresql": "$POSTGRES_STATUS",
    "pgbouncer": "$PGBOUNCER_STATUS"
  }
}
JSON

# Create HTML dashboard
cat > $HTML_FILE << 'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Scanner - Performance Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .timestamp {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.4em;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        .metric-value {
            font-weight: 700;
            color: #333;
            font-size: 1.1em;
        }
        .metric-value.good { color: #10b981; }
        .metric-value.warning { color: #f59e0b; }
        .metric-value.error { color: #ef4444; }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }
        .status-badge.up {
            background: #d1fae5;
            color: #065f46;
        }
        .status-badge.down {
            background: #fee2e2;
            color: #991b1b;
        }
        .refresh-btn {
            display: block;
            width: 200px;
            margin: 30px auto;
            padding: 15px 30px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .json-link {
            text-align: center;
            margin-top: 20px;
        }
        .json-link a {
            color: white;
            text-decoration: none;
            font-size: 1.1em;
            opacity: 0.9;
        }
        .json-link a:hover {
            opacity: 1;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Performance Dashboard</h1>
            <p class="timestamp" id="timestamp">Loading...</p>
        </div>

        <div class="grid">
            <!-- Performance Card -->
            <div class="card">
                <h2>⚡ Performance Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Light Load (5 users)</span>
                    <span class="metric-value good" id="rps-light">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Medium Load (20 users)</span>
                    <span class="metric-value good" id="rps-medium">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Heavy Load (50 users)</span>
                    <span class="metric-value" id="rps-heavy">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Response Time</span>
                    <span class="metric-value" id="response-time">--</span>
                </div>
            </div>

            <!-- Optimization Card -->
            <div class="card">
                <h2>🔧 Optimizations</h2>
                <div class="metric">
                    <span class="metric-label">Gzip Compression</span>
                    <span class="metric-value good" id="compression">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Redis Hit Rate</span>
                    <span class="metric-value good" id="redis-hit">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Browser Caching</span>
                    <span class="metric-value good" id="browser-cache">Enabled</span>
                </div>
                <div class="metric">
                    <span class="metric-label">DB Pooling</span>
                    <span class="metric-value good" id="db-pool">Active</span>
                </div>
            </div>

            <!-- Services Card -->
            <div class="card">
                <h2>🛠️ Service Status</h2>
                <div class="metric">
                    <span class="metric-label">Redis Cache</span>
                    <span id="redis-status">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">PostgreSQL</span>
                    <span id="postgres-status">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">PgBouncer</span>
                    <span id="pgbouncer-status">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed Requests</span>
                    <span class="metric-value" id="failed-requests">--</span>
                </div>
            </div>
        </div>

        <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
        
        <div class="json-link">
            <a href="/performance/latest.json" target="_blank">📊 View Raw JSON Data</a>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const response = await fetch('/performance/latest.json');
                const data = await response.json();
                
                // Update timestamp
                document.getElementById('timestamp').textContent = 'Last updated: ' + data.timestamp;
                
                // Performance metrics
                document.getElementById('rps-light').textContent = data.performance.light_load.requests_per_second.toFixed(2) + ' req/s';
                document.getElementById('rps-medium').textContent = data.performance.medium_load.requests_per_second.toFixed(2) + ' req/s';
                document.getElementById('rps-heavy').textContent = data.performance.heavy_load.requests_per_second.toFixed(2) + ' req/s';
                document.getElementById('response-time').textContent = data.performance.medium_load.avg_response_time_ms.toFixed(0) + ' ms';
                
                // Optimizations
                document.getElementById('compression').textContent = data.optimization.compression.reduction_percent + '%';
                document.getElementById('redis-hit').textContent = data.optimization.redis.hit_rate_percent + '%';
                
                // Service status
                const services = ['redis', 'postgres', 'pgbouncer'];
                services.forEach(service => {
                    const elem = document.getElementById(service + '-status');
                    const status = data.services[service];
                    const isUp = status.includes('Up') || status.includes('Running');
                    elem.innerHTML = `<span class="status-badge ${isUp ? 'up' : 'down'}">${isUp ? '✓ Online' : '✗ Offline'}</span>`;
                });
                
                // Failed requests
                const failed = data.performance.heavy_load.failed_requests;
                const failedElem = document.getElementById('failed-requests');
                failedElem.textContent = failed;
                failedElem.className = 'metric-value ' + (failed === 0 ? 'good' : 'error');
                
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 60 seconds
        setInterval(loadData, 60000);
    </script>
</body>
</html>
HTML

echo "Performance test completed at $TIMESTAMP"
BENCHMARK_SCRIPT

chmod +x /usr/local/bin/run_performance_test.sh

# Create Nginx location block for performance dashboard
echo "[3/4] Configuring Nginx..."
if ! grep -q "location /performance" /etc/nginx/sites-available/enterprisescanner; then
    sed -i '/location \/ {/i\    location /performance {\n        alias /var/www/html/performance;\n        index index.html;\n        autoindex on;\n        add_header Cache-Control "no-cache, must-revalidate";\n    }\n' /etc/nginx/sites-available/enterprisescanner
    nginx -t && systemctl reload nginx
fi

# Run initial test
echo "[4/4] Running initial performance test..."
/usr/local/bin/run_performance_test.sh

# Set up cron job for automatic testing every hour
(crontab -l 2>/dev/null; echo "0 * * * * /usr/local/bin/run_performance_test.sh > /var/log/performance_test.log 2>&1") | crontab -

echo ""
echo "======================================"
echo "✅ Performance Dashboard Setup Complete!"
echo "======================================"
echo ""
echo "Access your dashboard at:"
echo "  🌐 https://enterprisescanner.com/performance"
echo "  📊 https://enterprisescanner.com/performance/latest.json"
echo ""
echo "Features:"
echo "  ✓ Real-time performance metrics"
echo "  ✓ Service health monitoring"
echo "  ✓ Auto-refresh every 60 seconds"
echo "  ✓ Hourly automated tests (via cron)"
echo "  ✓ JSON API for external tools"
echo ""
echo "Manual test: /usr/local/bin/run_performance_test.sh"
echo "======================================"
