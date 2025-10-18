# Enterprise Scanner - Quick Start Guide

## 🎯 Local Testing (5 Minutes)

### Option 1: Test Current Development Setup
Your services are already running in development mode!

Access at:
- http://localhost:5001 - Chat System
- http://localhost:5002 - Security Assessment
- http://localhost:5003 - Analytics Dashboard
- http://localhost:5004 - API Documentation
- http://localhost:5005 - Partner Portal
- http://localhost:5006 - Client Onboarding
- http://localhost:5007 - Performance Monitoring

### Option 2: Test Production Setup Locally

1. **Generate Self-Signed SSL Certificates**
   ```bash
   cd docker
   ./setup-ssl.sh
   ```

2. **Configure Environment**
   ```bash
   # .env already exists with development settings
   # No changes needed for local testing
   ```

3. **Deploy with Production Stack**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Wait for services** (30-60 seconds)

5. **Access via Nginx proxy:**
   - https://localhost/chat/
   - https://localhost/assessment/
   - https://localhost/analytics/
   - https://localhost/api-docs/
   - https://localhost/partner/
   - https://localhost/onboarding/
   - https://localhost/monitoring/

6. **Check health status:**
   ```bash
   curl http://localhost/health
   ```

## 🚀 Production Deployment

### Prerequisites Checklist
- [ ] Server with Ubuntu 20.04+ or Windows Server 2019+
- [ ] Domain name pointing to server IP
- [ ] Ports 80 and 443 open in firewall
- [ ] Docker and Docker Compose installed
- [ ] SendGrid API key for emails
- [ ] Stripe account for payments
- [ ] Strong passwords generated

### Step-by-Step Deployment

1. **SSH into your server**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Docker** (if not already installed)
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Clone repository**
   ```bash
   git clone <your-repo-url>
   cd workspace/docker
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Update all CHANGE_THIS values
   ```

5. **Setup SSL certificates**
   ```bash
   chmod +x setup-ssl.sh
   ./setup-ssl.sh production
   ```

6. **Deploy!**
   ```bash
   chmod +x deploy-production.sh
   ./deploy-production.sh
   ```

7. **Verify deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

## 📊 What You Get

### Infrastructure
✅ Nginx reverse proxy with SSL/TLS
✅ 7 microservices running on Gunicorn
✅ PostgreSQL database with full schema
✅ Redis for caching and sessions
✅ Automated health monitoring
✅ Database backup system
✅ Load balancing and rate limiting

### Services
✅ **Enterprise Chat System** - Real-time customer engagement
✅ **Interactive Security Assessment** - 15-minute vulnerability scans
✅ **Advanced Analytics Dashboard** - Real-time threat intelligence
✅ **API Documentation Portal** - Complete API reference
✅ **Partner Portal** - Channel partner management
✅ **Client Onboarding** - Automated 5-phase implementation
✅ **Performance Monitoring** - SLA tracking and alerts

### Security Features
✅ SSL/TLS encryption with Let's Encrypt
✅ Rate limiting (10 req/s general, 30 req/s API)
✅ Security headers (HSTS, XSS protection, etc.)
✅ CORS policy enforcement
✅ Health check endpoints
✅ Non-root Docker containers

## 🔧 Common Tasks

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Restart Service
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Scale Services
```bash
# Add more workers to a service
docker-compose -f docker-compose.prod.yml up -d --scale enterprise_chat_system=3
```

### Database Backup
```bash
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U admin enterprisescanner > backup.sql
```

### Update Code
```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 80
sudo lsof -i :80

# Stop the conflicting service
sudo systemctl stop apache2  # or nginx
```

### Services Not Starting
```bash
# Check logs for errors
docker-compose -f docker-compose.prod.yml logs

# Verify environment variables
docker-compose -f docker-compose.prod.yml config
```

### Can't Access Services
```bash
# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Check credentials in .env file
cat .env | grep POSTGRES
```

## 📈 Next Steps

1. ✅ **Test locally** - Verify all services work
2. ✅ **Deploy to staging** - Test in production-like environment
3. ✅ **Configure DNS** - Point domain to server
4. ✅ **Setup monitoring** - Configure alerts
5. ✅ **Load testing** - Verify performance
6. ✅ **Backup automation** - Schedule daily backups
7. ✅ **Go live!** - Deploy to production

## 📞 Need Help?

- 📖 Read the full [PRODUCTION_README.md](./PRODUCTION_README.md)
- 💬 Check service health: `curl http://localhost/health`
- 📊 View metrics: https://your-domain/monitoring/
- 📧 Contact: support@enterprisescanner.com

---

**Ready to deploy?** Run `./deploy-production.sh` and you're live in minutes! 🚀
