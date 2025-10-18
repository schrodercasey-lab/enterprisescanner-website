#!/bin/bash

# ENTERPRISE SCANNER - LIVE SECURITY ASSESSMENT DEPLOYMENT
# Run this script on the production server as root

echo "=========================================="
echo "Enterprise Scanner Live Deployment Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Step 1: Update system
echo "Step 1: Updating system packages..."
apt update
apt install -y python3 python3-pip python3-venv nginx

# Step 2: Create application directory
echo "Step 2: Setting up application directory..."
mkdir -p /var/www/enterprisescanner.com
chown -R www-data:www-data /var/www/enterprisescanner.com

# Step 3: Create Python virtual environment
echo "Step 3: Creating Python environment..."
cd /var/www/enterprisescanner.com
python3 -m venv venv
source venv/bin/activate

# Step 4: Install Python dependencies
echo "Step 4: Installing Python dependencies..."
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
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.2
importlib-metadata==6.8.0
zipp==3.16.2
reportlab==4.0.4
dnspython==2.4.2
requests==2.31.0
EOF

pip install -r requirements.txt

# Step 5: Create backend structure
echo "Step 5: Creating backend application..."
mkdir -p backend/{api,database,models,services,utils,logs}
touch backend/logs/security_events.log
chown -R www-data:www-data backend/logs

# Step 6: Create Flask application (simplified for deployment)
cat > backend/app.py << 'EOF'
#!/usr/bin/env python3
"""
Enterprise Scanner - Production Flask Application
Live Security Assessment Tool
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Simple API key storage (in production, use database)
api_keys = {
    "es_production_key_12345": {
        "name": "Production Key",
        "permissions": "read_write",
        "created": "2025-10-15T12:00:00.000000",
        "last_used": None,
        "usage_count": 0
    }
}

def validate_api_key(api_key):
    """Validate API key"""
    return api_key in api_keys

def require_api_key(f):
    """Decorator to require API key authentication"""
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/health', methods=['GET'])
@require_api_key
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Enterprise Scanner API',
        'version': '2.0.0',
        'features': ['Live Security Assessment', 'PDF Reports', 'Real-time Scanning']
    })

@app.route('/api/keys/generate', methods=['POST'])
def generate_api_key():
    """Generate a new API key"""
    import uuid
    data = request.get_json() or {}
    
    new_key = f"es_key_{uuid.uuid4().hex[:16]}"
    api_keys[new_key] = {
        "name": data.get('name', 'Generated Key'),
        "permissions": data.get('permissions', 'read_write'),
        "created": "2025-10-15T12:00:00.000000",
        "last_used": None,
        "usage_count": 0
    }
    
    return jsonify({
        'success': True,
        'api_key': new_key,
        'message': 'API key generated successfully'
    })

# Import security assessment API
try:
    from api.security_assessment import security_assessment
    app.register_blueprint(security_assessment, url_prefix='/api')
    print("✓ Security Assessment API loaded")
except ImportError as e:
    print(f"⚠ Security Assessment API not available: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# Step 7: Create systemd service
echo "Step 7: Creating systemd service..."
cat > /etc/systemd/system/enterprise-scanner.service << 'EOF'
[Unit]
Description=Enterprise Scanner Flask Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/enterprisescanner.com
Environment=PATH=/var/www/enterprisescanner.com/venv/bin
ExecStart=/var/www/enterprisescanner.com/venv/bin/python backend/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Step 8: Configure Nginx
echo "Step 8: Configuring Nginx..."
cat > /etc/nginx/sites-available/enterprisescanner.com << 'EOF'
server {
    listen 80;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name enterprisescanner.com www.enterprisescanner.com;
    
    # SSL configuration (update paths as needed)
    ssl_certificate /etc/letsencrypt/live/enterprisescanner.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/enterprisescanner.com/privkey.pem;
    
    # Website files
    location / {
        root /var/www/enterprisescanner.com/website;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/enterprisescanner.com /etc/nginx/sites-enabled/
nginx -t

# Step 9: Start services
echo "Step 9: Starting services..."
systemctl daemon-reload
systemctl enable enterprise-scanner
systemctl start enterprise-scanner
systemctl reload nginx

# Step 10: Verify deployment
echo "Step 10: Verifying deployment..."
systemctl status enterprise-scanner --no-pager
systemctl status nginx --no-pager

echo "=========================================="
echo "Deployment completed!"
echo "API Key: es_production_key_12345"
echo "Test with: curl -H 'X-API-Key: es_production_key_12345' https://enterprisescanner.com/api/health"
echo "=========================================="
EOF

# Make script executable
chmod +x /root/deploy_enterprise_scanner.sh

echo "Deployment script created at /root/deploy_enterprise_scanner.sh"
echo "Run: sudo /root/deploy_enterprise_scanner.sh"