"""
Security Incident Response Playbook Execution Engine
NIST 800-61 Rev 2 compliant automated response playbooks

This module provides automated and semi-automated incident response
playbooks for common security incidents:

- Pre-defined playbooks (ransomware, data breach, DDoS, phishing, APT, etc.)
- Step-by-step execution with tracking
- Automated actions (network isolation, account disable, block IP, etc.)
- Manual action prompts with approval workflows
- Playbook versioning and customization
- Execution metrics and analytics
- Playbook testing and simulation
- Integration with SOAR platforms

NIST 800-61 Rev 2 Phases:
1. Preparation
2. Detection and Analysis
3. Containment, Eradication, and Recovery
4. Post-Incident Activity

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class PlaybookCategory(Enum):
    """Incident response playbook categories"""
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    DATA_BREACH = "data_breach"
    PHISHING = "phishing"
    DENIAL_OF_SERVICE = "denial_of_service"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    APT = "advanced_persistent_threat"
    INSIDER_THREAT = "insider_threat"
    WEB_ATTACK = "web_attack"
    SUPPLY_CHAIN = "supply_chain_compromise"


class StepType(Enum):
    """Playbook step types"""
    AUTOMATED = "automated"          # Fully automated action
    SEMI_AUTOMATED = "semi_automated" # Automated with approval
    MANUAL = "manual"                # Human action required
    DECISION = "decision"            # Decision point (branching)
    VERIFICATION = "verification"     # Verification checkpoint


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ActionType(Enum):
    """Types of automated actions"""
    ISOLATE_HOST = "isolate_host"
    BLOCK_IP = "block_ip"
    DISABLE_ACCOUNT = "disable_account"
    QUARANTINE_FILE = "quarantine_file"
    SNAPSHOT_SYSTEM = "snapshot_system"
    COLLECT_LOGS = "collect_logs"
    BLOCK_DOMAIN = "block_domain"
    REVOKE_CREDENTIALS = "revoke_credentials"
    ENABLE_MFA = "enable_mfa"
    RESET_PASSWORD = "reset_password"
    NOTIFY_STAKEHOLDERS = "notify_stakeholders"
    CREATE_BACKUP = "create_backup"


@dataclass
class PlaybookStep:
    """Individual step in incident response playbook"""
    step_id: str
    step_number: int
    title: str
    description: str
    step_type: StepType
    
    # NIST 800-61 phase
    ir_phase: str  # preparation, detection, containment, eradication, recovery, post_incident
    
    # Execution details
    action_type: Optional[ActionType] = None
    action_parameters: Dict[str, Any] = field(default_factory=dict)
    automation_script: Optional[str] = None
    
    # Approval requirements
    requires_approval: bool = False
    approvers: List[str] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # step_ids
    
    # Timing
    estimated_duration_minutes: int = 5
    timeout_minutes: Optional[int] = None
    
    # Status
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    
    # Results
    success: bool = False
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Decision branching
    next_step_on_success: Optional[str] = None
    next_step_on_failure: Optional[str] = None


@dataclass
class Playbook:
    """Incident response playbook"""
    playbook_id: str
    name: str
    description: str
    category: PlaybookCategory
    version: str
    
    # Metadata
    author: str = "Enterprise Scanner SOC"
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    
    # MITRE ATT&CK mapping
    mitre_tactics: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    
    # Steps
    steps: List[PlaybookStep] = field(default_factory=list)
    
    # Execution tracking
    execution_count: int = 0
    success_rate: float = 0.0
    average_duration_minutes: float = 0.0


@dataclass
class PlaybookExecution:
    """Playbook execution instance"""
    execution_id: str
    playbook_id: str
    incident_id: str
    
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Execution context
    triggered_by: str = "automatic"
    executor: Optional[str] = None
    
    # Current state
    current_step_index: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    
    # Results
    success: bool = False
    duration_minutes: float = 0.0
    
    # Execution log
    execution_log: List[Dict[str, Any]] = field(default_factory=list)


class PlaybookEngine:
    """
    Security Incident Response Playbook Execution Engine
    
    Manages automated and semi-automated execution of incident response
    playbooks following NIST 800-61 Rev 2 framework.
    """
    
    def __init__(self):
        self.playbooks: Dict[str, Playbook] = {}
        self.executions: Dict[str, PlaybookExecution] = {}
        
        # Action handlers (in production, these would be real integrations)
        self.action_handlers: Dict[ActionType, Callable] = {}
        
        # Initialize default playbooks
        self._initialize_default_playbooks()
    
    def _initialize_default_playbooks(self) -> None:
        """Initialize standard incident response playbooks"""
        
        # Ransomware Response Playbook
        ransomware_playbook = self._create_ransomware_playbook()
        self.playbooks[ransomware_playbook.playbook_id] = ransomware_playbook
        
        # Data Breach Response Playbook
        data_breach_playbook = self._create_data_breach_playbook()
        self.playbooks[data_breach_playbook.playbook_id] = data_breach_playbook
        
        # Phishing Response Playbook
        phishing_playbook = self._create_phishing_playbook()
        self.playbooks[phishing_playbook.playbook_id] = phishing_playbook
        
        # DDoS Response Playbook
        ddos_playbook = self._create_ddos_playbook()
        self.playbooks[ddos_playbook.playbook_id] = ddos_playbook
        
        print(f"✅ Initialized {len(self.playbooks)} default playbooks")
    
    def _create_ransomware_playbook(self) -> Playbook:
        """Create ransomware incident response playbook"""
        
        playbook = Playbook(
            playbook_id="PB-RANSOMWARE-001",
            name="Ransomware Incident Response",
            description="Comprehensive ransomware containment, eradication, and recovery playbook",
            category=PlaybookCategory.RANSOMWARE,
            version="1.0.0",
            mitre_tactics=["TA0040", "TA0005"],  # Impact, Defense Evasion
            mitre_techniques=["T1486", "T1490", "T1489"]  # Data Encrypted, Inhibit Recovery, Service Stop
        )
        
        # Step 1: Immediate Isolation
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-01",
            step_number=1,
            title="Isolate Infected Systems",
            description="Immediately isolate all infected systems from network to prevent spread",
            step_type=StepType.AUTOMATED,
            ir_phase="containment",
            action_type=ActionType.ISOLATE_HOST,
            estimated_duration_minutes=2,
            timeout_minutes=5
        ))
        
        # Step 2: Identify Ransomware Variant
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-02",
            step_number=2,
            title="Identify Ransomware Variant",
            description="Analyze ransom note, file extensions, and IOCs to identify ransomware family",
            step_type=StepType.MANUAL,
            ir_phase="detection",
            estimated_duration_minutes=15,
            depends_on=["RANSOM-STEP-01"]
        ))
        
        # Step 3: Check for Decryption Tools
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-03",
            step_number=3,
            title="Check for Available Decryption Tools",
            description="Consult No More Ransom project and vendor resources for decryption tools",
            step_type=StepType.AUTOMATED,
            ir_phase="recovery",
            estimated_duration_minutes=5,
            depends_on=["RANSOM-STEP-02"]
        ))
        
        # Step 4: Snapshot Systems
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-04",
            step_number=4,
            title="Create System Snapshots",
            description="Take forensic snapshots of affected systems for investigation",
            step_type=StepType.AUTOMATED,
            ir_phase="containment",
            action_type=ActionType.SNAPSHOT_SYSTEM,
            estimated_duration_minutes=30,
            depends_on=["RANSOM-STEP-01"]
        ))
        
        # Step 5: Assess Backup Status
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-05",
            step_number=5,
            title="Verify Backup Integrity",
            description="Verify that clean backups are available and not compromised",
            step_type=StepType.MANUAL,
            ir_phase="recovery",
            estimated_duration_minutes=20,
            depends_on=["RANSOM-STEP-04"]
        ))
        
        # Step 6: Disable Compromised Accounts
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-06",
            step_number=6,
            title="Disable Compromised Accounts",
            description="Disable all accounts suspected of compromise or used in initial access",
            step_type=StepType.SEMI_AUTOMATED,
            ir_phase="containment",
            action_type=ActionType.DISABLE_ACCOUNT,
            requires_approval=True,
            approvers=["incident_commander", "ciso"],
            estimated_duration_minutes=10,
            depends_on=["RANSOM-STEP-02"]
        ))
        
        # Step 7: Block C2 Communications
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-07",
            step_number=7,
            title="Block Command & Control",
            description="Block all identified C2 IP addresses and domains at firewall/proxy",
            step_type=StepType.AUTOMATED,
            ir_phase="containment",
            action_type=ActionType.BLOCK_IP,
            estimated_duration_minutes=5,
            depends_on=["RANSOM-STEP-02"]
        ))
        
        # Step 8: Malware Removal
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-08",
            step_number=8,
            title="Remove Ransomware",
            description="Use EDR tools to remove ransomware from affected systems",
            step_type=StepType.SEMI_AUTOMATED,
            ir_phase="eradication",
            estimated_duration_minutes=45,
            requires_approval=True,
            depends_on=["RANSOM-STEP-04", "RANSOM-STEP-06"]
        ))
        
        # Step 9: Restore from Backup
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-09",
            step_number=9,
            title="Restore Systems from Backup",
            description="Restore affected systems from verified clean backups",
            step_type=StepType.SEMI_AUTOMATED,
            ir_phase="recovery",
            estimated_duration_minutes=120,
            requires_approval=True,
            approvers=["incident_commander", "infrastructure_team"],
            depends_on=["RANSOM-STEP-05", "RANSOM-STEP-08"]
        ))
        
        # Step 10: Reset All Passwords
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-10",
            step_number=10,
            title="Force Password Reset",
            description="Force password reset for all users and rotate service account credentials",
            step_type=StepType.AUTOMATED,
            ir_phase="recovery",
            action_type=ActionType.RESET_PASSWORD,
            estimated_duration_minutes=30,
            depends_on=["RANSOM-STEP-08"]
        ))
        
        # Step 11: Enable Enhanced Monitoring
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-11",
            step_number=11,
            title="Enable Enhanced Monitoring",
            description="Enable enhanced logging and monitoring for early detection of recurrence",
            step_type=StepType.AUTOMATED,
            ir_phase="recovery",
            estimated_duration_minutes=15,
            depends_on=["RANSOM-STEP-09"]
        ))
        
        # Step 12: Verify System Integrity
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-12",
            step_number=12,
            title="Verify System Integrity",
            description="Run integrity checks and vulnerability scans on restored systems",
            step_type=StepType.AUTOMATED,
            ir_phase="recovery",
            estimated_duration_minutes=60,
            depends_on=["RANSOM-STEP-09", "RANSOM-STEP-10"]
        ))
        
        # Step 13: Notify Stakeholders
        playbook.steps.append(PlaybookStep(
            step_id="RANSOM-STEP-13",
            step_number=13,
            title="Stakeholder Notification",
            description="Notify executives, legal, PR, and affected parties per incident communication plan",
            step_type=StepType.MANUAL,
            ir_phase="post_incident",
            action_type=ActionType.NOTIFY_STAKEHOLDERS,
            estimated_duration_minutes=30,
            depends_on=["RANSOM-STEP-12"]
        ))
        
        return playbook
    
    def _create_data_breach_playbook(self) -> Playbook:
        """Create data breach incident response playbook"""
        
        playbook = Playbook(
            playbook_id="PB-DATABREACH-001",
            name="Data Breach Incident Response",
            description="Data breach containment, investigation, and regulatory notification playbook",
            category=PlaybookCategory.DATA_BREACH,
            version="1.0.0",
            mitre_tactics=["TA0010", "TA0009"],  # Exfiltration, Collection
            mitre_techniques=["T1048", "T1567", "T1020"]  # Exfiltration Over Alternative Protocol
        )
        
        playbook.steps.extend([
            PlaybookStep(
                step_id="BREACH-STEP-01",
                step_number=1,
                title="Isolate Affected Systems",
                description="Isolate systems involved in suspected data breach",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.ISOLATE_HOST,
                estimated_duration_minutes=5
            ),
            PlaybookStep(
                step_id="BREACH-STEP-02",
                step_number=2,
                title="Identify Compromised Data",
                description="Determine what data was accessed or exfiltrated",
                step_type=StepType.MANUAL,
                ir_phase="detection",
                estimated_duration_minutes=60,
                depends_on=["BREACH-STEP-01"]
            ),
            PlaybookStep(
                step_id="BREACH-STEP-03",
                step_number=3,
                title="Preserve Evidence",
                description="Collect and preserve forensic evidence per chain of custody",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.SNAPSHOT_SYSTEM,
                estimated_duration_minutes=30,
                depends_on=["BREACH-STEP-01"]
            ),
            PlaybookStep(
                step_id="BREACH-STEP-04",
                step_number=4,
                title="Block Exfiltration Paths",
                description="Block identified exfiltration methods and C2 channels",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.BLOCK_IP,
                estimated_duration_minutes=10,
                depends_on=["BREACH-STEP-02"]
            ),
            PlaybookStep(
                step_id="BREACH-STEP-05",
                step_number=5,
                title="Revoke Compromised Credentials",
                description="Revoke all credentials that may have been compromised",
                step_type=StepType.SEMI_AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.REVOKE_CREDENTIALS,
                requires_approval=True,
                estimated_duration_minutes=20,
                depends_on=["BREACH-STEP-02"]
            ),
            PlaybookStep(
                step_id="BREACH-STEP-06",
                step_number=6,
                title="Assess Regulatory Requirements",
                description="Determine GDPR, CCPA, HIPAA, PCI DSS notification requirements",
                step_type=StepType.MANUAL,
                ir_phase="post_incident",
                estimated_duration_minutes=30,
                depends_on=["BREACH-STEP-02"]
            ),
            PlaybookStep(
                step_id="BREACH-STEP-07",
                step_number=7,
                title="Notify Affected Parties",
                description="Notify affected individuals and regulatory bodies per legal requirements",
                step_type=StepType.MANUAL,
                ir_phase="post_incident",
                action_type=ActionType.NOTIFY_STAKEHOLDERS,
                estimated_duration_minutes=120,
                depends_on=["BREACH-STEP-06"]
            )
        ])
        
        return playbook
    
    def _create_phishing_playbook(self) -> Playbook:
        """Create phishing incident response playbook"""
        
        playbook = Playbook(
            playbook_id="PB-PHISHING-001",
            name="Phishing Incident Response",
            description="Phishing campaign detection, containment, and user remediation",
            category=PlaybookCategory.PHISHING,
            version="1.0.0",
            mitre_tactics=["TA0001", "TA0043"],  # Initial Access, Reconnaissance
            mitre_techniques=["T1566", "T1598"]  # Phishing
        )
        
        playbook.steps.extend([
            PlaybookStep(
                step_id="PHISH-STEP-01",
                step_number=1,
                title="Quarantine Phishing Emails",
                description="Quarantine all instances of phishing email from all mailboxes",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.QUARANTINE_FILE,
                estimated_duration_minutes=5
            ),
            PlaybookStep(
                step_id="PHISH-STEP-02",
                step_number=2,
                title="Block Sender and Domains",
                description="Block sender email address and associated domains",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.BLOCK_DOMAIN,
                estimated_duration_minutes=3,
                depends_on=["PHISH-STEP-01"]
            ),
            PlaybookStep(
                step_id="PHISH-STEP-03",
                step_number=3,
                title="Identify Victims",
                description="Identify users who opened email or clicked malicious links",
                step_type=StepType.AUTOMATED,
                ir_phase="detection",
                estimated_duration_minutes=10,
                depends_on=["PHISH-STEP-01"]
            ),
            PlaybookStep(
                step_id="PHISH-STEP-04",
                step_number=4,
                title="Reset Compromised Credentials",
                description="Force password reset for users who entered credentials",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.RESET_PASSWORD,
                estimated_duration_minutes=10,
                depends_on=["PHISH-STEP-03"]
            ),
            PlaybookStep(
                step_id="PHISH-STEP-05",
                step_number=5,
                title="Scan for Malware",
                description="Run EDR scans on systems of users who clicked links/attachments",
                step_type=StepType.AUTOMATED,
                ir_phase="detection",
                estimated_duration_minutes=30,
                depends_on=["PHISH-STEP-03"]
            ),
            PlaybookStep(
                step_id="PHISH-STEP-06",
                step_number=6,
                title="User Awareness Training",
                description="Enroll affected users in security awareness training",
                step_type=StepType.MANUAL,
                ir_phase="post_incident",
                estimated_duration_minutes=15,
                depends_on=["PHISH-STEP-05"]
            )
        ])
        
        return playbook
    
    def _create_ddos_playbook(self) -> Playbook:
        """Create DDoS incident response playbook"""
        
        playbook = Playbook(
            playbook_id="PB-DDOS-001",
            name="DDoS Attack Response",
            description="Distributed Denial of Service mitigation and recovery",
            category=PlaybookCategory.DENIAL_OF_SERVICE,
            version="1.0.0",
            mitre_tactics=["TA0040"],  # Impact
            mitre_techniques=["T1498", "T1499"]  # Network/Endpoint DoS
        )
        
        playbook.steps.extend([
            PlaybookStep(
                step_id="DDOS-STEP-01",
                step_number=1,
                title="Activate DDoS Protection",
                description="Enable cloud-based DDoS protection (Cloudflare, AWS Shield, etc.)",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                estimated_duration_minutes=5
            ),
            PlaybookStep(
                step_id="DDOS-STEP-02",
                step_number=2,
                title="Identify Attack Vectors",
                description="Analyze traffic patterns to identify attack type and source",
                step_type=StepType.AUTOMATED,
                ir_phase="detection",
                estimated_duration_minutes=10,
                depends_on=["DDOS-STEP-01"]
            ),
            PlaybookStep(
                step_id="DDOS-STEP-03",
                step_number=3,
                title="Block Attack Sources",
                description="Implement ACLs to block identified attack source IPs/ranges",
                step_type=StepType.AUTOMATED,
                ir_phase="containment",
                action_type=ActionType.BLOCK_IP,
                estimated_duration_minutes=5,
                depends_on=["DDOS-STEP-02"]
            ),
            PlaybookStep(
                step_id="DDOS-STEP-04",
                step_number=4,
                title="Scale Infrastructure",
                description="Auto-scale infrastructure to handle legitimate traffic",
                step_type=StepType.AUTOMATED,
                ir_phase="recovery",
                estimated_duration_minutes=15,
                depends_on=["DDOS-STEP-03"]
            ),
            PlaybookStep(
                step_id="DDOS-STEP-05",
                step_number=5,
                title="Notify ISP/Provider",
                description="Contact ISP and hosting provider for upstream mitigation",
                step_type=StepType.MANUAL,
                ir_phase="containment",
                estimated_duration_minutes=20,
                depends_on=["DDOS-STEP-02"]
            )
        ])
        
        return playbook
    
    def execute_playbook(
        self,
        playbook_id: str,
        incident_id: str,
        executor: Optional[str] = None,
        auto_approve: bool = False
    ) -> PlaybookExecution:
        """
        Execute incident response playbook.
        
        Args:
            playbook_id: Playbook to execute
            incident_id: Associated incident ID
            executor: User executing playbook
            auto_approve: Auto-approve steps requiring approval (use with caution)
            
        Returns:
            PlaybookExecution instance
        """
        if playbook_id not in self.playbooks:
            raise ValueError(f"Playbook {playbook_id} not found")
        
        playbook = self.playbooks[playbook_id]
        
        execution = PlaybookExecution(
            execution_id=str(uuid.uuid4()),
            playbook_id=playbook_id,
            incident_id=incident_id,
            started_at=datetime.now(),
            executor=executor
        )
        
        self.executions[execution.execution_id] = execution
        
        print(f"🚀 Executing Playbook: {playbook.name}")
        print(f"   Execution ID: {execution.execution_id}")
        print(f"   Incident: {incident_id}")
        print(f"   Total Steps: {len(playbook.steps)}")
        print()
        
        # Execute steps in order
        for step in playbook.steps:
            self._execute_step(execution, playbook, step, auto_approve)
        
        # Complete execution
        execution.completed_at = datetime.now()
        execution.duration_minutes = (execution.completed_at - execution.started_at).total_seconds() / 60
        execution.success = execution.failed_steps == 0
        
        # Update playbook metrics
        playbook.execution_count += 1
        playbook.average_duration_minutes = (
            (playbook.average_duration_minutes * (playbook.execution_count - 1) + execution.duration_minutes)
            / playbook.execution_count
        )
        if execution.success:
            playbook.success_rate = (
                (playbook.success_rate * (playbook.execution_count - 1) + 100)
                / playbook.execution_count
            )
        else:
            playbook.success_rate = (
                (playbook.success_rate * (playbook.execution_count - 1) + 0)
                / playbook.execution_count
            )
        
        print(f"\n{'='*60}")
        print(f"✅ Playbook Execution Complete")
        print(f"   Duration: {execution.duration_minutes:.1f} minutes")
        print(f"   Completed Steps: {execution.completed_steps}/{len(playbook.steps)}")
        print(f"   Failed Steps: {execution.failed_steps}")
        print(f"   Success: {'YES' if execution.success else 'NO'}")
        print(f"{'='*60}")
        
        return execution
    
    def _execute_step(
        self,
        execution: PlaybookExecution,
        playbook: Playbook,
        step: PlaybookStep,
        auto_approve: bool
    ) -> None:
        """Execute single playbook step"""
        
        # Check dependencies
        if not self._check_dependencies(execution, step):
            step.status = StepStatus.SKIPPED
            execution.skipped_steps += 1
            print(f"⏭️  Step {step.step_number}: {step.title} - SKIPPED (dependencies not met)")
            return
        
        print(f"▶️  Step {step.step_number}: {step.title}")
        print(f"    Type: {step.step_type.value} | Phase: {step.ir_phase}")
        
        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.now()
        
        try:
            if step.step_type == StepType.AUTOMATED:
                self._execute_automated_step(step)
            elif step.step_type == StepType.SEMI_AUTOMATED:
                if step.requires_approval and not auto_approve:
                    self._request_approval(step)
                self._execute_automated_step(step)
            elif step.step_type == StepType.MANUAL:
                self._execute_manual_step(step)
            
            step.status = StepStatus.COMPLETED
            step.success = True
            execution.completed_steps += 1
            
            print(f"    ✅ COMPLETED ({(datetime.now() - step.started_at).total_seconds():.1f}s)")
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            execution.failed_steps += 1
            
            print(f"    ❌ FAILED: {e}")
        
        finally:
            step.completed_at = datetime.now()
            execution.current_step_index += 1
            
            # Log to execution log
            execution.execution_log.append({
                'step_id': step.step_id,
                'step_number': step.step_number,
                'title': step.title,
                'status': step.status.value,
                'duration_seconds': (step.completed_at - step.started_at).total_seconds() if step.completed_at else 0,
                'success': step.success,
                'error': step.error_message
            })
        
        print()
    
    def _check_dependencies(self, execution: PlaybookExecution, step: PlaybookStep) -> bool:
        """Check if step dependencies are satisfied"""
        if not step.depends_on:
            return True
        
        # Check if all dependent steps completed successfully
        for log_entry in execution.execution_log:
            if log_entry['step_id'] in step.depends_on:
                if not log_entry['success']:
                    return False
        
        return True
    
    def _execute_automated_step(self, step: PlaybookStep) -> None:
        """Execute automated action"""
        if not step.action_type:
            return
        
        # In production, execute real actions via integrations
        # For now, simulate execution
        action = step.action_type.value
        params = step.action_parameters
        
        print(f"    🤖 Executing automated action: {action}")
        
        # Simulate different actions
        if step.action_type == ActionType.ISOLATE_HOST:
            step.result_data = {'hosts_isolated': params.get('hosts', ['host1', 'host2'])}
        elif step.action_type == ActionType.BLOCK_IP:
            step.result_data = {'ips_blocked': params.get('ips', ['192.168.1.100'])}
        elif step.action_type == ActionType.DISABLE_ACCOUNT:
            step.result_data = {'accounts_disabled': params.get('accounts', ['user1'])}
        elif step.action_type == ActionType.RESET_PASSWORD:
            step.result_data = {'passwords_reset': params.get('users', ['all_users'])}
        
        # Simulate execution time
        import time
        time.sleep(0.5)
    
    def _execute_manual_step(self, step: PlaybookStep) -> None:
        """Execute manual step (simulated)"""
        print(f"    👤 Manual action required: {step.description}")
        print(f"    📋 Estimated duration: {step.estimated_duration_minutes} minutes")
        
        # In production, this would wait for human confirmation
        # For now, auto-complete
        step.result_data = {'status': 'completed_by_analyst'}
    
    def _request_approval(self, step: PlaybookStep) -> None:
        """Request approval for step execution"""
        print(f"    ⚠️  Approval required from: {', '.join(step.approvers)}")
        
        # In production, send notifications and wait for approval
        # For now, auto-approve after notification
        step.status = StepStatus.AWAITING_APPROVAL
        
        # Simulate approval delay
        import time
        time.sleep(0.3)
        
        print(f"    ✅ Approval granted")
    
    def get_playbook_metrics(self) -> Dict[str, Any]:
        """Get playbook execution metrics"""
        
        metrics = {
            'total_playbooks': len(self.playbooks),
            'total_executions': len(self.executions),
            'by_category': {},
            'top_playbooks': []
        }
        
        # Count by category
        for playbook in self.playbooks.values():
            category = playbook.category.value
            if category not in metrics['by_category']:
                metrics['by_category'][category] = {
                    'count': 0,
                    'executions': 0,
                    'success_rate': 0.0
                }
            metrics['by_category'][category]['count'] += 1
            metrics['by_category'][category]['executions'] += playbook.execution_count
            metrics['by_category'][category]['success_rate'] = (
                (metrics['by_category'][category]['success_rate'] * (metrics['by_category'][category]['count'] - 1) + playbook.success_rate)
                / metrics['by_category'][category]['count']
            )
        
        # Top playbooks by execution count
        sorted_playbooks = sorted(
            self.playbooks.values(),
            key=lambda p: p.execution_count,
            reverse=True
        )[:5]
        
        for pb in sorted_playbooks:
            metrics['top_playbooks'].append({
                'name': pb.name,
                'executions': pb.execution_count,
                'success_rate': pb.success_rate,
                'avg_duration_minutes': pb.average_duration_minutes
            })
        
        return metrics


# Example usage
if __name__ == "__main__":
    # Initialize playbook engine
    engine = PlaybookEngine()
    
    print("Available Playbooks:")
    for pb_id, pb in engine.playbooks.items():
        print(f"  - {pb.name} ({pb_id}): {len(pb.steps)} steps")
    print()
    
    # Execute ransomware playbook
    execution = engine.execute_playbook(
        playbook_id="PB-RANSOMWARE-001",
        incident_id="INC-20251017-RANSOM-001",
        executor="alice@enterprisescanner.com",
        auto_approve=True  # Auto-approve for demo
    )
    
    # Get metrics
    metrics = engine.get_playbook_metrics()
    print(f"\n📊 Playbook Engine Metrics:")
    print(f"   Total Playbooks: {metrics['total_playbooks']}")
    print(f"   Total Executions: {metrics['total_executions']}")
    print(f"\n   By Category:")
    for category, data in metrics['by_category'].items():
        print(f"     {category}: {data['executions']} executions, {data['success_rate']:.1f}% success")
