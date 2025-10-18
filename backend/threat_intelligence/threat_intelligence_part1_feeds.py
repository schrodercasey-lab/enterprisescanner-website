"""
Military-Grade Threat Intelligence Integration - Part 1
========================================================

CISA AIS + DoD Cyber Exchange Integration

COMPLIANCE FRAMEWORKS:
- NIST 800-53 Rev 5: SI-4 (Information System Monitoring), SI-5 (Security Alerts)
- Executive Order 13636: Critical Infrastructure Cybersecurity
- DHS CISA Directive: Automated Indicator Sharing (AIS)
- DoD Cyber Exchange: Threat Intelligence Sharing
- PPD-21: Critical Infrastructure Security

THREAT FEEDS INTEGRATED:
- CISA AIS (Automated Indicator Sharing) - DHS managed
- DoD Cyber Exchange - DoD threat intelligence
- US-CERT National Cyber Awareness System (NCAS)
- CNVD (China National Vulnerability Database)
- CNNVD (China National Vulnerability Database of Information Security)
- AlienVault OTX (Open Threat Exchange)
- Emerging Threats (Proofpoint)
- Abuse.ch (malware tracker)

Part 1 Focus: Threat Feed Ingestion, Aggregation, and Enrichment
"""

import json
import hashlib
import requests
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re


class ThreatFeedSource(Enum):
    """Threat intelligence feed sources"""
    CISA_AIS = "cisa_ais"  # DHS CISA Automated Indicator Sharing
    DOD_CYBER_EXCHANGE = "dod_cyber_exchange"  # DoD Cyber Exchange
    US_CERT = "us_cert"  # US-CERT advisories
    CNVD = "cnvd"  # China National Vulnerability Database
    CNNVD = "cnnvd"  # China National Vulnerability Database (InfoSec)
    ALIENVAULT_OTX = "alienvault_otx"  # AlienVault Open Threat Exchange
    EMERGING_THREATS = "emerging_threats"  # Proofpoint Emerging Threats
    ABUSE_CH = "abuse_ch"  # Abuse.ch malware tracker
    FBI_FLASH = "fbi_flash"  # FBI Private Industry Notification
    NSA_CYBERSECURITY = "nsa_cybersecurity"  # NSA Cybersecurity Advisories
    CISA_ICS_CERT = "cisa_ics_cert"  # ICS-CERT for critical infrastructure
    THREATCONNECT = "threatconnect"  # ThreatConnect platform
    CUSTOM_FEED = "custom_feed"  # Custom organization feeds


class IndicatorType(Enum):
    """Types of threat indicators"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH_MD5 = "md5"
    FILE_HASH_SHA1 = "sha1"
    FILE_HASH_SHA256 = "sha256"
    EMAIL_ADDRESS = "email"
    USER_AGENT = "user_agent"
    SSL_CERT_FINGERPRINT = "ssl_cert"
    MUTEX = "mutex"
    REGISTRY_KEY = "registry_key"
    CVE = "cve"
    YARA_RULE = "yara_rule"


class ThreatSeverity(Enum):
    """Threat severity levels (aligned with DoD)"""
    CRITICAL = "critical"  # Active exploitation, immediate action required
    HIGH = "high"  # Known threat, high likelihood
    MEDIUM = "medium"  # Moderate threat
    LOW = "low"  # Informational
    INFO = "info"  # General awareness


class ConfidenceLevel(Enum):
    """Indicator confidence levels"""
    CONFIRMED = 100  # Verified by authoritative source (CISA, DoD, FBI)
    HIGH = 85  # Multiple independent sources
    MEDIUM = 60  # Single reliable source
    LOW = 40  # Unverified or dated
    UNKNOWN = 0  # No confidence data


class ThreatCategory(Enum):
    """Threat categories (MITRE-aligned)"""
    APT = "advanced_persistent_threat"
    RANSOMWARE = "ransomware"
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    C2_SERVER = "command_and_control"
    EXPLOIT_KIT = "exploit_kit"
    CRYPTOMINING = "cryptomining"
    DATA_EXFILTRATION = "data_exfiltration"
    VULNERABILITY = "vulnerability"
    INSIDER_THREAT = "insider_threat"
    SUPPLY_CHAIN = "supply_chain_compromise"


@dataclass
class ThreatIndicator:
    """Individual threat indicator from feeds"""
    indicator_id: str
    indicator_type: IndicatorType
    indicator_value: str  # IP, domain, hash, etc.
    source: ThreatFeedSource
    severity: ThreatSeverity
    confidence: ConfidenceLevel
    category: ThreatCategory
    first_seen: datetime
    last_seen: datetime
    description: str
    tags: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)  # T1071, T1059, etc.
    associated_malware: List[str] = field(default_factory=list)
    associated_campaigns: List[str] = field(default_factory=list)
    associated_actors: List[str] = field(default_factory=list)  # APT28, Lazarus, etc.
    killchain_phase: Optional[str] = None  # Lockheed Martin Cyber Kill Chain
    ttl_hours: int = 72  # Time to live (hours)
    expires_at: Optional[datetime] = None
    enrichment_data: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatFeedMetrics:
    """Metrics for threat feed health"""
    feed_source: ThreatFeedSource
    last_update: datetime
    indicators_received: int
    indicators_valid: int
    indicators_expired: int
    average_confidence: float
    feed_latency_seconds: float
    feed_available: bool
    error_count: int
    last_error: Optional[str] = None


@dataclass
class ThreatIntelligenceReport:
    """Aggregated threat intelligence report"""
    report_id: str
    report_time: datetime
    total_indicators: int
    indicators_by_type: Dict[IndicatorType, int]
    indicators_by_severity: Dict[ThreatSeverity, int]
    indicators_by_source: Dict[ThreatFeedSource, int]
    active_campaigns: List[str]
    active_threat_actors: List[str]
    trending_malware: List[str]
    feed_metrics: List[ThreatFeedMetrics]
    recommendations: List[str]
    critical_alerts: List[ThreatIndicator]


class ThreatFeedAggregator:
    """
    Military-grade threat intelligence feed aggregator
    Ingests, normalizes, and enriches threat indicators from multiple sources
    """
    
    # CISA AIS feed endpoints (example - real endpoints require authentication)
    FEED_URLS = {
        ThreatFeedSource.CISA_AIS: "https://api.cisa.gov/taxii/discovery",
        ThreatFeedSource.US_CERT: "https://www.us-cert.gov/ncas/current-activity.xml",
        ThreatFeedSource.ALIENVAULT_OTX: "https://otx.alienvault.com/api/v1/pulses/subscribed",
        ThreatFeedSource.ABUSE_CH: "https://urlhaus-api.abuse.ch/v1/urls/recent/",
        ThreatFeedSource.EMERGING_THREATS: "https://rules.emergingthreats.net/",
    }
    
    # Known APT groups (partial list)
    APT_GROUPS = {
        'APT1': {'country': 'China', 'aka': ['Comment Crew', 'PLA Unit 61398']},
        'APT28': {'country': 'Russia', 'aka': ['Fancy Bear', 'Sofacy', 'Pawn Storm']},
        'APT29': {'country': 'Russia', 'aka': ['Cozy Bear', 'The Dukes']},
        'APT33': {'country': 'Iran', 'aka': ['Elfin', 'Holmium']},
        'APT38': {'country': 'North Korea', 'aka': ['Lazarus Group', 'Hidden Cobra']},
        'APT40': {'country': 'China', 'aka': ['Leviathan', 'TEMP.Periscope']},
        'APT41': {'country': 'China', 'aka': ['Winnti', 'Barium']},
        'Lazarus': {'country': 'North Korea', 'aka': ['Hidden Cobra', 'Guardians of Peace']},
        'FIN7': {'country': 'Unknown', 'aka': ['Carbanak']},
        'FIN8': {'country': 'Unknown', 'aka': []},
        'Kimsuky': {'country': 'North Korea', 'aka': ['Thallium', 'Black Banshee']},
        'Turla': {'country': 'Russia', 'aka': ['Venomous Bear', 'Waterbug']},
    }
    
    # Cyber Kill Chain phases
    KILLCHAIN_PHASES = [
        'reconnaissance',
        'weaponization',
        'delivery',
        'exploitation',
        'installation',
        'command_and_control',
        'actions_on_objectives'
    ]
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize threat feed aggregator
        
        Args:
            api_keys: Dictionary of API keys for various feeds
                      {'cisa_ais': 'key', 'alienvault': 'key', etc.}
        """
        self.api_keys = api_keys or {}
        self.indicators: List[ThreatIndicator] = []
        self.feed_metrics: List[ThreatFeedMetrics] = []
        self.indicator_cache: Dict[str, ThreatIndicator] = {}
    
    def ingest_all_feeds(self) -> ThreatIntelligenceReport:
        """Ingest indicators from all configured threat feeds"""
        print("🌐 Starting Threat Intelligence Feed Ingestion...")
        
        self.indicators = []
        self.feed_metrics = []
        
        # Ingest from each feed source
        if 'cisa_ais' in self.api_keys:
            self.ingest_cisa_ais()
        
        if 'dod_cyber_exchange' in self.api_keys:
            self.ingest_dod_cyber_exchange()
        
        if 'us_cert' in self.api_keys:
            self.ingest_us_cert()
        
        if 'alienvault' in self.api_keys:
            self.ingest_alienvault_otx()
        
        if 'abuse_ch' in self.api_keys:
            self.ingest_abuse_ch()
        
        # Deduplicate and enrich indicators
        self.deduplicate_indicators()
        self.enrich_indicators()
        
        # Generate report
        return self._generate_report()
    
    def ingest_cisa_ais(self):
        """
        Ingest indicators from CISA AIS (Automated Indicator Sharing)
        
        CISA AIS is a DHS program that enables real-time exchange of
        machine-readable cyber threat indicators and defensive measures
        between the federal government and the private sector.
        
        Requires: CISA AIS account and authentication certificate
        """
        print("  🏛️  Ingesting CISA AIS (Automated Indicator Sharing)...")
        
        start_time = datetime.now()
        indicators_received = 0
        indicators_valid = 0
        error = None
        
        try:
            # CISA AIS uses TAXII (Trusted Automated eXchange of Indicator Information)
            # This would connect to CISA's TAXII server
            
            # Example indicators (in production, these would come from TAXII feed)
            example_indicators = [
                {
                    'type': 'ipv4',
                    'value': '192.0.2.1',
                    'severity': 'critical',
                    'confidence': 100,
                    'description': 'C2 server associated with APT28 (Fancy Bear)',
                    'tags': ['apt28', 'russia', 'c2'],
                    'mitre_techniques': ['T1071.001', 'T1090'],
                    'malware': ['Sofacy', 'X-Agent'],
                    'campaign': 'Operation Ghost',
                    'actor': 'APT28',
                    'first_seen': '2025-10-15T10:00:00Z',
                    'last_seen': '2025-10-17T08:00:00Z',
                },
                {
                    'type': 'domain',
                    'value': 'malicious-c2.example.com',
                    'severity': 'high',
                    'confidence': 85,
                    'description': 'Phishing domain targeting DoD contractors',
                    'tags': ['phishing', 'dod', 'defense-industrial-base'],
                    'mitre_techniques': ['T1566.002'],
                    'campaign': 'Operation Sidewinder',
                    'first_seen': '2025-10-16T14:00:00Z',
                    'last_seen': '2025-10-17T09:00:00Z',
                },
                {
                    'type': 'sha256',
                    'value': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                    'severity': 'critical',
                    'confidence': 100,
                    'description': 'Ransomware payload - LockBit 3.0',
                    'tags': ['ransomware', 'lockbit', 'file-encryption'],
                    'mitre_techniques': ['T1486', 'T1490'],
                    'malware': ['LockBit 3.0'],
                    'first_seen': '2025-10-14T06:00:00Z',
                    'last_seen': '2025-10-17T10:00:00Z',
                }
            ]
            
            for indicator_data in example_indicators:
                indicators_received += 1
                
                # Parse and normalize indicator
                indicator = self._parse_cisa_indicator(indicator_data)
                if indicator:
                    self.indicators.append(indicator)
                    indicators_valid += 1
        
        except Exception as e:
            error = str(e)
            print(f"  ❌ Error ingesting CISA AIS: {e}")
        
        # Record metrics
        latency = (datetime.now() - start_time).total_seconds()
        self.feed_metrics.append(ThreatFeedMetrics(
            feed_source=ThreatFeedSource.CISA_AIS,
            last_update=datetime.now(),
            indicators_received=indicators_received,
            indicators_valid=indicators_valid,
            indicators_expired=0,
            average_confidence=95.0,  # CISA has high confidence
            feed_latency_seconds=latency,
            feed_available=error is None,
            error_count=1 if error else 0,
            last_error=error
        ))
        
        print(f"    ✅ CISA AIS: {indicators_valid}/{indicators_received} indicators ingested")
    
    def ingest_dod_cyber_exchange(self):
        """
        Ingest indicators from DoD Cyber Exchange
        
        DoD Cyber Exchange provides cybersecurity tools, resources, and
        threat intelligence for DoD personnel and defense contractors.
        
        Requires: DoD CAC/PIV authentication
        """
        print("  🪖  Ingesting DoD Cyber Exchange...")
        
        start_time = datetime.now()
        indicators_received = 0
        indicators_valid = 0
        error = None
        
        try:
            # DoD Cyber Exchange requires CAC/PIV authentication
            # Example indicators (in production, these would come from authenticated API)
            
            example_indicators = [
                {
                    'type': 'ipv4',
                    'value': '198.51.100.1',
                    'severity': 'critical',
                    'confidence': 100,
                    'description': 'APT40 (Leviathan) infrastructure targeting DoD networks',
                    'tags': ['apt40', 'china', 'maritime', 'espionage'],
                    'mitre_techniques': ['T1566.001', 'T1078', 'T1098'],
                    'actor': 'APT40',
                    'campaign': 'Operation Ephemeral Hydra',
                    'classification': 'UNCLASSIFIED//FOUO',
                    'first_seen': '2025-10-10T00:00:00Z',
                    'last_seen': '2025-10-17T00:00:00Z',
                },
                {
                    'type': 'domain',
                    'value': 'login-portal-defense.mil.fake.com',
                    'severity': 'high',
                    'confidence': 100,
                    'description': 'Typosquatting domain impersonating DoD portal',
                    'tags': ['phishing', 'credential-harvesting', 'typosquatting'],
                    'mitre_techniques': ['T1566.002', 'T1598.003'],
                    'campaign': 'DoD Credential Harvesting',
                    'classification': 'UNCLASSIFIED',
                    'first_seen': '2025-10-16T00:00:00Z',
                    'last_seen': '2025-10-17T00:00:00Z',
                },
            ]
            
            for indicator_data in example_indicators:
                indicators_received += 1
                
                indicator = self._parse_dod_indicator(indicator_data)
                if indicator:
                    self.indicators.append(indicator)
                    indicators_valid += 1
        
        except Exception as e:
            error = str(e)
            print(f"  ❌ Error ingesting DoD Cyber Exchange: {e}")
        
        # Record metrics
        latency = (datetime.now() - start_time).total_seconds()
        self.feed_metrics.append(ThreatFeedMetrics(
            feed_source=ThreatFeedSource.DOD_CYBER_EXCHANGE,
            last_update=datetime.now(),
            indicators_received=indicators_received,
            indicators_valid=indicators_valid,
            indicators_expired=0,
            average_confidence=98.0,  # DoD has very high confidence
            feed_latency_seconds=latency,
            feed_available=error is None,
            error_count=1 if error else 0,
            last_error=error
        ))
        
        print(f"    ✅ DoD Cyber Exchange: {indicators_valid}/{indicators_received} indicators ingested")
    
    def ingest_us_cert(self):
        """Ingest advisories from US-CERT"""
        print("  🇺🇸 Ingesting US-CERT Advisories...")
        
        start_time = datetime.now()
        indicators_received = 0
        indicators_valid = 0
        error = None
        
        try:
            # US-CERT publishes alerts and advisories
            example_indicators = [
                {
                    'type': 'cve',
                    'value': 'CVE-2025-12345',
                    'severity': 'critical',
                    'confidence': 100,
                    'description': 'Critical RCE in widely-used Apache component',
                    'tags': ['apache', 'rce', 'zero-day'],
                    'mitre_techniques': ['T1190'],
                    'first_seen': '2025-10-15T00:00:00Z',
                    'last_seen': '2025-10-17T00:00:00Z',
                    'cvss_score': 9.8,
                    'cve_url': 'https://nvd.nist.gov/vuln/detail/CVE-2025-12345'
                }
            ]
            
            for indicator_data in example_indicators:
                indicators_received += 1
                
                indicator = self._parse_us_cert_indicator(indicator_data)
                if indicator:
                    self.indicators.append(indicator)
                    indicators_valid += 1
        
        except Exception as e:
            error = str(e)
            print(f"  ❌ Error ingesting US-CERT: {e}")
        
        # Record metrics
        latency = (datetime.now() - start_time).total_seconds()
        self.feed_metrics.append(ThreatFeedMetrics(
            feed_source=ThreatFeedSource.US_CERT,
            last_update=datetime.now(),
            indicators_received=indicators_received,
            indicators_valid=indicators_valid,
            indicators_expired=0,
            average_confidence=95.0,
            feed_latency_seconds=latency,
            feed_available=error is None,
            error_count=1 if error else 0,
            last_error=error
        ))
        
        print(f"    ✅ US-CERT: {indicators_valid}/{indicators_received} indicators ingested")
    
    def ingest_alienvault_otx(self):
        """Ingest indicators from AlienVault OTX"""
        print("  👽 Ingesting AlienVault OTX...")
        
        start_time = datetime.now()
        indicators_received = 0
        indicators_valid = 0
        error = None
        
        try:
            # AlienVault OTX is a community-driven threat intelligence platform
            example_indicators = [
                {
                    'type': 'ipv4',
                    'value': '203.0.113.1',
                    'severity': 'medium',
                    'confidence': 60,
                    'description': 'Suspicious scanning activity',
                    'tags': ['scanning', 'reconnaissance'],
                    'mitre_techniques': ['T1046'],
                    'first_seen': '2025-10-16T00:00:00Z',
                    'last_seen': '2025-10-17T00:00:00Z',
                }
            ]
            
            for indicator_data in example_indicators:
                indicators_received += 1
                
                indicator = self._parse_alienvault_indicator(indicator_data)
                if indicator:
                    self.indicators.append(indicator)
                    indicators_valid += 1
        
        except Exception as e:
            error = str(e)
            print(f"  ❌ Error ingesting AlienVault OTX: {e}")
        
        # Record metrics
        latency = (datetime.now() - start_time).total_seconds()
        self.feed_metrics.append(ThreatFeedMetrics(
            feed_source=ThreatFeedSource.ALIENVAULT_OTX,
            last_update=datetime.now(),
            indicators_received=indicators_received,
            indicators_valid=indicators_valid,
            indicators_expired=0,
            average_confidence=65.0,  # Community feeds have lower confidence
            feed_latency_seconds=latency,
            feed_available=error is None,
            error_count=1 if error else 0,
            last_error=error
        ))
        
        print(f"    ✅ AlienVault OTX: {indicators_valid}/{indicators_received} indicators ingested")
    
    def ingest_abuse_ch(self):
        """Ingest indicators from Abuse.ch"""
        print("  🔗 Ingesting Abuse.ch (URLhaus, MalwareBazaar)...")
        
        start_time = datetime.now()
        indicators_received = 0
        indicators_valid = 0
        error = None
        
        try:
            # Abuse.ch provides malware URLs and samples
            example_indicators = [
                {
                    'type': 'url',
                    'value': 'http://malicious-payload.example.com/payload.exe',
                    'severity': 'high',
                    'confidence': 85,
                    'description': 'Emotet downloader URL',
                    'tags': ['emotet', 'malware', 'downloader'],
                    'mitre_techniques': ['T1566.001', 'T1204.002'],
                    'malware': ['Emotet'],
                    'first_seen': '2025-10-17T00:00:00Z',
                    'last_seen': '2025-10-17T10:00:00Z',
                }
            ]
            
            for indicator_data in example_indicators:
                indicators_received += 1
                
                indicator = self._parse_abuse_ch_indicator(indicator_data)
                if indicator:
                    self.indicators.append(indicator)
                    indicators_valid += 1
        
        except Exception as e:
            error = str(e)
            print(f"  ❌ Error ingesting Abuse.ch: {e}")
        
        # Record metrics
        latency = (datetime.now() - start_time).total_seconds()
        self.feed_metrics.append(ThreatFeedMetrics(
            feed_source=ThreatFeedSource.ABUSE_CH,
            last_update=datetime.now(),
            indicators_received=indicators_received,
            indicators_valid=indicators_valid,
            indicators_expired=0,
            average_confidence=80.0,
            feed_latency_seconds=latency,
            feed_available=error is None,
            error_count=1 if error else 0,
            last_error=error
        ))
        
        print(f"    ✅ Abuse.ch: {indicators_valid}/{indicators_received} indicators ingested")
    
    def _parse_cisa_indicator(self, data: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Parse CISA AIS indicator format"""
        try:
            indicator_type = self._map_indicator_type(data['type'])
            severity = ThreatSeverity(data.get('severity', 'medium').lower())
            confidence = ConfidenceLevel.CONFIRMED  # CISA is authoritative
            
            # Determine category
            category = ThreatCategory.MALWARE
            if 'phishing' in data.get('tags', []):
                category = ThreatCategory.PHISHING
            elif 'ransomware' in data.get('tags', []):
                category = ThreatCategory.RANSOMWARE
            elif 'c2' in data.get('tags', []):
                category = ThreatCategory.C2_SERVER
            
            indicator_id = hashlib.sha256(
                f"{data['value']}-{data.get('first_seen', '')}".encode()
            ).hexdigest()[:16]
            
            return ThreatIndicator(
                indicator_id=f"CISA-{indicator_id}",
                indicator_type=indicator_type,
                indicator_value=data['value'],
                source=ThreatFeedSource.CISA_AIS,
                severity=severity,
                confidence=confidence,
                category=category,
                first_seen=datetime.fromisoformat(data['first_seen'].replace('Z', '+00:00')),
                last_seen=datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')),
                description=data.get('description', ''),
                tags=data.get('tags', []),
                mitre_techniques=data.get('mitre_techniques', []),
                associated_malware=data.get('malware', []),
                associated_campaigns=[data.get('campaign')] if data.get('campaign') else [],
                associated_actors=[data.get('actor')] if data.get('actor') else [],
                ttl_hours=168,  # 7 days for CISA indicators
                expires_at=datetime.now() + timedelta(hours=168),
                raw_data=data
            )
        except Exception as e:
            print(f"    ⚠️  Error parsing CISA indicator: {e}")
            return None
    
    def _parse_dod_indicator(self, data: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Parse DoD Cyber Exchange indicator format"""
        try:
            indicator_type = self._map_indicator_type(data['type'])
            severity = ThreatSeverity(data.get('severity', 'high').lower())
            confidence = ConfidenceLevel.CONFIRMED  # DoD is authoritative
            
            category = ThreatCategory.APT
            if 'phishing' in data.get('tags', []):
                category = ThreatCategory.PHISHING
            
            indicator_id = hashlib.sha256(
                f"{data['value']}-{data.get('first_seen', '')}".encode()
            ).hexdigest()[:16]
            
            return ThreatIndicator(
                indicator_id=f"DOD-{indicator_id}",
                indicator_type=indicator_type,
                indicator_value=data['value'],
                source=ThreatFeedSource.DOD_CYBER_EXCHANGE,
                severity=severity,
                confidence=confidence,
                category=category,
                first_seen=datetime.fromisoformat(data['first_seen'].replace('Z', '+00:00')),
                last_seen=datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')),
                description=data.get('description', ''),
                tags=data.get('tags', []),
                mitre_techniques=data.get('mitre_techniques', []),
                associated_actors=[data.get('actor')] if data.get('actor') else [],
                associated_campaigns=[data.get('campaign')] if data.get('campaign') else [],
                ttl_hours=336,  # 14 days for DoD indicators
                expires_at=datetime.now() + timedelta(hours=336),
                enrichment_data={'classification': data.get('classification', 'UNCLASSIFIED')},
                raw_data=data
            )
        except Exception as e:
            print(f"    ⚠️  Error parsing DoD indicator: {e}")
            return None
    
    def _parse_us_cert_indicator(self, data: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Parse US-CERT indicator format"""
        try:
            indicator_type = self._map_indicator_type(data['type'])
            severity = ThreatSeverity(data.get('severity', 'medium').lower())
            
            indicator_id = hashlib.sha256(data['value'].encode()).hexdigest()[:16]
            
            return ThreatIndicator(
                indicator_id=f"USCERT-{indicator_id}",
                indicator_type=indicator_type,
                indicator_value=data['value'],
                source=ThreatFeedSource.US_CERT,
                severity=severity,
                confidence=ConfidenceLevel.CONFIRMED,
                category=ThreatCategory.VULNERABILITY,
                first_seen=datetime.fromisoformat(data['first_seen'].replace('Z', '+00:00')),
                last_seen=datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')),
                description=data.get('description', ''),
                tags=data.get('tags', []),
                mitre_techniques=data.get('mitre_techniques', []),
                ttl_hours=720,  # 30 days for CVEs
                expires_at=datetime.now() + timedelta(hours=720),
                enrichment_data={
                    'cvss_score': data.get('cvss_score'),
                    'cve_url': data.get('cve_url')
                },
                raw_data=data
            )
        except Exception as e:
            print(f"    ⚠️  Error parsing US-CERT indicator: {e}")
            return None
    
    def _parse_alienvault_indicator(self, data: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Parse AlienVault OTX indicator format"""
        try:
            indicator_type = self._map_indicator_type(data['type'])
            severity = ThreatSeverity(data.get('severity', 'medium').lower())
            
            indicator_id = hashlib.sha256(data['value'].encode()).hexdigest()[:16]
            
            return ThreatIndicator(
                indicator_id=f"OTX-{indicator_id}",
                indicator_type=indicator_type,
                indicator_value=data['value'],
                source=ThreatFeedSource.ALIENVAULT_OTX,
                severity=severity,
                confidence=ConfidenceLevel.MEDIUM,  # Community source
                category=ThreatCategory.MALWARE,
                first_seen=datetime.fromisoformat(data['first_seen'].replace('Z', '+00:00')),
                last_seen=datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')),
                description=data.get('description', ''),
                tags=data.get('tags', []),
                mitre_techniques=data.get('mitre_techniques', []),
                ttl_hours=24,  # 24 hours for community indicators
                expires_at=datetime.now() + timedelta(hours=24),
                raw_data=data
            )
        except Exception as e:
            print(f"    ⚠️  Error parsing AlienVault indicator: {e}")
            return None
    
    def _parse_abuse_ch_indicator(self, data: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Parse Abuse.ch indicator format"""
        try:
            indicator_type = self._map_indicator_type(data['type'])
            severity = ThreatSeverity(data.get('severity', 'high').lower())
            
            indicator_id = hashlib.sha256(data['value'].encode()).hexdigest()[:16]
            
            return ThreatIndicator(
                indicator_id=f"ABCH-{indicator_id}",
                indicator_type=indicator_type,
                indicator_value=data['value'],
                source=ThreatFeedSource.ABUSE_CH,
                severity=severity,
                confidence=ConfidenceLevel.HIGH,  # Abuse.ch is reliable
                category=ThreatCategory.MALWARE,
                first_seen=datetime.fromisoformat(data['first_seen'].replace('Z', '+00:00')),
                last_seen=datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')),
                description=data.get('description', ''),
                tags=data.get('tags', []),
                mitre_techniques=data.get('mitre_techniques', []),
                associated_malware=data.get('malware', []),
                ttl_hours=48,  # 48 hours for malware URLs
                expires_at=datetime.now() + timedelta(hours=48),
                raw_data=data
            )
        except Exception as e:
            print(f"    ⚠️  Error parsing Abuse.ch indicator: {e}")
            return None
    
    def _map_indicator_type(self, type_str: str) -> IndicatorType:
        """Map feed-specific type strings to IndicatorType enum"""
        type_mapping = {
            'ipv4': IndicatorType.IP_ADDRESS,
            'ip': IndicatorType.IP_ADDRESS,
            'domain': IndicatorType.DOMAIN,
            'url': IndicatorType.URL,
            'md5': IndicatorType.FILE_HASH_MD5,
            'sha1': IndicatorType.FILE_HASH_SHA1,
            'sha256': IndicatorType.FILE_HASH_SHA256,
            'email': IndicatorType.EMAIL_ADDRESS,
            'cve': IndicatorType.CVE,
        }
        return type_mapping.get(type_str.lower(), IndicatorType.IP_ADDRESS)
    
    def deduplicate_indicators(self):
        """Remove duplicate indicators, keeping highest confidence version"""
        print("  🔄 Deduplicating indicators...")
        
        # Group by indicator value
        indicator_map: Dict[str, List[ThreatIndicator]] = {}
        for indicator in self.indicators:
            key = f"{indicator.indicator_type.value}:{indicator.indicator_value}"
            if key not in indicator_map:
                indicator_map[key] = []
            indicator_map[key].append(indicator)
        
        # Keep highest confidence indicator for each value
        deduplicated = []
        for key, duplicates in indicator_map.items():
            if len(duplicates) == 1:
                deduplicated.append(duplicates[0])
            else:
                # Sort by confidence, then by source authority
                sorted_indicators = sorted(
                    duplicates,
                    key=lambda x: (x.confidence.value, self._source_priority(x.source)),
                    reverse=True
                )
                best = sorted_indicators[0]
                
                # Merge tags and techniques from all duplicates
                all_tags = set(best.tags)
                all_techniques = set(best.mitre_techniques)
                for dup in sorted_indicators[1:]:
                    all_tags.update(dup.tags)
                    all_techniques.update(dup.mitre_techniques)
                
                best.tags = list(all_tags)
                best.mitre_techniques = list(all_techniques)
                
                deduplicated.append(best)
        
        original_count = len(self.indicators)
        self.indicators = deduplicated
        print(f"    ✅ Deduplicated: {original_count} → {len(self.indicators)} indicators")
    
    def _source_priority(self, source: ThreatFeedSource) -> int:
        """Return priority score for source (higher = more authoritative)"""
        priorities = {
            ThreatFeedSource.CISA_AIS: 100,
            ThreatFeedSource.DOD_CYBER_EXCHANGE: 95,
            ThreatFeedSource.FBI_FLASH: 90,
            ThreatFeedSource.NSA_CYBERSECURITY: 90,
            ThreatFeedSource.US_CERT: 85,
            ThreatFeedSource.CISA_ICS_CERT: 80,
            ThreatFeedSource.ABUSE_CH: 70,
            ThreatFeedSource.EMERGING_THREATS: 65,
            ThreatFeedSource.ALIENVAULT_OTX: 50,
            ThreatFeedSource.CNVD: 40,
            ThreatFeedSource.CNNVD: 40,
        }
        return priorities.get(source, 0)
    
    def enrich_indicators(self):
        """Enrich indicators with additional context"""
        print("  💎 Enriching indicators with context...")
        
        for indicator in self.indicators:
            # Enrich with APT group information
            for actor in indicator.associated_actors:
                if actor in self.APT_GROUPS:
                    indicator.enrichment_data['apt_details'] = self.APT_GROUPS[actor]
            
            # Assign kill chain phase based on MITRE techniques
            if indicator.mitre_techniques:
                indicator.killchain_phase = self._infer_killchain_phase(indicator.mitre_techniques)
        
        print(f"    ✅ Enriched {len(self.indicators)} indicators")
    
    def _infer_killchain_phase(self, techniques: List[str]) -> str:
        """Infer kill chain phase from MITRE ATT&CK techniques"""
        # Simplified mapping (in production, use full MITRE ATT&CK framework)
        if any(t.startswith('T1046') or t.startswith('T1595') for t in techniques):
            return 'reconnaissance'
        elif any(t.startswith('T1566') or t.startswith('T1091') for t in techniques):
            return 'delivery'
        elif any(t.startswith('T1190') or t.startswith('T1203') for t in techniques):
            return 'exploitation'
        elif any(t.startswith('T1071') or t.startswith('T1090') for t in techniques):
            return 'command_and_control'
        elif any(t.startswith('T1486') or t.startswith('T1567') for t in techniques):
            return 'actions_on_objectives'
        else:
            return 'unknown'
    
    def _generate_report(self) -> ThreatIntelligenceReport:
        """Generate comprehensive threat intelligence report"""
        
        # Count indicators by type
        indicators_by_type = {}
        for ind_type in IndicatorType:
            count = sum(1 for i in self.indicators if i.indicator_type == ind_type)
            if count > 0:
                indicators_by_type[ind_type] = count
        
        # Count indicators by severity
        indicators_by_severity = {}
        for severity in ThreatSeverity:
            count = sum(1 for i in self.indicators if i.severity == severity)
            if count > 0:
                indicators_by_severity[severity] = count
        
        # Count indicators by source
        indicators_by_source = {}
        for source in ThreatFeedSource:
            count = sum(1 for i in self.indicators if i.source == source)
            if count > 0:
                indicators_by_source[source] = count
        
        # Extract active campaigns and actors
        active_campaigns = list(set(
            campaign
            for ind in self.indicators
            for campaign in ind.associated_campaigns
        ))
        
        active_threat_actors = list(set(
            actor
            for ind in self.indicators
            for actor in ind.associated_actors
        ))
        
        # Extract trending malware
        trending_malware = list(set(
            malware
            for ind in self.indicators
            for malware in ind.associated_malware
        ))
        
        # Get critical alerts
        critical_alerts = [
            ind for ind in self.indicators
            if ind.severity == ThreatSeverity.CRITICAL
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return ThreatIntelligenceReport(
            report_id=hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16],
            report_time=datetime.now(),
            total_indicators=len(self.indicators),
            indicators_by_type=indicators_by_type,
            indicators_by_severity=indicators_by_severity,
            indicators_by_source=indicators_by_source,
            active_campaigns=active_campaigns,
            active_threat_actors=active_threat_actors,
            trending_malware=trending_malware,
            feed_metrics=self.feed_metrics,
            recommendations=recommendations,
            critical_alerts=critical_alerts
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        critical_count = sum(1 for i in self.indicators if i.severity == ThreatSeverity.CRITICAL)
        if critical_count > 0:
            recommendations.append(f"🔴 CRITICAL: {critical_count} critical indicators detected - immediate action required")
        
        # Check for APT activity
        apt_actors = [a for i in self.indicators for a in i.associated_actors if 'APT' in a]
        if apt_actors:
            recommendations.append(f"⚠️  APT Activity: {len(set(apt_actors))} APT groups detected - enable enhanced monitoring")
        
        # Check for ransomware
        ransomware_count = sum(1 for i in self.indicators if i.category == ThreatCategory.RANSOMWARE)
        if ransomware_count > 0:
            recommendations.append(f"💀 Ransomware: {ransomware_count} ransomware indicators - verify backups and isolation procedures")
        
        recommendations.append("📊 Enable automated blocking of CISA AIS and DoD indicators in firewall/IDS/IPS")
        recommendations.append("🔍 Correlate indicators with internal logs using Part 2 (IoC Correlation Engine)")
        recommendations.append("🎯 Activate threat hunting playbooks from Part 3 for detected APT groups")
        
        return recommendations


def main():
    """Example usage"""
    print("=" * 80)
    print("Military-Grade Threat Intelligence Integration - Part 1")
    print("CISA AIS + DoD Cyber Exchange Feed Aggregation")
    print("=" * 80)
    print()
    
    # Initialize aggregator with API keys
    aggregator = ThreatFeedAggregator(api_keys={
        'cisa_ais': 'DEMO_KEY',
        'dod_cyber_exchange': 'DEMO_KEY',
        'us_cert': 'DEMO_KEY',
        'alienvault': 'DEMO_KEY',
        'abuse_ch': 'DEMO_KEY'
    })
    
    # Ingest all feeds
    report = aggregator.ingest_all_feeds()
    
    # Display results
    print("\n" + "=" * 80)
    print("THREAT INTELLIGENCE REPORT - PART 1")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  Total Indicators: {report.total_indicators}")
    print(f"\n🎯 Indicators by Type:")
    for ind_type, count in report.indicators_by_type.items():
        print(f"    {ind_type.value}: {count}")
    print(f"\n⚠️  Indicators by Severity:")
    for severity, count in report.indicators_by_severity.items():
        print(f"    {severity.value.upper()}: {count}")
    print(f"\n📡 Indicators by Source:")
    for source, count in report.indicators_by_source.items():
        print(f"    {source.value}: {count}")
    print(f"\n🎪 Active Campaigns: {', '.join(report.active_campaigns) if report.active_campaigns else 'None'}")
    print(f"👥 Active Threat Actors: {', '.join(report.active_threat_actors) if report.active_threat_actors else 'None'}")
    print(f"🦠 Trending Malware: {', '.join(report.trending_malware) if report.trending_malware else 'None'}")
    print(f"\n🚨 Critical Alerts: {len(report.critical_alerts)}")
    if report.critical_alerts:
        for alert in report.critical_alerts[:3]:  # Show first 3
            print(f"    - {alert.indicator_value}: {alert.description}")
    print(f"\n💡 Recommendations:")
    for rec in report.recommendations:
        print(f"    {rec}")
    
    print("\n" + "=" * 80)
    print("✅ Part 1 Complete - Threat Feed Aggregation")
    print("📋 Next: Part 2 - STIX/TAXII Protocol + IoC Correlation Engine")
    print("=" * 80)


if __name__ == "__main__":
    main()
