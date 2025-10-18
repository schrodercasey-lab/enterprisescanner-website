"""
Module G.2.4: Industry-Specific Intelligence Gathering
======================================================

Purpose: Collect and analyze industry-specific threat intelligence for
         targeted sectors with unique regulatory and threat landscapes.

Sectors Covered:
- Financial Services (Banking, Investment, Insurance)
- Healthcare (Hospitals, Pharma, Medical Devices)
- Energy & Utilities (Power, Oil & Gas, Renewable)
- Retail & E-commerce (Point-of-Sale, Online)
- Technology (SaaS, Cloud, Software Development)

Features:
- Industry-specific threat actor tracking
- Regulatory compliance advisory monitoring
- Sector-targeted campaign detection
- Industry vulnerability prioritization
- Compliance framework mapping (PCI-DSS, HIPAA, NERC CIP, SOX)
- Attack vector analysis by sector
- Peer organization breach intelligence

Author: Enterprise Scanner AI Development Team
Version: 1.0.0
Created: October 17, 2025
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Industry(Enum):
    """Supported industry sectors"""
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    ENERGY = "energy"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    GOVERNMENT = "government"
    MANUFACTURING = "manufacturing"
    TELECOMMUNICATIONS = "telecommunications"


class ComplianceFramework(Enum):
    """Major compliance frameworks by industry"""
    PCI_DSS = "pci_dss"  # Financial/Retail
    HIPAA = "hipaa"  # Healthcare
    NERC_CIP = "nerc_cip"  # Energy
    SOX = "sox"  # Financial
    GDPR = "gdpr"  # All industries (EU)
    CCPA = "ccpa"  # All industries (California)
    FISMA = "fisma"  # Government
    NIST_CSF = "nist_csf"  # All industries
    ISO_27001 = "iso_27001"  # All industries


class ThreatSeverity(Enum):
    """Industry-specific threat severity"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class IndustryThreat:
    """Represents an industry-specific threat"""
    threat_id: Optional[int] = None
    industry: Industry = Industry.FINANCIAL
    threat_name: str = ""
    threat_type: str = ""  # campaign, vulnerability, actor, technique
    description: str = ""
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    affected_organizations: List[str] = field(default_factory=list)
    attack_vectors: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)  # IoCs, CVEs
    compliance_impact: List[ComplianceFramework] = field(default_factory=list)
    mitigation_recommendations: List[str] = field(default_factory=list)
    source: str = ""
    confidence_score: float = 0.5  # 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'threat_id': self.threat_id,
            'industry': self.industry.value,
            'threat_name': self.threat_name,
            'threat_type': self.threat_type,
            'severity': self.severity.value,
            'first_observed': self.first_observed.isoformat() if self.first_observed else None,
            'last_observed': self.last_observed.isoformat() if self.last_observed else None,
            'affected_organizations': self.affected_organizations,
            'compliance_impact': [f.value for f in self.compliance_impact],
            'confidence_score': self.confidence_score
        }


@dataclass
class RegulatoryAdvisory:
    """Represents regulatory/compliance advisory"""
    advisory_id: Optional[int] = None
    industry: Industry = Industry.FINANCIAL
    framework: ComplianceFramework = ComplianceFramework.NIST_CSF
    advisory_title: str = ""
    advisory_number: str = ""  # e.g., "CISA AA23-158A"
    published_date: Optional[datetime] = None
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    description: str = ""
    affected_controls: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    source_url: str = ""
    
    def is_overdue(self) -> bool:
        """Check if advisory deadline has passed"""
        if self.deadline:
            return datetime.now() > self.deadline
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'advisory_id': self.advisory_id,
            'industry': self.industry.value,
            'framework': self.framework.value,
            'advisory_title': self.advisory_title,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'severity': self.severity.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_overdue': self.is_overdue()
        }


@dataclass
class IndustryCampaign:
    """Represents industry-targeted threat campaign"""
    campaign_id: Optional[int] = None
    campaign_name: str = ""
    target_industry: Industry = Industry.FINANCIAL
    threat_actor: str = ""
    start_date: Optional[datetime] = None
    is_active: bool = True
    victim_count: int = 0
    attack_techniques: List[str] = field(default_factory=list)  # MITRE ATT&CK IDs
    primary_objective: str = ""  # financial theft, espionage, disruption
    malware_families: List[str] = field(default_factory=list)
    ioc_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'target_industry': self.target_industry.value,
            'threat_actor': self.threat_actor,
            'is_active': self.is_active,
            'victim_count': self.victim_count,
            'primary_objective': self.primary_objective
        }


# =============================================================================
# Industry-Specific Intelligence Gatherer
# =============================================================================

class IndustryIntelligenceGatherer:
    """
    Collect and analyze industry-specific threat intelligence
    
    Capabilities:
    - Industry threat landscape monitoring
    - Regulatory advisory tracking
    - Sector-specific campaign detection
    - Compliance framework mapping
    - Peer breach intelligence
    - Attack vector analysis by sector
    - Industry vulnerability prioritization
    """
    
    # Industry-specific threat actor mapping
    INDUSTRY_ACTORS = {
        Industry.FINANCIAL: [
            "FIN7", "FIN8", "Carbanak", "Lazarus Group", "Silence Group",
            "APT38", "Cobalt Group", "MoneyTaker"
        ],
        Industry.HEALTHCARE: [
            "APT41", "FIN6", "APT10", "Wizard Spider", "Conti Group",
            "REvil", "Ryuk", "Black Kingdom"
        ],
        Industry.ENERGY: [
            "APT33", "APT34", "Dragonfly", "XENOTIME", "APT41",
            "Sandworm", "TEMP.Veles", "Lyceum"
        ],
        Industry.RETAIL: [
            "FIN7", "FIN8", "Magecart", "REvil", "Carbanak",
            "APT41", "Cobalt Strike teams"
        ],
        Industry.TECHNOLOGY: [
            "APT41", "APT10", "Lazarus Group", "APT29", "APT28",
            "Nobelium", "Hafnium", "LAPSUS$"
        ]
    }
    
    # Compliance framework to industry mapping
    COMPLIANCE_MAPPING = {
        Industry.FINANCIAL: [
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.SOX,
            ComplianceFramework.GDPR,
            ComplianceFramework.NIST_CSF
        ],
        Industry.HEALTHCARE: [
            ComplianceFramework.HIPAA,
            ComplianceFramework.GDPR,
            ComplianceFramework.NIST_CSF,
            ComplianceFramework.ISO_27001
        ],
        Industry.ENERGY: [
            ComplianceFramework.NERC_CIP,
            ComplianceFramework.NIST_CSF,
            ComplianceFramework.ISO_27001
        ],
        Industry.RETAIL: [
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.GDPR,
            ComplianceFramework.CCPA,
            ComplianceFramework.NIST_CSF
        ],
        Industry.TECHNOLOGY: [
            ComplianceFramework.ISO_27001,
            ComplianceFramework.GDPR,
            ComplianceFramework.NIST_CSF,
            ComplianceFramework.SOX
        ]
    }
    
    # Common attack vectors by industry
    ATTACK_VECTORS = {
        Industry.FINANCIAL: [
            "Phishing", "Business Email Compromise", "ATM Malware",
            "SWIFT Network Attacks", "Card Skimming", "Web Application Attacks"
        ],
        Industry.HEALTHCARE: [
            "Ransomware", "Phishing", "Medical Device Exploitation",
            "EHR System Attacks", "Supply Chain Attacks", "Insider Threats"
        ],
        Industry.ENERGY: [
            "ICS/SCADA Attacks", "Supply Chain Compromise", "Spear Phishing",
            "Watering Hole Attacks", "Remote Access Exploitation", "Living off the Land"
        ],
        Industry.RETAIL: [
            "Point-of-Sale Malware", "E-commerce Skimming", "Magecart Attacks",
            "Supply Chain Attacks", "Ransomware", "Credential Stuffing"
        ],
        Industry.TECHNOLOGY: [
            "Software Supply Chain", "Zero-Day Exploitation", "API Attacks",
            "Cloud Misconfigurations", "Insider Threats", "Advanced Persistent Threats"
        ]
    }
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        """
        Initialize industry intelligence gatherer
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.threats: Dict[Industry, List[IndustryThreat]] = {}
        self.advisories: Dict[Industry, List[RegulatoryAdvisory]] = {}
        self.campaigns: Dict[Industry, List[IndustryCampaign]] = {}
        
        # HTTP session with retry logic
        self.session = self._create_http_session()
        
        # Load existing data
        self._load_industry_threats()
        
        logger.info(f"IndustryIntelligenceGatherer initialized for {len(Industry)} sectors")
    
    def _create_http_session(self) -> requests.Session:
        """Create HTTP session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _load_industry_threats(self) -> None:
        """Load industry-specific threats from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT threat_id, industry, threat_name, threat_type,
                       description, severity, first_observed, last_observed,
                       affected_organizations, attack_vectors, indicators,
                       compliance_frameworks, source, confidence_score
                FROM industry_threat_intel
                WHERE last_observed >= date('now', '-6 months')
            """)
            
            for row in cursor.fetchall():
                try:
                    industry = Industry(row[1])
                    
                    threat = IndustryThreat(
                        threat_id=row[0],
                        industry=industry,
                        threat_name=row[2],
                        threat_type=row[3],
                        description=row[4],
                        severity=ThreatSeverity(row[5]) if row[5] else ThreatSeverity.MEDIUM,
                        first_observed=datetime.fromisoformat(row[6]) if row[6] else None,
                        last_observed=datetime.fromisoformat(row[7]) if row[7] else None,
                        affected_organizations=json.loads(row[8]) if row[8] else [],
                        attack_vectors=json.loads(row[9]) if row[9] else [],
                        indicators=json.loads(row[10]) if row[10] else [],
                        compliance_impact=[ComplianceFramework(f) for f in json.loads(row[11])] if row[11] else [],
                        source=row[12] if row[12] else "",
                        confidence_score=row[13] if row[13] else 0.5
                    )
                    
                    if industry not in self.threats:
                        self.threats[industry] = []
                    self.threats[industry].append(threat)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid threat record: {e}")
            
            conn.close()
            
            total_threats = sum(len(t) for t in self.threats.values())
            logger.info(f"Loaded {total_threats} industry-specific threats")
            
        except Exception as e:
            logger.error(f"Error loading industry threats: {e}")
    
    def add_industry_threat(self, threat: IndustryThreat) -> int:
        """
        Add industry-specific threat to database
        
        Args:
            threat: IndustryThreat object
            
        Returns:
            threat_id
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO industry_threat_intel (
                    industry, threat_name, threat_type, description,
                    severity, first_observed, last_observed,
                    affected_organizations, attack_vectors, indicators,
                    compliance_frameworks, source, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                threat.industry.value,
                threat.threat_name,
                threat.threat_type,
                threat.description,
                threat.severity.value,
                threat.first_observed.isoformat() if threat.first_observed else None,
                threat.last_observed.isoformat() if threat.last_observed else None,
                json.dumps(threat.affected_organizations),
                json.dumps(threat.attack_vectors),
                json.dumps(threat.indicators),
                json.dumps([f.value for f in threat.compliance_impact]),
                threat.source,
                threat.confidence_score
            ))
            
            threat_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            threat.threat_id = threat_id
            
            if threat.industry not in self.threats:
                self.threats[threat.industry] = []
            self.threats[threat.industry].append(threat)
            
            logger.info(f"Added {threat.industry.value} threat: {threat.threat_name}")
            
            return threat_id
            
        except Exception as e:
            logger.error(f"Error adding industry threat: {e}")
            raise
    
    def get_industry_threats(
        self,
        industry: Industry,
        severity: Optional[ThreatSeverity] = None,
        days_back: int = 30
    ) -> List[IndustryThreat]:
        """
        Get threats for specific industry
        
        Args:
            industry: Industry sector
            severity: Optional severity filter
            days_back: Number of days to look back
            
        Returns:
            List of IndustryThreat objects
        """
        threats = self.threats.get(industry, [])
        
        # Filter by date
        cutoff = datetime.now() - timedelta(days=days_back)
        threats = [t for t in threats if t.last_observed and t.last_observed >= cutoff]
        
        # Filter by severity
        if severity:
            threats = [t for t in threats if t.severity == severity]
        
        return sorted(threats, key=lambda t: t.last_observed or datetime.min, reverse=True)
    
    def get_active_campaigns(self, industry: Industry) -> List[IndustryCampaign]:
        """Get active campaigns targeting specific industry"""
        return [c for c in self.campaigns.get(industry, []) if c.is_active]
    
    def get_relevant_actors(self, industry: Industry) -> List[str]:
        """Get threat actors known to target specific industry"""
        return self.INDUSTRY_ACTORS.get(industry, [])
    
    def get_compliance_frameworks(self, industry: Industry) -> List[ComplianceFramework]:
        """Get applicable compliance frameworks for industry"""
        return self.COMPLIANCE_MAPPING.get(industry, [])
    
    def get_attack_vectors(self, industry: Industry) -> List[str]:
        """Get common attack vectors for industry"""
        return self.ATTACK_VECTORS.get(industry, [])
    
    def analyze_industry_landscape(self, industry: Industry) -> Dict[str, Any]:
        """
        Comprehensive industry threat landscape analysis
        
        Args:
            industry: Industry sector
            
        Returns:
            Dictionary with landscape analysis
        """
        threats = self.get_industry_threats(industry, days_back=90)
        campaigns = self.get_active_campaigns(industry)
        
        # Severity distribution
        severity_dist = {}
        for threat in threats:
            sev = threat.severity.value
            severity_dist[sev] = severity_dist.get(sev, 0) + 1
        
        # Threat type distribution
        type_dist = {}
        for threat in threats:
            t_type = threat.threat_type
            type_dist[t_type] = type_dist.get(t_type, 0) + 1
        
        # Top attack vectors
        vector_count = {}
        for threat in threats:
            for vector in threat.attack_vectors:
                vector_count[vector] = vector_count.get(vector, 0) + 1
        
        top_vectors = sorted(vector_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Compliance impact
        compliance_impact = {}
        for threat in threats:
            for framework in threat.compliance_impact:
                fw = framework.value
                compliance_impact[fw] = compliance_impact.get(fw, 0) + 1
        
        return {
            'industry': industry.value,
            'analysis_period': '90 days',
            'total_threats': len(threats),
            'active_campaigns': len(campaigns),
            'severity_distribution': severity_dist,
            'threat_type_distribution': type_dist,
            'top_attack_vectors': [{'vector': v, 'count': c} for v, c in top_vectors],
            'compliance_impact': compliance_impact,
            'known_threat_actors': self.get_relevant_actors(industry),
            'applicable_frameworks': [f.value for f in self.get_compliance_frameworks(industry)],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_peer_breach_intelligence(
        self,
        industry: Industry,
        months_back: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get breach intelligence from peer organizations
        
        Args:
            industry: Industry sector
            months_back: Number of months to look back
            
        Returns:
            List of breach incidents
        """
        threats = self.get_industry_threats(industry, days_back=months_back * 30)
        
        breaches = []
        for threat in threats:
            if threat.affected_organizations:
                breach = {
                    'threat_name': threat.threat_name,
                    'date': threat.last_observed.isoformat() if threat.last_observed else None,
                    'severity': threat.severity.value,
                    'organizations_affected': len(threat.affected_organizations),
                    'attack_vectors': threat.attack_vectors,
                    'compliance_impact': [f.value for f in threat.compliance_impact]
                }
                breaches.append(breach)
        
        return sorted(breaches, key=lambda x: x['date'] or '', reverse=True)
    
    def prioritize_vulnerabilities_for_industry(
        self,
        industry: Industry,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize vulnerabilities based on industry context
        
        Args:
            industry: Industry sector
            vulnerabilities: List of vulnerability dicts
            
        Returns:
            Prioritized list with industry risk scores
        """
        relevant_actors = set(self.get_relevant_actors(industry))
        relevant_vectors = set(self.get_attack_vectors(industry))
        
        for vuln in vulnerabilities:
            industry_score = 0.0
            
            # Base CVSS score
            cvss = vuln.get('cvss_score', 0.0)
            industry_score += cvss * 10
            
            # Check if exploited by industry-relevant actors
            associated_actors = set(vuln.get('associated_actors', []))
            if associated_actors & relevant_actors:
                industry_score += 20
            
            # Check if relevant to common attack vectors
            vuln_vectors = set(vuln.get('attack_vectors', []))
            if vuln_vectors & relevant_vectors:
                industry_score += 15
            
            # Compliance criticality
            if vuln.get('compliance_critical', False):
                industry_score += 15
            
            # Exploit availability
            if vuln.get('exploited_in_wild', False):
                industry_score += 20
            elif vuln.get('has_exploit', False):
                industry_score += 10
            
            vuln['industry_risk_score'] = min(100.0, industry_score)
        
        return sorted(vulnerabilities, key=lambda x: x.get('industry_risk_score', 0), reverse=True)
    
    def get_industry_summary(self) -> Dict[str, Any]:
        """Get summary across all industries"""
        summary = {
            'total_industries_monitored': len(Industry),
            'by_industry': {}
        }
        
        for industry in Industry:
            threats = self.get_industry_threats(industry, days_back=30)
            campaigns = self.get_active_campaigns(industry)
            
            summary['by_industry'][industry.value] = {
                'threats_30_days': len(threats),
                'active_campaigns': len(campaigns),
                'known_actors': len(self.get_relevant_actors(industry)),
                'compliance_frameworks': len(self.get_compliance_frameworks(industry))
            }
        
        return summary


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize gatherer
    gatherer = IndustryIntelligenceGatherer()
    
    # Add sample threat
    threat = IndustryThreat(
        industry=Industry.FINANCIAL,
        threat_name="BEC Campaign Targeting Banks",
        threat_type="campaign",
        description="Business Email Compromise campaign targeting financial institutions",
        severity=ThreatSeverity.HIGH,
        first_observed=datetime.now() - timedelta(days=30),
        last_observed=datetime.now(),
        affected_organizations=["Bank A", "Credit Union B"],
        attack_vectors=["Phishing", "Business Email Compromise"],
        compliance_impact=[ComplianceFramework.SOX, ComplianceFramework.PCI_DSS],
        source="Financial ISAC",
        confidence_score=0.85
    )
    
    gatherer.add_industry_threat(threat)
    
    # Analyze financial sector
    print("\n=== Financial Sector Threat Landscape ===")
    landscape = gatherer.analyze_industry_landscape(Industry.FINANCIAL)
    print(f"Total Threats (90 days): {landscape['total_threats']}")
    print(f"Active Campaigns: {landscape['active_campaigns']}")
    print(f"Severity Distribution: {landscape['severity_distribution']}")
    print(f"Top Attack Vectors: {landscape['top_attack_vectors']}")
    
    # Get relevant actors for healthcare
    print("\n=== Healthcare Threat Actors ===")
    healthcare_actors = gatherer.get_relevant_actors(Industry.HEALTHCARE)
    print(f"Known Actors: {', '.join(healthcare_actors)}")
    
    # Get compliance frameworks for retail
    print("\n=== Retail Compliance Frameworks ===")
    retail_compliance = gatherer.get_compliance_frameworks(Industry.RETAIL)
    print(f"Applicable Frameworks: {', '.join([f.value for f in retail_compliance])}")
    
    # Summary across all industries
    print("\n=== Cross-Industry Summary ===")
    summary = gatherer.get_industry_summary()
    for industry, stats in summary['by_industry'].items():
        print(f"{industry}: {stats['threats_30_days']} threats, {stats['active_campaigns']} campaigns")
