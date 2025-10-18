# Environment Variables Reference - Enterprise Scanner
**Complete documentation of all environment variables**  
**Last Updated:** October 16, 2025

---

## 🔐 SECURITY WARNING

**⚠️ NEVER commit `.env.production` or any file containing actual values to Git!**

This document explains what each variable does. Actual values are stored in:
- Production: `/opt/enterprisescanner/.env.production` (on server)
- Local: `.env.production` (gitignored)

---

## 🗂️ TABLE OF CONTENTS

1. [Application Settings](#application-settings)
2. [Database Configuration](#database-configuration)
3. [Redis Configuration](#redis-configuration)
4. [Email Configuration](#email-configuration)
5. [Security Settings](#security-settings)
6. [Google Workspace Integration](#google-workspace-integration)
7. [Monitoring & Analytics](#monitoring--analytics)
8. [External Services](#external-services)
9. [Feature Flags](#feature-flags)
10. [Development vs Production](#development-vs-production)

---

## 📋 APPLICATION SETTINGS

### `FLASK_APP`
**Purpose:** Entry point for Flask application  
**Required:** Yes (when using Flask)  
**Type:** String (filename)  
**Example:** `app.py`  
**Default:** None  
**Used By:** Flask, gunicorn, development server

### `FLASK_ENV`
**Purpose:** Application environment mode  
**Required:** Yes  
**Type:** String  
**Values:**
- `development` - Debug mode, auto-reload, verbose errors
- `production` - Optimized, no debug, secure errors
- `testing` - Test mode with fixtures

**Example:** `production`  
**Default:** `production`  
**Used By:** Flask core, error handling, logging

### `SECRET_KEY`
**Purpose:** Session encryption, CSRF protection, security tokens  
**Required:** YES (CRITICAL)  
**Type:** String (random, 32+ characters)  
**Example:** `your-super-secret-random-key-here-change-this`  
**Generation:** `python -c "import secrets; print(secrets.token_hex(32))"`  
**Security:** NEVER use default, NEVER commit to Git  
**Used By:** Flask sessions, WTForms CSRF, JWT tokens

### `DEBUG`
**Purpose:** Enable/disable debug mode  
**Required:** No  
**Type:** Boolean  
**Values:** `True` / `False`  
**Example:** `False`  
**Default:** `False`  
**Security:** MUST be `False` in production (exposes source code)  
**Used By:** Flask debug toolbar, error pages

### `PORT`
**Purpose:** Port for application to listen on  
**Required:** No  
**Type:** Integer  
**Example:** `5000`  
**Default:** `5000`  
**Used By:** Flask development server, gunicorn

### `HOST`
**Purpose:** IP address to bind application  
**Required:** No  
**Type:** String (IP address)  
**Values:**
- `127.0.0.1` - Localhost only (behind Nginx)
- `0.0.0.0` - All interfaces (only in containers)

**Example:** `127.0.0.1`  
**Default:** `127.0.0.1`  
**Security:** Use `127.0.0.1` on host, `0.0.0.0` in containers only  
**Used By:** Flask bind configuration

---

## 🗄️ DATABASE CONFIGURATION

### `DATABASE_URL`
**Purpose:** PostgreSQL connection string  
**Required:** YES (for production)  
**Type:** String (connection URI)  
**Format:** `postgresql://username:password@host:port/database`  
**Example:** `postgresql://admin:SecurePass2024!@127.0.0.1:5432/enterprisescanner`  
**Production Value:** Uses PgBouncer: `postgresql://admin:SecurePass2024!@127.0.0.1:6432/enterprisescanner`  
**Development Value:** `sqlite:///dev.db` (for local testing)  
**Security:** Contains password - NEVER commit  
**Used By:** SQLAlchemy, database migrations

### `DB_HOST`
**Purpose:** Database server hostname/IP  
**Required:** No (if using DATABASE_URL)  
**Type:** String  
**Example:** `127.0.0.1`  
**Default:** `127.0.0.1`  
**Used By:** Manual database configuration

### `DB_PORT`
**Purpose:** Database server port  
**Required:** No  
**Type:** Integer  
**Values:**
- `5432` - Direct PostgreSQL connection
- `6432` - Via PgBouncer connection pooler (RECOMMENDED)

**Example:** `6432`  
**Default:** `5432`  
**Production:** `6432` (PgBouncer)  
**Used By:** Database connection logic

### `DB_NAME`
**Purpose:** Database name  
**Required:** No  
**Type:** String  
**Example:** `enterprisescanner`  
**Default:** `enterprisescanner`  
**Used By:** Database connection

### `DB_USER`
**Purpose:** Database username  
**Required:** No  
**Type:** String  
**Example:** `admin`  
**Default:** `admin`  
**Used By:** Database authentication

### `DB_PASSWORD`
**Purpose:** Database password  
**Required:** No  
**Type:** String  
**Example:** `SecurePass2024!`  
**Security:** NEVER commit to Git  
**Used By:** Database authentication

### `PGBOUNCER_URL`
**Purpose:** PgBouncer-specific connection string  
**Required:** No (optional optimization)  
**Type:** String  
**Example:** `postgresql://admin:SecurePass2024!@127.0.0.1:6432/enterprisescanner`  
**Purpose:** Use for connection pooling (recommended for production)  
**Used By:** SQLAlchemy when connection pooling desired

---

## 💾 REDIS CONFIGURATION

### `REDIS_URL`
**Purpose:** Redis connection string  
**Required:** YES (for caching)  
**Type:** String (Redis URI)  
**Format:** `redis://host:port/db`  
**Example:** `redis://127.0.0.1:6379/0`  
**Default:** `redis://127.0.0.1:6379/0`  
**Notes:** No password needed (localhost-only)  
**Used By:** Flask-Caching, Celery, session storage

### `REDIS_HOST`
**Purpose:** Redis server hostname/IP  
**Required:** No (if using REDIS_URL)  
**Type:** String  
**Example:** `127.0.0.1`  
**Default:** `127.0.0.1`  
**Used By:** Manual Redis configuration

### `REDIS_PORT`
**Purpose:** Redis server port  
**Required:** No  
**Type:** Integer  
**Example:** `6379`  
**Default:** `6379`  
**Used By:** Manual Redis configuration

### `REDIS_DB`
**Purpose:** Redis database number (0-15)  
**Required:** No  
**Type:** Integer  
**Example:** `0`  
**Default:** `0`  
**Notes:** Use different numbers for different purposes (0=cache, 1=sessions, 2=celery)  
**Used By:** Redis client configuration

### `CACHE_TYPE`
**Purpose:** Caching backend type  
**Required:** No  
**Type:** String  
**Values:**
- `redis` - Use Redis (RECOMMENDED)
- `simple` - In-memory cache (development only)
- `null` - No caching (testing)

**Example:** `redis`  
**Default:** `simple`  
**Production:** `redis`  
**Used By:** Flask-Caching

### `CACHE_DEFAULT_TIMEOUT`
**Purpose:** Default cache expiration time  
**Required:** No  
**Type:** Integer (seconds)  
**Example:** `300` (5 minutes)  
**Default:** `300`  
**Used By:** Flask-Caching

---

## 📧 EMAIL CONFIGURATION

### `MAIL_SERVER`
**Purpose:** SMTP server hostname  
**Required:** YES (for email)  
**Type:** String  
**Example:** `smtp.gmail.com`  
**Production Value:** `smtp.gmail.com` (Google Workspace)  
**Used By:** Flask-Mail, email sending

### `MAIL_PORT`
**Purpose:** SMTP server port  
**Required:** YES  
**Type:** Integer  
**Values:**
- `587` - TLS (RECOMMENDED)
- `465` - SSL
- `25` - Unencrypted (NOT RECOMMENDED)

**Example:** `587`  
**Default:** `587`  
**Used By:** Flask-Mail

### `MAIL_USE_TLS`
**Purpose:** Enable TLS encryption  
**Required:** YES  
**Type:** Boolean  
**Example:** `True`  
**Default:** `True`  
**Security:** MUST be True for port 587  
**Used By:** Flask-Mail

### `MAIL_USE_SSL`
**Purpose:** Enable SSL encryption  
**Required:** No  
**Type:** Boolean  
**Example:** `False`  
**Default:** `False`  
**Notes:** Use for port 465, not with TLS  
**Used By:** Flask-Mail

### `MAIL_USERNAME`
**Purpose:** SMTP authentication username  
**Required:** YES  
**Type:** String (email address)  
**Example:** `info@enterprisescanner.com`  
**Production Value:** `info@enterprisescanner.com`  
**Used By:** Flask-Mail authentication

### `MAIL_PASSWORD`
**Purpose:** SMTP authentication password  
**Required:** YES  
**Type:** String  
**Example:** `your-google-workspace-password`  
**Security:** Use App Password for Google Workspace, NEVER commit  
**Used By:** Flask-Mail authentication

### `MAIL_DEFAULT_SENDER`
**Purpose:** Default "From" email address  
**Required:** No  
**Type:** String or Tuple  
**Example:** `"Enterprise Scanner" <info@enterprisescanner.com>`  
**Default:** Same as MAIL_USERNAME  
**Used By:** Flask-Mail default sender

---

## 🔒 SECURITY SETTINGS

### `SSL_CERT_PATH`
**Purpose:** Path to SSL certificate file  
**Required:** YES (for HTTPS)  
**Type:** String (filesystem path)  
**Example:** `/etc/letsencrypt/live/enterprisescanner.com/fullchain.pem`  
**Production Value:** `/etc/letsencrypt/live/enterprisescanner.com/fullchain.pem`  
**Used By:** Nginx SSL configuration

### `SSL_KEY_PATH`
**Purpose:** Path to SSL private key  
**Required:** YES (for HTTPS)  
**Type:** String (filesystem path)  
**Example:** `/etc/letsencrypt/live/enterprisescanner.com/privkey.pem`  
**Production Value:** `/etc/letsencrypt/live/enterprisescanner.com/privkey.pem`  
**Security:** Private key - protect file permissions (600)  
**Used By:** Nginx SSL configuration

### `SESSION_COOKIE_SECURE`
**Purpose:** Send cookies over HTTPS only  
**Required:** No  
**Type:** Boolean  
**Example:** `True`  
**Default:** `False`  
**Production:** `True` (REQUIRED)  
**Security:** MUST be True in production  
**Used By:** Flask session management

### `SESSION_COOKIE_HTTPONLY`
**Purpose:** Prevent JavaScript access to cookies  
**Required:** No  
**Type:** Boolean  
**Example:** `True`  
**Default:** `True`  
**Security:** MUST be True (XSS protection)  
**Used By:** Flask session management

### `SESSION_COOKIE_SAMESITE`
**Purpose:** CSRF protection for cookies  
**Required:** No  
**Type:** String  
**Values:** `Strict` / `Lax` / `None`  
**Example:** `Lax`  
**Default:** `Lax`  
**Security:** Use `Lax` or `Strict`  
**Used By:** Flask session management

### `PERMANENT_SESSION_LIFETIME`
**Purpose:** Session expiration time  
**Required:** No  
**Type:** Integer (seconds)  
**Example:** `86400` (24 hours)  
**Default:** `31536000` (1 year)  
**Production:** `86400` (24 hours recommended)  
**Used By:** Flask session management

### `CONTENT_SECURITY_POLICY`
**Purpose:** CSP header for XSS protection  
**Required:** No (but HIGHLY RECOMMENDED)  
**Type:** String (CSP directive)  
**Example:** See full CSP section below  
**Used By:** Flask-Talisman, custom middleware

---

## 🏢 GOOGLE WORKSPACE INTEGRATION

### `GOOGLE_WORKSPACE_DOMAIN`
**Purpose:** Your Google Workspace domain  
**Required:** Yes (for email)  
**Type:** String  
**Example:** `enterprisescanner.com`  
**Used By:** Email configuration, documentation

### `GOOGLE_WORKSPACE_ADMIN_EMAIL`
**Purpose:** Workspace admin email  
**Required:** No  
**Type:** String  
**Example:** `admin@enterprisescanner.com`  
**Used By:** Administrative notifications

### Email Addresses (All @enterprisescanner.com)
```env
EMAIL_INFO=info@enterprisescanner.com
EMAIL_SALES=sales@enterprisescanner.com
EMAIL_SUPPORT=support@enterprisescanner.com
EMAIL_SECURITY=security@enterprisescanner.com
EMAIL_PARTNERSHIPS=partnerships@enterprisescanner.com
```
**Used By:** Contact forms, email routing, documentation

---

## 📊 MONITORING & ANALYTICS

### `GOOGLE_ANALYTICS_ID`
**Purpose:** Google Analytics tracking ID  
**Required:** No  
**Type:** String  
**Format:** `G-XXXXXXXXXX`  
**Example:** `G-XXXXXXXXXX`  
**Status:** Prepared but not yet active  
**Used By:** Google Analytics script in HTML

### `SENTRY_DSN`
**Purpose:** Sentry error tracking endpoint  
**Required:** No (optional)  
**Type:** String (URL)  
**Example:** `https://xxxxx@sentry.io/xxxxx`  
**Notes:** For production error monitoring  
**Used By:** Sentry SDK

### `LOG_LEVEL`
**Purpose:** Application logging verbosity  
**Required:** No  
**Type:** String  
**Values:** `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL`  
**Example:** `INFO`  
**Default:** `INFO`  
**Development:** `DEBUG`  
**Production:** `INFO` or `WARNING`  
**Used By:** Python logging configuration

### `LOG_FILE_PATH`
**Purpose:** Path to application log file  
**Required:** No  
**Type:** String  
**Example:** `/var/log/enterprisescanner/app.log`  
**Default:** `./logs/app.log`  
**Used By:** Application logging

---

## 🌐 EXTERNAL SERVICES

### `PROMETHEUS_URL`
**Purpose:** Prometheus metrics endpoint  
**Required:** No  
**Type:** String (URL)  
**Example:** `http://127.0.0.1:9090`  
**Default:** `http://127.0.0.1:9090`  
**Used By:** Grafana data source, health checks

### `GRAFANA_URL`
**Purpose:** Grafana dashboard URL  
**Required:** No  
**Type:** String (URL)  
**Example:** `https://enterprisescanner.com/grafana`  
**Production Value:** `https://enterprisescanner.com/grafana`  
**Used By:** Dashboard links, documentation

### `CDN_URL`
**Purpose:** CDN base URL for static assets  
**Required:** No  
**Type:** String (URL)  
**Example:** `https://cdn.enterprisescanner.com`  
**Status:** Not yet implemented  
**Future:** CloudFlare/AWS CloudFront integration  
**Used By:** Asset URL generation

---

## 🎚️ FEATURE FLAGS

### `ENABLE_REDIS_CACHE`
**Purpose:** Enable/disable Redis caching  
**Required:** No  
**Type:** Boolean  
**Example:** `True`  
**Default:** `False`  
**Status:** Ready but not yet integrated  
**Used By:** Application cache logic

### `ENABLE_EMAIL_NOTIFICATIONS`
**Purpose:** Enable/disable email sending  
**Required:** No  
**Type:** Boolean  
**Example:** `True`  
**Default:** `False`  
**Development:** `False` (avoid sending test emails)  
**Production:** `True`  
**Used By:** Email notification logic

### `ENABLE_ANALYTICS`
**Purpose:** Enable/disable analytics tracking  
**Required:** No  
**Type:** Boolean  
**Example:** `True`  
**Default:** `False`  
**Notes:** Disable in development for privacy  
**Used By:** Analytics script inclusion

### `MAINTENANCE_MODE`
**Purpose:** Put site in maintenance mode  
**Required:** No  
**Type:** Boolean  
**Example:** `False`  
**Default:** `False`  
**Production:** Set to `True` during major updates  
**Used By:** Maintenance page middleware

---

## 🔄 DEVELOPMENT VS PRODUCTION

### Complete `.env.development` Example
```env
# Application
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database (SQLite for development)
DATABASE_URL=sqlite:///dev.db

# Redis (optional in dev)
REDIS_URL=redis://127.0.0.1:6379/0
CACHE_TYPE=simple

# Email (disabled in dev)
ENABLE_EMAIL_NOTIFICATIONS=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=test@example.com
MAIL_PASSWORD=test

# Security (relaxed for dev)
SESSION_COOKIE_SECURE=False
LOG_LEVEL=DEBUG

# Features
ENABLE_REDIS_CACHE=False
ENABLE_ANALYTICS=False
MAINTENANCE_MODE=False
```

### Complete `.env.production` Example
```env
# Application
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<GENERATE_RANDOM_32_CHAR_STRING>
PORT=5000
HOST=127.0.0.1

# Database (PostgreSQL via PgBouncer)
DATABASE_URL=postgresql://admin:SecurePass2024!@127.0.0.1:6432/enterprisescanner
DB_HOST=127.0.0.1
DB_PORT=6432
DB_NAME=enterprisescanner
DB_USER=admin
DB_PASSWORD=SecurePass2024!

# Redis
REDIS_URL=redis://127.0.0.1:6379/0
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300

# Email (Google Workspace)
ENABLE_EMAIL_NOTIFICATIONS=True
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=info@enterprisescanner.com
MAIL_PASSWORD=<GOOGLE_APP_PASSWORD>
MAIL_DEFAULT_SENDER=Enterprise Scanner <info@enterprisescanner.com>

# Google Workspace
GOOGLE_WORKSPACE_DOMAIN=enterprisescanner.com
EMAIL_INFO=info@enterprisescanner.com
EMAIL_SALES=sales@enterprisescanner.com
EMAIL_SUPPORT=support@enterprisescanner.com
EMAIL_SECURITY=security@enterprisescanner.com
EMAIL_PARTNERSHIPS=partnerships@enterprisescanner.com

# SSL
SSL_CERT_PATH=/etc/letsencrypt/live/enterprisescanner.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/enterprisescanner.com/privkey.pem

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=86400

# Monitoring
PROMETHEUS_URL=http://127.0.0.1:9090
GRAFANA_URL=https://enterprisescanner.com/grafana
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/enterprisescanner/app.log

# Analytics
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
ENABLE_ANALYTICS=True

# Features
ENABLE_REDIS_CACHE=True
MAINTENANCE_MODE=False

# Content Security Policy
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;
```

---

## 🔧 LOADING ENVIRONMENT VARIABLES

### In Python (Flask)
```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('.env.production')

# Access variables
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')  # with default
```

### In Bash
```bash
# Load .env file
source .env.production

# Or export manually
export DATABASE_URL="postgresql://admin:SecurePass2024!@127.0.0.1:6432/enterprisescanner"
```

### In Docker Compose
```yaml
services:
  app:
    env_file:
      - .env.production
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
```

---

## 🛡️ SECURITY BEST PRACTICES

1. **NEVER commit `.env*` files to Git**
   ```bash
   # Add to .gitignore
   .env
   .env.*
   !.env.example
   ```

2. **Use different secrets for dev/prod**
   - Development: Simple keys for convenience
   - Production: Strong random keys

3. **Rotate secrets regularly**
   - Change SECRET_KEY every 90 days
   - Update passwords quarterly
   - Regenerate API keys on suspected compromise

4. **Restrict file permissions**
   ```bash
   chmod 600 .env.production
   chown www-data:www-data .env.production
   ```

5. **Use environment-specific files**
   - `.env.development` - Development
   - `.env.testing` - Testing
   - `.env.production` - Production
   - `.env.example` - Template (safe to commit)

6. **Validate required variables**
   ```python
   required_vars = ['SECRET_KEY', 'DATABASE_URL', 'REDIS_URL']
   for var in required_vars:
       if not os.getenv(var):
           raise ValueError(f"Missing required environment variable: {var}")
   ```

---

## 📚 RELATED DOCUMENTATION

- **INFRASTRUCTURE_MAP.md** - Infrastructure overview
- **COMMON_COMMANDS.md** - Common operations
- **.github/ai-context.md** - Project context
- **SERVICE_DEPENDENCIES.md** - Architecture diagram

---

**Last Updated:** October 16, 2025  
**Next Review:** After adding new integrations or services
