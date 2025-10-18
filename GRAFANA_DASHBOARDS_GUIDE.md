# 📊 Grafana Dashboards - Quick Reference Guide

**Access URL:** https://enterprisescanner.com/grafana  
**Username:** `admin`  
**Password:** `Admin123!`

---

## 🎯 Available Dashboards

### 1. 🏢 **Enterprise Scanner - System Overview**
**Direct URL:** https://enterprisescanner.com/grafana/d/enterprisescanner-overview

**Purpose:** Executive-level overview of platform health and performance

**Key Metrics Displayed:**
- ⏱️ **System Uptime** - Server uptime in seconds
- 🔥 **CPU Usage %** - Real-time CPU utilization
- 💾 **Memory Usage %** - RAM consumption percentage  
- 🔌 **DB Connections** - Active PostgreSQL connections

**Graphs (30-second refresh):**
- CPU Usage Over Time (5-minute intervals)
- Memory Usage Over Time (5-minute intervals)
- Database Size Growth (tracks data growth)
- Network Traffic (RX/TX rates)

**Best For:** Quick system health checks, executive reporting, incident response

---

### 2. 📈 **Node Exporter Full**
**Direct URL:** https://enterprisescanner.com/grafana/d/node-exporter-full

**Purpose:** Detailed system resource monitoring

**Key Metrics Displayed:**
- 🖥️ **CPU Usage** - Per-core breakdown and idle time
- 🧠 **Memory Usage** - Available vs. total memory
- 💿 **Disk Usage** - Filesystem usage percentages
- 🌐 **Network Traffic** - Receive/transmit bytes per second

**Refresh Rate:** 30 seconds

**Best For:** Performance troubleshooting, capacity planning, system optimization

---

### 3. 🗄️ **PostgreSQL Database**
**Direct URL:** https://enterprisescanner.com/grafana/d/postgresql-db

**Purpose:** Database performance and health monitoring

**Key Metrics Displayed:**
- 🔗 **Active Connections** - Current connections to `enterprisescanner` database
- 📦 **Database Size** - Total size in bytes
- ⚡ **Transaction Rate** - Commits per second
- 📊 **Rows Fetched** - Query performance metric

**Refresh Rate:** 30 seconds

**Best For:** Database performance tuning, query optimization, connection management

---

## 🚀 Quick Access Commands

### Check All Dashboards
```bash
curl -s -u admin:Admin123! http://localhost:3000/api/search | grep -o '"title":"[^"]*"'
```

### Verify Prometheus Data
```bash
curl -s http://localhost:9090/api/v1/query?query=up | grep '"value"'
```

### Check Dashboard Health
```bash
curl -s -u admin:Admin123! http://localhost:3000/api/health
```

---

## 📱 Dashboard Features

### Navigation
- **Home** - Click Grafana logo top-left
- **Search** - Click search icon or press `/`
- **Dashboards** - Left sidebar → Dashboards
- **Explore** - Left sidebar → Explore (ad-hoc queries)

### Time Range Selection
- Top-right corner: "Last 6 hours" dropdown
- Options: 5m, 15m, 1h, 6h, 12h, 24h, 7d, 30d
- Custom range picker available

### Panel Actions
- **Zoom** - Click and drag on any graph
- **Full Screen** - Click panel title → View
- **Edit** - Click panel title → Edit (admin only)
- **Share** - Click panel title → Share → Link

### Refresh Rates
- All dashboards: 30-second auto-refresh
- Adjustable: Top-right refresh dropdown
- Options: 5s, 10s, 30s, 1m, 5m, 15m, 30m, 1h, 2h, 1d

---

## 🎨 Customization Tips

### Adding New Panels
1. Click "Add panel" (top-right)
2. Select visualization type (Graph, Stat, Gauge, etc.)
3. Add Prometheus query (PromQL)
4. Configure display options
5. Save dashboard

### Popular PromQL Queries

**CPU Usage:**
```promql
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory Usage:**
```promql
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

**Disk Space Used:**
```promql
(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100
```

**Network RX Rate:**
```promql
rate(node_network_receive_bytes_total[5m])
```

**PostgreSQL Connection Count:**
```promql
pg_stat_database_numbackends{datname="enterprisescanner"}
```

**Database Size:**
```promql
pg_database_size_bytes{datname="enterprisescanner"}
```

---

## 🔔 Setting Up Alerts (Future Enhancement)

### Alert Targets (To Be Configured)
- Email notifications
- Slack integration
- PagerDuty escalation
- Webhook endpoints

### Recommended Alert Rules
- CPU usage > 80% for 5 minutes
- Memory usage > 90% for 5 minutes
- Disk usage > 85%
- Database connections > 100
- Service down (up == 0)

---

## 📊 Dashboard URLs Summary

| Dashboard | URL |
|-----------|-----|
| **Home** | https://enterprisescanner.com/grafana |
| **Enterprise Scanner Overview** | https://enterprisescanner.com/grafana/d/enterprisescanner-overview |
| **Node Exporter Full** | https://enterprisescanner.com/grafana/d/node-exporter-full |
| **PostgreSQL Database** | https://enterprisescanner.com/grafana/d/postgresql-db |

---

## 🔐 Security Notes

- ✅ HTTPS-only access via Nginx reverse proxy
- ✅ Authentication required (admin/Admin123!)
- ✅ Metrics endpoints bound to localhost only
- ✅ No external access to Prometheus/exporters
- ⚠️ **Change default password after first login!**

### Change Admin Password
1. Login to Grafana
2. Click admin icon (bottom-left)
3. Profile → Change Password
4. Save new password securely

---

## 🛠️ Troubleshooting

### Dashboard Shows "No Data"
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check data source in Grafana
curl -u admin:Admin123! http://localhost:3000/api/datasources
```

### Graphs Not Updating
```bash
# Restart Grafana
docker restart grafana

# Check Prometheus scraping
docker logs prometheus | tail -20
```

### Can't Access Grafana
```bash
# Check Nginx configuration
nginx -t

# Check Grafana container
docker ps | grep grafana
docker logs grafana | tail -20
```

---

## 📈 Performance Baseline (October 16, 2025)

**System Status:**
- CPU Usage: ~5-10% (normal load)
- Memory Usage: ~30-40% (with monitoring stack)
- Database Size: 2.2KB (initial deployment)
- DB Connections: 1-2 (minimal activity)
- Uptime: 9+ minutes (monitoring deployment)

**Expected Growth:**
- Database: +100MB/month (with moderate activity)
- Memory: Stable at 40-50% with full production load
- CPU: Spikes to 40-60% during active scans
- Connections: 5-20 concurrent users in production

---

## 🎉 Next Steps

1. ✅ **Login to Grafana** - https://enterprisescanner.com/grafana
2. ✅ **Explore all 3 dashboards** - Familiarize with layouts
3. ⏳ **Change admin password** - Security best practice
4. ⏳ **Star important dashboards** - Quick access from home
5. ⏳ **Set up mobile access** - Grafana mobile app available
6. ⏳ **Configure alerts** - Proactive monitoring (future)

---

**Dashboard Setup Completed:** October 16, 2025  
**Total Dashboards:** 3 (custom + 2 imported)  
**Metrics Collected:** 500+ data points  
**Refresh Rate:** 30 seconds  
**Data Retention:** 30 days (Prometheus)

🎊 **Your monitoring platform is fully operational!**
