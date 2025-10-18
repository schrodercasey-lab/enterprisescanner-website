"""
Military Upgrade #22: SIEM Integration
Part 1: Log Aggregation & Normalization

This module implements centralized log aggregation and normalization for
Security Information and Event Management (SIEM) systems.

Key Features:
- Multi-source log collection (syslog, JSON, CEF, LEEF)
- Log parsing and normalization to common schema
- Field extraction and enrichment
- Timestamp standardization
- Log filtering and routing
- Integration with Splunk, ELK Stack, QRadar

Compliance:
- NIST 800-53 AU-6 (Audit Review, Analysis, and Reporting)
- NIST 800-92 (Guide to Computer Security Log Management)
- PCI DSS Requirement 10.2 (Audit Logs)
- GDPR Article 32 (Security of Processing)
- SOC 2 CC7.2 (System Operations)
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import re
import json
import hashlib


class LogLevel(Enum):
    """Standard log severity levels (RFC 5424)"""
    EMERGENCY = 0  # System unusable
    ALERT = 1  # Action must be taken immediately
    CRITICAL = 2  # Critical conditions
    ERROR = 3  # Error conditions
    WARNING = 4  # Warning conditions
    NOTICE = 5  # Normal but significant
    INFO = 6  # Informational messages
    DEBUG = 7  # Debug messages


class LogFormat(Enum):
    """Supported log formats"""
    SYSLOG = "syslog"  # RFC 5424
    JSON = "json"
    CEF = "cef"  # Common Event Format (ArcSight)
    LEEF = "leef"  # Log Event Extended Format (QRadar)
    APACHE = "apache"
    NGINX = "nginx"
    AWS_CLOUDTRAIL = "aws_cloudtrail"
    KUBERNETES = "kubernetes"


class EventCategory(Enum):
    """SIEM event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    SECURITY = "security"
    AUDIT = "audit"


@dataclass
class NormalizedLog:
    """Normalized log event schema (ECS-inspired)"""
    # Core fields
    timestamp: datetime
    log_level: LogLevel
    message: str
    
    # Source identification
    source_ip: Optional[str] = None
    source_hostname: Optional[str] = None
    source_service: Optional[str] = None
    
    # Event classification
    event_category: Optional[EventCategory] = None
    event_action: Optional[str] = None
    event_outcome: Optional[str] = None  # success, failure
    
    # User/Actor
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    
    # Destination
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None
    
    # Network
    protocol: Optional[str] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None
    
    # HTTP
    http_method: Optional[str] = None
    http_status: Optional[int] = None
    http_url: Optional[str] = None
    http_user_agent: Optional[str] = None
    
    # File
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Process
    process_name: Optional[str] = None
    process_id: Optional[int] = None
    
    # Metadata
    original_log: str = ""
    log_format: Optional[LogFormat] = None
    tags: List[str] = field(default_factory=list)
    
    # Enrichment
    geo_city: Optional[str] = None
    geo_country: Optional[str] = None
    threat_score: Optional[int] = None


@dataclass
class LogSource:
    """Log source configuration"""
    source_id: str
    source_name: str
    source_type: str  # server, firewall, application, database
    log_format: LogFormat
    enabled: bool = True
    
    # Collection
    collection_method: str = "syslog"  # syslog, file, api
    endpoint: Optional[str] = None
    port: Optional[int] = None
    
    # Filtering
    filters: List[str] = field(default_factory=list)
    
    # Statistics
    logs_received: int = 0
    logs_parsed: int = 0
    parse_errors: int = 0
    last_received: Optional[datetime] = None


class LogParser:
    """Log parsing engine"""
    
    def __init__(self):
        # Regex patterns for common formats
        self.syslog_pattern = re.compile(
            r'<(?P<priority>\d+)>(?P<timestamp>[\w\s:+-]+) '
            r'(?P<hostname>[\w.-]+) (?P<service>[\w.-]+): (?P<message>.*)'
        )
        
        self.apache_pattern = re.compile(
            r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\w+) (?P<url>[^\s]+) HTTP/[\d.]+"\s+'
            r'(?P<status>\d+) (?P<bytes>\d+)'
        )
        
        self.auth_pattern = re.compile(
            r'(?P<action>Failed|Successful) (?P<method>password|publickey) for '
            r'(?P<user>[\w-]+) from (?P<ip>[\d.]+)'
        )
    
    def parse(self, raw_log: str, log_format: LogFormat) -> Optional[NormalizedLog]:
        """Parse raw log to normalized format"""
        try:
            if log_format == LogFormat.JSON:
                return self._parse_json(raw_log)
            elif log_format == LogFormat.SYSLOG:
                return self._parse_syslog(raw_log)
            elif log_format == LogFormat.CEF:
                return self._parse_cef(raw_log)
            elif log_format == LogFormat.APACHE:
                return self._parse_apache(raw_log)
            else:
                # Generic parsing
                return self._parse_generic(raw_log, log_format)
                
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return None
    
    def _parse_json(self, raw_log: str) -> NormalizedLog:
        """Parse JSON log format"""
        data = json.loads(raw_log)
        
        # Map common JSON fields to normalized schema
        return NormalizedLog(
            timestamp=self._parse_timestamp(data.get('timestamp', data.get('@timestamp'))),
            log_level=self._parse_log_level(data.get('level', 'INFO')),
            message=data.get('message', data.get('msg', '')),
            source_hostname=data.get('host', data.get('hostname')),
            source_service=data.get('service', data.get('app')),
            user_name=data.get('user', data.get('username')),
            source_ip=data.get('source_ip', data.get('ip')),
            http_method=data.get('method'),
            http_status=data.get('status'),
            http_url=data.get('url', data.get('path')),
            original_log=raw_log,
            log_format=LogFormat.JSON
        )
    
    def _parse_syslog(self, raw_log: str) -> NormalizedLog:
        """Parse syslog format (RFC 5424)"""
        match = self.syslog_pattern.match(raw_log)
        
        if not match:
            return self._parse_generic(raw_log, LogFormat.SYSLOG)
        
        priority = int(match.group('priority'))
        severity = priority & 0x07  # Last 3 bits
        
        # Check for authentication events
        message = match.group('message')
        auth_match = self.auth_pattern.search(message)
        
        log = NormalizedLog(
            timestamp=self._parse_timestamp(match.group('timestamp')),
            log_level=LogLevel(severity),
            message=message,
            source_hostname=match.group('hostname'),
            source_service=match.group('service'),
            original_log=raw_log,
            log_format=LogFormat.SYSLOG
        )
        
        # Extract authentication details
        if auth_match:
            log.event_category = EventCategory.AUTHENTICATION
            log.event_action = 'login'
            log.event_outcome = 'success' if auth_match.group('action') == 'Successful' else 'failure'
            log.user_name = auth_match.group('user')
            log.source_ip = auth_match.group('ip')
            log.tags.append('authentication')
        
        return log
    
    def _parse_cef(self, raw_log: str) -> NormalizedLog:
        """Parse Common Event Format (CEF)"""
        # CEF format: CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        parts = raw_log.split('|')
        
        if len(parts) < 8 or not parts[0].startswith('CEF:'):
            return self._parse_generic(raw_log, LogFormat.CEF)
        
        severity_map = {
            '0': LogLevel.INFO,
            '1-3': LogLevel.WARNING,
            '4-6': LogLevel.ERROR,
            '7-8': LogLevel.CRITICAL,
            '9-10': LogLevel.EMERGENCY
        }
        
        severity = int(parts[6]) if parts[6].isdigit() else 0
        log_level = LogLevel.INFO
        if severity >= 9:
            log_level = LogLevel.EMERGENCY
        elif severity >= 7:
            log_level = LogLevel.CRITICAL
        elif severity >= 4:
            log_level = LogLevel.ERROR
        elif severity >= 1:
            log_level = LogLevel.WARNING
        
        # Parse extension fields
        extension = parts[7] if len(parts) > 7 else ""
        ext_fields = {}
        for field in extension.split():
            if '=' in field:
                key, value = field.split('=', 1)
                ext_fields[key] = value
        
        return NormalizedLog(
            timestamp=datetime.now(timezone.utc),
            log_level=log_level,
            message=parts[5],  # Name field
            source_hostname=ext_fields.get('shost', ext_fields.get('dvc')),
            source_ip=ext_fields.get('src'),
            destination_ip=ext_fields.get('dst'),
            destination_port=int(ext_fields.get('dpt', 0)) if ext_fields.get('dpt', '').isdigit() else None,
            user_name=ext_fields.get('suser'),
            original_log=raw_log,
            log_format=LogFormat.CEF,
            tags=['cef']
        )
    
    def _parse_apache(self, raw_log: str) -> NormalizedLog:
        """Parse Apache access log format"""
        match = self.apache_pattern.match(raw_log)
        
        if not match:
            return self._parse_generic(raw_log, LogFormat.APACHE)
        
        status = int(match.group('status'))
        log_level = LogLevel.INFO
        if status >= 500:
            log_level = LogLevel.ERROR
        elif status >= 400:
            log_level = LogLevel.WARNING
        
        return NormalizedLog(
            timestamp=self._parse_timestamp(match.group('timestamp')),
            log_level=log_level,
            message=f"{match.group('method')} {match.group('url')} {status}",
            source_ip=match.group('ip'),
            http_method=match.group('method'),
            http_url=match.group('url'),
            http_status=status,
            bytes_sent=int(match.group('bytes')),
            event_category=EventCategory.NETWORK,
            original_log=raw_log,
            log_format=LogFormat.APACHE,
            tags=['http', 'access']
        )
    
    def _parse_generic(self, raw_log: str, log_format: LogFormat) -> NormalizedLog:
        """Generic parsing fallback"""
        # Extract timestamp if present
        timestamp = datetime.now(timezone.utc)
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, raw_log)
            if match:
                timestamp = self._parse_timestamp(match.group(0))
                break
        
        return NormalizedLog(
            timestamp=timestamp,
            log_level=LogLevel.INFO,
            message=raw_log[:500],  # First 500 chars
            original_log=raw_log,
            log_format=log_format,
            tags=['unparsed']
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse various timestamp formats"""
        if not timestamp_str:
            return datetime.now(timezone.utc)
        
        # Try ISO format
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%d/%b/%Y:%H:%M:%S',
            '%b %d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str.strip(), fmt)
                # Add timezone if not present
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        
        # Fallback to current time
        return datetime.now(timezone.utc)
    
    def _parse_log_level(self, level_str: str) -> LogLevel:
        """Parse log level string"""
        level_map = {
            'EMERGENCY': LogLevel.EMERGENCY,
            'EMERG': LogLevel.EMERGENCY,
            'ALERT': LogLevel.ALERT,
            'CRITICAL': LogLevel.CRITICAL,
            'CRIT': LogLevel.CRITICAL,
            'ERROR': LogLevel.ERROR,
            'ERR': LogLevel.ERROR,
            'WARNING': LogLevel.WARNING,
            'WARN': LogLevel.WARNING,
            'NOTICE': LogLevel.NOTICE,
            'INFO': LogLevel.INFO,
            'DEBUG': LogLevel.DEBUG,
        }
        
        return level_map.get(level_str.upper(), LogLevel.INFO)


class LogAggregator:
    """Log Aggregation & Normalization Engine"""
    
    def __init__(self):
        self.parser = LogParser()
        self.sources: Dict[str, LogSource] = {}
        self.logs: List[NormalizedLog] = []
        self.parse_errors: List[Dict[str, Any]] = []
        
        # Statistics
        self.total_received = 0
        self.total_parsed = 0
        self.total_errors = 0
    
    def register_source(self, source: LogSource) -> bool:
        """Register log source"""
        try:
            self.sources[source.source_id] = source
            print(f"✅ Log source registered: {source.source_name} ({source.log_format.value})")
            return True
        except Exception as e:
            print(f"❌ Failed to register source: {e}")
            return False
    
    def ingest_log(self, source_id: str, raw_log: str) -> Optional[NormalizedLog]:
        """Ingest and normalize log"""
        if source_id not in self.sources:
            print(f"❌ Unknown source: {source_id}")
            return None
        
        source = self.sources[source_id]
        
        if not source.enabled:
            return None
        
        self.total_received += 1
        source.logs_received += 1
        source.last_received = datetime.now(timezone.utc)
        
        # Apply filters
        if self._should_filter(raw_log, source.filters):
            return None
        
        # Parse log
        normalized = self.parser.parse(raw_log, source.log_format)
        
        if normalized:
            # Enrich with source info
            if not normalized.source_hostname:
                normalized.source_hostname = source.source_name
            if not normalized.source_service:
                normalized.source_service = source.source_type
            
            self.logs.append(normalized)
            self.total_parsed += 1
            source.logs_parsed += 1
            
            return normalized
        else:
            self.total_errors += 1
            source.parse_errors += 1
            self._record_parse_error(source_id, raw_log)
            return None
    
    def _should_filter(self, log: str, filters: List[str]) -> bool:
        """Check if log should be filtered out"""
        for filter_pattern in filters:
            if re.search(filter_pattern, log, re.IGNORECASE):
                return True
        return False
    
    def _record_parse_error(self, source_id: str, raw_log: str) -> None:
        """Record parse error for analysis"""
        self.parse_errors.append({
            'timestamp': datetime.now(timezone.utc),
            'source_id': source_id,
            'raw_log': raw_log[:500],
            'error_type': 'parse_failure'
        })
    
    def batch_ingest(self, source_id: str, raw_logs: List[str]) -> Dict[str, int]:
        """Batch ingest multiple logs"""
        results = {'success': 0, 'failed': 0}
        
        for raw_log in raw_logs:
            if self.ingest_log(source_id, raw_log):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def search_logs(self, query: Dict[str, Any], limit: int = 100) -> List[NormalizedLog]:
        """Search normalized logs"""
        results = []
        
        for log in self.logs[-10000:]:  # Search last 10k logs
            if self._matches_query(log, query):
                results.append(log)
                if len(results) >= limit:
                    break
        
        return results
    
    def _matches_query(self, log: NormalizedLog, query: Dict[str, Any]) -> bool:
        """Check if log matches search query"""
        for key, value in query.items():
            log_value = getattr(log, key, None)
            if log_value != value:
                return False
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregation statistics"""
        return {
            'total_received': self.total_received,
            'total_parsed': self.total_parsed,
            'total_errors': self.total_errors,
            'parse_success_rate': f"{(self.total_parsed/self.total_received*100):.1f}%" if self.total_received > 0 else "0%",
            'sources': len(self.sources),
            'active_sources': sum(1 for s in self.sources.values() if s.enabled),
            'logs_stored': len(self.logs),
            'recent_errors': len([e for e in self.parse_errors if 
                                 datetime.now(timezone.utc) - e['timestamp'] < timedelta(hours=1)])
        }
    
    def export_to_elk(self, logs: List[NormalizedLog]) -> List[Dict[str, Any]]:
        """Export logs to ELK format"""
        return [
            {
                '@timestamp': log.timestamp.isoformat(),
                'level': log.log_level.name,
                'message': log.message,
                'source': {
                    'ip': log.source_ip,
                    'hostname': log.source_hostname,
                    'service': log.source_service
                },
                'event': {
                    'category': log.event_category.value if log.event_category else None,
                    'action': log.event_action,
                    'outcome': log.event_outcome
                },
                'user': {
                    'id': log.user_id,
                    'name': log.user_name
                },
                'http': {
                    'method': log.http_method,
                    'status': log.http_status,
                    'url': log.http_url
                },
                'tags': log.tags
            }
            for log in logs
        ]


# Example usage
if __name__ == "__main__":
    aggregator = LogAggregator()
    
    # Register sources
    web_source = LogSource(
        source_id="web01",
        source_name="web-server-01",
        source_type="web_server",
        log_format=LogFormat.APACHE,
        collection_method="syslog",
        port=514
    )
    
    aggregator.register_source(web_source)
    
    # Ingest logs
    apache_log = '192.168.1.100 - - [17/Oct/2025:10:30:45 +0000] "GET /api/users HTTP/1.1" 200 1234'
    normalized = aggregator.ingest_log("web01", apache_log)
    
    if normalized:
        print(f"\n✅ Log normalized:")
        print(f"Timestamp: {normalized.timestamp}")
        print(f"Level: {normalized.log_level.name}")
        print(f"Source IP: {normalized.source_ip}")
        print(f"HTTP Status: {normalized.http_status}")
    
    # Get statistics
    stats = aggregator.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"Total received: {stats['total_received']}")
    print(f"Parse success rate: {stats['parse_success_rate']}")
