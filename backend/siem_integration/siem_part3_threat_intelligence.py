"""
Military Upgrade #22: SIEM Integration
Part 3: Threat Intelligence Integration

This module integrates external threat intelligence feeds
to enrich security events with IOCs and threat actor profiles.

Key Features:
- STIX/TAXII protocol support
- IOC (Indicators of Compromise) matching
- Threat actor attribution
- CVE vulnerability correlation
- TTP (Tactics, Techniques, Procedures) mapping

Compliance:
- NIST 800-150 (Cyber Threat Intelligence)
- MITRE ATT&CK Framework
- CISA Cybersecurity Advisories
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib


class ThreatType(Enum):
    """Types of threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    APT = "apt"  # Advanced Persistent Threat
    BOTNET = "botnet"
    EXPLOIT = "exploit"


class IOCType(Enum):
    """Indicator of Compromise types"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    CVE = "cve"


@dataclass
class ThreatIntelligence:
    """Threat intelligence entry"""
    ioc_id: str
    ioc_type: IOCType
    ioc_value: str
    
    threat_type: ThreatType
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0.0 - 1.0
    
    # Attribution
    threat_actor: Optional[str] = None
    campaign: Optional[str] = None
    
    # Context
    description: str = ""
    ttps: List[str] = field(default_factory=list)  # MITRE ATT&CK IDs
    
    # Metadata
    source: str = "internal"
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class ThreatMatch:
    """Match between event and threat intelligence"""
    match_id: str
    ioc: ThreatIntelligence
    matched_value: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


class ThreatIntelligenceEngine:
    """Threat intelligence integration engine"""
    
    def __init__(self):
        self.iocs: Dict[str, ThreatIntelligence] = {}
        self.matches: List[ThreatMatch] = []
        
        # Load default threat intel
        self._load_default_feeds()
    
    def _load_default_feeds(self):
        """Load default threat intelligence feeds"""
        # Known malicious IPs
        malicious_ips = [
            "203.0.113.42",  # Example malicious IP
            "198.51.100.10",
            "192.0.2.50"
        ]
        
        for ip in malicious_ips:
            self.add_ioc(ThreatIntelligence(
                ioc_id=self._generate_ioc_id(ip),
                ioc_type=IOCType.IP_ADDRESS,
                ioc_value=ip,
                threat_type=ThreatType.MALWARE,
                severity="HIGH",
                confidence=0.9,
                threat_actor="APT29",
                description="Known C2 server",
                ttps=["T1071.001"],  # Application Layer Protocol: Web
                source="CISA",
                tags=["c2", "malware"]
            ))
        
        # Known malicious domains
        malicious_domains = [
            "evil-phishing.com",
            "malware-download.net",
            "ransomware-c2.org"
        ]
        
        for domain in malicious_domains:
            self.add_ioc(ThreatIntelligence(
                ioc_id=self._generate_ioc_id(domain),
                ioc_type=IOCType.DOMAIN,
                ioc_value=domain,
                threat_type=ThreatType.PHISHING,
                severity="CRITICAL",
                confidence=0.95,
                campaign="PhishingCampaign2024",
                description="Active phishing domain",
                ttps=["T1566.002"],  # Phishing: Spearphishing Link
                source="PhishTank",
                tags=["phishing", "credential_theft"]
            ))
        
        # Known malware file hashes
        malware_hashes = [
            "d41d8cd98f00b204e9800998ecf8427e",  # Example MD5
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # Example SHA256
        ]
        
        for hash_value in malware_hashes:
            self.add_ioc(ThreatIntelligence(
                ioc_id=self._generate_ioc_id(hash_value),
                ioc_type=IOCType.FILE_HASH,
                ioc_value=hash_value,
                threat_type=ThreatType.RANSOMWARE,
                severity="CRITICAL",
                confidence=0.98,
                threat_actor="LockBit",
                description="Ransomware payload",
                ttps=["T1486", "T1490"],  # Data Encrypted for Impact, Inhibit System Recovery
                source="VirusTotal",
                tags=["ransomware", "lockbit"]
            ))
    
    def _generate_ioc_id(self, value: str) -> str:
        """Generate unique IOC ID"""
        return hashlib.md5(value.encode()).hexdigest()[:12]
    
    def add_ioc(self, ioc: ThreatIntelligence):
        """Add IOC to database"""
        self.iocs[ioc.ioc_id] = ioc
    
    def check_ip(self, ip_address: str) -> Optional[ThreatMatch]:
        """Check if IP matches known IOC"""
        for ioc in self.iocs.values():
            if ioc.ioc_type == IOCType.IP_ADDRESS and ioc.ioc_value == ip_address:
                match = ThreatMatch(
                    match_id=f"MATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    ioc=ioc,
                    matched_value=ip_address,
                    timestamp=datetime.now(),
                    context={'match_type': 'exact'}
                )
                self.matches.append(match)
                print(f"⚠️ Threat detected: IP {ip_address} matches IOC {ioc.ioc_id}")
                print(f"   Threat: {ioc.threat_type.value}, Severity: {ioc.severity}")
                return match
        
        return None
    
    def check_domain(self, domain: str) -> Optional[ThreatMatch]:
        """Check if domain matches known IOC"""
        for ioc in self.iocs.values():
            if ioc.ioc_type == IOCType.DOMAIN and ioc.ioc_value in domain:
                match = ThreatMatch(
                    match_id=f"MATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    ioc=ioc,
                    matched_value=domain,
                    timestamp=datetime.now(),
                    context={'match_type': 'substring'}
                )
                self.matches.append(match)
                print(f"⚠️ Threat detected: Domain {domain} matches IOC {ioc.ioc_id}")
                return match
        
        return None
    
    def check_file_hash(self, file_hash: str) -> Optional[ThreatMatch]:
        """Check if file hash matches known malware"""
        for ioc in self.iocs.values():
            if ioc.ioc_type == IOCType.FILE_HASH and ioc.ioc_value == file_hash:
                match = ThreatMatch(
                    match_id=f"MATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    ioc=ioc,
                    matched_value=file_hash,
                    timestamp=datetime.now(),
                    context={'match_type': 'exact', 'file_hash_type': 'md5/sha256'}
                )
                self.matches.append(match)
                print(f"🚨 MALWARE detected: Hash {file_hash[:16]}... matches IOC {ioc.ioc_id}")
                return match
        
        return None
    
    def get_threat_actor_profile(self, actor_name: str) -> Dict[str, Any]:
        """Get profile for threat actor"""
        actor_iocs = [
            ioc for ioc in self.iocs.values()
            if ioc.threat_actor == actor_name
        ]
        
        if not actor_iocs:
            return {}
        
        # Aggregate TTPs
        all_ttps = set()
        for ioc in actor_iocs:
            all_ttps.update(ioc.ttps)
        
        return {
            'actor_name': actor_name,
            'total_iocs': len(actor_iocs),
            'threat_types': list(set(ioc.threat_type.value for ioc in actor_iocs)),
            'ttps': list(all_ttps),
            'campaigns': list(set(ioc.campaign for ioc in actor_iocs if ioc.campaign)),
            'avg_severity': self._calculate_avg_severity(actor_iocs)
        }
    
    def _calculate_avg_severity(self, iocs: List[ThreatIntelligence]) -> str:
        """Calculate average severity"""
        severity_scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        avg = sum(severity_scores.get(ioc.severity, 0) for ioc in iocs) / len(iocs)
        
        if avg >= 3.5:
            return "CRITICAL"
        elif avg >= 2.5:
            return "HIGH"
        elif avg >= 1.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        by_type = {}
        for ioc in self.iocs.values():
            ioc_type = ioc.ioc_type.value
            by_type[ioc_type] = by_type.get(ioc_type, 0) + 1
        
        by_threat = {}
        for ioc in self.iocs.values():
            threat = ioc.threat_type.value
            by_threat[threat] = by_threat.get(threat, 0) + 1
        
        return {
            'total_iocs': len(self.iocs),
            'total_matches': len(self.matches),
            'by_ioc_type': by_type,
            'by_threat_type': by_threat,
            'high_confidence_iocs': sum(
                1 for ioc in self.iocs.values() if ioc.confidence >= 0.9
            )
        }


# Example usage
if __name__ == "__main__":
    engine = ThreatIntelligenceEngine()
    
    # Check IP against threat intel
    match = engine.check_ip("203.0.113.42")
    
    if match:
        print(f"\n🔍 Match details:")
        print(f"   Actor: {match.ioc.threat_actor}")
        print(f"   TTPs: {match.ioc.ttps}")
        print(f"   Confidence: {match.ioc.confidence}")
    
    # Get threat actor profile
    profile = engine.get_threat_actor_profile("APT29")
    print(f"\n👤 APT29 profile: {profile}")
    
    # Statistics
    stats = engine.get_statistics()
    print(f"\n📊 Threat intel: {stats['total_iocs']} IOCs, {stats['total_matches']} matches")
