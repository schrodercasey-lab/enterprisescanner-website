"""
JUPITER VR/AR Platform - API Server (Module G.3.12)

Flask + SocketIO server providing third-party API access.
RESTful endpoints and WebSocket streaming for VR integrations.

Features:
- REST API for VR data access (threats, sessions, analytics)
- WebSocket streaming for real-time updates
- API key authentication
- Rate limiting enforcement
- Usage tracking and analytics

Port: 5012

Enterprise Scanner - JUPITER Platform
October 2025
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
from datetime import datetime
from typing import Dict, List
import json

# Import API integration components
from api_integration import (
    VRAPIGateway,
    APIPermission,
    RateLimitTier,
    APIRequest
)


# ============================================================================
# Flask Application Setup
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# Configure CORS with whitelist (production-ready)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://enterprisescanner.com",
            "https://demo.enterprisescanner.com",
            "https://app.enterprisescanner.com",
            "http://localhost:*"  # For development
        ]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"],
    storage_uri="memory://"
)

socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize API Gateway
api_gateway = VRAPIGateway()

# Track connected WebSocket clients
connected_clients: Dict[str, Dict] = {}


# ============================================================================
# Authentication Middleware
# ============================================================================

def authenticate_api_request(required_permission=None):
    """Authenticate API request using headers"""
    api_key_id = request.headers.get('X-API-Key-ID')
    api_key_secret = request.headers.get('X-API-Key-Secret')
    
    if not api_key_id or not api_key_secret:
        return None, {'error': 'Missing API credentials'}, 401
    
    auth_result = api_gateway.authenticate_request(
        api_key_id,
        api_key_secret,
        required_permission
    )
    
    if not auth_result['authenticated']:
        return None, {'error': auth_result['error']}, 403
    
    return auth_result['api_key'], None, None


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'JUPITER VR API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'websocket_clients': len(connected_clients)
    })


@app.route('/api/keys', methods=['POST'])
def create_api_key():
    """Create a new API key"""
    data = request.get_json()
    
    # This would normally require admin authentication
    # For demo, we'll allow key creation
    
    api_key = api_gateway.auth_manager.generate_api_key(
        name=data.get('name', 'API Key'),
        owner_id=data.get('owner_id', 'default_owner'),
        permissions=[APIPermission[p] for p in data.get('permissions', ['READ_THREATS'])],
        rate_limit_tier=RateLimitTier[data.get('tier', 'BASIC')],
        expires_in_days=data.get('expires_in_days')
    )
    
    return jsonify({
        'success': True,
        'api_key': {
            'key_id': api_key.key_id,
            'key_secret': api_key.key_secret,  # Only returned once
            'name': api_key.name,
            'tier': api_key.rate_limit_tier.value,
            'permissions': [p.value for p in api_key.permissions],
            'created_at': api_key.created_at.isoformat(),
            'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None
        }
    })


@app.route('/api/keys', methods=['GET'])
@limiter.limit("100 per hour")
def list_api_keys():
    """List API keys for authenticated user"""
    api_key, error, status = authenticate_api_request()
    if error:
        return jsonify(error), status
    
    keys = api_gateway.auth_manager.list_api_keys(api_key.owner_id)
    
    return jsonify({
        'success': True,
        'keys': [
            {
                'key_id': k.key_id,
                'name': k.name,
                'tier': k.rate_limit_tier.value,
                'created_at': k.created_at.isoformat(),
                'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None,
                'is_active': k.is_active
            }
            for k in keys
        ]
    })


@app.route('/api/keys/<key_id>', methods=['DELETE'])
@limiter.limit("20 per hour")
def revoke_api_key(key_id):
    """Revoke an API key"""
    api_key, error, status = authenticate_api_request()
    if error:
        return jsonify(error), status
    
    success = api_gateway.auth_manager.revoke_api_key(key_id)
    
    return jsonify({
        'success': success,
        'message': 'API key revoked' if success else 'API key not found'
    })


@app.route('/api/threats', methods=['GET'])
@limiter.limit("500 per hour")
def get_threats():
    """Get threat data"""
    api_key, error, status = authenticate_api_request(APIPermission.READ_THREATS)
    if error:
        return jsonify(error), status
    
    limit = int(request.args.get('limit', 100))
    severity = request.args.get('severity')
    
    # Log request
    api_request = APIRequest(
        request_id=secrets.token_hex(16),
        api_key_id=api_key.key_id,
        endpoint='/api/threats',
        method='GET',
        timestamp=datetime.now(),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    # Mock threat data (would come from actual threat database)
    threats = [
        {
            'threat_id': f'threat_{i}',
            'type': 'malware',
            'severity': 'high',
            'source_ip': f'192.168.1.{i}',
            'detected_at': datetime.now().isoformat(),
            'status': 'active'
        }
        for i in range(min(limit, 50))
    ]
    
    # Complete request log
    api_request.status_code = 200
    api_request.response_time_ms = 45.2
    api_request.bytes_transferred = len(json.dumps(threats))
    
    api_gateway.log_request(api_request)
    
    return jsonify({
        'success': True,
        'threats': threats,
        'count': len(threats),
        'limit': limit
    })


@app.route('/api/vr/sessions', methods=['POST'])
def create_vr_session():
    """Create a new VR session"""
    api_key, error, status = authenticate_api_request(APIPermission.WRITE_VR_SESSIONS)
    if error:
        return jsonify(error), status
    
    data = request.get_json()
    
    session_id = f"vr_session_{secrets.token_hex(16)}"
    
    session = {
        'session_id': session_id,
        'user_id': data.get('user_id'),
        'environment': data.get('environment', 'default'),
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    # Log request
    api_request = APIRequest(
        request_id=secrets.token_hex(16),
        api_key_id=api_key.key_id,
        endpoint='/api/vr/sessions',
        method='POST',
        timestamp=datetime.now(),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        status_code=201,
        response_time_ms=32.1,
        bytes_transferred=len(json.dumps(session))
    )
    
    api_gateway.log_request(api_request)
    
    # Trigger webhook
    api_gateway.trigger_webhook('vr.session.created', session)
    
    return jsonify({
        'success': True,
        'session': session
    }), 201


@app.route('/api/vr/sessions/<session_id>', methods=['GET'])
def get_vr_session(session_id):
    """Get VR session details"""
    api_key, error, status = authenticate_api_request(APIPermission.READ_VR_SESSIONS)
    if error:
        return jsonify(error), status
    
    # Mock session data
    session = {
        'session_id': session_id,
        'user_id': 'user_001',
        'environment': 'threat_visualization',
        'created_at': datetime.now().isoformat(),
        'duration_seconds': 1234,
        'interactions': 56,
        'status': 'active'
    }
    
    return jsonify({
        'success': True,
        'session': session
    })


@app.route('/api/analytics/<metric>', methods=['GET'])
def get_analytics(metric):
    """Get analytics data"""
    api_key, error, status = authenticate_api_request(APIPermission.READ_ANALYTICS)
    if error:
        return jsonify(error), status
    
    time_range = request.args.get('time_range', '24h')
    
    # Mock analytics data
    data = {
        'metric': metric,
        'time_range': time_range,
        'values': [
            {'timestamp': datetime.now().isoformat(), 'value': 100 + i}
            for i in range(10)
        ]
    }
    
    return jsonify({
        'success': True,
        'analytics': data
    })


@app.route('/api/usage', methods=['GET'])
def get_usage_stats():
    """Get API usage statistics"""
    api_key, error, status = authenticate_api_request()
    if error:
        return jsonify(error), status
    
    # Get usage stats
    usage_stats = api_gateway.rate_limiter.get_usage_stats(api_key.key_id)
    rate_limit = api_gateway.rate_limiter.check_rate_limit(api_key)
    quota = api_gateway.rate_limiter.check_quota(api_key)
    
    return jsonify({
        'success': True,
        'usage': {
            'requests_count': usage_stats.requests_count if usage_stats else 0,
            'data_transferred_mb': round(
                (usage_stats.data_transferred_bytes / (1024 * 1024)) if usage_stats else 0,
                2
            ),
            'rate_limit': rate_limit,
            'quota': quota
        }
    })


@app.route('/api/stats', methods=['GET'])
def get_api_stats():
    """Get overall API statistics"""
    api_key, error, status = authenticate_api_request(APIPermission.ADMIN)
    if error:
        return jsonify(error), status
    
    time_range = int(request.args.get('hours', 24))
    
    stats = api_gateway.get_api_statistics(
        api_key_id=api_key.key_id,
        time_range_hours=time_range
    )
    
    return jsonify({
        'success': True,
        'statistics': stats
    })


@app.route('/api/webhooks', methods=['POST'])
def register_webhook():
    """Register a webhook"""
    api_key, error, status = authenticate_api_request()
    if error:
        return jsonify(error), status
    
    data = request.get_json()
    
    webhook = api_gateway.register_webhook(
        url=data['url'],
        events=data['events'],
        owner_id=api_key.owner_id
    )
    
    return jsonify({
        'success': True,
        'webhook': {
            'webhook_id': webhook.webhook_id,
            'url': webhook.url,
            'events': webhook.events,
            'secret': webhook.secret  # Only returned once
        }
    }), 201


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to JUPITER VR API'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if request.sid in connected_clients:
        del connected_clients[request.sid]
    print(f"Client disconnected: {request.sid}")


@socketio.on('authenticate')
def handle_authenticate(data):
    """Authenticate WebSocket connection"""
    api_key_id = data.get('api_key_id')
    api_key_secret = data.get('api_key_secret')
    
    if not api_key_id or not api_key_secret:
        emit('error', {'message': 'Missing credentials'})
        disconnect()
        return
    
    auth_result = api_gateway.authenticate_request(api_key_id, api_key_secret)
    
    if not auth_result['authenticated']:
        emit('error', {'message': auth_result['error']})
        disconnect()
        return
    
    # Store client info
    connected_clients[request.sid] = {
        'api_key': auth_result['api_key'],
        'connected_at': datetime.now()
    }
    
    emit('authenticated', {
        'message': 'Authentication successful',
        'rate_limit': auth_result['rate_limit'],
        'quota': auth_result['quota']
    })


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to data streams"""
    if request.sid not in connected_clients:
        emit('error', {'message': 'Not authenticated'})
        return
    
    channels = data.get('channels', [])
    
    # Store subscription
    connected_clients[request.sid]['subscriptions'] = channels
    
    emit('subscribed', {
        'channels': channels,
        'message': f'Subscribed to {len(channels)} channels'
    })


@socketio.on('stream_threats')
def handle_stream_threats():
    """Stream threat data to client"""
    if request.sid not in connected_clients:
        emit('error', {'message': 'Not authenticated'})
        return
    
    # Mock streaming (would come from real threat feed)
    emit('threat_update', {
        'threat_id': f'threat_{secrets.token_hex(8)}',
        'type': 'malware',
        'severity': 'high',
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# Background Tasks
# ============================================================================

def broadcast_system_status():
    """Broadcast system status to all connected clients"""
    if not connected_clients:
        return
    
    status = {
        'timestamp': datetime.now().isoformat(),
        'active_threats': 42,
        'vr_sessions': 12,
        'system_health': 'good'
    }
    
    socketio.emit('system_status', status)


# ============================================================================
# Server Startup
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("JUPITER VR API Server - Module G.3.12")
    print("=" * 70)
    print("\nStarting API server on port 5012...")
    print("\nRESTful API Endpoints:")
    print("  • GET  /api/health           - Health check")
    print("  • POST /api/keys             - Create API key")
    print("  • GET  /api/keys             - List API keys")
    print("  • DEL  /api/keys/<id>        - Revoke API key")
    print("  • GET  /api/threats          - Get threats")
    print("  • POST /api/vr/sessions      - Create VR session")
    print("  • GET  /api/vr/sessions/<id> - Get session details")
    print("  • GET  /api/analytics/<metric> - Get analytics")
    print("  • GET  /api/usage            - Get usage stats")
    print("  • GET  /api/stats            - Get API statistics")
    print("  • POST /api/webhooks         - Register webhook")
    print("\nWebSocket Events:")
    print("  • authenticate - Authenticate connection")
    print("  • subscribe    - Subscribe to channels")
    print("  • stream_threats - Stream threat updates")
    print("\nServer Configuration:")
    print("  • Port: 5012")
    print("  • CORS: Enabled")
    print("  • WebSocket: Enabled")
    print("=" * 70)
    print("\nServer ready for API requests!")
    print("=" * 70 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5012, debug=False, allow_unsafe_werkzeug=True)
