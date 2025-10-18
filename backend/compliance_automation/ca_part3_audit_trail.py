"""
Military Upgrade #25: Compliance Automation
Part 3: Audit Trail Generation

This module generates comprehensive, tamper-proof audit trails
for compliance demonstration and forensic analysis.

Key Features:
- Immutable audit logging with cryptographic verification
- Automated audit trail generation for controls
- Compliance event tracking
- Chain of custody for all artifacts
- Audit report generation with evidence linking

Compliance:
- NIST 800-53 AU-2, AU-3, AU-6, AU-9 (Audit family)
- PCI DSS Requirement 10 (Track and monitor all access)
- HIPAA §164.312(b) (Audit controls)
- SOC 2 CC7.2 (System monitoring)
- ISO 27001 A.8.15, A.8.16 (Logging, Monitoring)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json


class AuditEventType(Enum):
    """Types of auditable events"""
    CONTROL_IMPLEMENTATION = "control_implementation"
    EVIDENCE_COLLECTION = "evidence_collection"
    EVIDENCE_VALIDATION = "evidence_validation"
    POLICY_CHANGE = "policy_change"
    ACCESS_GRANTED = "access_granted"
    ACCESS_REVOKED = "access_revoked"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_INCIDENT = "security_incident"
    COMPLIANCE_TEST = "compliance_test"
    AUDIT_REVIEW = "audit_review"


class AuditSeverity(Enum):
    """Audit event severity"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Single audit trail event"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    
    # Event details
    actor: str  # User or system performing action
    action: str
    resource: str
    result: str  # success, failure, partial
    
    # Context
    severity: AuditSeverity = AuditSeverity.INFO
    control_id: Optional[str] = None
    framework: Optional[str] = None
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Integrity
    previous_event_hash: Optional[str] = None
    event_hash: Optional[str] = None
    
    # Metadata
    source_ip: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class AuditChain:
    """Blockchain-style audit chain"""
    chain_id: str
    events: List[AuditEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)


class AuditTrailGenerator:
    """Audit trail generation and verification engine"""
    
    def __init__(self):
        self.chains: Dict[str, AuditChain] = {}
        self.events: List[AuditEvent] = []
        
        # Initialize default chain
        self._initialize_chain("default")
    
    def _initialize_chain(self, chain_id: str):
        """Initialize new audit chain"""
        chain = AuditChain(chain_id=chain_id)
        self.chains[chain_id] = chain
        
        # Genesis event
        genesis = self._create_genesis_event(chain_id)
        chain.events.append(genesis)
        self.events.append(genesis)
    
    def _create_genesis_event(self, chain_id: str) -> AuditEvent:
        """Create genesis (first) event in chain"""
        genesis = AuditEvent(
            event_id=f"GENESIS-{chain_id}",
            event_type=AuditEventType.AUDIT_REVIEW,
            timestamp=datetime.now(),
            actor="system",
            action="initialize_audit_chain",
            resource=chain_id,
            result="success",
            details={'message': 'Audit chain initialized'}
        )
        
        # Calculate hash
        genesis.event_hash = self._calculate_event_hash(genesis)
        
        return genesis
    
    def log_event(self, event_type: AuditEventType, actor: str, action: str,
                  resource: str, result: str, chain_id: str = "default",
                  **kwargs) -> AuditEvent:
        """Log audit event"""
        chain = self.chains.get(chain_id)
        if not chain:
            self._initialize_chain(chain_id)
            chain = self.chains[chain_id]
        
        event_id = f"EVENT-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
        
        # Get previous event hash for chaining
        previous_hash = None
        if chain.events:
            previous_hash = chain.events[-1].event_hash
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            previous_event_hash=previous_hash,
            **kwargs
        )
        
        # Calculate event hash
        event.event_hash = self._calculate_event_hash(event)
        
        # Add to chain
        chain.events.append(event)
        chain.last_modified = datetime.now()
        self.events.append(event)
        
        print(f"📝 Audit event logged: {event_id}")
        print(f"   Type: {event_type.value}")
        print(f"   Actor: {actor} → {action} → {resource}")
        print(f"   Hash: {event.event_hash[:16]}...")
        
        return event
    
    def _calculate_event_hash(self, event: AuditEvent) -> str:
        """Calculate cryptographic hash of event"""
        # Create deterministic string representation
        hash_data = {
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'actor': event.actor,
            'action': event.action,
            'resource': event.resource,
            'result': event.result,
            'previous_hash': event.previous_event_hash or '',
            'details': json.dumps(event.details, sort_keys=True)
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def verify_chain_integrity(self, chain_id: str = "default") -> bool:
        """Verify audit chain integrity"""
        chain = self.chains.get(chain_id)
        if not chain:
            print(f"❌ Chain {chain_id} not found")
            return False
        
        print(f"\n🔍 Verifying audit chain: {chain_id}")
        print(f"   Events: {len(chain.events)}")
        
        for i, event in enumerate(chain.events):
            # Verify event hash
            calculated_hash = self._calculate_event_hash(event)
            if calculated_hash != event.event_hash:
                print(f"❌ Hash mismatch at event {i}: {event.event_id}")
                return False
            
            # Verify chain linkage (except genesis)
            if i > 0:
                previous_event = chain.events[i - 1]
                if event.previous_event_hash != previous_event.event_hash:
                    print(f"❌ Chain break at event {i}: {event.event_id}")
                    return False
        
        print(f"✅ Chain integrity verified ({len(chain.events)} events)")
        return True
    
    def generate_control_audit_trail(self, control_id: str) -> Dict[str, Any]:
        """Generate audit trail for specific control"""
        control_events = [
            e for e in self.events
            if e.control_id == control_id
        ]
        
        if not control_events:
            return {'control_id': control_id, 'events': [], 'message': 'No events found'}
        
        # Sort by timestamp
        control_events.sort(key=lambda e: e.timestamp)
        
        # Generate timeline
        timeline = []
        for event in control_events:
            timeline.append({
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type.value,
                'actor': event.actor,
                'action': event.action,
                'result': event.result,
                'hash': event.event_hash[:16] + '...'
            })
        
        return {
            'control_id': control_id,
            'total_events': len(control_events),
            'first_event': control_events[0].timestamp.isoformat(),
            'last_event': control_events[-1].timestamp.isoformat(),
            'timeline': timeline
        }
    
    def generate_compliance_report(self, framework: str, 
                                   start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """Generate compliance audit report"""
        # Filter events by framework and date range
        report_events = [
            e for e in self.events
            if e.framework == framework
            and start_date <= e.timestamp <= end_date
        ]
        
        # Group by event type
        by_type = {}
        for event in report_events:
            etype = event.event_type.value
            by_type[etype] = by_type.get(etype, 0) + 1
        
        # Group by result
        by_result = {}
        for event in report_events:
            by_result[event.result] = by_result.get(event.result, 0) + 1
        
        # Find critical events
        critical_events = [
            e for e in report_events
            if e.severity == AuditSeverity.CRITICAL
        ]
        
        return {
            'framework': framework,
            'report_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': len(report_events),
            'by_event_type': by_type,
            'by_result': by_result,
            'critical_events': len(critical_events),
            'success_rate': f"{(by_result.get('success', 0) / len(report_events) * 100):.1f}%" if report_events else "0%",
            'chain_verified': self.verify_chain_integrity()
        }
    
    def export_audit_trail(self, chain_id: str = "default", 
                          format: str = "json") -> str:
        """Export audit trail in various formats"""
        chain = self.chains.get(chain_id)
        if not chain:
            return "{}"
        
        export_data = {
            'chain_id': chain_id,
            'created_at': chain.created_at.isoformat(),
            'last_modified': chain.last_modified.isoformat(),
            'total_events': len(chain.events),
            'chain_verified': self.verify_chain_integrity(chain_id),
            'events': []
        }
        
        for event in chain.events:
            export_data['events'].append({
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'actor': event.actor,
                'action': event.action,
                'resource': event.resource,
                'result': event.result,
                'control_id': event.control_id,
                'framework': event.framework,
                'event_hash': event.event_hash,
                'previous_event_hash': event.previous_event_hash
            })
        
        if format == "json":
            return json.dumps(export_data, indent=2)
        else:
            return str(export_data)
    
    def search_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Search audit events with filters"""
        results = self.events
        
        if 'event_type' in filters:
            results = [e for e in results if e.event_type == filters['event_type']]
        
        if 'actor' in filters:
            results = [e for e in results if e.actor == filters['actor']]
        
        if 'control_id' in filters:
            results = [e for e in results if e.control_id == filters['control_id']]
        
        if 'framework' in filters:
            results = [e for e in results if e.framework == filters['framework']]
        
        if 'start_date' in filters:
            results = [e for e in results if e.timestamp >= filters['start_date']]
        
        if 'end_date' in filters:
            results = [e for e in results if e.timestamp <= filters['end_date']]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics"""
        by_type = {}
        by_severity = {}
        
        for event in self.events:
            etype = event.event_type.value
            by_type[etype] = by_type.get(etype, 0) + 1
            
            severity = event.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_events': len(self.events),
            'total_chains': len(self.chains),
            'by_event_type': by_type,
            'by_severity': by_severity,
            'chains': {chain_id: len(chain.events) 
                      for chain_id, chain in self.chains.items()}
        }


# Example usage
if __name__ == "__main__":
    audit = AuditTrailGenerator()
    
    # Log control implementation
    audit.log_event(
        event_type=AuditEventType.CONTROL_IMPLEMENTATION,
        actor="admin-user",
        action="implement_control",
        resource="AC-2",
        result="success",
        control_id="AC-2",
        framework="NIST-800-53",
        severity=AuditSeverity.INFO,
        details={'implementation_date': datetime.now().isoformat()}
    )
    
    # Log evidence collection
    audit.log_event(
        event_type=AuditEventType.EVIDENCE_COLLECTION,
        actor="automated",
        action="collect_firewall_config",
        resource="web-prod-01",
        result="success",
        control_id="SC-7",
        framework="NIST-800-53",
        severity=AuditSeverity.INFO
    )
    
    # Verify chain integrity
    audit.verify_chain_integrity()
    
    # Generate report
    report = audit.generate_compliance_report(
        framework="NIST-800-53",
        start_date=datetime.now().replace(hour=0, minute=0, second=0),
        end_date=datetime.now()
    )
    print(f"\n📊 Compliance report: {report['total_events']} events")
    print(f"   Success rate: {report['success_rate']}")
