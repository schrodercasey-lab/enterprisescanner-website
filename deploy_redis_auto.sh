#!/bin/bash

# Option E - Task 1: Redis Caching Setup (Automated)
# This script automatically handles all password prompts

echo "=== Option E: Task 1 - Redis Caching Setup ==="
echo ""

# Create Redis directory structure
echo "1. Creating Redis configuration directory..."
mkdir -p /opt/enterprisescanner/redis
cd /opt/enterprisescanner/redis

# Create Redis configuration file
echo "2. Creating Redis configuration..."
cat > redis.conf << 'EOF'
# Redis Configuration for Enterprise Scanner

# Network
bind 127.0.0.1
port 6379
protected-mode yes

# General
daemonize no
pidfile /var/run/redis.pid
loglevel notice
logfile ""

# Persistence - RDB + AOF for data durability
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# AOF persistence
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Memory Management
maxmemory 256mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Performance
timeout 300
tcp-keepalive 300
tcp-backlog 511

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Security
requirepass SecureRedisPass2024!

# Clients
maxclients 10000
EOF

# Create Docker Compose file for Redis
echo "3. Creating Docker Compose configuration..."
cat > docker-compose.redis.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: enterprisescanner_redis
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "SecureRedisPass2024!", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - backend

volumes:
  redis_data:
    driver: local

networks:
  backend:
    name: enterprisescanner_network
EOF

# Create backend network if it doesn't exist
echo "4. Creating backend network..."
docker network create enterprisescanner_network 2>/dev/null || echo "Network already exists"

# Deploy Redis (no password prompt - runs in background)
echo "5. Deploying Redis container..."
docker-compose -f docker-compose.redis.yml up -d

# Wait for Redis to start
echo "6. Waiting for Redis to be ready..."
sleep 5

# Test Redis connection (using -a flag to pass password non-interactively)
echo "7. Testing Redis connection..."
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning ping

# Get Redis info without password prompt
echo "8. Getting Redis information..."
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO server | grep redis_version

# Create Python Redis helper module
echo "9. Creating Python Redis integration..."
cat > /opt/enterprisescanner/backend/redis_helper.py << 'EOF'
"""
Redis Helper Module for Enterprise Scanner
Provides caching utilities for API responses and session management
"""

import redis
import json
import pickle
from functools import wraps
from datetime import timedelta

class RedisCache:
    def __init__(self, host='127.0.0.1', port=6379, password='SecureRedisPass2024!', db=0):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=False,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
        
    def ping(self):
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"Redis connection error: {e}")
            return False
    
    def set(self, key, value, ttl=3600):
        """Set a value with TTL (default 1 hour)"""
        try:
            serialized = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key):
        """Get a value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete(self, key):
        """Delete a key from cache"""
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key):
        """Check if key exists"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    def get_stats(self):
        """Get Redis statistics"""
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_days': info.get('uptime_in_days', 0)
            }
        except Exception as e:
            print(f"Redis stats error: {e}")
            return {}

def cache_response(ttl=3600, key_prefix='api'):
    """
    Decorator to cache API responses
    Usage: @cache_response(ttl=1800, key_prefix='scan')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cache = RedisCache()
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                print(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            print(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Example usage
if __name__ == "__main__":
    cache = RedisCache()
    
    # Test connection
    print("Testing Redis connection...")
    if cache.ping():
        print("✅ Redis connected successfully!")
        
        # Test set/get
        cache.set('test_key', {'message': 'Hello Redis!'}, ttl=60)
        value = cache.get('test_key')
        print(f"Test value: {value}")
        
        # Get stats
        stats = cache.get_stats()
        print(f"Redis stats: {stats}")
    else:
        print("❌ Redis connection failed!")
EOF

# Install redis-py if not already installed
echo "10. Installing Python Redis library..."
pip3 install redis --quiet 2>/dev/null || echo "redis-py already installed"

# Test Python Redis integration
echo "11. Testing Python Redis integration..."
cd /opt/enterprisescanner/backend
python3 redis_helper.py

# Create Redis monitoring script
echo "12. Creating Redis monitoring script..."
cat > /opt/enterprisescanner/redis/monitor_redis.sh << 'EOF'
#!/bin/bash
# Redis monitoring and health check script

echo "=== Redis Health Check ==="
echo ""

# Container status
echo "Container Status:"
docker ps | grep enterprisescanner_redis

echo ""
echo "Redis Info:"
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO server | grep -E "redis_version|uptime_in_days"

echo ""
echo "Connected Clients:"
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO clients | grep connected_clients

echo ""
echo "Memory Usage:"
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO memory | grep -E "used_memory_human|maxmemory_human|mem_fragmentation_ratio"

echo ""
echo "Stats:"
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO stats | grep -E "total_commands_processed|keyspace_hits|keyspace_misses"

echo ""
echo "Persistence Status:"
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO persistence | grep -E "aof_enabled|rdb_last_save_time"

echo ""
echo "Cache Hit Rate:"
HITS=$(docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
MISSES=$(docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
TOTAL=$((HITS + MISSES))
if [ $TOTAL -gt 0 ]; then
    HIT_RATE=$(echo "scale=2; $HITS * 100 / $TOTAL" | bc)
    echo "Hit Rate: ${HIT_RATE}%"
else
    echo "Hit Rate: N/A (no requests yet)"
fi
EOF

chmod +x /opt/enterprisescanner/redis/monitor_redis.sh

# Add Redis exporter to monitoring stack
echo "13. Adding Redis exporter for Prometheus..."
cat > /opt/enterprisescanner/monitoring/docker-compose.redis-exporter.yml << 'EOF'
version: '3.8'

services:
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    restart: unless-stopped
    ports:
      - "127.0.0.1:9121:9121"
    environment:
      - REDIS_ADDR=redis://enterprisescanner_redis:6379
      - REDIS_PASSWORD=SecureRedisPass2024!
    networks:
      - monitoring_default
      - backend

networks:
  monitoring_default:
    external: true
  backend:
    external: true
    name: enterprisescanner_network
EOF

# Deploy Redis exporter
echo "14. Deploying Redis exporter..."
cd /opt/enterprisescanner/monitoring
docker-compose -f docker-compose.redis-exporter.yml up -d

# Update Prometheus configuration
echo "15. Updating Prometheus configuration..."
# Backup current config
cp prometheus.yml prometheus.yml.backup-$(date +%Y%m%d-%H%M%S)

# Add Redis exporter to Prometheus
if ! grep -q "redis-exporter" prometheus.yml; then
    cat >> prometheus.yml << 'EOF'

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
EOF
    echo "Prometheus config updated"
else
    echo "Redis exporter already in Prometheus config"
fi

# Restart Prometheus to pick up new config
echo "16. Restarting Prometheus..."
docker restart prometheus

# Final verification
echo ""
echo "17. Final verification..."
sleep 3
docker exec enterprisescanner_redis redis-cli -a "SecureRedisPass2024!" --no-auth-warning PING

echo ""
echo "✅ Redis Caching Setup Complete!"
echo ""
echo "=== Redis Information ==="
echo "Host: 127.0.0.1"
echo "Port: 6379"
echo "Password: SecureRedisPass2024!"
echo "Max Memory: 256MB (LRU eviction)"
echo "Persistence: RDB + AOF"
echo ""
echo "=== Monitoring ==="
echo "Redis Exporter: http://127.0.0.1:9121/metrics"
echo "Monitor Script: /opt/enterprisescanner/redis/monitor_redis.sh"
echo ""
echo "=== Next Steps ==="
echo "1. Integrate Redis caching in backend services"
echo "2. Configure cache TTL values per endpoint"
echo "3. Monitor cache hit rates in Grafana"
echo ""
echo "=== Cache TTL Recommendations ==="
echo "- Session data: 3600s (1 hour)"
echo "- API responses: 300s (5 minutes)"
echo "- Static data: 86400s (24 hours)"
echo "- User preferences: 7200s (2 hours)"
echo ""
