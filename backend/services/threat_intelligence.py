"""
Enterprise Threat Intelligence Service
Provides real-time CVE feeds, security advisories, and threat actor tracking
for Fortune 500 cybersecurity assessment platform.
"""

import json
import requests
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import re
from dataclasses import dataclass
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CVEData:
    """CVE vulnerability data structure"""
    cve_id: str
    description: str
    severity: str
    cvss_score: float
    published_date: str
    modified_date: str
    affected_products: List[str]
    exploit_availability: bool
    threat_level: str
    remediation: str
    references: List[str]

@dataclass
class ThreatActor:
    """Threat actor intelligence data"""
    actor_id: str
    name: str
    aliases: List[str]
    attribution: str
    target_sectors: List[str]
    techniques: List[str]
    last_activity: str
    threat_level: str
    description: str

@dataclass
class SecurityAdvisory:
    """Security advisory data structure"""
    advisory_id: str
    title: str
    description: str
    severity: str
    affected_systems: List[str]
    published_date: str
    vendor: str
    solution: str
    references: List[str]

class ThreatIntelligenceManager:
    """
    Enterprise-grade threat intelligence management system
    Integrates multiple threat intelligence sources for Fortune 500 clients
    """
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        self.db_path = db_path
        self.setup_database()
        self.api_endpoints = {
            'nist_cve': 'https://services.nvd.nist.gov/rest/json/cves/2.0',
            'mitre_attack': 'https://attack.mitre.org/api/v2',
            'cisa_advisories': 'https://www.cisa.gov/api/v1/advisories',
            'threat_actors': 'https://api.threatintel.com/v1/actors'  # Example endpoint
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EnterpriseScanner-ThreatIntel/1.0',
            'Accept': 'application/json'
        })
        
    def setup_database(self):
        """Initialize threat intelligence database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # CVE data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cve_data (
                    cve_id TEXT PRIMARY KEY,
                    description TEXT,
                    severity TEXT,
                    cvss_score REAL,
                    published_date TEXT,
                    modified_date TEXT,
                    affected_products TEXT,
                    exploit_availability INTEGER,
                    threat_level TEXT,
                    remediation TEXT,
                    reference_links TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Threat actors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_actors (
                    actor_id TEXT PRIMARY KEY,
                    name TEXT,
                    aliases TEXT,
                    attribution TEXT,
                    target_sectors TEXT,
                    techniques TEXT,
                    last_activity TEXT,
                    threat_level TEXT,
                    description TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Security advisories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_advisories (
                    advisory_id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    severity TEXT,
                    affected_systems TEXT,
                    published_date TEXT,
                    vendor TEXT,
                    solution TEXT,
                    reference_links TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Threat feed sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feed_sources (
                    source_id TEXT PRIMARY KEY,
                    source_name TEXT,
                    source_url TEXT,
                    last_sync TIMESTAMP,
                    status TEXT,
                    records_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Threat intelligence database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")
            raise
    
    async def fetch_latest_cves(self, days_back: int = 7, limit: int = 100) -> List[CVEData]:
        """
        Fetch latest CVE data from NIST NVD
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'pubStartDate': start_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'pubEndDate': end_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'resultsPerPage': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_endpoints['nist_cve'], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        cves = []
                        
                        for vulnerability in data.get('vulnerabilities', []):
                            cve = vulnerability.get('cve', {})
                            
                            # Extract CVSS score
                            cvss_score = 0.0
                            metrics = cve.get('metrics', {})
                            if 'cvssMetricV31' in metrics:
                                cvss_score = metrics['cvssMetricV31'][0]['cvssData']['baseScore']
                            elif 'cvssMetricV30' in metrics:
                                cvss_score = metrics['cvssMetricV30'][0]['cvssData']['baseScore']
                            elif 'cvssMetricV2' in metrics:
                                cvss_score = metrics['cvssMetricV2'][0]['cvssData']['baseScore']
                            
                            # Determine severity
                            severity = self._calculate_severity(cvss_score)
                            
                            # Extract affected products
                            affected_products = []
                            configurations = cve.get('configurations', {}).get('nodes', [])
                            for node in configurations:
                                for cpe_match in node.get('cpeMatch', []):
                                    if cpe_match.get('vulnerable', False):
                                        affected_products.append(cpe_match.get('criteria', ''))
                            
                            cve_data = CVEData(
                                cve_id=cve.get('id', ''),
                                description=cve.get('descriptions', [{}])[0].get('value', ''),
                                severity=severity,
                                cvss_score=cvss_score,
                                published_date=cve.get('published', ''),
                                modified_date=cve.get('lastModified', ''),
                                affected_products=affected_products[:10],  # Limit for storage
                                exploit_availability=self._check_exploit_availability(cve.get('id', '')),
                                threat_level=self._assess_threat_level(cvss_score, severity),
                                remediation=self._generate_remediation_guidance(cve),
                                references=[ref.get('url', '') for ref in cve.get('references', [])][:5]
                            )
                            cves.append(cve_data)
                        
                        # Store in database
                        await self._store_cves(cves)
                        logger.info(f"Fetched and stored {len(cves)} CVEs")
                        return cves
                        
                    else:
                        logger.error(f"CVE API request failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching CVEs: {e}")
            return []
    
    async def fetch_threat_actors(self) -> List[ThreatActor]:
        """
        Fetch threat actor intelligence data
        """
        try:
            # Mock threat actor data for demonstration
            # In production, this would integrate with commercial threat intel feeds
            threat_actors = [
                ThreatActor(
                    actor_id="apt29",
                    name="APT29",
                    aliases=["Cozy Bear", "The Dukes", "YTTRIUM"],
                    attribution="Russia-linked",
                    target_sectors=["Government", "Healthcare", "Technology", "Finance"],
                    techniques=["Spear phishing", "Supply chain attacks", "Living off the land"],
                    last_activity="2024-01-15",
                    threat_level="Critical",
                    description="Advanced persistent threat group attributed to Russian SVR"
                ),
                ThreatActor(
                    actor_id="apt40",
                    name="APT40",
                    aliases=["Leviathan", "TEMP.Periscope", "TEMP.Jumper"],
                    attribution="China-linked",
                    target_sectors=["Maritime", "Government", "Technology"],
                    techniques=["Web shells", "Credential harvesting", "Lateral movement"],
                    last_activity="2024-01-10",
                    threat_level="High",
                    description="Chinese state-sponsored group targeting maritime industries"
                ),
                ThreatActor(
                    actor_id="lazarus",
                    name="Lazarus Group",
                    aliases=["HIDDEN COBRA", "Guardians of Peace", "APT38"],
                    attribution="North Korea-linked",
                    target_sectors=["Financial", "Cryptocurrency", "Media", "Government"],
                    techniques=["Custom malware", "Destructive attacks", "Financial theft"],
                    last_activity="2024-01-12",
                    threat_level="Critical",
                    description="North Korean state-sponsored group known for financial crimes"
                ),
                ThreatActor(
                    actor_id="conti",
                    name="Conti",
                    aliases=["Wizard Spider", "TrickBot"],
                    attribution="Cybercriminal",
                    target_sectors=["Healthcare", "Government", "Manufacturing", "Retail"],
                    techniques=["Ransomware", "Data exfiltration", "Double extortion"],
                    last_activity="2024-01-08",
                    threat_level="High",
                    description="Ransomware-as-a-Service group with sophisticated operations"
                )
            ]
            
            await self._store_threat_actors(threat_actors)
            logger.info(f"Updated {len(threat_actors)} threat actor profiles")
            return threat_actors
            
        except Exception as e:
            logger.error(f"Error fetching threat actors: {e}")
            return []
    
    async def fetch_security_advisories(self) -> List[SecurityAdvisory]:
        """
        Fetch security advisories from various vendors
        """
        try:
            advisories = []
            
            # Mock security advisories (in production, integrate with vendor APIs)
            mock_advisories = [
                SecurityAdvisory(
                    advisory_id="MSFT-2024-001",
                    title="Critical Windows RCE Vulnerability",
                    description="Remote code execution vulnerability in Windows SMB service",
                    severity="Critical",
                    affected_systems=["Windows Server 2019", "Windows Server 2022", "Windows 10", "Windows 11"],
                    published_date="2024-01-15T10:00:00Z",
                    vendor="Microsoft",
                    solution="Apply January 2024 security updates immediately",
                    references=["https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2024-0001"]
                ),
                SecurityAdvisory(
                    advisory_id="CISCO-2024-002",
                    title="Cisco IOS XE Web UI Vulnerability",
                    description="Authentication bypass in Cisco IOS XE web management interface",
                    severity="High",
                    affected_systems=["Cisco IOS XE 16.x", "Cisco IOS XE 17.x"],
                    published_date="2024-01-12T14:30:00Z",
                    vendor="Cisco",
                    solution="Upgrade to latest IOS XE version or disable web UI",
                    references=["https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-iosxe-webui-privesc-j22SaA4z"]
                ),
                SecurityAdvisory(
                    advisory_id="VMWARE-2024-003",
                    title="VMware vCenter Server SSRF Vulnerability",
                    description="Server-side request forgery in VMware vCenter Server",
                    severity="Medium",
                    affected_systems=["vCenter Server 7.0", "vCenter Server 8.0"],
                    published_date="2024-01-10T09:15:00Z",
                    vendor="VMware",
                    solution="Apply VMware security patches VMSA-2024-0001",
                    references=["https://www.vmware.com/security/advisories/VMSA-2024-0001.html"]
                )
            ]
            
            advisories.extend(mock_advisories)
            await self._store_security_advisories(advisories)
            logger.info(f"Updated {len(advisories)} security advisories")
            return advisories
            
        except Exception as e:
            logger.error(f"Error fetching security advisories: {e}")
            return []
    
    def get_threat_intelligence_summary(self) -> Dict:
        """
        Generate comprehensive threat intelligence summary for dashboard
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # CVE statistics
            cursor.execute("SELECT COUNT(*) FROM cve_data WHERE severity = 'Critical'")
            critical_cves = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cve_data WHERE severity = 'High'")
            high_cves = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cve_data WHERE threat_level = 'Critical'")
            critical_threats = cursor.fetchone()[0]
            
            # Recent threat activity
            cursor.execute("""
                SELECT COUNT(*) FROM threat_actors 
                WHERE last_activity >= date('now', '-30 days')
            """)
            active_threat_actors = cursor.fetchone()[0]
            
            # Recent advisories
            cursor.execute("""
                SELECT COUNT(*) FROM security_advisories 
                WHERE published_date >= date('now', '-7 days')
            """)
            recent_advisories = cursor.fetchone()[0]
            
            # Top threat categories
            cursor.execute("""
                SELECT severity, COUNT(*) FROM cve_data 
                GROUP BY severity ORDER BY COUNT(*) DESC
            """)
            severity_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'summary': {
                    'critical_cves': critical_cves,
                    'high_cves': high_cves,
                    'critical_threats': critical_threats,
                    'active_threat_actors': active_threat_actors,
                    'recent_advisories': recent_advisories
                },
                'severity_distribution': severity_distribution,
                'threat_landscape': {
                    'trending_vulnerabilities': self._get_trending_vulnerabilities(),
                    'active_campaigns': self._get_active_threat_campaigns(),
                    'industry_targeting': self._get_industry_targeting_trends()
                },
                'recommendations': self._generate_threat_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating threat intelligence summary: {e}")
            return {'error': 'Failed to generate summary'}
    
    def search_threat_intelligence(self, query: str, category: str = 'all') -> Dict:
        """
        Search threat intelligence database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results = {
                'cves': [],
                'threat_actors': [],
                'advisories': []
            }
            
            if category in ['all', 'cves']:
                cursor.execute("""
                    SELECT * FROM cve_data 
                    WHERE cve_id LIKE ? OR description LIKE ?
                    ORDER BY cvss_score DESC LIMIT 10
                """, (f'%{query}%', f'%{query}%'))
                
                results['cves'] = [dict(zip([col[0] for col in cursor.description], row)) 
                                 for row in cursor.fetchall()]
            
            if category in ['all', 'actors']:
                cursor.execute("""
                    SELECT * FROM threat_actors 
                    WHERE name LIKE ? OR aliases LIKE ? OR description LIKE ?
                    ORDER BY threat_level DESC LIMIT 10
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                results['threat_actors'] = [dict(zip([col[0] for col in cursor.description], row)) 
                                          for row in cursor.fetchall()]
            
            if category in ['all', 'advisories']:
                cursor.execute("""
                    SELECT * FROM security_advisories 
                    WHERE title LIKE ? OR description LIKE ?
                    ORDER BY published_date DESC LIMIT 10
                """, (f'%{query}%', f'%{query}%'))
                
                results['advisories'] = [dict(zip([col[0] for col in cursor.description], row)) 
                                       for row in cursor.fetchall()]
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching threat intelligence: {e}")
            return {'error': 'Search failed'}
    
    # Helper methods
    def _calculate_severity(self, cvss_score: float) -> str:
        """Calculate vulnerability severity based on CVSS score"""
        if cvss_score >= 9.0:
            return "Critical"
        elif cvss_score >= 7.0:
            return "High"
        elif cvss_score >= 4.0:
            return "Medium"
        else:
            return "Low"
    
    def _assess_threat_level(self, cvss_score: float, severity: str) -> str:
        """Assess threat level based on multiple factors"""
        if severity == "Critical" and cvss_score >= 9.5:
            return "Critical"
        elif severity in ["Critical", "High"]:
            return "High"
        elif severity == "Medium":
            return "Medium"
        else:
            return "Low"
    
    def _check_exploit_availability(self, cve_id: str) -> bool:
        """Check if public exploits are available (mock implementation)"""
        # In production, integrate with exploit databases
        return False
    
    def _generate_remediation_guidance(self, cve: Dict) -> str:
        """Generate remediation guidance"""
        return "Apply vendor security patches and implement compensating controls as appropriate."
    
    def _get_trending_vulnerabilities(self) -> List[Dict]:
        """Get trending vulnerability types"""
        return [
            {"type": "Remote Code Execution", "count": 15, "trend": "up"},
            {"type": "Privilege Escalation", "count": 12, "trend": "stable"},
            {"type": "Information Disclosure", "count": 8, "trend": "down"}
        ]
    
    def _get_active_threat_campaigns(self) -> List[Dict]:
        """Get active threat campaigns"""
        return [
            {"campaign": "SolarWinds Supply Chain", "actor": "APT29", "status": "ongoing"},
            {"campaign": "Exchange Server Exploitation", "actor": "Multiple", "status": "declining"},
            {"campaign": "Ransomware Operations", "actor": "Conti", "status": "active"}
        ]
    
    def _get_industry_targeting_trends(self) -> List[Dict]:
        """Get industry targeting trends"""
        return [
            {"industry": "Healthcare", "threat_level": "High", "primary_threats": ["Ransomware", "Data theft"]},
            {"industry": "Financial", "threat_level": "Critical", "primary_threats": ["APT", "Fraud"]},
            {"industry": "Government", "threat_level": "Critical", "primary_threats": ["Espionage", "APT"]}
        ]
    
    def _generate_threat_recommendations(self) -> List[str]:
        """Generate threat-based recommendations"""
        return [
            "Prioritize patching for Critical and High severity vulnerabilities",
            "Implement enhanced monitoring for APT29 TTPs",
            "Review and update incident response procedures",
            "Conduct threat hunting activities focusing on recent IOCs",
            "Enhance email security controls to prevent phishing attacks"
        ]
    
    async def _store_cves(self, cves: List[CVEData]):
        """Store CVE data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for cve in cves:
                cursor.execute("""
                    INSERT OR REPLACE INTO cve_data 
                    (cve_id, description, severity, cvss_score, published_date, modified_date,
                     affected_products, exploit_availability, threat_level, remediation, reference_links)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cve.cve_id, cve.description, cve.severity, cve.cvss_score,
                    cve.published_date, cve.modified_date, json.dumps(cve.affected_products),
                    int(cve.exploit_availability), cve.threat_level, cve.remediation,
                    json.dumps(cve.references)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing CVEs: {e}")
    
    async def _store_threat_actors(self, actors: List[ThreatActor]):
        """Store threat actor data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for actor in actors:
                cursor.execute("""
                    INSERT OR REPLACE INTO threat_actors 
                    (actor_id, name, aliases, attribution, target_sectors, techniques,
                     last_activity, threat_level, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    actor.actor_id, actor.name, json.dumps(actor.aliases),
                    actor.attribution, json.dumps(actor.target_sectors),
                    json.dumps(actor.techniques), actor.last_activity,
                    actor.threat_level, actor.description
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing threat actors: {e}")
    
    async def _store_security_advisories(self, advisories: List[SecurityAdvisory]):
        """Store security advisory data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for advisory in advisories:
                cursor.execute("""
                    INSERT OR REPLACE INTO security_advisories 
                    (advisory_id, title, description, severity, affected_systems,
                     published_date, vendor, solution, reference_links)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    advisory.advisory_id, advisory.title, advisory.description,
                    advisory.severity, json.dumps(advisory.affected_systems),
                    advisory.published_date, advisory.vendor, advisory.solution,
                    json.dumps(advisory.references)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing security advisories: {e}")

# Global threat intelligence manager instance
threat_intel_manager = ThreatIntelligenceManager()