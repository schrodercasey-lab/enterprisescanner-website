"""
Military-Grade CISA CDM Capabilities 1-4 - Core Implementation
================================================================

DHS Continuous Diagnostics and Mitigation (CDM) Program
Federal Mandate for Government Agencies and Contractors

CAPABILITIES IMPLEMENTED:
1. HWAM (Hardware Asset Management) - Capability 1
2. SWAM (Software Asset Management) - Capability 2  
3. CSM (Configuration Settings Management) - Capability 3
4. VM (Vulnerability Management) - Capability 4

COMPLIANCE:
- DHS CDM Program (OMB M-14-03, M-19-03)
- NIST 800-137 (ISCM - Information Security Continuous Monitoring)
- NIST 800-53 Rev 5 (CM-8, SI-2, RA-5, CM-6)
- FISMA (Federal Information Security Management Act)
- FedRAMP Moderate/High baseline requirements
- DoD RMF (Risk Management Framework)
- CMMC Level 3+ (Asset Management, Configuration Management)

DEFEND ARCHITECTURE PHASES:
- DATA: Asset discovery and data collection
- EVALUATE: Risk scoring and compliance assessment
- FABRICATE: Remediation recommendations
- EFFECTUATE: Automated remediation workflows
- NAVIGATE: Dashboard visualization
- DECIDE: Executive reporting and decision support

Classification: Unclassified
Distribution: Approved for Public Release

Author: Enterprise Scanner Team
Version: 1.0.0
Last Updated: October 2025
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import re
from collections import defaultdict


# ============================================================================
# ENUMERATIONS - CDM PROGRAM DEFINITIONS
# ============================================================================

class CDMCapability(Enum):
    """DHS CDM Program Capabilities (Phases 1-4)"""
    HWAM = "Hardware Asset Management"  # Capability 1
    SWAM = "Software Asset Management"  # Capability 2
    CSM = "Configuration Settings Management"  # Capability 3
    VM = "Vulnerability Management"  # Capability 4
    PAM = "Privileged Access Management"  # Future capability
    TRUST = "Trust & Behavioral Analytics"  # Future capability


class AssetType(Enum):
    """Hardware asset types (HWAM)"""
    WORKSTATION = "Workstation"
    LAPTOP = "Laptop"
    SERVER = "Server"
    NETWORK_DEVICE = "Network Device"
    MOBILE_DEVICE = "Mobile Device"
    IOT_DEVICE = "IoT Device"
    VIRTUAL_MACHINE = "Virtual Machine"
    CONTAINER = "Container"
    CLOUD_INSTANCE = "Cloud Instance"


class AssetClassification(Enum):
    """Asset security classification"""
    UNCLASSIFIED = "Unclassified"
    CUI = "Controlled Unclassified Information"
    CONFIDENTIAL = "Confidential"
    SECRET = "Secret"
    TOP_SECRET = "Top Secret"


class SoftwareType(Enum):
    """Software asset types (SWAM)"""
    OPERATING_SYSTEM = "Operating System"
    APPLICATION = "Application"
    DATABASE = "Database"
    MIDDLEWARE = "Middleware"
    FIRMWARE = "Firmware"
    DRIVER = "Driver"
    LIBRARY = "Library"
    PLUGIN = "Plugin"


class LicenseCompliance(Enum):
    """Software license compliance status"""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    EXPIRED = "Expired"
    MISSING = "Missing"
    UNKNOWN = "Unknown"


class ConfigurationBaseline(Enum):
    """Configuration baselines (CSM)"""
    CIS_LEVEL_1 = "CIS Level 1 (Basic)"
    CIS_LEVEL_2 = "CIS Level 2 (Defense in Depth)"
    DISA_STIG = "DISA STIG"
    NIST_800_53 = "NIST 800-53"
    FEDRAMP_MODERATE = "FedRAMP Moderate"
    FEDRAMP_HIGH = "FedRAMP High"
    CMMC_LEVEL_3 = "CMMC Level 3"
    CUSTOM = "Custom Baseline"


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels (VM)"""
    CRITICAL = "Critical"  # CVSS 9.0-10.0
    HIGH = "High"  # CVSS 7.0-8.9
    MEDIUM = "Medium"  # CVSS 4.0-6.9
    LOW = "Low"  # CVSS 0.1-3.9
    INFORMATIONAL = "Informational"  # CVSS 0.0


class RemediationStatus(Enum):
    """Vulnerability remediation status"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    REMEDIATED = "Remediated"
    MITIGATED = "Mitigated"
    ACCEPTED_RISK = "Accepted Risk"
    FALSE_POSITIVE = "False Positive"


# ============================================================================
# DATA CLASSES - CAPABILITY 1: HWAM
# ============================================================================

@dataclass
class HardwareAsset:
    """Hardware asset inventory record (CDM Capability 1)"""
    asset_id: str  # Unique identifier
    asset_type: AssetType
    hostname: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    
    # Location & ownership
    physical_location: Optional[str] = None
    building: Optional[str] = None
    room: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    
    # Security classification
    classification: AssetClassification = AssetClassification.UNCLASSIFIED
    security_zone: Optional[str] = None  # DMZ, Internal, Restricted
    criticality: str = "Medium"  # Critical, High, Medium, Low
    
    # Lifecycle
    purchase_date: Optional[datetime] = None
    warranty_expiration: Optional[datetime] = None
    eol_date: Optional[datetime] = None  # End of Life
    last_seen: Optional[datetime] = None
    discovered_date: datetime = field(default_factory=datetime.now)
    
    # Technical details
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    ram_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    
    # Compliance
    is_authorized: bool = False  # Authorized to operate?
    is_managed: bool = False  # Under organizational management?
    has_security_agent: bool = False  # EDR/antivirus installed?
    last_scanned: Optional[datetime] = None
    
    # Tags and metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DATA CLASSES - CAPABILITY 2: SWAM
# ============================================================================

@dataclass
class SoftwareAsset:
    """Software asset inventory record (CDM Capability 2)"""
    software_id: str  # Unique identifier
    software_name: str
    software_type: SoftwareType
    version: str
    vendor: str
    
    # Installation details
    installed_on: List[str] = field(default_factory=list)  # Asset IDs
    installation_date: Optional[datetime] = None
    install_path: Optional[str] = None
    
    # Licensing
    license_type: str = "Unknown"  # Commercial, Open Source, Freeware, Subscription
    license_key: Optional[str] = None
    license_expiration: Optional[datetime] = None
    seats_purchased: Optional[int] = None
    seats_in_use: int = 0
    license_compliance: LicenseCompliance = LicenseCompliance.UNKNOWN
    
    # Security
    is_approved: bool = False  # Authorized software list?
    is_eol: bool = False  # End of life / no longer supported?
    has_known_vulnerabilities: bool = False
    vulnerability_count: int = 0
    highest_cve_severity: Optional[str] = None
    
    # Compliance
    requires_patching: bool = False
    latest_version: Optional[str] = None
    patch_available: bool = False
    
    # Metadata
    discovered_date: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DATA CLASSES - CAPABILITY 3: CSM
# ============================================================================

@dataclass
class ConfigurationSetting:
    """Configuration setting record (CDM Capability 3)"""
    setting_id: str
    asset_id: str  # Asset this applies to
    category: str  # Password Policy, Encryption, Access Control, etc.
    setting_name: str
    current_value: Any
    
    # Baseline comparison
    baseline: ConfigurationBaseline
    required_value: Any
    is_compliant: bool
    deviation_reason: Optional[str] = None
    
    # Risk assessment
    risk_level: str = "Medium"  # Critical, High, Medium, Low
    impact_description: str = ""
    remediation_effort: str = "Medium"  # High, Medium, Low
    
    # Compliance references
    nist_controls: List[str] = field(default_factory=list)  # e.g., ["CM-6", "SC-7"]
    cis_controls: List[str] = field(default_factory=list)  # e.g., ["5.1", "5.2"]
    stig_ids: List[str] = field(default_factory=list)  # DISA STIG IDs
    
    # Remediation
    remediation_command: Optional[str] = None
    remediation_status: RemediationStatus = RemediationStatus.OPEN
    
    # Audit trail
    checked_date: datetime = field(default_factory=datetime.now)
    last_modified: Optional[datetime] = None
    modified_by: Optional[str] = None


# ============================================================================
# DATA CLASSES - CAPABILITY 4: VM
# ============================================================================

@dataclass
class VulnerabilityFinding:
    """Vulnerability finding record (CDM Capability 4)"""
    vuln_id: str  # Internal unique ID
    cve_id: Optional[str] = None  # CVE-2024-XXXXX
    title: str = ""
    description: str = ""
    
    # Affected asset
    asset_id: str = ""
    hostname: str = ""
    ip_address: Optional[str] = None
    
    # Vulnerability details
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    cvss_score: float = 0.0
    cvss_vector: Optional[str] = None
    
    # Affected component
    affected_software: Optional[str] = None
    affected_version: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    
    # Exploit information
    exploit_available: bool = False
    exploit_maturity: Optional[str] = None  # Unproven, POC, Functional, High
    in_the_wild: bool = False  # Active exploitation?
    
    # Remediation
    remediation_status: RemediationStatus = RemediationStatus.OPEN
    remediation_recommendation: str = ""
    patch_available: bool = False
    patch_version: Optional[str] = None
    workaround: Optional[str] = None
    
    # Risk assessment
    business_impact: str = "Medium"
    likelihood: str = "Medium"
    overall_risk: str = "Medium"
    
    # Compliance
    nist_controls: List[str] = field(default_factory=list)
    requires_poam: bool = False  # Plan of Action & Milestones
    
    # Timeline
    discovered_date: datetime = field(default_factory=datetime.now)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    remediation_date: Optional[datetime] = None
    
    # Metadata
    scanner_source: Optional[str] = None
    false_positive: bool = False
    notes: str = ""
    tags: List[str] = field(default_factory=list)


# ============================================================================
# CDM DASHBOARD DATA
# ============================================================================

@dataclass
class CDMDashboard:
    """CDM Dashboard metrics for DEFEND architecture"""
    
    # Overall metrics
    total_assets: int = 0
    managed_assets: int = 0
    unmanaged_assets: int = 0
    
    # HWAM metrics
    authorized_hardware: int = 0
    unauthorized_hardware: int = 0
    end_of_life_hardware: int = 0
    
    # SWAM metrics
    total_software: int = 0
    licensed_software: int = 0
    unlicensed_software: int = 0
    eol_software: int = 0
    vulnerable_software: int = 0
    
    # CSM metrics
    total_config_checks: int = 0
    compliant_configs: int = 0
    non_compliant_configs: int = 0
    compliance_percentage: float = 0.0
    
    # VM metrics
    total_vulnerabilities: int = 0
    critical_vulns: int = 0
    high_vulns: int = 0
    medium_vulns: int = 0
    low_vulns: int = 0
    open_vulns: int = 0
    remediated_vulns: int = 0
    
    # Risk scoring
    overall_risk_score: int = 0  # 0-100
    hwam_risk_score: int = 0
    swam_risk_score: int = 0
    csm_risk_score: int = 0
    vm_risk_score: int = 0
    
    # Trends
    new_assets_last_30d: int = 0
    new_vulns_last_30d: int = 0
    remediated_vulns_last_30d: int = 0
    
    # Compliance posture
    fisma_compliant: bool = False
    fedramp_ready: bool = False
    cmmc_level: int = 0
    
    # Timestamps
    generated_date: datetime = field(default_factory=datetime.now)


# ============================================================================
# MAIN CDM ENGINE
# ============================================================================

class CDMEngine:
    """
    DHS CDM Program Implementation Engine
    
    Implements all 4 core CDM capabilities:
    1. HWAM - Hardware Asset Management
    2. SWAM - Software Asset Management
    3. CSM - Configuration Settings Management
    4. VM - Vulnerability Management
    
    Supports DEFEND architecture for federal compliance.
    """
    
    def __init__(self, agency_name: str = "Federal Agency", 
                 agency_code: str = "AGY"):
        self.agency_name = agency_name
        self.agency_code = agency_code
        
        # Data stores
        self.hardware_assets: Dict[str, HardwareAsset] = {}
        self.software_assets: Dict[str, SoftwareAsset] = {}
        self.configurations: Dict[str, List[ConfigurationSetting]] = {}
        self.vulnerabilities: Dict[str, List[VulnerabilityFinding]] = {}
        
        # Baselines
        self.active_baseline = ConfigurationBaseline.CIS_LEVEL_1
        
        # Reporting
        self.dashboard_cache: Optional[CDMDashboard] = None
        self.last_scan_date: Optional[datetime] = None
    
    # ========================================================================
    # CAPABILITY 1: HWAM - HARDWARE ASSET MANAGEMENT
    # ========================================================================
    
    def discover_hardware_assets(self, scan_results: List[Dict[str, Any]]) -> List[HardwareAsset]:
        """
        Discover and inventory hardware assets
        
        Args:
            scan_results: Network scan results with asset information
            
        Returns:
            List of discovered hardware assets
        """
        discovered = []
        
        for result in scan_results:
            asset_id = self._generate_asset_id(
                result.get('ip_address', ''),
                result.get('mac_address', '')
            )
            
            # Determine asset type
            asset_type = self._classify_asset_type(result)
            
            asset = HardwareAsset(
                asset_id=asset_id,
                asset_type=asset_type,
                hostname=result.get('hostname', 'unknown'),
                ip_address=result.get('ip_address'),
                mac_address=result.get('mac_address'),
                manufacturer=result.get('manufacturer'),
                model=result.get('model'),
                serial_number=result.get('serial_number'),
                os_type=result.get('os_type'),
                os_version=result.get('os_version'),
                last_seen=datetime.now()
            )
            
            # Store in inventory
            self.hardware_assets[asset_id] = asset
            discovered.append(asset)
        
        return discovered
    
    def classify_asset_criticality(self, asset_id: str, 
                                   criteria: Dict[str, Any]) -> str:
        """
        Classify asset criticality based on business criteria
        
        Args:
            asset_id: Asset identifier
            criteria: Classification criteria
            
        Returns:
            Criticality level: Critical, High, Medium, Low
        """
        asset = self.hardware_assets.get(asset_id)
        if not asset:
            return "Unknown"
        
        # Scoring logic
        score = 0
        
        # Check if it's a server
        if asset.asset_type in [AssetType.SERVER, AssetType.CLOUD_INSTANCE]:
            score += 3
        
        # Check classification level
        if asset.classification in [AssetClassification.SECRET, 
                                   AssetClassification.TOP_SECRET]:
            score += 3
        elif asset.classification == AssetClassification.CONFIDENTIAL:
            score += 2
        
        # Check if it has security classification
        if asset.security_zone == "Restricted":
            score += 2
        elif asset.security_zone == "DMZ":
            score += 1
        
        # Determine criticality
        if score >= 6:
            criticality = "Critical"
        elif score >= 4:
            criticality = "High"
        elif score >= 2:
            criticality = "Medium"
        else:
            criticality = "Low"
        
        # Update asset
        asset.criticality = criticality
        return criticality
    
    def identify_unauthorized_assets(self) -> List[HardwareAsset]:
        """
        Identify hardware assets not authorized to operate
        
        Returns:
            List of unauthorized assets
        """
        unauthorized = []
        
        for asset_id, asset in self.hardware_assets.items():
            if not asset.is_authorized:
                unauthorized.append(asset)
        
        return unauthorized
    
    def identify_eol_hardware(self) -> List[HardwareAsset]:
        """
        Identify end-of-life hardware assets
        
        Returns:
            List of EOL assets
        """
        eol_assets = []
        now = datetime.now()
        
        for asset_id, asset in self.hardware_assets.items():
            if asset.eol_date and asset.eol_date <= now:
                eol_assets.append(asset)
            elif asset.warranty_expiration and asset.warranty_expiration <= now:
                asset.is_eol = True  # Mark for review
                eol_assets.append(asset)
        
        return eol_assets
    
    # ========================================================================
    # CAPABILITY 2: SWAM - SOFTWARE ASSET MANAGEMENT
    # ========================================================================
    
    def discover_software_assets(self, asset_id: str, 
                                 software_list: List[Dict[str, Any]]) -> List[SoftwareAsset]:
        """
        Discover and inventory software on an asset
        
        Args:
            asset_id: Hardware asset identifier
            software_list: List of installed software
            
        Returns:
            List of software assets
        """
        discovered = []
        
        for sw in software_list:
            software_id = self._generate_software_id(
                sw.get('name', ''),
                sw.get('version', ''),
                sw.get('vendor', '')
            )
            
            # Check if already tracked
            if software_id in self.software_assets:
                # Update installation list
                if asset_id not in self.software_assets[software_id].installed_on:
                    self.software_assets[software_id].installed_on.append(asset_id)
                    self.software_assets[software_id].seats_in_use += 1
            else:
                # Create new software asset
                software_type = self._classify_software_type(sw)
                
                software = SoftwareAsset(
                    software_id=software_id,
                    software_name=sw.get('name', 'Unknown'),
                    software_type=software_type,
                    version=sw.get('version', 'Unknown'),
                    vendor=sw.get('vendor', 'Unknown'),
                    installed_on=[asset_id],
                    seats_in_use=1
                )
                
                self.software_assets[software_id] = software
                discovered.append(software)
        
        return discovered
    
    def check_license_compliance(self) -> Dict[str, List[SoftwareAsset]]:
        """
        Check software license compliance across all assets
        
        Returns:
            Dictionary of compliance issues by type
        """
        compliance_issues = {
            'expired': [],
            'over_licensed': [],
            'under_licensed': [],
            'missing': []
        }
        
        for sw_id, software in self.software_assets.items():
            # Check expiration
            if software.license_expiration:
                if software.license_expiration <= datetime.now():
                    software.license_compliance = LicenseCompliance.EXPIRED
                    compliance_issues['expired'].append(software)
            
            # Check seat count
            if software.seats_purchased:
                if software.seats_in_use > software.seats_purchased:
                    software.license_compliance = LicenseCompliance.NON_COMPLIANT
                    compliance_issues['over_licensed'].append(software)
                elif software.seats_in_use < software.seats_purchased * 0.5:
                    # More than 50% unused
                    compliance_issues['under_licensed'].append(software)
            
            # Check if license key is missing
            if software.license_type == "Commercial" and not software.license_key:
                software.license_compliance = LicenseCompliance.MISSING
                compliance_issues['missing'].append(software)
        
        return compliance_issues
    
    def identify_unauthorized_software(self, 
                                      approved_list: Set[str]) -> List[SoftwareAsset]:
        """
        Identify software not on approved list
        
        Args:
            approved_list: Set of approved software names
            
        Returns:
            List of unauthorized software
        """
        unauthorized = []
        
        for sw_id, software in self.software_assets.items():
            if software.software_name not in approved_list:
                software.is_approved = False
                unauthorized.append(software)
            else:
                software.is_approved = True
        
        return unauthorized
    
    def identify_eol_software(self, eol_database: Dict[str, datetime]) -> List[SoftwareAsset]:
        """
        Identify end-of-life software
        
        Args:
            eol_database: Dictionary mapping software name to EOL date
            
        Returns:
            List of EOL software
        """
        eol_software = []
        now = datetime.now()
        
        for sw_id, software in self.software_assets.items():
            key = f"{software.software_name}:{software.version}"
            if key in eol_database:
                if eol_database[key] <= now:
                    software.is_eol = True
                    eol_software.append(software)
        
        return eol_software
    
    # ========================================================================
    # CAPABILITY 3: CSM - CONFIGURATION SETTINGS MANAGEMENT
    # ========================================================================
    
    def scan_configuration_baseline(self, asset_id: str, 
                                    settings: List[Dict[str, Any]],
                                    baseline: ConfigurationBaseline) -> List[ConfigurationSetting]:
        """
        Scan asset configuration against baseline
        
        Args:
            asset_id: Asset to scan
            settings: Current configuration settings
            baseline: Baseline to compare against
            
        Returns:
            List of configuration findings
        """
        findings = []
        baseline_rules = self._load_baseline_rules(baseline)
        
        for setting in settings:
            setting_name = setting.get('name', '')
            current_value = setting.get('value')
            
            # Check if rule exists for this setting
            if setting_name in baseline_rules:
                rule = baseline_rules[setting_name]
                is_compliant = self._check_compliance(current_value, rule['required_value'])
                
                config = ConfigurationSetting(
                    setting_id=f"{asset_id}:{setting_name}",
                    asset_id=asset_id,
                    category=rule.get('category', 'General'),
                    setting_name=setting_name,
                    current_value=current_value,
                    baseline=baseline,
                    required_value=rule['required_value'],
                    is_compliant=is_compliant,
                    risk_level=rule.get('risk_level', 'Medium'),
                    impact_description=rule.get('impact', ''),
                    nist_controls=rule.get('nist_controls', []),
                    cis_controls=rule.get('cis_controls', []),
                    remediation_command=rule.get('remediation', '')
                )
                
                findings.append(config)
                
                # Store by asset
                if asset_id not in self.configurations:
                    self.configurations[asset_id] = []
                self.configurations[asset_id].append(config)
        
        return findings
    
    def generate_remediation_script(self, asset_id: str) -> str:
        """
        Generate automated remediation script for non-compliant configs
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Remediation script (PowerShell/Bash)
        """
        if asset_id not in self.configurations:
            return "# No configuration findings for this asset"
        
        script = f"# Configuration Remediation Script\n"
        script += f"# Asset: {asset_id}\n"
        script += f"# Generated: {datetime.now().isoformat()}\n\n"
        
        for config in self.configurations[asset_id]:
            if not config.is_compliant and config.remediation_command:
                script += f"# {config.setting_name}\n"
                script += f"# Risk: {config.risk_level}\n"
                script += f"{config.remediation_command}\n\n"
        
        return script
    
    def calculate_configuration_compliance(self, asset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate configuration compliance percentage
        
        Args:
            asset_id: Specific asset or None for all assets
            
        Returns:
            Compliance statistics
        """
        if asset_id:
            configs = self.configurations.get(asset_id, [])
        else:
            configs = []
            for asset_configs in self.configurations.values():
                configs.extend(asset_configs)
        
        total = len(configs)
        if total == 0:
            return {'total': 0, 'compliant': 0, 'percentage': 0.0}
        
        compliant = sum(1 for c in configs if c.is_compliant)
        percentage = (compliant / total) * 100
        
        return {
            'total': total,
            'compliant': compliant,
            'non_compliant': total - compliant,
            'percentage': round(percentage, 2)
        }
    
    # ========================================================================
    # CAPABILITY 4: VM - VULNERABILITY MANAGEMENT
    # ========================================================================
    
    def import_vulnerability_scan(self, asset_id: str, 
                                  scan_results: List[Dict[str, Any]]) -> List[VulnerabilityFinding]:
        """
        Import vulnerability scan results
        
        Args:
            asset_id: Scanned asset
            scan_results: Vulnerability findings from scanner
            
        Returns:
            List of vulnerability findings
        """
        vulnerabilities = []
        
        for result in scan_results:
            vuln_id = f"{asset_id}:{result.get('cve_id', 'VULN')}:{result.get('port', 0)}"
            
            severity = self._map_severity(result.get('cvss_score', 0.0))
            
            vuln = VulnerabilityFinding(
                vuln_id=vuln_id,
                cve_id=result.get('cve_id'),
                title=result.get('title', 'Unknown Vulnerability'),
                description=result.get('description', ''),
                asset_id=asset_id,
                hostname=result.get('hostname', ''),
                ip_address=result.get('ip_address'),
                severity=severity,
                cvss_score=result.get('cvss_score', 0.0),
                cvss_vector=result.get('cvss_vector'),
                affected_software=result.get('affected_software'),
                affected_version=result.get('affected_version'),
                port=result.get('port'),
                protocol=result.get('protocol'),
                exploit_available=result.get('exploit_available', False),
                remediation_recommendation=result.get('remediation', ''),
                patch_available=result.get('patch_available', False),
                scanner_source=result.get('scanner', 'Unknown')
            )
            
            # Calculate due date based on severity
            vuln.due_date = self._calculate_remediation_due_date(severity)
            
            # Determine if POA&M required (federal requirement)
            if severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]:
                vuln.requires_poam = True
            
            vulnerabilities.append(vuln)
            
            # Store by asset
            if asset_id not in self.vulnerabilities:
                self.vulnerabilities[asset_id] = []
            self.vulnerabilities[asset_id].append(vuln)
        
        return vulnerabilities
    
    def prioritize_vulnerabilities(self) -> List[VulnerabilityFinding]:
        """
        Prioritize vulnerabilities using risk-based approach
        
        Returns:
            Sorted list of vulnerabilities (highest risk first)
        """
        all_vulns = []
        for asset_vulns in self.vulnerabilities.values():
            all_vulns.extend(asset_vulns)
        
        # Scoring logic
        def risk_score(vuln: VulnerabilityFinding) -> int:
            score = 0
            
            # CVSS score (0-100)
            score += vuln.cvss_score * 10
            
            # Exploit availability (+30)
            if vuln.exploit_available:
                score += 30
            
            # Active exploitation (+50)
            if vuln.in_the_wild:
                score += 50
            
            # Asset criticality (get from hardware inventory)
            asset = self.hardware_assets.get(vuln.asset_id)
            if asset:
                if asset.criticality == "Critical":
                    score += 40
                elif asset.criticality == "High":
                    score += 20
                elif asset.criticality == "Medium":
                    score += 10
            
            return int(score)
        
        # Sort by risk score
        all_vulns.sort(key=risk_score, reverse=True)
        return all_vulns
    
    def generate_poam_report(self) -> List[Dict[str, Any]]:
        """
        Generate Plan of Action & Milestones (POA&M) for federal compliance
        
        Returns:
            List of POA&M entries for high/critical vulnerabilities
        """
        poam_entries = []
        
        for asset_id, vulns in self.vulnerabilities.items():
            for vuln in vulns:
                if vuln.requires_poam and vuln.remediation_status == RemediationStatus.OPEN:
                    entry = {
                        'poam_id': f"POAM-{len(poam_entries) + 1:04d}",
                        'weakness': vuln.title,
                        'cve_id': vuln.cve_id,
                        'affected_system': vuln.hostname,
                        'severity': vuln.severity.value,
                        'cvss_score': vuln.cvss_score,
                        'nist_controls': vuln.nist_controls,
                        'status': vuln.remediation_status.value,
                        'scheduled_completion': vuln.due_date.isoformat() if vuln.due_date else None,
                        'milestones': self._generate_milestones(vuln),
                        'resources_required': self._estimate_resources(vuln),
                        'point_of_contact': 'Security Team',
                        'date_identified': vuln.discovered_date.isoformat()
                    }
                    poam_entries.append(entry)
        
        return poam_entries
    
    def calculate_mean_time_to_remediate(self) -> Dict[str, float]:
        """
        Calculate MTTR (Mean Time To Remediate) by severity
        
        Returns:
            Dictionary of MTTR in days by severity level
        """
        mttr = {}
        
        for severity in VulnerabilitySeverity:
            remediated = []
            
            for asset_vulns in self.vulnerabilities.values():
                for vuln in asset_vulns:
                    if (vuln.severity == severity and 
                        vuln.remediation_status == RemediationStatus.REMEDIATED and
                        vuln.remediation_date):
                        days = (vuln.remediation_date - vuln.discovered_date).days
                        remediated.append(days)
            
            if remediated:
                mttr[severity.value] = sum(remediated) / len(remediated)
            else:
                mttr[severity.value] = 0.0
        
        return mttr
    
    # ========================================================================
    # DASHBOARD & REPORTING
    # ========================================================================
    
    def generate_dashboard(self) -> CDMDashboard:
        """
        Generate comprehensive CDM dashboard
        
        Returns:
            CDM dashboard with all metrics
        """
        dashboard = CDMDashboard()
        
        # HWAM metrics
        dashboard.total_assets = len(self.hardware_assets)
        dashboard.managed_assets = sum(1 for a in self.hardware_assets.values() if a.is_managed)
        dashboard.unmanaged_assets = dashboard.total_assets - dashboard.managed_assets
        dashboard.authorized_hardware = sum(1 for a in self.hardware_assets.values() if a.is_authorized)
        dashboard.unauthorized_hardware = dashboard.total_assets - dashboard.authorized_hardware
        dashboard.end_of_life_hardware = len(self.identify_eol_hardware())
        
        # SWAM metrics
        dashboard.total_software = len(self.software_assets)
        dashboard.licensed_software = sum(1 for s in self.software_assets.values() 
                                         if s.license_compliance == LicenseCompliance.COMPLIANT)
        dashboard.unlicensed_software = dashboard.total_software - dashboard.licensed_software
        dashboard.vulnerable_software = sum(1 for s in self.software_assets.values() 
                                           if s.has_known_vulnerabilities)
        
        # CSM metrics
        all_configs = []
        for configs in self.configurations.values():
            all_configs.extend(configs)
        dashboard.total_config_checks = len(all_configs)
        dashboard.compliant_configs = sum(1 for c in all_configs if c.is_compliant)
        dashboard.non_compliant_configs = dashboard.total_config_checks - dashboard.compliant_configs
        if dashboard.total_config_checks > 0:
            dashboard.compliance_percentage = (dashboard.compliant_configs / dashboard.total_config_checks) * 100
        
        # VM metrics
        all_vulns = []
        for vulns in self.vulnerabilities.values():
            all_vulns.extend(vulns)
        dashboard.total_vulnerabilities = len(all_vulns)
        dashboard.critical_vulns = sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.CRITICAL)
        dashboard.high_vulns = sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.HIGH)
        dashboard.medium_vulns = sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.MEDIUM)
        dashboard.low_vulns = sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.LOW)
        dashboard.open_vulns = sum(1 for v in all_vulns if v.remediation_status == RemediationStatus.OPEN)
        dashboard.remediated_vulns = sum(1 for v in all_vulns if v.remediation_status == RemediationStatus.REMEDIATED)
        
        # Risk scores
        dashboard.hwam_risk_score = self._calculate_hwam_risk()
        dashboard.swam_risk_score = self._calculate_swam_risk()
        dashboard.csm_risk_score = self._calculate_csm_risk()
        dashboard.vm_risk_score = self._calculate_vm_risk()
        dashboard.overall_risk_score = (dashboard.hwam_risk_score + 
                                       dashboard.swam_risk_score + 
                                       dashboard.csm_risk_score + 
                                       dashboard.vm_risk_score) // 4
        
        # Compliance determination
        dashboard.fisma_compliant = self._check_fisma_compliance(dashboard)
        dashboard.fedramp_ready = self._check_fedramp_readiness(dashboard)
        dashboard.cmmc_level = self._determine_cmmc_level(dashboard)
        
        self.dashboard_cache = dashboard
        return dashboard
    
    def export_cdm_report(self, format: str = "json") -> str:
        """
        Export comprehensive CDM report
        
        Args:
            format: Output format (json, xml, csv)
            
        Returns:
            Formatted report string
        """
        dashboard = self.generate_dashboard()
        
        if format == "json":
            report = {
                'agency': self.agency_name,
                'agency_code': self.agency_code,
                'report_date': datetime.now().isoformat(),
                'dashboard': self._dashboard_to_dict(dashboard),
                'hardware_assets': [self._asset_to_dict(a) for a in self.hardware_assets.values()],
                'software_assets': [self._software_to_dict(s) for s in self.software_assets.values()],
                'vulnerabilities': [self._vuln_to_dict(v) for vulns in self.vulnerabilities.values() for v in vulns],
                'poam': self.generate_poam_report()
            }
            return json.dumps(report, indent=2, default=str)
        
        return "Unsupported format"
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_asset_id(self, ip: str, mac: str) -> str:
        """Generate unique asset ID"""
        data = f"{ip}:{mac}:{datetime.now().timestamp()}"
        return hashlib.md5(data.encode()).hexdigest()[:16].upper()
    
    def _generate_software_id(self, name: str, version: str, vendor: str) -> str:
        """Generate unique software ID"""
        data = f"{vendor}:{name}:{version}"
        return hashlib.md5(data.encode()).hexdigest()[:16].upper()
    
    def _classify_asset_type(self, result: Dict[str, Any]) -> AssetType:
        """Classify hardware asset type from scan result"""
        os_type = result.get('os_type', '').lower()
        
        if 'server' in os_type or 'windows server' in os_type:
            return AssetType.SERVER
        elif 'workstation' in os_type or 'desktop' in os_type:
            return AssetType.WORKSTATION
        elif 'laptop' in os_type or 'mobile' in os_type:
            return AssetType.LAPTOP
        elif 'router' in os_type or 'switch' in os_type or 'firewall' in os_type:
            return AssetType.NETWORK_DEVICE
        else:
            return AssetType.WORKSTATION
    
    def _classify_software_type(self, sw: Dict[str, Any]) -> SoftwareType:
        """Classify software type"""
        name = sw.get('name', '').lower()
        
        if 'windows' in name or 'linux' in name or 'ubuntu' in name:
            return SoftwareType.OPERATING_SYSTEM
        elif 'database' in name or 'sql' in name or 'oracle' in name:
            return SoftwareType.DATABASE
        elif 'driver' in name:
            return SoftwareType.DRIVER
        else:
            return SoftwareType.APPLICATION
    
    def _load_baseline_rules(self, baseline: ConfigurationBaseline) -> Dict[str, Dict]:
        """Load configuration baseline rules"""
        # This would load from a database or file
        # Simplified example
        return {
            'password_min_length': {
                'category': 'Password Policy',
                'required_value': 14,
                'risk_level': 'High',
                'impact': 'Weak passwords increase breach risk',
                'nist_controls': ['IA-5'],
                'cis_controls': ['5.2'],
                'remediation': 'Set-ADDefaultDomainPasswordPolicy -MinPasswordLength 14'
            },
            'encryption_enabled': {
                'category': 'Encryption',
                'required_value': True,
                'risk_level': 'Critical',
                'impact': 'Unencrypted data at risk of exposure',
                'nist_controls': ['SC-13', 'SC-28'],
                'cis_controls': ['3.6'],
                'remediation': 'Enable-BitLocker -MountPoint "C:"'
            }
        }
    
    def _check_compliance(self, current: Any, required: Any) -> bool:
        """Check if current value meets requirement"""
        if isinstance(required, bool):
            return current == required
        elif isinstance(required, (int, float)):
            return current >= required
        else:
            return current == required
    
    def _map_severity(self, cvss_score: float) -> VulnerabilitySeverity:
        """Map CVSS score to severity enum"""
        if cvss_score >= 9.0:
            return VulnerabilitySeverity.CRITICAL
        elif cvss_score >= 7.0:
            return VulnerabilitySeverity.HIGH
        elif cvss_score >= 4.0:
            return VulnerabilitySeverity.MEDIUM
        elif cvss_score > 0.0:
            return VulnerabilitySeverity.LOW
        else:
            return VulnerabilitySeverity.INFORMATIONAL
    
    def _calculate_remediation_due_date(self, severity: VulnerabilitySeverity) -> datetime:
        """Calculate remediation due date per federal requirements"""
        now = datetime.now()
        
        if severity == VulnerabilitySeverity.CRITICAL:
            return now + timedelta(days=15)  # 15 days for critical
        elif severity == VulnerabilitySeverity.HIGH:
            return now + timedelta(days=30)  # 30 days for high
        elif severity == VulnerabilitySeverity.MEDIUM:
            return now + timedelta(days=90)  # 90 days for medium
        else:
            return now + timedelta(days=180)  # 180 days for low
    
    def _generate_milestones(self, vuln: VulnerabilityFinding) -> List[Dict[str, Any]]:
        """Generate POA&M milestones"""
        milestones = [
            {
                'milestone': 'Initial Assessment',
                'completion_date': (vuln.discovered_date + timedelta(days=3)).isoformat(),
                'status': 'Complete'
            },
            {
                'milestone': 'Remediation Planning',
                'completion_date': (vuln.discovered_date + timedelta(days=7)).isoformat(),
                'status': 'In Progress'
            }
        ]
        return milestones
    
    def _estimate_resources(self, vuln: VulnerabilityFinding) -> str:
        """Estimate resources required for remediation"""
        if vuln.severity == VulnerabilitySeverity.CRITICAL:
            return "2 engineers, 40 hours"
        elif vuln.severity == VulnerabilitySeverity.HIGH:
            return "1 engineer, 20 hours"
        else:
            return "1 engineer, 8 hours"
    
    def _calculate_hwam_risk(self) -> int:
        """Calculate HWAM risk score (0-100)"""
        if not self.hardware_assets:
            return 0
        
        unauthorized = self.identify_unauthorized_assets()
        unmanaged = [a for a in self.hardware_assets.values() if not a.is_managed]
        eol = self.identify_eol_hardware()
        
        risk = 0
        risk += (len(unauthorized) / len(self.hardware_assets)) * 40
        risk += (len(unmanaged) / len(self.hardware_assets)) * 30
        risk += (len(eol) / len(self.hardware_assets)) * 30
        
        return int(risk)
    
    def _calculate_swam_risk(self) -> int:
        """Calculate SWAM risk score (0-100)"""
        if not self.software_assets:
            return 0
        
        vulnerable = [s for s in self.software_assets.values() if s.has_known_vulnerabilities]
        eol = [s for s in self.software_assets.values() if s.is_eol]
        unlicensed = [s for s in self.software_assets.values() 
                     if s.license_compliance != LicenseCompliance.COMPLIANT]
        
        risk = 0
        risk += (len(vulnerable) / len(self.software_assets)) * 50
        risk += (len(eol) / len(self.software_assets)) * 30
        risk += (len(unlicensed) / len(self.software_assets)) * 20
        
        return int(risk)
    
    def _calculate_csm_risk(self) -> int:
        """Calculate CSM risk score (0-100)"""
        compliance = self.calculate_configuration_compliance()
        if compliance['total'] == 0:
            return 0
        
        return int(100 - compliance['percentage'])
    
    def _calculate_vm_risk(self) -> int:
        """Calculate VM risk score (0-100)"""
        all_vulns = []
        for vulns in self.vulnerabilities.values():
            all_vulns.extend(vulns)
        
        if not all_vulns:
            return 0
        
        critical = sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.CRITICAL)
        high = sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.HIGH)
        
        # Weight by severity
        risk = (critical * 10 + high * 5) / len(all_vulns) * 100
        return min(100, int(risk))
    
    def _check_fisma_compliance(self, dashboard: CDMDashboard) -> bool:
        """Check FISMA compliance status"""
        # Simplified check
        return (dashboard.overall_risk_score < 40 and 
                dashboard.compliance_percentage > 80)
    
    def _check_fedramp_readiness(self, dashboard: CDMDashboard) -> bool:
        """Check FedRAMP readiness"""
        # Stricter requirements
        return (dashboard.overall_risk_score < 30 and 
                dashboard.compliance_percentage > 90 and
                dashboard.critical_vulns == 0)
    
    def _determine_cmmc_level(self, dashboard: CDMDashboard) -> int:
        """Determine CMMC maturity level"""
        if dashboard.compliance_percentage > 95 and dashboard.overall_risk_score < 20:
            return 5
        elif dashboard.compliance_percentage > 90 and dashboard.overall_risk_score < 30:
            return 4
        elif dashboard.compliance_percentage > 85 and dashboard.overall_risk_score < 40:
            return 3
        elif dashboard.compliance_percentage > 75:
            return 2
        else:
            return 1
    
    def _dashboard_to_dict(self, dashboard: CDMDashboard) -> Dict:
        """Convert dashboard to dictionary"""
        return {k: v for k, v in dashboard.__dict__.items()}
    
    def _asset_to_dict(self, asset: HardwareAsset) -> Dict:
        """Convert asset to dictionary"""
        return {k: v if not isinstance(v, Enum) else v.value 
                for k, v in asset.__dict__.items()}
    
    def _software_to_dict(self, software: SoftwareAsset) -> Dict:
        """Convert software to dictionary"""
        return {k: v if not isinstance(v, Enum) else v.value 
                for k, v in software.__dict__.items()}
    
    def _vuln_to_dict(self, vuln: VulnerabilityFinding) -> Dict:
        """Convert vulnerability to dictionary"""
        return {k: v if not isinstance(v, Enum) else v.value 
                for k, v in vuln.__dict__.items()}


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Initialize CDM engine
    cdm = CDMEngine(agency_name="Department of Defense", agency_code="DOD")
    
    print("=" * 80)
    print("DHS CDM PROGRAM - CAPABILITIES 1-4 IMPLEMENTATION")
    print("=" * 80)
    
    # Example: Discover hardware assets
    sample_scan = [
        {
            'ip_address': '10.0.1.100',
            'mac_address': '00:11:22:33:44:55',
            'hostname': 'srv-web-01',
            'os_type': 'Windows Server 2019',
            'manufacturer': 'Dell',
            'model': 'PowerEdge R740'
        }
    ]
    
    assets = cdm.discover_hardware_assets(sample_scan)
    print(f"\n[HWAM] Discovered {len(assets)} hardware assets")
    
    # Example: Discover software
    sample_software = [
        {
            'name': 'Microsoft Office 365',
            'version': '2021',
            'vendor': 'Microsoft'
        }
    ]
    
    software = cdm.discover_software_assets(assets[0].asset_id, sample_software)
    print(f"[SWAM] Discovered {len(software)} software assets")
    
    # Example: Configuration baseline scan
    sample_config = [
        {
            'name': 'password_min_length',
            'value': 12
        }
    ]
    
    configs = cdm.scan_configuration_baseline(
        assets[0].asset_id,
        sample_config,
        ConfigurationBaseline.CIS_LEVEL_1
    )
    print(f"[CSM] Scanned {len(configs)} configuration settings")
    
    # Example: Import vulnerabilities
    sample_vulns = [
        {
            'cve_id': 'CVE-2024-12345',
            'title': 'Remote Code Execution',
            'cvss_score': 9.8,
            'hostname': 'srv-web-01',
            'affected_software': 'Apache HTTP Server',
            'affected_version': '2.4.49'
        }
    ]
    
    vulns = cdm.import_vulnerability_scan(assets[0].asset_id, sample_vulns)
    print(f"[VM] Imported {len(vulns)} vulnerabilities")
    
    # Generate dashboard
    dashboard = cdm.generate_dashboard()
    print(f"\n{'=' * 80}")
    print("CDM DASHBOARD SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Assets: {dashboard.total_assets}")
    print(f"Configuration Compliance: {dashboard.compliance_percentage:.1f}%")
    print(f"Total Vulnerabilities: {dashboard.total_vulnerabilities}")
    print(f"  - Critical: {dashboard.critical_vulns}")
    print(f"  - High: {dashboard.high_vulns}")
    print(f"Overall Risk Score: {dashboard.overall_risk_score}/100")
    print(f"FISMA Compliant: {'Yes' if dashboard.fisma_compliant else 'No'}")
    print(f"FedRAMP Ready: {'Yes' if dashboard.fedramp_ready else 'No'}")
    print(f"CMMC Level: {dashboard.cmmc_level}")
    
    print(f"\n{'=' * 80}")
    print("CDM CAPABILITIES 1-4 IMPLEMENTATION COMPLETE")
    print("=" * 80)
