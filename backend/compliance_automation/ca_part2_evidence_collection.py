"""
Military Upgrade #25: Compliance Automation
Part 2: Automated Evidence Collection

This module automates the collection, validation, and storage of
compliance evidence from multiple sources.

Key Features:
- Automated evidence gathering from logs, configs, APIs
- Evidence validation and integrity checking
- Artifact storage with retention policies
- Chain of custody tracking
- Automated screenshot and report generation

Evidence Types:
- System configurations (firewall rules, OS settings)
- Access logs (authentication, authorization, privileged access)
- Network traffic captures
- Security scan results
- Policy documents and attestations
- Training completion records
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json


class EvidenceType(Enum):
    """Types of compliance evidence"""
    SYSTEM_CONFIG = "system_config"
    ACCESS_LOG = "access_log"
    AUDIT_LOG = "audit_log"
    SCAN_RESULT = "scan_result"
    POLICY_DOCUMENT = "policy_document"
    SCREENSHOT = "screenshot"
    ATTESTATION = "attestation"
    TRAINING_RECORD = "training_record"
    NETWORK_CAPTURE = "network_capture"


class EvidenceStatus(Enum):
    """Evidence validation status"""
    PENDING = "pending"
    COLLECTED = "collected"
    VALIDATED = "validated"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class EvidenceArtifact:
    """Single piece of compliance evidence"""
    artifact_id: str
    evidence_type: EvidenceType
    control_id: str
    framework: str
    
    # Content
    title: str
    description: str
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size_bytes: int = 0
    
    # Collection metadata
    collected_at: datetime = field(default_factory=datetime.now)
    collected_by: str = "automated"
    collection_method: str = ""
    
    # Validation
    status: EvidenceStatus = EvidenceStatus.PENDING
    validated_at: Optional[datetime] = None
    validated_by: Optional[str] = None
    validation_notes: str = ""
    
    # Retention
    retention_period_days: int = 2555  # 7 years default
    expires_at: Optional[datetime] = None
    
    # Chain of custody
    custody_chain: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tags and metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvidenceCollector:
    """Automated evidence collection engine"""
    
    def __init__(self):
        self.artifacts: Dict[str, EvidenceArtifact] = {}
        self.collection_schedules: Dict[str, Dict[str, Any]] = {}
    
    def collect_system_config(self, system: str, config_type: str,
                             control_id: str, framework: str) -> EvidenceArtifact:
        """Collect system configuration evidence"""
        artifact_id = f"EVIDENCE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Simulate config collection
        config_data = self._fetch_system_config(system, config_type)
        
        # Calculate hash for integrity
        file_hash = hashlib.sha256(json.dumps(config_data).encode()).hexdigest()
        
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            evidence_type=EvidenceType.SYSTEM_CONFIG,
            control_id=control_id,
            framework=framework,
            title=f"{system} {config_type} Configuration",
            description=f"System configuration snapshot for {system}",
            file_hash=file_hash,
            file_size_bytes=len(json.dumps(config_data)),
            collection_method="API",
            status=EvidenceStatus.COLLECTED,
            metadata=config_data,
            tags=[system, config_type, "automated"]
        )
        
        # Set expiration
        artifact.expires_at = datetime.now() + timedelta(days=artifact.retention_period_days)
        
        # Record custody
        artifact.custody_chain.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'collected',
            'actor': 'automated',
            'notes': f'Collected via {artifact.collection_method}'
        })
        
        self.artifacts[artifact_id] = artifact
        
        print(f"✅ Collected evidence: {artifact_id}")
        print(f"   Type: {artifact.evidence_type.value}")
        print(f"   Control: {control_id}")
        print(f"   Hash: {file_hash[:16]}...")
        
        return artifact
    
    def _fetch_system_config(self, system: str, config_type: str) -> Dict[str, Any]:
        """Fetch system configuration (simulated)"""
        configs = {
            'firewall': {
                'system': system,
                'type': 'firewall',
                'rules_count': 47,
                'default_policy': 'deny',
                'last_modified': datetime.now().isoformat(),
                'version': '5.2.1',
                'enabled_features': ['stateful_inspection', 'ids', 'logging']
            },
            'user_access': {
                'system': system,
                'type': 'user_access',
                'total_users': 156,
                'privileged_users': 12,
                'mfa_enabled': True,
                'password_policy': {
                    'min_length': 12,
                    'complexity': 'high',
                    'expiry_days': 90
                }
            },
            'encryption': {
                'system': system,
                'type': 'encryption',
                'data_at_rest': 'AES-256',
                'data_in_transit': 'TLS 1.3',
                'key_rotation_days': 90,
                'hsm_enabled': True
            }
        }
        
        return configs.get(config_type, {'system': system, 'type': config_type})
    
    def collect_access_logs(self, system: str, time_range_hours: int,
                           control_id: str, framework: str) -> EvidenceArtifact:
        """Collect access log evidence"""
        artifact_id = f"EVIDENCE-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
        
        # Simulate log collection
        logs = self._fetch_access_logs(system, time_range_hours)
        
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            evidence_type=EvidenceType.ACCESS_LOG,
            control_id=control_id,
            framework=framework,
            title=f"{system} Access Logs ({time_range_hours}h)",
            description=f"Access logs for {system} covering last {time_range_hours} hours",
            file_size_bytes=len(str(logs)),
            collection_method="SIEM API",
            status=EvidenceStatus.COLLECTED,
            metadata={'log_count': len(logs), 'time_range_hours': time_range_hours},
            tags=[system, "access_logs", "automated"]
        )
        
        artifact.expires_at = datetime.now() + timedelta(days=artifact.retention_period_days)
        
        self.artifacts[artifact_id] = artifact
        
        print(f"✅ Collected access logs: {artifact_id}")
        print(f"   System: {system}")
        print(f"   Log entries: {len(logs)}")
        
        return artifact
    
    def _fetch_access_logs(self, system: str, hours: int) -> List[Dict[str, Any]]:
        """Fetch access logs (simulated)"""
        # Simulated log entries
        return [
            {
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'user': f'user{i % 10}',
                'action': 'login' if i % 3 == 0 else 'access',
                'resource': f'/api/resource{i % 5}',
                'result': 'success' if i % 7 != 0 else 'failure'
            }
            for i in range(min(hours * 10, 100))  # Limit to 100 entries
        ]
    
    def collect_scan_results(self, scan_type: str, target: str,
                            control_id: str, framework: str) -> EvidenceArtifact:
        """Collect security scan results"""
        artifact_id = f"EVIDENCE-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
        
        # Simulate scan results
        results = self._fetch_scan_results(scan_type, target)
        
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            evidence_type=EvidenceType.SCAN_RESULT,
            control_id=control_id,
            framework=framework,
            title=f"{scan_type} Scan - {target}",
            description=f"{scan_type} security scan results for {target}",
            collection_method="Scanner API",
            status=EvidenceStatus.COLLECTED,
            metadata=results,
            tags=[scan_type, target, "automated"]
        )
        
        artifact.expires_at = datetime.now() + timedelta(days=365)  # 1 year retention
        
        self.artifacts[artifact_id] = artifact
        
        print(f"✅ Collected scan results: {artifact_id}")
        print(f"   Scan type: {scan_type}")
        print(f"   Findings: {results['findings_count']}")
        
        return artifact
    
    def _fetch_scan_results(self, scan_type: str, target: str) -> Dict[str, Any]:
        """Fetch scan results (simulated)"""
        return {
            'scan_type': scan_type,
            'target': target,
            'scan_date': datetime.now().isoformat(),
            'findings_count': 3,
            'findings': [
                {'severity': 'low', 'title': 'Outdated SSL certificate'},
                {'severity': 'medium', 'title': 'Missing security headers'},
                {'severity': 'low', 'title': 'Verbose error messages'}
            ],
            'scan_duration_seconds': 127,
            'coverage_percent': 95.8
        }
    
    def validate_evidence(self, artifact_id: str, validator: str, 
                         approved: bool, notes: str = "") -> bool:
        """Validate collected evidence"""
        artifact = self.artifacts.get(artifact_id)
        if not artifact:
            return False
        
        artifact.status = EvidenceStatus.VALIDATED if approved else EvidenceStatus.REJECTED
        artifact.validated_at = datetime.now()
        artifact.validated_by = validator
        artifact.validation_notes = notes
        
        # Record custody
        artifact.custody_chain.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'validated' if approved else 'rejected',
            'actor': validator,
            'notes': notes
        })
        
        print(f"{'✅' if approved else '❌'} Evidence {artifact_id} {'validated' if approved else 'rejected'}")
        return True
    
    def schedule_collection(self, evidence_type: EvidenceType, 
                           control_id: str, frequency_days: int,
                           collection_params: Dict[str, Any]):
        """Schedule recurring evidence collection"""
        schedule_id = f"SCHEDULE-{control_id}-{evidence_type.value}"
        
        self.collection_schedules[schedule_id] = {
            'evidence_type': evidence_type,
            'control_id': control_id,
            'frequency_days': frequency_days,
            'params': collection_params,
            'next_collection': datetime.now() + timedelta(days=frequency_days),
            'last_collection': None
        }
        
        print(f"📅 Scheduled {evidence_type.value} collection for {control_id}")
        print(f"   Frequency: every {frequency_days} days")
    
    def check_expiring_evidence(self, days_threshold: int = 30) -> List[EvidenceArtifact]:
        """Find evidence expiring soon"""
        threshold_date = datetime.now() + timedelta(days=days_threshold)
        
        expiring = [
            artifact for artifact in self.artifacts.values()
            if artifact.expires_at and artifact.expires_at <= threshold_date
            and artifact.status != EvidenceStatus.EXPIRED
        ]
        
        return expiring
    
    def generate_evidence_report(self, control_id: str) -> Dict[str, Any]:
        """Generate evidence report for control"""
        control_artifacts = [
            a for a in self.artifacts.values()
            if a.control_id == control_id
        ]
        
        by_type = {}
        for artifact in control_artifacts:
            atype = artifact.evidence_type.value
            by_type[atype] = by_type.get(atype, 0) + 1
        
        by_status = {}
        for artifact in control_artifacts:
            status = artifact.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'control_id': control_id,
            'total_artifacts': len(control_artifacts),
            'by_type': by_type,
            'by_status': by_status,
            'validated_artifacts': sum(1 for a in control_artifacts 
                                      if a.status == EvidenceStatus.VALIDATED),
            'oldest_artifact': min((a.collected_at for a in control_artifacts), 
                                  default=None),
            'newest_artifact': max((a.collected_at for a in control_artifacts),
                                  default=None)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evidence collection statistics"""
        by_type = {}
        by_status = {}
        
        for artifact in self.artifacts.values():
            atype = artifact.evidence_type.value
            by_type[atype] = by_type.get(atype, 0) + 1
            
            status = artifact.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'total_artifacts': len(self.artifacts),
            'by_type': by_type,
            'by_status': by_status,
            'scheduled_collections': len(self.collection_schedules),
            'expiring_soon': len(self.check_expiring_evidence(30))
        }


# Example usage
if __name__ == "__main__":
    collector = EvidenceCollector()
    
    # Collect system config evidence
    config_evidence = collector.collect_system_config(
        system="web-prod-01",
        config_type="firewall",
        control_id="SC-7",
        framework="NIST-800-53"
    )
    
    # Collect access logs
    log_evidence = collector.collect_access_logs(
        system="auth-server",
        time_range_hours=24,
        control_id="AU-2",
        framework="NIST-800-53"
    )
    
    # Validate evidence
    collector.validate_evidence(
        config_evidence.artifact_id,
        validator="auditor-1",
        approved=True,
        notes="Configuration meets requirements"
    )
    
    # Statistics
    stats = collector.get_statistics()
    print(f"\n📊 Evidence: {stats['total_artifacts']} artifacts collected")
    print(f"   Validated: {stats['by_status'].get('validated', 0)}")
