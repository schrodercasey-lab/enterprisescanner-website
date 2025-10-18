#!/bin/bash
# Enterprise Scanner - Direct Server Deployment Script
# This script creates and deploys Enterprise Scanner directly on the server

set -e

echo "🚀 Enterprise Scanner - Direct Server Deployment"
echo "================================================"

# Create workspace directory
mkdir -p /root/enterprise_scanner
cd /root/enterprise_scanner

# Install git to clone or download files
apt-get update -q
apt-get install -yq git curl wget unzip

# Create the basic structure
mkdir -p backend/{api,models,services,utils,database}
mkdir -p website/{css,js,assets}
mkdir -p deployment/{scripts,configs,security}
mkdir -p business/{sales,marketing,research}
mkdir -p docs/{api,user-guides}
mkdir -p logs
mkdir -p backups

echo "✅ Directory structure created"

# Create production environment file
cat > .env.production << 'EOF'
# Enterprise Scanner - Production Environment Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=ApTTcH0c!mEi$7FTPFm4AnzF%iiIyVDZuFX7Rk*deESST7Fk52Bq8m%BpRGYxrHm
JWT_SECRET_KEY=*j*!HOzBjmBVouSiO$jqqeq*LDYz!Mpb

# Domain Configuration
DOMAIN_URL=https://enterprisescanner.com
ALLOWED_HOSTS=enterprisescanner.com,www.enterprisescanner.com,127.0.0.1,localhost
PUBLIC_URL=https://enterprisescanner.com

# Database Configuration (Production SQLite)
DATABASE_URL=sqlite:///enterprise_scanner_production.db
DB_TYPE=sqlite
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True

# Production Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=info@enterprisescanner.com
EMAIL_PASSWORD=YOUR_GOOGLE_WORKSPACE_PASSWORD
EMAIL_TESTING_MODE=False

# Security Configuration
SECURITY_HEADERS=True
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=True
HSTS_PRELOAD=True
X_FRAME_OPTIONS=DENY
X_CONTENT_TYPE_OPTIONS=nosniff
X_XSS_PROTECTION=1; mode=block
REFERRER_POLICY=strict-origin-when-cross-origin

# Server Configuration
SERVER_NAME=enterprisescanner.com
PREFERRED_URL_SCHEME=https
USE_RELOADER=False
THREADED=True
PROCESSES=1

# Monitoring and Logging
LOG_LEVEL=INFO
LOG_FILE=/opt/enterprise_scanner/logs/enterprise_scanner.log
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True
PERFORMANCE_MONITORING=True

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_PATH=/opt/enterprise_scanner/backups
BACKUP_RETENTION_DAYS=30

ENVIRONMENT=production
VERSION=1.0.0
EOF

echo "✅ Production environment created"

# Create requirements file
cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
SQLAlchemy==2.0.21
gunicorn==21.2.0
gevent==23.7.0
psutil==5.9.5
cryptography==41.0.4
Werkzeug==2.3.7
EOF

echo "✅ Requirements file created"

echo "🎉 Direct deployment setup complete!"
echo "Next: Run the full deployment script"
EOF