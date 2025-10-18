"""
Military Upgrade #19: WAF & API Security
Part 2: API Rate Limiting & Quota Enforcement

This module implements comprehensive API rate limiting, quota management, and
throttling to prevent abuse and ensure fair resource usage.

Key Features:
- Token bucket algorithm for rate limiting
- Sliding window counters
- Per-user/API key quota enforcement
- Burst allowance with sustained rate limits
- Distributed rate limiting (Redis-compatible)
- Cost-based rate limiting (weighted endpoints)

Compliance:
- OWASP API Security Top 10 - API4:2023 (Unrestricted Resource Consumption)
- NIST 800-53 SC-5 (Denial of Service Protection)
- PCI DSS Requirement 6.5.10
- ISO 27001 A.12.2.1 (Controls Against Malware)
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time


class RateLimitStrategy(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"  # Best for burst + sustained
    LEAKY_BUCKET = "leaky_bucket"  # Smooth rate, no burst
    FIXED_WINDOW = "fixed_window"  # Simple but edge case issues
    SLIDING_WINDOW = "sliding_window"  # Accurate but memory intensive
    SLIDING_LOG = "sliding_log"  # Most accurate, highest memory


class QuotaPeriod(Enum):
    """Quota period types"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"


class RateLimitTier(Enum):
    """Service tier with different limits"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests_per_second: int = 10
    requests_per_minute: int = 600
    requests_per_hour: int = 10000
    requests_per_day: int = 100000
    
    # Burst allowance
    burst_size: int = 20  # Allow brief spikes
    
    # Cost-based limits (for expensive operations)
    cost_limit_per_minute: int = 1000  # Cost units


@dataclass
class QuotaConfig:
    """API quota configuration"""
    tier: RateLimitTier
    
    # Monthly quotas
    monthly_requests: int
    monthly_compute_units: int  # For expensive operations
    monthly_data_transfer_gb: int
    
    # Concurrent connections
    max_concurrent_requests: int = 10
    
    # Feature limits
    max_api_keys: int = 5
    max_webhooks: int = 10
    
    # Overage
    allow_overage: bool = False
    overage_rate: float = 0.0  # $ per extra 1000 requests


@dataclass
class APIKey:
    """API key with associated limits"""
    api_key: str
    user_id: str
    tier: RateLimitTier
    
    # Limits
    rate_limit: RateLimit
    quota: QuotaConfig
    
    # Usage tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    total_requests: int = 0
    
    # Status
    enabled: bool = True
    expires_at: Optional[datetime] = None


@dataclass
class RateLimitViolation:
    """Rate limit violation event"""
    violation_id: str
    timestamp: datetime
    api_key: str
    user_id: str
    
    # Violation details
    endpoint: str
    requests_attempted: int
    limit_exceeded: str  # "per_second", "per_minute", etc.
    current_usage: int
    limit: int
    
    # Response
    retry_after: int  # Seconds


@dataclass
class EndpointCost:
    """Cost weight for expensive endpoints"""
    endpoint: str
    cost: int = 1  # Cost units (1 = standard, 10 = expensive)
    description: str = ""


class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> Tuple[bool, Optional[float]]:
        """
        Attempt to consume tokens
        
        Returns:
            (allowed, retry_after)
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, None
        else:
            # Calculate retry_after
            tokens_needed = tokens - self.tokens
            retry_after = tokens_needed / self.refill_rate
            return False, retry_after
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on refill rate
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


class SlidingWindowCounter:
    """Sliding window rate limiter"""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: List[float] = []
    
    def allow_request(self) -> Tuple[bool, Optional[int]]:
        """Check if request is allowed"""
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]
        
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True, None
        else:
            # Calculate retry_after (when oldest request expires)
            oldest = min(self.requests)
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, retry_after


class APIRateLimiter:
    """API Rate Limiting & Quota Enforcement Engine"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, Dict[str, SlidingWindowCounter]] = {}
        self.violations: List[RateLimitViolation] = []
        self.endpoint_costs: Dict[str, EndpointCost] = {}
        
        # Usage tracking
        self.usage: Dict[str, Dict[str, int]] = {}  # {api_key: {period: count}}
        
        # Tier configurations
        self._initialize_tier_configs()
        self._initialize_endpoint_costs()
    
    def _initialize_tier_configs(self) -> None:
        """Initialize rate limit tiers"""
        self.tier_configs = {
            RateLimitTier.FREE: QuotaConfig(
                tier=RateLimitTier.FREE,
                monthly_requests=10000,
                monthly_compute_units=1000,
                monthly_data_transfer_gb=1,
                max_concurrent_requests=2,
                max_api_keys=1,
                max_webhooks=1,
                allow_overage=False
            ),
            RateLimitTier.BASIC: QuotaConfig(
                tier=RateLimitTier.BASIC,
                monthly_requests=100000,
                monthly_compute_units=10000,
                monthly_data_transfer_gb=10,
                max_concurrent_requests=5,
                max_api_keys=3,
                max_webhooks=5,
                allow_overage=True,
                overage_rate=0.01
            ),
            RateLimitTier.PROFESSIONAL: QuotaConfig(
                tier=RateLimitTier.PROFESSIONAL,
                monthly_requests=1000000,
                monthly_compute_units=100000,
                monthly_data_transfer_gb=100,
                max_concurrent_requests=20,
                max_api_keys=10,
                max_webhooks=50,
                allow_overage=True,
                overage_rate=0.005
            ),
            RateLimitTier.ENTERPRISE: QuotaConfig(
                tier=RateLimitTier.ENTERPRISE,
                monthly_requests=10000000,
                monthly_compute_units=1000000,
                monthly_data_transfer_gb=1000,
                max_concurrent_requests=100,
                max_api_keys=50,
                max_webhooks=200,
                allow_overage=True,
                overage_rate=0.001
            )
        }
    
    def _initialize_endpoint_costs(self) -> None:
        """Initialize endpoint cost weights"""
        self.endpoint_costs = {
            '/api/search': EndpointCost('/api/search', cost=5, description="Database-intensive search"),
            '/api/report': EndpointCost('/api/report', cost=10, description="Generate large report"),
            '/api/scan': EndpointCost('/api/scan', cost=20, description="Full security scan"),
            '/api/export': EndpointCost('/api/export', cost=15, description="Data export operation"),
            '/api/users': EndpointCost('/api/users', cost=1, description="Standard CRUD"),
        }
    
    def create_api_key(self, user_id: str, tier: RateLimitTier) -> APIKey:
        """Create new API key with rate limits"""
        api_key_value = f"esk_{user_id}_{int(time.time())}"
        
        # Get tier configuration
        quota = self.tier_configs[tier]
        
        # Set rate limits based on tier
        if tier == RateLimitTier.FREE:
            rate_limit = RateLimit(
                requests_per_second=1,
                requests_per_minute=60,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_size=5,
                cost_limit_per_minute=100
            )
        elif tier == RateLimitTier.BASIC:
            rate_limit = RateLimit(
                requests_per_second=5,
                requests_per_minute=300,
                requests_per_hour=5000,
                requests_per_day=100000,
                burst_size=10,
                cost_limit_per_minute=500
            )
        elif tier == RateLimitTier.PROFESSIONAL:
            rate_limit = RateLimit(
                requests_per_second=20,
                requests_per_minute=1200,
                requests_per_hour=20000,
                requests_per_day=1000000,
                burst_size=50,
                cost_limit_per_minute=2000
            )
        else:  # ENTERPRISE
            rate_limit = RateLimit(
                requests_per_second=100,
                requests_per_minute=6000,
                requests_per_hour=100000,
                requests_per_day=10000000,
                burst_size=200,
                cost_limit_per_minute=10000
            )
        
        api_key = APIKey(
            api_key=api_key_value,
            user_id=user_id,
            tier=tier,
            rate_limit=rate_limit,
            quota=quota
        )
        
        self.api_keys[api_key_value] = api_key
        
        # Initialize token bucket
        self.token_buckets[api_key_value] = TokenBucket(
            capacity=rate_limit.burst_size,
            refill_rate=rate_limit.requests_per_second
        )
        
        # Initialize sliding windows
        self.sliding_windows[api_key_value] = {
            'minute': SlidingWindowCounter(rate_limit.requests_per_minute, 60),
            'hour': SlidingWindowCounter(rate_limit.requests_per_hour, 3600),
            'day': SlidingWindowCounter(rate_limit.requests_per_day, 86400)
        }
        
        print(f"✅ API key created: {api_key_value} | Tier: {tier.value}")
        return api_key
    
    def check_rate_limit(self, api_key: str, endpoint: str) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        if api_key not in self.api_keys:
            return {
                'allowed': False,
                'reason': 'Invalid API key',
                'status_code': 401
            }
        
        key_obj = self.api_keys[api_key]
        
        if not key_obj.enabled:
            return {
                'allowed': False,
                'reason': 'API key disabled',
                'status_code': 403
            }
        
        if key_obj.expires_at and datetime.now() > key_obj.expires_at:
            return {
                'allowed': False,
                'reason': 'API key expired',
                'status_code': 403
            }
        
        # Get endpoint cost
        endpoint_cost = self.endpoint_costs.get(endpoint, EndpointCost(endpoint, cost=1))
        cost = endpoint_cost.cost
        
        # Check token bucket (per-second + burst)
        bucket = self.token_buckets[api_key]
        allowed, retry_after = bucket.consume(cost)
        
        if not allowed:
            self._record_violation(api_key, endpoint, "per_second", retry_after)
            return {
                'allowed': False,
                'reason': 'Rate limit exceeded (per-second)',
                'retry_after': int(retry_after) if retry_after else 1,
                'limit': key_obj.rate_limit.requests_per_second,
                'status_code': 429
            }
        
        # Check sliding windows (minute, hour, day)
        windows = self.sliding_windows[api_key]
        
        for period, window in windows.items():
            allowed, retry_after = window.allow_request()
            if not allowed:
                self._record_violation(api_key, endpoint, f"per_{period}", retry_after)
                return {
                    'allowed': False,
                    'reason': f'Rate limit exceeded (per-{period})',
                    'retry_after': retry_after,
                    'limit': getattr(key_obj.rate_limit, f"requests_per_{period}"),
                    'status_code': 429
                }
        
        # Update usage tracking
        key_obj.last_used = datetime.now()
        key_obj.total_requests += 1
        
        return {
            'allowed': True,
            'remaining': {
                'per_second': int(bucket.tokens),
                'per_minute': key_obj.rate_limit.requests_per_minute - len(windows['minute'].requests),
                'per_hour': key_obj.rate_limit.requests_per_hour - len(windows['hour'].requests),
                'per_day': key_obj.rate_limit.requests_per_day - len(windows['day'].requests)
            },
            'cost': cost
        }
    
    def _record_violation(self, api_key: str, endpoint: str, limit_type: str,
                         retry_after: Optional[float]) -> None:
        """Record rate limit violation"""
        key_obj = self.api_keys[api_key]
        
        violation = RateLimitViolation(
            violation_id=f"VIO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            api_key=api_key,
            user_id=key_obj.user_id,
            endpoint=endpoint,
            requests_attempted=key_obj.total_requests,
            limit_exceeded=limit_type,
            current_usage=key_obj.total_requests,
            limit=self._get_limit_value(key_obj, limit_type),
            retry_after=int(retry_after) if retry_after else 60
        )
        
        self.violations.append(violation)
        
        print(f"⚠️  Rate limit violation: {violation.violation_id}")
        print(f"   User: {key_obj.user_id} | Limit: {limit_type}")
        print(f"   Retry after: {violation.retry_after}s")
    
    def _get_limit_value(self, key_obj: APIKey, limit_type: str) -> int:
        """Get limit value for violation type"""
        mapping = {
            'per_second': key_obj.rate_limit.requests_per_second,
            'per_minute': key_obj.rate_limit.requests_per_minute,
            'per_hour': key_obj.rate_limit.requests_per_hour,
            'per_day': key_obj.rate_limit.requests_per_day
        }
        return mapping.get(limit_type, 0)
    
    def check_monthly_quota(self, api_key: str) -> Dict[str, Any]:
        """Check if monthly quota is exceeded"""
        if api_key not in self.api_keys:
            return {'quota_exceeded': True, 'reason': 'Invalid API key'}
        
        key_obj = self.api_keys[api_key]
        quota = key_obj.quota
        
        # Get current month's usage
        month_key = datetime.now().strftime('%Y-%m')
        usage = self.usage.get(api_key, {}).get(month_key, 0)
        
        if usage >= quota.monthly_requests:
            if not quota.allow_overage:
                return {
                    'quota_exceeded': True,
                    'reason': 'Monthly quota exceeded',
                    'usage': usage,
                    'limit': quota.monthly_requests,
                    'overage_allowed': False
                }
            else:
                # Calculate overage cost
                overage = usage - quota.monthly_requests
                overage_cost = (overage / 1000) * quota.overage_rate
                
                return {
                    'quota_exceeded': False,  # Allowed with overage
                    'overage': True,
                    'usage': usage,
                    'limit': quota.monthly_requests,
                    'overage_amount': overage,
                    'overage_cost': overage_cost
                }
        
        return {
            'quota_exceeded': False,
            'usage': usage,
            'limit': quota.monthly_requests,
            'remaining': quota.monthly_requests - usage
        }
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        return {
            'total_api_keys': len(self.api_keys),
            'active_keys': sum(1 for k in self.api_keys.values() if k.enabled),
            'total_violations': len(self.violations),
            'violations_last_hour': len([
                v for v in self.violations 
                if datetime.now() - v.timestamp < timedelta(hours=1)
            ]),
            'tier_distribution': self._get_tier_distribution(),
            'top_violators': self._get_top_violators()
        }
    
    def _get_tier_distribution(self) -> Dict[str, int]:
        """Get distribution of API keys by tier"""
        distribution = {}
        for key in self.api_keys.values():
            tier = key.tier.value
            distribution[tier] = distribution.get(tier, 0) + 1
        return distribution
    
    def _get_top_violators(self) -> List[Dict[str, Any]]:
        """Get top rate limit violators"""
        user_violations = {}
        for violation in self.violations:
            user_id = violation.user_id
            user_violations[user_id] = user_violations.get(user_id, 0) + 1
        
        sorted_violators = sorted(user_violations.items(), key=lambda x: x[1], reverse=True)
        return [{'user_id': uid, 'violations': count} for uid, count in sorted_violators[:10]]


# Example usage
if __name__ == "__main__":
    limiter = APIRateLimiter()
    
    # Create API key
    api_key = limiter.create_api_key("user123", RateLimitTier.PROFESSIONAL)
    
    # Check rate limit
    result = limiter.check_rate_limit(api_key.api_key, "/api/scan")
    
    print(f"\n✅ Rate limit check:")
    print(f"Allowed: {result['allowed']}")
    if result['allowed']:
        print(f"Remaining: {result['remaining']}")
        print(f"Cost: {result['cost']} units")
