"""
Military Upgrade #25: Compliance Automation
Part 1: Compliance Framework Mapping

This module provides comprehensive mapping across multiple compliance
frameworks to eliminate redundant audits and streamline compliance.

Key Features:
- Multi-framework control mapping (NIST, ISO, PCI, HIPAA, SOC 2)
- Control inheritance and family grouping
- Gap analysis automation
- Compliance posture scoring
- Cross-framework equivalence mapping

Compliance Frameworks:
- NIST 800-53 Rev 5 (20 control families, 1,000+ controls)
- ISO 27001:2022 (93 controls, 4 domains)
- PCI DSS v4.0 (12 requirements, 300+ sub-requirements)
- HIPAA Security Rule (45 CFR Part 164)
- SOC 2 Trust Services Criteria (5 categories)
- GDPR (99 articles, 173 recitals)
- FedRAMP (325 baseline controls)
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    NIST_800_53 = "nist_800_53_rev5"
    ISO_27001 = "iso_27001_2022"
    PCI_DSS = "pci_dss_v4"
    HIPAA = "hipaa_security_rule"
    SOC2 = "soc2_tsc"
    GDPR = "gdpr"
    FEDRAMP = "fedramp"
    CMMC = "cmmc_2_0"


class ControlStatus(Enum):
    """Control implementation status"""
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    NOT_APPLICABLE = "not_applicable"


class ComplianceLevel(Enum):
    """Compliance maturity levels"""
    LEVEL_0 = 0  # Non-compliant
    LEVEL_1 = 1  # Initial/Ad-hoc
    LEVEL_2 = 2  # Managed
    LEVEL_3 = 3  # Defined
    LEVEL_4 = 4  # Quantitatively Managed
    LEVEL_5 = 5  # Optimizing


@dataclass
class ComplianceControl:
    """Single compliance control"""
    control_id: str
    framework: ComplianceFramework
    control_family: str
    title: str
    description: str
    
    # Implementation
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    implementation_date: Optional[datetime] = None
    
    # Evidence
    evidence_required: List[str] = field(default_factory=list)
    evidence_collected: List[str] = field(default_factory=list)
    
    # Relationships
    parent_control: Optional[str] = None
    child_controls: List[str] = field(default_factory=list)
    related_controls: List[str] = field(default_factory=list)
    
    # Cross-framework mapping
    equivalent_controls: Dict[ComplianceFramework, List[str]] = field(default_factory=dict)
    
    # Testing
    last_tested: Optional[datetime] = None
    test_frequency_days: int = 90
    test_result: Optional[str] = None


@dataclass
class FrameworkMapping:
    """Mapping between two frameworks"""
    source_framework: ComplianceFramework
    target_framework: ComplianceFramework
    control_mappings: Dict[str, List[str]] = field(default_factory=dict)  # source_id -> [target_ids]


class ComplianceMapper:
    """Compliance framework mapping and automation engine"""
    
    def __init__(self):
        self.controls: Dict[str, ComplianceControl] = {}
        self.mappings: List[FrameworkMapping] = []
        
        # Load control library
        self._load_control_library()
        
        # Load cross-framework mappings
        self._load_framework_mappings()
    
    def _load_control_library(self):
        """Load comprehensive control library"""
        # NIST 800-53 Rev 5 controls (sample)
        nist_controls = [
            {
                'id': 'AC-1', 'family': 'Access Control', 'title': 'Policy and Procedures',
                'description': 'Develop, document, and disseminate access control policy',
                'evidence': ['Policy documents', 'Review records', 'Distribution logs']
            },
            {
                'id': 'AC-2', 'family': 'Access Control', 'title': 'Account Management',
                'description': 'Manage information system accounts',
                'evidence': ['User provisioning logs', 'Access reviews', 'Termination records']
            },
            {
                'id': 'AC-3', 'family': 'Access Control', 'title': 'Access Enforcement',
                'description': 'Enforce approved authorizations',
                'evidence': ['Access logs', 'Authorization matrices', 'System configs']
            },
            {
                'id': 'AU-2', 'family': 'Audit and Accountability', 'title': 'Event Logging',
                'description': 'Determine auditable events',
                'evidence': ['Audit policy', 'Log samples', 'Event definitions']
            },
            {
                'id': 'AU-6', 'family': 'Audit and Accountability', 'title': 'Audit Review',
                'description': 'Review and analyze audit records',
                'evidence': ['Review procedures', 'Analysis reports', 'Findings documentation']
            },
            {
                'id': 'IA-2', 'family': 'Identification and Authentication', 
                'title': 'User Identification and Authentication',
                'description': 'Uniquely identify and authenticate users',
                'evidence': ['Authentication logs', 'User directory', 'MFA configs']
            },
            {
                'id': 'SC-7', 'family': 'System and Communications Protection',
                'title': 'Boundary Protection',
                'description': 'Monitor and control communications at system boundaries',
                'evidence': ['Firewall configs', 'Network diagrams', 'DMZ documentation']
            },
            {
                'id': 'SI-4', 'family': 'System and Information Integrity',
                'title': 'System Monitoring',
                'description': 'Monitor systems to detect attacks and indicators',
                'evidence': ['IDS/IPS configs', 'SIEM logs', 'Alert definitions']
            }
        ]
        
        for ctrl in nist_controls:
            control = ComplianceControl(
                control_id=ctrl['id'],
                framework=ComplianceFramework.NIST_800_53,
                control_family=ctrl['family'],
                title=ctrl['title'],
                description=ctrl['description'],
                evidence_required=ctrl['evidence']
            )
            self.controls[f"NIST-{ctrl['id']}"] = control
        
        # ISO 27001:2022 controls (sample)
        iso_controls = [
            {
                'id': 'A.5.1', 'family': 'Organizational Controls', 
                'title': 'Policies for information security',
                'description': 'Information security policy and topic-specific policies',
                'evidence': ['Information security policy', 'Topic-specific policies']
            },
            {
                'id': 'A.5.10', 'family': 'Organizational Controls',
                'title': 'Acceptable use of information and other associated assets',
                'description': 'Rules for acceptable use',
                'evidence': ['Acceptable use policy', 'Acknowledgment records']
            },
            {
                'id': 'A.8.2', 'family': 'Technological Controls',
                'title': 'Privileged access rights',
                'description': 'Allocation and use of privileged access rights',
                'evidence': ['Privileged access logs', 'Review records', 'Authorization matrix']
            },
            {
                'id': 'A.8.5', 'family': 'Technological Controls',
                'title': 'Secure authentication',
                'description': 'Secure authentication technologies and procedures',
                'evidence': ['Authentication policy', 'MFA implementation', 'Password standards']
            }
        ]
        
        for ctrl in iso_controls:
            control = ComplianceControl(
                control_id=ctrl['id'],
                framework=ComplianceFramework.ISO_27001,
                control_family=ctrl['family'],
                title=ctrl['title'],
                description=ctrl['description'],
                evidence_required=ctrl['evidence']
            )
            self.controls[f"ISO-{ctrl['id']}"] = control
        
        # PCI DSS v4.0 requirements (sample)
        pci_controls = [
            {
                'id': '1.1.1', 'family': 'Requirement 1', 
                'title': 'Network security controls processes and procedures',
                'description': 'Documented processes for network security controls',
                'evidence': ['Network security policy', 'Procedures', 'Review records']
            },
            {
                'id': '2.2.1', 'family': 'Requirement 2',
                'title': 'Configuration standards for system components',
                'description': 'Hardening standards for all system components',
                'evidence': ['Hardening standards', 'Configuration baselines', 'Compliance scans']
            },
            {
                'id': '8.3.1', 'family': 'Requirement 8',
                'title': 'Multi-factor authentication',
                'description': 'MFA for all access to CDE',
                'evidence': ['MFA implementation', 'Authentication logs', 'User enrollment']
            },
            {
                'id': '10.2.1', 'family': 'Requirement 10',
                'title': 'Audit logs to detect anomalies',
                'description': 'Audit logs capture user activities',
                'evidence': ['Audit logs', 'Log retention policy', 'Review procedures']
            }
        ]
        
        for ctrl in pci_controls:
            control = ComplianceControl(
                control_id=ctrl['id'],
                framework=ComplianceFramework.PCI_DSS,
                control_family=ctrl['family'],
                title=ctrl['title'],
                description=ctrl['description'],
                evidence_required=ctrl['evidence']
            )
            self.controls[f"PCI-{ctrl['id']}"] = control
    
    def _load_framework_mappings(self):
        """Load cross-framework control mappings"""
        # NIST 800-53 to ISO 27001 mapping
        nist_to_iso = FrameworkMapping(
            source_framework=ComplianceFramework.NIST_800_53,
            target_framework=ComplianceFramework.ISO_27001,
            control_mappings={
                'AC-1': ['A.5.1'],  # Policy and Procedures -> Policies for IS
                'AC-2': ['A.8.2'],  # Account Management -> Privileged access
                'AC-3': ['A.8.2'],  # Access Enforcement -> Privileged access
                'IA-2': ['A.8.5'],  # User Auth -> Secure authentication
                'AU-2': ['A.8.15'], # Event Logging -> Logging
                'AU-6': ['A.8.16'], # Audit Review -> Monitoring activities
            }
        )
        self.mappings.append(nist_to_iso)
        
        # NIST 800-53 to PCI DSS mapping
        nist_to_pci = FrameworkMapping(
            source_framework=ComplianceFramework.NIST_800_53,
            target_framework=ComplianceFramework.PCI_DSS,
            control_mappings={
                'AC-2': ['8.2.1', '8.2.2'],  # Account Management
                'IA-2': ['8.3.1', '8.4.1'],  # Authentication -> MFA
                'AU-2': ['10.2.1', '10.3.1'], # Event Logging
                'SC-7': ['1.2.1', '1.3.1'],  # Boundary Protection
            }
        )
        self.mappings.append(nist_to_pci)
        
        # Update equivalent controls
        for mapping in self.mappings:
            for source_id, target_ids in mapping.control_mappings.items():
                source_key = f"{mapping.source_framework.name}-{source_id}"
                if source_key in self.controls:
                    self.controls[source_key].equivalent_controls[mapping.target_framework] = target_ids
    
    def get_control(self, control_id: str, framework: ComplianceFramework) -> Optional[ComplianceControl]:
        """Get control by ID and framework"""
        key = f"{framework.name}-{control_id}"
        return self.controls.get(key)
    
    def find_equivalent_controls(self, control_id: str, 
                                 source_framework: ComplianceFramework,
                                 target_framework: ComplianceFramework) -> List[str]:
        """Find equivalent controls in target framework"""
        key = f"{source_framework.name}-{control_id}"
        control = self.controls.get(key)
        
        if not control:
            return []
        
        return control.equivalent_controls.get(target_framework, [])
    
    def calculate_compliance_score(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Calculate compliance score for framework"""
        framework_controls = [
            c for c in self.controls.values() 
            if c.framework == framework
        ]
        
        if not framework_controls:
            return {'score': 0, 'level': ComplianceLevel.LEVEL_0}
        
        total = len(framework_controls)
        implemented = sum(1 for c in framework_controls 
                         if c.status == ControlStatus.IMPLEMENTED)
        partial = sum(1 for c in framework_controls 
                     if c.status == ControlStatus.PARTIALLY_IMPLEMENTED)
        
        # Weighted score (implemented=1.0, partial=0.5)
        score = (implemented + (partial * 0.5)) / total * 100
        
        # Determine compliance level
        if score >= 95:
            level = ComplianceLevel.LEVEL_5
        elif score >= 80:
            level = ComplianceLevel.LEVEL_4
        elif score >= 60:
            level = ComplianceLevel.LEVEL_3
        elif score >= 40:
            level = ComplianceLevel.LEVEL_2
        elif score >= 20:
            level = ComplianceLevel.LEVEL_1
        else:
            level = ComplianceLevel.LEVEL_0
        
        return {
            'framework': framework.value,
            'total_controls': total,
            'implemented': implemented,
            'partial': partial,
            'not_implemented': total - implemented - partial,
            'score': round(score, 2),
            'level': level.name,
            'level_value': level.value
        }
    
    def generate_gap_analysis(self, framework: ComplianceFramework) -> List[Dict[str, Any]]:
        """Generate gap analysis for framework"""
        gaps = []
        
        framework_controls = [
            c for c in self.controls.values() 
            if c.framework == framework
        ]
        
        for control in framework_controls:
            if control.status != ControlStatus.IMPLEMENTED:
                gap = {
                    'control_id': control.control_id,
                    'title': control.title,
                    'status': control.status.value,
                    'priority': self._calculate_gap_priority(control),
                    'evidence_gaps': [
                        e for e in control.evidence_required 
                        if e not in control.evidence_collected
                    ]
                }
                gaps.append(gap)
        
        # Sort by priority
        gaps.sort(key=lambda x: x['priority'], reverse=True)
        return gaps
    
    def _calculate_gap_priority(self, control: ComplianceControl) -> int:
        """Calculate gap priority (1-5, 5=highest)"""
        # High priority families
        critical_families = ['Access Control', 'Identification and Authentication', 
                            'System and Communications Protection']
        
        if control.control_family in critical_families:
            return 5
        elif control.status == ControlStatus.NOT_IMPLEMENTED:
            return 4
        elif len(control.equivalent_controls) > 2:
            # High leverage - maps to multiple frameworks
            return 3
        else:
            return 2
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get compliance statistics"""
        by_framework = {}
        for framework in ComplianceFramework:
            score = self.calculate_compliance_score(framework)
            if score['total_controls'] > 0:
                by_framework[framework.value] = score
        
        return {
            'total_controls': len(self.controls),
            'total_mappings': len(self.mappings),
            'by_framework': by_framework
        }


# Example usage
if __name__ == "__main__":
    mapper = ComplianceMapper()
    
    # Calculate NIST compliance
    nist_score = mapper.calculate_compliance_score(ComplianceFramework.NIST_800_53)
    print(f"📊 NIST 800-53 Compliance: {nist_score['score']}% ({nist_score['level']})")
    print(f"   Implemented: {nist_score['implemented']}/{nist_score['total_controls']}")
    
    # Find equivalent controls
    iso_equivalents = mapper.find_equivalent_controls('AC-2', 
                                                      ComplianceFramework.NIST_800_53,
                                                      ComplianceFramework.ISO_27001)
    print(f"\n🔗 NIST AC-2 maps to ISO: {iso_equivalents}")
    
    # Gap analysis
    gaps = mapper.generate_gap_analysis(ComplianceFramework.NIST_800_53)
    print(f"\n⚠️ Found {len(gaps)} gaps (top 3):")
    for gap in gaps[:3]:
        print(f"   - {gap['control_id']}: {gap['title']} (Priority: {gap['priority']})")
