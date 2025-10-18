# Service Dependencies - Enterprise Scanner
**Visual architecture and dependency mapping**  
**Last Updated:** October 16, 2025

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                  │
│                              ↓                                       │
│                    enterprisescanner.com                            │
│                    (DNS: 8.8.8.8, 1.1.1.1)                         │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    DIGITALOCEAN DROPLET                             │
│                      134.199.147.45                                 │
│                   Ubuntu 22.04.5 LTS                                │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    LET'S ENCRYPT SSL/TLS                            │
│                      Certificate (A+ Rating)                         │
│              /etc/letsencrypt/live/enterprisescanner.com/           │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    NGINX 1.18.0 (Port 443)                          │
│                    - Gzip Compression (80%)                          │
│                    - Browser Caching Headers                         │
│                    - SSL Termination                                 │
│                    - Reverse Proxy (Grafana)                         │
│                    - Static File Serving                             │
└─────────────────────────────────────────────────────────────────────┘
            ↓                    ↓                        ↓
    ┌───────────┐       ┌────────────┐          ┌────────────┐
    │  Static   │       │   Future   │          │  Grafana   │
    │   Files   │       │ Flask App  │          │  Reverse   │
    │ /var/www/ │       │  (Backend) │          │   Proxy    │
    │   html/   │       │            │          │   /grafana │
    └───────────┘       └────────────┘          └────────────┘
                               ↓                        ↓
                    ┌──────────┴──────────┐    ┌───────────────┐
                    ↓                     ↓    │   Grafana     │
            ┌───────────┐         ┌──────────┐│  Container    │
            │   Redis   │         │ PgBouncer││  (Port 3000)  │
            │  Cache    │         │Connection││               │
            │ Container │         │  Pooler  ││               │
            │127.0.0.1: │         │127.0.0.1:││               │
            │   6379    │         │   6432   ││               │
            └───────────┘         └──────────┘│               │
                                       ↓      └───────────────┘
                                ┌────────────┐        ↓
                                │PostgreSQL  │ ┌─────────────┐
                                │ Container  │ │ Prometheus  │
                                │127.0.0.1:  │ │  Container  │
                                │   5432     │ │127.0.0.1:   │
                                └────────────┘ │    9090     │
                                       ↑       └─────────────┘
                                       │              ↑
                            ┌──────────┴──────┐      │
                            │                 │      │
                    ┌───────────────┐  ┌──────────────┐
                    │ Redis Exporter│  │    Node      │
                    │   Container   │  │  Exporter    │
                    │  127.0.0.1:   │  │  Container   │
                    │     9121      │  │ 127.0.0.1:   │
                    └───────────────┘  │    9100      │
                            ↓          └──────────────┘
                            │                 ↓
                    ┌───────────────────────────┐
                    │  Postgres Exporter        │
                    │     Container             │
                    │    127.0.0.1:9187        │
                    └───────────────────────────┘
```

---

## 🔗 DEPENDENCY CHAIN

### **Layer 1: External Services**
```
Internet → DNS (Google/Cloudflare) → 134.199.147.45
```
**Dependencies:** Domain registrar, DNS providers  
**Failure Impact:** Website unreachable  
**Monitoring:** DNS health checks, domain expiration alerts

---

### **Layer 2: SSL/TLS Termination**
```
Let's Encrypt Certificate → Nginx SSL Configuration
```
**Dependencies:** Let's Encrypt API, Certbot, Nginx  
**Failure Impact:** Browser security warnings, HTTPS unavailable  
**Monitoring:** Certificate expiration (auto-renews 30 days before expiry)  
**Manual Check:** `certbot certificates`

---

### **Layer 3: Web Server (Nginx)**
```
Nginx → Static Files (/var/www/html/)
Nginx → Future Flask App (when deployed)
Nginx → Grafana Reverse Proxy (/grafana → http://grafana:3000)
```
**Dependencies:** Ubuntu filesystem, Let's Encrypt certs, config files  
**Failure Impact:** Entire website down  
**Monitoring:** `systemctl status nginx`, health checks  
**Logs:** `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

---

### **Layer 4: Application Backend (Future)**
```
Flask App → Redis (caching)
Flask App → PgBouncer → PostgreSQL (data)
```
**Dependencies:** Python runtime, Redis, PostgreSQL, PgBouncer  
**Failure Impact:** Dynamic features broken, API unavailable  
**Current Status:** Ready but not yet deployed (using static HTML)

---

### **Layer 5: Data Layer**

#### **Redis Cache**
```
Redis Container (127.0.0.1:6379)
├── Future Flask App (caching)
└── Redis Exporter (metrics) → Prometheus
```
**Dependencies:** Docker, Redis image, disk space for persistence  
**Failure Impact:** Performance degradation (no cached data)  
**Graceful Degradation:** App can function without Redis, just slower  
**Monitoring:** Redis Exporter → Prometheus → Grafana  
**Health Check:** `docker exec enterprisescanner_redis redis-cli PING`

#### **PostgreSQL Database**
```
PostgreSQL Container (127.0.0.1:5432)
├── PgBouncer → Future Flask App
└── Postgres Exporter (metrics) → Prometheus
```
**Dependencies:** Docker, PostgreSQL image, disk space for data  
**Failure Impact:** No persistent data, app unusable  
**Critical Service:** YES - database failure = total app failure  
**Monitoring:** Postgres Exporter → Prometheus → Grafana  
**Health Check:** `docker exec enterprisescanner_postgres pg_isready`

#### **PgBouncer Connection Pooler**
```
PgBouncer (127.0.0.1:6432) → PostgreSQL (127.0.0.1:5432)
```
**Dependencies:** PostgreSQL running, PgBouncer binary, config file  
**Failure Impact:** Connection pool exhaustion, performance issues  
**Graceful Degradation:** App can connect directly to PostgreSQL  
**Monitoring:** PgBouncer logs, pool status queries  
**Admin Console:** `psql -h 127.0.0.1 -p 6432 -d pgbouncer`

---

### **Layer 6: Monitoring & Observability**

#### **Prometheus (Metrics Collection)**
```
Prometheus (127.0.0.1:9090)
├── Scrapes Redis Exporter (127.0.0.1:9121)
├── Scrapes Node Exporter (127.0.0.1:9100)
└── Scrapes Postgres Exporter (127.0.0.1:9187)
```
**Dependencies:** Docker, Prometheus image, config file  
**Failure Impact:** No metrics collection, blind to performance  
**Critical Service:** NO - app functions without it  
**Access:** http://127.0.0.1:9090 (localhost only)

#### **Grafana (Dashboards)**
```
Grafana (Internal Port 3000)
├── Nginx Reverse Proxy → https://enterprisescanner.com/grafana
└── Data Source: Prometheus (http://prometheus:9090)
```
**Dependencies:** Docker, Grafana image, Prometheus, Nginx proxy  
**Failure Impact:** No visual dashboards, metrics still collected  
**Critical Service:** NO - monitoring/visibility only  
**Access:** https://enterprisescanner.com/grafana (public via Nginx)

#### **Exporters**
```
Redis Exporter → Redis metrics → Prometheus
Node Exporter → System metrics → Prometheus
Postgres Exporter → Database metrics → Prometheus
```
**Dependencies:** Respective services (Redis, OS, PostgreSQL)  
**Failure Impact:** Missing metrics for that component  
**Critical Services:** NO - monitoring only

---

## 🎯 CRITICAL PATH ANALYSIS

### **What Must Work for Website to Function?**

#### **Minimum Viable System (Current - Static Website)**
```
✅ CRITICAL:
1. Internet connectivity
2. DNS resolution (enterprisescanner.com → 134.199.147.45)
3. Let's Encrypt SSL certificate (valid)
4. Nginx web server (running)
5. Static HTML files (/var/www/html/)

❌ NOT CRITICAL (can fail without breaking site):
- Redis (not yet integrated)
- PostgreSQL (not yet integrated)
- PgBouncer (not yet integrated)
- Prometheus (monitoring only)
- Grafana (monitoring only)
- All Exporters (monitoring only)
```

#### **Future Dynamic System (Flask App Deployed)**
```
✅ CRITICAL:
1-5. (Same as above)
6. Flask application (running)
7. PostgreSQL database (running)
8. PgBouncer connection pooler (running)

⚠️ IMPORTANT (performance impact):
9. Redis cache (running)

❌ NOT CRITICAL:
- Prometheus (monitoring only)
- Grafana (monitoring only)
- All Exporters (monitoring only)
```

---

## 🔄 DEPENDENCY MATRIX

| Service | Depends On | Depended On By | Failure Impact |
|---------|-----------|----------------|----------------|
| **Internet** | None | All services | 🔴 TOTAL OUTAGE |
| **DNS** | Domain registrar | Internet users | 🔴 TOTAL OUTAGE |
| **SSL Cert** | Let's Encrypt | Nginx | 🟡 Security warnings |
| **Nginx** | SSL, filesystem | Website access | 🔴 TOTAL OUTAGE |
| **Static Files** | Nginx | Users | 🔴 TOTAL OUTAGE |
| **Flask App** | Nginx, Redis, PgBouncer | API consumers | 🔴 App unusable |
| **Redis** | Docker | Flask App | 🟡 Performance degraded |
| **PostgreSQL** | Docker | PgBouncer, Flask | 🔴 App unusable |
| **PgBouncer** | PostgreSQL | Flask App | 🟡 Can bypass to direct |
| **Prometheus** | Exporters | Grafana | 🟢 Monitoring blind |
| **Grafana** | Prometheus, Nginx | Ops team | 🟢 No dashboards |
| **Redis Exporter** | Redis | Prometheus | 🟢 Missing metrics |
| **Node Exporter** | OS | Prometheus | 🟢 Missing metrics |
| **Postgres Exporter** | PostgreSQL | Prometheus | 🟢 Missing metrics |

**Legend:**
- 🔴 Critical: Service outage or major functionality loss
- 🟡 Important: Performance degradation or reduced functionality
- 🟢 Non-critical: Monitoring/visibility only

---

## 🚨 FAILURE SCENARIOS & IMPACT

### **Scenario 1: Nginx Crashes**
```
Failure: Nginx process dies
Impact: 🔴 TOTAL OUTAGE - Website unreachable
Cascade: None (other services continue running)
Detection: Health checks, monitoring alerts
Recovery: systemctl restart nginx (15 seconds)
Prevention: Keep Nginx config tested, monitor resource usage
```

### **Scenario 2: PostgreSQL Container Stops**
```
Failure: PostgreSQL container crashes
Impact: 
  - Current (Static Site): 🟢 No impact
  - Future (Flask App): 🔴 App unusable - database unavailable
Cascade: PgBouncer can't connect, Flask errors, Postgres Exporter fails
Detection: Health checks, Prometheus alerts
Recovery: docker restart enterprisescanner_postgres (30 seconds)
Prevention: Monitor database health, disk space, memory
```

### **Scenario 3: Redis Container Stops**
```
Failure: Redis container crashes
Impact:
  - Current (Static Site): 🟢 No impact
  - Future (Flask App): 🟡 Performance degraded - no caching
Cascade: Redis Exporter fails, Flask app slower
Detection: Health checks, Prometheus alerts
Recovery: docker restart enterprisescanner_redis (10 seconds)
Graceful: Flask app can function without Redis cache
Prevention: Monitor memory usage, persistence, eviction policy
```

### **Scenario 4: SSL Certificate Expires**
```
Failure: Let's Encrypt certificate not renewed
Impact: 🟡 Browser security warnings - users scared away
Cascade: None (Nginx still serves content)
Detection: Certificate expiration monitoring (30 days before)
Recovery: certbot renew; systemctl reload nginx (30 seconds)
Prevention: Auto-renewal enabled, monitoring
```

### **Scenario 5: Disk Space Full**
```
Failure: Server runs out of disk space
Impact: 🔴 Multiple service failures
Cascade: 
  - PostgreSQL can't write (database errors)
  - Redis persistence fails
  - Logs can't write
  - Nginx errors
Detection: df -h monitoring, Prometheus node_exporter
Recovery: Clear logs, remove old files, upgrade droplet
Prevention: Monitor disk usage, implement log rotation
```

### **Scenario 6: PgBouncer Crashes**
```
Failure: PgBouncer process dies
Impact:
  - Current (Static Site): 🟢 No impact
  - Future (Flask App): 🟡 Connection pool unavailable
Cascade: Flask app can still connect directly to PostgreSQL (slower)
Detection: Process monitoring, connection errors
Recovery: su - postgres -c "pgbouncer -d /etc/pgbouncer/pgbouncer.ini"
Graceful: Apps can bypass and connect to PostgreSQL directly
Prevention: Monitor pool saturation, connection counts
```

### **Scenario 7: Prometheus/Grafana Down**
```
Failure: Monitoring stack crashes
Impact: 🟢 Blind to metrics, but services function normally
Cascade: No metrics collection, no dashboards
Detection: Can't access Grafana dashboard
Recovery: docker-compose restart prometheus grafana
Prevention: These services are non-critical to operations
```

### **Scenario 8: DNS Resolution Fails**
```
Failure: DNS provider outage or misconfiguration
Impact: 🔴 TOTAL OUTAGE - domain doesn't resolve
Cascade: None (server still running, just unreachable)
Detection: External monitoring, user reports
Recovery: Switch to backup DNS provider, update records
Prevention: Use multiple DNS providers (Google + Cloudflare)
```

---

## 🔧 TROUBLESHOOTING DECISION TREE

### **Website is Down**
```
1. Can you ping 134.199.147.45?
   NO → Check DigitalOcean status, network connectivity
   YES → Continue to 2

2. Is Nginx running?
   NO → systemctl start nginx
   YES → Continue to 3

3. Does nginx -t pass?
   NO → Fix Nginx config, restore from backup
   YES → Continue to 4

4. Is SSL certificate valid?
   NO → Run certbot renew
   YES → Continue to 5

5. Are static files present?
   NO → Restore from backup, re-upload
   YES → Check Nginx error logs
```

### **Performance is Slow**
```
1. Is Redis running and responding?
   NO → docker restart enterprisescanner_redis
   YES → Continue to 2

2. Is PostgreSQL responding?
   NO → docker restart enterprisescanner_postgres
   YES → Continue to 3

3. Is PgBouncer pool saturated?
   YES → Increase pool size or restart PgBouncer
   NO → Continue to 4

4. Is disk space low (<20%)?
   YES → Clear logs, remove old files
   NO → Continue to 5

5. Is CPU/memory high?
   YES → Identify processes with 'top', kill or restart
   NO → Check network latency, CDN performance
```

### **Database Connections Failing**
```
1. Is PostgreSQL container running?
   NO → docker restart enterprisescanner_postgres
   YES → Continue to 2

2. Can you connect directly to PostgreSQL?
   NO → Check PostgreSQL logs, restart if needed
   YES → Continue to 3

3. Is PgBouncer running?
   NO → Start PgBouncer
   YES → Continue to 4

4. Is PgBouncer pool full?
   YES → Increase pool size, restart connections
   NO → Check application connection strings
```

---

## 📊 SERVICE STARTUP ORDER

**Correct boot sequence for all services:**

```
1. Ubuntu OS boots
2. Docker daemon starts
3. Docker Compose brings up containers:
   a. PostgreSQL (database must be ready first)
   b. Redis (cache independent)
   c. Prometheus (metrics collector)
   d. Redis Exporter (depends on Redis)
   e. Node Exporter (system metrics)
   f. Postgres Exporter (depends on PostgreSQL)
   g. Grafana (depends on Prometheus)
4. PgBouncer starts (native service, depends on PostgreSQL)
5. Nginx starts (depends on SSL certs, Grafana for reverse proxy)
6. Future: Flask App starts (depends on all data services)
```

**Dependencies enforced by:**
- Docker Compose `depends_on` directive
- Systemd service dependencies
- Application retry logic

---

## 💡 OPTIMIZATION OPPORTUNITIES

### **Current Bottlenecks**
1. **Single Server** - No redundancy, single point of failure
2. **No Load Balancing** - Can't distribute traffic
3. **No Database Replication** - No read replicas
4. **No Redis Cluster** - Single cache instance

### **Future Improvements**
1. **Multi-Server Architecture** - Load balancer + 2+ app servers
2. **Database Read Replicas** - Separate read/write workloads
3. **Redis Cluster** - Distributed caching with failover
4. **CDN Integration** - CloudFlare/AWS CloudFront for static assets
5. **Geographic Redundancy** - Multi-region deployment

---

## 📚 RELATED DOCUMENTATION

- **INFRASTRUCTURE_MAP.md** - Complete infrastructure reference
- **COMMON_COMMANDS.md** - Frequently used commands
- **TROUBLESHOOTING_PLAYBOOK.md** - Issue resolution guide
- **.github/ai-context.md** - Project context for AI assistants

---

**Last Updated:** October 16, 2025  
**Next Review:** After Flask application deployment or major architecture changes
