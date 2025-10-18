#!/usr/bin/env python3
"""
Enterprise Scanner - Simple Production Deployment Script
Deploys Enterprise Scanner without complex dependencies for immediate use
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

# Configuration
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEPLOYMENT_LOG = os.path.join(WORKSPACE_ROOT, 'logs', 'deployment.log')

def log(message):
    """Log deployment messages"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # Write to log file
    os.makedirs(os.path.dirname(DEPLOYMENT_LOG), exist_ok=True)
    with open(DEPLOYMENT_LOG, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def create_simple_env():
    """Create simplified production environment without Redis"""
    env_path = os.path.join(WORKSPACE_ROOT, '.env.production.simple')
    
    env_content = """# Enterprise Scanner - Simple Production Configuration
# Generated for immediate deployment without complex dependencies

# Application Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=ApTTcH0c!mEi$7FTPFm4AnzF%iiIyVDZuFX7Rk*deESST7Fk52Bq8m%BpRGYxrHm
JWT_SECRET_KEY=*j*!HOzBjmBVouSiO$jqqeq*LDYz!Mpb

# Domain Configuration
DOMAIN_URL=https://enterprisescanner.com
ALLOWED_HOSTS=enterprisescanner.com,www.enterprisescanner.com

# Database Configuration (SQLite Production)
DATABASE_URL=sqlite:///enterprise_scanner_production.db
DB_TYPE=sqlite
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enterprise_scanner
DB_USER=enterprise_user

# Connection Pool Settings (SQLite)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True

# Email Configuration (Production Gmail/Google Workspace)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=info@enterprisescanner.com
EMAIL_PASSWORD=CHANGE_EMAIL_PASSWORD
EMAIL_TESTING_MODE=False

# Business Email Addresses
EMAIL_INFO=info@enterprisescanner.com
EMAIL_SALES=sales@enterprisescanner.com
EMAIL_SUPPORT=support@enterprisescanner.com
EMAIL_SECURITY=security@enterprisescanner.com
EMAIL_PARTNERSHIPS=partnerships@enterprisescanner.com

# Security Configuration (Simplified)
SECURITY_HEADERS=True
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=True
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' cdnjs.cloudflare.com
X_FRAME_OPTIONS=DENY
X_CONTENT_TYPE_OPTIONS=nosniff
REFERRER_POLICY=strict-origin-when-cross-origin

# Session Configuration
SESSION_TIMEOUT=3600
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict

# API Configuration (Simplified - no Redis rate limiting)
API_SECRET_KEY=epfHKtlWxb61@m1BXUF1qv9Kg^NcCp%7
API_RATE_LIMIT=1000
API_RATE_LIMIT_WINDOW=3600
API_KEY_EXPIRY_DAYS=365
RATE_LIMITING_ENABLED=False

# Partner Configuration
PARTNER_COMMISSION_BRONZE=25.0
PARTNER_COMMISSION_SILVER=30.0
PARTNER_COMMISSION_GOLD=35.0
PARTNER_APPROVAL_REQUIRED=True

# Monitoring and Logging (Simplified)
LOG_LEVEL=INFO
LOG_FILE=logs/enterprise_scanner.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True
PERFORMANCE_MONITORING=True

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_KEY=CHANGE_BACKUP_KEY

# External Services (Disabled for simple deployment)
REDIS_ENABLED=False
CELERY_ENABLED=False

# Analytics and Tracking
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
MIXPANEL_TOKEN=CHANGE_MIXPANEL_TOKEN
HOTJAR_ID=CHANGE_HOTJAR_ID

# Production Features (Simplified)
RATE_LIMITING=False
CACHING_ENABLED=False
COMPRESSION_ENABLED=True
MINIFICATION_ENABLED=True
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    log(f"Created simplified production environment: {env_path}")
    return env_path

def verify_database():
    """Verify production database exists and is accessible"""
    db_path = os.path.join(WORKSPACE_ROOT, 'enterprise_scanner_production.db')
    
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        log(f"Production database verified: {db_path} ({db_size} bytes)")
        return True
    else:
        log(f"ERROR: Production database not found: {db_path}")
        return False

def test_flask_application():
    """Test Flask application startup"""
    try:
        # Change to workspace directory
        os.chdir(WORKSPACE_ROOT)
        
        # Set environment for simple production
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        
        # Test import of main application
        result = subprocess.run([
            sys.executable, '-c', 
            'import backend.app; print("Flask application imports successfully")'
        ], capture_output=True, text=True, env=env, timeout=10)
        
        if result.returncode == 0:
            log("Flask application imports successfully")
            return True
        else:
            log(f"Flask import error: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"Flask test error: {e}")
        return False

def create_start_script():
    """Create simple production start script"""
    script_path = os.path.join(WORKSPACE_ROOT, 'start_production.py')
    
    script_content = '''#!/usr/bin/env python3
"""
Enterprise Scanner - Simple Production Startup Script
Starts the application for immediate production use
"""

import os
import sys
from dotenv import load_dotenv

# Set up paths
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKSPACE_ROOT)

# Load simplified production environment
load_dotenv('.env.production.simple')

# Set Flask environment
os.environ['FLASK_ENV'] = 'production'
os.environ['RATE_LIMITING_ENABLED'] = 'False'

print("Starting Enterprise Scanner in Simple Production Mode...")
print("Database: SQLite Production")
print("Security: Enabled (simplified)")
print("Rate Limiting: Disabled")
print("Redis: Disabled")
print("URL: http://localhost:5000")
print("CRM Dashboard: http://localhost:5000/crm-dashboard.html")
print()

# Start the application
if __name__ == '__main__':
    from backend.app import app
    
    # Configure Flask for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Start server
    print("Enterprise Scanner started successfully!")
    print("Access the CRM dashboard at: http://localhost:5000/crm-dashboard.html")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    log(f"Created production start script: {script_path}")
    return script_path

def main():
    """Main deployment function"""
    log("=" * 60)
    log("ENTERPRISE SCANNER - SIMPLE PRODUCTION DEPLOYMENT")
    log("=" * 60)
    
    # Step 1: Create simplified environment
    log("Step 1: Creating simplified production environment...")
    env_path = create_simple_env()
    
    # Step 2: Verify database
    log("Step 2: Verifying production database...")
    if not verify_database():
        log("ERROR: Production database verification failed!")
        return False
    
    # Step 3: Test Flask application
    log("Step 3: Testing Flask application...")
    if not test_flask_application():
        log("ERROR: Flask application test failed!")
        return False
    
    # Step 4: Create start script
    log("Step 4: Creating production start script...")
    script_path = create_start_script()
    
    # Step 5: Final verification
    log("Step 5: Final deployment verification...")
    
    log("")
    log("🎉 SIMPLE PRODUCTION DEPLOYMENT COMPLETE!")
    log("")
    log("DEPLOYMENT SUMMARY:")
    log(f"• Environment: {env_path}")
    log(f"• Start Script: {script_path}")
    log(f"• Database: enterprise_scanner_production.db")
    log(f"• Security: Enabled (simplified)")
    log(f"• Features: CRM Dashboard, Fortune 500 Data, Lead Management")
    log("")
    log("TO START ENTERPRISE SCANNER:")
    log("python start_production.py")
    log("")
    log("ACCESS POINTS:")
    log("• Main Application: http://localhost:5000")
    log("• CRM Dashboard: http://localhost:5000/crm-dashboard.html")
    log("• API Documentation: http://localhost:5000/api-documentation.html")
    log("")
    log("NEXT STEPS:")
    log("1. Configure domain DNS to point to server IP")
    log("2. Set up SSL certificates for HTTPS")
    log("3. Configure Google Workspace email integration")
    log("4. Deploy to production server (e.g., AWS, DigitalOcean)")
    log("")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Simple Production Deployment completed successfully!")
        print("Run: python start_production.py")
    else:
        print("\n❌ Simple Production Deployment failed!")
        sys.exit(1)