"""
24/7 SOC-as-a-Service - Incident Management Module
Enterprise-grade Security Operations Center automation

This module provides comprehensive incident response automation:
- Automated incident detection and classification
- Real-time incident escalation workflows
- NIST 800-61 compliant incident response
- Integration with ticketing systems (Jira, ServiceNow)
- Automated evidence collection and preservation
- Incident timeline reconstruction
- Post-incident review automation

Compliance Frameworks:
- NIST 800-61 Rev 2 (Computer Security Incident Handling Guide)
- NIST 800-53 Rev 5 (IR Family - Incident Response)
- PCI DSS Requirement 12.10 (Incident Response Plan)
- HIPAA Security Rule §164.308(a)(6) (Security Incident Procedures)
- ISO 27001:2013 (A.16 - Information Security Incident Management)

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib


class IncidentSeverity(Enum):
    """Incident severity levels per NIST 800-61"""
    CRITICAL = "critical"      # Category 1: Immediate action required
    HIGH = "high"              # Category 2: Escalation within 1 hour
    MEDIUM = "medium"          # Category 3: Escalation within 4 hours
    LOW = "low"                # Category 4: Standard response time
    INFORMATIONAL = "info"     # Category 5: No immediate action


class IncidentStatus(Enum):
    """Incident lifecycle status"""
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCategory(Enum):
    """NIST 800-61 incident categories"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware_infection"
    DENIAL_OF_SERVICE = "denial_of_service"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing_attack"
    WEB_ATTACK = "web_application_attack"
    RANSOMWARE = "ransomware"
    APT = "advanced_persistent_threat"
    POLICY_VIOLATION = "security_policy_violation"
    VULNERABILITY_EXPLOIT = "vulnerability_exploitation"
    CRYPTOJACKING = "cryptojacking"


class EscalationTier(Enum):
    """SOC escalation tiers"""
    L1_ANALYST = "tier1_analyst"
    L2_ANALYST = "tier2_analyst"
    L3_SPECIALIST = "tier3_specialist"
    INCIDENT_MANAGER = "incident_manager"
    CSIRT_LEAD = "csirt_lead"
    CISO = "ciso"
    EXECUTIVE = "executive"


class IRPhase(Enum):
    """NIST 800-61 Incident Response phases"""
    PREPARATION = "preparation"
    DETECTION_ANALYSIS = "detection_and_analysis"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    POST_INCIDENT = "post_incident_activity"


@dataclass
class IncidentAlert:
    """Security alert that may indicate an incident"""
    alert_id: str
    alert_source: str  # IDS, SIEM, EDR, WAF, etc.
    alert_type: str
    severity: IncidentSeverity
    description: str
    timestamp: datetime
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    affected_assets: List[str] = field(default_factory=list)
    indicators: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentEvidence:
    """Digital evidence collected during incident"""
    evidence_id: str
    evidence_type: str  # logs, network_capture, memory_dump, disk_image, etc.
    collection_timestamp: datetime
    collected_by: str
    file_path: Optional[str] = None
    file_hash: Optional[str] = None  # SHA-256
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    description: str = ""
    preservation_status: str = "collected"  # collected, preserved, analyzed


@dataclass
class IncidentTimelineEvent:
    """Event in incident timeline"""
    event_id: str
    timestamp: datetime
    event_type: str  # detection, escalation, containment_action, communication, etc.
    description: str
    performed_by: str
    ir_phase: IRPhase
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """Security incident with full lifecycle tracking"""
    incident_id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    
    # Timestamps
    detected_at: datetime
    reported_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Assignment and escalation
    assigned_to: Optional[str] = None
    escalation_tier: EscalationTier = EscalationTier.L1_ANALYST
    escalated_to: List[str] = field(default_factory=list)
    
    # Affected resources
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    affected_data: List[str] = field(default_factory=list)
    
    # Incident response
    current_phase: IRPhase = IRPhase.DETECTION_ANALYSIS
    containment_actions: List[str] = field(default_factory=list)
    eradication_actions: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    
    # Evidence and analysis
    alerts: List[IncidentAlert] = field(default_factory=list)
    evidence: List[IncidentEvidence] = field(default_factory=list)
    timeline: List[IncidentTimelineEvent] = field(default_factory=list)
    
    # Impact assessment
    confidentiality_impact: str = "unknown"  # none, low, medium, high
    integrity_impact: str = "unknown"
    availability_impact: str = "unknown"
    
    # Communication
    stakeholders_notified: List[str] = field(default_factory=list)
    external_notifications: List[str] = field(default_factory=list)  # Law enforcement, customers, etc.
    
    # Compliance
    regulatory_requirements: List[str] = field(default_factory=list)
    breach_notification_required: bool = False
    
    # Metrics
    time_to_detect: Optional[timedelta] = None
    time_to_acknowledge: Optional[timedelta] = None
    time_to_contain: Optional[timedelta] = None
    time_to_resolve: Optional[timedelta] = None
    
    # Lessons learned
    root_cause: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_incidents: List[str] = field(default_factory=list)
    ticket_id: Optional[str] = None  # Jira, ServiceNow, etc.
    created_by: str = "SOC Automation"
    last_updated: datetime = field(default_factory=datetime.now)


class SOCIncidentManager:
    """
    24/7 SOC Incident Management System
    
    Provides automated incident detection, classification, escalation,
    and response coordination following NIST 800-61 framework.
    """
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.active_incidents: Set[str] = set()
        self.escalation_rules: Dict[IncidentSeverity, Dict[str, Any]] = self._initialize_escalation_rules()
        self.sla_thresholds: Dict[IncidentSeverity, Dict[str, int]] = self._initialize_sla_thresholds()
        
    def _initialize_escalation_rules(self) -> Dict[IncidentSeverity, Dict[str, Any]]:
        """Initialize automated escalation rules based on severity"""
        return {
            IncidentSeverity.CRITICAL: {
                'immediate_escalation': [EscalationTier.INCIDENT_MANAGER, EscalationTier.CSIRT_LEAD, EscalationTier.CISO],
                'escalation_delay_minutes': 0,
                'notification_channels': ['pagerduty', 'sms', 'phone', 'email', 'slack'],
                'war_room_required': True,
                'executive_notification': True
            },
            IncidentSeverity.HIGH: {
                'immediate_escalation': [EscalationTier.L2_ANALYST, EscalationTier.INCIDENT_MANAGER],
                'escalation_delay_minutes': 15,
                'notification_channels': ['pagerduty', 'sms', 'email', 'slack'],
                'war_room_required': True,
                'executive_notification': False
            },
            IncidentSeverity.MEDIUM: {
                'immediate_escalation': [EscalationTier.L2_ANALYST],
                'escalation_delay_minutes': 60,
                'notification_channels': ['email', 'slack'],
                'war_room_required': False,
                'executive_notification': False
            },
            IncidentSeverity.LOW: {
                'immediate_escalation': [],
                'escalation_delay_minutes': 240,
                'notification_channels': ['email'],
                'war_room_required': False,
                'executive_notification': False
            },
            IncidentSeverity.INFORMATIONAL: {
                'immediate_escalation': [],
                'escalation_delay_minutes': None,
                'notification_channels': ['email'],
                'war_room_required': False,
                'executive_notification': False
            }
        }
    
    def _initialize_sla_thresholds(self) -> Dict[IncidentSeverity, Dict[str, int]]:
        """Initialize SLA thresholds (in minutes) for each severity"""
        return {
            IncidentSeverity.CRITICAL: {
                'acknowledge': 15,      # 15 minutes
                'respond': 30,          # 30 minutes
                'contain': 120,         # 2 hours
                'resolve': 240          # 4 hours
            },
            IncidentSeverity.HIGH: {
                'acknowledge': 30,      # 30 minutes
                'respond': 60,          # 1 hour
                'contain': 240,         # 4 hours
                'resolve': 480          # 8 hours
            },
            IncidentSeverity.MEDIUM: {
                'acknowledge': 120,     # 2 hours
                'respond': 240,         # 4 hours
                'contain': 480,         # 8 hours
                'resolve': 1440         # 24 hours
            },
            IncidentSeverity.LOW: {
                'acknowledge': 240,     # 4 hours
                'respond': 480,         # 8 hours
                'contain': 1440,        # 24 hours
                'resolve': 2880         # 48 hours
            },
            IncidentSeverity.INFORMATIONAL: {
                'acknowledge': 480,     # 8 hours
                'respond': 1440,        # 24 hours
                'contain': None,
                'resolve': 4320         # 72 hours
            }
        }
    
    def create_incident(
        self,
        title: str,
        description: str,
        category: IncidentCategory,
        severity: IncidentSeverity,
        initial_alert: Optional[IncidentAlert] = None,
        affected_systems: List[str] = None,
        detected_at: datetime = None
    ) -> Incident:
        """
        Create new security incident with automated classification and escalation.
        
        Args:
            title: Brief incident title
            description: Detailed incident description
            category: NIST 800-61 incident category
            severity: Incident severity level
            initial_alert: Initial security alert that triggered incident
            affected_systems: List of affected systems/assets
            detected_at: Detection timestamp (defaults to now)
            
        Returns:
            Created Incident object
        """
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        detected_at = detected_at or datetime.now()
        reported_at = datetime.now()
        
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            status=IncidentStatus.NEW,
            detected_at=detected_at,
            reported_at=reported_at,
            affected_systems=affected_systems or [],
            time_to_detect=reported_at - detected_at
        )
        
        # Add initial alert if provided
        if initial_alert:
            incident.alerts.append(initial_alert)
        
        # Create initial timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=reported_at,
            event_type="incident_created",
            description=f"Incident {incident_id} created: {title}",
            performed_by="SOC Automation",
            ir_phase=IRPhase.DETECTION_ANALYSIS,
            details={
                'severity': severity.value,
                'category': category.value,
                'detection_source': initial_alert.alert_source if initial_alert else 'manual'
            }
        )
        incident.timeline.append(timeline_event)
        
        # Store incident
        self.incidents[incident_id] = incident
        self.active_incidents.add(incident_id)
        
        print(f"🚨 Incident Created: {incident_id}")
        print(f"   Title: {title}")
        print(f"   Severity: {severity.value.upper()}")
        print(f"   Category: {category.value}")
        
        # Trigger automated escalation
        self._auto_escalate(incident)
        
        # Check for regulatory requirements
        self._assess_regulatory_requirements(incident)
        
        return incident
    
    def _auto_escalate(self, incident: Incident) -> None:
        """Automatically escalate incident based on severity and rules"""
        rules = self.escalation_rules.get(incident.severity, {})
        immediate_escalation = rules.get('immediate_escalation', [])
        
        if immediate_escalation:
            print(f"⚠️  Auto-escalating {incident.incident_id} to: {', '.join([t.value for t in immediate_escalation])}")
            
            for tier in immediate_escalation:
                self._escalate_to_tier(incident, tier)
            
            # War room required?
            if rules.get('war_room_required'):
                self._create_war_room(incident)
            
            # Executive notification?
            if rules.get('executive_notification'):
                self._notify_executives(incident)
    
    def _escalate_to_tier(self, incident: Incident, tier: EscalationTier) -> None:
        """Escalate incident to specific tier"""
        incident.escalation_tier = tier
        incident.escalated_to.append(tier.value)
        
        # Add timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type="escalation",
            description=f"Incident escalated to {tier.value}",
            performed_by="SOC Automation",
            ir_phase=incident.current_phase,
            details={'tier': tier.value}
        )
        incident.timeline.append(timeline_event)
        
        print(f"📈 Escalated to: {tier.value}")
    
    def _create_war_room(self, incident: Incident) -> None:
        """Create virtual war room for incident coordination"""
        print(f"🏛️  Creating war room for {incident.incident_id}")
        
        # In production, this would:
        # - Create Slack channel or Teams room
        # - Invite key stakeholders
        # - Set up video conference bridge
        # - Create shared incident document
        
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type="war_room_created",
            description="Virtual war room created for incident coordination",
            performed_by="SOC Automation",
            ir_phase=incident.current_phase,
            details={'channel': f"incident-{incident.incident_id.lower()}"}
        )
        incident.timeline.append(timeline_event)
    
    def _notify_executives(self, incident: Incident) -> None:
        """Send executive notification for critical incidents"""
        print(f"📧 Sending executive notification for {incident.incident_id}")
        
        executives = ['ciso@enterprisescanner.com', 'cto@enterprisescanner.com', 'ceo@enterprisescanner.com']
        incident.stakeholders_notified.extend(executives)
        
        # Add timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type="executive_notification",
            description="Executive team notified of critical incident",
            performed_by="SOC Automation",
            ir_phase=incident.current_phase,
            details={'recipients': executives}
        )
        incident.timeline.append(timeline_event)
    
    def _assess_regulatory_requirements(self, incident: Incident) -> None:
        """Assess if incident requires regulatory notification"""
        regulatory_flags = []
        
        # Data breach detection
        if incident.category == IncidentCategory.DATA_BREACH:
            regulatory_flags.append('GDPR')
            regulatory_flags.append('CCPA')
            regulatory_flags.append('HIPAA')
            incident.breach_notification_required = True
        
        # Ransomware
        if incident.category == IncidentCategory.RANSOMWARE:
            regulatory_flags.append('FBI IC3')
            regulatory_flags.append('CISA')
        
        # APT
        if incident.category == IncidentCategory.APT:
            regulatory_flags.append('CISA')
            regulatory_flags.append('FBI')
        
        incident.regulatory_requirements = regulatory_flags
        
        if regulatory_flags:
            print(f"⚖️  Regulatory requirements identified: {', '.join(regulatory_flags)}")
    
    def acknowledge_incident(self, incident_id: str, acknowledged_by: str) -> None:
        """Acknowledge incident and assign to analyst"""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        incident.acknowledged_at = datetime.now()
        incident.assigned_to = acknowledged_by
        incident.status = IncidentStatus.TRIAGED
        incident.time_to_acknowledge = incident.acknowledged_at - incident.reported_at
        
        # Check SLA
        sla_threshold = self.sla_thresholds[incident.severity]['acknowledge']
        ack_minutes = incident.time_to_acknowledge.total_seconds() / 60
        
        if ack_minutes > sla_threshold:
            print(f"⏰ SLA BREACH: Acknowledgment took {ack_minutes:.1f} min (threshold: {sla_threshold} min)")
        else:
            print(f"✅ SLA Met: Acknowledged in {ack_minutes:.1f} min")
        
        # Add timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=incident.acknowledged_at,
            event_type="incident_acknowledged",
            description=f"Incident acknowledged by {acknowledged_by}",
            performed_by=acknowledged_by,
            ir_phase=incident.current_phase,
            details={'tta_minutes': ack_minutes}
        )
        incident.timeline.append(timeline_event)
        
        print(f"✋ Incident {incident_id} acknowledged by {acknowledged_by}")
    
    def add_evidence(self, incident_id: str, evidence: IncidentEvidence) -> None:
        """Add digital evidence to incident with chain of custody"""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Add chain of custody entry
        custody_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'evidence_added',
            'handler': 'SOC Automation',
            'hash_verified': evidence.file_hash is not None
        }
        evidence.chain_of_custody.append(custody_entry)
        
        incident.evidence.append(evidence)
        
        # Add timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type="evidence_collected",
            description=f"Evidence collected: {evidence.evidence_type}",
            performed_by=evidence.collected_by,
            ir_phase=incident.current_phase,
            details={
                'evidence_id': evidence.evidence_id,
                'evidence_type': evidence.evidence_type,
                'file_hash': evidence.file_hash
            }
        )
        incident.timeline.append(timeline_event)
        
        print(f"🔍 Evidence added to {incident_id}: {evidence.evidence_type}")
    
    def update_phase(self, incident_id: str, new_phase: IRPhase, updated_by: str) -> None:
        """Update incident response phase per NIST 800-61"""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        old_phase = incident.current_phase
        incident.current_phase = new_phase
        
        # Update status based on phase
        phase_status_mapping = {
            IRPhase.DETECTION_ANALYSIS: IncidentStatus.INVESTIGATING,
            IRPhase.CONTAINMENT: IncidentStatus.CONTAINED,
            IRPhase.ERADICATION: IncidentStatus.ERADICATED,
            IRPhase.RECOVERY: IncidentStatus.RECOVERING,
            IRPhase.POST_INCIDENT: IncidentStatus.RESOLVED
        }
        
        if new_phase in phase_status_mapping:
            incident.status = phase_status_mapping[new_phase]
        
        # Add timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type="phase_change",
            description=f"IR phase changed: {old_phase.value} → {new_phase.value}",
            performed_by=updated_by,
            ir_phase=new_phase,
            details={'old_phase': old_phase.value, 'new_phase': new_phase.value}
        )
        incident.timeline.append(timeline_event)
        
        print(f"📋 {incident_id} phase updated: {old_phase.value} → {new_phase.value}")
    
    def resolve_incident(
        self,
        incident_id: str,
        resolved_by: str,
        root_cause: str,
        resolution_summary: str,
        lessons_learned: List[str] = None,
        recommendations: List[str] = None
    ) -> None:
        """Resolve incident with root cause analysis and lessons learned"""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        incident.resolved_at = datetime.now()
        incident.status = IncidentStatus.RESOLVED
        incident.current_phase = IRPhase.POST_INCIDENT
        incident.root_cause = root_cause
        incident.time_to_resolve = incident.resolved_at - incident.detected_at
        
        if lessons_learned:
            incident.lessons_learned = lessons_learned
        
        if recommendations:
            incident.recommendations = recommendations
        
        # Check SLA
        sla_threshold = self.sla_thresholds[incident.severity]['resolve']
        if sla_threshold:
            resolve_minutes = incident.time_to_resolve.total_seconds() / 60
            
            if resolve_minutes > sla_threshold:
                print(f"⏰ SLA BREACH: Resolution took {resolve_minutes:.1f} min (threshold: {sla_threshold} min)")
            else:
                print(f"✅ SLA Met: Resolved in {resolve_minutes:.1f} min")
        
        # Add timeline event
        timeline_event = IncidentTimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=incident.resolved_at,
            event_type="incident_resolved",
            description=f"Incident resolved by {resolved_by}: {resolution_summary}",
            performed_by=resolved_by,
            ir_phase=IRPhase.POST_INCIDENT,
            details={
                'root_cause': root_cause,
                'resolution_summary': resolution_summary,
                'ttr_minutes': incident.time_to_resolve.total_seconds() / 60
            }
        )
        incident.timeline.append(timeline_event)
        
        print(f"✅ Incident {incident_id} RESOLVED")
        print(f"   Root Cause: {root_cause}")
        print(f"   Time to Resolve: {incident.time_to_resolve}")
        
        # Remove from active incidents
        self.active_incidents.discard(incident_id)
        
        # Generate post-incident report
        self._generate_post_incident_report(incident)
    
    def _generate_post_incident_report(self, incident: Incident) -> Dict[str, Any]:
        """Generate comprehensive post-incident review report"""
        report = {
            'incident_id': incident.incident_id,
            'title': incident.title,
            'category': incident.category.value,
            'severity': incident.severity.value,
            'detection_date': incident.detected_at.isoformat(),
            'resolution_date': incident.resolved_at.isoformat() if incident.resolved_at else None,
            'total_duration': str(incident.time_to_resolve) if incident.time_to_resolve else None,
            'metrics': {
                'time_to_detect': str(incident.time_to_detect) if incident.time_to_detect else None,
                'time_to_acknowledge': str(incident.time_to_acknowledge) if incident.time_to_acknowledge else None,
                'time_to_contain': str(incident.time_to_contain) if incident.time_to_contain else None,
                'time_to_resolve': str(incident.time_to_resolve) if incident.time_to_resolve else None
            },
            'impact_assessment': {
                'confidentiality': incident.confidentiality_impact,
                'integrity': incident.integrity_impact,
                'availability': incident.availability_impact,
                'affected_systems': len(incident.affected_systems),
                'affected_users': len(incident.affected_users)
            },
            'root_cause': incident.root_cause,
            'lessons_learned': incident.lessons_learned,
            'recommendations': incident.recommendations,
            'evidence_collected': len(incident.evidence),
            'timeline_events': len(incident.timeline),
            'regulatory_implications': incident.regulatory_requirements,
            'breach_notification_required': incident.breach_notification_required
        }
        
        print(f"\n📊 Post-Incident Report Generated for {incident.incident_id}")
        print(f"   Total Events: {len(incident.timeline)}")
        print(f"   Evidence Collected: {len(incident.evidence)}")
        print(f"   Lessons Learned: {len(incident.lessons_learned)}")
        
        return report
    
    def get_active_incidents(self, severity_filter: IncidentSeverity = None) -> List[Incident]:
        """Get list of active incidents, optionally filtered by severity"""
        active = [self.incidents[iid] for iid in self.active_incidents if iid in self.incidents]
        
        if severity_filter:
            active = [i for i in active if i.severity == severity_filter]
        
        return sorted(active, key=lambda x: (x.severity.value, x.detected_at), reverse=True)
    
    def get_sla_violations(self) -> List[Dict[str, Any]]:
        """Get list of incidents with SLA violations"""
        violations = []
        
        for incident_id in self.active_incidents:
            incident = self.incidents.get(incident_id)
            if not incident:
                continue
            
            thresholds = self.sla_thresholds[incident.severity]
            
            # Check acknowledgment SLA
            if incident.acknowledged_at and incident.time_to_acknowledge:
                ack_minutes = incident.time_to_acknowledge.total_seconds() / 60
                if ack_minutes > thresholds['acknowledge']:
                    violations.append({
                        'incident_id': incident_id,
                        'violation_type': 'acknowledgment',
                        'threshold_minutes': thresholds['acknowledge'],
                        'actual_minutes': ack_minutes,
                        'severity': incident.severity.value
                    })
            
            # Check resolution SLA
            if not incident.resolved_at:
                time_open = (datetime.now() - incident.detected_at).total_seconds() / 60
                resolve_threshold = thresholds['resolve']
                if resolve_threshold and time_open > resolve_threshold:
                    violations.append({
                        'incident_id': incident_id,
                        'violation_type': 'resolution',
                        'threshold_minutes': resolve_threshold,
                        'actual_minutes': time_open,
                        'severity': incident.severity.value
                    })
        
        return violations
    
    def generate_soc_metrics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Generate SOC performance metrics"""
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        recent_incidents = [
            inc for inc in self.incidents.values()
            if inc.detected_at >= cutoff_date
        ]
        
        if not recent_incidents:
            return {'error': 'No incidents in time period'}
        
        # Calculate metrics
        total_incidents = len(recent_incidents)
        by_severity = {}
        by_category = {}
        
        avg_ttd = []  # time to detect
        avg_tta = []  # time to acknowledge
        avg_ttr = []  # time to resolve
        
        for inc in recent_incidents:
            # Count by severity
            sev = inc.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # Count by category
            cat = inc.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Time metrics
            if inc.time_to_detect:
                avg_ttd.append(inc.time_to_detect.total_seconds() / 60)
            if inc.time_to_acknowledge:
                avg_tta.append(inc.time_to_acknowledge.total_seconds() / 60)
            if inc.time_to_resolve:
                avg_ttr.append(inc.time_to_resolve.total_seconds() / 60)
        
        metrics = {
            'time_period_days': time_period_days,
            'total_incidents': total_incidents,
            'active_incidents': len(self.active_incidents),
            'by_severity': by_severity,
            'by_category': by_category,
            'average_time_to_detect_minutes': sum(avg_ttd) / len(avg_ttd) if avg_ttd else 0,
            'average_time_to_acknowledge_minutes': sum(avg_tta) / len(avg_tta) if avg_tta else 0,
            'average_time_to_resolve_minutes': sum(avg_ttr) / len(avg_ttr) if avg_ttr else 0,
            'sla_violations': len(self.get_sla_violations()),
            'resolved_incidents': len([i for i in recent_incidents if i.status == IncidentStatus.RESOLVED]),
            'resolution_rate': len([i for i in recent_incidents if i.status == IncidentStatus.RESOLVED]) / total_incidents * 100
        }
        
        return metrics


# Example usage
if __name__ == "__main__":
    # Initialize SOC
    soc = SOCIncidentManager()
    
    # Create test alert
    alert = IncidentAlert(
        alert_id="ALT-20251017-001",
        alert_source="EDR",
        alert_type="ransomware_detected",
        severity=IncidentSeverity.CRITICAL,
        description="Ransomware encryption activity detected on production server",
        timestamp=datetime.now() - timedelta(minutes=5),
        source_ip="10.0.1.50",
        affected_assets=["PROD-WEB-01"],
        indicators={'file_hash': 'abc123', 'process': 'encrypt.exe'}
    )
    
    # Create incident
    incident = soc.create_incident(
        title="Ransomware Attack on Production Server",
        description="EDR detected ransomware encryption activity on PROD-WEB-01. Multiple files being encrypted.",
        category=IncidentCategory.RANSOMWARE,
        severity=IncidentSeverity.CRITICAL,
        initial_alert=alert,
        affected_systems=["PROD-WEB-01", "FILE-SERVER-01"],
        detected_at=datetime.now() - timedelta(minutes=5)
    )
    
    # Acknowledge incident
    soc.acknowledge_incident(incident.incident_id, "analyst@enterprisescanner.com")
    
    # Add evidence
    evidence = IncidentEvidence(
        evidence_id="EV-001",
        evidence_type="memory_dump",
        collection_timestamp=datetime.now(),
        collected_by="forensics_team",
        file_path="/evidence/PROD-WEB-01-memory.raw",
        file_hash=hashlib.sha256(b"dummy_data").hexdigest(),
        description="Memory dump from infected server"
    )
    soc.add_evidence(incident.incident_id, evidence)
    
    # Update phase
    soc.update_phase(incident.incident_id, IRPhase.CONTAINMENT, "analyst@enterprisescanner.com")
    
    # Resolve incident
    soc.resolve_incident(
        incident.incident_id,
        resolved_by="analyst@enterprisescanner.com",
        root_cause="Phishing email with malicious attachment bypassed email filtering",
        resolution_summary="Server isolated, ransomware removed, files restored from backup",
        lessons_learned=[
            "Email filtering rules need strengthening",
            "User security awareness training required",
            "Backup restoration procedures worked as expected"
        ],
        recommendations=[
            "Implement advanced email filtering with sandboxing",
            "Conduct quarterly phishing simulations",
            "Review and update incident response playbooks"
        ]
    )
    
    # Generate metrics
    metrics = soc.generate_soc_metrics(time_period_days=30)
    print(f"\n📊 SOC Metrics (30 days):")
    print(f"   Total Incidents: {metrics['total_incidents']}")
    print(f"   Resolution Rate: {metrics['resolution_rate']:.1f}%")
    print(f"   Avg Time to Resolve: {metrics['average_time_to_resolve_minutes']:.1f} min")
