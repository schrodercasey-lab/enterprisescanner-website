"""
API Security Management Endpoints
REST API for managing API keys, rate limits, and security monitoring.
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.api_security import (
        security_manager, require_api_security, validate_request_data,
        SecurityLevel, RateLimitType
    )
except ImportError:
    # Mock API security if not available
    class MockSecurityManager:
        def create_api_key(self, *args, **kwargs): return {'key': 'mock-key'}
        def revoke_api_key(self, *args): return True
        def get_api_keys(self, *args): return []
    security_manager = MockSecurityManager()
    def require_api_security(*args, **kwargs):
        def decorator(f): return f
        return decorator
    def validate_request_data(*args, **kwargs):
        def decorator(f): return f
        return decorator
    class SecurityLevel: PUBLIC = 'public'; PRIVILEGED = 'privileged'
    class RateLimitType: STANDARD = 'standard'; STRICT = 'strict'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
api_security_bp = Blueprint('api_security', __name__, url_prefix='/api/security')


@api_security_bp.route('/keys', methods=['POST'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['api_key_management'])
@validate_request_data(
    required_fields=['name', 'permissions'],
    optional_fields=['expires_days', 'organization_id']
)
def create_api_key():
    """Create new API key for organization"""
    try:
        data = g.validated_data
        security_context = g.security_context
        
        # Use current organization if not specified
        organization_id = data.get('organization_id', security_context['organization_id'])
        user_id = security_context['user_id']
        
        # Validate permissions
        available_permissions = [
            'api_access', 'read_reports', 'write_reports', 'user_management',
            'api_key_management', 'security_monitoring', 'threat_intelligence',
            'vulnerability_scanning', 'compliance_reporting', 'audit_access'
        ]
        
        invalid_permissions = set(data['permissions']) - set(available_permissions)
        if invalid_permissions:
            return jsonify({
                "error": "Invalid permissions",
                "invalid_permissions": list(invalid_permissions),
                "available_permissions": available_permissions
            }), 400
        
        # Generate API key
        api_key = security_manager.generate_api_key(
            organization_id=organization_id,
            user_id=user_id,
            name=data['name'],
            permissions=data['permissions'],
            expires_days=data.get('expires_days')
        )
        
        return jsonify({
            "message": "API key created successfully",
            "api_key": {
                "key_id": api_key.key_id,
                "key_secret": api_key.key_secret,  # Only returned once
                "name": api_key.name,
                "permissions": api_key.permissions,
                "organization_id": api_key.organization_id,
                "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
                "created_at": api_key.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        return jsonify({"error": "Failed to create API key"}), 500


@api_security_bp.route('/keys', methods=['GET'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['api_key_management'])
def list_api_keys():
    """List API keys for organization"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        # Get API keys from database
        import sqlite3
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT key_id, name, permissions, is_active, created_at, expires_at, last_used_at
            FROM api_keys WHERE organization_id = ?
            ORDER BY created_at DESC
        ''', (organization_id,))
        
        api_keys = []
        for row in cursor.fetchall():
            api_keys.append({
                "key_id": row[0],
                "name": row[1],
                "permissions": json.loads(row[2]),
                "is_active": row[3],
                "created_at": row[4],
                "expires_at": row[5],
                "last_used_at": row[6],
                "key_secret": "***hidden***"  # Never return secret
            })
        
        conn.close()
        
        return jsonify({
            "api_keys": api_keys,
            "total": len(api_keys)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        return jsonify({"error": "Failed to list API keys"}), 500


@api_security_bp.route('/keys/<key_id>', methods=['DELETE'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['api_key_management'])
def revoke_api_key(key_id):
    """Revoke API key"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        import sqlite3
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        
        # Check if key belongs to organization
        cursor.execute('''
            SELECT organization_id FROM api_keys WHERE key_id = ?
        ''', (key_id,))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "API key not found"}), 404
        
        if result[0] != organization_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Revoke the key
        cursor.execute('''
            UPDATE api_keys SET is_active = FALSE WHERE key_id = ?
        ''', (key_id,))
        
        conn.commit()
        conn.close()
        
        # Log security event
        security_manager.log_security_event(
            event_type="api_key_revoked",
            severity="info",
            source_ip=request.remote_addr,
            user_id=security_context['user_id'],
            organization_id=organization_id,
            endpoint="/api/security/keys",
            method="DELETE",
            details={"revoked_key_id": key_id}
        )
        
        return jsonify({"message": "API key revoked successfully"}), 200
        
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        return jsonify({"error": "Failed to revoke API key"}), 500


@api_security_bp.route('/events', methods=['GET'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['security_monitoring'])
def get_security_events():
    """Get security events for organization"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 100)), 1000)
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        
        # Get events from security manager
        events = security_manager.get_security_events(organization_id, limit)
        
        # Filter by event type and severity if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # Convert to JSON format
        events_data = []
        for event in events:
            events_data.append({
                "event_id": event.event_id,
                "event_type": event.event_type,
                "severity": event.severity,
                "source_ip": event.source_ip,
                "user_id": event.user_id,
                "organization_id": event.organization_id,
                "api_key_id": event.api_key_id,
                "endpoint": event.endpoint,
                "method": event.method,
                "user_agent": event.user_agent,
                "details": event.details,
                "timestamp": event.timestamp.isoformat()
            })
        
        return jsonify({
            "events": events_data,
            "total": len(events_data),
            "filters": {
                "event_type": event_type,
                "severity": severity,
                "limit": limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        return jsonify({"error": "Failed to get security events"}), 500


@api_security_bp.route('/rate-limits', methods=['GET'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['security_monitoring'])
def get_rate_limit_status():
    """Get current rate limit status"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        import sqlite3
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        
        # Get rate limit data for organization
        cursor.execute('''
            SELECT identifier, limit_type, requests_minute, requests_hour, requests_day,
                   reset_minute, reset_hour, reset_day, blocked_until
            FROM rate_limits 
            WHERE identifier = ? OR identifier LIKE ?
            ORDER BY limit_type, identifier
        ''', (organization_id, f"{organization_id}_%"))
        
        rate_limits = []
        for row in cursor.fetchall():
            rate_limits.append({
                "identifier": row[0],
                "limit_type": row[1],
                "requests_minute": row[2],
                "requests_hour": row[3],
                "requests_day": row[4],
                "reset_minute": row[5],
                "reset_hour": row[6],
                "reset_day": row[7],
                "blocked_until": row[8],
                "is_blocked": bool(row[8] and datetime.fromisoformat(row[8]) > datetime.utcnow())
            })
        
        conn.close()
        
        return jsonify({
            "rate_limits": rate_limits,
            "organization_id": organization_id
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get rate limit status: {e}")
        return jsonify({"error": "Failed to get rate limit status"}), 500


@api_security_bp.route('/whitelist', methods=['POST'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['security_monitoring'])
@validate_request_data(
    required_fields=['ip_address'],
    optional_fields=['description']
)
def add_ip_whitelist():
    """Add IP address to organization whitelist"""
    try:
        data = g.validated_data
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        ip_address = data['ip_address']
        description = data.get('description', '')
        
        # Validate IP address format
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return jsonify({"error": "Invalid IP address format"}), 400
        
        # Add to whitelist
        security_manager.add_ip_to_whitelist(ip_address, organization_id, description)
        
        return jsonify({
            "message": "IP address added to whitelist",
            "ip_address": ip_address,
            "organization_id": organization_id
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to add IP to whitelist: {e}")
        return jsonify({"error": "Failed to add IP to whitelist"}), 500


@api_security_bp.route('/whitelist', methods=['GET'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['security_monitoring'])
def get_ip_whitelist():
    """Get IP whitelist for organization"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        import sqlite3
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ip_address, description, is_active, created_at
            FROM ip_whitelist 
            WHERE organization_id = ?
            ORDER BY created_at DESC
        ''', (organization_id,))
        
        whitelist = []
        for row in cursor.fetchall():
            whitelist.append({
                "ip_address": row[0],
                "description": row[1],
                "is_active": row[2],
                "created_at": row[3]
            })
        
        conn.close()
        
        return jsonify({
            "whitelist": whitelist,
            "organization_id": organization_id
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get IP whitelist: {e}")
        return jsonify({"error": "Failed to get IP whitelist"}), 500


@api_security_bp.route('/whitelist/<ip_address>', methods=['DELETE'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['security_monitoring'])
def remove_ip_whitelist(ip_address):
    """Remove IP address from organization whitelist"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        import sqlite3
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ip_whitelist SET is_active = FALSE 
            WHERE ip_address = ? AND organization_id = ?
        ''', (ip_address, organization_id))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "IP address not found in whitelist"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "IP address removed from whitelist",
            "ip_address": ip_address
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to remove IP from whitelist: {e}")
        return jsonify({"error": "Failed to remove IP from whitelist"}), 500


@api_security_bp.route('/stats', methods=['GET'])
@require_api_security(SecurityLevel.PRIVILEGED, permissions=['security_monitoring'])
def get_security_stats():
    """Get security statistics for organization"""
    try:
        security_context = g.security_context
        organization_id = security_context['organization_id']
        
        import sqlite3
        from collections import defaultdict
        
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        
        # Get event statistics for last 24 hours
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        cursor.execute('''
            SELECT event_type, severity, COUNT(*) as count
            FROM security_events 
            WHERE organization_id = ? AND timestamp > ?
            GROUP BY event_type, severity
            ORDER BY count DESC
        ''', (organization_id, twenty_four_hours_ago))
        
        event_stats = defaultdict(lambda: defaultdict(int))
        total_events = 0
        
        for row in cursor.fetchall():
            event_stats[row[0]][row[1]] = row[2]
            total_events += row[2]
        
        # Get API key usage statistics
        cursor.execute('''
            SELECT COUNT(*) as total_keys, 
                   SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_keys
            FROM api_keys 
            WHERE organization_id = ?
        ''', (organization_id,))
        
        key_stats = cursor.fetchone()
        
        # Get rate limit violations
        cursor.execute('''
            SELECT COUNT(*) as violations
            FROM security_events 
            WHERE organization_id = ? AND event_type = 'rate_limit_exceeded' 
            AND timestamp > ?
        ''', (organization_id, twenty_four_hours_ago))
        
        rate_limit_violations = cursor.fetchone()[0]
        
        # Get IP whitelist count
        cursor.execute('''
            SELECT COUNT(*) as whitelisted_ips
            FROM ip_whitelist 
            WHERE organization_id = ? AND is_active = 1
        ''', (organization_id,))
        
        whitelisted_ips = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "organization_id": organization_id,
            "time_period": "24_hours",
            "total_events": total_events,
            "event_breakdown": dict(event_stats),
            "api_keys": {
                "total": key_stats[0],
                "active": key_stats[1]
            },
            "rate_limit_violations": rate_limit_violations,
            "whitelisted_ips": whitelisted_ips,
            "security_score": max(0, 100 - (rate_limit_violations * 2))  # Simple scoring
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get security stats: {e}")
        return jsonify({"error": "Failed to get security stats"}), 500


@api_security_bp.route('/test', methods=['GET'])
@require_api_security(SecurityLevel.PUBLIC)
def test_security():
    """Test endpoint for security validation"""
    try:
        security_context = g.get('security_context', {})
        
        return jsonify({
            "message": "Security test successful",
            "timestamp": datetime.utcnow().isoformat(),
            "security_context": {
                "authenticated": bool(security_context.get('api_key_info')),
                "organization_id": security_context.get('organization_id'),
                "user_id": security_context.get('user_id'),
                "source_ip": security_context.get('source_ip'),
                "security_level": security_context.get('security_level', {}).value if security_context.get('security_level') else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Security test failed: {e}")
        return jsonify({"error": "Security test failed"}), 500


# Error handlers
@api_security_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@api_security_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@api_security_bp.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403


@api_security_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@api_security_bp.errorhandler(429)
def rate_limited(error):
    return jsonify({"error": "Rate limit exceeded"}), 429


@api_security_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500