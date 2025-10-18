"""
Module 2: Access Control - Security & Permissions

Role-based access control system that enforces:
- Access level permissions (Public, Sales, Customer, Developer, Admin, Military)
- Rate limiting per user/access level
- Feature gating based on access level
- Audit logging of all access attempts
- Security monitoring and alerting

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict


class AccessLevel(Enum):
    """User access levels with increasing privileges"""
    PUBLIC = "public"              # Website visitors, rate limited
    SALES = "sales"                # Sales team, competitive intel
    CUSTOMER = "customer"          # Paying customers, full scan access
    DEVELOPER = "developer"        # Dev team, code access
    ADMIN = "admin"                # System administrators, full control
    MILITARY = "military"          # Advanced ops, autonomous features


@dataclass
class RateLimitConfig:
    """Rate limiting configuration per access level"""
    queries_per_day: int
    queries_per_hour: int
    queries_per_minute: int
    burst_allowance: int = 5  # Allow short bursts


@dataclass
class AccessRecord:
    """Record of user access attempt"""
    timestamp: datetime
    user_id: str
    access_level: str
    feature: str
    granted: bool
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class AccessControl:
    """
    Role-Based Access Control (RBAC) system
    
    Enforces permissions, rate limits, and logs all access
    """
    
    # Rate limit configurations per access level
    RATE_LIMITS = {
        AccessLevel.PUBLIC: RateLimitConfig(
            queries_per_day=10,
            queries_per_hour=5,
            queries_per_minute=1,
            burst_allowance=2
        ),
        AccessLevel.SALES: RateLimitConfig(
            queries_per_day=100,
            queries_per_hour=50,
            queries_per_minute=5,
            burst_allowance=10
        ),
        AccessLevel.CUSTOMER: RateLimitConfig(
            queries_per_day=1000,
            queries_per_hour=200,
            queries_per_minute=10,
            burst_allowance=20
        ),
        AccessLevel.DEVELOPER: RateLimitConfig(
            queries_per_day=500,
            queries_per_hour=100,
            queries_per_minute=10,
            burst_allowance=15
        ),
        AccessLevel.ADMIN: RateLimitConfig(
            queries_per_day=2000,
            queries_per_hour=500,
            queries_per_minute=20,
            burst_allowance=30
        ),
        AccessLevel.MILITARY: RateLimitConfig(
            queries_per_day=999999,  # Effectively unlimited
            queries_per_hour=999999,
            queries_per_minute=100,
            burst_allowance=50
        )
    }
    
    # Feature permissions matrix
    FEATURE_PERMISSIONS = {
        'general_questions': [
            AccessLevel.PUBLIC, AccessLevel.SALES, AccessLevel.CUSTOMER,
            AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'product_info': [
            AccessLevel.PUBLIC, AccessLevel.SALES, AccessLevel.CUSTOMER,
            AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'pricing_info': [
            AccessLevel.PUBLIC, AccessLevel.SALES, AccessLevel.CUSTOMER,
            AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        
        # Sales-specific features
        'competitive_intelligence': [
            AccessLevel.SALES, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'proposal_generation': [
            AccessLevel.SALES, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'customer_analysis': [
            AccessLevel.SALES, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        
        # Customer features
        'scan_analysis': [
            AccessLevel.CUSTOMER, AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'vulnerability_explanation': [
            AccessLevel.CUSTOMER, AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'threat_intelligence': [
            AccessLevel.CUSTOMER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'remediation_guidance': [
            AccessLevel.CUSTOMER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'report_generation': [
            AccessLevel.CUSTOMER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'compliance_check': [
            AccessLevel.CUSTOMER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        
        # Developer features
        'code_generation': [
            AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'api_access': [
            AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'debugging_assistance': [
            AccessLevel.DEVELOPER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        
        # Admin features
        'system_status': [
            AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'user_management': [
            AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'configuration': [
            AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'security_audit': [
            AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        'performance_monitoring': [
            AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        
        # Military features
        'autonomous_response': [AccessLevel.MILITARY],
        'predictive_intelligence': [AccessLevel.MILITARY],
        'red_team_automation': [AccessLevel.MILITARY],
        'voice_commands': [AccessLevel.MILITARY],
        'emergency_calls': [AccessLevel.MILITARY],
        'zero_day_research': [AccessLevel.MILITARY],
        
        # Voice features (Customer+)
        'voice_interface': [
            AccessLevel.CUSTOMER, AccessLevel.ADMIN, AccessLevel.MILITARY
        ],
        
        # Phone alerts (Admin+)
        'phone_alerts': [
            AccessLevel.ADMIN, AccessLevel.MILITARY
        ]
    }
    
    def __init__(self, storage_backend: str = "memory"):
        """
        Initialize Access Control system
        
        Args:
            storage_backend: 'memory' or 'redis' for distributed systems
        """
        self.logger = logging.getLogger(__name__)
        self.storage_backend = storage_backend
        
        # In-memory rate limit tracking
        # Structure: {user_id: {timeframe: [timestamps]}}
        self.rate_limit_tracker: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        
        # User access levels (in production, would query database)
        self.user_access_levels: Dict[str, AccessLevel] = {}
        
        # Access log (in production, would write to database)
        self.access_log: List[AccessRecord] = []
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'granted': 0,
            'denied': 0,
            'rate_limited': 0,
            'by_access_level': defaultdict(int),
            'by_feature': defaultdict(int)
        }
        
        self.logger.info("AccessControl initialized")
    
    def verify_access(
        self,
        user_id: str,
        feature: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Verify if user has access to requested feature
        
        Args:
            user_id: User identifier
            feature: Feature being accessed
            ip_address: User's IP (optional, for logging)
            
        Returns:
            True if access granted, False otherwise
        """
        self.stats['total_requests'] += 1
        self.stats['by_feature'][feature] += 1
        
        # Get user's access level
        access_level = self.get_access_level(user_id)
        self.stats['by_access_level'][access_level.value] += 1
        
        # Check if feature exists
        if feature not in self.FEATURE_PERMISSIONS:
            self._log_access(
                user_id, access_level.value, feature, False,
                f"Unknown feature: {feature}", ip_address
            )
            self.stats['denied'] += 1
            return False
        
        # Check if access level has permission
        allowed_levels = self.FEATURE_PERMISSIONS[feature]
        
        if access_level not in allowed_levels:
            self._log_access(
                user_id, access_level.value, feature, False,
                f"Insufficient access level: {access_level.value}", ip_address
            )
            self.stats['denied'] += 1
            self.logger.warning(
                f"Access denied: user={user_id}, level={access_level.value}, "
                f"feature={feature}"
            )
            return False
        
        # Access granted
        self._log_access(
            user_id, access_level.value, feature, True,
            "Access granted", ip_address
        )
        self.stats['granted'] += 1
        
        return True
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limits
        
        Uses token bucket algorithm for rate limiting
        
        Args:
            user_id: User identifier
            
        Returns:
            True if within limits, False if exceeded
        """
        access_level = self.get_access_level(user_id)
        config = self.RATE_LIMITS[access_level]
        
        current_time = time.time()
        
        # Clean old timestamps
        self._clean_old_timestamps(user_id, current_time)
        
        # Check per-minute limit
        minute_timestamps = self.rate_limit_tracker[user_id]['minute']
        if len(minute_timestamps) >= config.queries_per_minute:
            self.logger.warning(
                f"Rate limit exceeded (per-minute): user={user_id}, "
                f"level={access_level.value}"
            )
            self.stats['rate_limited'] += 1
            return False
        
        # Check per-hour limit
        hour_timestamps = self.rate_limit_tracker[user_id]['hour']
        if len(hour_timestamps) >= config.queries_per_hour:
            self.logger.warning(
                f"Rate limit exceeded (per-hour): user={user_id}, "
                f"level={access_level.value}"
            )
            self.stats['rate_limited'] += 1
            return False
        
        # Check per-day limit
        day_timestamps = self.rate_limit_tracker[user_id]['day']
        if len(day_timestamps) >= config.queries_per_day:
            self.logger.warning(
                f"Rate limit exceeded (per-day): user={user_id}, "
                f"level={access_level.value}"
            )
            self.stats['rate_limited'] += 1
            return False
        
        # Add timestamp to tracking
        self.rate_limit_tracker[user_id]['minute'].append(current_time)
        self.rate_limit_tracker[user_id]['hour'].append(current_time)
        self.rate_limit_tracker[user_id]['day'].append(current_time)
        
        return True
    
    def _clean_old_timestamps(self, user_id: str, current_time: float):
        """Remove timestamps outside rate limit windows"""
        # Clean minute window (60 seconds)
        self.rate_limit_tracker[user_id]['minute'] = [
            ts for ts in self.rate_limit_tracker[user_id]['minute']
            if current_time - ts < 60
        ]
        
        # Clean hour window (3600 seconds)
        self.rate_limit_tracker[user_id]['hour'] = [
            ts for ts in self.rate_limit_tracker[user_id]['hour']
            if current_time - ts < 3600
        ]
        
        # Clean day window (86400 seconds)
        self.rate_limit_tracker[user_id]['day'] = [
            ts for ts in self.rate_limit_tracker[user_id]['day']
            if current_time - ts < 86400
        ]
    
    def get_access_level(self, user_id: str) -> AccessLevel:
        """
        Get user's access level
        
        In production, would query user database
        
        Args:
            user_id: User identifier
            
        Returns:
            AccessLevel enum
        """
        # Check cache
        if user_id in self.user_access_levels:
            return self.user_access_levels[user_id]
        
        # Default to customer level (in production, query database)
        # For demo purposes, derive from user_id pattern
        if 'public' in user_id.lower() or 'guest' in user_id.lower():
            level = AccessLevel.PUBLIC
        elif 'sales' in user_id.lower():
            level = AccessLevel.SALES
        elif 'dev' in user_id.lower():
            level = AccessLevel.DEVELOPER
        elif 'admin' in user_id.lower():
            level = AccessLevel.ADMIN
        elif 'military' in user_id.lower() or 'mil' in user_id.lower():
            level = AccessLevel.MILITARY
        else:
            level = AccessLevel.CUSTOMER
        
        # Cache it
        self.user_access_levels[user_id] = level
        
        return level
    
    def set_access_level(self, user_id: str, access_level: AccessLevel):
        """
        Set user's access level (admin function)
        
        Args:
            user_id: User identifier
            access_level: New access level
        """
        self.user_access_levels[user_id] = access_level
        self.logger.info(f"Access level set: user={user_id}, level={access_level.value}")
    
    def get_permitted_features(self, access_level: AccessLevel) -> List[str]:
        """
        Get list of features permitted for access level
        
        Args:
            access_level: Access level to check
            
        Returns:
            List of feature names
        """
        permitted = []
        
        for feature, allowed_levels in self.FEATURE_PERMISSIONS.items():
            if access_level in allowed_levels:
                permitted.append(feature)
        
        return sorted(permitted)
    
    def get_rate_limit_status(self, user_id: str) -> Dict[str, any]:
        """
        Get current rate limit status for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with current usage and limits
        """
        access_level = self.get_access_level(user_id)
        config = self.RATE_LIMITS[access_level]
        
        current_time = time.time()
        self._clean_old_timestamps(user_id, current_time)
        
        return {
            'access_level': access_level.value,
            'limits': {
                'per_minute': config.queries_per_minute,
                'per_hour': config.queries_per_hour,
                'per_day': config.queries_per_day
            },
            'current_usage': {
                'per_minute': len(self.rate_limit_tracker[user_id]['minute']),
                'per_hour': len(self.rate_limit_tracker[user_id]['hour']),
                'per_day': len(self.rate_limit_tracker[user_id]['day'])
            },
            'remaining': {
                'per_minute': config.queries_per_minute - len(self.rate_limit_tracker[user_id]['minute']),
                'per_hour': config.queries_per_hour - len(self.rate_limit_tracker[user_id]['hour']),
                'per_day': config.queries_per_day - len(self.rate_limit_tracker[user_id]['day'])
            }
        }
    
    def _log_access(
        self,
        user_id: str,
        access_level: str,
        feature: str,
        granted: bool,
        reason: str,
        ip_address: Optional[str] = None
    ):
        """Log access attempt for audit trail"""
        record = AccessRecord(
            timestamp=datetime.now(),
            user_id=user_id,
            access_level=access_level,
            feature=feature,
            granted=granted,
            reason=reason,
            ip_address=ip_address
        )
        
        self.access_log.append(record)
        
        # In production, would write to database
        # For now, keep last 10000 records in memory
        if len(self.access_log) > 10000:
            self.access_log = self.access_log[-10000:]
    
    def get_access_log(
        self,
        user_id: Optional[str] = None,
        feature: Optional[str] = None,
        granted: Optional[bool] = None,
        limit: int = 100
    ) -> List[AccessRecord]:
        """
        Query access log with filters
        
        Args:
            user_id: Filter by user (optional)
            feature: Filter by feature (optional)
            granted: Filter by granted status (optional)
            limit: Max records to return
            
        Returns:
            List of AccessRecord objects
        """
        filtered = self.access_log
        
        if user_id:
            filtered = [r for r in filtered if r.user_id == user_id]
        
        if feature:
            filtered = [r for r in filtered if r.feature == feature]
        
        if granted is not None:
            filtered = [r for r in filtered if r.granted == granted]
        
        # Return most recent first
        return sorted(filtered, key=lambda r: r.timestamp, reverse=True)[:limit]
    
    def get_stats(self) -> Dict[str, any]:
        """Get access control statistics"""
        return {
            'total_requests': self.stats['total_requests'],
            'granted': self.stats['granted'],
            'denied': self.stats['denied'],
            'rate_limited': self.stats['rate_limited'],
            'grant_rate': (
                self.stats['granted'] / self.stats['total_requests']
                if self.stats['total_requests'] > 0 else 0
            ),
            'by_access_level': dict(self.stats['by_access_level']),
            'by_feature': dict(self.stats['by_feature'])
        }
    
    def reset_rate_limits(self, user_id: str):
        """Reset rate limits for user (admin function)"""
        if user_id in self.rate_limit_tracker:
            del self.rate_limit_tracker[user_id]
            self.logger.info(f"Rate limits reset for user: {user_id}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("ACCESS CONTROL - MODULE 2")
    print("="*70)
    
    # Initialize
    print("\n1. Initializing Access Control...")
    ac = AccessControl()
    
    # Test different access levels
    print("\n2. Testing Access Levels:")
    
    test_users = [
        ("public_user", AccessLevel.PUBLIC),
        ("sales_rep", AccessLevel.SALES),
        ("customer_john", AccessLevel.CUSTOMER),
        ("admin_sarah", AccessLevel.ADMIN),
        ("military_ops", AccessLevel.MILITARY)
    ]
    
    for user_id, expected_level in test_users:
        ac.set_access_level(user_id, expected_level)
        level = ac.get_access_level(user_id)
        features = ac.get_permitted_features(level)
        print(f"\n   {user_id} ({level.value}): {len(features)} features")
        print(f"   Sample features: {', '.join(features[:5])}")
    
    # Test feature access
    print("\n3. Testing Feature Access:")
    
    test_cases = [
        ("public_user", "general_questions", True),
        ("public_user", "scan_analysis", False),
        ("customer_john", "scan_analysis", True),
        ("customer_john", "autonomous_response", False),
        ("military_ops", "autonomous_response", True)
    ]
    
    for user, feature, expected in test_cases:
        result = ac.verify_access(user, feature)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {user} → {feature}: {'GRANTED' if result else 'DENIED'}")
    
    # Test rate limiting
    print("\n4. Testing Rate Limiting:")
    
    # Public user (10/day limit)
    print("\n   Public user (10 queries/day):")
    for i in range(12):
        within_limit = ac.check_rate_limit("public_user")
        if i < 10:
            assert within_limit, f"Should be within limit at query {i+1}"
        else:
            assert not within_limit, f"Should exceed limit at query {i+1}"
    
    status = ac.get_rate_limit_status("public_user")
    print(f"   Usage: {status['current_usage']['per_day']}/{status['limits']['per_day']}")
    print(f"   Remaining: {status['remaining']['per_day']}")
    
    # Military user (unlimited)
    print("\n   Military user (unlimited):")
    for i in range(50):
        assert ac.check_rate_limit("military_ops"), f"Military should never hit limit"
    
    status = ac.get_rate_limit_status("military_ops")
    print(f"   Usage: {status['current_usage']['per_minute']}")
    
    # Statistics
    print("\n5. Access Control Statistics:")
    stats = ac.get_stats()
    print(json.dumps(stats, indent=2))
    
    # Access log
    print("\n6. Recent Access Log (last 5):")
    log = ac.get_access_log(limit=5)
    for record in log:
        print(f"   {record.timestamp.strftime('%H:%M:%S')} - "
              f"{record.user_id} → {record.feature}: "
              f"{'✅ GRANTED' if record.granted else '❌ DENIED'}")
    
    print("\n" + "="*70)
    print("MODULE 2 COMPLETE ✅")
    print("="*70)
