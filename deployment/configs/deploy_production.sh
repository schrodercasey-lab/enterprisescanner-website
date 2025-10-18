#!/bin/bash
# Enterprise Scanner Production Deployment Script
# Complete setup for production environment

set -e

echo "🚀 Enterprise Scanner Production Deployment"
echo "=========================================="

# Configuration
DOMAIN="enterprisescanner.com"
APP_USER="enterprise_scanner"
APP_DIR="/opt/enterprise_scanner"
SSL_DIR="deployment/ssl"

# Create application user
echo "Creating application user..."
sudo useradd -r -s /bin/bash -d $APP_DIR $APP_USER || true

# Create application directory
echo "Creating application directory..."
sudo mkdir -p $APP_DIR
sudo mkdir -p $APP_DIR/logs
sudo mkdir -p $APP_DIR/backups

# Copy application files
echo "Copying application files..."
sudo cp -r . $APP_DIR/
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Create Python virtual environment
echo "Setting up Python virtual environment..."
sudo -u $APP_USER python3 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
sudo -u $APP_USER $APP_DIR/venv/bin/pip install gunicorn gevent

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y nginx postgresql postgresql-contrib redis-server

# Setup PostgreSQL
echo "Setting up PostgreSQL..."
sudo -u postgres createuser $APP_USER || true
sudo -u postgres createdb enterprise_scanner || true
sudo -u postgres psql -c "ALTER USER $APP_USER PASSWORD 'CHANGE_PASSWORD';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE enterprise_scanner TO $APP_USER;" || true

# Run database migration
echo "Running database migration..."
sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/deployment/scripts/setup_postgresql.py

# Install SSL certificates
echo "Setting up SSL certificates..."
bash $APP_DIR/deployment/configs/setup_ssl.sh

# Configure Nginx
echo "Configuring Nginx..."
sudo cp $APP_DIR/deployment/configs/nginx.conf /etc/nginx/sites-available/enterprise_scanner
sudo ln -sf /etc/nginx/sites-available/enterprise_scanner /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Install systemd service
echo "Installing systemd service..."
sudo cp $APP_DIR/deployment/configs/enterprise-scanner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable enterprise-scanner

# Start services
echo "Starting services..."
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl start enterprise-scanner
sudo systemctl start nginx

# Setup firewall
echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "✅ Production deployment completed!"
echo "Application URL: https://$DOMAIN"
echo "Health Check: https://$DOMAIN/api/health"
echo ""
echo "Next steps:"
echo "1. Update .env.production with your actual passwords and API keys"
echo "2. Configure your domain DNS to point to this server"
echo "3. Test the application: https://$DOMAIN"
echo "4. Monitor logs: sudo journalctl -u enterprise-scanner -f"
