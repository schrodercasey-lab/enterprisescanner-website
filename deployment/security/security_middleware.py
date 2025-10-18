"""
Enterprise Scanner Security Middleware
Advanced security features for production deployment
"""

from flask import request, jsonify, session, g
from functools import wraps
import hashlib
import hmac
import time
import json
import redis
from datetime import datetime, timedelta
import logging

# Initialize Redis for rate limiting
redis_client = redis.Redis(host='localhost', port=6379, db=1)

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Load security configuration
        self.load_security_config()
    
    def load_security_config(self):
        """Load security configuration from environment"""
        import os
        
        self.rate_limit_requests = int(os.getenv('API_RATE_LIMIT', 1000))
        self.rate_limit_window = int(os.getenv('API_RATE_LIMIT_WINDOW', 3600))
        self.api_secret_key = os.getenv('API_SECRET_KEY', '')
        self.csrf_secret = os.getenv('CSRF_SECRET', '')
        self.security_headers_enabled = os.getenv('SECURITY_HEADERS', 'True').lower() == 'true'
    
    def before_request(self):
        """Process request before routing"""
        # Rate limiting
        if not self.check_rate_limit():
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # API key validation for API endpoints
        if request.path.startswith('/api/'):
            if not self.validate_api_key():
                return jsonify({'error': 'Invalid API key'}), 401
        
        # CSRF protection for POST/PUT/DELETE requests
        if request.method in ['POST', 'PUT', 'DELETE'] and not request.path.startswith('/api/'):
            if not self.validate_csrf_token():
                return jsonify({'error': 'CSRF token validation failed'}), 403
        
        # Log security events
        self.log_security_event()
    
    def after_request(self, response):
        """Process response after routing"""
        if self.security_headers_enabled:
            self.add_security_headers(response)
        
        return response
    
    def check_rate_limit(self):
        """Implement rate limiting"""
        try:
            client_ip = self.get_client_ip()
            key = f"rate_limit:{client_ip}"
            
            current_requests = redis_client.get(key)
            if current_requests is None:
                redis_client.setex(key, self.rate_limit_window, 1)
                return True
            
            if int(current_requests) >= self.rate_limit_requests:
                return False
            
            redis_client.incr(key)
            return True
            
        except Exception as e:
            logging.error(f"Rate limiting error: {e}")
            return True  # Allow on error to prevent blocking
    
    def validate_api_key(self):
        """Validate API key for API endpoints"""
        try:
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return False
            
            # Validate against stored API key
            expected_key = self.api_secret_key
            if not expected_key:
                return True  # Allow if no key configured
            
            return hmac.compare_digest(api_key, expected_key)
            
        except Exception as e:
            logging.error(f"API key validation error: {e}")
            return False
    
    def validate_csrf_token(self):
        """Validate CSRF token for form submissions"""
        try:
            csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not csrf_token:
                return False
            
            # Generate expected token
            session_id = session.get('session_id', '')
            expected_token = self.generate_csrf_token(session_id)
            
            return hmac.compare_digest(csrf_token, expected_token)
            
        except Exception as e:
            logging.error(f"CSRF validation error: {e}")
            return False
    
    def generate_csrf_token(self, session_id):
        """Generate CSRF token for session"""
        message = f"{session_id}:{int(time.time() // 3600)}"  # Valid for 1 hour
        return hmac.new(
            self.csrf_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def get_client_ip(self):
        """Get real client IP address"""
        # Check for forwarded IP first (behind proxy)
        forwarded_ips = request.headers.get('X-Forwarded-For')
        if forwarded_ips:
            return forwarded_ips.split(',')[0].strip()
        
        return request.headers.get('X-Real-IP', request.remote_addr)
    
    def add_security_headers(self, response):
        """Add comprehensive security headers"""
        # HSTS (HTTP Strict Transport Security)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Type Options
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Frame Options
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), accelerometer=(), gyroscope=()'
        )
        
        # Remove server information
        response.headers.pop('Server', None)
        response.headers['X-Powered-By'] = 'Enterprise Scanner'
    
    def log_security_event(self):
        """Log security-related events"""
        try:
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'ip': self.get_client_ip(),
                'method': request.method,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent', ''),
                'referrer': request.headers.get('Referer', ''),
                'content_length': request.content_length or 0
            }
            
            # Log suspicious patterns
            suspicious_patterns = [
                'admin', 'wp-admin', 'phpmyadmin', '.env', 'config',
                'sql', 'union', 'select', 'drop', 'insert', 'update',
                'script', 'javascript:', 'vbscript:', 'onload', 'onerror'
            ]
            
            path_lower = request.path.lower()
            if any(pattern in path_lower for pattern in suspicious_patterns):
                event_data['alert'] = 'Suspicious request pattern detected'
                logging.warning(f"Security Alert: {json.dumps(event_data)}")
            
        except Exception as e:
            logging.error(f"Security logging error: {e}")

# Initialize security middleware
security_middleware = SecurityMiddleware()

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not security_middleware.validate_api_key():
            return jsonify({'error': 'Valid API key required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_csrf_token(f):
    """Decorator to require CSRF token for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not security_middleware.validate_csrf_token():
            return jsonify({'error': 'CSRF token validation failed'}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token_for_session():
    """Generate CSRF token for current session"""
    session_id = session.get('session_id', secrets.token_hex(16))
    session['session_id'] = session_id
    return security_middleware.generate_csrf_token(session_id)
