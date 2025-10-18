"""
Military-Grade Threat Intelligence Integration - Part 2
========================================================

STIX/TAXII Protocol Implementation + IoC Correlation Engine

COMPLIANCE FRAMEWORKS:
- NIST 800-53 Rev 5: SI-4 (Information System Monitoring)
- STIX 2.1 (Structured Threat Information Expression)
- TAXII 2.1 (Trusted Automated eXchange of Indicator Information)
- OASIS Cyber Threat Intelligence (CTI) Standards
- MITRE ATT&CK Framework Integration

PROTOCOLS:
- STIX 2.1: JSON-based threat intelligence representation
- TAXII 2.1: RESTful API for sharing threat intelligence
- OpenC2: Open Command and Control for automated response

Part 2 Focus: STIX/TAXII Implementation, IoC Correlation, Automated Enrichment
"""

import json
import hashlib
import sqlite3
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import ipaddress
import re


class STIXObjectType(Enum):
    """STIX 2.1 Domain Objects"""
    ATTACK_PATTERN = "attack-pattern"
    CAMPAIGN = "campaign"
    COURSE_OF_ACTION = "course-of-action"
    IDENTITY = "identity"
    INDICATOR = "indicator"
    INTRUSION_SET = "intrusion-set"
    MALWARE = "malware"
    OBSERVED_DATA = "observed-data"
    REPORT = "report"
    THREAT_ACTOR = "threat-actor"
    TOOL = "tool"
    VULNERABILITY = "vulnerability"


class CorrelationMethod(Enum):
    """Methods for correlating indicators with assets"""
    EXACT_MATCH = "exact_match"  # IP, domain, hash exact match
    SUBNET_MATCH = "subnet_match"  # IP in subnet
    REGEX_MATCH = "regex_match"  # Pattern matching
    FUZZY_MATCH = "fuzzy_match"  # Similarity matching
    BEHAVIORAL_MATCH = "behavioral_match"  # Behavior pattern


class CorrelationSeverity(Enum):
    """Severity of IoC correlation match"""
    CONFIRMED_COMPROMISE = "confirmed_compromise"  # 100% match, immediate response
    HIGH_CONFIDENCE = "high_confidence"  # 85%+ match
    MEDIUM_CONFIDENCE = "medium_confidence"  # 60-84% match
    LOW_CONFIDENCE = "low_confidence"  # 40-59% match
    INFORMATIONAL = "informational"  # <40% match


@dataclass
class STIXIndicator:
    """STIX 2.1 Indicator object"""
    id: str  # indicator--<UUID>
    type: str = "indicator"
    spec_version: str = "2.1"
    created: str = ""
    modified: str = ""
    name: str = ""
    description: str = ""
    pattern: str = ""  # STIX Pattern (e.g., "[ipv4-addr:value = '192.0.2.1']")
    pattern_type: str = "stix"
    valid_from: str = ""
    valid_until: Optional[str] = None
    kill_chain_phases: List[Dict[str, str]] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    confidence: int = 0
    external_references: List[Dict[str, str]] = field(default_factory=list)
    object_marking_refs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to STIX 2.1 JSON format"""
        return {k: v for k, v in asdict(self).items() if v is not None and v != "" and v != [] and v != 0}


@dataclass
class TAXIICollection:
    """TAXII 2.1 Collection"""
    id: str
    title: str
    description: str
    can_read: bool = True
    can_write: bool = False
    media_types: List[str] = field(default_factory=lambda: ["application/taxii+json;version=2.1"])


@dataclass
class IoCCorrelation:
    """Indicator of Compromise correlation result"""
    correlation_id: str
    timestamp: datetime
    indicator_id: str
    indicator_value: str
    indicator_type: str
    asset_id: str
    asset_type: str  # ec2_instance, s3_bucket, ip_address, domain, etc.
    asset_identifier: str
    correlation_method: CorrelationMethod
    confidence_score: float  # 0-100
    severity: CorrelationSeverity
    description: str
    evidence: List[Dict[str, Any]]
    recommended_actions: List[str]
    mitre_techniques: List[str]
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None
    automated_response_triggered: bool = False
    false_positive_likelihood: float = 0.0  # 0-100


@dataclass
class IoCCorrelationReport:
    """Comprehensive IoC correlation assessment"""
    report_id: str
    scan_time: datetime
    total_indicators_checked: int
    total_assets_scanned: int
    correlations_found: List[IoCCorrelation]
    confirmed_compromises: int
    high_confidence_matches: int
    medium_confidence_matches: int
    low_confidence_matches: int
    affected_assets: Set[str]
    affected_asset_types: Dict[str, int]
    threat_actors_detected: Set[str]
    campaigns_detected: Set[str]
    recommended_actions: List[str]
    correlation_score: int  # 0-100 (lower is better - fewer matches)


class STIXTAXIIProcessor:
    """
    STIX/TAXII protocol implementation for threat intelligence
    Converts indicators to STIX 2.1 format and enables TAXII sharing
    """
    
    def __init__(self):
        self.stix_objects: List[Dict[str, Any]] = []
        self.taxii_collections: List[TAXIICollection] = []
    
    def create_stix_indicator(
        self,
        indicator_value: str,
        indicator_type: str,
        name: str,
        description: str,
        confidence: int,
        labels: List[str],
        kill_chain_phases: List[Dict[str, str]] = None,
        valid_hours: int = 168
    ) -> STIXIndicator:
        """
        Create STIX 2.1 Indicator object
        
        Args:
            indicator_value: IP, domain, hash, etc.
            indicator_type: ipv4-addr, domain-name, file:hashes.MD5, etc.
            name: Human-readable name
            description: Indicator description
            confidence: 0-100
            labels: Tags (e.g., ['malicious-activity', 'apt28'])
            kill_chain_phases: Cyber Kill Chain phases
            valid_hours: How long indicator is valid
        """
        indicator_id = f"indicator--{hashlib.sha256(indicator_value.encode()).hexdigest()[:36]}"
        now = datetime.now().isoformat() + "Z"
        valid_until = (datetime.now() + timedelta(hours=valid_hours)).isoformat() + "Z"
        
        # Create STIX pattern based on type
        if indicator_type == "ipv4-addr":
            pattern = f"[ipv4-addr:value = '{indicator_value}']"
        elif indicator_type == "domain-name":
            pattern = f"[domain-name:value = '{indicator_value}']"
        elif indicator_type == "url":
            pattern = f"[url:value = '{indicator_value}']"
        elif indicator_type.startswith("file:hashes"):
            hash_type = indicator_type.split('.')[-1].upper()
            pattern = f"[file:hashes.'{hash_type}' = '{indicator_value}']"
        else:
            pattern = f"[{indicator_type}:value = '{indicator_value}']"
        
        # Default kill chain if not provided
        if kill_chain_phases is None:
            kill_chain_phases = [{
                "kill_chain_name": "lockheed-martin-cyber-kill-chain",
                "phase_name": "command-and-control"
            }]
        
        indicator = STIXIndicator(
            id=indicator_id,
            created=now,
            modified=now,
            name=name,
            description=description,
            pattern=pattern,
            pattern_type="stix",
            valid_from=now,
            valid_until=valid_until,
            kill_chain_phases=kill_chain_phases,
            labels=labels,
            confidence=confidence
        )
        
        self.stix_objects.append(indicator.to_dict())
        return indicator
    
    def create_stix_bundle(self, objects: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create STIX 2.1 Bundle containing multiple objects
        
        Args:
            objects: List of STIX objects (uses self.stix_objects if None)
        
        Returns:
            STIX Bundle as dictionary
        """
        if objects is None:
            objects = self.stix_objects
        
        bundle = {
            "type": "bundle",
            "id": f"bundle--{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:36]}",
            "objects": objects
        }
        
        return bundle
    
    def export_to_taxii(self, collection_id: str = "default") -> Dict[str, Any]:
        """
        Export STIX objects to TAXII 2.1 format
        
        Returns:
            TAXII envelope containing STIX objects
        """
        taxii_envelope = {
            "more": False,
            "objects": self.stix_objects
        }
        
        return taxii_envelope
    
    def parse_stix_pattern(self, pattern: str) -> Tuple[str, str]:
        """
        Parse STIX pattern to extract type and value
        
        Args:
            pattern: STIX pattern (e.g., "[ipv4-addr:value = '192.0.2.1']")
        
        Returns:
            Tuple of (type, value)
        """
        # Example: [ipv4-addr:value = '192.0.2.1']
        match = re.search(r'\[([^:]+):value\s*=\s*[\'"]([^\'"]+)[\'"]\]', pattern)
        if match:
            return match.group(1), match.group(2)
        return "", ""
    
    def validate_stix_object(self, stix_obj: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate STIX 2.1 object against specification
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Required fields
        if 'type' not in stix_obj:
            errors.append("Missing required field: type")
        if 'id' not in stix_obj:
            errors.append("Missing required field: id")
        if 'spec_version' not in stix_obj or stix_obj['spec_version'] != '2.1':
            errors.append("spec_version must be '2.1'")
        
        # Validate ID format
        if 'id' in stix_obj:
            if not re.match(r'^[a-z-]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', stix_obj['id']):
                errors.append(f"Invalid ID format: {stix_obj['id']}")
        
        # Type-specific validation
        if stix_obj.get('type') == 'indicator':
            if 'pattern' not in stix_obj:
                errors.append("Indicator must have pattern field")
            if 'valid_from' not in stix_obj:
                errors.append("Indicator must have valid_from field")
        
        return len(errors) == 0, errors


class IoCCorrelationEngine:
    """
    IoC Correlation Engine
    Correlates threat indicators with infrastructure assets to identify compromises
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize correlation engine with SQLite database
        
        Args:
            db_path: Path to SQLite database (use :memory: for in-memory)
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_database()
        self.correlations: List[IoCCorrelation] = []
    
    def _init_database(self):
        """Initialize correlation database schema"""
        cursor = self.conn.cursor()
        
        # Indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                value TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                source TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                mitre_techniques TEXT,
                threat_actor TEXT,
                campaign TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                metadata TEXT,
                last_scan TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Correlations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS correlations (
                id TEXT PRIMARY KEY,
                indicator_id TEXT NOT NULL,
                asset_id TEXT NOT NULL,
                method TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                severity TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                evidence TEXT,
                false_positive_likelihood REAL DEFAULT 0.0,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (indicator_id) REFERENCES indicators(id),
                FOREIGN KEY (asset_id) REFERENCES assets(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicators_value ON indicators(value)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_identifier ON assets(identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_correlations_timestamp ON correlations(timestamp)")
        
        self.conn.commit()
    
    def add_indicator(
        self,
        indicator_id: str,
        indicator_type: str,
        indicator_value: str,
        severity: str,
        confidence: int,
        source: str,
        mitre_techniques: List[str] = None,
        threat_actor: str = None,
        campaign: str = None
    ):
        """Add indicator to correlation database"""
        cursor = self.conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO indicators 
            (id, type, value, severity, confidence, source, first_seen, last_seen, 
             mitre_techniques, threat_actor, campaign)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            indicator_id,
            indicator_type,
            indicator_value,
            severity,
            confidence,
            source,
            now,
            now,
            json.dumps(mitre_techniques) if mitre_techniques else None,
            threat_actor,
            campaign
        ))
        
        self.conn.commit()
    
    def add_asset(
        self,
        asset_id: str,
        asset_type: str,
        asset_identifier: str,
        metadata: Dict[str, Any] = None
    ):
        """Add asset to correlation database"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO assets (id, type, identifier, metadata, last_scan)
            VALUES (?, ?, ?, ?, ?)
        """, (
            asset_id,
            asset_type,
            asset_identifier,
            json.dumps(metadata) if metadata else None,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
    
    def correlate_indicators(
        self,
        asset_data: Dict[str, List[Dict[str, Any]]]
    ) -> IoCCorrelationReport:
        """
        Correlate all indicators against asset data
        
        Args:
            asset_data: Dictionary of asset types to asset lists
                       {
                           'ec2_instances': [{'id': 'i-123', 'private_ip': '10.0.1.5', ...}],
                           'security_groups': [{'id': 'sg-123', 'ingress_ips': ['0.0.0.0/0'], ...}],
                           's3_buckets': [{'name': 'my-bucket', 'objects': [...]}],
                           ...
                       }
        
        Returns:
            IoC correlation report
        """
        print("🔍 Starting IoC Correlation Analysis...")
        
        self.correlations = []
        
        # Load indicators from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM indicators")
        indicators = cursor.fetchall()
        
        total_indicators = len(indicators)
        total_assets = sum(len(assets) for assets in asset_data.values())
        
        print(f"  📊 Correlating {total_indicators} indicators against {total_assets} assets...")
        
        # Correlate each indicator type
        for indicator in indicators:
            (ind_id, ind_type, ind_value, severity, confidence, source, 
             first_seen, last_seen, mitre_tech, threat_actor, campaign, created) = indicator
            
            if ind_type == "ip_address":
                self._correlate_ip_indicator(
                    ind_id, ind_value, severity, confidence, 
                    asset_data, mitre_tech, threat_actor, campaign
                )
            elif ind_type == "domain":
                self._correlate_domain_indicator(
                    ind_id, ind_value, severity, confidence,
                    asset_data, mitre_tech, threat_actor, campaign
                )
            elif ind_type in ["md5", "sha1", "sha256"]:
                self._correlate_hash_indicator(
                    ind_id, ind_value, ind_type, severity, confidence,
                    asset_data, mitre_tech, threat_actor, campaign
                )
        
        # Generate report
        return self._generate_correlation_report(total_indicators, total_assets)
    
    def _correlate_ip_indicator(
        self,
        indicator_id: str,
        ip_value: str,
        severity: str,
        confidence: int,
        asset_data: Dict[str, List[Dict[str, Any]]],
        mitre_techniques: str = None,
        threat_actor: str = None,
        campaign: str = None
    ):
        """Correlate IP indicator against assets"""
        
        try:
            indicator_ip = ipaddress.ip_address(ip_value)
        except:
            return
        
        # Check EC2 instances
        for instance in asset_data.get('ec2_instances', []):
            # Check public IP
            if instance.get('public_ip') == ip_value:
                self._create_correlation(
                    indicator_id, ip_value, "ip_address",
                    instance['id'], "ec2_instance", instance['id'],
                    CorrelationMethod.EXACT_MATCH,
                    confidence,
                    severity,
                    f"EC2 instance public IP matches malicious indicator",
                    [{"field": "public_ip", "value": instance.get('public_ip')}],
                    mitre_techniques, threat_actor, campaign
                )
            
            # Check private IP
            if instance.get('private_ip') == ip_value:
                self._create_correlation(
                    indicator_id, ip_value, "ip_address",
                    instance['id'], "ec2_instance", instance['id'],
                    CorrelationMethod.EXACT_MATCH,
                    confidence * 0.8,  # Slightly lower confidence for private IP
                    severity,
                    f"EC2 instance private IP matches malicious indicator (possible lateral movement)",
                    [{"field": "private_ip", "value": instance.get('private_ip')}],
                    mitre_techniques, threat_actor, campaign
                )
        
        # Check Security Groups
        for sg in asset_data.get('security_groups', []):
            for rule in sg.get('ingress_rules', []):
                cidr = rule.get('cidr')
                if cidr:
                    try:
                        network = ipaddress.ip_network(cidr, strict=False)
                        if indicator_ip in network:
                            self._create_correlation(
                                indicator_id, ip_value, "ip_address",
                                sg['id'], "security_group", sg['id'],
                                CorrelationMethod.SUBNET_MATCH,
                                confidence * 0.6,
                                severity,
                                f"Security group allows traffic from malicious IP subnet {cidr}",
                                [{"rule": rule}],
                                mitre_techniques, threat_actor, campaign
                            )
                    except:
                        continue
        
        # Check CloudTrail logs (if provided)
        for log_entry in asset_data.get('cloudtrail_logs', []):
            if log_entry.get('source_ip') == ip_value:
                self._create_correlation(
                    indicator_id, ip_value, "ip_address",
                    log_entry.get('user_identity', {}).get('arn', 'unknown'),
                    "cloudtrail_event", log_entry.get('event_name', 'unknown'),
                    CorrelationMethod.EXACT_MATCH,
                    confidence,
                    severity,
                    f"CloudTrail event from malicious IP: {log_entry.get('event_name')}",
                    [log_entry],
                    mitre_techniques, threat_actor, campaign
                )
    
    def _correlate_domain_indicator(
        self,
        indicator_id: str,
        domain_value: str,
        severity: str,
        confidence: int,
        asset_data: Dict[str, List[Dict[str, Any]]],
        mitre_techniques: str = None,
        threat_actor: str = None,
        campaign: str = None
    ):
        """Correlate domain indicator against assets"""
        
        # Check DNS logs (if provided)
        for dns_log in asset_data.get('dns_logs', []):
            if dns_log.get('query_name') == domain_value:
                self._create_correlation(
                    indicator_id, domain_value, "domain",
                    dns_log.get('source_ip', 'unknown'), "dns_query", dns_log.get('source_ip', 'unknown'),
                    CorrelationMethod.EXACT_MATCH,
                    confidence,
                    severity,
                    f"DNS query to malicious domain from {dns_log.get('source_ip')}",
                    [dns_log],
                    mitre_techniques, threat_actor, campaign
                )
            
            # Check for subdomain matches
            if domain_value in dns_log.get('query_name', ''):
                self._create_correlation(
                    indicator_id, domain_value, "domain",
                    dns_log.get('source_ip', 'unknown'), "dns_query", dns_log.get('source_ip', 'unknown'),
                    CorrelationMethod.REGEX_MATCH,
                    confidence * 0.7,
                    severity,
                    f"DNS query to subdomain of malicious domain: {dns_log.get('query_name')}",
                    [dns_log],
                    mitre_techniques, threat_actor, campaign
                )
        
        # Check VPC Flow Logs for domain resolution
        for flow_log in asset_data.get('vpc_flow_logs', []):
            if domain_value in flow_log.get('destination_name', ''):
                self._create_correlation(
                    indicator_id, domain_value, "domain",
                    flow_log.get('source_ip', 'unknown'), "network_flow", 
                    f"{flow_log.get('source_ip')} -> {flow_log.get('destination_ip')}",
                    CorrelationMethod.REGEX_MATCH,
                    confidence * 0.8,
                    severity,
                    f"Network flow to resolved IP of malicious domain",
                    [flow_log],
                    mitre_techniques, threat_actor, campaign
                )
    
    def _correlate_hash_indicator(
        self,
        indicator_id: str,
        hash_value: str,
        hash_type: str,
        severity: str,
        confidence: int,
        asset_data: Dict[str, List[Dict[str, Any]]],
        mitre_techniques: str = None,
        threat_actor: str = None,
        campaign: str = None
    ):
        """Correlate file hash indicator against assets"""
        
        # Check S3 buckets
        for bucket in asset_data.get('s3_buckets', []):
            for obj in bucket.get('objects', []):
                if obj.get(f'{hash_type}_hash') == hash_value:
                    self._create_correlation(
                        indicator_id, hash_value, hash_type,
                        bucket['name'], "s3_object", f"{bucket['name']}/{obj.get('key')}",
                        CorrelationMethod.EXACT_MATCH,
                        confidence,
                        severity,
                        f"Malicious file found in S3: {obj.get('key')}",
                        [{"bucket": bucket['name'], "key": obj.get('key'), "hash": hash_value}],
                        mitre_techniques, threat_actor, campaign
                    )
        
        # Check EC2 instances (file scans)
        for instance in asset_data.get('ec2_instances', []):
            for file_scan in instance.get('file_scans', []):
                if file_scan.get(f'{hash_type}_hash') == hash_value:
                    self._create_correlation(
                        indicator_id, hash_value, hash_type,
                        instance['id'], "ec2_file", f"{instance['id']}:{file_scan.get('path')}",
                        CorrelationMethod.EXACT_MATCH,
                        confidence,
                        severity,
                        f"Malicious file found on EC2 instance: {file_scan.get('path')}",
                        [{"instance": instance['id'], "path": file_scan.get('path'), "hash": hash_value}],
                        mitre_techniques, threat_actor, campaign
                    )
    
    def _create_correlation(
        self,
        indicator_id: str,
        indicator_value: str,
        indicator_type: str,
        asset_id: str,
        asset_type: str,
        asset_identifier: str,
        method: CorrelationMethod,
        confidence_score: float,
        severity: str,
        description: str,
        evidence: List[Dict[str, Any]],
        mitre_techniques: str = None,
        threat_actor: str = None,
        campaign: str = None
    ):
        """Create correlation record"""
        
        # Determine correlation severity
        if confidence_score >= 95:
            corr_severity = CorrelationSeverity.CONFIRMED_COMPROMISE
        elif confidence_score >= 85:
            corr_severity = CorrelationSeverity.HIGH_CONFIDENCE
        elif confidence_score >= 60:
            corr_severity = CorrelationSeverity.MEDIUM_CONFIDENCE
        elif confidence_score >= 40:
            corr_severity = CorrelationSeverity.LOW_CONFIDENCE
        else:
            corr_severity = CorrelationSeverity.INFORMATIONAL
        
        # Calculate false positive likelihood
        fp_likelihood = self._calculate_false_positive_likelihood(
            method, confidence_score, asset_type
        )
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            corr_severity, asset_type, threat_actor
        )
        
        # Parse MITRE techniques
        techniques = json.loads(mitre_techniques) if mitre_techniques else []
        
        correlation = IoCCorrelation(
            correlation_id=hashlib.sha256(f"{indicator_id}-{asset_id}-{datetime.now()}".encode()).hexdigest()[:16],
            timestamp=datetime.now(),
            indicator_id=indicator_id,
            indicator_value=indicator_value,
            indicator_type=indicator_type,
            asset_id=asset_id,
            asset_type=asset_type,
            asset_identifier=asset_identifier,
            correlation_method=method,
            confidence_score=confidence_score,
            severity=corr_severity,
            description=description,
            evidence=evidence,
            recommended_actions=recommended_actions,
            mitre_techniques=techniques,
            threat_actor=threat_actor,
            campaign=campaign,
            automated_response_triggered=False,
            false_positive_likelihood=fp_likelihood
        )
        
        self.correlations.append(correlation)
        
        # Store in database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO correlations 
            (id, indicator_id, asset_id, method, confidence_score, severity, timestamp, evidence, false_positive_likelihood)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            correlation.correlation_id,
            indicator_id,
            asset_id,
            method.value,
            confidence_score,
            corr_severity.value,
            correlation.timestamp.isoformat(),
            json.dumps(evidence),
            fp_likelihood
        ))
        self.conn.commit()
        
        print(f"    🚨 {corr_severity.value.upper()}: {description}")
    
    def _calculate_false_positive_likelihood(
        self,
        method: CorrelationMethod,
        confidence: float,
        asset_type: str
    ) -> float:
        """Calculate likelihood of false positive (0-100)"""
        
        # Base likelihood on method
        method_fp = {
            CorrelationMethod.EXACT_MATCH: 5.0,
            CorrelationMethod.SUBNET_MATCH: 20.0,
            CorrelationMethod.REGEX_MATCH: 30.0,
            CorrelationMethod.FUZZY_MATCH: 50.0,
            CorrelationMethod.BEHAVIORAL_MATCH: 40.0
        }
        
        fp = method_fp.get(method, 25.0)
        
        # Adjust for confidence
        fp = fp * (100 - confidence) / 100
        
        # Adjust for asset type (some types more prone to FPs)
        if asset_type in ['cloudtrail_event', 'dns_query']:
            fp *= 1.2  # Slightly higher FP rate
        
        return min(100, max(0, fp))
    
    def _generate_recommended_actions(
        self,
        severity: CorrelationSeverity,
        asset_type: str,
        threat_actor: str = None
    ) -> List[str]:
        """Generate recommended actions based on correlation"""
        actions = []
        
        if severity == CorrelationSeverity.CONFIRMED_COMPROMISE:
            actions.append("🔴 IMMEDIATE: Isolate affected asset from network")
            actions.append("🔴 IMMEDIATE: Initiate incident response procedure")
            actions.append("🔴 IMMEDIATE: Capture forensic evidence (memory dump, disk image)")
            actions.append("🔴 IMMEDIATE: Revoke all credentials associated with asset")
            actions.append("🔴 IMMEDIATE: Notify SOC and CISO")
            
            if threat_actor:
                actions.append(f"🔍 INVESTIGATE: Review all activity for indicators of {threat_actor}")
        
        elif severity == CorrelationSeverity.HIGH_CONFIDENCE:
            actions.append("🟠 URGENT: Quarantine asset for investigation")
            actions.append("🟠 URGENT: Analyze network traffic and logs")
            actions.append("🟠 URGENT: Check for lateral movement indicators")
            actions.append("🟠 URGENT: Verify with secondary IoC sources")
        
        elif severity == CorrelationSeverity.MEDIUM_CONFIDENCE:
            actions.append("🟡 INVESTIGATE: Enhanced monitoring of asset")
            actions.append("🟡 INVESTIGATE: Correlate with other security events")
            actions.append("🟡 INVESTIGATE: Verify business justification for activity")
        
        # Asset-specific actions
        if asset_type == "ec2_instance":
            actions.append("📊 Analyze CloudWatch logs and metrics")
            actions.append("📊 Check Systems Manager Session Manager logs")
        elif asset_type == "s3_object":
            actions.append("📦 Enable S3 access logging if not enabled")
            actions.append("📦 Review bucket policies and ACLs")
        
        return actions
    
    def _generate_correlation_report(
        self,
        total_indicators: int,
        total_assets: int
    ) -> IoCCorrelationReport:
        """Generate comprehensive correlation report"""
        
        # Count by severity
        confirmed = sum(1 for c in self.correlations if c.severity == CorrelationSeverity.CONFIRMED_COMPROMISE)
        high = sum(1 for c in self.correlations if c.severity == CorrelationSeverity.HIGH_CONFIDENCE)
        medium = sum(1 for c in self.correlations if c.severity == CorrelationSeverity.MEDIUM_CONFIDENCE)
        low = sum(1 for c in self.correlations if c.severity == CorrelationSeverity.LOW_CONFIDENCE)
        
        # Affected assets
        affected_assets = set(c.asset_id for c in self.correlations)
        
        # Affected asset types
        affected_types = {}
        for c in self.correlations:
            affected_types[c.asset_type] = affected_types.get(c.asset_type, 0) + 1
        
        # Threat actors and campaigns
        threat_actors = set(c.threat_actor for c in self.correlations if c.threat_actor)
        campaigns = set(c.campaign for c in self.correlations if c.campaign)
        
        # Calculate correlation score (0-100, lower is better)
        if total_assets > 0:
            compromise_rate = len(affected_assets) / total_assets * 100
            score = max(0, 100 - compromise_rate)
        else:
            score = 100
        
        # Generate recommendations
        recommendations = []
        if confirmed > 0:
            recommendations.append(f"🔴 CRITICAL: {confirmed} confirmed compromises - execute incident response plan immediately")
        if high > 0:
            recommendations.append(f"🟠 HIGH: {high} high-confidence matches - investigate within 1 hour")
        if len(threat_actors) > 0:
            recommendations.append(f"👥 APT Activity: {len(threat_actors)} threat actors detected: {', '.join(threat_actors)}")
        if len(campaigns) > 0:
            recommendations.append(f"🎪 Active Campaigns: {', '.join(campaigns)}")
        
        recommendations.append("📊 Enable automated response for CONFIRMED_COMPROMISE correlations")
        recommendations.append("🔍 Deploy threat hunting playbooks (Part 3) for detected threat actors")
        
        return IoCCorrelationReport(
            report_id=hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16],
            scan_time=datetime.now(),
            total_indicators_checked=total_indicators,
            total_assets_scanned=total_assets,
            correlations_found=self.correlations,
            confirmed_compromises=confirmed,
            high_confidence_matches=high,
            medium_confidence_matches=medium,
            low_confidence_matches=low,
            affected_assets=affected_assets,
            affected_asset_types=affected_types,
            threat_actors_detected=threat_actors,
            campaigns_detected=campaigns,
            recommended_actions=recommendations,
            correlation_score=int(score)
        )


def main():
    """Example usage"""
    print("=" * 80)
    print("Military-Grade Threat Intelligence Integration - Part 2")
    print("STIX/TAXII Protocol + IoC Correlation Engine")
    print("=" * 80)
    print()
    
    # Initialize STIX/TAXII processor
    stix_processor = STIXTAXIIProcessor()
    
    # Create STIX indicators
    print("📝 Creating STIX 2.1 Indicators...")
    stix_processor.create_stix_indicator(
        indicator_value="192.0.2.1",
        indicator_type="ipv4-addr",
        name="APT28 C2 Server",
        description="Command and control server associated with APT28",
        confidence=100,
        labels=["malicious-activity", "apt28", "c2"],
        kill_chain_phases=[{
            "kill_chain_name": "lockheed-martin-cyber-kill-chain",
            "phase_name": "command-and-control"
        }]
    )
    
    # Create STIX bundle
    bundle = stix_processor.create_stix_bundle()
    print(f"  ✅ Created STIX bundle with {len(bundle['objects'])} objects")
    
    # Initialize correlation engine
    print("\n🔍 Initializing IoC Correlation Engine...")
    correlation_engine = IoCCorrelationEngine()
    
    # Add indicators
    correlation_engine.add_indicator(
        indicator_id="IND-001",
        indicator_type="ip_address",
        indicator_value="192.0.2.1",
        severity="critical",
        confidence=100,
        source="CISA_AIS",
        mitre_techniques=["T1071.001", "T1090"],
        threat_actor="APT28",
        campaign="Operation Ghost"
    )
    
    # Example asset data
    asset_data = {
        'ec2_instances': [
            {
                'id': 'i-1234567890abcdef0',
                'public_ip': '192.0.2.1',
                'private_ip': '10.0.1.5',
                'state': 'running'
            }
        ],
        'cloudtrail_logs': [
            {
                'event_name': 'ConsoleLogin',
                'source_ip': '192.0.2.1',
                'user_identity': {'arn': 'arn:aws:iam::123456789012:user/admin'}
            }
        ]
    }
    
    # Run correlation
    report = correlation_engine.correlate_indicators(asset_data)
    
    # Display results
    print("\n" + "=" * 80)
    print("IOC CORRELATION REPORT - PART 2")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  Indicators Checked: {report.total_indicators_checked}")
    print(f"  Assets Scanned: {report.total_assets_scanned}")
    print(f"  Correlations Found: {len(report.correlations_found)}")
    print(f"\n🚨 Correlations by Severity:")
    print(f"  CONFIRMED COMPROMISES: {report.confirmed_compromises}")
    print(f"  HIGH CONFIDENCE: {report.high_confidence_matches}")
    print(f"  MEDIUM CONFIDENCE: {report.medium_confidence_matches}")
    print(f"  LOW CONFIDENCE: {report.low_confidence_matches}")
    print(f"\n📈 Correlation Score: {report.correlation_score}/100 (higher is better)")
    print(f"\n💡 Recommendations:")
    for rec in report.recommended_actions:
        print(f"  {rec}")
    
    print("\n" + "=" * 80)
    print("✅ Part 2 Complete - STIX/TAXII + IoC Correlation")
    print("📋 Next: Part 3 - MITRE ATT&CK Mapping + Threat Hunting Playbooks")
    print("=" * 80)


if __name__ == "__main__":
    main()
