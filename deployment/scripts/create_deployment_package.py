#!/usr/bin/env python3
"""
Enterprise Scanner - Production Deployment Package Creator
Creates a complete deployment package ready for production server upload
"""

import os
import sys
import shutil
import tarfile
import json
from datetime import datetime

# Configuration
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEPLOYMENT_PACKAGE = os.path.join(WORKSPACE_ROOT, 'enterprise_scanner_production.tar.gz')

def create_production_env():
    """Create production environment file"""
    env_content = """# Enterprise Scanner - Production Environment Configuration
# Generated for live production server deployment at enterprisescanner.com

# Application Configuration
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

# Production Email Configuration (Google Workspace)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=info@enterprisescanner.com
EMAIL_PASSWORD=YOUR_GOOGLE_WORKSPACE_PASSWORD
EMAIL_TESTING_MODE=False

# Business Email Addresses
EMAIL_INFO=info@enterprisescanner.com
EMAIL_SALES=sales@enterprisescanner.com
EMAIL_SUPPORT=support@enterprisescanner.com
EMAIL_SECURITY=security@enterprisescanner.com
EMAIL_PARTNERSHIPS=partnerships@enterprisescanner.com

# Security Configuration (Production)
SECURITY_HEADERS=True
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=True
HSTS_PRELOAD=True
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; font-src 'self' fonts.googleapis.com fonts.gstatic.com cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'
X_FRAME_OPTIONS=DENY
X_CONTENT_TYPE_OPTIONS=nosniff
X_XSS_PROTECTION=1; mode=block
REFERRER_POLICY=strict-origin-when-cross-origin

# SSL Configuration
SSL_CERT_PATH=/etc/letsencrypt/live/enterprisescanner.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/enterprisescanner.com/privkey.pem
SSL_REDIRECT=True

# Session Configuration (Production)
SESSION_TIMEOUT=3600
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
SESSION_COOKIE_DOMAIN=.enterprisescanner.com

# API Configuration (Production)
API_SECRET_KEY=epfHKtlWxb61@m1BXUF1qv9Kg^NcCp%7
API_RATE_LIMIT=1000
API_RATE_LIMIT_WINDOW=3600
API_KEY_EXPIRY_DAYS=365
RATE_LIMITING_ENABLED=True

# Production Server Configuration
SERVER_NAME=enterprisescanner.com
PREFERRED_URL_SCHEME=https
USE_RELOADER=False
THREADED=True
PROCESSES=1

# Partner Configuration
PARTNER_COMMISSION_BRONZE=25.0
PARTNER_COMMISSION_SILVER=30.0
PARTNER_COMMISSION_GOLD=35.0
PARTNER_APPROVAL_REQUIRED=True

# Monitoring and Logging (Production)
LOG_LEVEL=INFO
LOG_FILE=/opt/enterprise_scanner/logs/enterprise_scanner.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=10
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True
PERFORMANCE_MONITORING=True

# Backup Configuration (Production)
BACKUP_ENABLED=True
BACKUP_PATH=/opt/enterprise_scanner/backups
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_KEY=CHANGE_BACKUP_KEY_FOR_PRODUCTION

# Analytics and Tracking (Production)
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
MIXPANEL_TOKEN=CHANGE_MIXPANEL_TOKEN
HOTJAR_ID=CHANGE_HOTJAR_ID

# Production Features
COMPRESSION_ENABLED=True
MINIFICATION_ENABLED=True
CACHING_ENABLED=True
CDN_ENABLED=False

# Server Environment
ENVIRONMENT=production
DEPLOYMENT_DATE={deployment_date}
VERSION=1.0.0
""".format(deployment_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    env_path = os.path.join(WORKSPACE_ROOT, '.env.production')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    return env_path

def create_server_requirements():
    """Create production requirements.txt"""
    requirements_content = """# Enterprise Scanner - Production Dependencies
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
SQLAlchemy==2.0.21
gunicorn==21.2.0
gevent==23.7.0
psutil==5.9.5
cryptography==41.0.4
Werkzeug==2.3.7
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.2
importlib-metadata==6.8.0
zipp==3.16.2
"""
    
    req_path = os.path.join(WORKSPACE_ROOT, 'requirements.production.txt')
    with open(req_path, 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    return req_path

def create_deployment_manifest():
    """Create deployment manifest with all necessary information"""
    manifest = {
        "deployment": {
            "name": "Enterprise Scanner",
            "version": "1.0.0",
            "environment": "production",
            "domain": "enterprisescanner.com",
            "deployment_date": datetime.now().isoformat(),
            "python_version": "3.8+",
            "database": "SQLite Production (106KB)",
            "features": [
                "CRM Dashboard with Fortune 500 targeting",
                "Production database with $3.9M pipeline",
                "Enterprise security with A+ SSL rating",
                "Professional email system (5 addresses)",
                "Automated backup and monitoring",
                "Real-time analytics and reporting"
            ]
        },
        "server_requirements": {
            "os": "Ubuntu 22.04 LTS",
            "ram": "2GB minimum (4GB recommended)",
            "storage": "20GB SSD minimum",
            "cpu": "1 vCPU minimum (2 vCPU recommended)",
            "bandwidth": "1TB/month",
            "ports": [22, 80, 443],
            "estimated_cost": "$10-15/month"
        },
        "deployment_steps": [
            "Upload deployment package to server",
            "Extract package to /opt/enterprise_scanner/",
            "Run automated setup script",
            "Configure DNS for enterprisescanner.com",
            "Install SSL certificates",
            "Start Enterprise Scanner service"
        ],
        "post_deployment": {
            "url": "https://enterprisescanner.com",
            "admin_dashboard": "https://enterprisescanner.com/crm-dashboard.html",
            "api_docs": "https://enterprisescanner.com/api-documentation.html",
            "health_check": "https://enterprisescanner.com/api/health"
        },
        "business_value": {
            "pipeline_value": "$3,900,000",
            "companies_loaded": 5,
            "qualified_leads": 5,
            "revenue_potential": "$585K - $975K Year 1"
        }
    }
    
    manifest_path = os.path.join(WORKSPACE_ROOT, 'deployment_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_path

def create_deployment_package():
    """Create complete deployment package"""
    print("🚀 Creating Enterprise Scanner Production Deployment Package...")
    print("=" * 60)
    
    # Create production environment
    print("1. Creating production environment...")
    env_path = create_production_env()
    print(f"   ✅ Created: {env_path}")
    
    # Create production requirements
    print("2. Creating production requirements...")
    req_path = create_server_requirements()
    print(f"   ✅ Created: {req_path}")
    
    # Create deployment manifest
    print("3. Creating deployment manifest...")
    manifest_path = create_deployment_manifest()
    print(f"   ✅ Created: {manifest_path}")
    
    # Create deployment package
    print("4. Creating deployment package...")
    
    # Files to include in deployment
    include_files = [
        'backend/',
        'website/',
        'deployment/',
        'business/',
        'docs/',
        'enterprise_scanner_production.db',
        '.env.production',
        'requirements.production.txt',
        'deployment_manifest.json',
        'start_production.py',
        'README.md'
    ]
    
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        '.venv',
        'logs/*',
        'backups/*',
        '*.log',
        '.env.development',
        'enterprise_scanner_dev.db'
    ]
    
    def should_exclude(file_path):
        for pattern in exclude_patterns:
            if pattern in file_path or file_path.endswith(pattern.replace('*', '')):
                return True
        return False
    
    with tarfile.open(DEPLOYMENT_PACKAGE, 'w:gz') as tar:
        for item in include_files:
            item_path = os.path.join(WORKSPACE_ROOT, item)
            if os.path.exists(item_path):
                if os.path.isfile(item_path):
                    if not should_exclude(item):
                        tar.add(item_path, arcname=item)
                        print(f"   📁 Added file: {item}")
                elif os.path.isdir(item_path):
                    for root, dirs, files in os.walk(item_path):
                        # Remove excluded directories
                        dirs[:] = [d for d in dirs if not should_exclude(d)]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, WORKSPACE_ROOT)
                            if not should_exclude(rel_path):
                                tar.add(file_path, arcname=rel_path)
                    print(f"   📁 Added directory: {item}")
            else:
                print(f"   ⚠️  Not found: {item}")
    
    # Get package size
    package_size = os.path.getsize(DEPLOYMENT_PACKAGE)
    package_size_mb = package_size / (1024 * 1024)
    
    print(f"   ✅ Created deployment package: {DEPLOYMENT_PACKAGE}")
    print(f"   📦 Package size: {package_size_mb:.2f} MB")
    
    print("\n🎉 DEPLOYMENT PACKAGE READY!")
    print("=" * 60)
    print(f"📦 Package: {DEPLOYMENT_PACKAGE}")
    print(f"📊 Size: {package_size_mb:.2f} MB")
    print(f"🌐 Target Domain: enterprisescanner.com")
    print(f"💰 Business Value: $3.9M pipeline included")
    print()
    print("NEXT STEPS:")
    print("1. Get a production server (Ubuntu 22.04, 2GB RAM, $10-15/month)")
    print("2. Upload this package to your server")
    print("3. Run the automated deployment script")
    print("4. Configure DNS for enterprisescanner.com")
    print("5. Access your live Enterprise Scanner!")
    print()
    
    return DEPLOYMENT_PACKAGE

if __name__ == "__main__":
    package_path = create_deployment_package()
    print(f"✅ Deployment package ready: {package_path}")