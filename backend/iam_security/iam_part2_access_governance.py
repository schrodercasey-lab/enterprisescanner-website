"""
Military Upgrade #33: Enhanced IAM Security - Part 2
Access Governance & Identity Lifecycle Management

This module provides identity governance and administration:
- Automated provisioning/deprovisioning
- Role lifecycle management
- Access policy enforcement
- Segregation of duties (SoD) enforcement
- Identity lifecycle automation
- Entitlement management
- Policy-based access control (PBAC)
- Compliance enforcement

Key Capabilities:
- Automated onboarding/offboarding
- Role mining and optimization
- Access policy generation
- SoD conflict detection and remediation
- Attestation and recertification
- Access reviews and auditing
- Identity synchronization
- Delegated administration

Compliance:
- NIST 800-53 AC-2 (Account Management)
- NIST 800-53 AC-5 (Separation of Duties)
- SOX (Access Controls)
- GDPR Article 32 (Access Management)
- HIPAA (Access Controls)
- PCI DSS 7.1 (Limit Access)

Author: Enterprise Scanner Team
Version: 1.0.0 (October 17, 2025)
"""

import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum


class ProvisioningAction(Enum):
    """Provisioning actions"""
    CREATE = "create"
    MODIFY = "modify"
    DISABLE = "disable"
    DELETE = "delete"
    RESTORE = "restore"


class AccessPolicyType(Enum):
    """Access policy types"""
    ROLE_BASED = "role_based"  # RBAC
    ATTRIBUTE_BASED = "attribute_based"  # ABAC
    RULE_BASED = "rule_based"
    TIME_BASED = "time_based"
    LOCATION_BASED = "location_based"


class LifecycleStage(Enum):
    """Identity lifecycle stages"""
    PRE_HIRE = "pre_hire"
    ACTIVE = "active"
    LEAVE = "leave"
    TRANSFER = "transfer"
    TERMINATION = "termination"
    POST_TERMINATION = "post_termination"


@dataclass
class AccessPolicy:
    """Access control policy"""
    policy_id: str
    policy_name: str
    policy_type: AccessPolicyType
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Actions
    allow_actions: List[str] = field(default_factory=list)
    deny_actions: List[str] = field(default_factory=list)
    
    # Scope
    applies_to: List[str] = field(default_factory=list)  # Roles, groups
    resources: List[str] = field(default_factory=list)
    
    # Status
    enabled: bool = True
    priority: int = 100  # Lower = higher priority
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    last_modified: datetime = field(default_factory=datetime.now)


@dataclass
class RoleDefinition:
    """Role definition"""
    role_id: str
    role_name: str
    description: str
    
    # Permissions
    permissions: List[str] = field(default_factory=list)
    
    # Inheritance
    inherits_from: List[str] = field(default_factory=list)
    
    # Constraints
    max_members: Optional[int] = None
    requires_approval: bool = False
    
    # Risk
    risk_level: str = "low"  # low, medium, high, critical
    
    # SoD
    conflicts_with: List[str] = field(default_factory=list)
    
    # Metadata
    owner: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class ProvisioningRequest:
    """Identity provisioning request"""
    request_id: str
    action: ProvisioningAction
    
    # Target
    identity_id: str
    username: str
    
    # Details
    attributes: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    
    # Workflow
    requested_by: str = ""
    requested_at: datetime = field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status
    status: str = "pending"  # pending, approved, completed, failed
    error_message: Optional[str] = None


@dataclass
class SoDConflict:
    """Segregation of duties conflict"""
    conflict_id: str
    identity_id: str
    
    # Conflicting roles
    role1: str
    role2: str
    
    # Details
    conflict_type: str = "role_combination"
    severity: str = "high"  # low, medium, high, critical
    description: str = ""
    
    # Remediation
    remediation_status: str = "open"  # open, accepted_risk, remediated
    remediation_plan: Optional[str] = None
    remediation_date: Optional[datetime] = None
    
    # Metadata
    detected_date: datetime = field(default_factory=datetime.now)
    detected_by: str = "auto"


class IdentityGovernanceEngine:
    """
    Identity governance and lifecycle management engine
    """
    
    def __init__(self):
        """Initialize governance engine"""
        self.roles: Dict[str, RoleDefinition] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.provisioning_requests: List[ProvisioningRequest] = []
        self.sod_conflicts: List[SoDConflict] = []
        
        # Configuration
        self.auto_approve_low_risk = True
        self.require_manager_approval = True
        
        # Initialize default roles and policies
        self._initialize_default_roles()
        self._initialize_default_policies()
    
    def _initialize_default_roles(self):
        """Initialize default role definitions"""
        default_roles = [
            RoleDefinition(
                role_id="ROLE-001",
                role_name="employee",
                description="Standard employee access",
                permissions=["read_email", "access_intranet", "submit_expenses"],
                risk_level="low"
            ),
            RoleDefinition(
                role_id="ROLE-002",
                role_name="developer",
                description="Software developer",
                permissions=["read_code", "write_code", "submit_pr", "access_dev"],
                risk_level="medium",
                inherits_from=["employee"]
            ),
            RoleDefinition(
                role_id="ROLE-003",
                role_name="prod_admin",
                description="Production administrator",
                permissions=["deploy_prod", "restart_services", "view_logs"],
                risk_level="high",
                conflicts_with=["developer", "auditor"]
            ),
            RoleDefinition(
                role_id="ROLE-004",
                role_name="auditor",
                description="Security auditor",
                permissions=["read_logs", "generate_reports", "audit_access"],
                risk_level="medium",
                conflicts_with=["prod_admin", "system_admin"]
            ),
            RoleDefinition(
                role_id="ROLE-005",
                role_name="system_admin",
                description="System administrator",
                permissions=["manage_users", "configure_system", "install_software"],
                risk_level="critical",
                conflicts_with=["auditor", "developer"]
            )
        ]
        
        for role in default_roles:
            self.roles[role.role_id] = role
    
    def _initialize_default_policies(self):
        """Initialize default access policies"""
        default_policies = [
            AccessPolicy(
                policy_id="POL-001",
                policy_name="Business Hours Access",
                policy_type=AccessPolicyType.TIME_BASED,
                conditions={"hour_range": [8, 18]},
                allow_actions=["read", "write"],
                applies_to=["employee"],
                priority=50
            ),
            AccessPolicy(
                policy_id="POL-002",
                policy_name="Manager Approval Required",
                policy_type=AccessPolicyType.RULE_BASED,
                conditions={"risk_level": ["high", "critical"]},
                allow_actions=["request_access"],
                priority=10
            ),
            AccessPolicy(
                policy_id="POL-003",
                policy_name="MFA Required for Admin",
                policy_type=AccessPolicyType.ROLE_BASED,
                conditions={"roles": ["system_admin", "prod_admin"]},
                allow_actions=["admin_access"],
                priority=5
            )
        ]
        
        for policy in default_policies:
            self.policies[policy.policy_id] = policy
    
    def provision_identity(
        self,
        username: str,
        attributes: Dict[str, Any],
        roles: List[str],
        requested_by: str
    ) -> ProvisioningRequest:
        """
        Create new identity provisioning request
        
        Args:
            username: Username for new identity
            attributes: Identity attributes (email, dept, manager, etc.)
            roles: Roles to assign
            requested_by: Requestor
            
        Returns:
            Provisioning request
        """
        request_id = f"PROV-{len(self.provisioning_requests)+1:06d}"
        identity_id = f"USER-{len(self.provisioning_requests)+100:04d}"
        
        request = ProvisioningRequest(
            request_id=request_id,
            action=ProvisioningAction.CREATE,
            identity_id=identity_id,
            username=username,
            attributes=attributes,
            roles=roles,
            requested_by=requested_by
        )
        
        print(f"\n👤 Provisioning Request: {request_id}")
        print(f"   Username: {username}")
        print(f"   Roles: {', '.join(roles)}")
        print(f"   Department: {attributes.get('department', 'N/A')}")
        
        # Check if approval required
        requires_approval = False
        for role_name in roles:
            role = self._find_role_by_name(role_name)
            if role and role.risk_level in ['high', 'critical']:
                requires_approval = True
                break
        
        if self.auto_approve_low_risk and not requires_approval:
            # Auto-approve low risk requests
            request.status = "approved"
            request.approved_by = "auto_approved"
            request.approved_at = datetime.now()
            print(f"   ✅ Auto-approved (low risk)")
            
            # Execute provisioning
            self._execute_provisioning(request)
        else:
            # Requires manual approval
            request.status = "pending"
            print(f"   ⏳ Pending approval (high risk roles)")
        
        self.provisioning_requests.append(request)
        return request
    
    def deprovision_identity(
        self,
        identity_id: str,
        reason: str,
        requested_by: str
    ) -> ProvisioningRequest:
        """
        Deprovision (terminate) identity
        
        Args:
            identity_id: Identity to deprovision
            reason: Termination reason
            requested_by: Requestor
            
        Returns:
            Deprovisioning request
        """
        request_id = f"DEPROV-{len(self.provisioning_requests)+1:06d}"
        
        request = ProvisioningRequest(
            request_id=request_id,
            action=ProvisioningAction.DELETE,
            identity_id=identity_id,
            username="",  # Will be populated from identity
            attributes={"reason": reason},
            requested_by=requested_by
        )
        
        print(f"\n🚫 Deprovisioning Request: {request_id}")
        print(f"   Identity: {identity_id}")
        print(f"   Reason: {reason}")
        
        # Deprovisioning is critical - always require approval
        request.status = "pending"
        print(f"   ⏳ Pending approval")
        
        self.provisioning_requests.append(request)
        return request
    
    def _execute_provisioning(self, request: ProvisioningRequest):
        """Execute approved provisioning request"""
        try:
            if request.action == ProvisioningAction.CREATE:
                print(f"   🔧 Creating identity: {request.username}")
                # In production: Create in AD, email, systems
                
            elif request.action == ProvisioningAction.MODIFY:
                print(f"   🔧 Modifying identity: {request.identity_id}")
                # In production: Update attributes, roles
                
            elif request.action == ProvisioningAction.DELETE:
                print(f"   🔧 Deprovisioning identity: {request.identity_id}")
                # In production: Disable accounts, revoke access
            
            request.status = "completed"
            request.completed_at = datetime.now()
            print(f"   ✅ Provisioning completed")
            
        except Exception as e:
            request.status = "failed"
            request.error_message = str(e)
            print(f"   ❌ Provisioning failed: {e}")
    
    def _find_role_by_name(self, role_name: str) -> Optional[RoleDefinition]:
        """Find role by name"""
        for role in self.roles.values():
            if role.role_name == role_name:
                return role
        return None
    
    def detect_sod_conflicts(
        self,
        identity_id: str,
        current_roles: List[str],
        new_role: str
    ) -> List[SoDConflict]:
        """
        Detect segregation of duties conflicts
        
        Args:
            identity_id: Identity to check
            current_roles: Currently assigned roles
            new_role: New role being added
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        new_role_def = self._find_role_by_name(new_role)
        if not new_role_def:
            return conflicts
        
        print(f"\n🔍 Checking SoD conflicts for: {new_role}")
        print(f"   Current roles: {', '.join(current_roles)}")
        
        # Check if new role conflicts with existing roles
        for current_role in current_roles:
            current_role_def = self._find_role_by_name(current_role)
            if not current_role_def:
                continue
            
            # Check both directions
            if (new_role in current_role_def.conflicts_with or
                current_role in new_role_def.conflicts_with):
                
                conflict_id = f"SOD-{len(self.sod_conflicts)+1:04d}"
                
                conflict = SoDConflict(
                    conflict_id=conflict_id,
                    identity_id=identity_id,
                    role1=current_role,
                    role2=new_role,
                    severity="high",
                    description=f"Conflicting roles: {current_role} and {new_role}"
                )
                
                conflicts.append(conflict)
                self.sod_conflicts.append(conflict)
                
                print(f"   ⚠️  SoD Conflict: {current_role} ↔ {new_role}")
        
        if not conflicts:
            print(f"   ✅ No conflicts detected")
        
        return conflicts
    
    def mine_roles(
        self,
        identities_data: List[Dict[str, Any]]
    ) -> List[RoleDefinition]:
        """
        Mine roles from existing permissions (role mining)
        
        Args:
            identities_data: Identity and permission data
            
        Returns:
            Discovered role definitions
        """
        print(f"\n⛏️  Mining roles from {len(identities_data)} identities")
        
        # Group identities by permission sets
        permission_groups: Dict[str, List[str]] = {}
        
        for identity in identities_data:
            permissions = tuple(sorted(identity.get('permissions', [])))
            if permissions:
                key = str(hash(permissions))
                if key not in permission_groups:
                    permission_groups[key] = []
                permission_groups[key].append(identity.get('username', 'unknown'))
        
        # Create role definitions for common patterns
        mined_roles = []
        
        for idx, (perm_hash, members) in enumerate(permission_groups.items()):
            if len(members) >= 3:  # At least 3 users with same permissions
                role_id = f"MINED-{idx+1:03d}"
                role_name = f"discovered_role_{idx+1}"
                
                # Get permissions from first member
                sample_identity = next(
                    i for i in identities_data
                    if i.get('username') == members[0]
                )
                permissions = sample_identity.get('permissions', [])
                
                role = RoleDefinition(
                    role_id=role_id,
                    role_name=role_name,
                    description=f"Discovered role with {len(permissions)} permissions",
                    permissions=permissions,
                    risk_level="medium"
                )
                
                mined_roles.append(role)
                
                print(f"   📋 Discovered: {role_name}")
                print(f"      Members: {len(members)}")
                print(f"      Permissions: {len(permissions)}")
        
        print(f"\n   ✅ Mined {len(mined_roles)} role definitions")
        return mined_roles
    
    def enforce_access_policy(
        self,
        identity: Dict[str, Any],
        resource: str,
        action: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Enforce access policies
        
        Args:
            identity: Identity attributes
            resource: Resource being accessed
            action: Action being performed
            context: Request context
            
        Returns:
            True if access allowed
        """
        print(f"\n🛡️  Enforcing access policies")
        print(f"   Identity: {identity.get('username')}")
        print(f"   Resource: {resource}")
        print(f"   Action: {action}")
        
        # Sort policies by priority
        sorted_policies = sorted(
            [p for p in self.policies.values() if p.enabled],
            key=lambda p: p.priority
        )
        
        allow = False
        
        for policy in sorted_policies:
            # Check if policy applies
            if not self._policy_applies(policy, identity, resource):
                continue
            
            print(f"   📜 Evaluating: {policy.policy_name}")
            
            # Check conditions
            if not self._check_policy_conditions(policy, context):
                print(f"      ❌ Conditions not met")
                continue
            
            # Check actions
            if action in policy.deny_actions:
                print(f"      🚫 Action denied by policy")
                return False
            
            if action in policy.allow_actions:
                print(f"      ✅ Action allowed by policy")
                allow = True
        
        if allow:
            print(f"   ✅ Access ALLOWED")
        else:
            print(f"   🚫 Access DENIED")
        
        return allow
    
    def _policy_applies(
        self,
        policy: AccessPolicy,
        identity: Dict[str, Any],
        resource: str
    ) -> bool:
        """Check if policy applies to identity/resource"""
        # Check if identity has applicable role/group
        identity_roles = identity.get('roles', [])
        identity_groups = identity.get('groups', [])
        
        if policy.applies_to:
            has_applicable = any(
                role in policy.applies_to or group in policy.applies_to
                for role in identity_roles
                for group in identity_groups
            )
            if not has_applicable:
                return False
        
        # Check if resource is in scope
        if policy.resources and resource not in policy.resources:
            return False
        
        return True
    
    def _check_policy_conditions(
        self,
        policy: AccessPolicy,
        context: Dict[str, Any]
    ) -> bool:
        """Check if policy conditions are met"""
        if not policy.conditions:
            return True
        
        # Time-based
        if 'hour_range' in policy.conditions:
            hour = datetime.now().hour
            hour_range = policy.conditions['hour_range']
            if not (hour_range[0] <= hour <= hour_range[1]):
                return False
        
        # Location-based
        if 'allowed_locations' in policy.conditions:
            location = context.get('location')
            if location not in policy.conditions['allowed_locations']:
                return False
        
        # Risk-based
        if 'risk_level' in policy.conditions:
            identity_risk = context.get('risk_level')
            if identity_risk in policy.conditions['risk_level']:
                return True
        
        return True
    
    def generate_governance_report(self) -> Dict[str, Any]:
        """Generate identity governance report"""
        return {
            'roles': {
                'total': len(self.roles),
                'by_risk': {
                    'low': sum(1 for r in self.roles.values() if r.risk_level == 'low'),
                    'medium': sum(1 for r in self.roles.values() if r.risk_level == 'medium'),
                    'high': sum(1 for r in self.roles.values() if r.risk_level == 'high'),
                    'critical': sum(1 for r in self.roles.values() if r.risk_level == 'critical')
                }
            },
            'provisioning': {
                'total_requests': len(self.provisioning_requests),
                'pending': sum(1 for r in self.provisioning_requests if r.status == 'pending'),
                'completed': sum(1 for r in self.provisioning_requests if r.status == 'completed'),
                'failed': sum(1 for r in self.provisioning_requests if r.status == 'failed')
            },
            'sod_conflicts': {
                'total': len(self.sod_conflicts),
                'open': sum(1 for c in self.sod_conflicts if c.remediation_status == 'open'),
                'remediated': sum(1 for c in self.sod_conflicts if c.remediation_status == 'remediated')
            },
            'policies': {
                'total': len(self.policies),
                'enabled': sum(1 for p in self.policies.values() if p.enabled)
            }
        }


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("IDENTITY GOVERNANCE & LIFECYCLE MANAGEMENT")
    print("="*70)
    
    # Initialize engine
    engine = IdentityGovernanceEngine()
    
    # Provision new identity
    print("\n" + "="*70)
    print("IDENTITY PROVISIONING")
    print("="*70)
    
    provision_request = engine.provision_identity(
        username="alice.johnson",
        attributes={
            "email": "alice.johnson@company.com",
            "department": "Engineering",
            "manager": "bob.smith@company.com",
            "title": "Senior Developer"
        },
        roles=["employee", "developer"],
        requested_by="hr@company.com"
    )
    
    # Check SoD conflicts
    print("\n" + "="*70)
    print("SEGREGATION OF DUTIES CHECK")
    print("="*70)
    
    conflicts = engine.detect_sod_conflicts(
        "USER-001",
        current_roles=["developer"],
        new_role="prod_admin"
    )
    
    # Role mining
    print("\n" + "="*70)
    print("ROLE MINING")
    print("="*70)
    
    sample_identities = [
        {
            'username': 'dev1',
            'permissions': ['read_code', 'write_code', 'submit_pr']
        },
        {
            'username': 'dev2',
            'permissions': ['read_code', 'write_code', 'submit_pr']
        },
        {
            'username': 'dev3',
            'permissions': ['read_code', 'write_code', 'submit_pr']
        }
    ]
    
    mined_roles = engine.mine_roles(sample_identities)
    
    # Policy enforcement
    print("\n" + "="*70)
    print("ACCESS POLICY ENFORCEMENT")
    print("="*70)
    
    allowed = engine.enforce_access_policy(
        identity={
            'username': 'alice.johnson',
            'roles': ['employee', 'developer'],
            'groups': ['engineering']
        },
        resource='code_repository',
        action='write',
        context={
            'location': 'office',
            'device_managed': True
        }
    )
    
    # Deprovisioning
    print("\n" + "="*70)
    print("IDENTITY DEPROVISIONING")
    print("="*70)
    
    deprovision_request = engine.deprovision_identity(
        "USER-999",
        reason="Employee termination",
        requested_by="hr@company.com"
    )
    
    # Generate report
    print("\n" + "="*70)
    print("GOVERNANCE REPORT")
    print("="*70)
    
    report = engine.generate_governance_report()
    print(json.dumps(report, indent=2))
