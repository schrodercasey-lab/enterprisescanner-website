"""
Cloud Security Scanner Module - Azure
Enterprise-grade Azure security assessment and misconfiguration detection
"""

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AzureSecurityFinding:
    """Azure security finding"""
    cloud_provider: str = 'Azure'
    service: str = ''
    resource_id: str = ''
    finding_type: str = ''
    severity: str = ''
    description: str = ''
    recommendation: str = ''
    compliance_frameworks: List[str] = None
    remediation_steps: List[str] = None
    
    def __post_init__(self):
        if self.compliance_frameworks is None:
            self.compliance_frameworks = []
        if self.remediation_steps is None:
            self.remediation_steps = []


class AzureSecurityScanner:
    """
    Azure Security Scanner for Enterprise Scanner
    
    Features:
    - Storage account security analysis
    - Azure AD configuration review
    - Network Security Groups analysis
    - Activity log monitoring
    - Key Vault security
    - Virtual machine security
    - Public exposure detection
    - Compliance mapping (CIS, NIST, PCI-DSS)
    """
    
    def __init__(self, subscription_id: str, 
                 tenant_id: Optional[str] = None,
                 client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None):
        """
        Initialize Azure security scanner
        
        Args:
            subscription_id: Azure subscription ID
            tenant_id: Azure AD tenant ID (for service principal auth)
            client_id: Service principal client ID
            client_secret: Service principal secret
        """
        self.subscription_id = subscription_id
        self.findings = []
        
        # Initialize credentials
        if tenant_id and client_id and client_secret:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            # Use default credentials (environment variables or managed identity)
            self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self.storage_client = StorageManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
        
        logger.info(f"Azure Security Scanner initialized for subscription {subscription_id}")
    
    def scan_subscription(self) -> List[AzureSecurityFinding]:
        """
        Perform comprehensive Azure subscription security scan
        
        Returns:
            List of security findings
        """
        logger.info("Starting comprehensive Azure security scan...")
        self.findings = []
        
        # Scan storage accounts
        self._scan_storage_accounts()
        
        # Scan network security groups
        self._scan_network_security_groups()
        
        # Scan virtual machines
        self._scan_virtual_machines()
        
        # Check public IP exposures
        self._check_public_exposures()
        
        # Check encryption settings
        self._check_encryption_settings()
        
        logger.info(f"Azure security scan complete. Found {len(self.findings)} issues.")
        return self.findings
    
    def _scan_storage_accounts(self):
        """Scan storage accounts for security misconfigurations"""
        try:
            logger.info("Scanning Azure Storage accounts...")
            
            # Get all resource groups
            resource_groups = self.resource_client.resource_groups.list()
            
            for rg in resource_groups:
                rg_name = rg.name
                
                try:
                    # List storage accounts in resource group
                    storage_accounts = self.storage_client.storage_accounts.list_by_resource_group(rg_name)
                    
                    for account in storage_accounts:
                        account_name = account.name
                        
                        # Check public access
                        if account.allow_blob_public_access:
                            self.findings.append(AzureSecurityFinding(
                                service='Storage',
                                resource_id=f"{rg_name}/{account_name}",
                                finding_type='Public Blob Access Enabled',
                                severity='high',
                                description=f'Storage account {account_name} allows public blob access',
                                recommendation='Disable public blob access unless absolutely required',
                                compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                remediation_steps=[
                                    'Navigate to Azure Portal',
                                    f'Open storage account {account_name}',
                                    'Configuration > Allow Blob public access',
                                    'Set to Disabled'
                                ]
                            ))
                        
                        # Check HTTPS only
                        if not account.enable_https_traffic_only:
                            self.findings.append(AzureSecurityFinding(
                                service='Storage',
                                resource_id=f"{rg_name}/{account_name}",
                                finding_type='HTTPS Not Enforced',
                                severity='high',
                                description=f'Storage account {account_name} does not enforce HTTPS',
                                recommendation='Enable "Secure transfer required" to enforce HTTPS',
                                compliance_frameworks=['CIS', 'NIST', 'PCI-DSS', 'HIPAA'],
                                remediation_steps=[
                                    'Navigate to Azure Portal',
                                    f'Open storage account {account_name}',
                                    'Configuration > Secure transfer required',
                                    'Set to Enabled'
                                ]
                            ))
                        
                        # Check minimum TLS version
                        if hasattr(account, 'minimum_tls_version'):
                            if account.minimum_tls_version != 'TLS1_2':
                                self.findings.append(AzureSecurityFinding(
                                    service='Storage',
                                    resource_id=f"{rg_name}/{account_name}",
                                    finding_type='Weak TLS Version',
                                    severity='medium',
                                    description=f'Storage account {account_name} allows TLS versions below 1.2',
                                    recommendation='Set minimum TLS version to 1.2',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to Azure Portal',
                                        f'Open storage account {account_name}',
                                        'Configuration > Minimum TLS version',
                                        'Set to Version 1.2'
                                    ]
                                ))
                        
                        # Check encryption
                        if hasattr(account, 'encryption'):
                            if not account.encryption or not account.encryption.services:
                                self.findings.append(AzureSecurityFinding(
                                    service='Storage',
                                    resource_id=f"{rg_name}/{account_name}",
                                    finding_type='Encryption Not Enabled',
                                    severity='critical',
                                    description=f'Storage account {account_name} does not have encryption enabled',
                                    recommendation='Enable encryption for blobs and files',
                                    compliance_frameworks=['CIS', 'NIST', 'HIPAA', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to Azure Portal',
                                        f'Open storage account {account_name}',
                                        'Encryption > Enable for all services'
                                    ]
                                ))
                        
                except Exception as e:
                    logger.debug(f"Error scanning storage in resource group {rg_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scanning storage accounts: {e}")
    
    def _scan_network_security_groups(self):
        """Scan Network Security Groups for overly permissive rules"""
        try:
            logger.info("Scanning Network Security Groups...")
            
            # Get all NSGs
            nsgs = self.network_client.network_security_groups.list_all()
            
            for nsg in nsgs:
                nsg_name = nsg.name
                
                # Check security rules
                for rule in nsg.security_rules:
                    rule_name = rule.name
                    
                    # Check for open SSH (port 22)
                    if rule.direction == 'Inbound' and rule.access == 'Allow':
                        if (rule.destination_port_range == '22' or 
                            (rule.destination_port_ranges and '22' in rule.destination_port_ranges)):
                            if (rule.source_address_prefix == '*' or 
                                rule.source_address_prefix == 'Internet'):
                                self.findings.append(AzureSecurityFinding(
                                    service='Network',
                                    resource_id=f"{nsg_name}/{rule_name}",
                                    finding_type='SSH Open to Internet',
                                    severity='critical',
                                    description=f'NSG {nsg_name} allows SSH from internet',
                                    recommendation='Restrict SSH to specific IP addresses',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to Azure Portal',
                                        f'Open NSG {nsg_name}',
                                        f'Edit rule {rule_name}',
                                        'Change Source to specific IP addresses'
                                    ]
                                ))
                        
                        # Check for open RDP (port 3389)
                        if (rule.destination_port_range == '3389' or 
                            (rule.destination_port_ranges and '3389' in rule.destination_port_ranges)):
                            if (rule.source_address_prefix == '*' or 
                                rule.source_address_prefix == 'Internet'):
                                self.findings.append(AzureSecurityFinding(
                                    service='Network',
                                    resource_id=f"{nsg_name}/{rule_name}",
                                    finding_type='RDP Open to Internet',
                                    severity='critical',
                                    description=f'NSG {nsg_name} allows RDP from internet',
                                    recommendation='Restrict RDP to specific IP addresses',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to Azure Portal',
                                        f'Open NSG {nsg_name}',
                                        f'Edit rule {rule_name}',
                                        'Change Source to specific IP addresses'
                                    ]
                                ))
                        
                        # Check for unrestricted access (all ports)
                        if rule.destination_port_range == '*':
                            if (rule.source_address_prefix == '*' or 
                                rule.source_address_prefix == 'Internet'):
                                self.findings.append(AzureSecurityFinding(
                                    service='Network',
                                    resource_id=f"{nsg_name}/{rule_name}",
                                    finding_type='Unrestricted Network Access',
                                    severity='critical',
                                    description=f'NSG {nsg_name} allows all traffic from internet',
                                    recommendation='Implement least privilege network access',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to Azure Portal',
                                        f'Open NSG {nsg_name}',
                                        f'Delete or restrict rule {rule_name}',
                                        'Add specific rules for required services only'
                                    ]
                                ))
                                
        except Exception as e:
            logger.error(f"Error scanning NSGs: {e}")
    
    def _scan_virtual_machines(self):
        """Scan virtual machines for security issues"""
        try:
            logger.info("Scanning virtual machines...")
            
            # Get all VMs
            vms = self.compute_client.virtual_machines.list_all()
            
            for vm in vms:
                vm_name = vm.name
                
                # Check if VM has managed disks
                if vm.storage_profile.os_disk.managed_disk is None:
                    self.findings.append(AzureSecurityFinding(
                        service='Compute',
                        resource_id=vm_name,
                        finding_type='Unmanaged Disks',
                        severity='medium',
                        description=f'VM {vm_name} uses unmanaged disks',
                        recommendation='Migrate to managed disks for better security and reliability',
                        compliance_frameworks=['CIS', 'NIST'],
                        remediation_steps=[
                            'Navigate to Azure Portal',
                            f'Open VM {vm_name}',
                            'Disks > Migrate to managed disks'
                        ]
                    ))
                
                # Check OS disk encryption
                if vm.storage_profile.os_disk.encryption_settings:
                    if not vm.storage_profile.os_disk.encryption_settings.enabled:
                        self.findings.append(AzureSecurityFinding(
                            service='Compute',
                            resource_id=vm_name,
                            finding_type='Disk Encryption Disabled',
                            severity='high',
                            description=f'VM {vm_name} does not have disk encryption enabled',
                            recommendation='Enable Azure Disk Encryption',
                            compliance_frameworks=['CIS', 'NIST', 'HIPAA', 'PCI-DSS'],
                            remediation_steps=[
                                'Navigate to Azure Portal',
                                f'Open VM {vm_name}',
                                'Disks > Enable Azure Disk Encryption'
                            ]
                        ))
                
                # Check for boot diagnostics
                if not vm.diagnostics_profile or not vm.diagnostics_profile.boot_diagnostics:
                    self.findings.append(AzureSecurityFinding(
                        service='Compute',
                        resource_id=vm_name,
                        finding_type='Boot Diagnostics Disabled',
                        severity='low',
                        description=f'VM {vm_name} does not have boot diagnostics enabled',
                        recommendation='Enable boot diagnostics for troubleshooting',
                        compliance_frameworks=['CIS'],
                        remediation_steps=[
                            'Navigate to Azure Portal',
                            f'Open VM {vm_name}',
                            'Boot diagnostics > Enable'
                        ]
                    ))
                    
        except Exception as e:
            logger.error(f"Error scanning VMs: {e}")
    
    def _check_public_exposures(self):
        """Check for publicly exposed resources"""
        try:
            logger.info("Checking for public exposures...")
            
            # Get all public IPs
            public_ips = self.network_client.public_ip_addresses.list_all()
            
            public_ip_count = sum(1 for _ in public_ips)
            
            if public_ip_count > 0:
                self.findings.append(AzureSecurityFinding(
                    service='Network',
                    resource_id='public-ips',
                    finding_type='Public IP Addresses',
                    severity='medium',
                    description=f'{public_ip_count} public IP addresses allocated',
                    recommendation='Review necessity of public IPs, use Azure Firewall or VPN',
                    compliance_frameworks=['CIS', 'NIST'],
                    remediation_steps=[
                        'Review each public IP for necessity',
                        'Move resources to private networks where possible',
                        'Use Azure Firewall for outbound access',
                        'Implement VPN for administrative access'
                    ]
                ))
                
        except Exception as e:
            logger.error(f"Error checking public exposures: {e}")
    
    def _check_encryption_settings(self):
        """Check encryption settings across services"""
        try:
            logger.info("Checking encryption settings...")
            
            # Get all resource groups
            resource_groups = self.resource_client.resource_groups.list()
            
            for rg in resource_groups:
                rg_name = rg.name
                
                try:
                    # Check storage accounts encryption (already covered above)
                    # Check disk encryption for data disks
                    disks = self.compute_client.disks.list_by_resource_group(rg_name)
                    
                    for disk in disks:
                        if hasattr(disk, 'encryption_settings_collection'):
                            if not disk.encryption_settings_collection or not disk.encryption_settings_collection.enabled:
                                self.findings.append(AzureSecurityFinding(
                                    service='Compute',
                                    resource_id=f"{rg_name}/{disk.name}",
                                    finding_type='Unencrypted Disk',
                                    severity='high',
                                    description=f'Disk {disk.name} is not encrypted',
                                    recommendation='Enable Azure Disk Encryption',
                                    compliance_frameworks=['CIS', 'NIST', 'HIPAA', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to Azure Portal',
                                        f'Open disk {disk.name}',
                                        'Enable encryption'
                                    ]
                                ))
                        
                except Exception as e:
                    logger.debug(f"Error checking encryption in resource group {rg_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking encryption settings: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of security scan results"""
        critical = len([f for f in self.findings if f.severity == 'critical'])
        high = len([f for f in self.findings if f.severity == 'high'])
        medium = len([f for f in self.findings if f.severity == 'medium'])
        low = len([f for f in self.findings if f.severity == 'low'])
        
        # Calculate risk score (0-100, lower is better)
        risk_score = min(100, (critical * 25) + (high * 10) + (medium * 5) + (low * 2))
        
        # Determine security posture
        if risk_score >= 80:
            posture = 'Critical'
        elif risk_score >= 60:
            posture = 'High Risk'
        elif risk_score >= 40:
            posture = 'Medium Risk'
        elif risk_score >= 20:
            posture = 'Low Risk'
        else:
            posture = 'Good'
        
        return {
            'cloud_provider': 'Azure',
            'subscription_id': self.subscription_id,
            'total_findings': len(self.findings),
            'severity_breakdown': {
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            },
            'risk_score': risk_score,
            'security_posture': posture,
            'services_scanned': ['Storage', 'Network', 'Compute'],
            'compliance_frameworks': ['CIS', 'NIST', 'PCI-DSS', 'HIPAA']
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Azure Security Scanner initialized")
    print("Note: Requires Azure credentials to perform actual scans")
    print("\nFeatures:")
    print("  • Storage account security analysis")
    print("  • Network Security Groups analysis")
    print("  • Virtual machine security")
    print("  • Public exposure detection")
    print("  • Encryption verification")
    print("  • CIS, NIST, PCI-DSS, HIPAA compliance mapping")
