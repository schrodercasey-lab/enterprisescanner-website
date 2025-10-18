"""
Military Upgrade #26: CMDB & Asset Management
Part 3: Change Tracking and Versioning

This module implements comprehensive change tracking, version control,
and rollback capabilities for all configuration changes.

Key Features:
- Change request management
- Version control for configurations
- Change approval workflow
- Automated rollback
- Change audit trail

Compliance:
- ITIL v4 Change Management
- NIST 800-53 CM-3 (Configuration Change Control)
- ISO 20000 Change Management
- SOX Change Controls
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChangeType(Enum):
    """Types of changes"""
    STANDARD = "standard"
    NORMAL = "normal"
    EMERGENCY = "emergency"
    CONFIGURATION = "configuration"


class ChangeStatus(Enum):
    """Change request status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ChangeRisk(Enum):
    """Change risk levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ChangeRequest:
    """Change request record"""
    change_id: str
    change_type: ChangeType
    title: str
    description: str
    
    # Affected items
    affected_ci_ids: List[str] = field(default_factory=list)
    
    # Risk assessment
    risk_level: ChangeRisk = ChangeRisk.MEDIUM
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Planning
    implementation_plan: str = ""
    rollback_plan: str = ""
    test_plan: str = ""
    
    # Scheduling
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    maintenance_window: bool = False
    
    # Status
    status: ChangeStatus = ChangeStatus.DRAFT
    
    # Workflow
    requested_by: str = ""
    requested_at: datetime = field(default_factory=datetime.now)
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Implementation
    implemented_by: Optional[str] = None
    implemented_at: Optional[datetime] = None
    
    # Outcome
    success: Optional[bool] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class ConfigurationVersion:
    """Configuration version record"""
    version_id: str
    ci_id: str
    version_number: str
    
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Change tracking
    change_id: Optional[str] = None
    changed_by: str = "system"
    changed_at: datetime = field(default_factory=datetime.now)
    change_description: str = ""
    
    # Diff from previous
    changes: Dict[str, Any] = field(default_factory=dict)


class ChangeTrackingEngine:
    """Change tracking and version control engine"""
    
    def __init__(self):
        self.change_requests: Dict[str, ChangeRequest] = {}
        self.versions: Dict[str, List[ConfigurationVersion]] = {}  # ci_id -> [versions]
    
    def create_change_request(self, change_type: ChangeType, title: str,
                             description: str, requested_by: str,
                             affected_ci_ids: List[str],
                             **kwargs) -> ChangeRequest:
        """Create new change request"""
        change_id = f"CHG-{datetime.now().strftime('%Y%m%d')}-{len(self.change_requests) + 1:04d}"
        
        change = ChangeRequest(
            change_id=change_id,
            change_type=change_type,
            title=title,
            description=description,
            requested_by=requested_by,
            affected_ci_ids=affected_ci_ids,
            **kwargs
        )
        
        self.change_requests[change_id] = change
        
        print(f"📝 Change request created: {change_id}")
        print(f"   Title: {title}")
        print(f"   Type: {change_type.value}")
        print(f"   Affected CIs: {len(affected_ci_ids)}")
        
        return change
    
    def submit_change_request(self, change_id: str) -> bool:
        """Submit change request for review"""
        change = self.change_requests.get(change_id)
        if not change or change.status != ChangeStatus.DRAFT:
            return False
        
        # Validate required fields
        if not change.implementation_plan or not change.rollback_plan:
            print(f"❌ Cannot submit: Missing implementation or rollback plan")
            return False
        
        change.status = ChangeStatus.SUBMITTED
        
        print(f"📤 Change submitted: {change_id}")
        return True
    
    def review_change_request(self, change_id: str, reviewer: str,
                             approved: bool, comments: str = "") -> bool:
        """Review and approve/reject change request"""
        change = self.change_requests.get(change_id)
        if not change or change.status != ChangeStatus.SUBMITTED:
            return False
        
        change.reviewed_by = reviewer
        
        if approved:
            change.status = ChangeStatus.APPROVED
            change.approved_by = reviewer
            change.approved_at = datetime.now()
            print(f"✅ Change approved: {change_id}")
        else:
            change.status = ChangeStatus.REJECTED
            print(f"❌ Change rejected: {change_id}")
        
        if comments:
            change.notes.append(f"[{reviewer}] {comments}")
        
        return True
    
    def schedule_change(self, change_id: str, start_time: datetime,
                       end_time: datetime, maintenance_window: bool = False):
        """Schedule approved change"""
        change = self.change_requests.get(change_id)
        if not change or change.status != ChangeStatus.APPROVED:
            return False
        
        change.scheduled_start = start_time
        change.scheduled_end = end_time
        change.maintenance_window = maintenance_window
        change.status = ChangeStatus.SCHEDULED
        
        print(f"📅 Change scheduled: {change_id}")
        print(f"   Window: {start_time} to {end_time}")
        if maintenance_window:
            print(f"   ⚠️ Maintenance window required")
        
        return True
    
    def implement_change(self, change_id: str, ci_id: str,
                        new_configuration: Dict[str, Any],
                        implemented_by: str) -> Optional[ConfigurationVersion]:
        """Implement change and create version"""
        change = self.change_requests.get(change_id)
        if not change:
            return None
        
        change.status = ChangeStatus.IN_PROGRESS
        
        # Create new version
        version = self._create_version(
            ci_id=ci_id,
            configuration=new_configuration,
            change_id=change_id,
            changed_by=implemented_by,
            change_description=change.title
        )
        
        change.implemented_by = implemented_by
        change.implemented_at = datetime.now()
        change.status = ChangeStatus.COMPLETED
        change.success = True
        
        print(f"🔧 Change implemented: {change_id}")
        print(f"   Version created: {version.version_id}")
        
        return version
    
    def _create_version(self, ci_id: str, configuration: Dict[str, Any],
                       change_id: Optional[str], changed_by: str,
                       change_description: str) -> ConfigurationVersion:
        """Create configuration version"""
        # Get current version number
        ci_versions = self.versions.get(ci_id, [])
        
        if ci_versions:
            last_version = ci_versions[-1]
            major, minor, patch = map(int, last_version.version_number.split('.'))
            new_version = f"{major}.{minor}.{patch + 1}"
            
            # Calculate diff
            changes = self._calculate_diff(last_version.configuration, configuration)
        else:
            new_version = "1.0.0"
            changes = {'initial': True}
        
        version_id = f"VER-{ci_id}-{new_version}"
        
        version = ConfigurationVersion(
            version_id=version_id,
            ci_id=ci_id,
            version_number=new_version,
            configuration=configuration,
            change_id=change_id,
            changed_by=changed_by,
            change_description=change_description,
            changes=changes
        )
        
        if ci_id not in self.versions:
            self.versions[ci_id] = []
        
        self.versions[ci_id].append(version)
        
        print(f"   📦 Version {new_version} created for {ci_id}")
        
        return version
    
    def _calculate_diff(self, old_config: Dict[str, Any],
                       new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate difference between configurations"""
        diff = {
            'added': {},
            'modified': {},
            'removed': {}
        }
        
        # Find added and modified
        for key, new_value in new_config.items():
            if key not in old_config:
                diff['added'][key] = new_value
            elif old_config[key] != new_value:
                diff['modified'][key] = {
                    'old': old_config[key],
                    'new': new_value
                }
        
        # Find removed
        for key in old_config:
            if key not in new_config:
                diff['removed'][key] = old_config[key]
        
        return diff
    
    def rollback_change(self, change_id: str, rollback_by: str) -> bool:
        """Rollback a change to previous version"""
        change = self.change_requests.get(change_id)
        if not change:
            return False
        
        print(f"⏪ Rolling back change: {change_id}")
        
        # Rollback each affected CI
        for ci_id in change.affected_ci_ids:
            ci_versions = self.versions.get(ci_id, [])
            
            if len(ci_versions) >= 2:
                # Get previous version
                previous_version = ci_versions[-2]
                
                # Create rollback version
                self._create_version(
                    ci_id=ci_id,
                    configuration=previous_version.configuration,
                    change_id=f"ROLLBACK-{change_id}",
                    changed_by=rollback_by,
                    change_description=f"Rollback of {change_id}"
                )
                
                print(f"   ✅ Rolled back {ci_id} to version {previous_version.version_number}")
        
        change.status = ChangeStatus.ROLLED_BACK
        change.success = False
        change.notes.append(f"Rolled back by {rollback_by} at {datetime.now()}")
        
        return True
    
    def get_version_history(self, ci_id: str) -> List[ConfigurationVersion]:
        """Get version history for CI"""
        return self.versions.get(ci_id, [])
    
    def get_version(self, ci_id: str, version_number: str) -> Optional[ConfigurationVersion]:
        """Get specific version"""
        ci_versions = self.versions.get(ci_id, [])
        for version in ci_versions:
            if version.version_number == version_number:
                return version
        return None
    
    def compare_versions(self, ci_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions"""
        v1 = self.get_version(ci_id, version1)
        v2 = self.get_version(ci_id, version2)
        
        if not v1 or not v2:
            return {}
        
        diff = self._calculate_diff(v1.configuration, v2.configuration)
        
        return {
            'ci_id': ci_id,
            'version1': version1,
            'version2': version2,
            'differences': diff,
            'total_changes': (len(diff['added']) + len(diff['modified']) + len(diff['removed']))
        }
    
    def get_pending_changes(self) -> List[ChangeRequest]:
        """Get changes awaiting approval"""
        return [c for c in self.change_requests.values()
                if c.status in [ChangeStatus.SUBMITTED, ChangeStatus.UNDER_REVIEW]]
    
    def get_scheduled_changes(self) -> List[ChangeRequest]:
        """Get scheduled changes"""
        return [c for c in self.change_requests.values()
                if c.status == ChangeStatus.SCHEDULED]
    
    def get_emergency_changes(self) -> List[ChangeRequest]:
        """Get emergency changes"""
        return [c for c in self.change_requests.values()
                if c.change_type == ChangeType.EMERGENCY]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get change tracking statistics"""
        by_type = {}
        by_status = {}
        
        for change in self.change_requests.values():
            ctype = change.change_type.value
            by_type[ctype] = by_type.get(ctype, 0) + 1
            
            status = change.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        total_versions = sum(len(versions) for versions in self.versions.values())
        
        success_rate = 0
        completed_changes = [c for c in self.change_requests.values()
                           if c.status == ChangeStatus.COMPLETED]
        if completed_changes:
            successful = sum(1 for c in completed_changes if c.success)
            success_rate = (successful / len(completed_changes)) * 100
        
        return {
            'total_changes': len(self.change_requests),
            'by_type': by_type,
            'by_status': by_status,
            'total_versions': total_versions,
            'success_rate': f"{success_rate:.1f}%",
            'pending_approvals': len(self.get_pending_changes())
        }


# Example usage
if __name__ == "__main__":
    tracker = ChangeTrackingEngine()
    
    # Create change request
    change = tracker.create_change_request(
        change_type=ChangeType.NORMAL,
        title="Upgrade database to v15.0",
        description="Upgrade PostgreSQL from v14.5 to v15.0",
        requested_by="dba-team",
        affected_ci_ids=["CI-DATABASE-0001"],
        implementation_plan="1. Backup database\n2. Stop service\n3. Upgrade\n4. Start service",
        rollback_plan="Restore from backup",
        risk_level=ChangeRisk.HIGH
    )
    
    # Submit and approve
    tracker.submit_change_request(change.change_id)
    tracker.review_change_request(change.change_id, "change-manager", True, "Approved with conditions")
    
    # Schedule
    tracker.schedule_change(
        change.change_id,
        datetime(2025, 10, 20, 2, 0),
        datetime(2025, 10, 20, 4, 0),
        maintenance_window=True
    )
    
    # Statistics
    stats = tracker.get_statistics()
    print(f"\n📊 Change Statistics:")
    print(f"   Total changes: {stats['total_changes']}")
    print(f"   Success rate: {stats['success_rate']}")
