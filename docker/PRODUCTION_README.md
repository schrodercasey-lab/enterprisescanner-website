# Enterprise Scanner - Production Deployment Guide

## 🚀 Overview

This production deployment package includes:
- **Nginx** reverse proxy with SSL/TLS support
- **Gunicorn** WSGI servers for all 7 microservices
- **PostgreSQL** database with full schema
- **Redis** for caching and session management
- Automated health checks and monitoring
- Database backup and rollback capabilities
- SSL certificate management

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or Windows Server 2019+
- **RAM**: Minimum 8GB, recommended 16GB+
- **CPU**: Minimum 4 cores, recommended 8+ cores
- **Disk**: Minimum 50GB SSD storage
- **Network**: Static IP address, ports 80/443 open

### Software Requirements
- Docker 20.10+
- Docker Compose 1.29+
- OpenSSL (for SSL certificates)
- Git (for version control)

## 🛠️ Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd workspace/docker
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your production values
nano .env
```

**Critical settings to update:**
- `POSTGRES_PASSWORD` - Strong database password
- `REDIS_PASSWORD` - Strong Redis password
- `SECRET_KEY` - Random 64-character string
- `SENDGRID_API_KEY` - Your SendGrid API key
- `STRIPE_SECRET_KEY` - Your Stripe secret key
- `SSL_CERT_EMAIL` - Your email for Let's Encrypt

### 3. Generate SSL Certificates

**For Production (Let's Encrypt):**
```bash
chmod +x setup-ssl.sh
./setup-ssl.sh production
```

**For Development (Self-signed):**
```bash
chmod +x setup-ssl.sh
./setup-ssl.sh
```

### 4. Deploy Services

**Linux/Mac:**
```bash
chmod +x deploy-production.sh
./deploy-production.sh
```

**Windows PowerShell:**
```powershell
.\deploy-production.ps1
```

The script will:
1. Validate prerequisites
2. Backup existing deployment
3. Build all Docker images
4. Start all services
5. Run health checks
6. Display access URLs

## 🏗️ Architecture

```
                    Internet
                       |
                       v
                  [Nginx :80/443]
                       |
        +--------------+---------------+
        |              |               |
   [Chat:5001]  [Assessment:5002] [Analytics:5003]
        |              |               |
        +------+-------+-------+-------+
               |               |
          [PostgreSQL]    [Redis]
```

## 📊 Service Endpoints

All services are accessible through Nginx reverse proxy:

- **Main Website**: https://enterprisescanner.com/
- **Live Chat**: https://enterprisescanner.com/chat/
- **Security Assessment**: https://enterprisescanner.com/assessment/
- **Analytics Dashboard**: https://enterprisescanner.com/analytics/
- **API Documentation**: https://enterprisescanner.com/api-docs/
- **Partner Portal**: https://enterprisescanner.com/partner/
- **Client Onboarding**: https://enterprisescanner.com/onboarding/
- **Performance Monitoring**: https://enterprisescanner.com/monitoring/

## 🔧 Management Commands

### View Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f enterprise_chat_system
```

### Restart Services
```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart nginx
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Update Services
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## 🗄️ Database Management

### Backup Database
```bash
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U admin enterprisescanner > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker-compose -f docker-compose.prod.yml exec -T postgres \
    psql -U admin enterprisescanner < backup_20250101.sql
```

### Connect to Database
```bash
docker-compose -f docker-compose.prod.yml exec postgres \
    psql -U admin enterprisescanner
```

## 🔒 Security Best Practices

### 1. Update Secrets
- Change all default passwords in `.env`
- Use strong, random passwords (minimum 32 characters)
- Never commit `.env` to version control

### 2. SSL/TLS
- Use Let's Encrypt for production certificates
- Enable HSTS headers (already configured in nginx.conf)
- Set up auto-renewal for SSL certificates

### 3. Firewall Configuration
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 4. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
```

## 📈 Monitoring & Health Checks

### Built-in Health Endpoints
Each service exposes a `/health` endpoint:
- http://localhost:5001/health (Chat)
- http://localhost:5002/health (Assessment)
- http://localhost:5003/health (Analytics)
- etc.

### Monitor Service Health
```bash
# Check all services
for port in 5001 5002 5003 5004 5005 5006 5007; do
    echo "Port $port:"
    curl -s http://localhost:$port/health | jq .
done
```

### View Resource Usage
```bash
docker stats
```

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check specific service
docker-compose -f docker-compose.prod.yml logs enterprise_chat_system

# Verify environment
docker-compose -f docker-compose.prod.yml config
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# View PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres
```

### Nginx 502 Errors
```bash
# Check if backend services are running
docker-compose -f docker-compose.prod.yml ps

# Test backend health
curl http://localhost:5001/health
```

### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in ssl/fullchain.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

## 🔄 Automated Backups

### Setup Cron Job for Daily Backups
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/workspace/docker && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U admin enterprisescanner > backups/backup_$(date +\%Y\%m\%d).sql
```

## 📞 Support

For issues or questions:
- **Email**: support@enterprisescanner.com
- **Documentation**: https://enterprisescanner.com/api-docs/
- **Status Page**: https://enterprisescanner.com/monitoring/

## 📝 License

Copyright © 2025 Enterprise Scanner. All rights reserved.
