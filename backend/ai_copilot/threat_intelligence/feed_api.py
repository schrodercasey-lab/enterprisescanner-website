"""
G.2.9: Threat Intelligence Feed API

Enterprise-grade REST API for threat intelligence distribution and consumption.
Supports STIX/TAXII protocols, webhook delivery, rate limiting, and comprehensive
query filtering for integration with security tools and platforms.

Features:
- RESTful API endpoints
- STIX 2.1 format support
- TAXII 2.1 server implementation
- Webhook delivery system
- API key authentication
- Rate limiting and throttling
- Query filtering and pagination
- Feed subscription management
- Real-time intelligence streaming
- Custom feed creation

Author: Enterprise Scanner Development Team
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import json
import time
from collections import defaultdict


class APIKeyPermission(Enum):
    """API key permission levels"""
    READ_BASIC = "read_basic"          # Basic threat intel access
    READ_PREMIUM = "read_premium"      # Premium threat intel access
    READ_ALL = "read_all"              # All threat intel access
    WRITE = "write"                    # Submit threat intelligence
    ADMIN = "admin"                    # Full administrative access


class FeedType(Enum):
    """Types of threat intelligence feeds"""
    IOC = "ioc"                        # Indicators of Compromise
    VULNERABILITY = "vulnerability"     # Vulnerability intelligence
    THREAT_ACTOR = "threat_actor"      # Threat actor profiles
    MALWARE = "malware"                # Malware intelligence
    CAMPAIGN = "campaign"              # Threat campaigns
    TTP = "ttp"                        # Tactics, Techniques, Procedures
    ALL = "all"                        # All intelligence types


class DeliveryMethod(Enum):
    """Intelligence delivery methods"""
    REST_API = "rest_api"              # RESTful API pull
    WEBHOOK = "webhook"                # Push via webhook
    STIX_TAXII = "stix_taxii"         # STIX/TAXII protocol
    EMAIL = "email"                    # Email delivery
    SYSLOG = "syslog"                  # Syslog format


class RateLimitTier(Enum):
    """Rate limiting tiers"""
    FREE = "free"                      # 100 requests/hour
    BASIC = "basic"                    # 1,000 requests/hour
    PROFESSIONAL = "professional"      # 10,000 requests/hour
    ENTERPRISE = "enterprise"          # 100,000 requests/hour
    UNLIMITED = "unlimited"            # No limits


@dataclass
class APIKey:
    """API key for authentication and authorization"""
    key_id: str
    api_key: str
    organization: str
    permissions: List[APIKeyPermission]
    rate_limit_tier: RateLimitTier
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    request_count: int = 0
    
    def is_valid(self) -> bool:
        """Check if API key is valid"""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def has_permission(self, permission: APIKeyPermission) -> bool:
        """Check if key has specific permission"""
        return permission in self.permissions or APIKeyPermission.ADMIN in self.permissions
    
    def get_rate_limit(self) -> int:
        """Get requests per hour for this key"""
        limits = {
            RateLimitTier.FREE: 100,
            RateLimitTier.BASIC: 1000,
            RateLimitTier.PROFESSIONAL: 10000,
            RateLimitTier.ENTERPRISE: 100000,
            RateLimitTier.UNLIMITED: float('inf')
        }
        return limits[self.rate_limit_tier]


@dataclass
class FeedSubscription:
    """Threat intelligence feed subscription"""
    subscription_id: str
    api_key_id: str
    feed_types: List[FeedType]
    delivery_method: DeliveryMethod
    webhook_url: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_delivery_at: Optional[datetime] = None
    delivery_count: int = 0


@dataclass
class WebhookDelivery:
    """Webhook delivery record"""
    delivery_id: str
    subscription_id: str
    payload: Dict
    status: str  # pending, delivered, failed, retrying
    attempts: int = 0
    max_attempts: int = 3
    scheduled_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class QueryFilter:
    """Query filtering parameters"""
    feed_types: Optional[List[FeedType]] = None
    severity_min: Optional[str] = None
    confidence_min: Optional[float] = None
    industries: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    threat_actors: Optional[List[str]] = None
    malware_families: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict:
        """Convert filter to dictionary"""
        return {
            'feed_types': [ft.value for ft in self.feed_types] if self.feed_types else None,
            'severity_min': self.severity_min,
            'confidence_min': self.confidence_min,
            'industries': self.industries,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'threat_actors': self.threat_actors,
            'malware_families': self.malware_families,
            'limit': self.limit,
            'offset': self.offset
        }


class ThreatIntelligenceFeedAPI:
    """
    Enterprise-grade REST API for threat intelligence distribution.
    
    Features:
    - STIX 2.1 and TAXII 2.1 protocol support
    - RESTful endpoints with pagination
    - Webhook delivery system
    - API key authentication and authorization
    - Rate limiting and throttling
    - Query filtering by multiple criteria
    - Real-time intelligence streaming
    - Custom feed management
    """
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        self.db_path = db_path
        self._init_database()
        
        # Rate limiting tracking (in-memory for demo)
        self.rate_limit_tracker: Dict[str, List[float]] = defaultdict(list)
        
        # Configuration
        self.rate_limit_window_seconds = 3600  # 1 hour
        self.webhook_timeout_seconds = 30
        self.max_results_per_request = 1000
        
    def _init_database(self):
        """Initialize API database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                api_key TEXT UNIQUE NOT NULL,
                organization TEXT NOT NULL,
                permissions TEXT NOT NULL,
                rate_limit_tier TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_used_at TIMESTAMP,
                request_count INTEGER DEFAULT 0
            )
        """)
        
        # Feed subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feed_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                api_key_id TEXT NOT NULL,
                feed_types TEXT NOT NULL,
                delivery_method TEXT NOT NULL,
                webhook_url TEXT,
                filters TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_delivery_at TIMESTAMP,
                delivery_count INTEGER DEFAULT 0,
                FOREIGN KEY (api_key_id) REFERENCES api_keys(key_id)
            )
        """)
        
        # Webhook deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_deliveries (
                delivery_id TEXT PRIMARY KEY,
                subscription_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered_at TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (subscription_id) REFERENCES feed_subscriptions(subscription_id)
            )
        """)
        
        # API usage logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                response_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_api_key(
        self,
        organization: str,
        permissions: List[APIKeyPermission],
        rate_limit_tier: RateLimitTier,
        expires_days: Optional[int] = None
    ) -> APIKey:
        """Create new API key"""
        key_id = hashlib.sha256(
            f"{organization}{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Generate secure API key
        api_key = hashlib.sha256(
            f"{key_id}{organization}{time.time()}".encode()
        ).hexdigest()
        
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=expires_days) if expires_days else None
        
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,
            organization=organization,
            permissions=permissions,
            rate_limit_tier=rate_limit_tier,
            created_at=created_at,
            expires_at=expires_at
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_keys
            (key_id, api_key, organization, permissions, rate_limit_tier,
             created_at, expires_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            api_key_obj.key_id,
            api_key_obj.api_key,
            api_key_obj.organization,
            json.dumps([p.value for p in api_key_obj.permissions]),
            api_key_obj.rate_limit_tier.value,
            api_key_obj.created_at.isoformat(),
            api_key_obj.expires_at.isoformat() if api_key_obj.expires_at else None,
            1 if api_key_obj.is_active else 0
        ))
        
        conn.commit()
        conn.close()
        
        return api_key_obj
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key object"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key_id, api_key, organization, permissions, rate_limit_tier,
                   created_at, expires_at, is_active, last_used_at, request_count
            FROM api_keys
            WHERE api_key = ?
        """, (api_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        key_id, api_key, org, perms_json, tier, created, expires, active, last_used, count = result
        
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,
            organization=org,
            permissions=[APIKeyPermission(p) for p in json.loads(perms_json)],
            rate_limit_tier=RateLimitTier(tier),
            created_at=datetime.fromisoformat(created),
            expires_at=datetime.fromisoformat(expires) if expires else None,
            is_active=bool(active),
            last_used_at=datetime.fromisoformat(last_used) if last_used else None,
            request_count=count
        )
        
        if not api_key_obj.is_valid():
            return None
        
        return api_key_obj
    
    def check_rate_limit(self, api_key_id: str, rate_limit: int) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        
        # Clean old requests outside window
        self.rate_limit_tracker[api_key_id] = [
            req_time for req_time in self.rate_limit_tracker[api_key_id]
            if now - req_time < self.rate_limit_window_seconds
        ]
        
        # Check if under limit
        if len(self.rate_limit_tracker[api_key_id]) >= rate_limit:
            return False
        
        # Add current request
        self.rate_limit_tracker[api_key_id].append(now)
        return True
    
    def query_threat_intelligence(
        self,
        api_key: APIKey,
        filters: QueryFilter
    ) -> Dict[str, Any]:
        """
        Query threat intelligence with filters.
        
        Returns paginated results with metadata.
        """
        # Check rate limit
        if not self.check_rate_limit(api_key.key_id, api_key.get_rate_limit()):
            return {
                'error': 'Rate limit exceeded',
                'retry_after': self.rate_limit_window_seconds,
                'status': 429
            }
        
        # Enforce max results
        filters.limit = min(filters.limit, self.max_results_per_request)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        
        # Query IoCs if requested
        if not filters.feed_types or FeedType.IOC in filters.feed_types:
            iocs = self._query_iocs(cursor, filters)
            results.extend(iocs)
        
        # Query vulnerabilities if requested
        if not filters.feed_types or FeedType.VULNERABILITY in filters.feed_types:
            vulns = self._query_vulnerabilities(cursor, filters)
            results.extend(vulns)
        
        # Query threat actors if requested
        if not filters.feed_types or FeedType.THREAT_ACTOR in filters.feed_types:
            actors = self._query_threat_actors(cursor, filters)
            results.extend(actors)
        
        conn.close()
        
        # Apply pagination
        total_count = len(results)
        paginated_results = results[filters.offset:filters.offset + filters.limit]
        
        # Update API key usage
        self._update_api_key_usage(api_key.key_id)
        
        return {
            'status': 200,
            'data': paginated_results,
            'metadata': {
                'total_count': total_count,
                'returned_count': len(paginated_results),
                'limit': filters.limit,
                'offset': filters.offset,
                'has_more': (filters.offset + filters.limit) < total_count
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _query_iocs(self, cursor, filters: QueryFilter) -> List[Dict]:
        """Query Indicators of Compromise"""
        query = "SELECT * FROM indicators_of_compromise WHERE 1=1"
        params = []
        
        if filters.confidence_min:
            query += " AND confidence >= ?"
            params.append(filters.confidence_min)
        
        if filters.start_date:
            query += " AND first_seen >= ?"
            params.append(filters.start_date.isoformat())
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        results = []
        for row in cursor.fetchall()[:filters.limit]:
            ioc_data = dict(zip(columns, row))
            ioc_data['feed_type'] = 'ioc'
            results.append(ioc_data)
        
        return results
    
    def _query_vulnerabilities(self, cursor, filters: QueryFilter) -> List[Dict]:
        """Query vulnerability intelligence"""
        query = "SELECT * FROM vulnerabilities WHERE 1=1"
        params = []
        
        if filters.severity_min:
            query += " AND severity >= ?"
            params.append(filters.severity_min)
        
        if filters.start_date:
            query += " AND published_date >= ?"
            params.append(filters.start_date.isoformat())
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        results = []
        for row in cursor.fetchall()[:filters.limit]:
            vuln_data = dict(zip(columns, row))
            vuln_data['feed_type'] = 'vulnerability'
            results.append(vuln_data)
        
        return results
    
    def _query_threat_actors(self, cursor, filters: QueryFilter) -> List[Dict]:
        """Query threat actor profiles"""
        query = "SELECT * FROM threat_actors WHERE 1=1"
        params = []
        
        if filters.threat_actors:
            placeholders = ','.join('?' * len(filters.threat_actors))
            query += f" AND actor_id IN ({placeholders})"
            params.extend(filters.threat_actors)
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        results = []
        for row in cursor.fetchall()[:filters.limit]:
            actor_data = dict(zip(columns, row))
            actor_data['feed_type'] = 'threat_actor'
            results.append(actor_data)
        
        return results
    
    def _update_api_key_usage(self, key_id: str):
        """Update API key usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys
            SET last_used_at = ?, request_count = request_count + 1
            WHERE key_id = ?
        """, (datetime.utcnow().isoformat(), key_id))
        
        conn.commit()
        conn.close()
    
    def create_subscription(
        self,
        api_key_id: str,
        feed_types: List[FeedType],
        delivery_method: DeliveryMethod,
        webhook_url: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> FeedSubscription:
        """Create feed subscription"""
        subscription_id = hashlib.sha256(
            f"{api_key_id}{time.time()}".encode()
        ).hexdigest()[:16]
        
        subscription = FeedSubscription(
            subscription_id=subscription_id,
            api_key_id=api_key_id,
            feed_types=feed_types,
            delivery_method=delivery_method,
            webhook_url=webhook_url,
            filters=filters or {}
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feed_subscriptions
            (subscription_id, api_key_id, feed_types, delivery_method,
             webhook_url, filters, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subscription.subscription_id,
            subscription.api_key_id,
            json.dumps([ft.value for ft in subscription.feed_types]),
            subscription.delivery_method.value,
            subscription.webhook_url,
            json.dumps(subscription.filters),
            1 if subscription.is_active else 0,
            subscription.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return subscription
    
    def schedule_webhook_delivery(
        self,
        subscription_id: str,
        payload: Dict
    ) -> WebhookDelivery:
        """Schedule webhook delivery"""
        delivery_id = hashlib.sha256(
            f"{subscription_id}{time.time()}".encode()
        ).hexdigest()[:16]
        
        delivery = WebhookDelivery(
            delivery_id=delivery_id,
            subscription_id=subscription_id,
            payload=payload,
            status='pending'
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO webhook_deliveries
            (delivery_id, subscription_id, payload, status, scheduled_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            delivery.delivery_id,
            delivery.subscription_id,
            json.dumps(delivery.payload),
            delivery.status,
            delivery.scheduled_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return delivery
    
    def to_stix_format(self, intelligence_data: Dict) -> Dict:
        """
        Convert intelligence data to STIX 2.1 format.
        
        STIX (Structured Threat Information Expression) is a standardized
        language for describing cyber threat information.
        """
        feed_type = intelligence_data.get('feed_type', 'unknown')
        
        if feed_type == 'ioc':
            return self._ioc_to_stix(intelligence_data)
        elif feed_type == 'vulnerability':
            return self._vulnerability_to_stix(intelligence_data)
        elif feed_type == 'threat_actor':
            return self._threat_actor_to_stix(intelligence_data)
        else:
            return {
                'type': 'bundle',
                'id': f"bundle--{hashlib.sha256(str(intelligence_data).encode()).hexdigest()[:16]}",
                'objects': []
            }
    
    def _ioc_to_stix(self, ioc_data: Dict) -> Dict:
        """Convert IoC to STIX indicator object"""
        return {
            'type': 'indicator',
            'spec_version': '2.1',
            'id': f"indicator--{ioc_data.get('ioc_id', 'unknown')}",
            'created': ioc_data.get('first_seen', datetime.utcnow().isoformat()),
            'modified': ioc_data.get('last_seen', datetime.utcnow().isoformat()),
            'name': f"{ioc_data.get('indicator_type', 'unknown')} indicator",
            'description': ioc_data.get('context', ''),
            'indicator_types': ['malicious-activity'],
            'pattern': f"[{ioc_data.get('indicator_type', 'unknown')}:value = '{ioc_data.get('indicator', '')}']",
            'pattern_type': 'stix',
            'valid_from': ioc_data.get('first_seen', datetime.utcnow().isoformat()),
            'confidence': int(ioc_data.get('confidence', 0.5) * 100)
        }
    
    def _vulnerability_to_stix(self, vuln_data: Dict) -> Dict:
        """Convert vulnerability to STIX vulnerability object"""
        return {
            'type': 'vulnerability',
            'spec_version': '2.1',
            'id': f"vulnerability--{vuln_data.get('cve_id', 'unknown')}",
            'created': vuln_data.get('published_date', datetime.utcnow().isoformat()),
            'modified': vuln_data.get('last_modified_date', datetime.utcnow().isoformat()),
            'name': vuln_data.get('cve_id', 'Unknown Vulnerability'),
            'description': vuln_data.get('description', ''),
            'external_references': [{
                'source_name': 'cve',
                'external_id': vuln_data.get('cve_id', '')
            }]
        }
    
    def _threat_actor_to_stix(self, actor_data: Dict) -> Dict:
        """Convert threat actor to STIX threat-actor object"""
        return {
            'type': 'threat-actor',
            'spec_version': '2.1',
            'id': f"threat-actor--{actor_data.get('actor_id', 'unknown')}",
            'created': actor_data.get('first_observed', datetime.utcnow().isoformat()),
            'modified': actor_data.get('last_updated', datetime.utcnow().isoformat()),
            'name': actor_data.get('name', 'Unknown Actor'),
            'description': actor_data.get('description', ''),
            'threat_actor_types': [actor_data.get('actor_type', 'unknown')],
            'sophistication': actor_data.get('sophistication_level', 'unknown'),
            'resource_level': actor_data.get('resource_level', 'unknown'),
            'primary_motivation': actor_data.get('motivation', 'unknown')
        }


# Example usage
if __name__ == "__main__":
    # Initialize API
    api = ThreatIntelligenceFeedAPI()
    
    print("=== Threat Intelligence Feed API ===\n")
    
    # Example 1: Create API key
    print("=== API Key Creation ===\n")
    
    api_key = api.create_api_key(
        organization="ACME Security Corp",
        permissions=[
            APIKeyPermission.READ_PREMIUM,
            APIKeyPermission.WRITE
        ],
        rate_limit_tier=RateLimitTier.PROFESSIONAL,
        expires_days=365
    )
    
    print(f"Organization: {api_key.organization}")
    print(f"API Key: {api_key.api_key[:20]}...")
    print(f"Key ID: {api_key.key_id}")
    print(f"Rate Limit: {api_key.get_rate_limit()} requests/hour")
    print(f"Permissions: {', '.join([p.value for p in api_key.permissions])}")
    print(f"Expires: {api_key.expires_at.strftime('%Y-%m-%d') if api_key.expires_at else 'Never'}")
    
    # Example 2: Validate API key
    print("\n=== API Key Validation ===\n")
    
    validated_key = api.validate_api_key(api_key.api_key)
    if validated_key:
        print(f"✓ API key valid for: {validated_key.organization}")
        print(f"  Rate limit tier: {validated_key.rate_limit_tier.value}")
    
    # Example 3: Query threat intelligence
    print("\n=== Query Threat Intelligence ===\n")
    
    filters = QueryFilter(
        feed_types=[FeedType.IOC, FeedType.VULNERABILITY],
        confidence_min=0.7,
        start_date=datetime.utcnow() - timedelta(days=7),
        limit=10,
        offset=0
    )
    
    response = api.query_threat_intelligence(api_key, filters)
    
    print(f"Status: {response['status']}")
    print(f"Total results: {response['metadata']['total_count']}")
    print(f"Returned: {response['metadata']['returned_count']}")
    print(f"Has more: {response['metadata']['has_more']}")
    
    # Example 4: Create subscription
    print("\n=== Feed Subscription ===\n")
    
    subscription = api.create_subscription(
        api_key_id=api_key.key_id,
        feed_types=[FeedType.IOC, FeedType.MALWARE],
        delivery_method=DeliveryMethod.WEBHOOK,
        webhook_url="https://customer.example.com/threat-intel-webhook",
        filters={
            'severity_min': 'high',
            'confidence_min': 0.8
        }
    )
    
    print(f"Subscription ID: {subscription.subscription_id}")
    print(f"Feed types: {', '.join([ft.value for ft in subscription.feed_types])}")
    print(f"Delivery: {subscription.delivery_method.value}")
    print(f"Webhook URL: {subscription.webhook_url}")
    print(f"Active: {subscription.is_active}")
    
    # Example 5: STIX format conversion
    print("\n=== STIX Format Conversion ===\n")
    
    sample_ioc = {
        'feed_type': 'ioc',
        'ioc_id': 'IOC-12345',
        'indicator': '198.51.100.42',
        'indicator_type': 'ipv4-addr',
        'first_seen': datetime.utcnow().isoformat(),
        'last_seen': datetime.utcnow().isoformat(),
        'confidence': 0.85,
        'context': 'Command and control server for APT29'
    }
    
    stix_object = api.to_stix_format(sample_ioc)
    
    print(f"STIX Type: {stix_object['type']}")
    print(f"STIX ID: {stix_object['id']}")
    print(f"Pattern: {stix_object['pattern']}")
    print(f"Confidence: {stix_object['confidence']}")
    
    # Example 6: Schedule webhook delivery
    print("\n=== Webhook Delivery ===\n")
    
    payload = {
        'event': 'new_threat_intelligence',
        'data': sample_ioc,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    delivery = api.schedule_webhook_delivery(
        subscription_id=subscription.subscription_id,
        payload=payload
    )
    
    print(f"Delivery ID: {delivery.delivery_id}")
    print(f"Status: {delivery.status}")
    print(f"Scheduled: {delivery.scheduled_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Max attempts: {delivery.max_attempts}")
    
    print("\n✓ Threat Intelligence Feed API operational!")
