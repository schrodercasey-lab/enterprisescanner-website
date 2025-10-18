#!/bin/bash

# Deploy Live Security Assessment Tool to Production Server
# This script updates the production server with our comprehensive security assessment API

echo "=== Deploying Live Security Assessment Tool to Production ==="

# Navigate to production directory
cd /var/www/enterprisescanner.com

# Create API directory if it doesn't exist
mkdir -p backend/api

# Backup current app.py
cp backend/app.py backend/app.py.backup.$(date +%Y%m%d_%H%M%S)

echo "✅ Created backup of current app.py"

# Install required packages for security assessment
source venv/bin/activate
pip install dnspython reportlab requests

echo "✅ Installed required Python packages"

# Update app.py to include security assessment blueprint
cat > backend/app.py << 'FLASK_APP_EOF'
"""
Enterprise Scanner - Production Flask Application
Comprehensive cybersecurity platform with Live Security Assessment Tool
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import os

# Import the comprehensive security assessment blueprint
from api.security_assessment import security_assessment

app = Flask(__name__)

# Configure API keys
api_keys = {
    'es_production_key_12345': {
        'name': 'Production Key',
        'permissions': 'read_write',
        'created': '2025-10-15T00:00:00',
        'last_used': None,
        'usage_count': 0
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

# Register the security assessment blueprint
app.register_blueprint(security_assessment, url_prefix='/api/security')

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
    data = request.get_json() or {}
    
    new_key = f"es_key_{uuid.uuid4().hex[:16]}"
    api_keys[new_key] = {
        "name": data.get('name', 'Generated Key'),
        "permissions": data.get('permissions', 'read_write'),
        "created": datetime.now().isoformat(),
        "last_used": None,
        "usage_count": 0
    }
    
    return jsonify({
        'success': True,
        'api_key': new_key,
        'message': 'API key generated successfully'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
FLASK_APP_EOF

echo "✅ Updated app.py with security assessment blueprint"

# Create __init__.py file for the api package
cat > backend/api/__init__.py << 'INIT_EOF'
"""API package for Enterprise Scanner"""
INIT_EOF

echo "✅ Created API package initialization"

echo "=== Deployment complete! ==="
echo "Next steps:"
echo "1. Copy the security_assessment.py file to backend/api/"
echo "2. Restart the enterprise-scanner service"
echo "3. Test the API endpoints"

EOF