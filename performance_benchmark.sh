#!/bin/bash
# Performance Benchmarking Script for Enterprise Scanner
# Tests combined impact of Redis + Compression + Caching + PgBouncer

echo "======================================"
echo "Enterprise Scanner Performance Benchmark"
echo "======================================"
echo ""

# Install benchmarking tools
echo "[1/5] Installing benchmarking tools..."
apt-get update -qq
apt-get install -y apache2-utils wrk curl -qq

echo ""
echo "[2/5] Testing Homepage Performance..."
echo "--------------------------------------"

# Test 1: Simple response time
echo "Test 1: Response Time (10 requests)"
ab -n 10 -c 1 https://enterprisescanner.com/ 2>&1 | grep -E "(Requests per second|Time per request|Transfer rate)"

echo ""
echo "Test 2: Concurrent Load (100 requests, 10 concurrent)"
ab -n 100 -c 10 https://enterprisescanner.com/ 2>&1 | grep -E "(Requests per second|Time per request|Transfer rate|Failed requests)"

echo ""
echo "Test 3: High Load (500 requests, 50 concurrent)"
ab -n 500 -c 50 https://enterprisescanner.com/ 2>&1 | grep -E "(Requests per second|Time per request|Transfer rate|Failed requests)"

echo ""
echo "[3/5] Testing Compression Effectiveness..."
echo "--------------------------------------"
curl -s -w "\nOriginal Size: %{size_download} bytes\n" -H "Accept-Encoding: identity" https://enterprisescanner.com/ -o /dev/null
curl -s -w "Compressed Size: %{size_download} bytes\n" -H "Accept-Encoding: gzip" https://enterprisescanner.com/ -o /dev/null

echo ""
echo "[4/5] Checking Cache Headers..."
echo "--------------------------------------"
curl -I https://enterprisescanner.com/ 2>&1 | grep -E "(Cache-Control|Content-Encoding|ETag)"
curl -I https://enterprisescanner.com/css/styles.css 2>&1 | grep -E "(Cache-Control|Content-Encoding)"

echo ""
echo "[5/5] Docker & Database Status..."
echo "--------------------------------------"
echo "Redis Status:"
docker ps | grep redis | awk '{print $1, $2, $7}'
docker exec enterprisescanner_redis redis-cli INFO stats | grep -E "(total_connections_received|instantaneous_ops_per_sec|keyspace_hits|keyspace_misses)"

echo ""
echo "PostgreSQL Status:"
docker ps | grep postgres | awk '{print $1, $2, $7}'

echo ""
echo "PgBouncer Status:"
ps aux | grep pgbouncer | grep -v grep | awk '{print $1, $2, $11}'
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d pgbouncer -t -c "SHOW POOLS;" 2>/dev/null | head -2

echo ""
echo "======================================"
echo "Benchmark Complete!"
echo "======================================"
