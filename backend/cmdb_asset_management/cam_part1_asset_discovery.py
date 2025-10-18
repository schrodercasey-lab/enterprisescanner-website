"""
Military Upgrade #26: CMDB & Asset Management
Part 1: Asset Discovery and Inventory

This module provides comprehensive automated asset discovery and
inventory management across cloud, on-premise, and hybrid environments.

Key Features:
- Multi-source asset discovery (cloud APIs, network scans, agents)
- Real-time inventory tracking
- Asset classification and tagging
- Lifecycle management
- Shadow IT detection

Asset Types:
- Compute (VMs, containers, serverless)
- Network (routers, switches, firewalls, load balancers)
- Storage (databases, file systems, object storage)
- Applications (web apps, APIs, microservices)
- Cloud resources (S3, RDS, Lambda, etc.)

Compliance:
- NIST 800-53 CM-8 (System Component Inventory)
- PCI DSS 2.4 (Maintain inventory)
- ISO 27001 A.8.1 (Asset responsibility)
- SOC 2 CC6.1 (Logical access controls)
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AssetType(Enum):
    """Types of assets"""
    SERVER = "server"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    DATABASE = "database"
    NETWORK_DEVICE = "network_device"
    STORAGE = "storage"
    APPLICATION = "application"
    CLOUD_RESOURCE = "cloud_resource"
    ENDPOINT = "endpoint"
    IOT_DEVICE = "iot_device"


class AssetStatus(Enum):
    """Asset lifecycle status"""
    DISCOVERED = "discovered"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"
    UNKNOWN = "unknown"


class AssetCriticality(Enum):
    """Business criticality levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


@dataclass
class Asset:
    """Comprehensive asset record"""
    asset_id: str
    asset_type: AssetType
    name: str
    
    # Classification
    criticality: AssetCriticality = AssetCriticality.MEDIUM
    classification: str = "internal"  # public, internal, confidential, restricted
    
    # Status
    status: AssetStatus = AssetStatus.DISCOVERED
    health_status: str = "healthy"  # healthy, degraded, critical, unknown
    
    # Network information
    ip_addresses: List[str] = field(default_factory=list)
    mac_addresses: List[str] = field(default_factory=list)
    hostnames: List[str] = field(default_factory=list)
    
    # Technical details
    operating_system: Optional[str] = None
    os_version: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    
    # Location
    datacenter: Optional[str] = None
    rack: Optional[str] = None
    cloud_provider: Optional[str] = None
    cloud_region: Optional[str] = None
    
    # Ownership
    owner: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    
    # Lifecycle
    discovered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    commissioned_date: Optional[datetime] = None
    decommission_date: Optional[datetime] = None
    
    # Security
    is_pci_scope: bool = False
    is_hipaa_scope: bool = False
    has_pii: bool = False
    
    # Relationships
    parent_asset_id: Optional[str] = None
    child_assets: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AssetDiscoveryEngine:
    """Asset discovery and inventory management engine"""
    
    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.discovery_sources: List[str] = []
    
    def discover_network_assets(self, network_range: str) -> List[Asset]:
        """Discover assets via network scanning"""
        discovered = []
        
        print(f"\n🔍 Discovering assets in network: {network_range}")
        
        # Simulate network discovery
        discovered_hosts = self._scan_network(network_range)
        
        for host in discovered_hosts:
            asset = Asset(
                asset_id=f"ASSET-NET-{host['ip'].replace('.', '-')}",
                asset_type=self._determine_asset_type(host),
                name=host.get('hostname', f"host-{host['ip']}"),
                ip_addresses=[host['ip']],
                hostnames=[host.get('hostname', '')],
                operating_system=host.get('os'),
                os_version=host.get('os_version'),
                tags=['network_discovery', 'auto_discovered']
            )
            
            self.assets[asset.asset_id] = asset
            discovered.append(asset)
            
            print(f"   ✅ Discovered: {asset.name} ({asset.ip_addresses[0]})")
        
        print(f"\n📊 Total discovered: {len(discovered)} assets")
        return discovered
    
    def _scan_network(self, network_range: str) -> List[Dict[str, Any]]:
        """Simulate network scanning"""
        return [
            {
                'ip': '10.0.1.10',
                'hostname': 'web-prod-01',
                'os': 'Linux',
                'os_version': 'Ubuntu 22.04',
                'open_ports': [22, 80, 443],
                'services': ['ssh', 'nginx']
            },
            {
                'ip': '10.0.1.11',
                'hostname': 'db-prod-01',
                'os': 'Linux',
                'os_version': 'Ubuntu 22.04',
                'open_ports': [22, 3306],
                'services': ['ssh', 'mysql']
            },
            {
                'ip': '10.0.1.20',
                'hostname': 'fw-01',
                'os': 'Cisco IOS',
                'os_version': '15.2',
                'open_ports': [22, 443],
                'services': ['ssh', 'https']
            }
        ]
    
    def _determine_asset_type(self, host: Dict[str, Any]) -> AssetType:
        """Determine asset type from scan data"""
        services = host.get('services', [])
        os = host.get('os', '').lower()
        
        if 'mysql' in services or 'postgres' in services:
            return AssetType.DATABASE
        elif 'cisco' in os or 'juniper' in os:
            return AssetType.NETWORK_DEVICE
        elif 'nginx' in services or 'apache' in services:
            return AssetType.SERVER
        else:
            return AssetType.VIRTUAL_MACHINE
    
    def discover_cloud_assets(self, cloud_provider: str, region: str) -> List[Asset]:
        """Discover cloud resources"""
        discovered = []
        
        print(f"\n☁️ Discovering {cloud_provider} assets in {region}")
        
        # Simulate cloud API calls
        cloud_resources = self._query_cloud_api(cloud_provider, region)
        
        for resource in cloud_resources:
            asset = Asset(
                asset_id=f"ASSET-{cloud_provider.upper()}-{resource['id']}",
                asset_type=AssetType.CLOUD_RESOURCE,
                name=resource['name'],
                cloud_provider=cloud_provider,
                cloud_region=region,
                status=AssetStatus.ACTIVE,
                metadata=resource,
                tags=[cloud_provider, region, 'cloud', 'auto_discovered']
            )
            
            self.assets[asset.asset_id] = asset
            discovered.append(asset)
            
            print(f"   ✅ Discovered: {asset.name} ({resource['type']})")
        
        print(f"\n📊 Total discovered: {len(discovered)} cloud resources")
        return discovered
    
    def _query_cloud_api(self, provider: str, region: str) -> List[Dict[str, Any]]:
        """Simulate cloud API queries"""
        if provider.lower() == 'aws':
            return [
                {'id': 'i-abc123', 'name': 'web-server-prod', 'type': 'EC2', 'state': 'running'},
                {'id': 'rds-xyz789', 'name': 'main-db', 'type': 'RDS', 'state': 'available'},
                {'id': 'lb-def456', 'name': 'prod-lb', 'type': 'ELB', 'state': 'active'},
                {'id': 's3-bucket-001', 'name': 'app-data-bucket', 'type': 'S3', 'state': 'active'}
            ]
        elif provider.lower() == 'azure':
            return [
                {'id': 'vm-001', 'name': 'azure-vm-prod', 'type': 'VM', 'state': 'running'},
                {'id': 'sql-001', 'name': 'azure-sql-db', 'type': 'SQL Database', 'state': 'online'}
            ]
        return []
    
    def classify_asset(self, asset_id: str, criticality: AssetCriticality,
                      classification: str, compliance_scopes: Dict[str, bool]):
        """Classify asset for security and compliance"""
        asset = self.assets.get(asset_id)
        if not asset:
            return False
        
        asset.criticality = criticality
        asset.classification = classification
        asset.is_pci_scope = compliance_scopes.get('pci', False)
        asset.is_hipaa_scope = compliance_scopes.get('hipaa', False)
        asset.has_pii = compliance_scopes.get('pii', False)
        
        print(f"🏷️ Classified {asset.name}:")
        print(f"   Criticality: {criticality.name}")
        print(f"   Classification: {classification}")
        print(f"   Compliance: PCI={asset.is_pci_scope}, HIPAA={asset.is_hipaa_scope}")
        
        return True
    
    def detect_shadow_it(self) -> List[Asset]:
        """Detect unauthorized/unmanaged assets"""
        shadow_assets = []
        
        for asset in self.assets.values():
            # Shadow IT indicators
            if (not asset.owner or 
                not asset.department or
                'unauthorized' in asset.tags or
                asset.status == AssetStatus.UNKNOWN):
                
                shadow_assets.append(asset)
                asset.tags.append('shadow_it')
        
        if shadow_assets:
            print(f"\n⚠️ Shadow IT detected: {len(shadow_assets)} assets")
            for asset in shadow_assets[:5]:  # Show first 5
                print(f"   - {asset.name} ({asset.asset_id})")
        
        return shadow_assets
    
    def get_asset_by_ip(self, ip_address: str) -> Optional[Asset]:
        """Find asset by IP address"""
        for asset in self.assets.values():
            if ip_address in asset.ip_addresses:
                return asset
        return None
    
    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """Get all assets of specific type"""
        return [a for a in self.assets.values() if a.asset_type == asset_type]
    
    def get_critical_assets(self) -> List[Asset]:
        """Get all critical assets"""
        return [a for a in self.assets.values() 
                if a.criticality == AssetCriticality.CRITICAL]
    
    def get_compliance_scope_assets(self, scope: str) -> List[Asset]:
        """Get assets in specific compliance scope"""
        if scope.lower() == 'pci':
            return [a for a in self.assets.values() if a.is_pci_scope]
        elif scope.lower() == 'hipaa':
            return [a for a in self.assets.values() if a.is_hipaa_scope]
        elif scope.lower() == 'pii':
            return [a for a in self.assets.values() if a.has_pii]
        return []
    
    def update_asset_health(self, asset_id: str, health_status: str):
        """Update asset health status"""
        asset = self.assets.get(asset_id)
        if asset:
            asset.health_status = health_status
            asset.last_seen = datetime.now()
            print(f"💓 Health updated: {asset.name} → {health_status}")
    
    def decommission_asset(self, asset_id: str, reason: str = ""):
        """Decommission asset"""
        asset = self.assets.get(asset_id)
        if not asset:
            return False
        
        asset.status = AssetStatus.DECOMMISSIONED
        asset.decommission_date = datetime.now()
        if reason:
            asset.metadata['decommission_reason'] = reason
        
        print(f"🔴 Decommissioned: {asset.name}")
        if reason:
            print(f"   Reason: {reason}")
        
        return True
    
    def generate_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        by_type = {}
        by_status = {}
        by_criticality = {}
        
        for asset in self.assets.values():
            # By type
            atype = asset.asset_type.value
            by_type[atype] = by_type.get(atype, 0) + 1
            
            # By status
            status = asset.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # By criticality
            crit = asset.criticality.name
            by_criticality[crit] = by_criticality.get(crit, 0) + 1
        
        return {
            'total_assets': len(self.assets),
            'by_type': by_type,
            'by_status': by_status,
            'by_criticality': by_criticality,
            'critical_assets': len(self.get_critical_assets()),
            'pci_scope_assets': len(self.get_compliance_scope_assets('pci')),
            'hipaa_scope_assets': len(self.get_compliance_scope_assets('hipaa')),
            'shadow_it_assets': len([a for a in self.assets.values() if 'shadow_it' in a.tags])
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get asset management statistics"""
        active_assets = sum(1 for a in self.assets.values() 
                           if a.status == AssetStatus.ACTIVE)
        
        return {
            'total_assets': len(self.assets),
            'active_assets': active_assets,
            'discovery_sources': len(self.discovery_sources),
            'asset_types': len(set(a.asset_type for a in self.assets.values()))
        }


# Example usage
if __name__ == "__main__":
    discovery = AssetDiscoveryEngine()
    
    # Network discovery
    network_assets = discovery.discover_network_assets("10.0.1.0/24")
    
    # Cloud discovery
    cloud_assets = discovery.discover_cloud_assets("AWS", "us-east-1")
    
    # Classify critical asset
    if network_assets:
        discovery.classify_asset(
            network_assets[0].asset_id,
            AssetCriticality.CRITICAL,
            "confidential",
            {'pci': True, 'hipaa': False, 'pii': True}
        )
    
    # Generate report
    report = discovery.generate_inventory_report()
    print(f"\n📊 Inventory Report:")
    print(f"   Total assets: {report['total_assets']}")
    print(f"   Critical: {report['critical_assets']}")
    print(f"   PCI scope: {report['pci_scope_assets']}")
