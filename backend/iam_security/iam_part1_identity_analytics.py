"""
Military Upgrade #33: Enhanced IAM Security - Part 1
Identity Analytics & Privilege Management

This module provides advanced identity-centric security:
- Privilege analytics and anomaly detection
- Access certification automation
- Identity governance & administration (IGA)
- Privileged access management (PAM)
- Zero trust identity verification
- Just-in-time (JIT) access provisioning
- Standing privilege elimination
- Identity lifecycle management

Key Capabilities:
- Real-time privilege escalation detection
- Dormant account identification
- Excessive permissions analysis
- Segregation of duties (SoD) violations
- Access review automation
- Role-based access control (RBAC) optimization
- Attribute-based access control (ABAC)
- Risk-based authentication

Compliance:
- NIST 800-53 AC-2 (Account Management)
- NIST 800-53 AC-6 (Least Privilege)
- PCI DSS 7.1 (Access Control)
- PCI DSS 8.2 (User Authentication)
- SOX (Segregation of Duties)
- HIPAA (Access Controls)
- GDPR Article 32 (Security of Processing)

Author: Enterprise Scanner Team
Version: 1.0.0 (October 17, 2025)
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import random


class IdentityType(Enum):
    """Identity types in the system"""
    HUMAN_USER = "human_user"
    SERVICE_ACCOUNT = "service_account"
    APPLICATION = "application"
    DEVICE = "device"
    API_KEY = "api_key"
    FEDERATED = "federated"


class AccessLevel(Enum):
    """Access privilege levels"""
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3
    SUPER_ADMIN = 4


class RiskLevel(Enum):
    """Identity risk levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AccessDecision(Enum):
    """Zero trust access decisions"""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"  # Require additional authentication
    MONITOR = "monitor"      # Allow but log extensively


@dataclass
class Identity:
    """Identity object"""
    identity_id: str
    identity_type: IdentityType
    username: str
    display_name: str
    
    # Status
    enabled: bool = True
    locked: bool = False
    password_expired: bool = False
    
    # Attributes
    email: Optional[str] = None
    department: Optional[str] = None
    manager: Optional[str] = None
    cost_center: Optional[str] = None
    
    # Lifecycle
    created_date: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    last_password_change: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    
    # Risk
    risk_score: float = 0.0  # 0-100
    risk_level: RiskLevel = RiskLevel.LOW
    
    # Permissions
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    last_modified: datetime = field(default_factory=datetime.now)


@dataclass
class AccessRequest:
    """Access request for approval workflow"""
    request_id: str
    identity_id: str
    resource: str
    access_level: AccessLevel
    
    # Request details
    justification: str
    requested_by: str
    requested_at: datetime = field(default_factory=datetime.now)
    
    # Approval
    status: str = "pending"  # pending, approved, denied, expired
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    expiration: Optional[datetime] = None
    
    # Duration
    temporary: bool = False
    duration_hours: Optional[int] = None


@dataclass
class PrivilegeAnalysis:
    """Privilege analysis results"""
    identity_id: str
    analysis_date: datetime
    
    # Findings
    excessive_permissions: List[str] = field(default_factory=list)
    dormant_access: List[str] = field(default_factory=list)
    sod_violations: List[str] = field(default_factory=list)
    orphaned_accounts: bool = False
    
    # Metrics
    total_permissions: int = 0
    used_permissions: int = 0
    unused_permissions: int = 0
    days_since_login: int = 0
    
    # Risk
    privilege_risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AccessCertification:
    """Access certification campaign"""
    campaign_id: str
    campaign_name: str
    certifier: str  # Manager or reviewer
    
    # Scope
    identities: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    
    # Timeline
    start_date: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    completed_date: Optional[datetime] = None
    
    # Progress
    total_items: int = 0
    certified_items: int = 0
    revoked_items: int = 0
    pending_items: int = 0
    
    # Status
    status: str = "active"  # active, completed, expired


class IdentityAnalyticsEngine:
    """
    Advanced identity analytics and privilege management
    """
    
    def __init__(self):
        """Initialize identity analytics engine"""
        self.identities: Dict[str, Identity] = {}
        self.access_requests: List[AccessRequest] = []
        self.certifications: List[AccessCertification] = []
        self.privilege_analyses: List[PrivilegeAnalysis] = []
        
        # Policies
        self.max_privilege_duration_days = 90
        self.dormant_account_threshold_days = 90
        self.password_expiry_days = 90
        
        # Statistics
        self.stats = {
            'total_identities': 0,
            'high_risk_identities': 0,
            'dormant_accounts': 0,
            'excessive_permissions': 0,
            'sod_violations': 0
        }
    
    def analyze_identity_risk(self, identity_id: str) -> float:
        """
        Analyze identity risk score based on multiple factors
        
        Args:
            identity_id: Identity to analyze
            
        Returns:
            Risk score (0-100)
        """
        identity = self.identities.get(identity_id)
        if not identity:
            return 0.0
        
        risk_score = 0.0
        
        # Factor 1: Privilege level (40 points)
        privilege_score = self._calculate_privilege_score(identity)
        risk_score += privilege_score * 0.4
        
        # Factor 2: Account activity (20 points)
        activity_score = self._calculate_activity_score(identity)
        risk_score += activity_score * 0.2
        
        # Factor 3: Access patterns (20 points)
        pattern_score = self._calculate_pattern_score(identity)
        risk_score += pattern_score * 0.2
        
        # Factor 4: Compliance violations (20 points)
        compliance_score = self._calculate_compliance_score(identity)
        risk_score += compliance_score * 0.2
        
        # Update identity
        identity.risk_score = risk_score
        identity.risk_level = self._score_to_risk_level(risk_score)
        
        return risk_score
    
    def _calculate_privilege_score(self, identity: Identity) -> float:
        """Calculate score based on privilege level"""
        score = 0.0
        
        # Check for administrative roles
        admin_keywords = ['admin', 'root', 'superuser', 'privileged']
        has_admin = any(
            keyword in role.lower()
            for role in identity.roles
            for keyword in admin_keywords
        )
        
        if has_admin:
            score += 60
        
        # Number of permissions
        if len(identity.permissions) > 50:
            score += 30
        elif len(identity.permissions) > 20:
            score += 20
        elif len(identity.permissions) > 10:
            score += 10
        
        # Service accounts are higher risk if compromised
        if identity.identity_type == IdentityType.SERVICE_ACCOUNT:
            score += 10
        
        return min(score, 100)
    
    def _calculate_activity_score(self, identity: Identity) -> float:
        """Calculate score based on account activity"""
        score = 0.0
        
        if identity.last_login:
            days_since_login = (datetime.now() - identity.last_login).days
            
            # Dormant accounts
            if days_since_login > 180:
                score += 70
            elif days_since_login > 90:
                score += 50
            elif days_since_login > 30:
                score += 30
        else:
            # Never logged in
            score += 80
        
        # Password age
        if identity.last_password_change:
            days_since_password = (datetime.now() - identity.last_password_change).days
            if days_since_password > 180:
                score += 20
        
        return min(score, 100)
    
    def _calculate_pattern_score(self, identity: Identity) -> float:
        """Calculate score based on access patterns (simulated)"""
        # In production, would analyze:
        # - Login times (unusual hours)
        # - Login locations (unusual geography)
        # - Access patterns (unusual resources)
        # - Failed authentication attempts
        
        score = random.uniform(0, 40)  # Simulated anomaly score
        return score
    
    def _calculate_compliance_score(self, identity: Identity) -> float:
        """Calculate score based on compliance violations"""
        score = 0.0
        
        # Check for violations (simulated)
        violations = random.randint(0, 3)
        score = violations * 25  # 25 points per violation
        
        return min(score, 100)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score >= 75:
            return RiskLevel.CRITICAL
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def identify_excessive_privileges(
        self,
        identity_id: str,
        lookback_days: int = 90
    ) -> PrivilegeAnalysis:
        """
        Identify excessive or unused privileges
        
        Args:
            identity_id: Identity to analyze
            lookback_days: Analysis period
            
        Returns:
            Privilege analysis results
        """
        identity = self.identities.get(identity_id)
        if not identity:
            return None
        
        print(f"\n🔍 Analyzing privileges for: {identity.username}")
        
        analysis = PrivilegeAnalysis(
            identity_id=identity_id,
            analysis_date=datetime.now()
        )
        
        # Simulate usage analysis (in production, analyze audit logs)
        total_perms = len(identity.permissions)
        used_perms = random.randint(int(total_perms * 0.3), int(total_perms * 0.7))
        unused_perms = total_perms - used_perms
        
        analysis.total_permissions = total_perms
        analysis.used_permissions = used_perms
        analysis.unused_permissions = unused_perms
        
        # Identify excessive permissions
        if unused_perms > total_perms * 0.3:  # >30% unused
            analysis.excessive_permissions = identity.permissions[:unused_perms]
        
        # Check for dormant access
        if identity.last_login:
            days_since_login = (datetime.now() - identity.last_login).days
            analysis.days_since_login = days_since_login
            
            if days_since_login > self.dormant_account_threshold_days:
                analysis.dormant_access = identity.roles
        
        # Check for SoD violations (simulated)
        high_risk_combos = [
            ('developer', 'production_admin'),
            ('finance', 'payment_processor'),
            ('auditor', 'system_admin')
        ]
        
        for role1, role2 in high_risk_combos:
            if any(role1 in r.lower() for r in identity.roles) and \
               any(role2 in r.lower() for r in identity.roles):
                analysis.sod_violations.append(f"{role1} + {role2}")
        
        # Check for orphaned accounts
        if not identity.manager:
            analysis.orphaned_accounts = True
        
        # Calculate privilege risk
        risk_factors = [
            unused_perms / total_perms if total_perms > 0 else 0,
            1.0 if analysis.dormant_access else 0,
            len(analysis.sod_violations) * 0.3,
            1.0 if analysis.orphaned_accounts else 0
        ]
        analysis.privilege_risk_score = sum(risk_factors) / len(risk_factors) * 100
        
        # Generate recommendations
        if analysis.excessive_permissions:
            analysis.recommendations.append(
                f"Revoke {len(analysis.excessive_permissions)} unused permissions"
            )
        if analysis.dormant_access:
            analysis.recommendations.append(
                f"Disable dormant account (inactive {analysis.days_since_login} days)"
            )
        if analysis.sod_violations:
            analysis.recommendations.append(
                f"Remediate {len(analysis.sod_violations)} SoD violations"
            )
        if analysis.orphaned_accounts:
            analysis.recommendations.append(
                "Assign account owner/manager"
            )
        
        self.privilege_analyses.append(analysis)
        
        print(f"   Total Permissions: {analysis.total_permissions}")
        print(f"   Used: {analysis.used_permissions}, Unused: {analysis.unused_permissions}")
        print(f"   Excessive: {len(analysis.excessive_permissions)}")
        print(f"   SoD Violations: {len(analysis.sod_violations)}")
        print(f"   Risk Score: {analysis.privilege_risk_score:.1f}/100")
        
        return analysis
    
    def create_access_certification(
        self,
        campaign_name: str,
        certifier: str,
        identities: List[str],
        duration_days: int = 30
    ) -> AccessCertification:
        """
        Create access certification campaign
        
        Args:
            campaign_name: Campaign name
            certifier: Reviewer (usually manager)
            identities: Identities to certify
            duration_days: Days to complete certification
            
        Returns:
            Certification campaign
        """
        campaign_id = f"CERT-{len(self.certifications)+1:04d}"
        
        certification = AccessCertification(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            certifier=certifier,
            identities=identities,
            due_date=datetime.now() + timedelta(days=duration_days)
        )
        
        # Calculate scope
        total_items = 0
        for identity_id in identities:
            identity = self.identities.get(identity_id)
            if identity:
                total_items += len(identity.permissions)
                total_items += len(identity.roles)
        
        certification.total_items = total_items
        certification.pending_items = total_items
        
        self.certifications.append(certification)
        
        print(f"\n📋 Created Certification Campaign: {campaign_id}")
        print(f"   Name: {campaign_name}")
        print(f"   Certifier: {certifier}")
        print(f"   Identities: {len(identities)}")
        print(f"   Items to Certify: {total_items}")
        print(f"   Due Date: {certification.due_date.strftime('%Y-%m-%d')}")
        
        return certification
    
    def request_just_in_time_access(
        self,
        identity_id: str,
        resource: str,
        access_level: AccessLevel,
        justification: str,
        duration_hours: int = 8
    ) -> AccessRequest:
        """
        Request just-in-time privileged access
        
        Args:
            identity_id: Requesting identity
            resource: Resource to access
            access_level: Requested access level
            justification: Business justification
            duration_hours: Access duration
            
        Returns:
            Access request
        """
        request_id = f"REQ-{len(self.access_requests)+1:06d}"
        
        identity = self.identities.get(identity_id)
        if not identity:
            print(f"❌ Identity not found: {identity_id}")
            return None
        
        request = AccessRequest(
            request_id=request_id,
            identity_id=identity_id,
            resource=resource,
            access_level=access_level,
            justification=justification,
            requested_by=identity.username,
            temporary=True,
            duration_hours=duration_hours,
            expiration=datetime.now() + timedelta(hours=duration_hours)
        )
        
        # Auto-approve based on risk (in production, would route to approver)
        risk_score = self.analyze_identity_risk(identity_id)
        
        if risk_score < 30 and access_level.value <= AccessLevel.WRITE.value:
            # Low risk, low privilege - auto-approve
            request.status = "approved"
            request.approved_by = "auto_approved"
            request.approved_at = datetime.now()
            print(f"   ✅ Auto-approved (low risk)")
        else:
            # Requires manual approval
            request.status = "pending"
            print(f"   ⏳ Pending approval (risk: {risk_score:.1f})")
        
        self.access_requests.append(request)
        
        print(f"\n🎫 JIT Access Request: {request_id}")
        print(f"   User: {identity.username}")
        print(f"   Resource: {resource}")
        print(f"   Level: {access_level.name}")
        print(f"   Duration: {duration_hours} hours")
        print(f"   Status: {request.status}")
        
        return request
    
    def evaluate_zero_trust_access(
        self,
        identity_id: str,
        resource: str,
        context: Dict[str, Any]
    ) -> AccessDecision:
        """
        Evaluate access request using zero trust principles
        
        Args:
            identity_id: Requesting identity
            resource: Resource being accessed
            context: Contextual information (IP, device, time, etc.)
            
        Returns:
            Access decision
        """
        identity = self.identities.get(identity_id)
        if not identity:
            return AccessDecision.DENY
        
        print(f"\n🛡️  Zero Trust Evaluation")
        print(f"   Identity: {identity.username}")
        print(f"   Resource: {resource}")
        
        # Calculate risk score
        risk_score = self.analyze_identity_risk(identity_id)
        
        # Check context
        context_risk = 0
        
        # Unusual time
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            context_risk += 20
            print(f"   ⚠️  Unusual time: {hour}:00")
        
        # Unusual location (simulated)
        if context.get('location') and context['location'] != 'corporate_network':
            context_risk += 30
            print(f"   ⚠️  External location: {context.get('location')}")
        
        # Unmanaged device
        if not context.get('device_managed'):
            context_risk += 25
            print(f"   ⚠️  Unmanaged device")
        
        # Total risk
        total_risk = (risk_score + context_risk) / 2
        
        print(f"   📊 Identity Risk: {risk_score:.1f}")
        print(f"   📊 Context Risk: {context_risk:.1f}")
        print(f"   📊 Total Risk: {total_risk:.1f}")
        
        # Make decision
        if total_risk >= 70:
            decision = AccessDecision.DENY
            print(f"   🚫 Decision: DENY (high risk)")
        elif total_risk >= 50:
            decision = AccessDecision.CHALLENGE
            print(f"   🔐 Decision: CHALLENGE (requires MFA)")
        elif total_risk >= 30:
            decision = AccessDecision.MONITOR
            print(f"   👁️  Decision: MONITOR (allow with logging)")
        else:
            decision = AccessDecision.ALLOW
            print(f"   ✅ Decision: ALLOW")
        
        return decision
    
    def generate_identity_report(self) -> Dict[str, Any]:
        """Generate comprehensive identity analytics report"""
        # Update statistics
        self.stats['total_identities'] = len(self.identities)
        self.stats['high_risk_identities'] = sum(
            1 for i in self.identities.values()
            if i.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        # Count dormant accounts
        dormant = 0
        for identity in self.identities.values():
            if identity.last_login:
                days_since = (datetime.now() - identity.last_login).days
                if days_since > self.dormant_account_threshold_days:
                    dormant += 1
        self.stats['dormant_accounts'] = dormant
        
        # Count excessive permissions
        excessive = sum(
            len(a.excessive_permissions)
            for a in self.privilege_analyses
        )
        self.stats['excessive_permissions'] = excessive
        
        # Count SoD violations
        sod_violations = sum(
            len(a.sod_violations)
            for a in self.privilege_analyses
        )
        self.stats['sod_violations'] = sod_violations
        
        return {
            'summary': self.stats,
            'high_risk_identities': [
                {
                    'id': i.identity_id,
                    'username': i.username,
                    'risk_score': i.risk_score,
                    'risk_level': i.risk_level.name
                }
                for i in self.identities.values()
                if i.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            ][:10],
            'privilege_analyses': [
                {
                    'identity_id': a.identity_id,
                    'unused_permissions': a.unused_permissions,
                    'sod_violations': len(a.sod_violations),
                    'risk_score': a.privilege_risk_score
                }
                for a in self.privilege_analyses
            ][:10],
            'access_requests': [
                {
                    'request_id': r.request_id,
                    'identity': r.requested_by,
                    'resource': r.resource,
                    'status': r.status
                }
                for r in self.access_requests[-10:]
            ]
        }


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("IDENTITY ANALYTICS & PRIVILEGE MANAGEMENT")
    print("="*70)
    
    # Initialize engine
    engine = IdentityAnalyticsEngine()
    
    # Create sample identities
    identities = [
        Identity(
            identity_id="USER-001",
            identity_type=IdentityType.HUMAN_USER,
            username="john.doe",
            display_name="John Doe",
            email="john.doe@company.com",
            department="Engineering",
            manager="jane.smith",
            roles=["developer", "prod_admin"],
            permissions=["read_code", "write_code", "deploy_prod", "db_admin"],
            last_login=datetime.now() - timedelta(days=2)
        ),
        Identity(
            identity_id="SVC-001",
            identity_type=IdentityType.SERVICE_ACCOUNT,
            username="backup_service",
            display_name="Backup Service Account",
            department="IT",
            roles=["backup_admin", "system_admin"],
            permissions=["read_all", "backup_create", "system_access"],
            last_login=datetime.now() - timedelta(days=150)  # Dormant
        )
    ]
    
    for identity in identities:
        engine.identities[identity.identity_id] = identity
    
    # Analyze identity risk
    print("\n" + "="*70)
    print("IDENTITY RISK ANALYSIS")
    print("="*70)
    
    for identity_id in engine.identities:
        risk_score = engine.analyze_identity_risk(identity_id)
        identity = engine.identities[identity_id]
        print(f"\n{identity.username}: {risk_score:.1f}/100 ({identity.risk_level.name})")
    
    # Privilege analysis
    print("\n" + "="*70)
    print("PRIVILEGE ANALYSIS")
    print("="*70)
    
    for identity_id in engine.identities:
        engine.identify_excessive_privileges(identity_id)
    
    # Access certification
    print("\n" + "="*70)
    print("ACCESS CERTIFICATION")
    print("="*70)
    
    certification = engine.create_access_certification(
        "Q1 2025 Access Review",
        "jane.smith@company.com",
        list(engine.identities.keys()),
        duration_days=30
    )
    
    # JIT access request
    print("\n" + "="*70)
    print("JUST-IN-TIME ACCESS")
    print("="*70)
    
    jit_request = engine.request_just_in_time_access(
        "USER-001",
        "production_database",
        AccessLevel.ADMIN,
        "Emergency database recovery",
        duration_hours=4
    )
    
    # Zero trust evaluation
    print("\n" + "="*70)
    print("ZERO TRUST ACCESS EVALUATION")
    print("="*70)
    
    decision = engine.evaluate_zero_trust_access(
        "USER-001",
        "financial_reports",
        {
            'location': 'remote',
            'device_managed': False,
            'ip_address': '203.0.113.42'
        }
    )
    
    # Generate report
    print("\n" + "="*70)
    print("IDENTITY ANALYTICS REPORT")
    print("="*70)
    
    report = engine.generate_identity_report()
    print(json.dumps(report, indent=2, default=str))
