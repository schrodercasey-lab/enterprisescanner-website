# Troubleshooting Playbook - Enterprise Scanner
**Quick solutions for common issues**  
**Last Updated:** October 16, 2025

---

## 🚨 EMERGENCY CONTACTS

**Production Server:**
- SSH: `root@134.199.147.45`
- Password: `Schroeder123!`

**Critical Services Status:**
- Website: https://enterprisescanner.com
- Grafana: https://enterprisescanner.com/grafana
- Performance: https://enterprisescanner.com/performance

---

## 🎯 QUICK DIAGNOSIS

```bash
# Run this first for overall health check
systemctl status nginx && \
docker ps && \
df -h && \
free -h
```

---

## 🔴 CRITICAL ISSUES (TOTAL OUTAGE)

### ❌ **"Website is completely down"**

#### **Symptoms:**
- Can't access https://enterprisescanner.com
- Connection timeout or refused
- ERR_CONNECTION_REFUSED in browser

#### **Quick Fix (5 minutes):**
```bash
# 1. SSH to server
ssh root@134.199.147.45

# 2. Check if Nginx is running
systemctl status nginx

# 3. If stopped, start it
systemctl start nginx

# 4. If running, restart it
systemctl restart nginx

# 5. Verify website is back
curl -I https://enterprisescanner.com
```

#### **Root Cause Analysis:**
```bash
# Check Nginx error logs
tail -50 /var/log/nginx/error.log

# Check system logs
journalctl -u nginx -n 50

# Check disk space (common cause)
df -h
# If >95% full, clear logs: > /var/log/nginx/access.log

# Check memory
free -h
# If OOM, restart services or upgrade droplet
```

#### **Prevention:**
- Monitor disk space weekly
- Set up automated alerts for Nginx status
- Enable auto-restart: `systemctl enable nginx`

---

### ❌ **"SSL certificate error / Not Secure warning"**

#### **Symptoms:**
- Browser shows "Your connection is not private"
- ERR_CERT_DATE_INVALID
- Certificate expired warning

#### **Quick Fix (2 minutes):**
```bash
# 1. Renew certificate
certbot renew

# 2. Reload Nginx
systemctl reload nginx

# 3. Verify
curl -I https://enterprisescanner.com
# Should show HTTP/2 200
```

#### **Root Cause Analysis:**
```bash
# Check certificate expiration
certbot certificates

# Check auto-renewal timer
systemctl status certbot.timer

# Test renewal process
certbot renew --dry-run
```

#### **Prevention:**
- Certbot auto-renews 30 days before expiry
- Check status monthly: `certbot certificates`
- Monitor certbot.timer: `systemctl status certbot.timer`

---

### ❌ **"Server not responding / Can't SSH"**

#### **Symptoms:**
- SSH connection timeout
- Can't ping 134.199.147.45
- DigitalOcean console shows server "off"

#### **Quick Fix (from DigitalOcean Console):**
1. Log into DigitalOcean: https://cloud.digitalocean.com
2. Navigate to droplet: enterprisescanner-prod-01
3. Check power status
4. If off, click "Power On"
5. If on but unresponsive, use console access
6. Reboot from console if needed

#### **Root Cause Analysis:**
```bash
# After regaining access:

# Check system logs for crash
journalctl -xb -p err

# Check for OOM kills
grep -i "out of memory" /var/log/syslog

# Check disk space
df -h

# Check for kernel panic
dmesg | grep -i panic
```

#### **Prevention:**
- Set up external monitoring (UptimeRobot, Pingdom)
- Monitor memory usage
- Configure swap space if RAM is limited
- Set up automatic reboot on crash

---

## 🟡 PERFORMANCE ISSUES (DEGRADED SERVICE)

### ⚠️ **"Website is slow / High response times"**

#### **Symptoms:**
- Pages take >5 seconds to load
- Performance dashboard shows >500ms response times
- Users complaining about slowness

#### **Quick Diagnosis:**
```bash
# 1. Check server load
uptime
# Load should be <2.0 on single-core droplet

# 2. Check memory
free -h
# Available memory should be >500MB

# 3. Check disk I/O
iostat -x 1 5
# %util should be <80%

# 4. Check network
ping -c 10 8.8.8.8
# Packet loss should be 0%

# 5. Test website response
time curl -I https://enterprisescanner.com
# Should complete in <1 second
```

#### **Quick Fixes:**

**If high CPU:**
```bash
# Find culprit
top
# Press 'P' to sort by CPU

# If Docker container is high:
docker stats

# Restart high-CPU container
docker restart <container_name>
```

**If low memory:**
```bash
# Check memory hogs
ps aux --sort=-%mem | head -10

# Restart Docker containers to free memory
cd /opt/enterprisescanner
docker-compose restart

# If still low, clear page cache (safe)
sync; echo 1 > /proc/sys/vm/drop_caches
```

**If disk I/O high:**
```bash
# Check disk usage
df -h

# Clear old logs
find /var/log -name "*.log" -mtime +30 -delete

# Clear Docker logs
docker system prune -a -f
```

#### **Root Cause Analysis:**
```bash
# Check Nginx access log for traffic spikes
wc -l /var/log/nginx/access.log
tail -1000 /var/log/nginx/access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn | head

# Check for DDoS/high traffic
grep "$(date '+%d/%b/%Y:%H')" /var/log/nginx/access.log | wc -l
# >10,000 requests/hour might indicate attack

# Check database performance
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d pgbouncer -c "SHOW POOLS;"
# Check for saturated pools

# Check Redis performance
docker exec enterprisescanner_redis redis-cli INFO stats | grep total_commands_processed
```

#### **Prevention:**
- Enable Redis caching in application
- Set up CloudFlare CDN
- Monitor performance metrics in Grafana
- Set up rate limiting in Nginx

---

### ⚠️ **"Redis connection failed"**

#### **Symptoms:**
- Application errors mentioning Redis
- Cache misses showing 100%
- Container not responding

#### **Quick Fix:**
```bash
# 1. Check if Redis is running
docker ps | grep redis

# 2. If not running, start it
docker restart enterprisescanner_redis

# 3. Test connection
docker exec enterprisescanner_redis redis-cli PING
# Should return: PONG

# 4. Check Redis logs
docker logs enterprisescanner_redis --tail 50
```

#### **Root Cause Analysis:**
```bash
# Check Redis memory usage
docker exec enterprisescanner_redis redis-cli INFO memory | grep used_memory_human

# Check if evicting keys (memory full)
docker exec enterprisescanner_redis redis-cli INFO stats | grep evicted_keys

# Check for errors
docker logs enterprisescanner_redis 2>&1 | grep -i error

# Verify Redis config
cat /opt/enterprisescanner/redis/redis.conf
```

#### **Recovery Options:**

**If memory full:**
```bash
# Clear all keys (CAREFUL!)
docker exec enterprisescanner_redis redis-cli FLUSHALL

# Or increase maxmemory in config
nano /opt/enterprisescanner/redis/redis.conf
# Change: maxmemory 256mb → maxmemory 512mb

# Restart Redis
docker restart enterprisescanner_redis
```

**If container crashed:**
```bash
# Check Docker logs
docker logs enterprisescanner_redis

# Remove and recreate
cd /opt/enterprisescanner
docker-compose down redis
docker-compose up -d redis
```

#### **Prevention:**
- Monitor Redis memory in Grafana
- Set appropriate maxmemory and eviction policy
- Regular Redis INFO checks
- Configure persistence (RDB + AOF)

---

### ⚠️ **"PostgreSQL connection refused"**

#### **Symptoms:**
- Database connection errors
- "could not connect to server" errors
- Application can't start

#### **Quick Fix:**
```bash
# 1. Check if PostgreSQL is running
docker ps | grep postgres

# 2. If not running, start it
docker restart enterprisescanner_postgres

# 3. Test connection
docker exec enterprisescanner_postgres pg_isready -U admin
# Should return: accepting connections

# 4. Try connecting
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT 1;"
```

#### **Root Cause Analysis:**
```bash
# Check PostgreSQL logs
docker logs enterprisescanner_postgres --tail 100

# Check for disk space issues
df -h /opt/enterprisescanner/postgres/data

# Check connection count
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT count(*) FROM pg_stat_activity;"

# Check for locks
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT * FROM pg_locks WHERE granted = false;"
```

#### **Common Fixes:**

**Too many connections:**
```bash
# Kill idle connections
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';"

# Or use PgBouncer (connection pooling)
# Connection string should use port 6432, not 5432
```

**Container won't start:**
```bash
# Check data directory permissions
ls -la /opt/enterprisescanner/postgres/data

# If corrupted, restore from backup
# (Make sure you have backups!)

# Or recreate container (WILL LOSE DATA)
docker-compose down postgres
rm -rf /opt/enterprisescanner/postgres/data/*
docker-compose up -d postgres
```

#### **Prevention:**
- Use PgBouncer (port 6432) for connection pooling
- Regular database backups
- Monitor connection count
- Set appropriate max_connections in PostgreSQL config

---

### ⚠️ **"PgBouncer not responding"**

#### **Symptoms:**
- Can't connect to port 6432
- "connection refused" on PgBouncer port
- Application using direct PostgreSQL connection

#### **Quick Fix:**
```bash
# 1. Check if PgBouncer is running
ps aux | grep pgbouncer

# 2. If not running, start it
su - postgres -c "pgbouncer -d /etc/pgbouncer/pgbouncer.ini"

# 3. Test connection
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d enterprisescanner -c "SELECT 1;"

# 4. Check PgBouncer admin console
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d pgbouncer -c "SHOW POOLS;"
```

#### **Root Cause Analysis:**
```bash
# Check PgBouncer logs
tail -100 /var/log/postgresql/pgbouncer.log

# Check configuration
cat /etc/pgbouncer/pgbouncer.ini

# Verify PostgreSQL is accessible
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT version();"
```

#### **Common Fixes:**

**Process died:**
```bash
# Kill any remaining processes
pkill pgbouncer

# Start fresh
su - postgres -c "pgbouncer -d /etc/pgbouncer/pgbouncer.ini"

# Check status
ps aux | grep pgbouncer
```

**Configuration error:**
```bash
# Test config
pgbouncer -v /etc/pgbouncer/pgbouncer.ini

# Check for typos in:
nano /etc/pgbouncer/pgbouncer.ini

# Especially:
# - listen_port = 6432
# - listen_addr = 127.0.0.1
# - auth_file = /etc/pgbouncer/userlist.txt
```

**Pool saturated:**
```bash
# Check pool status
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 6432 -U admin -d pgbouncer -c "SHOW POOLS;"

# If all pools used, increase pool size
nano /etc/pgbouncer/pgbouncer.ini
# Change: default_pool_size = 25 → default_pool_size = 50

# Reload config
pkill -HUP pgbouncer
```

#### **Prevention:**
- Monitor pool usage
- Set appropriate pool sizes
- Regular log review
- Consider converting to systemd service for auto-restart

---

## 🟢 MINOR ISSUES (NON-CRITICAL)

### 🔵 **"Grafana dashboard not loading"**

#### **Symptoms:**
- Can't access https://enterprisescanner.com/grafana
- 502 Bad Gateway error
- Dashboard shows no data

#### **Quick Fix:**
```bash
# 1. Check if Grafana is running
docker ps | grep grafana

# 2. Restart Grafana
docker restart enterprisescanner_grafana

# 3. Check Nginx reverse proxy config
nginx -t
cat /etc/nginx/sites-available/enterprisescanner | grep grafana

# 4. Reload Nginx
systemctl reload nginx

# 5. Test access
curl -I https://enterprisescanner.com/grafana
```

#### **Common Issues:**

**No data in dashboards:**
```bash
# Check if Prometheus is running
docker ps | grep prometheus

# Check Prometheus targets
curl http://127.0.0.1:9090/api/v1/targets | jq

# Restart Prometheus
docker restart enterprisescanner_prometheus

# Restart all exporters
docker restart enterprisescanner_redis_exporter
```

**Can't log in:**
```bash
# Reset Grafana admin password
docker exec -it enterprisescanner_grafana grafana-cli admin reset-admin-password NewPassword123

# Or access Grafana logs
docker logs enterprisescanner_grafana --tail 50
```

---

### 🔵 **"Performance dashboard not updating"**

#### **Symptoms:**
- /performance page shows old data
- latest.json not updating
- Performance test hasn't run

#### **Quick Fix:**
```bash
# 1. Run performance test manually
/usr/local/bin/run_performance_test.sh

# 2. Check if file updated
ls -lh /var/www/html/performance/latest.json
cat /var/www/html/performance/latest.json | jq

# 3. Check cron job
crontab -l | grep performance

# 4. Check test log
tail -50 /var/log/performance_test.log
```

#### **Common Issues:**

**Cron not running:**
```bash
# Check if cron service is running
systemctl status cron

# Re-add cron job
crontab -e
# Add: 0 * * * * /usr/local/bin/run_performance_test.sh

# Verify
crontab -l
```

**Script failing:**
```bash
# Check script permissions
ls -l /usr/local/bin/run_performance_test.sh
chmod +x /usr/local/bin/run_performance_test.sh

# Run manually and check errors
/usr/local/bin/run_performance_test.sh
echo $?  # Should be 0 for success
```

---

### 🔵 **"High disk usage"**

#### **Symptoms:**
- `df -h` shows >90% disk usage
- Services failing to write
- "No space left on device" errors

#### **Quick Fix (Find and Clear):**
```bash
# 1. Check disk usage
df -h

# 2. Find largest directories
du -h / | sort -rh | head -20

# 3. Common culprits:

# Clear old logs
> /var/log/nginx/access.log
> /var/log/nginx/error.log

# Clear Docker logs
docker system prune -a -f

# Clear old packages
apt autoremove -y
apt clean

# Clear systemd journal
journalctl --vacuum-time=7d

# 4. Verify
df -h
```

#### **Long-term Solutions:**
```bash
# Enable log rotation
nano /etc/logrotate.d/nginx
# Ensure rotation is configured

# Limit Docker log size
nano /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
systemctl restart docker

# Schedule weekly cleanup
crontab -e
# Add: 0 0 * * 0 docker system prune -af
```

---

### 🔵 **"Email not sending"**

#### **Symptoms:**
- Contact form submissions don't send emails
- No emails received at Google Workspace addresses
- SMTP errors in application logs

#### **Quick Diagnosis:**
```bash
# 1. Verify Google Workspace credentials
# Check .env.production file
cat .env.production | grep MAIL

# 2. Test SMTP connection
telnet smtp.gmail.com 587
# Should connect, then type 'quit'

# 3. Check application logs
tail -100 /var/log/enterprisescanner/app.log | grep -i mail

# 4. Test from command line (if mail command available)
echo "Test email" | mail -s "Test from server" support@enterprisescanner.com
```

#### **Common Fixes:**

**Invalid credentials:**
```env
# Update .env.production
MAIL_USERNAME=info@enterprisescanner.com
MAIL_PASSWORD=<CORRECT_APP_PASSWORD>

# For Google Workspace, use App Password, not account password
# Generate at: https://myaccount.google.com/apppasswords
```

**Firewall blocking port 587:**
```bash
# Check if port is reachable
nc -zv smtp.gmail.com 587

# If blocked, check UFW
ufw status
# Allow outbound SMTP if needed
ufw allow out 587/tcp
```

**MAIL_USE_TLS not set:**
```env
# Ensure in .env.production:
MAIL_USE_TLS=True
MAIL_PORT=587
```

---

## 📊 MONITORING & ALERTS

### Set Up Basic Monitoring

**1. External uptime monitoring (free):**
- UptimeRobot: https://uptimerobot.com (free)
- Add monitor for https://enterprisescanner.com
- Email alerts when down

**2. Disk space alerts:**
```bash
# Create alert script
nano /usr/local/bin/disk_alert.sh

#!/bin/bash
THRESHOLD=90
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $USAGE -gt $THRESHOLD ]; then
    echo "Disk usage is ${USAGE}% on $(hostname)" | mail -s "ALERT: High Disk Usage" support@enterprisescanner.com
fi

chmod +x /usr/local/bin/disk_alert.sh

# Run daily
crontab -e
0 12 * * * /usr/local/bin/disk_alert.sh
```

**3. Service health checks:**
```bash
# Create health check script
nano /usr/local/bin/health_check.sh

#!/bin/bash
systemctl is-active --quiet nginx || systemctl restart nginx
docker ps -q --filter "name=enterprisescanner_redis" --filter "status=exited" | xargs -r docker restart
docker ps -q --filter "name=enterprisescanner_postgres" --filter "status=exited" | xargs -r docker restart

chmod +x /usr/local/bin/health_check.sh

# Run every 5 minutes
crontab -e
*/5 * * * * /usr/local/bin/health_check.sh
```

---

## 🔍 DIAGNOSTIC COMMANDS REFERENCE

```bash
# Quick health check (run this first)
systemctl status nginx && docker ps && df -h && free -h

# Check all logs at once
tail -20 /var/log/nginx/error.log && \
docker logs enterprisescanner_redis --tail 20 && \
docker logs enterprisescanner_postgres --tail 20

# Network connectivity
ping -c 3 8.8.8.8          # Internet
ping -c 3 134.199.147.45   # Server IP
curl -I https://enterprisescanner.com  # Website

# Service ports
netstat -tulpn | grep LISTEN  # All listening ports
lsof -i :443                   # What's on port 443
lsof -i :6379                  # Redis
lsof -i :5432                  # PostgreSQL

# Resource usage
top -bn1 | head -20           # CPU usage
free -h                       # Memory
df -h                         # Disk
iostat -x 1 5                 # Disk I/O

# Database health
docker exec enterprisescanner_postgres pg_isready -U admin
PGPASSWORD='SecurePass2024!' psql -h 127.0.0.1 -p 5432 -U admin -d enterprisescanner -c "SELECT count(*) FROM pg_stat_activity;"

# Redis health
docker exec enterprisescanner_redis redis-cli PING
docker exec enterprisescanner_redis redis-cli INFO stats

# Certificate check
certbot certificates
openssl x509 -in /etc/letsencrypt/live/enterprisescanner.com/cert.pem -noout -dates
```

---

## 📞 ESCALATION PROCEDURES

### Level 1: Self-Service (This Playbook)
- Use this playbook first
- 90% of issues resolve here
- Time: 5-15 minutes

### Level 2: DigitalOcean Support
- If server hardware issues
- If network connectivity issues
- Access console: https://cloud.digitalocean.com
- Support: https://www.digitalocean.com/support

### Level 3: Full Restoration
- If all else fails, restore from backup
- Rebuild server from INFRASTRUCTURE_MAP.md
- Re-deploy services from docker-compose.yml

---

## 📚 RELATED DOCUMENTATION

- **INFRASTRUCTURE_MAP.md** - Complete system reference
- **COMMON_COMMANDS.md** - Command reference
- **SERVICE_DEPENDENCIES.md** - Architecture and dependencies
- **.github/ai-context.md** - Project context

---

## 💡 PREVENTION CHECKLIST

Weekly:
- [ ] Check disk usage: `df -h`
- [ ] Review Nginx error logs
- [ ] Verify SSL certificate expiry
- [ ] Check Docker container status
- [ ] Review performance metrics

Monthly:
- [ ] Update system packages: `apt update && apt upgrade`
- [ ] Rotate logs manually if needed
- [ ] Review and archive old backups
- [ ] Test restoration procedures
- [ ] Review and update this playbook

Quarterly:
- [ ] Full security audit
- [ ] Review all credentials
- [ ] Test disaster recovery plan
- [ ] Evaluate resource usage trends
- [ ] Plan capacity upgrades if needed

---

**Last Updated:** October 16, 2025  
**Next Review:** Monthly or after major incidents

**Remember:** When in doubt, check logs first! Most issues reveal themselves in `/var/log/nginx/error.log` or Docker container logs.
