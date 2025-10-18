"""
Military Upgrade #26: CMDB & Asset Management
Part 2: Configuration Management Database (CMDB)

This module implements a comprehensive CMDB for tracking configuration
items (CIs), relationships, and configuration baselines.

Key Features:
- Configuration item (CI) tracking
- CI relationships and dependencies
- Configuration baselines
- Change impact analysis
- Service mapping

CI Types:
- Hardware, Software, Network, Database
- Applications, Services, Documentation
- Business processes, Locations

Compliance:
- ITIL v4 Configuration Management
- NIST 800-53 CM-2, CM-3 (Configuration Management)
- ISO 20000 (IT Service Management)
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CIType(Enum):
    """Configuration Item types"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    DATABASE = "database"
    APPLICATION = "application"
    SERVICE = "service"
    DOCUMENTATION = "documentation"
    BUSINESS_PROCESS = "business_process"


class RelationshipType(Enum):
    """CI relationship types"""
    RUNS_ON = "runs_on"
    DEPENDS_ON = "depends_on"
    CONNECTS_TO = "connects_to"
    HOSTED_BY = "hosted_by"
    MANAGES = "manages"
    USES = "uses"
    PART_OF = "part_of"


@dataclass
class ConfigurationItem:
    """Configuration Item record"""
    ci_id: str
    ci_type: CIType
    name: str
    description: str
    
    # Configuration
    configuration: Dict[str, Any] = field(default_factory=dict)
    baseline_config: Dict[str, Any] = field(default_factory=dict)
    
    # Version control
    version: str = "1.0.0"
    config_hash: Optional[str] = None
    
    # Status
    operational_status: str = "operational"  # operational, non-operational, under_change
    
    # Lifecycle
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    modified_by: str = "system"
    
    # Ownership
    owner: Optional[str] = None
    support_group: Optional[str] = None
    
    # Relationships
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ConfigurationBaseline:
    """Configuration baseline snapshot"""
    baseline_id: str
    name: str
    description: str
    
    ci_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # ci_id -> config
    
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class CMDBEngine:
    """Configuration Management Database engine"""
    
    def __init__(self):
        self.cis: Dict[str, ConfigurationItem] = {}
        self.baselines: Dict[str, ConfigurationBaseline] = {}
    
    def register_ci(self, ci_type: CIType, name: str, description: str,
                   configuration: Dict[str, Any], **kwargs) -> ConfigurationItem:
        """Register new configuration item"""
        ci_id = f"CI-{ci_type.value.upper()}-{len(self.cis) + 1:04d}"
        
        ci = ConfigurationItem(
            ci_id=ci_id,
            ci_type=ci_type,
            name=name,
            description=description,
            configuration=configuration,
            baseline_config=configuration.copy(),  # Initial baseline
            **kwargs
        )
        
        self.cis[ci_id] = ci
        
        print(f"✅ Registered CI: {ci_id} - {name}")
        print(f"   Type: {ci_type.value}")
        
        return ci
    
    def add_relationship(self, source_ci_id: str, target_ci_id: str,
                        relationship_type: RelationshipType):
        """Add relationship between CIs"""
        source_ci = self.cis.get(source_ci_id)
        target_ci = self.cis.get(target_ci_id)
        
        if not source_ci or not target_ci:
            print(f"❌ CI not found")
            return False
        
        relationship = {
            'target_ci_id': target_ci_id,
            'relationship_type': relationship_type.value,
            'target_name': target_ci.name,
            'created_at': datetime.now().isoformat()
        }
        
        source_ci.relationships.append(relationship)
        
        print(f"🔗 Relationship added: {source_ci.name} {relationship_type.value} {target_ci.name}")
        
        return True
    
    def update_ci_configuration(self, ci_id: str, new_config: Dict[str, Any],
                               modified_by: str = "system"):
        """Update CI configuration"""
        ci = self.cis.get(ci_id)
        if not ci:
            return False
        
        # Store old config for comparison
        old_config = ci.configuration.copy()
        
        ci.configuration = new_config
        ci.last_modified = datetime.now()
        ci.modified_by = modified_by
        
        # Check for drift from baseline
        drift_detected = self._check_configuration_drift(ci)
        
        print(f"🔧 Updated CI: {ci.name}")
        print(f"   Modified by: {modified_by}")
        if drift_detected:
            print(f"   ⚠️ Configuration drift detected from baseline")
        
        return True
    
    def _check_configuration_drift(self, ci: ConfigurationItem) -> bool:
        """Check if configuration has drifted from baseline"""
        if not ci.baseline_config:
            return False
        
        # Compare current config to baseline
        drift_keys = []
        for key, baseline_value in ci.baseline_config.items():
            current_value = ci.configuration.get(key)
            if current_value != baseline_value:
                drift_keys.append(key)
        
        return len(drift_keys) > 0
    
    def create_baseline(self, name: str, description: str, 
                       ci_ids: List[str], created_by: str = "system") -> ConfigurationBaseline:
        """Create configuration baseline"""
        baseline_id = f"BASELINE-{len(self.baselines) + 1:04d}"
        
        baseline = ConfigurationBaseline(
            baseline_id=baseline_id,
            name=name,
            description=description,
            created_by=created_by
        )
        
        # Capture current configurations
        for ci_id in ci_ids:
            ci = self.cis.get(ci_id)
            if ci:
                baseline.ci_configs[ci_id] = ci.configuration.copy()
        
        self.baselines[baseline_id] = baseline
        
        print(f"📸 Created baseline: {baseline_id} - {name}")
        print(f"   CIs captured: {len(baseline.ci_configs)}")
        
        return baseline
    
    def approve_baseline(self, baseline_id: str, approved_by: str):
        """Approve configuration baseline"""
        baseline = self.baselines.get(baseline_id)
        if not baseline:
            return False
        
        baseline.approved = True
        baseline.approved_by = approved_by
        baseline.approved_at = datetime.now()
        
        # Update CI baselines
        for ci_id, config in baseline.ci_configs.items():
            ci = self.cis.get(ci_id)
            if ci:
                ci.baseline_config = config.copy()
        
        print(f"✅ Baseline approved: {baseline_id}")
        print(f"   Approved by: {approved_by}")
        
        return True
    
    def analyze_change_impact(self, ci_id: str) -> Dict[str, Any]:
        """Analyze impact of changing a CI"""
        ci = self.cis.get(ci_id)
        if not ci:
            return {}
        
        # Find all CIs that depend on this CI
        impacted_cis = []
        for other_ci in self.cis.values():
            for rel in other_ci.relationships:
                if (rel['target_ci_id'] == ci_id and 
                    rel['relationship_type'] in ['depends_on', 'runs_on', 'uses']):
                    impacted_cis.append({
                        'ci_id': other_ci.ci_id,
                        'name': other_ci.name,
                        'relationship': rel['relationship_type']
                    })
        
        # Find services affected
        affected_services = []
        for impacted in impacted_cis:
            impacted_ci = self.cis.get(impacted['ci_id'])
            if impacted_ci and impacted_ci.ci_type == CIType.SERVICE:
                affected_services.append(impacted['name'])
        
        impact_analysis = {
            'target_ci': ci.name,
            'direct_dependencies': len(impacted_cis),
            'impacted_cis': impacted_cis,
            'affected_services': affected_services,
            'risk_level': self._calculate_impact_risk(impacted_cis)
        }
        
        print(f"\n📊 Change Impact Analysis: {ci.name}")
        print(f"   Direct dependencies: {len(impacted_cis)}")
        print(f"   Affected services: {len(affected_services)}")
        print(f"   Risk level: {impact_analysis['risk_level']}")
        
        return impact_analysis
    
    def _calculate_impact_risk(self, impacted_cis: List[Dict[str, Any]]) -> str:
        """Calculate risk level of change"""
        count = len(impacted_cis)
        
        if count == 0:
            return "LOW"
        elif count <= 2:
            return "MEDIUM"
        elif count <= 5:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def generate_service_map(self, service_ci_id: str) -> Dict[str, Any]:
        """Generate service dependency map"""
        service_ci = self.cis.get(service_ci_id)
        if not service_ci:
            return {}
        
        service_map = {
            'service': service_ci.name,
            'layers': {
                'application': [],
                'database': [],
                'infrastructure': [],
                'network': []
            }
        }
        
        # Traverse relationships to build map
        self._build_service_map_recursive(service_ci, service_map, visited=set())
        
        print(f"\n🗺️ Service Map: {service_ci.name}")
        for layer, cis in service_map['layers'].items():
            if cis:
                print(f"   {layer.capitalize()}: {len(cis)} CIs")
        
        return service_map
    
    def _build_service_map_recursive(self, ci: ConfigurationItem, 
                                     service_map: Dict[str, Any],
                                     visited: Set[str]):
        """Recursively build service map"""
        if ci.ci_id in visited:
            return
        
        visited.add(ci.ci_id)
        
        # Categorize CI
        if ci.ci_type == CIType.APPLICATION:
            service_map['layers']['application'].append(ci.name)
        elif ci.ci_type == CIType.DATABASE:
            service_map['layers']['database'].append(ci.name)
        elif ci.ci_type == CIType.HARDWARE:
            service_map['layers']['infrastructure'].append(ci.name)
        elif ci.ci_type == CIType.NETWORK:
            service_map['layers']['network'].append(ci.name)
        
        # Traverse dependencies
        for rel in ci.relationships:
            if rel['relationship_type'] in ['depends_on', 'runs_on', 'uses']:
                target_ci = self.cis.get(rel['target_ci_id'])
                if target_ci:
                    self._build_service_map_recursive(target_ci, service_map, visited)
    
    def get_ci_by_name(self, name: str) -> Optional[ConfigurationItem]:
        """Find CI by name"""
        for ci in self.cis.values():
            if ci.name.lower() == name.lower():
                return ci
        return None
    
    def get_cis_by_type(self, ci_type: CIType) -> List[ConfigurationItem]:
        """Get all CIs of specific type"""
        return [ci for ci in self.cis.values() if ci.ci_type == ci_type]
    
    def get_drifted_cis(self) -> List[ConfigurationItem]:
        """Get CIs with configuration drift"""
        drifted = []
        for ci in self.cis.values():
            if self._check_configuration_drift(ci):
                drifted.append(ci)
        return drifted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get CMDB statistics"""
        by_type = {}
        for ci in self.cis.values():
            citype = ci.ci_type.value
            by_type[citype] = by_type.get(citype, 0) + 1
        
        total_relationships = sum(len(ci.relationships) for ci in self.cis.values())
        
        return {
            'total_cis': len(self.cis),
            'by_type': by_type,
            'total_relationships': total_relationships,
            'total_baselines': len(self.baselines),
            'drifted_cis': len(self.get_drifted_cis())
        }


# Example usage
if __name__ == "__main__":
    cmdb = CMDBEngine()
    
    # Register CIs
    web_server = cmdb.register_ci(
        CIType.HARDWARE,
        "web-prod-01",
        "Production web server",
        {'cpu': '8 cores', 'memory': '32GB', 'os': 'Ubuntu 22.04'}
    )
    
    web_app = cmdb.register_ci(
        CIType.APPLICATION,
        "customer-portal",
        "Customer portal application",
        {'version': '2.5.0', 'port': 8080, 'framework': 'Django'}
    )
    
    database = cmdb.register_ci(
        CIType.DATABASE,
        "customer-db",
        "Customer database",
        {'type': 'PostgreSQL', 'version': '14.5', 'size_gb': 500}
    )
    
    # Add relationships
    cmdb.add_relationship(web_app.ci_id, web_server.ci_id, RelationshipType.RUNS_ON)
    cmdb.add_relationship(web_app.ci_id, database.ci_id, RelationshipType.DEPENDS_ON)
    
    # Create baseline
    baseline = cmdb.create_baseline(
        "Production Baseline v1",
        "Initial production configuration baseline",
        [web_server.ci_id, web_app.ci_id, database.ci_id],
        created_by="admin"
    )
    
    # Analyze impact
    impact = cmdb.analyze_change_impact(database.ci_id)
    
    # Statistics
    stats = cmdb.get_statistics()
    print(f"\n📊 CMDB Statistics:")
    print(f"   Total CIs: {stats['total_cis']}")
    print(f"   Relationships: {stats['total_relationships']}")
