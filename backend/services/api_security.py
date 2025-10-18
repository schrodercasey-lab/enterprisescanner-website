"""
Enterprise API Security Service
Comprehensive API security framework for Fortune 500 cybersecurity platform.
"""

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import sqlite3
import logging
from functools import wraps
from flask import request, jsonify, g

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """API security levels for different endpoint types"""
    PUBLIC = "public"           # No authentication required
    AUTHENTICATED = "authenticated"  # Basic user authentication
    PRIVILEGED = "privileged"   # Admin/manager roles required
    EXECUTIVE = "executive"     # C-suite/executive access only


class RateLimitType(Enum):
    """Different types of rate limiting"""
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ORGANIZATION = "per_organization"
    PER_API_KEY = "per_api_key"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    block_duration_minutes: int


@dataclass
class APIKey:
    """API key configuration"""
    key_id: str
    key_secret: str
    organization_id: str
    user_id: str
    name: str
    permissions: List[str]
    rate_limit_config: RateLimitConfig
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]


@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    event_type: str
    severity: str
    source_ip: str
    user_id: Optional[str]
    organization_id: Optional[str]
    api_key_id: Optional[str]
    endpoint: str
    method: str
    user_agent: str
    details: Dict[str, Any]
    timestamp: datetime


@dataclass
class RateLimitStatus:
    """Rate limit status for tracking"""
    identifier: str
    limit_type: RateLimitType
    requests_made: int
    limit_per_minute: int
    limit_per_hour: int
    limit_per_day: int
    reset_time: datetime
    blocked_until: Optional[datetime]


class EnterpriseAPISecurityManager:
    """
    Enterprise-grade API security manager for Fortune 500 compliance.
    Provides comprehensive security features including rate limiting,
    authentication, authorization, and audit logging.
    """
    
    def __init__(self, db_path: str = "security.db"):
        self.db_path = db_path
        self.rate_limits: Dict[str, RateLimitStatus] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.security_events: List[SecurityEvent] = []
        
        # Default rate limit configurations
        self.default_rate_limits = {
            SecurityLevel.PUBLIC: RateLimitConfig(60, 1000, 10000, 100, 15),
            SecurityLevel.AUTHENTICATED: RateLimitConfig(120, 2000, 20000, 200, 10),
            SecurityLevel.PRIVILEGED: RateLimitConfig(300, 5000, 50000, 500, 5),
            SecurityLevel.EXECUTIVE: RateLimitConfig(1000, 10000, 100000, 1000, 1)
        }
        
        # Fortune 500 security configurations
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize security database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    key_secret_hash TEXT NOT NULL,
                    organization_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    rate_limit_config TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_used_at TIMESTAMP
                )
            ''')
            
            # Rate limit tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limits (
                    identifier TEXT PRIMARY KEY,
                    limit_type TEXT NOT NULL,
                    requests_minute INTEGER DEFAULT 0,
                    requests_hour INTEGER DEFAULT 0,
                    requests_day INTEGER DEFAULT 0,
                    reset_minute TIMESTAMP,
                    reset_hour TIMESTAMP,
                    reset_day TIMESTAMP,
                    blocked_until TIMESTAMP
                )
            ''')
            
            # Security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    organization_id TEXT,
                    api_key_id TEXT,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    user_agent TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # IP whitelist table for Fortune 500 clients
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_whitelist (
                    ip_address TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Security database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security database: {e}")
            raise
    
    def generate_api_key(self, organization_id: str, user_id: str, name: str, 
                        permissions: List[str], expires_days: Optional[int] = None) -> APIKey:
        """Generate new API key for organization"""
        try:
            key_id = f"esk_{uuid.uuid4().hex[:16]}"  # Enterprise Scanner Key
            key_secret = uuid.uuid4().hex + uuid.uuid4().hex  # 64 char secret
            key_secret_hash = hashlib.sha256(key_secret.encode()).hexdigest()
            
            expires_at = None
            if expires_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            # Default privileged rate limits for API keys
            rate_limit_config = self.default_rate_limits[SecurityLevel.PRIVILEGED]
            
            api_key = APIKey(
                key_id=key_id,
                key_secret=key_secret,
                organization_id=organization_id,
                user_id=user_id,
                name=name,
                permissions=permissions,
                rate_limit_config=rate_limit_config,
                is_active=True,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                last_used_at=None
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_keys 
                (key_id, key_secret_hash, organization_id, user_id, name, permissions, 
                 rate_limit_config, is_active, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                key_id, key_secret_hash, organization_id, user_id, name,
                json.dumps(permissions), json.dumps(asdict(rate_limit_config)),
                True, api_key.created_at, expires_at
            ))
            
            conn.commit()
            conn.close()
            
            # Log security event
            self.log_security_event(
                event_type="api_key_generated",
                severity="info",
                source_ip=request.remote_addr if request else "system",
                user_id=user_id,
                organization_id=organization_id,
                endpoint="/api/security/keys",
                method="POST",
                details={"key_id": key_id, "permissions": permissions}
            )
            
            logger.info(f"Generated API key {key_id} for organization {organization_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            raise
    
    def validate_api_key(self, key_id: str, key_secret: str) -> Optional[APIKey]:
        """Validate API key and return key info if valid"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT key_secret_hash, organization_id, user_id, name, permissions,
                       rate_limit_config, is_active, created_at, expires_at, last_used_at
                FROM api_keys WHERE key_id = ?
            ''', (key_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            key_secret_hash = hashlib.sha256(key_secret.encode()).hexdigest()
            if not hmac.compare_digest(result[0], key_secret_hash):
                return None
            
            # Check if key is active
            if not result[6]:
                return None
            
            # Check if key is expired
            if result[8] and datetime.fromisoformat(result[8]) < datetime.utcnow():
                return None
            
            # Update last used timestamp
            cursor.execute('''
                UPDATE api_keys SET last_used_at = CURRENT_TIMESTAMP 
                WHERE key_id = ?
            ''', (key_id,))
            
            conn.commit()
            conn.close()
            
            # Parse rate limit config
            rate_limit_config = RateLimitConfig(**json.loads(result[5]))
            
            return APIKey(
                key_id=key_id,
                key_secret=key_secret,
                organization_id=result[1],
                user_id=result[2],
                name=result[3],
                permissions=json.loads(result[4]),
                rate_limit_config=rate_limit_config,
                is_active=result[6],
                created_at=datetime.fromisoformat(result[7]),
                expires_at=datetime.fromisoformat(result[8]) if result[8] else None,
                last_used_at=datetime.fromisoformat(result[9]) if result[9] else None
            )
            
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return None
    
    def check_rate_limit(self, identifier: str, limit_type: RateLimitType, 
                        rate_config: RateLimitConfig) -> Tuple[bool, RateLimitStatus]:
        """Check if request is within rate limits"""
        try:
            now = datetime.utcnow()
            
            # Get current rate limit status
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT requests_minute, requests_hour, requests_day,
                       reset_minute, reset_hour, reset_day, blocked_until
                FROM rate_limits WHERE identifier = ? AND limit_type = ?
            ''', (identifier, limit_type.value))
            
            result = cursor.fetchone()
            
            if result:
                requests_minute, requests_hour, requests_day = result[0], result[1], result[2]
                reset_minute = datetime.fromisoformat(result[3]) if result[3] else now
                reset_hour = datetime.fromisoformat(result[4]) if result[4] else now
                reset_day = datetime.fromisoformat(result[5]) if result[5] else now
                blocked_until = datetime.fromisoformat(result[6]) if result[6] else None
            else:
                requests_minute = requests_hour = requests_day = 0
                reset_minute = reset_hour = reset_day = now
                blocked_until = None
            
            # Check if currently blocked
            if blocked_until and now < blocked_until:
                status = RateLimitStatus(
                    identifier=identifier,
                    limit_type=limit_type,
                    requests_made=requests_minute,
                    limit_per_minute=rate_config.requests_per_minute,
                    limit_per_hour=rate_config.requests_per_hour,
                    limit_per_day=rate_config.requests_per_day,
                    reset_time=reset_minute,
                    blocked_until=blocked_until
                )
                return False, status
            
            # Reset counters if time windows have expired
            if now >= reset_minute + timedelta(minutes=1):
                requests_minute = 0
                reset_minute = now
            
            if now >= reset_hour + timedelta(hours=1):
                requests_hour = 0
                reset_hour = now
            
            if now >= reset_day + timedelta(days=1):
                requests_day = 0
                reset_day = now
            
            # Check limits
            within_limits = (
                requests_minute < rate_config.requests_per_minute and
                requests_hour < rate_config.requests_per_hour and
                requests_day < rate_config.requests_per_day
            )
            
            if within_limits:
                # Increment counters
                requests_minute += 1
                requests_hour += 1
                requests_day += 1
                blocked_until = None
            else:
                # Block for configured duration
                blocked_until = now + timedelta(minutes=rate_config.block_duration_minutes)
            
            # Update database
            cursor.execute('''
                INSERT OR REPLACE INTO rate_limits 
                (identifier, limit_type, requests_minute, requests_hour, requests_day,
                 reset_minute, reset_hour, reset_day, blocked_until)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                identifier, limit_type.value, requests_minute, requests_hour, requests_day,
                reset_minute, reset_hour, reset_day, blocked_until
            ))
            
            conn.commit()
            conn.close()
            
            status = RateLimitStatus(
                identifier=identifier,
                limit_type=limit_type,
                requests_made=requests_minute,
                limit_per_minute=rate_config.requests_per_minute,
                limit_per_hour=rate_config.requests_per_hour,
                limit_per_day=rate_config.requests_per_day,
                reset_time=reset_minute,
                blocked_until=blocked_until
            )
            
            return within_limits, status
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            # On error, allow request but log
            status = RateLimitStatus(
                identifier=identifier,
                limit_type=limit_type,
                requests_made=0,
                limit_per_minute=rate_config.requests_per_minute,
                limit_per_hour=rate_config.requests_per_hour,
                limit_per_day=rate_config.requests_per_day,
                reset_time=now,
                blocked_until=None
            )
            return True, status
    
    def log_security_event(self, event_type: str, severity: str, source_ip: str,
                          endpoint: str, method: str, user_id: Optional[str] = None,
                          organization_id: Optional[str] = None, api_key_id: Optional[str] = None,
                          user_agent: Optional[str] = None, details: Optional[Dict] = None):
        """Log security event for audit trail"""
        try:
            event_id = str(uuid.uuid4())
            event = SecurityEvent(
                event_id=event_id,
                event_type=event_type,
                severity=severity,
                source_ip=source_ip,
                user_id=user_id,
                organization_id=organization_id,
                api_key_id=api_key_id,
                endpoint=endpoint,
                method=method,
                user_agent=user_agent or "",
                details=details or {},
                timestamp=datetime.utcnow()
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events 
                (event_id, event_type, severity, source_ip, user_id, organization_id,
                 api_key_id, endpoint, method, user_agent, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id, event_type, severity, source_ip, user_id, organization_id,
                api_key_id, endpoint, method, user_agent, json.dumps(details),
                event.timestamp
            ))
            
            conn.commit()
            conn.close()
            
            # Keep in-memory cache for recent events
            self.security_events.append(event)
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-500:]  # Keep last 500
            
            logger.info(f"Logged security event: {event_type} from {source_ip}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def add_ip_to_whitelist(self, ip_address: str, organization_id: str, description: str = ""):
        """Add IP address to Fortune 500 client whitelist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ip_whitelist 
                (ip_address, organization_id, description, is_active, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (ip_address, organization_id, description, True, datetime.utcnow()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added IP {ip_address} to whitelist for organization {organization_id}")
            
        except Exception as e:
            logger.error(f"Failed to add IP to whitelist: {e}")
            raise
    
    def is_ip_whitelisted(self, ip_address: str, organization_id: str) -> bool:
        """Check if IP is whitelisted for organization"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM ip_whitelist 
                WHERE ip_address = ? AND organization_id = ? AND is_active = TRUE
            ''', (ip_address, organization_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] > 0
            
        except Exception as e:
            logger.error(f"Failed to check IP whitelist: {e}")
            return False
    
    def get_security_events(self, organization_id: Optional[str] = None, 
                           limit: int = 100) -> List[SecurityEvent]:
        """Get recent security events for audit dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if organization_id:
                cursor.execute('''
                    SELECT event_id, event_type, severity, source_ip, user_id, organization_id,
                           api_key_id, endpoint, method, user_agent, details, timestamp
                    FROM security_events 
                    WHERE organization_id = ? OR organization_id IS NULL
                    ORDER BY timestamp DESC LIMIT ?
                ''', (organization_id, limit))
            else:
                cursor.execute('''
                    SELECT event_id, event_type, severity, source_ip, user_id, organization_id,
                           api_key_id, endpoint, method, user_agent, details, timestamp
                    FROM security_events 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            
            events = []
            for row in cursor.fetchall():
                events.append(SecurityEvent(
                    event_id=row[0],
                    event_type=row[1],
                    severity=row[2],
                    source_ip=row[3],
                    user_id=row[4],
                    organization_id=row[5],
                    api_key_id=row[6],
                    endpoint=row[7],
                    method=row[8],
                    user_agent=row[9],
                    details=json.loads(row[10]) if row[10] else {},
                    timestamp=datetime.fromisoformat(row[11])
                ))
            
            conn.close()
            return events
            
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []


# Global security manager instance
security_manager = EnterpriseAPISecurityManager()


def require_api_security(security_level: SecurityLevel = SecurityLevel.AUTHENTICATED,
                        permissions: List[str] = None):
    """
    Decorator for API endpoints requiring security validation.
    Implements comprehensive security checks for Fortune 500 compliance.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Apply security headers
                response_headers = security_manager.security_headers.copy()
                
                # Get request details
                source_ip = request.remote_addr
                endpoint = request.endpoint or request.path
                method = request.method
                user_agent = request.headers.get('User-Agent', '')
                
                # Check for API key authentication
                api_key_header = request.headers.get('X-API-Key')
                api_secret_header = request.headers.get('X-API-Secret')
                
                api_key_info = None
                user_id = None
                organization_id = None
                
                if api_key_header and api_secret_header:
                    api_key_info = security_manager.validate_api_key(api_key_header, api_secret_header)
                    if api_key_info:
                        user_id = api_key_info.user_id
                        organization_id = api_key_info.organization_id
                        
                        # Check IP whitelist for organization
                        if not security_manager.is_ip_whitelisted(source_ip, organization_id):
                            security_manager.log_security_event(
                                event_type="ip_not_whitelisted",
                                severity="warning",
                                source_ip=source_ip,
                                user_id=user_id,
                                organization_id=organization_id,
                                api_key_id=api_key_info.key_id,
                                endpoint=endpoint,
                                method=method,
                                user_agent=user_agent,
                                details={"message": "IP not in organization whitelist"}
                            )
                
                # Check security level requirements
                if security_level != SecurityLevel.PUBLIC:
                    if not api_key_info:
                        security_manager.log_security_event(
                            event_type="unauthorized_access",
                            severity="warning",
                            source_ip=source_ip,
                            endpoint=endpoint,
                            method=method,
                            user_agent=user_agent,
                            details={"message": "Missing or invalid API credentials"}
                        )
                        return jsonify({"error": "Unauthorized - Valid API key required"}), 401
                    
                    # Check permissions
                    if permissions:
                        missing_permissions = set(permissions) - set(api_key_info.permissions)
                        if missing_permissions:
                            security_manager.log_security_event(
                                event_type="insufficient_permissions",
                                severity="warning",
                                source_ip=source_ip,
                                user_id=user_id,
                                organization_id=organization_id,
                                api_key_id=api_key_info.key_id,
                                endpoint=endpoint,
                                method=method,
                                user_agent=user_agent,
                                details={"missing_permissions": list(missing_permissions)}
                            )
                            return jsonify({"error": "Insufficient permissions"}), 403
                
                # Rate limiting
                rate_config = security_manager.default_rate_limits[security_level]
                if api_key_info and api_key_info.rate_limit_config:
                    rate_config = api_key_info.rate_limit_config
                
                # Check multiple rate limit types
                rate_limit_checks = [
                    (source_ip, RateLimitType.PER_IP),
                ]
                
                if api_key_info:
                    rate_limit_checks.extend([
                        (api_key_info.key_id, RateLimitType.PER_API_KEY),
                        (organization_id, RateLimitType.PER_ORGANIZATION)
                    ])
                
                for identifier, limit_type in rate_limit_checks:
                    within_limits, status = security_manager.check_rate_limit(
                        identifier, limit_type, rate_config
                    )
                    
                    if not within_limits:
                        security_manager.log_security_event(
                            event_type="rate_limit_exceeded",
                            severity="warning",
                            source_ip=source_ip,
                            user_id=user_id,
                            organization_id=organization_id,
                            api_key_id=api_key_info.key_id if api_key_info else None,
                            endpoint=endpoint,
                            method=method,
                            user_agent=user_agent,
                            details={
                                "limit_type": limit_type.value,
                                "requests_made": status.requests_made,
                                "limit_per_minute": status.limit_per_minute
                            }
                        )
                        
                        response_headers.update({
                            'X-RateLimit-Limit': str(status.limit_per_minute),
                            'X-RateLimit-Remaining': str(max(0, status.limit_per_minute - status.requests_made)),
                            'X-RateLimit-Reset': str(int(status.reset_time.timestamp())),
                            'Retry-After': str(int((status.blocked_until - datetime.utcnow()).total_seconds()))
                        })
                        
                        return jsonify({
                            "error": "Rate limit exceeded",
                            "retry_after": int((status.blocked_until - datetime.utcnow()).total_seconds())
                        }), 429
                
                # Store security context for the request
                g.security_context = {
                    'api_key_info': api_key_info,
                    'user_id': user_id,
                    'organization_id': organization_id,
                    'source_ip': source_ip,
                    'security_level': security_level
                }
                
                # Log successful access
                security_manager.log_security_event(
                    event_type="api_access",
                    severity="info",
                    source_ip=source_ip,
                    user_id=user_id,
                    organization_id=organization_id,
                    api_key_id=api_key_info.key_id if api_key_info else None,
                    endpoint=endpoint,
                    method=method,
                    user_agent=user_agent,
                    details={"security_level": security_level.value}
                )
                
                # Execute the original function
                response = f(*args, **kwargs)
                
                # Apply security headers to response
                if hasattr(response, 'headers'):
                    for header, value in response_headers.items():
                        response.headers[header] = value
                
                return response
                
            except Exception as e:
                logger.error(f"Security validation error: {e}")
                security_manager.log_security_event(
                    event_type="security_error",
                    severity="error",
                    source_ip=request.remote_addr,
                    endpoint=request.endpoint or request.path,
                    method=request.method,
                    user_agent=request.headers.get('User-Agent', ''),
                    details={"error": str(e)}
                )
                return jsonify({"error": "Security validation failed"}), 500
        
        return decorated_function
    return decorator


def validate_request_data(required_fields: List[str] = None, 
                         optional_fields: List[str] = None,
                         max_size_mb: int = 10):
    """
    Decorator for validating request data and preventing injection attacks.
    Implements comprehensive input validation for Fortune 500 security.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check content length
                content_length = request.content_length
                if content_length and content_length > max_size_mb * 1024 * 1024:
                    return jsonify({"error": "Request too large"}), 413
                
                # Validate JSON data
                if request.is_json:
                    try:
                        data = request.get_json()
                        if not isinstance(data, dict):
                            return jsonify({"error": "Invalid JSON format"}), 400
                    except Exception:
                        return jsonify({"error": "Invalid JSON"}), 400
                else:
                    data = request.form.to_dict()
                
                # Check required fields
                if required_fields:
                    missing_fields = set(required_fields) - set(data.keys())
                    if missing_fields:
                        return jsonify({
                            "error": "Missing required fields",
                            "missing_fields": list(missing_fields)
                        }), 400
                
                # Check for unexpected fields
                if required_fields or optional_fields:
                    allowed_fields = set(required_fields or []) | set(optional_fields or [])
                    unexpected_fields = set(data.keys()) - allowed_fields
                    if unexpected_fields:
                        return jsonify({
                            "error": "Unexpected fields",
                            "unexpected_fields": list(unexpected_fields)
                        }), 400
                
                # Basic XSS and injection prevention
                dangerous_patterns = [
                    '<script', '</script>', 'javascript:', 'vbscript:',
                    'onload=', 'onerror=', 'onclick=', 'eval(',
                    'DROP TABLE', 'SELECT *', 'UNION SELECT',
                    'INSERT INTO', 'UPDATE SET', 'DELETE FROM'
                ]
                
                for key, value in data.items():
                    if isinstance(value, str):
                        value_lower = value.lower()
                        for pattern in dangerous_patterns:
                            if pattern.lower() in value_lower:
                                security_manager.log_security_event(
                                    event_type="malicious_input_detected",
                                    severity="high",
                                    source_ip=request.remote_addr,
                                    endpoint=request.endpoint or request.path,
                                    method=request.method,
                                    user_agent=request.headers.get('User-Agent', ''),
                                    details={
                                        "field": key,
                                        "pattern": pattern,
                                        "value_preview": value[:100]
                                    }
                                )
                                return jsonify({"error": "Invalid input detected"}), 400
                
                # Store validated data
                g.validated_data = data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Request validation error: {e}")
                return jsonify({"error": "Request validation failed"}), 400
        
        return decorated_function
    return decorator