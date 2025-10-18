"""
Unified Multi-Cloud Security Scanner
Orchestrates AWS, Azure, and GCP security assessments
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# Import cloud scanners with graceful fallback
try:
    from .cloud_security_aws import AWSSecurityScanner, CloudSecurityFinding as AWSFinding
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logger.warning("AWS SDK not available. Install boto3 for AWS scanning.")

try:
    from .cloud_security_azure import AzureSecurityScanner, AzureSecurityFinding
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure SDK not available. Install azure-mgmt-* packages for Azure scanning.")

try:
    from .cloud_security_gcp import GCPSecurityScanner, GCPSecurityFinding
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logger.warning("GCP SDK not available. Install google-cloud-* packages for GCP scanning.")


@dataclass
class MultiCloudScanResult:
    """Unified multi-cloud scan result"""
    total_findings: int
    findings_by_cloud: Dict[str, int]
    findings_by_severity: Dict[str, int]
    findings: List[Any]
    risk_scores: Dict[str, int]
    overall_risk_score: int
    security_posture: str
    clouds_scanned: List[str]
    scan_metadata: Dict[str, Any]


class MultiCloudSecurityScanner:
    """
    Multi-Cloud Security Scanner
    Orchestrates security assessments across AWS, Azure, and GCP
    
    Features:
    - Unified scanning interface for all cloud providers
    - Consistent finding format and severity levels
    - Aggregated risk scoring
    - Multi-cloud compliance reporting
    - Centralized vulnerability management
    """
    
    def __init__(self):
        """Initialize multi-cloud scanner"""
        self.aws_scanner = None
        self.azure_scanner = None
        self.gcp_scanner = None
        self.findings = []
    
    def configure_aws(self, access_key: Optional[str] = None, 
                     secret_key: Optional[str] = None, 
                     region: str = 'us-east-1',
                     profile_name: Optional[str] = None):
        """
        Configure AWS scanner
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            region: AWS region
            profile_name: AWS CLI profile name
        """
        if not AWS_AVAILABLE:
            logger.error("AWS SDK not available. Cannot configure AWS scanner.")
            return False
        
        try:
            self.aws_scanner = AWSSecurityScanner(
                access_key=access_key,
                secret_key=secret_key,
                region=region,
                profile_name=profile_name
            )
            logger.info("AWS scanner configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to configure AWS scanner: {e}")
            return False
    
    def configure_azure(self, subscription_id: str,
                       tenant_id: Optional[str] = None,
                       client_id: Optional[str] = None,
                       client_secret: Optional[str] = None):
        """
        Configure Azure scanner
        
        Args:
            subscription_id: Azure subscription ID
            tenant_id: Azure AD tenant ID
            client_id: Service principal client ID
            client_secret: Service principal secret
        """
        if not AZURE_AVAILABLE:
            logger.error("Azure SDK not available. Cannot configure Azure scanner.")
            return False
        
        try:
            self.azure_scanner = AzureSecurityScanner(
                subscription_id=subscription_id,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            logger.info("Azure scanner configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to configure Azure scanner: {e}")
            return False
    
    def configure_gcp(self, project_id: str, 
                     credentials_path: Optional[str] = None):
        """
        Configure GCP scanner
        
        Args:
            project_id: GCP project ID
            credentials_path: Path to service account JSON key
        """
        if not GCP_AVAILABLE:
            logger.error("GCP SDK not available. Cannot configure GCP scanner.")
            return False
        
        try:
            self.gcp_scanner = GCPSecurityScanner(
                project_id=project_id,
                credentials_path=credentials_path
            )
            logger.info("GCP scanner configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to configure GCP scanner: {e}")
            return False
    
    def scan_all_clouds(self) -> MultiCloudScanResult:
        """
        Scan all configured cloud providers
        
        Returns:
            Unified multi-cloud scan result
        """
        logger.info("Starting multi-cloud security scan...")
        all_findings = []
        clouds_scanned = []
        risk_scores = {}
        
        # Scan AWS
        if self.aws_scanner:
            try:
                logger.info("Scanning AWS...")
                aws_findings = self.aws_scanner.scan_account()
                all_findings.extend(aws_findings)
                clouds_scanned.append('AWS')
                aws_summary = self.aws_scanner.get_summary()
                risk_scores['AWS'] = aws_summary['risk_score']
                logger.info(f"AWS scan complete: {len(aws_findings)} findings")
            except Exception as e:
                logger.error(f"AWS scan failed: {e}")
        
        # Scan Azure
        if self.azure_scanner:
            try:
                logger.info("Scanning Azure...")
                azure_findings = self.azure_scanner.scan_subscription()
                all_findings.extend(azure_findings)
                clouds_scanned.append('Azure')
                azure_summary = self.azure_scanner.get_summary()
                risk_scores['Azure'] = azure_summary['risk_score']
                logger.info(f"Azure scan complete: {len(azure_findings)} findings")
            except Exception as e:
                logger.error(f"Azure scan failed: {e}")
        
        # Scan GCP
        if self.gcp_scanner:
            try:
                logger.info("Scanning GCP...")
                gcp_findings = self.gcp_scanner.scan_project()
                all_findings.extend(gcp_findings)
                clouds_scanned.append('GCP')
                gcp_summary = self.gcp_scanner.get_summary()
                risk_scores['GCP'] = gcp_summary['risk_score']
                logger.info(f"GCP scan complete: {len(gcp_findings)} findings")
            except Exception as e:
                logger.error(f"GCP scan failed: {e}")
        
        # Generate unified results
        return self._generate_unified_results(
            all_findings, clouds_scanned, risk_scores
        )
    
    def scan_aws_only(self) -> MultiCloudScanResult:
        """Scan AWS only"""
        if not self.aws_scanner:
            raise ValueError("AWS scanner not configured")
        
        findings = self.aws_scanner.scan_account()
        summary = self.aws_scanner.get_summary()
        
        return self._generate_unified_results(
            findings, ['AWS'], {'AWS': summary['risk_score']}
        )
    
    def scan_azure_only(self) -> MultiCloudScanResult:
        """Scan Azure only"""
        if not self.azure_scanner:
            raise ValueError("Azure scanner not configured")
        
        findings = self.azure_scanner.scan_subscription()
        summary = self.azure_scanner.get_summary()
        
        return self._generate_unified_results(
            findings, ['Azure'], {'Azure': summary['risk_score']}
        )
    
    def scan_gcp_only(self) -> MultiCloudScanResult:
        """Scan GCP only"""
        if not self.gcp_scanner:
            raise ValueError("GCP scanner not configured")
        
        findings = self.gcp_scanner.scan_project()
        summary = self.gcp_scanner.get_summary()
        
        return self._generate_unified_results(
            findings, ['GCP'], {'GCP': summary['risk_score']}
        )
    
    def _generate_unified_results(self, findings: List[Any], 
                                  clouds_scanned: List[str],
                                  risk_scores: Dict[str, int]) -> MultiCloudScanResult:
        """Generate unified multi-cloud results"""
        
        # Count findings by cloud provider
        findings_by_cloud = {}
        for cloud in clouds_scanned:
            findings_by_cloud[cloud] = len([
                f for f in findings 
                if hasattr(f, 'cloud_provider') and f.cloud_provider == cloud
            ])
        
        # Count findings by severity
        findings_by_severity = {
            'critical': len([f for f in findings if hasattr(f, 'severity') and f.severity == 'critical']),
            'high': len([f for f in findings if hasattr(f, 'severity') and f.severity == 'high']),
            'medium': len([f for f in findings if hasattr(f, 'severity') and f.severity == 'medium']),
            'low': len([f for f in findings if hasattr(f, 'severity') and f.severity == 'low'])
        }
        
        # Calculate overall risk score (weighted average)
        if risk_scores:
            overall_risk_score = round(sum(risk_scores.values()) / len(risk_scores))
        else:
            overall_risk_score = 0
        
        # Determine overall security posture
        if overall_risk_score >= 80:
            security_posture = 'Critical'
        elif overall_risk_score >= 60:
            security_posture = 'High Risk'
        elif overall_risk_score >= 40:
            security_posture = 'Medium Risk'
        elif overall_risk_score >= 20:
            security_posture = 'Low Risk'
        else:
            security_posture = 'Good'
        
        return MultiCloudScanResult(
            total_findings=len(findings),
            findings_by_cloud=findings_by_cloud,
            findings_by_severity=findings_by_severity,
            findings=findings,
            risk_scores=risk_scores,
            overall_risk_score=overall_risk_score,
            security_posture=security_posture,
            clouds_scanned=clouds_scanned,
            scan_metadata={
                'clouds_available': {
                    'AWS': AWS_AVAILABLE,
                    'Azure': AZURE_AVAILABLE,
                    'GCP': GCP_AVAILABLE
                },
                'clouds_configured': {
                    'AWS': self.aws_scanner is not None,
                    'Azure': self.azure_scanner is not None,
                    'GCP': self.gcp_scanner is not None
                }
            }
        )
    
    def get_findings_by_cloud(self, cloud_provider: str) -> List[Any]:
        """Get findings for specific cloud provider"""
        return [
            f for f in self.findings 
            if hasattr(f, 'cloud_provider') and f.cloud_provider == cloud_provider
        ]
    
    def get_findings_by_severity(self, severity: str) -> List[Any]:
        """Get findings by severity level"""
        return [
            f for f in self.findings 
            if hasattr(f, 'severity') and f.severity == severity
        ]
    
    def get_compliance_report(self, framework: str) -> Dict[str, Any]:
        """
        Generate compliance report for specific framework
        
        Args:
            framework: Compliance framework (CIS, NIST, PCI-DSS, HIPAA)
            
        Returns:
            Compliance report with findings mapped to framework
        """
        relevant_findings = [
            f for f in self.findings 
            if hasattr(f, 'compliance_frameworks') and framework in f.compliance_frameworks
        ]
        
        return {
            'framework': framework,
            'total_findings': len(relevant_findings),
            'findings_by_severity': {
                'critical': len([f for f in relevant_findings if f.severity == 'critical']),
                'high': len([f for f in relevant_findings if f.severity == 'high']),
                'medium': len([f for f in relevant_findings if f.severity == 'medium']),
                'low': len([f for f in relevant_findings if f.severity == 'low'])
            },
            'findings': relevant_findings
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scanner = MultiCloudSecurityScanner()
    
    print("Multi-Cloud Security Scanner initialized")
    print("\nAvailable Cloud Providers:")
    print(f"  • AWS: {'✅' if AWS_AVAILABLE else '❌ (install boto3)'}")
    print(f"  • Azure: {'✅' if AZURE_AVAILABLE else '❌ (install azure-mgmt-*)'}")
    print(f"  • GCP: {'✅' if GCP_AVAILABLE else '❌ (install google-cloud-*)'}")
    print("\nFeatures:")
    print("  • Unified multi-cloud scanning")
    print("  • Consistent severity levels across clouds")
    print("  • Aggregated risk scoring")
    print("  • Multi-cloud compliance reporting")
    print("  • CIS, NIST, PCI-DSS, HIPAA framework mapping")
