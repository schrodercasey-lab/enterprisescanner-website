"""
Military-Grade Zero-Trust Architecture - Part 2 of 5
===================================================

BeyondCorp Identity-Based Access Control

Features:
- Identity-centric access control
- Device trust verification
- Context-aware authorization
- User and device posture assessment
- Continuous authentication

COMPLIANCE:
- NIST 800-207 (Zero Trust Architecture)
- BeyondCorp Principles (Google)
- DoD Zero Trust Reference Architecture
- CMMC AC.L3-3.1.2 (Identity Management)
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib


class IdentityType(Enum):
    """Identity types"""
    USER = "User"
    SERVICE_ACCOUNT = "Service Account"
    DEVICE = "Device"
    WORKLOAD = "Workload"


class TrustLevel(Enum):
    """Trust levels"""
    UNTRUSTED = 0
    LOW = 25
    MEDIUM = 50
    HIGH = 75
    FULL = 100


class DevicePosture(Enum):
    """Device security posture"""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    UNKNOWN = "Unknown"


class AuthenticationMethod(Enum):
    """Authentication methods"""
    PASSWORD = "Password"
    MFA = "Multi-Factor Authentication"
    CERTIFICATE = "Certificate"
    BIOMETRIC = "Biometric"
    HARDWARE_TOKEN = "Hardware Token"


@dataclass
class Identity:
    """Identity object"""
    identity_id: str
    identity_type: IdentityType
    username: str
    email: Optional[str]
    groups: List[str]
    roles: List[str]
    trust_level: TrustLevel
    created_at: datetime
    last_authenticated: Optional[datetime]


@dataclass
class Device:
    """Device object"""
    device_id: str
    device_name: str
    device_type: str  # laptop, mobile, server
    os_version: str
    patch_level: str
    encryption_enabled: bool
    antivirus_status: bool
    firewall_enabled: bool
    managed: bool
    posture: DevicePosture
    last_scan: datetime


@dataclass
class AccessContext:
    """Access request context"""
    identity: Identity
    device: Device
    source_ip: str
    location: str
    time: datetime
    resource: str
    action: str
    risk_score: float


@dataclass
class AccessPolicy:
    """Identity-based access policy"""
    policy_id: str
    name: str
    required_trust_level: TrustLevel
    required_groups: List[str]
    required_device_posture: DevicePosture
    requires_mfa: bool
    allowed_locations: Optional[List[str]]
    allowed_ip_ranges: Optional[List[str]]
    time_restrictions: Optional[Dict[str, Any]]


class BeyondCorpEngine:
    """BeyondCorp Identity-Based Access Engine - Part 2 of Zero-Trust"""
    
    def __init__(self):
        self.identities: Dict[str, Identity] = {}
        self.devices: Dict[str, Device] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.access_logs: List[Dict[str, Any]] = []
    
    def register_identity(self, identity: Identity) -> bool:
        """Register new identity"""
        print(f"👤 Registering identity: {identity.username}")
        
        # Validate identity
        if not identity.username or not identity.identity_id:
            print(f"❌ Invalid identity data")
            return False
        
        # Check for duplicate
        if identity.identity_id in self.identities:
            print(f"❌ Identity already exists: {identity.identity_id}")
            return False
        
        self.identities[identity.identity_id] = identity
        print(f"✅ Identity registered: {identity.username}")
        return True
    
    def register_device(self, device: Device) -> bool:
        """Register device"""
        print(f"💻 Registering device: {device.device_name}")
        
        # Validate device
        if not device.device_id or not device.device_name:
            print(f"❌ Invalid device data")
            return False
        
        # Assess device posture
        device.posture = self._assess_device_posture(device)
        
        self.devices[device.device_id] = device
        print(f"✅ Device registered: {device.device_name} (Posture: {device.posture.value})")
        return True
    
    def authenticate_identity(self, identity_id: str, 
                            auth_method: AuthenticationMethod,
                            credentials: Dict[str, Any]) -> bool:
        """Authenticate identity"""
        print(f"🔐 Authenticating identity: {identity_id}")
        
        if identity_id not in self.identities:
            print(f"❌ Identity not found: {identity_id}")
            return False
        
        identity = self.identities[identity_id]
        
        # Verify credentials (simulated)
        if not self._verify_credentials(credentials, auth_method):
            print(f"❌ Authentication failed: Invalid credentials")
            return False
        
        # Update last authenticated time
        identity.last_authenticated = datetime.now()
        
        # Adjust trust level based on auth method
        if auth_method in [AuthenticationMethod.MFA, 
                          AuthenticationMethod.CERTIFICATE,
                          AuthenticationMethod.HARDWARE_TOKEN]:
            identity.trust_level = TrustLevel.HIGH
        elif auth_method == AuthenticationMethod.BIOMETRIC:
            identity.trust_level = TrustLevel.FULL
        else:
            identity.trust_level = TrustLevel.MEDIUM
        
        print(f"✅ Authentication successful (Trust: {identity.trust_level.value})")
        return True
    
    def evaluate_access_request(self, context: AccessContext, 
                               policy: AccessPolicy) -> Dict[str, Any]:
        """Evaluate access request against policy"""
        print(f"🔍 Evaluating access: {context.identity.username} -> {context.resource}")
        
        denial_reasons = []
        
        # Check 1: Trust level
        if context.identity.trust_level.value < policy.required_trust_level.value:
            denial_reasons.append(
                f"Insufficient trust level: {context.identity.trust_level.value} < "
                f"{policy.required_trust_level.value}"
            )
        
        # Check 2: Group membership
        if policy.required_groups:
            if not any(group in context.identity.groups for group in policy.required_groups):
                denial_reasons.append(
                    f"Not member of required groups: {policy.required_groups}"
                )
        
        # Check 3: Device posture
        if context.device.posture != policy.required_device_posture:
            denial_reasons.append(
                f"Device posture mismatch: {context.device.posture.value} != "
                f"{policy.required_device_posture.value}"
            )
        
        # Check 4: MFA requirement
        if policy.requires_mfa:
            if context.identity.trust_level.value < TrustLevel.HIGH.value:
                denial_reasons.append("MFA required but not used")
        
        # Check 5: Location restrictions
        if policy.allowed_locations:
            if context.location not in policy.allowed_locations:
                denial_reasons.append(
                    f"Location not allowed: {context.location}"
                )
        
        # Check 6: Time restrictions
        if policy.time_restrictions:
            if not self._check_time_restrictions(context.time, policy.time_restrictions):
                denial_reasons.append("Access outside allowed time window")
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(context)
        
        # Make decision
        if denial_reasons:
            result = {
                "allowed": False,
                "reasons": denial_reasons,
                "risk_score": risk_score,
                "timestamp": datetime.now()
            }
            print(f"  ❌ Access DENIED: {len(denial_reasons)} violations")
        else:
            result = {
                "allowed": True,
                "risk_score": risk_score,
                "timestamp": datetime.now()
            }
            print(f"  ✅ Access GRANTED (Risk: {risk_score:.2f})")
        
        # Log access attempt
        self._log_access_attempt(context, result)
        
        return result
    
    def continuous_verification(self, identity_id: str, device_id: str) -> Dict[str, Any]:
        """Perform continuous verification of identity and device"""
        print(f"🔄 Continuous verification: {identity_id} on {device_id}")
        
        if identity_id not in self.identities:
            return {"verified": False, "reason": "Identity not found"}
        
        if device_id not in self.devices:
            return {"verified": False, "reason": "Device not found"}
        
        identity = self.identities[identity_id]
        device = self.devices[device_id]
        
        issues = []
        
        # Check 1: Session age
        if identity.last_authenticated:
            session_age = (datetime.now() - identity.last_authenticated).total_seconds()
            if session_age > 3600:  # 1 hour
                issues.append("Session expired - re-authentication required")
        
        # Check 2: Device posture drift
        current_posture = self._assess_device_posture(device)
        if current_posture != device.posture:
            issues.append(f"Device posture changed: {device.posture.value} -> {current_posture.value}")
            device.posture = current_posture
        
        # Check 3: Trust level degradation
        if identity.trust_level.value < TrustLevel.MEDIUM.value:
            issues.append("Trust level below acceptable threshold")
        
        if issues:
            print(f"  ⚠️  Verification issues: {len(issues)}")
            return {
                "verified": False,
                "issues": issues,
                "requires_reauth": True
            }
        
        print(f"  ✅ Verification passed")
        return {
            "verified": True,
            "trust_level": identity.trust_level.value,
            "device_posture": device.posture.value
        }
    
    def assess_user_behavior(self, identity_id: str) -> Dict[str, Any]:
        """Assess user behavior for anomalies"""
        print(f"📊 Assessing user behavior: {identity_id}")
        
        if identity_id not in self.identities:
            return {"anomalies": [], "risk_score": 0.0}
        
        identity = self.identities[identity_id]
        anomalies = []
        
        # Analyze access logs for this identity
        user_logs = [log for log in self.access_logs 
                    if log.get("identity_id") == identity_id]
        
        if not user_logs:
            return {"anomalies": [], "risk_score": 0.0}
        
        # Check 1: Unusual access times
        access_times = [log["timestamp"].hour for log in user_logs]
        if any(hour < 6 or hour > 22 for hour in access_times):
            anomalies.append("Access during unusual hours")
        
        # Check 2: Multiple failed attempts
        failed_attempts = [log for log in user_logs if not log.get("allowed")]
        if len(failed_attempts) > 5:
            anomalies.append(f"Multiple failed access attempts: {len(failed_attempts)}")
        
        # Check 3: Access from multiple locations
        locations = set(log.get("location") for log in user_logs if log.get("location"))
        if len(locations) > 3:
            anomalies.append(f"Access from {len(locations)} different locations")
        
        # Calculate risk score
        risk_score = len(anomalies) * 0.3
        
        print(f"  📈 Anomalies detected: {len(anomalies)}, Risk: {risk_score:.2f}")
        
        return {
            "anomalies": anomalies,
            "risk_score": risk_score,
            "recommendation": "Require additional authentication" if risk_score > 0.5 else "Normal"
        }
    
    def enforce_least_privilege(self, identity_id: str) -> List[str]:
        """Enforce least privilege access"""
        print(f"🔒 Enforcing least privilege: {identity_id}")
        
        if identity_id not in self.identities:
            return []
        
        identity = self.identities[identity_id]
        recommendations = []
        
        # Analyze access patterns
        user_logs = [log for log in self.access_logs 
                    if log.get("identity_id") == identity_id]
        
        accessed_resources = set(log.get("resource") for log in user_logs 
                               if log.get("allowed"))
        
        # Check for excessive permissions
        if len(identity.roles) > 3:
            recommendations.append(
                f"User has {len(identity.roles)} roles - review for excessive permissions"
            )
        
        # Check for unused permissions
        if len(accessed_resources) < len(identity.roles):
            recommendations.append(
                "Some roles may be unused - consider removing"
            )
        
        # Check for admin-level access
        if "admin" in [role.lower() for role in identity.roles]:
            recommendations.append(
                "Admin role detected - verify necessity"
            )
        
        print(f"  📋 Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _assess_device_posture(self, device: Device) -> DevicePosture:
        """Assess device security posture"""
        compliant_checks = 0
        total_checks = 5
        
        if device.encryption_enabled:
            compliant_checks += 1
        if device.antivirus_status:
            compliant_checks += 1
        if device.firewall_enabled:
            compliant_checks += 1
        if device.managed:
            compliant_checks += 1
        
        # Check patch level (simulated)
        if device.patch_level == "current":
            compliant_checks += 1
        
        if compliant_checks >= 4:
            return DevicePosture.COMPLIANT
        elif compliant_checks >= 2:
            return DevicePosture.NON_COMPLIANT
        else:
            return DevicePosture.UNKNOWN
    
    def _verify_credentials(self, credentials: Dict[str, Any], 
                           method: AuthenticationMethod) -> bool:
        """Verify authentication credentials"""
        # Simulated credential verification
        if method == AuthenticationMethod.PASSWORD:
            return "password" in credentials
        elif method == AuthenticationMethod.MFA:
            return "password" in credentials and "token" in credentials
        elif method == AuthenticationMethod.CERTIFICATE:
            return "certificate" in credentials
        elif method == AuthenticationMethod.BIOMETRIC:
            return "biometric_data" in credentials
        return False
    
    def _calculate_risk_score(self, context: AccessContext) -> float:
        """Calculate risk score for access request"""
        risk = 0.0
        
        # Trust level factor
        risk += (100 - context.identity.trust_level.value) / 100 * 0.3
        
        # Device posture factor
        if context.device.posture == DevicePosture.NON_COMPLIANT:
            risk += 0.4
        elif context.device.posture == DevicePosture.UNKNOWN:
            risk += 0.6
        
        # Time factor (after hours)
        if context.time.hour < 6 or context.time.hour > 20:
            risk += 0.2
        
        return min(1.0, risk)
    
    def _check_time_restrictions(self, access_time: datetime, 
                                restrictions: Dict[str, Any]) -> bool:
        """Check if access time meets restrictions"""
        if "allowed_hours" in restrictions:
            start_hour, end_hour = restrictions["allowed_hours"]
            if not start_hour <= access_time.hour <= end_hour:
                return False
        
        if "allowed_days" in restrictions:
            if access_time.weekday() not in restrictions["allowed_days"]:
                return False
        
        return True
    
    def _log_access_attempt(self, context: AccessContext, result: Dict[str, Any]):
        """Log access attempt"""
        self.access_logs.append({
            "identity_id": context.identity.identity_id,
            "username": context.identity.username,
            "device_id": context.device.device_id,
            "resource": context.resource,
            "action": context.action,
            "allowed": result["allowed"],
            "risk_score": result["risk_score"],
            "timestamp": context.time,
            "location": context.location
        })


def main():
    """Test BeyondCorp engine"""
    engine = BeyondCorpEngine()
    
    print("=" * 70)
    print("BEYONDCORP IDENTITY-BASED ACCESS CONTROL")
    print("=" * 70)
    
    # Register identity
    identity = Identity(
        identity_id="user-001",
        identity_type=IdentityType.USER,
        username="alice",
        email="alice@company.com",
        groups=["engineering", "developers"],
        roles=["developer"],
        trust_level=TrustLevel.MEDIUM,
        created_at=datetime.now(),
        last_authenticated=None
    )
    engine.register_identity(identity)
    
    # Register device
    device = Device(
        device_id="dev-001",
        device_name="Alice-Laptop",
        device_type="laptop",
        os_version="Windows 11",
        patch_level="current",
        encryption_enabled=True,
        antivirus_status=True,
        firewall_enabled=True,
        managed=True,
        posture=DevicePosture.UNKNOWN,
        last_scan=datetime.now()
    )
    engine.register_device(device)
    
    # Authenticate
    engine.authenticate_identity("user-001", AuthenticationMethod.MFA, 
                                {"password": "secret", "token": "123456"})
    
    # Create access context
    context = AccessContext(
        identity=identity,
        device=device,
        source_ip="10.0.1.100",
        location="Office",
        time=datetime.now(),
        resource="database-prod",
        action="read",
        risk_score=0.0
    )
    
    # Create policy
    policy = AccessPolicy(
        policy_id="pol-001",
        name="Database Access",
        required_trust_level=TrustLevel.HIGH,
        required_groups=["engineering"],
        required_device_posture=DevicePosture.COMPLIANT,
        requires_mfa=True,
        allowed_locations=["Office", "VPN"],
        allowed_ip_ranges=None,
        time_restrictions=None
    )
    
    # Evaluate access
    result = engine.evaluate_access_request(context, policy)
    print(f"\n🔐 Access Decision: {'GRANTED' if result['allowed'] else 'DENIED'}")


if __name__ == "__main__":
    main()
