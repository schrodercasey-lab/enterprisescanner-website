# Common Commands - Enterprise Scanner
**Quick reference for frequently used terminal commands**  
**Last Updated:** October 16, 2025

---

## 🔐 SERVER ACCESS

### SSH Connection
```bash
# Connect to production server
ssh root@134.199.147.45

# With password: Schroeder123!
```

### SCP File Transfer
```powershell
# Windows PowerShell - Upload file to server
scp C:\path\to\local\file root@134.199.147.45:/var/www/html/

# Upload entire directory
scp -r C:\path\to\directory root@134.199.147.45:/var/www/html/

# Download from server to Windows
scp root@134.199.147.45:/path/to/remote/file C:\local\path\

# Upload specific website file
scp C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website\index.html root@134.199.147.45:/var/www/html/
```

---

## 🌐 NGINX WEB SERVER

### Service Management
```bash
# Check Nginx status
systemctl status nginx

# Start Nginx
systemctl start nginx

# Stop Nginx
systemctl stop nginx

# Restart Nginx (brief downtime)
systemctl restart nginx

# Reload Nginx (no downtime, graceful)
systemctl reload nginx

# Enable Nginx on boot
systemctl enable nginx
```

### Configuration Testing
```bash
# Test Nginx configuration (ALWAYS run before reload!)
nginx -t

# Test and display config
nginx -T

# Check Nginx version
nginx -v
```

### Log Viewing
```bash
# View access log (last 20 lines)
tail -20 /var/log/nginx/access.log

# Follow access log in real-time
tail -f /var/log/nginx/access.log

# View error log
tail -20 /var/log/nginx/error.log

# Follow error log
tail -f /var/log/nginx/error.log

# Search for specific IP in access log
grep "134.199.147.45" /var/log/nginx/access.log

# View today's errors
grep "$(date +%Y/%m/%d)" /var/log/nginx/error.log
```

---

## 🐳 DOCKER CONTAINERS

### Container Management
```bash
# List all running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Start all containers via Docker Compose
cd /opt/enterprisescanner
docker-compose up -d

# Stop all containers
docker-compose down

# Restart specific container
docker restart enterprisescanner_redis
docker restart enterprisescanner_postgres
docker restart enterprisescanner_grafana
docker restart enterprisescanner_prometheus

# View container logs
docker logs enterprisescanner_redis
docker logs enterprisescanner_postgres
docker logs -f enterprisescanner_redis  # Follow logs

# Check container resource usage
docker stats

# Execute command inside container
docker exec -it enterprisescanner_redis redis-cli
docker exec -it enterprisescanner_postgres psql -U admin -d enterprisescanner
```

### Container Health Checks
```bash
# Check Redis health
docker exec enterprisescanner_redis redis-cli PING
# Expected output: PONG

# Check PostgreSQL health
docker exec enterprisescanner_postgres pg_isready -U admin
# Expected output: accepting connections

# Inspect container
docker inspect enterprisescanner_redis
docker inspect enterprisescanner_postgres
```

---

## 💾 REDIS CACHE

### Redis CLI Access
```bash
# Access Redis CLI
docker exec -it enterprisescanner_redis redis-cli

# Or from host (if redis-cli installed)
redis-cli -h 127.0.0.1 -p 6379
```

### Redis Commands (inside redis-cli)
```redis
# Test connection
PING

# Get all keys
KEYS *

# Get value of key
GET key_name

# Set key-value
SET key_name "value"

# Delete key
DEL key_name

# Get Redis info
INFO

# Get memory stats
INFO memory

# Get stats
INFO stats

# Monitor commands in real-time
MONITOR

# Clear all data (CAREFUL!)
FLUSHALL

# Exit Redis CLI
EXIT
```

### Redis from Bash
```bash
# Get Redis info without entering CLI
docker exec enterprisescanner_redis redis-cli INFO stats

# Check Redis memory usage
docker exec enterprisescanner_redis redis-cli INFO memory | grep used_memory_human

# Get key count
docker exec enterprisescanner_redis redis-cli DBSIZE

# Test Redis connection
docker exec enterprisescanner_redis redis-cli PING
```

---

## 🗄️ POSTGRESQL DATABASE

### Database Access (Direct)
```bash
# Connect to PostgreSQL directly
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner

# Or via Docker exec
docker exec -it enterprisescanner_postgres psql -U admin -d enterprisescanner
```

### Database Access (via PgBouncer)
```bash
# Connect via PgBouncer connection pooler
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d enterprisescanner
```

### PostgreSQL Commands (inside psql)
```sql
-- List databases
\l

-- Connect to database
\c enterprisescanner

-- List tables
\dt

-- Describe table structure
\d table_name

-- List users
\du

-- View current connections
SELECT * FROM pg_stat_activity;

-- View database size
SELECT pg_size_pretty(pg_database_size('enterprisescanner'));

-- Exit psql
\q
```

### PostgreSQL from Bash
```bash
# Run SQL query from command line
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT version();"

# Export database to file
PGPASSWORD='SecurePass2024!' pg_dump -h 127.0.0.1 -p 5432 -U admin enterprisescanner > backup.sql

# Import database from file
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin enterprisescanner < backup.sql
```

---

## 🔌 PGBOUNCER CONNECTION POOLER

### PgBouncer Management
```bash
# Check PgBouncer status
ps aux | grep pgbouncer

# View PgBouncer logs
tail -f /var/log/postgresql/pgbouncer.log

# Access PgBouncer admin console
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d pgbouncer

# Stop PgBouncer
pkill pgbouncer

# Start PgBouncer
su - postgres -c "pgbouncer -d /etc/pgbouncer/pgbouncer.ini"

# Test PgBouncer config
pgbouncer -v /etc/pgbouncer/pgbouncer.ini
```

### PgBouncer Admin Commands (in pgbouncer console)
```sql
-- Show pool status
SHOW POOLS;

-- Show client connections
SHOW CLIENTS;

-- Show server connections
SHOW SERVERS;

-- Show statistics
SHOW STATS;

-- Show configuration
SHOW CONFIG;

-- Reload config without restart
RELOAD;

-- Pause all operations
PAUSE;

-- Resume operations
RESUME;

-- Exit
\q
```

---

## 📊 MONITORING (Prometheus & Grafana)

### Prometheus
```bash
# Check Prometheus status
docker ps | grep prometheus

# View Prometheus logs
docker logs enterprisescanner_prometheus

# Access Prometheus (from server via curl)
curl http://127.0.0.1:9090/metrics

# Check Prometheus targets
curl http://127.0.0.1:9090/api/v1/targets
```

### Grafana
```bash
# Check Grafana status
docker ps | grep grafana

# View Grafana logs
docker logs enterprisescanner_grafana

# Restart Grafana
docker restart enterprisescanner_grafana

# Access Grafana (from browser)
# https://enterprisescanner.com/grafana
```

### Exporters
```bash
# Check Redis Exporter metrics
curl http://127.0.0.1:9121/metrics

# Check Node Exporter metrics (if deployed)
curl http://127.0.0.1:9100/metrics

# Check Postgres Exporter metrics (if deployed)
curl http://127.0.0.1:9187/metrics
```

---

## 🎯 PERFORMANCE TESTING

### Run Performance Test
```bash
# Manual performance test
/usr/local/bin/run_performance_test.sh

# View latest results
cat /var/www/html/performance/latest.json

# View performance test log
tail -f /var/log/performance_test.log

# Test specific URL
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://enterprisescanner.com
```

### Check Website Response
```bash
# Quick response time check
time curl -I https://enterprisescanner.com

# Detailed timing
curl -o /dev/null -s -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" https://enterprisescanner.com

# Check specific endpoint
curl https://enterprisescanner.com/performance/latest.json | jq
```

---

## 🔍 SYSTEM MONITORING

### Server Health
```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
top
# Press 'q' to quit

# More detailed system stats
htop
# Press F10 or 'q' to quit

# Check running processes
ps aux | head -20

# Check system load
uptime

# Check system info
uname -a
cat /etc/os-release
```

### Service Status
```bash
# Check all running services
systemctl list-units --type=service --state=running

# Check specific service
systemctl status nginx
systemctl status docker

# View system logs
journalctl -xe
journalctl -u nginx
journalctl -u docker
```

---

## 📁 FILE MANAGEMENT

### Website Files
```bash
# List website files
ls -lah /var/www/html/

# Edit homepage
nano /var/www/html/index.html

# Check file permissions
ls -l /var/www/html/index.html

# Fix file permissions (if needed)
chown www-data:www-data /var/www/html/*.html
chmod 644 /var/www/html/*.html

# Create backup
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/html/

# Restore from backup
tar -xzf backup_20251016_120000.tar.gz -C /
```

### Application Files
```bash
# Navigate to application directory
cd /opt/enterprisescanner

# View Docker Compose config
cat docker-compose.yml

# Edit Docker Compose
nano docker-compose.yml

# View Redis config
cat redis/redis.conf

# View Prometheus config
cat prometheus/prometheus.yml
```

---

## 🔒 SSL CERTIFICATES

### Check SSL Status
```bash
# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/enterprisescanner.com/cert.pem -noout -dates

# Test SSL configuration
openssl s_client -connect enterprisescanner.com:443 -servername enterprisescanner.com

# Check certificate details
certbot certificates

# Test SSL renewal
certbot renew --dry-run
```

### Renew SSL Certificate
```bash
# Manual renewal
certbot renew

# Force renewal
certbot renew --force-renewal

# Renew and reload Nginx
certbot renew --post-hook "systemctl reload nginx"
```

---

## 🔥 EMERGENCY PROCEDURES

### Website Down
```bash
# 1. Check Nginx
systemctl status nginx
nginx -t
systemctl restart nginx

# 2. Check logs
tail -50 /var/log/nginx/error.log

# 3. Check disk space
df -h

# 4. Verify DNS
dig enterprisescanner.com
```

### High CPU/Memory
```bash
# Find top processes
top
# Press 'M' for memory, 'P' for CPU

# Kill specific process (use PID from top)
kill -9 <PID>

# Restart Docker containers
cd /opt/enterprisescanner
docker-compose restart
```

### Database Issues
```bash
# 1. Check PostgreSQL
docker ps | grep postgres
docker logs enterprisescanner_postgres

# 2. Check connections
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Restart PostgreSQL
docker restart enterprisescanner_postgres

# 4. Check PgBouncer
ps aux | grep pgbouncer
tail -20 /var/log/postgresql/pgbouncer.log
```

---

## 🧹 MAINTENANCE TASKS

### Clear Logs (when too large)
```bash
# Check log sizes
du -sh /var/log/nginx/*

# Clear Nginx logs (careful!)
> /var/log/nginx/access.log
> /var/log/nginx/error.log

# Rotate logs
logrotate -f /etc/logrotate.d/nginx
```

### Docker Cleanup
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup (careful!)
docker system prune -a
```

### Update System
```bash
# Update package list
apt update

# Upgrade packages
apt upgrade -y

# Upgrade security patches only
apt upgrade -y --security

# Check for reboot requirement
[ -f /var/run/reboot-required ] && cat /var/run/reboot-required.pkgs
```

---

## 📊 USEFUL ONE-LINERS

```bash
# Check website response time
curl -o /dev/null -s -w "%{time_total}\n" https://enterprisescanner.com

# Count number of requests in last hour
grep "$(date -d '1 hour ago' '+%d/%b/%Y:%H')" /var/log/nginx/access.log | wc -l

# Find largest files in /var/www/html
du -ah /var/www/html | sort -rh | head -20

# Check Redis memory
docker exec enterprisescanner_redis redis-cli INFO memory | grep human

# Monitor Docker container stats in real-time
watch -n 1 'docker stats --no-stream'

# Check all service ports
netstat -tulpn | grep LISTEN

# Find process using specific port
lsof -i :80
lsof -i :443

# Quick backup website
tar -czf ~/website_backup_$(date +%Y%m%d).tar.gz /var/www/html/

# Test if website is up
curl -s -o /dev/null -w "%{http_code}" https://enterprisescanner.com
# Returns: 200 = OK, 500 = Error, 000 = Down
```

---

## 🎯 DEPLOYMENT WORKFLOW

### Standard Website Update
```powershell
# 1. From Windows - Upload file
scp C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website\index.html root@134.199.147.45:/var/www/html/
```

```bash
# 2. On Server - Test Nginx config
nginx -t

# 3. Reload Nginx (no downtime)
systemctl reload nginx

# 4. Verify
curl -I https://enterprisescanner.com

# 5. Check for errors
tail -20 /var/log/nginx/error.log
```

### Docker Service Update
```bash
# 1. Navigate to compose directory
cd /opt/enterprisescanner

# 2. Pull latest images (if using registry)
docker-compose pull

# 3. Restart services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

---

**💡 TIP:** Bookmark this file for quick reference. Most issues can be resolved with these commands!

**⚠️ WARNING:** Always run `nginx -t` before `systemctl reload nginx` to avoid breaking the production website!

**📝 NOTE:** All commands assume you're logged into the production server (root@134.199.147.45) unless specified as PowerShell.
