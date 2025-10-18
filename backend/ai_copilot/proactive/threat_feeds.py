"""
Jupiter Threat Feeds Integration
Monitors CVE databases, exploit feeds, and threat intelligence sources
Provides real-time vulnerability awareness
"""

import sqlite3
import json
import requests
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from enum import Enum
import hashlib
import re


class ThreatFeedType(Enum):
    """Types of threat intelligence feeds"""
    CVE_DATABASE = "cve_database"  # NVD, MITRE CVE
    EXPLOIT_DATABASE = "exploit_database"  # Exploit-DB, Metasploit
    THREAT_INTELLIGENCE = "threat_intelligence"  # OSINT, vendor feeds
    RANSOMWARE_TRACKER = "ransomware_tracker"
    MALWARE_SIGNATURES = "malware_signatures"
    IOC_FEED = "ioc_feed"  # Indicators of Compromise
    ZERO_DAY_FEED = "zero_day_feed"
    VENDOR_ADVISORY = "vendor_advisory"


class VulnerabilitySeverity(Enum):
    """CVSS-based severity levels"""
    CRITICAL = "critical"  # CVSS 9.0-10.0
    HIGH = "high"  # CVSS 7.0-8.9
    MEDIUM = "medium"  # CVSS 4.0-6.9
    LOW = "low"  # CVSS 0.1-3.9
    NONE = "none"  # CVSS 0.0
    UNKNOWN = "unknown"


class ExploitStatus(Enum):
    """Exploit availability status"""
    EXPLOIT_PUBLIC = "exploit_public"  # Publicly available exploit
    EXPLOIT_PRIVATE = "exploit_private"  # Private/commercial exploit
    POC_AVAILABLE = "poc_available"  # Proof of concept code
    IN_THE_WILD = "in_the_wild"  # Actively being exploited
    NO_EXPLOIT = "no_exploit"  # No known exploit
    UNKNOWN = "unknown"


@dataclass
class Vulnerability:
    """Vulnerability information from threat feeds"""
    cve_id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: float
    cvss_vector: str
    published_date: datetime
    last_modified: datetime
    affected_products: List[str] = field(default_factory=list)
    affected_versions: List[str] = field(default_factory=list)
    exploit_status: ExploitStatus = ExploitStatus.UNKNOWN
    exploit_urls: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    cwe_ids: List[str] = field(default_factory=list)  # CWE weakness types
    vendor_advisories: List[str] = field(default_factory=list)
    patch_available: bool = False
    patch_urls: List[str] = field(default_factory=list)
    is_zero_day: bool = False
    
    def get_risk_score(self) -> float:
        """Calculate composite risk score (0-100)"""
        base_score = self.cvss_score * 10  # Convert to 0-100
        
        # Increase risk for public exploits
        if self.exploit_status == ExploitStatus.IN_THE_WILD:
            base_score *= 1.5
        elif self.exploit_status == ExploitStatus.EXPLOIT_PUBLIC:
            base_score *= 1.3
        elif self.exploit_status == ExploitStatus.POC_AVAILABLE:
            base_score *= 1.2
        
        # Increase risk for zero-days
        if self.is_zero_day:
            base_score *= 1.4
        
        # Reduce risk if patch available
        if self.patch_available:
            base_score *= 0.8
        
        return min(base_score, 100.0)  # Cap at 100


@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    threat_id: str
    threat_type: str  # malware, ransomware, apt, etc.
    threat_name: str
    description: str
    first_seen: datetime
    last_seen: datetime
    indicators_of_compromise: List[Dict] = field(default_factory=list)  # IPs, domains, hashes
    related_cves: List[str] = field(default_factory=list)
    targeted_industries: List[str] = field(default_factory=list)
    targeted_countries: List[str] = field(default_factory=list)
    ttps: List[str] = field(default_factory=list)  # MITRE ATT&CK TTPs
    severity: str = "unknown"
    is_active: bool = True


@dataclass
class ThreatFeed:
    """Threat feed source configuration"""
    feed_id: str
    feed_name: str
    feed_type: ThreatFeedType
    feed_url: str
    update_frequency: int  # minutes
    last_updated: Optional[datetime] = None
    is_enabled: bool = True
    requires_auth: bool = False
    api_key: Optional[str] = None


class JupiterThreatFeeds:
    """
    Threat feed aggregation and monitoring system
    Integrates multiple vulnerability and threat intelligence sources
    """
    
    def __init__(self, db_path: str = "jupiter_threat_feeds.db"):
        self.db_path = db_path
        self._init_database()
        self._init_default_feeds()
    
    def _init_database(self):
        """Initialize threat feeds database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Threat feeds configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_feeds (
                feed_id TEXT PRIMARY KEY,
                feed_name TEXT NOT NULL,
                feed_type TEXT NOT NULL,
                feed_url TEXT NOT NULL,
                update_frequency INTEGER DEFAULT 60,
                last_updated TEXT,
                is_enabled INTEGER DEFAULT 1,
                requires_auth INTEGER DEFAULT 0,
                api_key TEXT
            )
        """)
        
        # Vulnerabilities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                cve_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                cvss_score REAL NOT NULL,
                cvss_vector TEXT,
                published_date TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                affected_products TEXT,
                affected_versions TEXT,
                exploit_status TEXT,
                exploit_urls TEXT,
                references TEXT,
                cwe_ids TEXT,
                vendor_advisories TEXT,
                patch_available INTEGER DEFAULT 0,
                patch_urls TEXT,
                is_zero_day INTEGER DEFAULT 0,
                risk_score REAL,
                first_seen TEXT NOT NULL,
                last_checked TEXT NOT NULL
            )
        """)
        
        # Threat intelligence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                threat_id TEXT PRIMARY KEY,
                threat_type TEXT NOT NULL,
                threat_name TEXT NOT NULL,
                description TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                indicators_of_compromise TEXT,
                related_cves TEXT,
                targeted_industries TEXT,
                targeted_countries TEXT,
                ttps TEXT,
                severity TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Vulnerability tracking (user's systems)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerability_tracking (
                tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT NOT NULL,
                system_id TEXT NOT NULL,
                detected_date TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                assigned_to TEXT,
                remediation_notes TEXT,
                closed_date TEXT,
                FOREIGN KEY (cve_id) REFERENCES vulnerabilities(cve_id)
            )
        """)
        
        # Feed update log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feed_update_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id TEXT NOT NULL,
                update_timestamp TEXT NOT NULL,
                items_fetched INTEGER,
                new_items INTEGER,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (feed_id) REFERENCES threat_feeds(feed_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_default_feeds(self):
        """Initialize default threat feed sources"""
        default_feeds = [
            ThreatFeed(
                feed_id="nvd_cve",
                feed_name="NIST NVD CVE Database",
                feed_type=ThreatFeedType.CVE_DATABASE,
                feed_url="https://services.nvd.nist.gov/rest/json/cves/2.0",
                update_frequency=60,  # Every hour
                requires_auth=False
            ),
            ThreatFeed(
                feed_id="exploit_db",
                feed_name="Exploit Database",
                feed_type=ThreatFeedType.EXPLOIT_DATABASE,
                feed_url="https://www.exploit-db.com/",
                update_frequency=120,
                requires_auth=False
            ),
            ThreatFeed(
                feed_id="cisa_kev",
                feed_name="CISA Known Exploited Vulnerabilities",
                feed_type=ThreatFeedType.ZERO_DAY_FEED,
                feed_url="https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
                update_frequency=30,  # Every 30 minutes
                requires_auth=False
            ),
            ThreatFeed(
                feed_id="mitre_cve",
                feed_name="MITRE CVE List",
                feed_type=ThreatFeedType.CVE_DATABASE,
                feed_url="https://cve.mitre.org/",
                update_frequency=60,
                requires_auth=False
            )
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for feed in default_feeds:
            cursor.execute("""
                INSERT OR IGNORE INTO threat_feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feed.feed_id,
                feed.feed_name,
                feed.feed_type.value,
                feed.feed_url,
                feed.update_frequency,
                None,
                feed.is_enabled,
                feed.requires_auth,
                feed.api_key
            ))
        
        conn.commit()
        conn.close()
    
    def add_vulnerability(self, vuln: Vulnerability) -> bool:
        """Add or update vulnerability in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        risk_score = vuln.get_risk_score()
        
        cursor.execute("""
            INSERT OR REPLACE INTO vulnerabilities VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            vuln.cve_id,
            vuln.title,
            vuln.description,
            vuln.severity.value,
            vuln.cvss_score,
            vuln.cvss_vector,
            vuln.published_date.isoformat(),
            vuln.last_modified.isoformat(),
            json.dumps(vuln.affected_products),
            json.dumps(vuln.affected_versions),
            vuln.exploit_status.value,
            json.dumps(vuln.exploit_urls),
            json.dumps(vuln.references),
            json.dumps(vuln.cwe_ids),
            json.dumps(vuln.vendor_advisories),
            vuln.patch_available,
            json.dumps(vuln.patch_urls),
            vuln.is_zero_day,
            risk_score,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return True
    
    def search_vulnerabilities(
        self,
        product: str = None,
        severity: VulnerabilitySeverity = None,
        exploit_available: bool = None,
        min_cvss: float = None,
        days_since_published: int = None,
        limit: int = 100
    ) -> List[Vulnerability]:
        """Search vulnerabilities with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM vulnerabilities WHERE 1=1"
        params = []
        
        if product:
            query += " AND affected_products LIKE ?"
            params.append(f'%{product}%')
        
        if severity:
            query += " AND severity = ?"
            params.append(severity.value)
        
        if exploit_available:
            query += " AND exploit_status IN ('exploit_public', 'in_the_wild', 'poc_available')"
        
        if min_cvss:
            query += " AND cvss_score >= ?"
            params.append(min_cvss)
        
        if days_since_published:
            cutoff_date = (datetime.now() - timedelta(days=days_since_published)).isoformat()
            query += " AND published_date >= ?"
            params.append(cutoff_date)
        
        query += " ORDER BY risk_score DESC, cvss_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        vulnerabilities = []
        for row in rows:
            vuln = Vulnerability(
                cve_id=row[0],
                title=row[1],
                description=row[2],
                severity=VulnerabilitySeverity(row[3]),
                cvss_score=row[4],
                cvss_vector=row[5],
                published_date=datetime.fromisoformat(row[6]),
                last_modified=datetime.fromisoformat(row[7]),
                affected_products=json.loads(row[8]),
                affected_versions=json.loads(row[9]),
                exploit_status=ExploitStatus(row[10]),
                exploit_urls=json.loads(row[11]),
                references=json.loads(row[12]),
                cwe_ids=json.loads(row[13]),
                vendor_advisories=json.loads(row[14]),
                patch_available=bool(row[15]),
                patch_urls=json.loads(row[16]),
                is_zero_day=bool(row[17])
            )
            vulnerabilities.append(vuln)
        
        conn.close()
        return vulnerabilities
    
    def get_critical_vulnerabilities(self, days: int = 7) -> List[Vulnerability]:
        """Get critical vulnerabilities from recent days"""
        return self.search_vulnerabilities(
            severity=VulnerabilitySeverity.CRITICAL,
            days_since_published=days,
            limit=50
        )
    
    def get_exploited_vulnerabilities(self) -> List[Vulnerability]:
        """Get vulnerabilities with public exploits or actively exploited"""
        return self.search_vulnerabilities(
            exploit_available=True,
            limit=100
        )
    
    def get_zero_day_vulnerabilities(self) -> List[Vulnerability]:
        """Get zero-day vulnerabilities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM vulnerabilities 
            WHERE is_zero_day = 1
            ORDER BY published_date DESC
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        vulnerabilities = []
        
        for row in rows:
            vuln = Vulnerability(
                cve_id=row[0],
                title=row[1],
                description=row[2],
                severity=VulnerabilitySeverity(row[3]),
                cvss_score=row[4],
                cvss_vector=row[5],
                published_date=datetime.fromisoformat(row[6]),
                last_modified=datetime.fromisoformat(row[7]),
                affected_products=json.loads(row[8]),
                affected_versions=json.loads(row[9]),
                exploit_status=ExploitStatus(row[10]),
                exploit_urls=json.loads(row[11]),
                references=json.loads(row[12]),
                cwe_ids=json.loads(row[13]),
                vendor_advisories=json.loads(row[14]),
                patch_available=bool(row[15]),
                patch_urls=json.loads(row[16]),
                is_zero_day=bool(row[17])
            )
            vulnerabilities.append(vuln)
        
        conn.close()
        return vulnerabilities
    
    def check_product_vulnerabilities(self, product_name: str, version: str = None) -> List[Vulnerability]:
        """Check if specific product/version has known vulnerabilities"""
        vulns = self.search_vulnerabilities(product=product_name, limit=200)
        
        if version:
            # Filter by version if specified
            filtered_vulns = []
            for vuln in vulns:
                if any(version in v for v in vuln.affected_versions):
                    filtered_vulns.append(vuln)
            return filtered_vulns
        
        return vulns
    
    def add_threat_intelligence(self, threat: ThreatIntelligence) -> bool:
        """Add threat intelligence data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO threat_intelligence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            threat.threat_id,
            threat.threat_type,
            threat.threat_name,
            threat.description,
            threat.first_seen.isoformat(),
            threat.last_seen.isoformat(),
            json.dumps(threat.indicators_of_compromise),
            json.dumps(threat.related_cves),
            json.dumps(threat.targeted_industries),
            json.dumps(threat.targeted_countries),
            json.dumps(threat.ttps),
            threat.severity,
            threat.is_active
        ))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_active_threats(self, industry: str = None) -> List[ThreatIntelligence]:
        """Get active threat intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if industry:
            cursor.execute("""
                SELECT * FROM threat_intelligence 
                WHERE is_active = 1 AND targeted_industries LIKE ?
                ORDER BY last_seen DESC
            """, (f'%{industry}%',))
        else:
            cursor.execute("""
                SELECT * FROM threat_intelligence 
                WHERE is_active = 1
                ORDER BY last_seen DESC
            """)
        
        rows = cursor.fetchall()
        threats = []
        
        for row in rows:
            threat = ThreatIntelligence(
                threat_id=row[0],
                threat_type=row[1],
                threat_name=row[2],
                description=row[3],
                first_seen=datetime.fromisoformat(row[4]),
                last_seen=datetime.fromisoformat(row[5]),
                indicators_of_compromise=json.loads(row[6]),
                related_cves=json.loads(row[7]),
                targeted_industries=json.loads(row[8]),
                targeted_countries=json.loads(row[9]),
                ttps=json.loads(row[10]),
                severity=row[11],
                is_active=bool(row[12])
            )
            threats.append(threat)
        
        conn.close()
        return threats
    
    def get_statistics(self) -> Dict:
        """Get threat feed statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total vulnerabilities
        cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
        stats['total_vulnerabilities'] = cursor.fetchone()[0]
        
        # By severity
        cursor.execute("""
            SELECT severity, COUNT(*) FROM vulnerabilities GROUP BY severity
        """)
        stats['by_severity'] = dict(cursor.fetchall())
        
        # Exploitable vulnerabilities
        cursor.execute("""
            SELECT COUNT(*) FROM vulnerabilities 
            WHERE exploit_status IN ('exploit_public', 'in_the_wild', 'poc_available')
        """)
        stats['exploitable_count'] = cursor.fetchone()[0]
        
        # Zero-day vulnerabilities
        cursor.execute("SELECT COUNT(*) FROM vulnerabilities WHERE is_zero_day = 1")
        stats['zero_day_count'] = cursor.fetchone()[0]
        
        # Recent vulnerabilities (last 7 days)
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM vulnerabilities WHERE published_date >= ?
        """, (cutoff,))
        stats['recent_vulnerabilities'] = cursor.fetchone()[0]
        
        # Active threats
        cursor.execute("SELECT COUNT(*) FROM threat_intelligence WHERE is_active = 1")
        stats['active_threats'] = cursor.fetchone()[0]
        
        # Average risk score
        cursor.execute("SELECT AVG(risk_score) FROM vulnerabilities")
        stats['avg_risk_score'] = cursor.fetchone()[0] or 0.0
        
        # Highest risk vulnerabilities
        cursor.execute("""
            SELECT cve_id, cvss_score, risk_score FROM vulnerabilities 
            ORDER BY risk_score DESC LIMIT 10
        """)
        stats['highest_risk'] = [
            {'cve_id': row[0], 'cvss_score': row[1], 'risk_score': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    feeds = JupiterThreatFeeds()
    
    # Add sample vulnerability
    vuln = Vulnerability(
        cve_id="CVE-2024-12345",
        title="Critical Remote Code Execution in Web Framework",
        description="A critical vulnerability allows unauthenticated remote code execution...",
        severity=VulnerabilitySeverity.CRITICAL,
        cvss_score=9.8,
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        published_date=datetime.now(),
        last_modified=datetime.now(),
        affected_products=["WebFramework X", "WebFramework Y"],
        affected_versions=["1.0-2.5", "3.0-3.2"],
        exploit_status=ExploitStatus.EXPLOIT_PUBLIC,
        exploit_urls=["https://exploit-db.com/exploits/12345"],
        cwe_ids=["CWE-78"],
        patch_available=True,
        patch_urls=["https://vendor.com/security/patch-123"]
    )
    
    feeds.add_vulnerability(vuln)
    print(f"Added vulnerability: {vuln.cve_id}")
    print(f"Risk score: {vuln.get_risk_score():.1f}/100")
    
    # Search critical vulnerabilities
    critical = feeds.get_critical_vulnerabilities(days=30)
    print(f"\nCritical vulnerabilities (last 30 days): {len(critical)}")
    
    # Get statistics
    stats = feeds.get_statistics()
    print(f"\nThreat feed statistics:")
    print(f"  Total vulnerabilities: {stats['total_vulnerabilities']}")
    print(f"  Exploitable: {stats['exploitable_count']}")
    print(f"  Zero-days: {stats['zero_day_count']}")
    print(f"  Recent (7 days): {stats['recent_vulnerabilities']}")
