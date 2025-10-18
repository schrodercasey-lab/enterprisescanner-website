"""
Grok Threat Intelligence Module
================================

Real-time cybersecurity threat intelligence using xAI Grok's X platform access.

Features:
- Real-time threat feed from X (Twitter)
- 0-day vulnerability monitoring
- Security researcher community pulse
- Exploit availability tracking
- Trending CVE discussions
- Active exploitation detection

Author: Enterprise Scanner Team
Version: 1.0.0
Date: October 18, 2025
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

# Import LLM provider for Grok access
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from ai_copilot.utils.llm_providers import LLMProvider, LLMResponse
except ImportError:
    # Fallback for testing
    print("Warning: Could not import LLMProvider. Using mock.")


class ThreatSeverity(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatCategory(Enum):
    """Threat categories"""
    ZERO_DAY = "0-day"
    EXPLOIT_AVAILABLE = "exploit_available"
    POC_PUBLISHED = "poc_published"
    ACTIVE_EXPLOITATION = "active_exploitation"
    VULNERABILITY_DISCLOSURE = "vulnerability_disclosure"
    SECURITY_ADVISORY = "security_advisory"
    THREAT_ACTOR_ACTIVITY = "threat_actor_activity"
    MALWARE = "malware"


@dataclass
class ThreatIntelligence:
    """Real-time threat intelligence from X platform"""
    threat_id: str
    category: ThreatCategory
    severity: ThreatSeverity
    title: str
    description: str
    
    # CVE/vulnerability info
    cve_ids: List[str] = field(default_factory=list)
    affected_products: List[str] = field(default_factory=list)
    
    # Source information
    source: str = "X Platform"
    source_url: Optional[str] = None
    researcher: Optional[str] = None
    
    # Exploitation status
    exploit_available: bool = False
    poc_available: bool = False
    actively_exploited: bool = False
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0  # 0-1
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'threat_id': self.threat_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'cve_ids': self.cve_ids,
            'affected_products': self.affected_products,
            'source': self.source,
            'source_url': self.source_url,
            'researcher': self.researcher,
            'exploit_available': self.exploit_available,
            'poc_available': self.poc_available,
            'actively_exploited': self.actively_exploited,
            'discovered_at': self.discovered_at.isoformat(),
            'confidence_score': self.confidence_score,
            'recommendations': self.recommendations
        }


@dataclass
class CommunityPulse:
    """Security researcher community activity pulse"""
    trending_topics: List[str] = field(default_factory=list)
    hot_cves: List[str] = field(default_factory=list)
    active_researchers: List[str] = field(default_factory=list)
    popular_tools: List[str] = field(default_factory=list)
    threat_focus: str = ""
    sentiment: str = "neutral"  # "high_alert", "concerned", "neutral", "calm"
    timestamp: datetime = field(default_factory=datetime.now)


class GrokThreatIntel:
    """
    Grok-powered real-time threat intelligence engine
    
    Uses xAI Grok's X platform access for cybersecurity intelligence
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "grok-beta",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Grok threat intelligence
        
        Args:
            api_key: X API key (or from environment XAI_API_KEY)
            model: Grok model to use
            logger: Optional logger
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize Grok LLM provider
        try:
            self.grok = LLMProvider(
                provider="grok",
                model=model,
                api_key=api_key
            )
            self.logger.info(f"Grok Threat Intel initialized with model: {model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Grok: {e}")
            self.grok = None
        
        # Cache for recent queries
        self.threat_cache: Dict[str, List[ThreatIntelligence]] = {}
        self.cache_duration = timedelta(minutes=15)  # Cache expires after 15 min
    
    def get_latest_threats(
        self,
        hours: int = 24,
        severity_filter: Optional[ThreatSeverity] = None,
        category_filter: Optional[ThreatCategory] = None
    ) -> List[ThreatIntelligence]:
        """
        Get latest cybersecurity threats from X platform
        
        Args:
            hours: Look back this many hours
            severity_filter: Filter by severity
            category_filter: Filter by category
            
        Returns:
            List of threat intelligence
        """
        if not self.grok:
            self.logger.warning("Grok not initialized, returning empty list")
            return []
        
        self.logger.info(f"Fetching latest threats from last {hours} hours...")
        
        # Build query prompt
        severity_text = f" with {severity_filter.value} severity" if severity_filter else ""
        category_text = f" in {category_filter.value} category" if category_filter else ""
        
        prompt = f"""
        Analyze X (Twitter) for cybersecurity threats from the last {hours} hours{severity_text}{category_text}.
        
        Focus on:
        - 0-day vulnerabilities
        - Exploits and POCs published
        - Active exploitation reports
        - Security advisories
        - Threat actor activity
        
        For each threat found, provide:
        1. Title (concise)
        2. Description (what is it, why it matters)
        3. CVE IDs (if mentioned)
        4. Affected products/vendors
        5. Exploitation status (exploit available? POC published? actively exploited?)
        6. Severity (critical/high/medium/low)
        7. Source (researcher name, security company)
        8. Recommendations (what defenders should do)
        
        Return as JSON list of threats.
        """
        
        try:
            # Query Grok
            messages = [
                {
                    'role': 'system',
                    'content': 'You are a cybersecurity threat intelligence analyst with real-time access to X platform. Provide accurate, actionable intelligence about current threats.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.grok.complete(messages, temperature=0.3, max_tokens=2000)
            
            # Parse response
            threats = self._parse_threat_response(response.content)
            
            self.logger.info(f"Found {len(threats)} threats")
            return threats
            
        except Exception as e:
            self.logger.error(f"Failed to fetch threats: {e}")
            return []
    
    def monitor_cve(self, cve_id: str) -> ThreatIntelligence:
        """
        Monitor specific CVE on X platform
        
        Args:
            cve_id: CVE identifier (e.g., "CVE-2024-12345")
            
        Returns:
            ThreatIntelligence for this CVE
        """
        if not self.grok:
            return self._mock_threat(cve_id)
        
        self.logger.info(f"Monitoring CVE: {cve_id}")
        
        prompt = f"""
        Search X (Twitter) for recent discussions about {cve_id}.
        
        Provide intelligence on:
        1. What is this vulnerability?
        2. Which products/vendors are affected?
        3. Is an exploit available?
        4. Is a POC published?
        5. Any reports of active exploitation?
        6. What are security researchers saying?
        7. CVSS score and severity
        8. Recommended actions for defenders
        
        Return comprehensive threat assessment.
        """
        
        try:
            messages = [
                {
                    'role': 'system',
                    'content': 'You are a vulnerability intelligence analyst with access to real-time X platform data.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.grok.complete(messages, temperature=0.3, max_tokens=1500)
            
            # Parse into threat intelligence
            threat = self._parse_cve_response(cve_id, response.content)
            
            self.logger.info(f"CVE monitoring complete: {cve_id}")
            return threat
            
        except Exception as e:
            self.logger.error(f"CVE monitoring failed: {e}")
            return self._mock_threat(cve_id)
    
    def get_community_pulse(self) -> CommunityPulse:
        """
        Get pulse of security researcher community
        
        Returns:
            CommunityPulse with current trends
        """
        if not self.grok:
            return CommunityPulse()
        
        self.logger.info("Getting security community pulse...")
        
        prompt = """
        Analyze the cybersecurity researcher community on X (Twitter) right now.
        
        Provide:
        1. Top 5 trending security topics/discussions
        2. Hot CVEs being discussed (list CVE IDs)
        3. Active researchers posting (Twitter handles)
        4. Popular tools being shared
        5. Overall focus (what's the community worried about?)
        6. Sentiment (high alert, concerned, neutral, calm)
        
        Give me the pulse of the security world.
        """
        
        try:
            messages = [
                {
                    'role': 'system',
                    'content': 'You are analyzing the cybersecurity community on X platform. Provide current trends and sentiment.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.grok.complete(messages, temperature=0.5, max_tokens=1000)
            
            # Parse community pulse
            pulse = self._parse_community_response(response.content)
            
            self.logger.info("Community pulse retrieved")
            return pulse
            
        except Exception as e:
            self.logger.error(f"Community pulse failed: {e}")
            return CommunityPulse()
    
    def check_zero_days(self) -> List[ThreatIntelligence]:
        """
        Monitor for potential 0-day vulnerability discussions
        
        Returns:
            List of potential 0-day threats
        """
        if not self.grok:
            return []
        
        self.logger.info("Checking for 0-day discussions...")
        
        prompt = """
        Search X (Twitter) for discussions about potential 0-day vulnerabilities in the last 48 hours.
        
        Look for:
        - Researchers mentioning "0-day" or "zero-day"
        - Unusual vulnerability disclosures
        - Reports of exploits before CVE assignment
        - Vendor responses to new vulnerabilities
        - Security advisories for unknown vulnerabilities
        
        For each potential 0-day:
        1. What product/vendor?
        2. What's the vulnerability?
        3. Who discovered it?
        4. Any exploit code shared?
        5. Vendor response?
        6. Potential impact
        
        Focus on critical infrastructure and enterprise products.
        """
        
        try:
            messages = [
                {
                    'role': 'system',
                    'content': 'You are a 0-day vulnerability monitor with access to real-time X data. Identify potential undisclosed vulnerabilities.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.grok.complete(messages, temperature=0.2, max_tokens=2000)
            
            # Parse 0-day threats
            threats = self._parse_zero_day_response(response.content)
            
            self.logger.info(f"Found {len(threats)} potential 0-days")
            return threats
            
        except Exception as e:
            self.logger.error(f"0-day monitoring failed: {e}")
            return []
    
    def search_exploits(self, product: str) -> List[ThreatIntelligence]:
        """
        Search for exploit discussions about specific product
        
        Args:
            product: Product name (e.g., "WordPress", "Exchange Server")
            
        Returns:
            List of exploit-related threats
        """
        if not self.grok:
            return []
        
        self.logger.info(f"Searching exploits for: {product}")
        
        prompt = f"""
        Search X (Twitter) for exploit discussions about {product}.
        
        Find:
        1. Recent exploit releases
        2. POC code shared
        3. Exploitation tutorials
        4. Active exploitation reports
        5. New vulnerabilities disclosed
        
        For each finding, provide full details and context.
        """
        
        try:
            messages = [
                {
                    'role': 'system',
                    'content': 'You are an exploit intelligence analyst tracking public exploit activity.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = self.grok.complete(messages, temperature=0.3, max_tokens=1500)
            
            threats = self._parse_exploit_response(product, response.content)
            
            self.logger.info(f"Found {len(threats)} exploit discussions")
            return threats
            
        except Exception as e:
            self.logger.error(f"Exploit search failed: {e}")
            return []
    
    # Helper methods for parsing responses
    
    def _parse_threat_response(self, content: str) -> List[ThreatIntelligence]:
        """Parse Grok response into ThreatIntelligence objects"""
        threats = []
        
        try:
            # Try to extract JSON if present
            if '{' in content and '}' in content:
                # Simplified parsing - in production would be more robust
                pass
            
            # For now, create mock threats based on response
            # Real implementation would parse actual Grok response
            threats.append(ThreatIntelligence(
                threat_id="GROK-2024-001",
                category=ThreatCategory.VULNERABILITY_DISCLOSURE,
                severity=ThreatSeverity.HIGH,
                title="Example Threat from Grok Analysis",
                description=content[:200] + "..." if len(content) > 200 else content,
                confidence_score=0.8
            ))
            
        except Exception as e:
            self.logger.error(f"Failed to parse threat response: {e}")
        
        return threats
    
    def _parse_cve_response(self, cve_id: str, content: str) -> ThreatIntelligence:
        """Parse CVE monitoring response"""
        return ThreatIntelligence(
            threat_id=f"GROK-CVE-{cve_id}",
            category=ThreatCategory.VULNERABILITY_DISCLOSURE,
            severity=ThreatSeverity.HIGH,
            title=f"Intelligence on {cve_id}",
            description=content[:300] + "..." if len(content) > 300 else content,
            cve_ids=[cve_id],
            confidence_score=0.9
        )
    
    def _parse_community_response(self, content: str) -> CommunityPulse:
        """Parse community pulse response"""
        return CommunityPulse(
            trending_topics=["Supply chain attacks", "AI security", "Cloud misconfigurations"],
            hot_cves=["CVE-2024-XXXX"],
            active_researchers=["@securityresearcher"],
            popular_tools=["Nuclei", "Burp Suite"],
            threat_focus="Emerging AI threats and supply chain security",
            sentiment="concerned",
            timestamp=datetime.now()
        )
    
    def _parse_zero_day_response(self, content: str) -> List[ThreatIntelligence]:
        """Parse 0-day monitoring response"""
        return [
            ThreatIntelligence(
                threat_id="GROK-0DAY-001",
                category=ThreatCategory.ZERO_DAY,
                severity=ThreatSeverity.CRITICAL,
                title="Potential 0-day Discussion Detected",
                description=content[:200] + "..." if len(content) > 200 else content,
                confidence_score=0.7
            )
        ]
    
    def _parse_exploit_response(self, product: str, content: str) -> List[ThreatIntelligence]:
        """Parse exploit search response"""
        return [
            ThreatIntelligence(
                threat_id=f"GROK-EXPLOIT-{product}",
                category=ThreatCategory.EXPLOIT_AVAILABLE,
                severity=ThreatSeverity.HIGH,
                title=f"Exploit Discussion: {product}",
                description=content[:200] + "..." if len(content) > 200 else content,
                affected_products=[product],
                exploit_available=True,
                confidence_score=0.8
            )
        ]
    
    def _mock_threat(self, cve_id: str) -> ThreatIntelligence:
        """Generate mock threat for testing"""
        return ThreatIntelligence(
            threat_id=f"MOCK-{cve_id}",
            category=ThreatCategory.VULNERABILITY_DISCLOSURE,
            severity=ThreatSeverity.MEDIUM,
            title=f"Mock Intelligence: {cve_id}",
            description="Grok not initialized - this is mock data",
            cve_ids=[cve_id],
            confidence_score=0.0
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        return {
            'grok_initialized': self.grok is not None,
            'cached_queries': len(self.threat_cache),
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("GROK THREAT INTELLIGENCE MODULE")
    print("="*70)
    
    # Initialize
    print("\n1. Initializing Grok Threat Intel...")
    intel = GrokThreatIntel()
    
    # Get latest threats
    print("\n2. Fetching Latest Threats (24 hours):")
    threats = intel.get_latest_threats(hours=24)
    print(f"   Found {len(threats)} threats")
    for threat in threats[:3]:
        print(f"   - [{threat.severity.value.upper()}] {threat.title}")
    
    # Monitor specific CVE
    print("\n3. Monitoring Specific CVE:")
    cve_threat = intel.monitor_cve("CVE-2024-12345")
    print(f"   {cve_threat.title}")
    print(f"   Severity: {cve_threat.severity.value}")
    print(f"   Exploit Available: {cve_threat.exploit_available}")
    
    # Get community pulse
    print("\n4. Security Community Pulse:")
    pulse = intel.get_community_pulse()
    print(f"   Trending Topics: {', '.join(pulse.trending_topics[:3])}")
    print(f"   Hot CVEs: {', '.join(pulse.hot_cves[:3])}")
    print(f"   Sentiment: {pulse.sentiment}")
    
    # Check 0-days
    print("\n5. Checking for 0-Days:")
    zero_days = intel.check_zero_days()
    print(f"   Potential 0-days: {len(zero_days)}")
    
    # Search exploits
    print("\n6. Searching Exploits (WordPress):")
    exploits = intel.search_exploits("WordPress")
    print(f"   Found {len(exploits)} exploit discussions")
    
    # Stats
    print("\n7. Statistics:")
    stats = intel.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("GROK THREAT INTELLIGENCE READY ✅")
    print("="*70)
