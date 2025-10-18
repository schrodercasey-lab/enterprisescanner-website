"""
Scan Analyzer Module

AI-powered security scan analysis and explanation system.
This is the KILLER FEATURE of the AI Copilot.

Features:
- Explain vulnerabilities in plain English
- Analyze complete scan results
- Risk prioritization with business context
- Trend analysis (comparing multiple scans)
- Executive summaries for leadership
- Natural language queries about scan data

Integration:
- Connects to Enterprise Scanner scan database
- Analyzes Nmap, Nessus, OpenVAS, custom scan results
- Correlates vulnerabilities across assets
- Maps to compliance frameworks

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging


class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskLevel(Enum):
    """Business risk levels"""
    EXTREME = "extreme"  # Critical + exploitable + valuable asset
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class Vulnerability:
    """Single vulnerability"""
    vuln_id: str
    name: str
    description: str
    severity: SeverityLevel
    cvss_score: float
    
    # Affected asset
    asset_id: str
    asset_name: str
    asset_type: str  # 'server', 'web_app', 'database', 'network_device'
    
    # Technical details
    cve_ids: List[str] = field(default_factory=list)
    cwe_ids: List[str] = field(default_factory=list)
    port: Optional[int] = None
    service: Optional[str] = None
    
    # Exploit information
    exploit_available: bool = False
    exploited_in_wild: bool = False
    
    # Remediation
    remediation: Optional[str] = None
    patch_available: bool = False
    
    # Business context
    asset_criticality: str = "medium"  # 'critical', 'high', 'medium', 'low'
    data_sensitivity: str = "medium"  # Sensitivity of data on asset
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    scan_id: str = ""


@dataclass
class ScanResult:
    """Complete scan result"""
    scan_id: str
    scan_name: str
    scan_type: str  # 'network', 'web_app', 'infrastructure', 'compliance'
    
    # Scope
    target_assets: List[str]
    asset_count: int
    
    # Results
    vulnerabilities: List[Vulnerability]
    
    # Summary statistics
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    
    # Scan metadata
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: int = 0
    
    # Compliance
    compliance_frameworks: List[str] = field(default_factory=list)
    compliance_score: Optional[float] = None


@dataclass
class ScanAnalysis:
    """AI-generated scan analysis"""
    scan_id: str
    analysis_text: str
    
    # Key findings
    critical_issues: List[str]
    quick_wins: List[str]  # Easy fixes with high impact
    
    # Risk assessment
    overall_risk: RiskLevel
    risk_score: float  # 0-100
    
    # Priorities
    top_priorities: List[Dict[str, Any]]  # Top vulnerabilities to fix
    
    # Executive summary
    executive_summary: str
    
    # Recommendations
    immediate_actions: List[str]
    short_term_actions: List[str]
    long_term_actions: List[str]
    
    # Compliance impact
    compliance_issues: List[str]
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0


class ScanAnalyzer:
    """
    AI-powered scan analysis system
    
    This is the killer feature that makes Enterprise Scanner unique
    """
    
    def __init__(self, llm_provider=None, rag_system=None):
        """
        Initialize scan analyzer
        
        Args:
            llm_provider: LLMProvider instance
            rag_system: RAGSystem instance for context
        """
        self.logger = logging.getLogger(__name__)
        
        self.llm_provider = llm_provider
        self.rag_system = rag_system
        
        # Initialize if not provided
        if not self.llm_provider:
            try:
                from backend.ai_copilot.utils.llm_providers import LLMProvider
                self.llm_provider = LLMProvider(provider="openai", model="gpt-4-turbo")
            except Exception as e:
                self.logger.warning(f"LLM provider not available: {e}")
        
        if not self.rag_system:
            try:
                from backend.ai_copilot.knowledge.rag_system import RAGSystem
                self.rag_system = RAGSystem()
            except Exception as e:
                self.logger.warning(f"RAG system not available: {e}")
        
        # Statistics
        self.stats = {
            'total_analyses': 0,
            'scans_analyzed': 0,
            'vulnerabilities_explained': 0,
            'avg_analysis_time_ms': 0
        }
        
        self.logger.info("ScanAnalyzer initialized")
    
    def analyze_scan(self, scan_result: ScanResult) -> ScanAnalysis:
        """
        Analyze complete scan results
        
        Generates comprehensive AI analysis with:
        - Risk assessment
        - Prioritization
        - Executive summary
        - Action plan
        
        Args:
            scan_result: ScanResult object
            
        Returns:
            ScanAnalysis object
        """
        start_time = time.time()
        self.stats['total_analyses'] += 1
        self.stats['scans_analyzed'] += 1
        
        try:
            # Build analysis prompt
            prompt = self._build_scan_analysis_prompt(scan_result)
            
            # Get AI analysis
            messages = [
                {'role': 'system', 'content': 'You are an expert security analyst. Provide clear, actionable analysis.'},
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.llm_provider.complete(messages, temperature=0.3, max_tokens=2000)
            
            # Extract structured insights
            analysis = self._parse_scan_analysis(response.content, scan_result)
            
            # Calculate metrics
            analysis_time = int((time.time() - start_time) * 1000)
            self.stats['avg_analysis_time_ms'] = (
                (self.stats['avg_analysis_time_ms'] * (self.stats['total_analyses'] - 1) + analysis_time)
                / self.stats['total_analyses']
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Scan analysis failed: {e}", exc_info=True)
            
            # Return basic analysis
            return ScanAnalysis(
                scan_id=scan_result.scan_id,
                analysis_text=f"Analysis failed: {str(e)}",
                critical_issues=[],
                quick_wins=[],
                overall_risk=RiskLevel.MODERATE,
                risk_score=50.0,
                top_priorities=[],
                executive_summary="Analysis unavailable",
                immediate_actions=[],
                short_term_actions=[],
                long_term_actions=[],
                compliance_issues=[]
            )
    
    def explain_vulnerability(
        self,
        vulnerability: Vulnerability,
        target_audience: str = "technical"
    ) -> str:
        """
        Explain vulnerability in plain English
        
        Args:
            vulnerability: Vulnerability object
            target_audience: 'executive', 'technical', 'developer'
            
        Returns:
            Plain English explanation
        """
        self.stats['vulnerabilities_explained'] += 1
        
        try:
            # Use RAG to get relevant context about this vulnerability type
            if self.rag_system:
                rag_response = self.rag_system.generate(
                    query=f"Explain {vulnerability.name} vulnerability",
                    doc_types=['documentation', 'cve'],
                    system_prompt=f"Explain this vulnerability for a {target_audience} audience."
                )
                
                return rag_response.answer
            else:
                # Fallback to direct LLM
                prompt = self._build_vulnerability_explanation_prompt(vulnerability, target_audience)
                
                messages = [
                    {'role': 'system', 'content': f'You are explaining security vulnerabilities to a {target_audience} audience.'},
                    {'role': 'user', 'content': prompt}
                ]
                
                response = self.llm_provider.complete(messages, temperature=0.5, max_tokens=500)
                return response.content
                
        except Exception as e:
            self.logger.error(f"Vulnerability explanation failed: {e}")
            return f"Unable to explain vulnerability: {str(e)}"
    
    def prioritize_vulnerabilities(
        self,
        vulnerabilities: List[Vulnerability],
        business_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioritize vulnerabilities with business context
        
        Considers:
        - CVSS score
        - Exploitability
        - Asset criticality
        - Compliance impact
        - Remediation effort
        
        Args:
            vulnerabilities: List of vulnerabilities
            business_context: Business priorities, compliance requirements
            
        Returns:
            Prioritized list with risk scores
        """
        prioritized = []
        
        for vuln in vulnerabilities:
            # Calculate risk score (0-100)
            risk_score = self._calculate_risk_score(vuln, business_context)
            
            # Estimate remediation effort
            effort = self._estimate_remediation_effort(vuln)
            
            # Calculate priority (impact vs effort)
            priority_score = risk_score / max(effort, 1)
            
            prioritized.append({
                'vulnerability': vuln,
                'risk_score': risk_score,
                'remediation_effort': effort,
                'priority_score': priority_score,
                'justification': self._generate_priority_justification(vuln, risk_score)
            })
        
        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized
    
    def compare_scans(
        self,
        scan1: ScanResult,
        scan2: ScanResult
    ) -> Dict[str, Any]:
        """
        Compare two scans (trend analysis)
        
        Shows:
        - New vulnerabilities
        - Fixed vulnerabilities
        - Severity changes
        - Overall security posture improvement/decline
        
        Args:
            scan1: First scan (older)
            scan2: Second scan (newer)
            
        Returns:
            Comparison analysis
        """
        # Extract vulnerability IDs
        vulns1 = {v.vuln_id: v for v in scan1.vulnerabilities}
        vulns2 = {v.vuln_id: v for v in scan2.vulnerabilities}
        
        # Find differences
        new_vulns = [v for vid, v in vulns2.items() if vid not in vulns1]
        fixed_vulns = [v for vid, v in vulns1.items() if vid not in vulns2]
        persistent_vulns = [v for vid, v in vulns2.items() if vid in vulns1]
        
        # Calculate trend
        severity_score1 = self._calculate_severity_score(scan1)
        severity_score2 = self._calculate_severity_score(scan2)
        trend = "improving" if severity_score2 < severity_score1 else "declining" if severity_score2 > severity_score1 else "stable"
        
        return {
            'scan1_id': scan1.scan_id,
            'scan2_id': scan2.scan_id,
            'new_vulnerabilities': len(new_vulns),
            'fixed_vulnerabilities': len(fixed_vulns),
            'persistent_vulnerabilities': len(persistent_vulns),
            'new_critical': sum(1 for v in new_vulns if v.severity == SeverityLevel.CRITICAL),
            'fixed_critical': sum(1 for v in fixed_vulns if v.severity == SeverityLevel.CRITICAL),
            'severity_score_change': severity_score2 - severity_score1,
            'trend': trend,
            'improvement_percentage': ((severity_score1 - severity_score2) / severity_score1 * 100) if severity_score1 > 0 else 0,
            'details': {
                'new': new_vulns[:5],  # Top 5 new vulns
                'fixed': fixed_vulns[:5]  # Top 5 fixed vulns
            }
        }
    
    def generate_executive_summary(
        self,
        scan_result: ScanResult,
        include_recommendations: bool = True
    ) -> str:
        """
        Generate executive summary for leadership
        
        Non-technical, business-focused summary
        
        Args:
            scan_result: ScanResult object
            include_recommendations: Whether to include action items
            
        Returns:
            Executive summary text
        """
        try:
            prompt = f"""
Generate an executive summary for this security scan:

Scan: {scan_result.scan_name}
Assets Scanned: {scan_result.asset_count}
Critical Issues: {scan_result.critical_count}
High Severity: {scan_result.high_count}
Medium Severity: {scan_result.medium_count}

The summary should:
- Be 2-3 paragraphs
- Use business language (not technical jargon)
- Focus on business risk and impact
- {"Include 3-5 key recommendations" if include_recommendations else "Focus only on findings"}
- Be suitable for C-level executives

Do not use technical terms like CVE, CVSS, etc. Instead, explain business impact.
"""
            
            messages = [
                {'role': 'system', 'content': 'You are writing for business executives with no technical background.'},
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.llm_provider.complete(messages, temperature=0.5, max_tokens=600)
            return response.content
            
        except Exception as e:
            self.logger.error(f"Executive summary generation failed: {e}")
            return "Executive summary unavailable"
    
    def _build_scan_analysis_prompt(self, scan_result: ScanResult) -> str:
        """Build prompt for scan analysis"""
        # Summarize vulnerabilities
        vuln_summary = []
        for vuln in scan_result.vulnerabilities[:20]:  # Top 20
            vuln_summary.append(
                f"- {vuln.name} (Severity: {vuln.severity.value}, CVSS: {vuln.cvss_score}, "
                f"Asset: {vuln.asset_name})"
            )
        
        prompt = f"""
Analyze this security scan and provide comprehensive insights:

SCAN DETAILS:
- Scan ID: {scan_result.scan_id}
- Scan Type: {scan_result.scan_type}
- Assets Scanned: {scan_result.asset_count}
- Duration: {scan_result.duration_seconds}s

VULNERABILITY SUMMARY:
- Critical: {scan_result.critical_count}
- High: {scan_result.high_count}
- Medium: {scan_result.medium_count}
- Low: {scan_result.low_count}

TOP VULNERABILITIES:
{chr(10).join(vuln_summary[:10])}

Provide:
1. Overall risk assessment
2. Top 3 critical issues requiring immediate attention
3. Top 3 "quick wins" (easy fixes with high impact)
4. Executive summary (2-3 sentences for leadership)
5. Immediate actions (next 24-48 hours)
6. Short-term actions (next 1-2 weeks)
7. Long-term recommendations
8. Compliance concerns

Be specific and actionable.
"""
        return prompt
    
    def _build_vulnerability_explanation_prompt(
        self,
        vuln: Vulnerability,
        audience: str
    ) -> str:
        """Build prompt for vulnerability explanation"""
        return f"""
Explain this vulnerability for a {audience} audience:

Name: {vuln.name}
Severity: {vuln.severity.value} (CVSS: {vuln.cvss_score})
Affected Asset: {vuln.asset_name} ({vuln.asset_type})
CVE IDs: {', '.join(vuln.cve_ids) if vuln.cve_ids else 'None'}

Explanation should include:
1. What this vulnerability is (simple terms)
2. Why it's dangerous
3. How it could be exploited
4. Business impact
5. How to fix it

Keep it {"non-technical and business-focused" if audience == "executive" else "clear and actionable"}.
2-3 paragraphs maximum.
"""
    
    def _parse_scan_analysis(self, analysis_text: str, scan_result: ScanResult) -> ScanAnalysis:
        """Parse LLM response into structured analysis"""
        # Simple parsing (in production, use structured output or JSON mode)
        
        # Extract sections (very basic)
        critical_issues = []
        quick_wins = []
        immediate_actions = []
        
        # For now, return structured with the full text
        # In production, parse sections properly
        
        risk_score = self._calculate_overall_risk_score(scan_result)
        risk_level = self._risk_score_to_level(risk_score)
        
        return ScanAnalysis(
            scan_id=scan_result.scan_id,
            analysis_text=analysis_text,
            critical_issues=critical_issues,
            quick_wins=quick_wins,
            overall_risk=risk_level,
            risk_score=risk_score,
            top_priorities=[],
            executive_summary=analysis_text[:200] + "...",
            immediate_actions=immediate_actions,
            short_term_actions=[],
            long_term_actions=[],
            compliance_issues=[]
        )
    
    def _calculate_risk_score(
        self,
        vuln: Vulnerability,
        business_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate risk score for vulnerability (0-100)"""
        # Base score from CVSS
        score = vuln.cvss_score * 10  # Scale to 0-100
        
        # Adjust for asset criticality
        criticality_multiplier = {
            'critical': 1.5,
            'high': 1.3,
            'medium': 1.0,
            'low': 0.7
        }
        score *= criticality_multiplier.get(vuln.asset_criticality, 1.0)
        
        # Adjust for exploitability
        if vuln.exploit_available:
            score *= 1.3
        if vuln.exploited_in_wild:
            score *= 1.5
        
        # Cap at 100
        return min(score, 100.0)
    
    def _estimate_remediation_effort(self, vuln: Vulnerability) -> int:
        """Estimate remediation effort (1-10 scale)"""
        # Simple heuristic
        if vuln.patch_available:
            return 2  # Easy: apply patch
        elif vuln.remediation:
            return 5  # Medium: follow guidance
        else:
            return 8  # Hard: requires investigation
    
    def _generate_priority_justification(
        self,
        vuln: Vulnerability,
        risk_score: float
    ) -> str:
        """Generate human-readable priority justification"""
        reasons = []
        
        if risk_score > 80:
            reasons.append("extremely high risk")
        elif risk_score > 60:
            reasons.append("high risk")
        
        if vuln.exploit_available:
            reasons.append("exploit publicly available")
        
        if vuln.asset_criticality == "critical":
            reasons.append("affects critical asset")
        
        if vuln.patch_available:
            reasons.append("patch available (easy fix)")
        
        return ", ".join(reasons) if reasons else "standard priority"
    
    def _calculate_severity_score(self, scan_result: ScanResult) -> float:
        """Calculate overall severity score for scan"""
        return (
            scan_result.critical_count * 10 +
            scan_result.high_count * 5 +
            scan_result.medium_count * 2 +
            scan_result.low_count * 1
        )
    
    def _calculate_overall_risk_score(self, scan_result: ScanResult) -> float:
        """Calculate overall risk score (0-100)"""
        severity = self._calculate_severity_score(scan_result)
        max_possible = scan_result.asset_count * 50  # Assuming worst case
        
        if max_possible == 0:
            return 0.0
        
        score = (severity / max_possible) * 100
        return min(score, 100.0)
    
    def _risk_score_to_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score >= 80:
            return RiskLevel.EXTREME
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MODERATE
        elif score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def get_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        return self.stats.copy()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("SCAN ANALYZER MODULE - KILLER FEATURE")
    print("="*70)
    
    # Create mock scan data
    print("\n1. Creating Mock Scan Data...")
    
    vuln1 = Vulnerability(
        vuln_id="vuln_001",
        name="SQL Injection in Login Form",
        description="Unvalidated input in login form",
        severity=SeverityLevel.CRITICAL,
        cvss_score=9.8,
        asset_id="web_001",
        asset_name="customer-portal.example.com",
        asset_type="web_app",
        cve_ids=["CVE-2024-1234"],
        exploit_available=True,
        asset_criticality="critical"
    )
    
    vuln2 = Vulnerability(
        vuln_id="vuln_002",
        name="Outdated Apache Server",
        description="Apache 2.4.45 with known vulnerabilities",
        severity=SeverityLevel.HIGH,
        cvss_score=7.5,
        asset_id="server_001",
        asset_name="web-server-01",
        asset_type="server",
        patch_available=True,
        asset_criticality="high"
    )
    
    scan = ScanResult(
        scan_id="scan_001",
        scan_name="Production Infrastructure Scan",
        scan_type="infrastructure",
        target_assets=["customer-portal.example.com", "web-server-01"],
        asset_count=2,
        vulnerabilities=[vuln1, vuln2],
        critical_count=1,
        high_count=1,
        medium_count=3,
        low_count=5,
        duration_seconds=3600
    )
    
    # Initialize analyzer
    print("\n2. Initializing Scan Analyzer...")
    analyzer = ScanAnalyzer()
    
    # Test prioritization
    print("\n3. Testing Vulnerability Prioritization...")
    priorities = analyzer.prioritize_vulnerabilities([vuln1, vuln2])
    
    for i, p in enumerate(priorities, 1):
        print(f"\n   Priority #{i}:")
        print(f"   Vulnerability: {p['vulnerability'].name}")
        print(f"   Risk Score: {p['risk_score']:.1f}")
        print(f"   Effort: {p['remediation_effort']}/10")
        print(f"   Priority Score: {p['priority_score']:.2f}")
        print(f"   Justification: {p['justification']}")
    
    # Statistics
    print("\n4. Analyzer Statistics:")
    stats = analyzer.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("SCAN ANALYZER MODULE COMPLETE ✅")
    print("="*70)
