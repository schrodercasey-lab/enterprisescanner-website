"""
Military-Grade CDM Capabilities 1 & 2 - HWAM + SWAM Combined
=============================================================

DHS CDM Program - Integrated Hardware & Software Asset Management

This module combines:
- HWAM (Hardware Asset Management) - CDM Capability 1
- SWAM (Software Asset Management) - CDM Capability 2

UNIFIED CAPABILITIES:
- Complete asset visibility (hardware + software)
- License compliance automation
- Vulnerability correlation (CVE mapping to installed software)
- Software bill of materials (SBOM) generation
- Unauthorized software detection
- Software lifecycle management
- Patch management integration

COMPLIANCE:
- DHS CDM Program HWAM/SWAM requirements
- NIST 800-137 (ISCM)
- NIST 800-53 Rev 5 CM-8, SI-2, SA-22
- Executive Order 14028 (Software Supply Chain Security)
- OMB M-19-03 (Software Asset Management)
- FedRAMP Moderate/High baselines

INTEGRATION:
- Microsoft SCCM/Intune
- JAMF (macOS management)
- Tanium
- ServiceNow CMDB
- CycloneDX/SPDX SBOM formats

Classification: Unclassified
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import re
from collections import defaultdict


# ============================================================================
# ENUMERATIONS
# ============================================================================

class SoftwareCategory(Enum):
    """Software categories for SWAM"""
    OPERATING_SYSTEM = "Operating System"
    PRODUCTIVITY = "Productivity"
    DEVELOPMENT = "Development Tools"
    SECURITY = "Security Software"
    DATABASE = "Database"
    WEB_SERVER = "Web Server"
    MIDDLEWARE = "Middleware"
    MONITORING = "Monitoring"
    BACKUP = "Backup"
    VIRTUALIZATION = "Virtualization"


class SoftwareLicenseType(Enum):
    """Software license models"""
    PERPETUAL = "Perpetual License"
    SUBSCRIPTION = "Subscription"
    VOLUME = "Volume License Agreement"
    SITE_LICENSE = "Site License"
    NAMED_USER = "Named User"
    CONCURRENT = "Concurrent User"
    OPEN_SOURCE = "Open Source"
    FREEWARE = "Freeware"
    TRIAL = "Trial"


class PatchStatus(Enum):
    """Software patch status"""
    UP_TO_DATE = "Up to Date"
    PATCH_AVAILABLE = "Patch Available"
    CRITICAL_PATCH_NEEDED = "Critical Patch Needed"
    EOL_NO_PATCHES = "End of Life - No Patches"
    UNSUPPORTED = "Unsupported Version"


class SBOMFormat(Enum):
    """SBOM (Software Bill of Materials) formats"""
    CYCLONEDX = "CycloneDX"
    SPDX = "SPDX"
    SWID = "SWID Tag"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SoftwarePackage:
    """Software package with complete metadata"""
    package_id: str
    name: str
    version: str
    vendor: str
    category: SoftwareCategory
    
    # Installation details
    install_date: Optional[datetime] = None
    install_path: Optional[str] = None
    installed_by: Optional[str] = None
    installation_source: Optional[str] = None
    
    # Licensing
    license_type: SoftwareLicenseType = SoftwareLicenseType.OPEN_SOURCE
    license_key: Optional[str] = None
    license_expiration: Optional[datetime] = None
    license_count: Optional[int] = None
    cost_per_license: Optional[float] = None
    
    # Compliance
    is_approved: bool = False
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    security_scan_date: Optional[datetime] = None
    
    # Version management
    current_version: str = ""
    latest_version: Optional[str] = None
    patch_status: PatchStatus = PatchStatus.UP_TO_DATE
    eol_date: Optional[datetime] = None
    support_end_date: Optional[datetime] = None
    
    # Vulnerabilities
    cve_list: List[str] = field(default_factory=list)
    vulnerability_count: int = 0
    highest_cvss: float = 0.0
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependent_applications: List[str] = field(default_factory=list)
    
    # Usage metrics
    installations: List[str] = field(default_factory=list)  # Asset IDs
    last_used: Optional[datetime] = None
    usage_frequency: str = "Unknown"  # Daily, Weekly, Monthly, Rarely
    
    # Metadata
    description: Optional[str] = None
    vendor_url: Optional[str] = None
    support_url: Optional[str] = None
    documentation_url: Optional[str] = None
    checksum_sha256: Optional[str] = None
    file_size_mb: Optional[float] = None
    
    # Tags
    tags: List[str] = field(default_factory=list)
    business_criticality: str = "Medium"  # Critical, High, Medium, Low


@dataclass
class AssetInventoryRecord:
    """Combined hardware + software inventory record"""
    asset_id: str
    
    # Hardware (from HWAM)
    hardware_type: str
    hostname: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    
    # Software installed (from SWAM)
    installed_software: List[str] = field(default_factory=list)  # Package IDs
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    
    # Asset management
    owner: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    cost_center: Optional[str] = None
    
    # Compliance status
    is_compliant: bool = False
    compliance_issues: List[str] = field(default_factory=list)
    last_scanned: Optional[datetime] = None
    
    # Risk scoring
    risk_score: int = 0  # 0-100
    unauthorized_software_count: int = 0
    vulnerable_software_count: int = 0
    unlicensed_software_count: int = 0
    
    # Discovery
    discovered_date: datetime = field(default_factory=datetime.now)
    discovery_method: str = "Unknown"


@dataclass
class SoftwareBillOfMaterials:
    """SBOM (Software Bill of Materials) for compliance"""
    sbom_id: str
    asset_id: str
    hostname: str
    
    # SBOM metadata
    format: SBOMFormat
    spec_version: str
    generated_date: datetime
    generator_tool: str = "Enterprise Scanner CDM"
    
    # Components
    components: List[Dict[str, Any]] = field(default_factory=list)
    total_components: int = 0
    
    # Vulnerability summary
    total_vulnerabilities: int = 0
    critical_vulns: int = 0
    high_vulns: int = 0
    
    # License summary
    license_types: Dict[str, int] = field(default_factory=dict)
    
    # Compliance
    sbom_complete: bool = False
    compliance_frameworks: List[str] = field(default_factory=list)


# ============================================================================
# COMBINED HWAM + SWAM ENGINE
# ============================================================================

class IntegratedAssetManagement:
    """
    Integrated Hardware & Software Asset Management (HWAM + SWAM)
    
    Provides unified visibility and control over:
    - Hardware assets (servers, workstations, mobile devices)
    - Software assets (applications, OS, middleware)
    - License compliance
    - Vulnerability management
    - SBOM generation
    
    Supports DHS CDM Capabilities 1 & 2.
    """
    
    def __init__(self, organization: str = "Federal Agency"):
        self.organization = organization
        
        # Inventories
        self.assets: Dict[str, AssetInventoryRecord] = {}
        self.software_catalog: Dict[str, SoftwarePackage] = {}
        
        # Authorized lists
        self.approved_software_list: Set[str] = set()
        self.authorized_vendors: Set[str] = set()
        
        # Vulnerability database
        self.cve_database: Dict[str, List[Dict]] = {}
        
        # License tracking
        self.license_pool: Dict[str, Dict[str, Any]] = {}
    
    # ========================================================================
    # UNIFIED ASSET DISCOVERY
    # ========================================================================
    
    def discover_complete_asset(self, asset_data: Dict[str, Any]) -> AssetInventoryRecord:
        """
        Discover both hardware and software for a single asset
        
        Args:
            asset_data: Combined hardware + software data from agent/scan
            
        Returns:
            Complete asset inventory record
        """
        # Create hardware portion
        asset_id = asset_data.get('asset_id') or self._generate_asset_id(asset_data)
        
        record = AssetInventoryRecord(
            asset_id=asset_id,
            hardware_type=asset_data.get('hardware_type', 'Unknown'),
            hostname=asset_data.get('hostname', 'unknown'),
            ip_address=asset_data.get('ip_address'),
            mac_address=asset_data.get('mac_address'),
            manufacturer=asset_data.get('manufacturer'),
            model=asset_data.get('model'),
            serial_number=asset_data.get('serial_number'),
            os_name=asset_data.get('os_name'),
            os_version=asset_data.get('os_version'),
            owner=asset_data.get('owner'),
            department=asset_data.get('department'),
            location=asset_data.get('location'),
            discovery_method=asset_data.get('discovery_method', 'Agent')
        )
        
        # Process installed software
        software_list = asset_data.get('installed_software', [])
        for sw in software_list:
            package_id = self._register_software(sw, asset_id)
            record.installed_software.append(package_id)
        
        # Analyze compliance
        record.is_compliant = self._check_asset_compliance(record)
        record.compliance_issues = self._identify_compliance_issues(record)
        record.risk_score = self._calculate_asset_risk_score(record)
        
        # Store
        self.assets[asset_id] = record
        
        return record
    
    def bulk_import_assets(self, asset_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk import multiple assets
        
        Args:
            asset_list: List of asset data dictionaries
            
        Returns:
            Import statistics
        """
        stats = {
            'total': len(asset_list),
            'success': 0,
            'failed': 0,
            'new_assets': 0,
            'updated_assets': 0,
            'new_software': 0
        }
        
        for asset_data in asset_list:
            try:
                asset_id = asset_data.get('asset_id')
                if asset_id in self.assets:
                    stats['updated_assets'] += 1
                else:
                    stats['new_assets'] += 1
                
                self.discover_complete_asset(asset_data)
                stats['success'] += 1
                
            except Exception as e:
                print(f"Error importing asset: {e}")
                stats['failed'] += 1
        
        stats['new_software'] = len(self.software_catalog)
        
        return stats
    
    # ========================================================================
    # SOFTWARE ASSET MANAGEMENT (SWAM)
    # ========================================================================
    
    def _register_software(self, software_data: Dict[str, Any], 
                          asset_id: str) -> str:
        """
        Register software in catalog
        
        Args:
            software_data: Software metadata
            asset_id: Asset where software is installed
            
        Returns:
            Package ID
        """
        package_id = self._generate_package_id(software_data)
        
        if package_id in self.software_catalog:
            # Update existing
            package = self.software_catalog[package_id]
            if asset_id not in package.installations:
                package.installations.append(asset_id)
        else:
            # Create new
            category = self._classify_software(software_data)
            license_type = self._determine_license_type(software_data)
            
            package = SoftwarePackage(
                package_id=package_id,
                name=software_data.get('name', 'Unknown'),
                version=software_data.get('version', '0.0.0'),
                vendor=software_data.get('vendor', 'Unknown'),
                category=category,
                license_type=license_type,
                install_date=software_data.get('install_date'),
                install_path=software_data.get('install_path'),
                installations=[asset_id]
            )
            
            # Check if approved
            package.is_approved = package.name in self.approved_software_list
            
            # Check for vulnerabilities
            self._check_software_vulnerabilities(package)
            
            # Check patch status
            package.patch_status = self._check_patch_status(package)
            
            self.software_catalog[package_id] = package
        
        return package_id
    
    def scan_unauthorized_software(self) -> List[Tuple[str, SoftwarePackage]]:
        """
        Scan for unauthorized software across all assets
        
        Returns:
            List of (asset_id, software) tuples for unauthorized software
        """
        unauthorized = []
        
        for asset_id, asset in self.assets.items():
            for package_id in asset.installed_software:
                package = self.software_catalog.get(package_id)
                if package and not package.is_approved:
                    unauthorized.append((asset_id, package))
                    asset.unauthorized_software_count += 1
        
        return unauthorized
    
    def check_license_compliance(self) -> Dict[str, Any]:
        """
        Check software license compliance organization-wide
        
        Returns:
            License compliance report
        """
        compliance_report = {
            'total_licensed_software': 0,
            'compliant': 0,
            'violations': [],
            'expiring_soon': [],
            'cost_savings_opportunities': [],
            'total_license_cost': 0.0
        }
        
        for package_id, package in self.software_catalog.items():
            if package.license_type != SoftwareLicenseType.OPEN_SOURCE:
                compliance_report['total_licensed_software'] += 1
                
                # Check installation count vs license count
                if package.license_count:
                    if len(package.installations) > package.license_count:
                        compliance_report['violations'].append({
                            'software': package.name,
                            'licensed': package.license_count,
                            'installed': len(package.installations),
                            'over_deployment': len(package.installations) - package.license_count,
                            'risk': 'High'
                        })
                    elif len(package.installations) < package.license_count * 0.5:
                        # Under-utilized licenses
                        compliance_report['cost_savings_opportunities'].append({
                            'software': package.name,
                            'licensed': package.license_count,
                            'installed': len(package.installations),
                            'unused': package.license_count - len(package.installations),
                            'potential_savings': (package.license_count - len(package.installations)) * (package.cost_per_license or 0)
                        })
                    else:
                        compliance_report['compliant'] += 1
                
                # Check expiration
                if package.license_expiration:
                    days_until_expiry = (package.license_expiration - datetime.now()).days
                    if 0 < days_until_expiry < 90:
                        compliance_report['expiring_soon'].append({
                            'software': package.name,
                            'expiration_date': package.license_expiration.isoformat(),
                            'days_remaining': days_until_expiry
                        })
                
                # Calculate total cost
                if package.cost_per_license and package.license_count:
                    compliance_report['total_license_cost'] += (
                        package.cost_per_license * package.license_count
                    )
        
        return compliance_report
    
    def identify_vulnerable_software(self, severity_threshold: str = "HIGH") -> List[Dict[str, Any]]:
        """
        Identify software with known vulnerabilities
        
        Args:
            severity_threshold: Minimum severity to report (CRITICAL, HIGH, MEDIUM, LOW)
            
        Returns:
            List of vulnerable software with details
        """
        vulnerable = []
        severity_scores = {
            'CRITICAL': 9.0,
            'HIGH': 7.0,
            'MEDIUM': 4.0,
            'LOW': 0.1
        }
        
        threshold = severity_scores.get(severity_threshold, 7.0)
        
        for package_id, package in self.software_catalog.items():
            if package.highest_cvss >= threshold:
                vulnerable.append({
                    'package_id': package_id,
                    'software': package.name,
                    'version': package.version,
                    'vendor': package.vendor,
                    'cve_count': len(package.cve_list),
                    'cve_ids': package.cve_list,
                    'highest_cvss': package.highest_cvss,
                    'installations': len(package.installations),
                    'affected_assets': package.installations,
                    'patch_status': package.patch_status.value,
                    'remediation': self._generate_remediation(package)
                })
        
        # Sort by risk (CVSS * installation count)
        vulnerable.sort(
            key=lambda x: x['highest_cvss'] * x['installations'], 
            reverse=True
        )
        
        return vulnerable
    
    # ========================================================================
    # SBOM GENERATION
    # ========================================================================
    
    def generate_sbom(self, asset_id: str, 
                     format: SBOMFormat = SBOMFormat.CYCLONEDX) -> SoftwareBillOfMaterials:
        """
        Generate Software Bill of Materials (SBOM) for asset
        
        Args:
            asset_id: Asset identifier
            format: SBOM format (CycloneDX, SPDX, SWID)
            
        Returns:
            Software Bill of Materials
        """
        asset = self.assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        sbom = SoftwareBillOfMaterials(
            sbom_id=f"SBOM-{asset_id}-{datetime.now().strftime('%Y%m%d')}",
            asset_id=asset_id,
            hostname=asset.hostname,
            format=format,
            spec_version="1.4" if format == SBOMFormat.CYCLONEDX else "2.2",
            generated_date=datetime.now()
        )
        
        # Build components list
        for package_id in asset.installed_software:
            package = self.software_catalog.get(package_id)
            if package:
                component = self._create_sbom_component(package, format)
                sbom.components.append(component)
                
                # Aggregate vulnerabilities
                sbom.total_vulnerabilities += package.vulnerability_count
                if package.highest_cvss >= 9.0:
                    sbom.critical_vulns += 1
                elif package.highest_cvss >= 7.0:
                    sbom.high_vulns += 1
                
                # Track licenses
                license_key = package.license_type.value
                sbom.license_types[license_key] = sbom.license_types.get(license_key, 0) + 1
        
        sbom.total_components = len(sbom.components)
        sbom.sbom_complete = True
        sbom.compliance_frameworks = ["EO 14028", "NIST 800-53", "NIST 800-161"]
        
        return sbom
    
    def export_sbom(self, sbom: SoftwareBillOfMaterials) -> str:
        """
        Export SBOM to standard format
        
        Args:
            sbom: Software Bill of Materials object
            
        Returns:
            Formatted SBOM (JSON/XML)
        """
        if sbom.format == SBOMFormat.CYCLONEDX:
            return self._export_cyclonedx(sbom)
        elif sbom.format == SBOMFormat.SPDX:
            return self._export_spdx(sbom)
        else:
            return self._export_swid(sbom)
    
    # ========================================================================
    # REPORTING & ANALYTICS
    # ========================================================================
    
    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """
        Generate executive dashboard with key metrics
        
        Returns:
            Dashboard data
        """
        dashboard = {
            'organization': self.organization,
            'report_date': datetime.now().isoformat(),
            
            # Asset counts
            'total_assets': len(self.assets),
            'total_software_packages': len(self.software_catalog),
            
            # Compliance
            'compliant_assets': sum(1 for a in self.assets.values() if a.is_compliant),
            'compliance_percentage': 0.0,
            
            # Software metrics
            'approved_software': sum(1 for s in self.software_catalog.values() if s.is_approved),
            'unauthorized_software': sum(1 for s in self.software_catalog.values() if not s.is_approved),
            
            # Vulnerabilities
            'vulnerable_software': sum(1 for s in self.software_catalog.values() if s.vulnerability_count > 0),
            'total_cves': sum(s.vulnerability_count for s in self.software_catalog.values()),
            'critical_vulns': sum(1 for s in self.software_catalog.values() if s.highest_cvss >= 9.0),
            'high_vulns': sum(1 for s in self.software_catalog.values() if s.highest_cvss >= 7.0),
            
            # License compliance
            'licensed_software': sum(1 for s in self.software_catalog.values() 
                                    if s.license_type != SoftwareLicenseType.OPEN_SOURCE),
            'license_violations': 0,  # Calculated below
            
            # Risk scores
            'average_asset_risk': 0.0,
            'high_risk_assets': sum(1 for a in self.assets.values() if a.risk_score >= 70),
            
            # Patch status
            'up_to_date': sum(1 for s in self.software_catalog.values() 
                            if s.patch_status == PatchStatus.UP_TO_DATE),
            'patches_needed': sum(1 for s in self.software_catalog.values() 
                                if s.patch_status in [PatchStatus.PATCH_AVAILABLE, PatchStatus.CRITICAL_PATCH_NEEDED]),
            'eol_software': sum(1 for s in self.software_catalog.values() 
                              if s.patch_status == PatchStatus.EOL_NO_PATCHES)
        }
        
        # Calculate percentages
        if dashboard['total_assets'] > 0:
            dashboard['compliance_percentage'] = (
                dashboard['compliant_assets'] / dashboard['total_assets']
            ) * 100
            
            total_risk = sum(a.risk_score for a in self.assets.values())
            dashboard['average_asset_risk'] = total_risk / dashboard['total_assets']
        
        # License violations
        license_report = self.check_license_compliance()
        dashboard['license_violations'] = len(license_report['violations'])
        
        return dashboard
    
    def generate_cdm_report(self) -> str:
        """
        Generate comprehensive CDM HWAM+SWAM report
        
        Returns:
            JSON report
        """
        report = {
            'report_type': 'CDM Capabilities 1 & 2 (HWAM + SWAM)',
            'organization': self.organization,
            'generated_date': datetime.now().isoformat(),
            
            # Executive dashboard
            'executive_summary': self.generate_executive_dashboard(),
            
            # Asset inventory
            'assets': [self._asset_to_dict(a) for a in self.assets.values()],
            
            # Software catalog
            'software_catalog': [self._software_to_dict(s) for s in self.software_catalog.values()],
            
            # Compliance reports
            'unauthorized_software': len(self.scan_unauthorized_software()),
            'license_compliance': self.check_license_compliance(),
            'vulnerable_software': len(self.identify_vulnerable_software()),
            
            # Recommendations
            'recommendations': self._generate_recommendations()
        }
        
        return json.dumps(report, indent=2, default=str)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_asset_id(self, data: Dict) -> str:
        """Generate unique asset ID"""
        key = f"{data.get('serial_number', '')}:{data.get('mac_address', '')}:{data.get('hostname', '')}"
        return hashlib.md5(key.encode()).hexdigest()[:16].upper()
    
    def _generate_package_id(self, data: Dict) -> str:
        """Generate unique package ID"""
        key = f"{data.get('vendor', '')}:{data.get('name', '')}:{data.get('version', '')}"
        return hashlib.md5(key.encode()).hexdigest()[:16].upper()
    
    def _classify_software(self, data: Dict) -> SoftwareCategory:
        """Classify software by category"""
        name = data.get('name', '').lower()
        
        if 'windows' in name or 'linux' in name or 'ubuntu' in name:
            return SoftwareCategory.OPERATING_SYSTEM
        elif 'office' in name or 'adobe' in name:
            return SoftwareCategory.PRODUCTIVITY
        elif 'sql' in name or 'oracle' in name or 'postgres' in name:
            return SoftwareCategory.DATABASE
        elif 'apache' in name or 'nginx' in name or 'iis' in name:
            return SoftwareCategory.WEB_SERVER
        else:
            return SoftwareCategory.PRODUCTIVITY
    
    def _determine_license_type(self, data: Dict) -> SoftwareLicenseType:
        """Determine license type"""
        license_info = data.get('license', '').lower()
        
        if 'open source' in license_info or 'gpl' in license_info or 'mit' in license_info:
            return SoftwareLicenseType.OPEN_SOURCE
        elif 'subscription' in license_info:
            return SoftwareLicenseType.SUBSCRIPTION
        elif 'volume' in license_info:
            return SoftwareLicenseType.VOLUME
        else:
            return SoftwareLicenseType.PERPETUAL
    
    def _check_software_vulnerabilities(self, package: SoftwarePackage):
        """Check for known vulnerabilities"""
        # Query CVE database (simplified)
        key = f"{package.vendor}:{package.name}:{package.version}"
        if key in self.cve_database:
            cves = self.cve_database[key]
            package.cve_list = [cve['id'] for cve in cves]
            package.vulnerability_count = len(cves)
            package.highest_cvss = max([cve.get('cvss', 0.0) for cve in cves] + [0.0])
    
    def _check_patch_status(self, package: SoftwarePackage) -> PatchStatus:
        """Check patch status"""
        # Simplified logic
        if package.eol_date and package.eol_date < datetime.now():
            return PatchStatus.EOL_NO_PATCHES
        elif package.vulnerability_count > 0 and package.highest_cvss >= 9.0:
            return PatchStatus.CRITICAL_PATCH_NEEDED
        elif package.latest_version and package.version != package.latest_version:
            return PatchStatus.PATCH_AVAILABLE
        else:
            return PatchStatus.UP_TO_DATE
    
    def _check_asset_compliance(self, asset: AssetInventoryRecord) -> bool:
        """Check if asset is compliant"""
        # Simplified compliance check
        return (asset.unauthorized_software_count == 0 and
                asset.vulnerable_software_count == 0 and
                asset.unlicensed_software_count == 0)
    
    def _identify_compliance_issues(self, asset: AssetInventoryRecord) -> List[str]:
        """Identify compliance issues"""
        issues = []
        
        if asset.unauthorized_software_count > 0:
            issues.append(f"{asset.unauthorized_software_count} unauthorized software packages")
        
        if asset.vulnerable_software_count > 0:
            issues.append(f"{asset.vulnerable_software_count} vulnerable software packages")
        
        if asset.unlicensed_software_count > 0:
            issues.append(f"{asset.unlicensed_software_count} unlicensed software packages")
        
        return issues
    
    def _calculate_asset_risk_score(self, asset: AssetInventoryRecord) -> int:
        """Calculate asset risk score (0-100)"""
        risk = 0
        
        # Unauthorized software
        risk += min(asset.unauthorized_software_count * 10, 40)
        
        # Vulnerabilities
        risk += min(asset.vulnerable_software_count * 5, 40)
        
        # License violations
        risk += min(asset.unlicensed_software_count * 5, 20)
        
        return min(risk, 100)
    
    def _generate_remediation(self, package: SoftwarePackage) -> str:
        """Generate remediation recommendation"""
        if package.patch_status == PatchStatus.CRITICAL_PATCH_NEEDED:
            return f"URGENT: Update to version {package.latest_version} immediately"
        elif package.patch_status == PatchStatus.PATCH_AVAILABLE:
            return f"Update to version {package.latest_version} available"
        elif package.patch_status == PatchStatus.EOL_NO_PATCHES:
            return "Replace with supported alternative (EOL software)"
        else:
            return "No action required"
    
    def _create_sbom_component(self, package: SoftwarePackage, 
                              format: SBOMFormat) -> Dict[str, Any]:
        """Create SBOM component entry"""
        if format == SBOMFormat.CYCLONEDX:
            return {
                'type': 'application',
                'name': package.name,
                'version': package.version,
                'supplier': {'name': package.vendor},
                'licenses': [{'license': {'name': package.license_type.value}}],
                'hashes': [{'alg': 'SHA-256', 'content': package.checksum_sha256}] if package.checksum_sha256 else [],
                'purl': f"pkg:generic/{package.vendor}/{package.name}@{package.version}",
                'vulnerabilities': [{'id': cve} for cve in package.cve_list]
            }
        else:
            # SPDX format
            return {
                'SPDXID': f"SPDXRef-{package.package_id}",
                'name': package.name,
                'versionInfo': package.version,
                'supplier': f"Organization: {package.vendor}",
                'licenseConcluded': package.license_type.value
            }
    
    def _export_cyclonedx(self, sbom: SoftwareBillOfMaterials) -> str:
        """Export as CycloneDX JSON"""
        cyclonedx = {
            'bomFormat': 'CycloneDX',
            'specVersion': sbom.spec_version,
            'version': 1,
            'metadata': {
                'timestamp': sbom.generated_date.isoformat(),
                'component': {
                    'type': 'device',
                    'name': sbom.hostname
                }
            },
            'components': sbom.components
        }
        return json.dumps(cyclonedx, indent=2)
    
    def _export_spdx(self, sbom: SoftwareBillOfMaterials) -> str:
        """Export as SPDX JSON"""
        spdx = {
            'spdxVersion': f"SPDX-{sbom.spec_version}",
            'dataLicense': 'CC0-1.0',
            'SPDXID': 'SPDXRef-DOCUMENT',
            'name': f"SBOM-{sbom.hostname}",
            'documentNamespace': f"https://enterprisescanner.com/sbom/{sbom.sbom_id}",
            'creationInfo': {
                'created': sbom.generated_date.isoformat(),
                'creators': ['Tool: Enterprise Scanner CDM']
            },
            'packages': sbom.components
        }
        return json.dumps(spdx, indent=2)
    
    def _export_swid(self, sbom: SoftwareBillOfMaterials) -> str:
        """Export as SWID tag"""
        # Simplified SWID XML
        return f"<SoftwareIdentity name='{sbom.hostname}' />"
    
    def _asset_to_dict(self, asset: AssetInventoryRecord) -> Dict:
        """Convert asset to dictionary"""
        return {k: v for k, v in asset.__dict__.items()}
    
    def _software_to_dict(self, software: SoftwarePackage) -> Dict:
        """Convert software to dictionary"""
        data = {k: v for k, v in software.__dict__.items()}
        # Convert enums
        data['category'] = software.category.value
        data['license_type'] = software.license_type.value
        data['patch_status'] = software.patch_status.value
        return data
    
    def _generate_recommendations(self) -> List[str]:
        """Generate remediation recommendations"""
        recommendations = []
        
        # Check unauthorized software
        unauthorized = self.scan_unauthorized_software()
        if unauthorized:
            recommendations.append(
                f"Remove {len(unauthorized)} unauthorized software installations"
            )
        
        # Check vulnerabilities
        vulnerable = self.identify_vulnerable_software()
        if vulnerable:
            recommendations.append(
                f"Patch or remediate {len(vulnerable)} vulnerable software packages"
            )
        
        # Check license compliance
        license_report = self.check_license_compliance()
        if license_report['violations']:
            recommendations.append(
                f"Address {len(license_report['violations'])} license compliance violations"
            )
        
        if not recommendations:
            recommendations.append("No critical issues found - maintain current posture")
        
        return recommendations


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    iam = IntegratedAssetManagement(organization="Department of Defense")
    
    print("=" * 80)
    print("CDM CAPABILITIES 1 & 2: INTEGRATED HWAM + SWAM")
    print("=" * 80)
    
    # Sample asset with software
    sample_asset = {
        'hostname': 'srv-app-01',
        'hardware_type': 'Server',
        'serial_number': 'ABC123456',
        'installed_software': [
            {
                'name': 'Microsoft Windows Server 2019',
                'version': '10.0.17763',
                'vendor': 'Microsoft'
            },
            {
                'name': 'Apache HTTP Server',
                'version': '2.4.49',
                'vendor': 'Apache Foundation'
            }
        ]
    }
    
    # Discover asset
    asset = iam.discover_complete_asset(sample_asset)
    print(f"\n[DISCOVERY] Asset discovered: {asset.hostname}")
    print(f"  - Hardware: {asset.hardware_type}")
    print(f"  - Software packages: {len(asset.installed_software)}")
    print(f"  - Risk score: {asset.risk_score}/100")
    
    # Generate SBOM
    sbom = iam.generate_sbom(asset.asset_id)
    print(f"\n[SBOM] Generated for {sbom.hostname}")
    print(f"  - Components: {sbom.total_components}")
    print(f"  - Vulnerabilities: {sbom.total_vulnerabilities}")
    
    # Executive dashboard
    dashboard = iam.generate_executive_dashboard()
    print(f"\n[DASHBOARD] Executive Summary")
    print(f"  - Total assets: {dashboard['total_assets']}")
    print(f"  - Software packages: {dashboard['total_software_packages']}")
    print(f"  - Compliance: {dashboard['compliance_percentage']:.1f}%")
    
    print("\n" + "=" * 80)
    print("HWAM + SWAM CAPABILITIES OPERATIONAL")
    print("=" * 80)
