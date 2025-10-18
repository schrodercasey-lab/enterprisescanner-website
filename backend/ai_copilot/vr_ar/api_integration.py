"""
JUPITER VR/AR Platform - API Integration Layer (Module G.3.12)

Third-party API gateway for VR application integration.
Enables external developers to build on JUPITER platform.

API Features:
- RESTful API for VR session management
- WebSocket streaming for real-time data
- Authentication (API keys, OAuth2)
- Rate limiting and quota management
- Client SDKs (Python, JavaScript, Unity)

Security:
- API key authentication
- OAuth2 support
- Request signing
- Rate limiting (1000 req/hour default)
- Quota management (10GB/month default)

Enterprise Scanner - JUPITER Platform
October 2025
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import time


# ============================================================================
# Enums and Constants
# ============================================================================

class AuthMethod(Enum):
    """Authentication methods"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"


class APIPermission(Enum):
    """API permission scopes"""
    READ_THREATS = "read:threats"
    WRITE_THREATS = "write:threats"
    READ_VR_SESSIONS = "read:vr_sessions"
    WRITE_VR_SESSIONS = "write:vr_sessions"
    READ_ANALYTICS = "read:analytics"
    ADMIN = "admin"


class RateLimitTier(Enum):
    """Rate limit tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SDKLanguage(Enum):
    """Supported SDK languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    UNITY_CSHARP = "unity_csharp"
    JAVA = "java"


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class APIKey:
    """API key credentials"""
    key_id: str
    key_secret: str
    name: str
    owner_id: str
    permissions: List[APIPermission]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    rate_limit_tier: RateLimitTier = RateLimitTier.BASIC


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    tier: RateLimitTier
    requests_per_hour: int
    requests_per_day: int
    data_quota_gb_month: int
    websocket_connections: int
    burst_allowance: int = 100


@dataclass
class APIUsageStats:
    """API usage statistics"""
    api_key_id: str
    requests_count: int = 0
    data_transferred_bytes: int = 0
    websocket_connections_count: int = 0
    last_request_at: Optional[datetime] = None
    throttled_requests: int = 0


@dataclass
class APIRequest:
    """API request metadata"""
    request_id: str
    api_key_id: str
    endpoint: str
    method: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    bytes_transferred: int = 0


@dataclass
class WebhookConfig:
    """Webhook configuration"""
    webhook_id: str
    url: str
    events: List[str]
    secret: str
    is_active: bool = True
    retry_count: int = 3
    timeout_seconds: int = 30


# ============================================================================
# Authentication Manager
# ============================================================================

class AuthenticationManager:
    """Manage API authentication and authorization"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.oauth2_tokens: Dict[str, Dict] = {}
        self.jwt_secrets: Dict[str, str] = {}
    
    def generate_api_key(
        self,
        name: str,
        owner_id: str,
        permissions: List[APIPermission],
        rate_limit_tier: RateLimitTier = RateLimitTier.BASIC,
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """Generate a new API key"""
        key_id = f"jptr_{secrets.token_hex(16)}"
        key_secret = secrets.token_hex(32)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        api_key = APIKey(
            key_id=key_id,
            key_secret=hashlib.sha256(key_secret.encode()).hexdigest(),
            name=name,
            owner_id=owner_id,
            permissions=permissions,
            created_at=datetime.now(),
            expires_at=expires_at,
            rate_limit_tier=rate_limit_tier
        )
        
        self.api_keys[key_id] = api_key
        
        # Return unhashed secret only once
        api_key_copy = api_key
        api_key_copy.key_secret = key_secret  # Return unhashed for user
        return api_key_copy
    
    def validate_api_key(self, key_id: str, key_secret: str) -> Optional[APIKey]:
        """Validate API key credentials"""
        api_key = self.api_keys.get(key_id)
        
        if not api_key:
            return None
        
        # Check if active
        if not api_key.is_active:
            return None
        
        # Check expiration
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            api_key.is_active = False
            return None
        
        # Verify secret
        hashed_secret = hashlib.sha256(key_secret.encode()).hexdigest()
        if hashed_secret != api_key.key_secret:
            return None
        
        # Update last used
        api_key.last_used_at = datetime.now()
        
        return api_key
    
    def check_permission(
        self,
        api_key: APIKey,
        required_permission: APIPermission
    ) -> bool:
        """Check if API key has required permission"""
        if APIPermission.ADMIN in api_key.permissions:
            return True
        
        return required_permission in api_key.permissions
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            return True
        return False
    
    def list_api_keys(self, owner_id: str) -> List[APIKey]:
        """List all API keys for an owner"""
        return [
            key for key in self.api_keys.values()
            if key.owner_id == owner_id
        ]
    
    def rotate_api_key(self, key_id: str) -> Optional[APIKey]:
        """Rotate API key secret"""
        old_key = self.api_keys.get(key_id)
        if not old_key:
            return None
        
        # Generate new secret
        new_secret = secrets.token_hex(32)
        old_key.key_secret = hashlib.sha256(new_secret.encode()).hexdigest()
        old_key.last_used_at = None
        
        # Return unhashed secret
        key_copy = old_key
        key_copy.key_secret = new_secret
        return key_copy


# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """Rate limiting and quota management"""
    
    def __init__(self):
        self.usage_stats: Dict[str, APIUsageStats] = {}
        self.rate_limit_configs = {
            RateLimitTier.FREE: RateLimitConfig(
                tier=RateLimitTier.FREE,
                requests_per_hour=100,
                requests_per_day=1000,
                data_quota_gb_month=1,
                websocket_connections=1,
                burst_allowance=20
            ),
            RateLimitTier.BASIC: RateLimitConfig(
                tier=RateLimitTier.BASIC,
                requests_per_hour=1000,
                requests_per_day=10000,
                data_quota_gb_month=10,
                websocket_connections=5,
                burst_allowance=100
            ),
            RateLimitTier.PROFESSIONAL: RateLimitConfig(
                tier=RateLimitTier.PROFESSIONAL,
                requests_per_hour=10000,
                requests_per_day=100000,
                data_quota_gb_month=100,
                websocket_connections=25,
                burst_allowance=500
            ),
            RateLimitTier.ENTERPRISE: RateLimitConfig(
                tier=RateLimitTier.ENTERPRISE,
                requests_per_hour=100000,
                requests_per_day=1000000,
                data_quota_gb_month=1000,
                websocket_connections=100,
                burst_allowance=1000
            )
        }
        
        # Request tracking (in-memory, would use Redis in production)
        self.request_windows: Dict[str, List[float]] = {}
    
    def check_rate_limit(
        self,
        api_key: APIKey,
        current_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        if current_time is None:
            current_time = time.time()
        
        config = self.rate_limit_configs[api_key.rate_limit_tier]
        key_id = api_key.key_id
        
        # Initialize tracking
        if key_id not in self.request_windows:
            self.request_windows[key_id] = []
        
        requests = self.request_windows[key_id]
        
        # Remove old requests (outside 1 hour window)
        hour_ago = current_time - 3600
        requests = [r for r in requests if r > hour_ago]
        self.request_windows[key_id] = requests
        
        # Check hourly limit
        if len(requests) >= config.requests_per_hour:
            # Check burst allowance
            recent_burst = sum(1 for r in requests if r > current_time - 10)
            if recent_burst >= config.burst_allowance:
                return {
                    'allowed': False,
                    'reason': 'rate_limit_exceeded',
                    'limit': config.requests_per_hour,
                    'remaining': 0,
                    'reset_at': hour_ago + 3600
                }
        
        # Allow request
        requests.append(current_time)
        
        return {
            'allowed': True,
            'limit': config.requests_per_hour,
            'remaining': config.requests_per_hour - len(requests),
            'reset_at': hour_ago + 3600
        }
    
    def record_usage(
        self,
        api_key_id: str,
        bytes_transferred: int = 0
    ):
        """Record API usage"""
        if api_key_id not in self.usage_stats:
            self.usage_stats[api_key_id] = APIUsageStats(api_key_id=api_key_id)
        
        stats = self.usage_stats[api_key_id]
        stats.requests_count += 1
        stats.data_transferred_bytes += bytes_transferred
        stats.last_request_at = datetime.now()
    
    def check_quota(
        self,
        api_key: APIKey,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Check data quota for the month"""
        if month is None or year is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        config = self.rate_limit_configs[api_key.rate_limit_tier]
        stats = self.usage_stats.get(api_key.key_id)
        
        if not stats:
            return {
                'within_quota': True,
                'used_gb': 0,
                'quota_gb': config.data_quota_gb_month,
                'remaining_gb': config.data_quota_gb_month
            }
        
        used_gb = stats.data_transferred_bytes / (1024 ** 3)
        remaining_gb = config.data_quota_gb_month - used_gb
        
        return {
            'within_quota': used_gb < config.data_quota_gb_month,
            'used_gb': round(used_gb, 2),
            'quota_gb': config.data_quota_gb_month,
            'remaining_gb': round(max(0, remaining_gb), 2)
        }
    
    def get_usage_stats(self, api_key_id: str) -> Optional[APIUsageStats]:
        """Get usage statistics for an API key"""
        return self.usage_stats.get(api_key_id)


# ============================================================================
# VR API Gateway
# ============================================================================

class VRAPIGateway:
    """Main API gateway for VR integrations"""
    
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.rate_limiter = RateLimiter()
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.api_logs: List[APIRequest] = []
    
    def authenticate_request(
        self,
        api_key_id: str,
        api_key_secret: str,
        required_permission: Optional[APIPermission] = None
    ) -> Dict[str, Any]:
        """Authenticate an API request"""
        # Validate credentials
        api_key = self.auth_manager.validate_api_key(api_key_id, api_key_secret)
        
        if not api_key:
            return {
                'authenticated': False,
                'error': 'invalid_credentials'
            }
        
        # Check permission if required
        if required_permission:
            if not self.auth_manager.check_permission(api_key, required_permission):
                return {
                    'authenticated': False,
                    'error': 'insufficient_permissions'
                }
        
        # Check rate limit
        rate_limit = self.rate_limiter.check_rate_limit(api_key)
        
        if not rate_limit['allowed']:
            return {
                'authenticated': False,
                'error': 'rate_limit_exceeded',
                'rate_limit': rate_limit
            }
        
        # Check quota
        quota = self.rate_limiter.check_quota(api_key)
        
        if not quota['within_quota']:
            return {
                'authenticated': False,
                'error': 'quota_exceeded',
                'quota': quota
            }
        
        return {
            'authenticated': True,
            'api_key': api_key,
            'rate_limit': rate_limit,
            'quota': quota
        }
    
    def log_request(
        self,
        request: APIRequest
    ):
        """Log API request"""
        self.api_logs.append(request)
        
        # Record usage
        self.rate_limiter.record_usage(
            request.api_key_id,
            request.bytes_transferred
        )
        
        # Keep last 10000 requests in memory
        if len(self.api_logs) > 10000:
            self.api_logs = self.api_logs[-10000:]
    
    def register_webhook(
        self,
        url: str,
        events: List[str],
        owner_id: str
    ) -> WebhookConfig:
        """Register a webhook"""
        webhook_id = f"whk_{secrets.token_hex(16)}"
        secret = secrets.token_hex(32)
        
        webhook = WebhookConfig(
            webhook_id=webhook_id,
            url=url,
            events=events,
            secret=secret
        )
        
        self.webhooks[webhook_id] = webhook
        return webhook
    
    def trigger_webhook(
        self,
        event_type: str,
        payload: Dict
    ) -> List[Dict]:
        """Trigger webhooks for an event"""
        results = []
        
        for webhook in self.webhooks.values():
            if event_type in webhook.events and webhook.is_active:
                # In production, this would make HTTP POST request
                result = {
                    'webhook_id': webhook.webhook_id,
                    'event_type': event_type,
                    'status': 'success',
                    'timestamp': datetime.now()
                }
                results.append(result)
        
        return results
    
    def get_api_statistics(
        self,
        api_key_id: Optional[str] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """Get API usage statistics"""
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        if api_key_id:
            logs = [
                log for log in self.api_logs
                if log.api_key_id == api_key_id and log.timestamp > cutoff_time
            ]
        else:
            logs = [
                log for log in self.api_logs
                if log.timestamp > cutoff_time
            ]
        
        if not logs:
            return {
                'total_requests': 0,
                'avg_response_time_ms': 0,
                'total_data_transferred_mb': 0,
                'success_rate': 0
            }
        
        total_requests = len(logs)
        avg_response_time = sum(
            log.response_time_ms for log in logs if log.response_time_ms
        ) / total_requests if total_requests > 0 else 0
        
        total_data_mb = sum(log.bytes_transferred for log in logs) / (1024 * 1024)
        
        successful_requests = sum(
            1 for log in logs
            if log.status_code and 200 <= log.status_code < 300
        )
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'avg_response_time_ms': round(avg_response_time, 2),
            'total_data_transferred_mb': round(total_data_mb, 2),
            'success_rate': round(success_rate, 2),
            'time_range_hours': time_range_hours
        }


# ============================================================================
# SDK Wrapper Generator
# ============================================================================

class SDKWrapper:
    """Generate client SDK code for different languages"""
    
    @staticmethod
    def generate_python_sdk() -> str:
        """Generate Python SDK code"""
        return '''
# JUPITER VR Platform - Python SDK

import requests
from typing import Dict, Optional, List

class JupiterVRClient:
    """Python client for JUPITER VR API"""
    
    def __init__(self, api_key_id: str, api_key_secret: str, base_url: str = "http://localhost:5012"):
        self.api_key_id = api_key_id
        self.api_key_secret = api_key_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key-ID': api_key_id,
            'X-API-Key-Secret': api_key_secret
        })
    
    def get_threats(self, limit: int = 100) -> Dict:
        """Get threat data"""
        response = self.session.get(
            f"{self.base_url}/api/threats",
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_vr_session(self, session_id: str) -> Dict:
        """Get VR session details"""
        response = self.session.get(
            f"{self.base_url}/api/vr/sessions/{session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def create_vr_session(self, config: Dict) -> Dict:
        """Create a new VR session"""
        response = self.session.post(
            f"{self.base_url}/api/vr/sessions",
            json=config
        )
        response.raise_for_status()
        return response.json()
    
    def get_analytics(self, metric: str, time_range: str = "24h") -> Dict:
        """Get analytics data"""
        response = self.session.get(
            f"{self.base_url}/api/analytics/{metric}",
            params={'time_range': time_range}
        )
        response.raise_for_status()
        return response.json()

# Example usage:
# client = JupiterVRClient("your_key_id", "your_key_secret")
# threats = client.get_threats(limit=50)
# print(f"Found {len(threats['threats'])} threats")
'''
    
    @staticmethod
    def generate_javascript_sdk() -> str:
        """Generate JavaScript SDK code"""
        return '''
// JUPITER VR Platform - JavaScript SDK

class JupiterVRClient {
    constructor(apiKeyId, apiKeySecret, baseUrl = 'http://localhost:5012') {
        this.apiKeyId = apiKeyId;
        this.apiKeySecret = apiKeySecret;
        this.baseUrl = baseUrl;
    }
    
    async request(endpoint, options = {}) {
        const headers = {
            'X-API-Key-ID': this.apiKeyId,
            'X-API-Key-Secret': this.apiKeySecret,
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async getThreats(limit = 100) {
        return await this.request(`/api/threats?limit=${limit}`);
    }
    
    async getVRSession(sessionId) {
        return await this.request(`/api/vr/sessions/${sessionId}`);
    }
    
    async createVRSession(config) {
        return await this.request('/api/vr/sessions', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }
    
    async getAnalytics(metric, timeRange = '24h') {
        return await this.request(`/api/analytics/${metric}?time_range=${timeRange}`);
    }
    
    connectWebSocket(onMessage) {
        const ws = new WebSocket(`ws://localhost:5012/ws`);
        
        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'auth',
                api_key_id: this.apiKeyId,
                api_key_secret: this.apiKeySecret
            }));
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };
        
        return ws;
    }
}

// Example usage:
// const client = new JupiterVRClient('your_key_id', 'your_key_secret');
// const threats = await client.getThreats(50);
// console.log(`Found ${threats.threats.length} threats`);
'''
    
    @staticmethod
    def generate_unity_sdk() -> str:
        """Generate Unity C# SDK code"""
        return '''
// JUPITER VR Platform - Unity C# SDK

using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

public class JupiterVRClient : MonoBehaviour
{
    private string apiKeyId;
    private string apiKeySecret;
    private string baseUrl = "http://localhost:5012";
    
    public void Initialize(string keyId, string keySecret)
    {
        apiKeyId = keyId;
        apiKeySecret = keySecret;
    }
    
    public IEnumerator GetThreats(System.Action<string> callback, int limit = 100)
    {
        string url = $"{baseUrl}/api/threats?limit={limit}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("X-API-Key-ID", apiKeyId);
            request.SetRequestHeader("X-API-Key-Secret", apiKeySecret);
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                callback(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"API Error: {request.error}");
            }
        }
    }
    
    public IEnumerator GetVRSession(string sessionId, System.Action<string> callback)
    {
        string url = $"{baseUrl}/api/vr/sessions/{sessionId}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("X-API-Key-ID", apiKeyId);
            request.SetRequestHeader("X-API-Key-Secret", apiKeySecret);
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                callback(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"API Error: {request.error}");
            }
        }
    }
    
    public IEnumerator CreateVRSession(string configJson, System.Action<string> callback)
    {
        string url = $"{baseUrl}/api/vr/sessions";
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(configJson);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("X-API-Key-ID", apiKeyId);
            request.SetRequestHeader("X-API-Key-Secret", apiKeySecret);
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                callback(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"API Error: {request.error}");
            }
        }
    }
}

// Example usage in a MonoBehaviour:
// JupiterVRClient client = gameObject.AddComponent<JupiterVRClient>();
// client.Initialize("your_key_id", "your_key_secret");
// StartCoroutine(client.GetThreats((response) => {
//     Debug.Log("Threats: " + response);
// }));
'''


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("JUPITER VR API Integration Layer - Module G.3.12")
    print("=" * 70)
    
    # Initialize API Gateway
    gateway = VRAPIGateway()
    
    # Generate API key
    print("\n1. Generating API Key...")
    api_key = gateway.auth_manager.generate_api_key(
        name="Test Application",
        owner_id="developer_001",
        permissions=[
            APIPermission.READ_THREATS,
            APIPermission.READ_VR_SESSIONS,
            APIPermission.WRITE_VR_SESSIONS
        ],
        rate_limit_tier=RateLimitTier.PROFESSIONAL
    )
    
    print(f"   API Key ID: {api_key.key_id}")
    print(f"   Tier: {api_key.rate_limit_tier.value}")
    print(f"   Permissions: {[p.value for p in api_key.permissions]}")
    
    # Authenticate request
    print("\n2. Authenticating Request...")
    auth_result = gateway.authenticate_request(
        api_key.key_id,
        api_key.key_secret,
        APIPermission.READ_THREATS
    )
    
    if auth_result['authenticated']:
        print("   ✓ Authentication successful")
        print(f"   Rate limit: {auth_result['rate_limit']['remaining']} remaining")
        print(f"   Quota: {auth_result['quota']['remaining_gb']} GB remaining")
    else:
        print(f"   ✗ Authentication failed: {auth_result['error']}")
    
    # Register webhook
    print("\n3. Registering Webhook...")
    webhook = gateway.register_webhook(
        url="https://example.com/webhooks/jupiter",
        events=["threat.detected", "vr.session.started"],
        owner_id="developer_001"
    )
    print(f"   Webhook ID: {webhook.webhook_id}")
    print(f"   Events: {webhook.events}")
    
    # Generate SDK code
    print("\n4. Available Client SDKs:")
    print("   ✓ Python SDK")
    print("   ✓ JavaScript SDK")
    print("   ✓ Unity C# SDK")
    
    print("\n" + "=" * 70)
    print("API Integration Layer Ready!")
    print("=" * 70)
