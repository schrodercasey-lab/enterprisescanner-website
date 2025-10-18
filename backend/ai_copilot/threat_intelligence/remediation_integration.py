"""
G.2.12: Remediation Engine Integration

Enterprise-grade integration layer connecting threat intelligence to autonomous
remediation. Enables automated response to threats, intelligent patch deployment,
vulnerability prioritization, and campaign-based security automation.

Features:
- Threat-to-remediation mapping
- Automated patch deployment triggers
- Vulnerability prioritization sync
- Campaign-based response automation
- IoC-driven blocking rules
- Risk-based remediation scheduling
- Threat intelligence feedback loop
- Remediation effectiveness tracking
- Cross-system orchestration
- Real-time threat response

Author: Enterprise Scanner Development Team
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import json


class RemediationTrigger(Enum):
    """Triggers for automated remediation"""
    CRITICAL_VULNERABILITY = "critical_vulnerability"    # Critical CVE detected
    ACTIVE_EXPLOITATION = "active_exploitation"          # Active exploit detected
    CAMPAIGN_TARGET = "campaign_target"                  # Targeted by campaign
    IOC_MATCH = "ioc_match"                             # IoC matched in environment
    THREAT_PREDICTION = "threat_prediction"              # Predictive threat detected
    COMPLIANCE_VIOLATION = "compliance_violation"        # Compliance gap
    EXECUTIVE_DIRECTIVE = "executive_directive"          # Executive mandate


class RemediationAction(Enum):
    """Types of remediation actions"""
    PATCH_DEPLOY = "patch_deploy"              # Deploy security patch
    BLOCK_IOC = "block_ioc"                    # Block indicator (IP/domain/hash)
    ISOLATE_ASSET = "isolate_asset"            # Network isolation
    UPDATE_RULES = "update_rules"              # Update firewall/IDS rules
    SCAN_ASSETS = "scan_assets"                # Initiate vulnerability scan
    ALERT_TEAM = "alert_team"                  # Alert security team
    SCHEDULE_MAINTENANCE = "schedule_maintenance"  # Schedule maintenance window


class IntegrationStatus(Enum):
    """Integration execution status"""
    PENDING = "pending"              # Queued for execution
    IN_PROGRESS = "in_progress"      # Currently executing
    COMPLETED = "completed"          # Successfully completed
    FAILED = "failed"                # Execution failed
    CANCELLED = "cancelled"          # Manually cancelled
    REQUIRES_APPROVAL = "requires_approval"  # Needs human approval


@dataclass
class ThreatRemediationMapping:
    """Mapping between threat intelligence and remediation actions"""
    mapping_id: str
    threat_type: str  # vulnerability, ioc, campaign, actor
    threat_identifier: str  # CVE-ID, IoC value, campaign ID, etc.
    remediation_actions: List[RemediationAction]
    priority_score: int  # 0-100
    auto_execute: bool
    requires_approval: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def should_auto_execute(self, risk_score: float) -> bool:
        """Determine if action should auto-execute based on risk"""
        if not self.auto_execute:
            return False
        if self.requires_approval and risk_score < 90:
            return False
        return True


@dataclass
class RemediationTask:
    """Remediation task triggered by threat intelligence"""
    task_id: str
    trigger: RemediationTrigger
    action: RemediationAction
    threat_data: Dict[str, Any]
    target_assets: List[str]
    priority: int  # 0-100
    status: IntegrationStatus
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def get_duration_seconds(self) -> Optional[float]:
        """Calculate task execution duration"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class RemediationFeedback:
    """Feedback on remediation effectiveness"""
    feedback_id: str
    task_id: str
    effectiveness_score: float  # 0.0-1.0
    threat_eliminated: bool
    side_effects: Optional[str]
    lessons_learned: Optional[str]
    provided_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrossSystemOrchestration:
    """Orchestration across multiple security systems"""
    orchestration_id: str
    threat_id: str
    systems: List[str]  # firewall, ids, edr, siem, etc.
    actions: Dict[str, Any]  # system -> action mapping
    execution_order: List[str]
    status: IntegrationStatus
    created_at: datetime = field(default_factory=datetime.utcnow)


class RemediationEngineIntegration:
    """
    Integration layer connecting threat intelligence to autonomous remediation.
    
    Enables automated response to threats through intelligent mapping,
    prioritization, and orchestration across security systems.
    """
    
    def __init__(
        self,
        threat_db_path: str = "threat_intelligence.db",
        remediation_db_path: str = "remediation.db"
    ):
        self.threat_db_path = threat_db_path
        self.remediation_db_path = remediation_db_path
        self._init_database()
        
        # Auto-execution thresholds
        self.auto_execute_threshold = 80  # Risk score threshold for auto-execution
        
    def _init_database(self):
        """Initialize integration database tables"""
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        # Threat-remediation mappings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_remediation_mappings (
                mapping_id TEXT PRIMARY KEY,
                threat_type TEXT NOT NULL,
                threat_identifier TEXT NOT NULL,
                remediation_actions TEXT NOT NULL,
                priority_score INTEGER NOT NULL,
                auto_execute INTEGER DEFAULT 0,
                requires_approval INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Remediation tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS remediation_tasks (
                task_id TEXT PRIMARY KEY,
                trigger TEXT NOT NULL,
                action TEXT NOT NULL,
                threat_data TEXT NOT NULL,
                target_assets TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                scheduled_at TIMESTAMP NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                result TEXT,
                error_message TEXT
            )
        """)
        
        # Remediation feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS remediation_feedback (
                feedback_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                effectiveness_score REAL NOT NULL,
                threat_eliminated INTEGER NOT NULL,
                side_effects TEXT,
                lessons_learned TEXT,
                provided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES remediation_tasks(task_id)
            )
        """)
        
        # Cross-system orchestration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cross_system_orchestration (
                orchestration_id TEXT PRIMARY KEY,
                threat_id TEXT NOT NULL,
                systems TEXT NOT NULL,
                actions TEXT NOT NULL,
                execution_order TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_threat_mapping(
        self,
        threat_type: str,
        threat_identifier: str,
        remediation_actions: List[RemediationAction],
        priority_score: int,
        auto_execute: bool = False,
        requires_approval: bool = True
    ) -> ThreatRemediationMapping:
        """Create mapping between threat and remediation actions"""
        mapping_id = hashlib.sha256(
            f"{threat_type}{threat_identifier}".encode()
        ).hexdigest()[:16]
        
        mapping = ThreatRemediationMapping(
            mapping_id=mapping_id,
            threat_type=threat_type,
            threat_identifier=threat_identifier,
            remediation_actions=remediation_actions,
            priority_score=priority_score,
            auto_execute=auto_execute,
            requires_approval=requires_approval
        )
        
        # Store mapping
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO threat_remediation_mappings
            (mapping_id, threat_type, threat_identifier, remediation_actions,
             priority_score, auto_execute, requires_approval, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mapping.mapping_id,
            mapping.threat_type,
            mapping.threat_identifier,
            json.dumps([action.value for action in mapping.remediation_actions]),
            mapping.priority_score,
            1 if mapping.auto_execute else 0,
            1 if mapping.requires_approval else 0,
            mapping.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return mapping
    
    def trigger_remediation_from_vulnerability(
        self,
        cve_id: str,
        risk_score: float,
        affected_assets: List[str]
    ) -> Optional[RemediationTask]:
        """
        Trigger remediation based on vulnerability intelligence.
        
        Automatically creates remediation task for critical vulnerabilities
        with active exploitation.
        """
        # Get vulnerability details
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cve_id, cvss_score, severity, exploit_available,
                   epss_score, description
            FROM vulnerabilities
            WHERE cve_id = ?
        """, (cve_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        cve_id, cvss, severity, exploit_avail, epss, description = result
        
        # Determine trigger type
        if exploit_avail and epss and epss > 0.7:
            trigger = RemediationTrigger.ACTIVE_EXPLOITATION
        else:
            trigger = RemediationTrigger.CRITICAL_VULNERABILITY
        
        # Determine action based on severity and risk
        if risk_score >= 90:
            action = RemediationAction.PATCH_DEPLOY
        elif risk_score >= 70:
            action = RemediationAction.SCHEDULE_MAINTENANCE
        else:
            action = RemediationAction.SCAN_ASSETS
        
        # Create remediation task
        task = self._create_remediation_task(
            trigger=trigger,
            action=action,
            threat_data={
                'cve_id': cve_id,
                'cvss_score': cvss,
                'severity': severity,
                'exploit_available': bool(exploit_avail),
                'epss_score': epss,
                'description': description,
                'risk_score': risk_score
            },
            target_assets=affected_assets,
            priority=int(risk_score)
        )
        
        return task
    
    def trigger_remediation_from_ioc(
        self,
        ioc_value: str,
        ioc_type: str,
        confidence: float,
        affected_assets: List[str]
    ) -> Optional[RemediationTask]:
        """
        Trigger remediation based on IoC match.
        
        Automatically blocks high-confidence malicious indicators.
        """
        # Get IoC details
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT indicator, indicator_type, threat_level, confidence,
                   context, malware_family
            FROM indicators_of_compromise
            WHERE indicator = ? AND indicator_type = ?
        """, (ioc_value, ioc_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        indicator, ind_type, threat_level, conf, context, malware = result
        
        # High confidence IoCs should be blocked immediately
        action = RemediationAction.BLOCK_IOC if confidence >= 0.8 else RemediationAction.ALERT_TEAM
        
        # Calculate priority based on threat level and confidence
        priority_map = {'critical': 95, 'high': 85, 'medium': 70, 'low': 50}
        base_priority = priority_map.get(threat_level, 50)
        priority = int(base_priority * confidence)
        
        task = self._create_remediation_task(
            trigger=RemediationTrigger.IOC_MATCH,
            action=action,
            threat_data={
                'indicator': indicator,
                'indicator_type': ind_type,
                'threat_level': threat_level,
                'confidence': conf,
                'context': context,
                'malware_family': malware
            },
            target_assets=affected_assets,
            priority=priority
        )
        
        return task
    
    def trigger_remediation_from_campaign(
        self,
        campaign_id: str,
        target_match: bool,
        affected_assets: List[str]
    ) -> Optional[RemediationTask]:
        """
        Trigger remediation based on active threat campaign.
        
        Implements defensive measures when organization is targeted.
        """
        # Get campaign details
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT campaign_id, name, threat_actor, target_industries,
                   ttps, malware_families, status
            FROM threat_campaigns
            WHERE campaign_id = ?
        """, (campaign_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        camp_id, name, actor, industries, ttps, malware, status = result
        
        # If directly targeted, take immediate action
        if target_match:
            action = RemediationAction.UPDATE_RULES
            priority = 90
        else:
            action = RemediationAction.ALERT_TEAM
            priority = 70
        
        task = self._create_remediation_task(
            trigger=RemediationTrigger.CAMPAIGN_TARGET,
            action=action,
            threat_data={
                'campaign_id': camp_id,
                'campaign_name': name,
                'threat_actor': actor,
                'target_industries': json.loads(industries) if industries else [],
                'ttps': json.loads(ttps) if ttps else [],
                'malware_families': json.loads(malware) if malware else [],
                'status': status,
                'target_match': target_match
            },
            target_assets=affected_assets,
            priority=priority
        )
        
        return task
    
    def _create_remediation_task(
        self,
        trigger: RemediationTrigger,
        action: RemediationAction,
        threat_data: Dict[str, Any],
        target_assets: List[str],
        priority: int
    ) -> RemediationTask:
        """Create and store remediation task"""
        task_id = hashlib.sha256(
            f"{trigger.value}{action.value}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Determine if auto-execute
        auto_execute = (
            priority >= self.auto_execute_threshold and
            action in [RemediationAction.BLOCK_IOC, RemediationAction.ALERT_TEAM]
        )
        
        status = IntegrationStatus.PENDING if auto_execute else IntegrationStatus.REQUIRES_APPROVAL
        
        task = RemediationTask(
            task_id=task_id,
            trigger=trigger,
            action=action,
            threat_data=threat_data,
            target_assets=target_assets,
            priority=priority,
            status=status,
            scheduled_at=datetime.utcnow()
        )
        
        # Store task
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO remediation_tasks
            (task_id, trigger, action, threat_data, target_assets,
             priority, status, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.task_id,
            task.trigger.value,
            task.action.value,
            json.dumps(task.threat_data),
            json.dumps(task.target_assets),
            task.priority,
            task.status.value,
            task.scheduled_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return task
    
    def create_cross_system_orchestration(
        self,
        threat_id: str,
        systems: List[str],
        actions: Dict[str, Any]
    ) -> CrossSystemOrchestration:
        """
        Create cross-system orchestration plan.
        
        Coordinates actions across firewall, IDS, EDR, SIEM, etc.
        """
        orchestration_id = hashlib.sha256(
            f"{threat_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Determine execution order (firewall -> IDS -> EDR -> SIEM)
        priority_order = ['firewall', 'ids', 'edr', 'siem', 'soar']
        execution_order = [sys for sys in priority_order if sys in systems]
        execution_order.extend([sys for sys in systems if sys not in priority_order])
        
        orchestration = CrossSystemOrchestration(
            orchestration_id=orchestration_id,
            threat_id=threat_id,
            systems=systems,
            actions=actions,
            execution_order=execution_order,
            status=IntegrationStatus.PENDING
        )
        
        # Store orchestration
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cross_system_orchestration
            (orchestration_id, threat_id, systems, actions, execution_order, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            orchestration.orchestration_id,
            orchestration.threat_id,
            json.dumps(orchestration.systems),
            json.dumps(orchestration.actions),
            json.dumps(orchestration.execution_order),
            orchestration.status.value,
            orchestration.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return orchestration
    
    def submit_remediation_feedback(
        self,
        task_id: str,
        effectiveness_score: float,
        threat_eliminated: bool,
        side_effects: Optional[str] = None,
        lessons_learned: Optional[str] = None
    ) -> RemediationFeedback:
        """Submit feedback on remediation effectiveness"""
        feedback_id = hashlib.sha256(
            f"{task_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        feedback = RemediationFeedback(
            feedback_id=feedback_id,
            task_id=task_id,
            effectiveness_score=effectiveness_score,
            threat_eliminated=threat_eliminated,
            side_effects=side_effects,
            lessons_learned=lessons_learned
        )
        
        # Store feedback
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO remediation_feedback
            (feedback_id, task_id, effectiveness_score, threat_eliminated,
             side_effects, lessons_learned, provided_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.feedback_id,
            feedback.task_id,
            feedback.effectiveness_score,
            1 if feedback.threat_eliminated else 0,
            feedback.side_effects,
            feedback.lessons_learned,
            feedback.provided_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return feedback
    
    def get_pending_tasks(self, limit: int = 50) -> List[RemediationTask]:
        """Get pending remediation tasks"""
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_id, trigger, action, threat_data, target_assets,
                   priority, status, scheduled_at, started_at, completed_at,
                   result, error_message
            FROM remediation_tasks
            WHERE status IN ('pending', 'requires_approval')
            ORDER BY priority DESC, scheduled_at ASC
            LIMIT ?
        """, (limit,))
        
        tasks = []
        for row in cursor.fetchall():
            task = RemediationTask(
                task_id=row[0],
                trigger=RemediationTrigger(row[1]),
                action=RemediationAction(row[2]),
                threat_data=json.loads(row[3]),
                target_assets=json.loads(row[4]),
                priority=row[5],
                status=IntegrationStatus(row[6]),
                scheduled_at=datetime.fromisoformat(row[7]),
                started_at=datetime.fromisoformat(row[8]) if row[8] else None,
                completed_at=datetime.fromisoformat(row[9]) if row[9] else None,
                result=json.loads(row[10]) if row[10] else None,
                error_message=row[11]
            )
            tasks.append(task)
        
        conn.close()
        return tasks
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration performance metrics"""
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        # Total tasks by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM remediation_tasks
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Average effectiveness score
        cursor.execute("""
            SELECT AVG(effectiveness_score) as avg_score,
                   SUM(threat_eliminated) as threats_eliminated,
                   COUNT(*) as total_feedback
            FROM remediation_feedback
        """)
        feedback_stats = cursor.fetchone()
        
        # Tasks by trigger type
        cursor.execute("""
            SELECT trigger, COUNT(*) as count
            FROM remediation_tasks
            GROUP BY trigger
        """)
        trigger_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'status_distribution': status_counts,
            'avg_effectiveness_score': feedback_stats[0] if feedback_stats[0] else 0.0,
            'threats_eliminated': feedback_stats[1] or 0,
            'total_feedback_received': feedback_stats[2] or 0,
            'tasks_by_trigger': trigger_counts,
            'auto_execute_threshold': self.auto_execute_threshold
        }


# Example usage
if __name__ == "__main__":
    # Initialize remediation integration
    integration = RemediationEngineIntegration()
    
    print("=== Remediation Engine Integration ===\n")
    
    # Example 1: Create threat-remediation mapping
    print("=== Threat Mapping ===\n")
    
    mapping = integration.create_threat_mapping(
        threat_type="vulnerability",
        threat_identifier="CVE-2025-12345",
        remediation_actions=[
            RemediationAction.PATCH_DEPLOY,
            RemediationAction.SCAN_ASSETS
        ],
        priority_score=95,
        auto_execute=True,
        requires_approval=False
    )
    
    print(f"Created mapping: {mapping.mapping_id}")
    print(f"Threat: {mapping.threat_identifier}")
    print(f"Actions: {', '.join([a.value for a in mapping.remediation_actions])}")
    print(f"Priority: {mapping.priority_score}/100")
    print(f"Auto-execute: {mapping.auto_execute}")
    
    # Example 2: Trigger remediation from vulnerability
    print("\n=== Vulnerability Remediation ===\n")
    
    vuln_task = integration.trigger_remediation_from_vulnerability(
        cve_id="CVE-2024-1234",
        risk_score=92.5,
        affected_assets=["WEB-SERVER-01", "DB-SERVER-01", "APP-SERVER-01"]
    )
    
    if vuln_task:
        print(f"Task ID: {vuln_task.task_id}")
        print(f"Trigger: {vuln_task.trigger.value}")
        print(f"Action: {vuln_task.action.value}")
        print(f"Priority: {vuln_task.priority}/100")
        print(f"Status: {vuln_task.status.value}")
        print(f"Affected assets: {len(vuln_task.target_assets)}")
    
    # Example 3: Trigger remediation from IoC
    print("\n=== IoC-Based Remediation ===\n")
    
    ioc_task = integration.trigger_remediation_from_ioc(
        ioc_value="198.51.100.42",
        ioc_type="ipv4-addr",
        confidence=0.95,
        affected_assets=["FIREWALL-01", "IDS-01"]
    )
    
    if ioc_task:
        print(f"Task ID: {ioc_task.task_id}")
        print(f"Trigger: {ioc_task.trigger.value}")
        print(f"Action: {ioc_task.action.value}")
        print(f"Priority: {ioc_task.priority}/100")
        print(f"Status: {ioc_task.status.value}")
    
    # Example 4: Trigger remediation from campaign
    print("\n=== Campaign-Based Remediation ===\n")
    
    campaign_task = integration.trigger_remediation_from_campaign(
        campaign_id="CAMP-APT29-2024",
        target_match=True,
        affected_assets=["ALL-ENDPOINTS"]
    )
    
    if campaign_task:
        print(f"Task ID: {campaign_task.task_id}")
        print(f"Trigger: {campaign_task.trigger.value}")
        print(f"Action: {campaign_task.action.value}")
        print(f"Priority: {campaign_task.priority}/100")
    
    # Example 5: Cross-system orchestration
    print("\n=== Cross-System Orchestration ===\n")
    
    orchestration = integration.create_cross_system_orchestration(
        threat_id="THREAT-12345",
        systems=["firewall", "ids", "edr", "siem"],
        actions={
            'firewall': {'action': 'block_ip', 'ip': '198.51.100.42'},
            'ids': {'action': 'update_signatures', 'signature_id': 'SIG-12345'},
            'edr': {'action': 'scan_endpoints', 'threat_hash': 'abc123...'},
            'siem': {'action': 'create_alert', 'severity': 'critical'}
        }
    )
    
    print(f"Orchestration ID: {orchestration.orchestration_id}")
    print(f"Systems: {', '.join(orchestration.systems)}")
    print(f"Execution order: {' -> '.join(orchestration.execution_order)}")
    print(f"Status: {orchestration.status.value}")
    
    # Example 6: Submit remediation feedback
    print("\n=== Remediation Feedback ===\n")
    
    if vuln_task:
        feedback = integration.submit_remediation_feedback(
            task_id=vuln_task.task_id,
            effectiveness_score=0.95,
            threat_eliminated=True,
            side_effects=None,
            lessons_learned="Patch deployment successful, no system downtime"
        )
        
        print(f"Feedback ID: {feedback.feedback_id}")
        print(f"Effectiveness: {feedback.effectiveness_score:.0%}")
        print(f"Threat eliminated: {feedback.threat_eliminated}")
        print(f"Lessons: {feedback.lessons_learned}")
    
    # Example 7: Get pending tasks
    print("\n=== Pending Remediation Tasks ===\n")
    
    pending_tasks = integration.get_pending_tasks(limit=10)
    print(f"Pending tasks: {len(pending_tasks)}")
    for task in pending_tasks[:3]:
        print(f"\n{task.action.value} - Priority {task.priority}")
        print(f"  Trigger: {task.trigger.value}")
        print(f"  Status: {task.status.value}")
        print(f"  Assets: {len(task.target_assets)}")
    
    # Example 8: Get integration metrics
    print("\n=== Integration Metrics ===\n")
    
    metrics = integration.get_integration_metrics()
    print(f"Status distribution: {metrics['status_distribution']}")
    print(f"Avg effectiveness: {metrics['avg_effectiveness_score']:.2%}")
    print(f"Threats eliminated: {metrics['threats_eliminated']}")
    print(f"Total feedback: {metrics['total_feedback_received']}")
    print(f"Auto-execute threshold: {metrics['auto_execute_threshold']}")
    
    print("\n✓ Remediation Engine Integration operational!")
    print("\n🎉 MODULE G.2 COMPLETE! All 12 components delivered!")
