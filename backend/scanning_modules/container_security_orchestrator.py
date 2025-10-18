"""
Container Security Orchestration Module
Unified interface for Docker and Kubernetes security scanning

This module provides a single interface for comprehensive container security assessment:
- Docker container and image security
- Kubernetes cluster security
- Container registry scanning
- Unified reporting across container platforms
- Compliance framework mapping

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Import container scanners with graceful fallback
try:
    from .container_security_docker import DockerSecurityScanner, DOCKER_AVAILABLE
except ImportError:
    DockerSecurityScanner = None
    DOCKER_AVAILABLE = False

try:
    from .container_security_k8s import KubernetesSecurityScanner, KUBERNETES_AVAILABLE
except ImportError:
    KubernetesSecurityScanner = None
    KUBERNETES_AVAILABLE = False


@dataclass
class ContainerScanResult:
    """Unified container security scan result"""
    scan_timestamp: str
    platforms_scanned: List[str]  # ['docker', 'kubernetes']
    total_findings: int
    severity_breakdown: Dict[str, int]
    risk_score: float  # 0-100
    security_posture: str  # CRITICAL, POOR, FAIR, GOOD, EXCELLENT
    findings_by_platform: Dict[str, List[Dict]]
    findings_by_severity: Dict[str, List[Dict]]
    compliance_coverage: Dict[str, int]
    recommendations: List[str]


class ContainerSecurityOrchestrator:
    """
    Container Security Orchestration
    
    Unified interface for multi-platform container security assessment.
    Supports Docker containers/images and Kubernetes clusters.
    
    Features:
    - Automatic platform detection
    - Graceful degradation when SDKs unavailable
    - Unified finding format across platforms
    - Compliance framework aggregation
    - Risk scoring and prioritization
    """
    
    def __init__(self):
        """Initialize container security orchestrator"""
        self.docker_scanner = None
        self.k8s_scanner = None
        self.platforms_configured = []
        
        # Initialize available scanners
        if DOCKER_AVAILABLE and DockerSecurityScanner:
            self.docker_scanner = DockerSecurityScanner()
            if self.docker_scanner.client:
                self.platforms_configured.append('docker')
        
        if KUBERNETES_AVAILABLE and KubernetesSecurityScanner:
            # K8s scanner initialized on-demand with kubeconfig
            pass
    
    def configure_docker(self):
        """
        Configure Docker scanner
        
        Docker client automatically connects to local Docker daemon.
        """
        if not DOCKER_AVAILABLE:
            raise ImportError("Docker SDK not available. Install: pip install docker")
        
        if not self.docker_scanner:
            self.docker_scanner = DockerSecurityScanner()
        
        if self.docker_scanner.client and 'docker' not in self.platforms_configured:
            self.platforms_configured.append('docker')
    
    def configure_kubernetes(self, kubeconfig_path: Optional[str] = None):
        """
        Configure Kubernetes scanner
        
        Args:
            kubeconfig_path: Path to kubeconfig file (None = use default/in-cluster)
        """
        if not KUBERNETES_AVAILABLE:
            raise ImportError("Kubernetes SDK not available. Install: pip install kubernetes")
        
        self.k8s_scanner = KubernetesSecurityScanner(kubeconfig_path)
        
        if self.k8s_scanner.v1 and 'kubernetes' not in self.platforms_configured:
            self.platforms_configured.append('kubernetes')
    
    def scan_all_platforms(self) -> ContainerScanResult:
        """
        Run comprehensive container security assessment across all configured platforms
        
        Returns:
            ContainerScanResult with unified findings
        """
        docker_results = None
        k8s_results = None
        
        # Scan Docker if available
        if 'docker' in self.platforms_configured and self.docker_scanner:
            try:
                docker_results = self.docker_scanner.scan_all()
            except Exception as e:
                print(f"Docker scan failed: {e}")
        
        # Scan Kubernetes if available
        if 'kubernetes' in self.platforms_configured and self.k8s_scanner:
            try:
                k8s_results = self.k8s_scanner.scan_all()
            except Exception as e:
                print(f"Kubernetes scan failed: {e}")
        
        return self._generate_unified_results(docker_results, k8s_results)
    
    def scan_docker_only(self) -> Dict[str, Any]:
        """
        Run Docker-only security assessment
        
        Returns:
            Docker scan results
        """
        if 'docker' not in self.platforms_configured or not self.docker_scanner:
            return {
                'error': 'Docker scanner not configured or not available',
                'findings': [],
                'risk_score': 0
            }
        
        return self.docker_scanner.scan_all()
    
    def scan_kubernetes_only(self) -> Dict[str, Any]:
        """
        Run Kubernetes-only security assessment
        
        Returns:
            Kubernetes scan results
        """
        if 'kubernetes' not in self.platforms_configured or not self.k8s_scanner:
            return {
                'error': 'Kubernetes scanner not configured or not available',
                'findings': [],
                'risk_score': 0
            }
        
        return self.k8s_scanner.scan_all()
    
    def _generate_unified_results(
        self,
        docker_results: Optional[Dict[str, Any]],
        k8s_results: Optional[Dict[str, Any]]
    ) -> ContainerScanResult:
        """
        Generate unified container security assessment results
        
        Args:
            docker_results: Docker scan results
            k8s_results: Kubernetes scan results
        
        Returns:
            ContainerScanResult with aggregated findings
        """
        platforms_scanned = []
        findings_by_platform = {}
        all_findings = []
        compliance_coverage = {}
        
        # Aggregate Docker results
        if docker_results and 'error' not in docker_results:
            platforms_scanned.append('docker')
            findings_by_platform['docker'] = docker_results.get('findings', [])
            all_findings.extend(docker_results.get('findings', []))
            
            # Merge compliance coverage
            for framework, count in docker_results.get('compliance_coverage', {}).items():
                compliance_coverage[framework] = compliance_coverage.get(framework, 0) + count
        
        # Aggregate Kubernetes results
        if k8s_results and 'error' not in k8s_results:
            platforms_scanned.append('kubernetes')
            findings_by_platform['kubernetes'] = k8s_results.get('findings', [])
            all_findings.extend(k8s_results.get('findings', []))
            
            # Merge compliance coverage
            for framework, count in k8s_results.get('compliance_coverage', {}).items():
                compliance_coverage[framework] = compliance_coverage.get(framework, 0) + count
        
        # Calculate unified severity breakdown
        severity_breakdown = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        findings_by_severity = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }
        
        for finding in all_findings:
            severity = finding.get('severity', 'LOW')
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
            findings_by_severity[severity].append(finding)
        
        # Calculate unified risk score (weighted average if both platforms scanned)
        if docker_results and k8s_results and 'error' not in docker_results and 'error' not in k8s_results:
            # Weighted: Docker 40%, Kubernetes 60% (K8s typically more complex/critical)
            docker_risk = docker_results.get('risk_score', 0)
            k8s_risk = k8s_results.get('risk_score', 0)
            overall_risk_score = (docker_risk * 0.4) + (k8s_risk * 0.6)
        elif docker_results and 'error' not in docker_results:
            overall_risk_score = docker_results.get('risk_score', 0)
        elif k8s_results and 'error' not in k8s_results:
            overall_risk_score = k8s_results.get('risk_score', 0)
        else:
            overall_risk_score = 0
        
        # Determine overall security posture
        if overall_risk_score >= 80:
            security_posture = 'CRITICAL'
        elif overall_risk_score >= 60:
            security_posture = 'POOR'
        elif overall_risk_score >= 40:
            security_posture = 'FAIR'
        elif overall_risk_score >= 20:
            security_posture = 'GOOD'
        else:
            security_posture = 'EXCELLENT'
        
        # Generate unified recommendations
        recommendations = self._generate_unified_recommendations(
            severity_breakdown,
            platforms_scanned,
            docker_results,
            k8s_results
        )
        
        return ContainerScanResult(
            scan_timestamp=datetime.utcnow().isoformat(),
            platforms_scanned=platforms_scanned,
            total_findings=len(all_findings),
            severity_breakdown=severity_breakdown,
            risk_score=overall_risk_score,
            security_posture=security_posture,
            findings_by_platform=findings_by_platform,
            findings_by_severity=findings_by_severity,
            compliance_coverage=compliance_coverage,
            recommendations=recommendations
        )
    
    def _generate_unified_recommendations(
        self,
        severity_breakdown: Dict[str, int],
        platforms_scanned: List[str],
        docker_results: Optional[Dict[str, Any]],
        k8s_results: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate prioritized unified recommendations"""
        recommendations = []
        
        # Critical findings recommendations
        if severity_breakdown['CRITICAL'] > 0:
            recommendations.append(
                f"URGENT: Address {severity_breakdown['CRITICAL']} critical findings immediately"
            )
            
            if 'docker' in platforms_scanned:
                recommendations.append(
                    "Docker: Remove privileged containers and Docker socket mounts"
                )
            
            if 'kubernetes' in platforms_scanned:
                recommendations.append(
                    "Kubernetes: Fix wildcard RBAC permissions and privileged pods"
                )
        
        # High severity recommendations
        if severity_breakdown['HIGH'] > 0:
            if 'docker' in platforms_scanned:
                recommendations.append(
                    "Docker: Enable user namespace remapping and implement resource limits"
                )
            
            if 'kubernetes' in platforms_scanned:
                recommendations.append(
                    "Kubernetes: Implement Pod Security Standards and NetworkPolicies"
                )
        
        # Platform-specific recommendations
        if 'docker' in platforms_scanned and docker_results:
            docker_recs = docker_results.get('recommendations', [])
            recommendations.extend([f"Docker: {rec}" for rec in docker_recs[:2]])
        
        if 'kubernetes' in platforms_scanned and k8s_results:
            k8s_recs = k8s_results.get('recommendations', [])
            recommendations.extend([f"Kubernetes: {rec}" for rec in k8s_recs[:2]])
        
        # General best practices
        recommendations.append(
            "Implement container image scanning in CI/CD pipeline"
        )
        recommendations.append(
            "Enable runtime security monitoring and anomaly detection"
        )
        recommendations.append(
            "Review compliance frameworks: CIS Benchmarks, NIST 800-190"
        )
        
        return recommendations
    
    def get_compliance_report(self, framework: str) -> Dict[str, Any]:
        """
        Generate compliance-specific report
        
        Args:
            framework: Compliance framework (e.g., 'CIS', 'NIST', 'PCI-DSS', 'HIPAA')
        
        Returns:
            Dict with framework-specific findings and coverage
        """
        # Scan all platforms
        scan_result = self.scan_all_platforms()
        
        # Filter findings by compliance framework
        framework_findings = []
        
        for platform, findings in scan_result.findings_by_platform.items():
            for finding in findings:
                compliance_frameworks = finding.get('compliance_frameworks', [])
                
                # Check if framework matches (partial match for flexibility)
                if any(framework.upper() in cf.upper() for cf in compliance_frameworks):
                    framework_findings.append({
                        **finding,
                        'platform': platform
                    })
        
        # Calculate framework compliance score
        total_possible_checks = 100  # Baseline, adjust based on framework
        checks_failed = len(framework_findings)
        compliance_score = max(0, 100 - (checks_failed * 5))  # Rough calculation
        
        return {
            'framework': framework,
            'compliance_score': compliance_score,
            'total_findings': len(framework_findings),
            'findings': framework_findings,
            'platforms_assessed': scan_result.platforms_scanned,
            'severity_breakdown': {
                'CRITICAL': len([f for f in framework_findings if f.get('severity') == 'CRITICAL']),
                'HIGH': len([f for f in framework_findings if f.get('severity') == 'HIGH']),
                'MEDIUM': len([f for f in framework_findings if f.get('severity') == 'MEDIUM']),
                'LOW': len([f for f in framework_findings if f.get('severity') == 'LOW'])
            },
            'scan_timestamp': scan_result.scan_timestamp
        }
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available container platforms"""
        available = []
        
        if DOCKER_AVAILABLE:
            available.append('docker')
        
        if KUBERNETES_AVAILABLE:
            available.append('kubernetes')
        
        return available
    
    def get_configured_platforms(self) -> List[str]:
        """Get list of configured container platforms"""
        return self.platforms_configured.copy()


# Module availability checks
def is_docker_available() -> bool:
    """Check if Docker scanner is available"""
    return DOCKER_AVAILABLE

def is_kubernetes_available() -> bool:
    """Check if Kubernetes scanner is available"""
    return KUBERNETES_AVAILABLE

def is_any_platform_available() -> bool:
    """Check if any container platform scanner is available"""
    return DOCKER_AVAILABLE or KUBERNETES_AVAILABLE
