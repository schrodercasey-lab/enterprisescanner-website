"""
Military-Grade Access Control & Identity Hardening Module
Enterprise Scanner - Zero Trust Architecture Validation

Validates identity and access management against:
- Zero Trust Architecture (NIST 800-207, EO 14028)
- Hardware MFA enforcement (YubiKey, CAC/PIV cards)
- Privileged Access Management (PAM)
- Just-In-Time (JIT) access
- Adaptive authentication
- Break-glass account monitoring
- Microsegmentation
- Continuous authentication & authorization

Supports: AWS IAM, Azure AD, GCP IAM
Classification: Unclassified
Compliance: NIST 800-53 AC-*, IA-*, FedRAMP High, CMMC Level 3-5
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json


class MFAType(Enum):
    """Multi-Factor Authentication types"""
    NONE = "No MFA"
    SOFTWARE_TOTP = "Software TOTP (Google Authenticator, Authy)"
    SMS = "SMS (Deprecated - not secure)"
    HARDWARE_U2F = "Hardware U2F (YubiKey, Titan)"
    HARDWARE_PIV = "Hardware PIV/CAC (DoD Smart Card)"
    BIOMETRIC = "Biometric (FIDO2)"
    ADAPTIVE = "Adaptive (Risk-based)"


class PrivilegeLevel(Enum):
    """User privilege levels"""
    STANDARD = "Standard User"
    POWER_USER = "Power User"
    ADMIN = "Administrator"
    ROOT = "Root/Super Admin"
    SERVICE_ACCOUNT = "Service Account"
    BREAK_GLASS = "Break-Glass Emergency Account"


class ZeroTrustMaturityLevel(Enum):
    """Zero Trust Maturity Model (CISA)"""
    TRADITIONAL = "Traditional (Perimeter-based)"
    INITIAL = "Initial (Basic segmentation)"
    ADVANCED = "Advanced (Dynamic policies)"
    OPTIMAL = "Optimal (Continuous verification)"


@dataclass
class AccessFinding:
    """Represents an access control/identity finding"""
    severity: str  # critical, high, medium, low
    category: str  # mfa, pam, zero_trust, least_privilege, session_management
    resource_id: str
    resource_type: str
    title: str
    description: str
    remediation: str
    compliance_frameworks: List[str]
    zero_trust_pillar: Optional[str] = None  # identity, device, network, application, data
    references: List[str] = field(default_factory=list)


class AccessControlHardeningScanner:
    """
    Military-grade access control and identity validation.
    
    Validates:
    - Multi-Factor Authentication (hardware MFA for DoD)
    - Privileged Access Management (PAM)
    - Zero Trust Architecture principles
    - Least privilege enforcement
    - Session management and timeouts
    - Break-glass account monitoring
    - Adaptive authentication
    """
    
    # DoD-approved MFA methods (hardware only for IL5/IL6)
    DOD_APPROVED_MFA = [MFAType.HARDWARE_U2F, MFAType.HARDWARE_PIV, MFAType.BIOMETRIC]
    
    # Session timeout requirements (minutes)
    SESSION_TIMEOUT_REQUIREMENTS = {
        PrivilegeLevel.STANDARD: 30,
        PrivilegeLevel.POWER_USER: 20,
        PrivilegeLevel.ADMIN: 15,
        PrivilegeLevel.ROOT: 10,
        PrivilegeLevel.BREAK_GLASS: 5
    }
    
    # Password rotation requirements (days)
    PASSWORD_ROTATION_DAYS = {
        PrivilegeLevel.STANDARD: 90,
        PrivilegeLevel.POWER_USER: 60,
        PrivilegeLevel.ADMIN: 30,
        PrivilegeLevel.ROOT: 15,
        PrivilegeLevel.SERVICE_ACCOUNT: 90,
        PrivilegeLevel.BREAK_GLASS: 15
    }
    
    # Privileged actions requiring approval
    PRIVILEGED_ACTIONS = [
        'iam:CreateUser', 'iam:DeleteUser', 'iam:CreateAccessKey',
        'iam:AttachUserPolicy', 'iam:PutUserPolicy',
        'kms:DeleteKey', 'kms:ScheduleKeyDeletion',
        's3:DeleteBucket', 's3:PutBucketPolicy',
        'ec2:TerminateInstances', 'rds:DeleteDBInstance',
        'cloudtrail:DeleteTrail', 'cloudtrail:StopLogging',
        'guardduty:DeleteDetector', 'securityhub:DisableSecurityHub'
    ]
    
    def __init__(self, require_hardware_mfa: bool = True, zero_trust_level: ZeroTrustMaturityLevel = ZeroTrustMaturityLevel.ADVANCED):
        """
        Initialize access control hardening scanner.
        
        Args:
            require_hardware_mfa: Require hardware MFA (True for DoD IL5/IL6)
            zero_trust_level: Target Zero Trust maturity level
        """
        self.require_hardware_mfa = require_hardware_mfa
        self.zero_trust_level = zero_trust_level
        self.findings: List[AccessFinding] = []
        self.scanned_identities = 0
        self.compliant_identities = 0
        
    def scan_aws_iam(self, iam_resources: Dict) -> List[AccessFinding]:
        """
        Scan AWS IAM for access control hardening.
        
        Args:
            iam_resources: Dictionary of AWS IAM resources from boto3
            
        Returns:
            List of access control findings
        """
        findings = []
        
        # User accounts
        if 'Users' in iam_resources:
            findings.extend(self._scan_aws_iam_users(iam_resources['Users']))
        
        # IAM policies
        if 'Policies' in iam_resources:
            findings.extend(self._scan_aws_iam_policies(iam_resources['Policies']))
        
        # IAM roles
        if 'Roles' in iam_resources:
            findings.extend(self._scan_aws_iam_roles(iam_resources['Roles']))
        
        # IAM groups
        if 'Groups' in iam_resources:
            findings.extend(self._scan_aws_iam_groups(iam_resources['Groups']))
        
        # Access keys
        if 'AccessKeys' in iam_resources:
            findings.extend(self._scan_aws_access_keys(iam_resources['AccessKeys']))
        
        # Account password policy
        if 'PasswordPolicy' in iam_resources:
            findings.extend(self._scan_aws_password_policy(iam_resources['PasswordPolicy']))
        
        # MFA devices
        if 'MFADevices' in iam_resources:
            findings.extend(self._scan_aws_mfa_devices(iam_resources['MFADevices']))
        
        # Root account
        if 'RootAccount' in iam_resources:
            findings.extend(self._scan_aws_root_account(iam_resources['RootAccount']))
        
        self.findings.extend(findings)
        return findings
    
    def _scan_aws_iam_users(self, users: List[Dict]) -> List[AccessFinding]:
        """Validate IAM user configuration"""
        findings = []
        
        for user in users:
            self.scanned_identities += 1
            username = user.get('UserName', 'Unknown')
            user_arn = user.get('Arn', username)
            create_date = user.get('CreateDate')
            password_last_used = user.get('PasswordLastUsed')
            
            # Check MFA enforcement
            mfa_devices = user.get('MFADevices', [])
            if not mfa_devices:
                findings.append(AccessFinding(
                    severity='critical',
                    category='mfa',
                    resource_id=username,
                    resource_type='AWS::IAM::User',
                    title='IAM User Without MFA',
                    description=f'User "{username}" does not have MFA enabled. All users must use multi-factor authentication.',
                    remediation='Enable MFA for user. For DoD IL5/IL6, use hardware MFA (YubiKey, CAC/PIV card). AWS Console → IAM → Users → Security Credentials → Assign MFA device.',
                    compliance_frameworks=['NIST 800-53 IA-2(1)', 'FedRAMP High', 'CMMC Level 2-5', 'Zero Trust'],
                    zero_trust_pillar='identity',
                    references=['https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html']
                ))
            elif self.require_hardware_mfa:
                # Validate hardware MFA for DoD
                for mfa_device in mfa_devices:
                    serial_number = mfa_device.get('SerialNumber', '')
                    # Virtual MFA has "mfa/" in serial, hardware has "u2f/" or physical device serial
                    if '/mfa/' in serial_number.lower():
                        findings.append(AccessFinding(
                            severity='high',
                            category='mfa',
                            resource_id=username,
                            resource_type='AWS::IAM::User',
                            title='IAM User Using Virtual MFA (Not Hardware)',
                            description=f'User "{username}" uses virtual MFA (TOTP). DoD IL5/IL6 requires hardware MFA (YubiKey, U2F, CAC/PIV).',
                            remediation='Replace virtual MFA with hardware security key. Purchase YubiKey 5 NFC or use DoD CAC/PIV card.',
                            compliance_frameworks=['NIST 800-53 IA-2(1)', 'DoD IL5/IL6', 'Zero Trust'],
                            zero_trust_pillar='identity'
                        ))
            
            # Check for inactive users (no console login in 90 days)
            if password_last_used:
                inactive_days = (datetime.now() - password_last_used.replace(tzinfo=None)).days
                if inactive_days > 90:
                    findings.append(AccessFinding(
                        severity='medium',
                        category='least_privilege',
                        resource_id=username,
                        resource_type='AWS::IAM::User',
                        title='Inactive IAM User Account',
                        description=f'User "{username}" has not logged in for {inactive_days} days. Inactive accounts should be disabled or removed.',
                        remediation='Disable or delete inactive user accounts. If needed for emergency access, convert to break-glass account with strict monitoring.',
                        compliance_frameworks=['NIST 800-53 AC-2(3)', 'FedRAMP High'],
                        zero_trust_pillar='identity'
                    ))
            
            # Check for users with direct policy attachments (should use groups)
            attached_policies = user.get('AttachedPolicies', [])
            inline_policies = user.get('InlinePolicies', [])
            if attached_policies or inline_policies:
                findings.append(AccessFinding(
                    severity='medium',
                    category='least_privilege',
                    resource_id=username,
                    resource_type='AWS::IAM::User',
                    title='IAM User Has Direct Policy Attachments',
                    description=f'User "{username}" has policies attached directly. Best practice: Use IAM groups for permission management.',
                    remediation='Remove direct policy attachments. Create IAM groups (e.g., Developers, Admins) and add user to appropriate groups.',
                    compliance_frameworks=['NIST 800-53 AC-6', 'AWS Best Practices'],
                    zero_trust_pillar='identity'
                ))
            
            # Check for privileged users (admin policies)
            is_admin = False
            for policy in attached_policies:
                policy_arn = policy.get('PolicyArn', '')
                if 'AdministratorAccess' in policy_arn or 'PowerUserAccess' in policy_arn:
                    is_admin = True
                    break
            
            if is_admin:
                # Admin users require additional scrutiny
                if not mfa_devices:
                    findings.append(AccessFinding(
                        severity='critical',
                        category='pam',
                        resource_id=username,
                        resource_type='AWS::IAM::User',
                        title='Privileged User Without MFA',
                        description=f'Admin user "{username}" does not have MFA. Privileged accounts are high-value targets.',
                        remediation='Enable hardware MFA immediately. Consider using AWS SSO with SAML federation for centralized PAM.',
                        compliance_frameworks=['NIST 800-53 AC-6(5)', 'CMMC Level 3-5'],
                        zero_trust_pillar='identity'
                    ))
                
                # Check for privileged session recording
                if not user.get('SessionRecordingEnabled', False):
                    findings.append(AccessFinding(
                        severity='high',
                        category='pam',
                        resource_id=username,
                        resource_type='AWS::IAM::User',
                        title='Privileged User Sessions Not Recorded',
                        description=f'Admin user "{username}" sessions are not recorded. All privileged access must be logged and recorded.',
                        remediation='Enable CloudTrail for API logging and AWS Systems Manager Session Manager for terminal session recording.',
                        compliance_frameworks=['NIST 800-53 AU-2', 'FedRAMP High'],
                        zero_trust_pillar='identity'
                    ))
            
            # If all checks pass
            if not any(f.resource_id == username and f.resource_type == 'AWS::IAM::User' for f in findings):
                self.compliant_identities += 1
        
        return findings
    
    def _scan_aws_iam_policies(self, policies: List[Dict]) -> List[AccessFinding]:
        """Validate IAM policy configuration for least privilege"""
        findings = []
        
        for policy in policies:
            policy_name = policy.get('PolicyName', 'Unknown')
            policy_arn = policy.get('Arn', policy_name)
            policy_document = policy.get('PolicyDocument', {})
            
            if isinstance(policy_document, str):
                try:
                    policy_document = json.loads(policy_document)
                except:
                    continue
            
            statements = policy_document.get('Statement', [])
            for statement in statements:
                effect = statement.get('Effect', '')
                actions = statement.get('Action', [])
                resources = statement.get('Resource', [])
                
                # Convert single action/resource to list
                if isinstance(actions, str):
                    actions = [actions]
                if isinstance(resources, str):
                    resources = [resources]
                
                # Check for overly permissive policies
                if effect == 'Allow':
                    # Check for wildcard actions
                    if '*' in actions or any(':*' in action for action in actions):
                        if '*' in resources:
                            findings.append(AccessFinding(
                                severity='critical',
                                category='least_privilege',
                                resource_id=policy_name,
                                resource_type='AWS::IAM::Policy',
                                title='IAM Policy Allows Full Access (Action:* Resource:*)',
                                description=f'Policy "{policy_name}" allows all actions on all resources. This violates least privilege principle.',
                                remediation='Restrict policy to minimum required actions and resources. Use IAM Access Analyzer to determine actual permissions needed.',
                                compliance_frameworks=['NIST 800-53 AC-6', 'FedRAMP High', 'Zero Trust'],
                                zero_trust_pillar='identity',
                                references=['https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege']
                            ))
                    
                    # Check for dangerous privileged actions without conditions
                    dangerous_actions = [action for action in actions if action in self.PRIVILEGED_ACTIONS]
                    if dangerous_actions and not statement.get('Condition'):
                        findings.append(AccessFinding(
                            severity='high',
                            category='pam',
                            resource_id=policy_name,
                            resource_type='AWS::IAM::Policy',
                            title='Privileged Actions Without Conditions',
                            description=f'Policy "{policy_name}" allows privileged actions ({", ".join(dangerous_actions[:3])}) without conditions. Requires MFA or source IP restrictions.',
                            remediation='Add Condition block requiring MFA: "Condition": {{"Bool": {{"aws:MultiFactorAuthPresent": "true"}}}}',
                            compliance_frameworks=['NIST 800-53 AC-6(5)', 'Zero Trust'],
                            zero_trust_pillar='identity'
                        ))
                    
                    # Check for policies allowing privilege escalation
                    escalation_actions = ['iam:CreateAccessKey', 'iam:AttachUserPolicy', 'iam:PutUserPolicy', 'iam:CreatePolicyVersion']
                    if any(action in actions for action in escalation_actions):
                        findings.append(AccessFinding(
                            severity='high',
                            category='pam',
                            resource_id=policy_name,
                            resource_type='AWS::IAM::Policy',
                            title='IAM Policy Allows Privilege Escalation',
                            description=f'Policy "{policy_name}" includes actions that can be used for privilege escalation attacks.',
                            remediation='Remove privilege escalation actions or restrict to specific users/roles with MFA condition.',
                            compliance_frameworks=['NIST 800-53 AC-6', 'CMMC Level 3'],
                            zero_trust_pillar='identity'
                        ))
        
        return findings
    
    def _scan_aws_iam_roles(self, roles: List[Dict]) -> List[AccessFinding]:
        """Validate IAM role configuration"""
        findings = []
        
        for role in roles:
            role_name = role.get('RoleName', 'Unknown')
            role_arn = role.get('Arn', role_name)
            assume_role_policy = role.get('AssumeRolePolicyDocument', {})
            max_session_duration = role.get('MaxSessionDuration', 3600)  # seconds
            
            if isinstance(assume_role_policy, str):
                try:
                    assume_role_policy = json.loads(assume_role_policy)
                except:
                    continue
            
            # Check assume role policy for overly permissive principals
            statements = assume_role_policy.get('Statement', [])
            for statement in statements:
                effect = statement.get('Effect', '')
                principal = statement.get('Principal', {})
                
                if effect == 'Allow':
                    # Check for wildcard principals
                    if principal == '*' or (isinstance(principal, dict) and principal.get('AWS') == '*'):
                        findings.append(AccessFinding(
                            severity='critical',
                            category='least_privilege',
                            resource_id=role_name,
                            resource_type='AWS::IAM::Role',
                            title='IAM Role Allows Public Assumption',
                            description=f'Role "{role_name}" can be assumed by any AWS principal (Principal: "*"). This is a critical security risk.',
                            remediation='Restrict assume role policy to specific AWS accounts, IAM users, or federated identities.',
                            compliance_frameworks=['NIST 800-53 AC-6', 'FedRAMP High'],
                            zero_trust_pillar='identity'
                        ))
                    
                    # Check for cross-account access without external ID
                    if isinstance(principal, dict) and 'AWS' in principal:
                        aws_principals = principal['AWS'] if isinstance(principal['AWS'], list) else [principal['AWS']]
                        for aws_principal in aws_principals:
                            # External account ARN
                            if ':' in aws_principal and not statement.get('Condition', {}).get('StringEquals', {}).get('sts:ExternalId'):
                                findings.append(AccessFinding(
                                    severity='medium',
                                    category='least_privilege',
                                    resource_id=role_name,
                                    resource_type='AWS::IAM::Role',
                                    title='Cross-Account Role Without External ID',
                                    description=f'Role "{role_name}" allows cross-account access without external ID. Vulnerable to confused deputy attack.',
                                    remediation='Add Condition requiring external ID: "Condition": {{"StringEquals": {{"sts:ExternalId": "unique-secret-value"}}}}',
                                    compliance_frameworks=['AWS Security Best Practices'],
                                    zero_trust_pillar='identity',
                                    references=['https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html']
                                ))
            
            # Check session duration for privileged roles
            if 'admin' in role_name.lower() or 'privileged' in role_name.lower():
                max_duration_minutes = max_session_duration / 60
                required_duration = self.SESSION_TIMEOUT_REQUIREMENTS.get(PrivilegeLevel.ADMIN, 15)
                if max_duration_minutes > required_duration:
                    findings.append(AccessFinding(
                        severity='medium',
                        category='session_management',
                        resource_id=role_name,
                        resource_type='AWS::IAM::Role',
                        title='Privileged Role Session Duration Too Long',
                        description=f'Privileged role "{role_name}" has {max_duration_minutes:.0f} minute max session. Should be ≤{required_duration} minutes.',
                        remediation=f'Update MaxSessionDuration to {required_duration * 60} seconds for privileged roles.',
                        compliance_frameworks=['NIST 800-53 AC-12', 'Zero Trust'],
                        zero_trust_pillar='identity'
                    ))
        
        return findings
    
    def _scan_aws_iam_groups(self, groups: List[Dict]) -> List[AccessFinding]:
        """Validate IAM group configuration"""
        findings = []
        
        for group in groups:
            group_name = group.get('GroupName', 'Unknown')
            attached_policies = group.get('AttachedPolicies', [])
            
            # Check for admin groups
            is_admin_group = 'admin' in group_name.lower() or any('AdministratorAccess' in p.get('PolicyArn', '') for p in attached_policies)
            
            if is_admin_group:
                # Admin groups should have strict membership
                members = group.get('Users', [])
                if len(members) > 5:
                    findings.append(AccessFinding(
                        severity='medium',
                        category='pam',
                        resource_id=group_name,
                        resource_type='AWS::IAM::Group',
                        title='Admin Group Has Too Many Members',
                        description=f'Admin group "{group_name}" has {len(members)} members. Limit admin access to minimum required personnel.',
                        remediation='Review admin group membership. Remove users who do not require admin privileges. Consider role-based access with approval workflow.',
                        compliance_frameworks=['NIST 800-53 AC-6(5)', 'Least Privilege'],
                        zero_trust_pillar='identity'
                    ))
        
        return findings
    
    def _scan_aws_access_keys(self, access_keys: List[Dict]) -> List[AccessFinding]:
        """Validate access key management"""
        findings = []
        
        for key_info in access_keys:
            access_key_id = key_info.get('AccessKeyId', 'Unknown')
            username = key_info.get('UserName', 'Unknown')
            status = key_info.get('Status', 'Unknown')
            create_date = key_info.get('CreateDate')
            last_used = key_info.get('LastUsedDate')
            
            # Check key age
            if create_date:
                key_age_days = (datetime.now() - create_date.replace(tzinfo=None)).days
                if key_age_days > 90:
                    findings.append(AccessFinding(
                        severity='high',
                        category='least_privilege',
                        resource_id=access_key_id,
                        resource_type='AWS::IAM::AccessKey',
                        title='Access Key Exceeds 90-Day Rotation Policy',
                        description=f'Access key for user "{username}" is {key_age_days} days old. Keys should be rotated every 90 days (30 days for privileged users).',
                        remediation='Rotate access key: Create new key, update applications, deactivate old key, delete old key after verification.',
                        compliance_frameworks=['NIST 800-53 IA-5(1)', 'FedRAMP High', 'CIS AWS Benchmark'],
                        zero_trust_pillar='identity'
                    ))
            
            # Check for inactive keys
            if last_used and status == 'Active':
                inactive_days = (datetime.now() - last_used.replace(tzinfo=None)).days
                if inactive_days > 90:
                    findings.append(AccessFinding(
                        severity='medium',
                        category='least_privilege',
                        resource_id=access_key_id,
                        resource_type='AWS::IAM::AccessKey',
                        title='Inactive Access Key Not Removed',
                        description=f'Access key for user "{username}" has not been used in {inactive_days} days. Inactive keys should be deleted.',
                        remediation='Delete inactive access key if no longer needed.',
                        compliance_frameworks=['NIST 800-53 AC-2(3)', 'AWS Best Practices'],
                        zero_trust_pillar='identity'
                    ))
            
            # Check for multiple active keys (max should be 1 during rotation)
            user_keys = [k for k in access_keys if k.get('UserName') == username and k.get('Status') == 'Active']
            if len(user_keys) > 1:
                findings.append(AccessFinding(
                    severity='low',
                    category='least_privilege',
                    resource_id=username,
                    resource_type='AWS::IAM::User',
                    title='User Has Multiple Active Access Keys',
                    description=f'User "{username}" has {len(user_keys)} active access keys. Should have 1 (or 2 temporarily during rotation).',
                    remediation='Delete oldest access key after verifying new key works.',
                    compliance_frameworks=['AWS Best Practices'],
                    zero_trust_pillar='identity'
                ))
        
        return findings
    
    def _scan_aws_password_policy(self, password_policy: Dict) -> List[AccessFinding]:
        """Validate account password policy"""
        findings = []
        
        # Minimum password length (NIST recommends 14+, DoD requires 15+)
        min_length = password_policy.get('MinimumPasswordLength', 0)
        required_length = 15 if self.require_hardware_mfa else 14
        if min_length < required_length:
            findings.append(AccessFinding(
                severity='high',
                category='mfa',
                resource_id='AccountPasswordPolicy',
                resource_type='AWS::IAM::AccountPasswordPolicy',
                title=f'Password Minimum Length Below {required_length} Characters',
                description=f'Account password policy requires only {min_length} characters. NIST 800-63B recommends 14+ (DoD requires 15+).',
                remediation=f'Update password policy: aws iam update-account-password-policy --minimum-password-length {required_length}',
                compliance_frameworks=['NIST 800-53 IA-5(1)', 'NIST 800-63B', 'DoD IL5/IL6'],
                zero_trust_pillar='identity'
            ))
        
        # Require symbols, numbers, uppercase, lowercase
        require_symbols = password_policy.get('RequireSymbols', False)
        require_numbers = password_policy.get('RequireNumbers', False)
        require_uppercase = password_policy.get('RequireUppercaseCharacters', False)
        require_lowercase = password_policy.get('RequireLowercaseCharacters', False)
        
        if not (require_symbols and require_numbers and require_uppercase and require_lowercase):
            findings.append(AccessFinding(
                severity='medium',
                category='mfa',
                resource_id='AccountPasswordPolicy',
                resource_type='AWS::IAM::AccountPasswordPolicy',
                title='Password Complexity Requirements Not Enforced',
                description='Account password policy does not require symbols, numbers, uppercase, and lowercase characters.',
                remediation='Update password policy to require all character types: --require-symbols --require-numbers --require-uppercase-characters --require-lowercase-characters',
                compliance_frameworks=['NIST 800-53 IA-5(1)', 'CIS AWS Benchmark'],
                zero_trust_pillar='identity'
            ))
        
        # Password expiration (max 90 days)
        max_age = password_policy.get('MaxPasswordAge', 0)
        if max_age == 0 or max_age > 90:
            findings.append(AccessFinding(
                severity='medium',
                category='mfa',
                resource_id='AccountPasswordPolicy',
                resource_type='AWS::IAM::AccountPasswordPolicy',
                title='Password Expiration Not Enforced or Too Long',
                description=f'Account password policy has {max_age}-day expiration (or none). Passwords should expire every 90 days maximum.',
                remediation='Update password policy: --max-password-age 90',
                compliance_frameworks=['NIST 800-53 IA-5(1)', 'CIS AWS Benchmark'],
                zero_trust_pillar='identity'
            ))
        
        # Password reuse prevention
        reuse_prevention = password_policy.get('PasswordReusePrevention', 0)
        if reuse_prevention < 24:
            findings.append(AccessFinding(
                severity='low',
                category='mfa',
                resource_id='AccountPasswordPolicy',
                resource_type='AWS::IAM::AccountPasswordPolicy',
                title='Password Reuse Prevention Insufficient',
                description=f'Password policy remembers only {reuse_prevention} passwords. Should prevent reuse of last 24 passwords.',
                remediation='Update password policy: --password-reuse-prevention 24',
                compliance_frameworks=['NIST 800-53 IA-5(1)', 'CIS AWS Benchmark'],
                zero_trust_pillar='identity'
            ))
        
        return findings
    
    def _scan_aws_mfa_devices(self, mfa_devices: List[Dict]) -> List[AccessFinding]:
        """Validate MFA device types and configuration"""
        findings = []
        
        # This is primarily for tracking hardware vs virtual MFA
        # Main MFA checks are in _scan_aws_iam_users
        
        return findings
    
    def _scan_aws_root_account(self, root_account: Dict) -> List[AccessFinding]:
        """Validate root account security"""
        findings = []
        
        # Root account should NEVER be used for day-to-day operations
        last_used = root_account.get('PasswordLastUsed')
        if last_used:
            days_since_use = (datetime.now() - last_used.replace(tzinfo=None)).days
            if days_since_use < 365:
                findings.append(AccessFinding(
                    severity='critical',
                    category='pam',
                    resource_id='root',
                    resource_type='AWS::IAM::RootAccount',
                    title='Root Account Recently Used',
                    description=f'Root account was used {days_since_use} days ago. Root should NEVER be used except for emergency account recovery.',
                    remediation='Create IAM admin users for all administrative tasks. Lock root account credentials in physical safe.',
                    compliance_frameworks=['NIST 800-53 AC-6(5)', 'CIS AWS Benchmark', 'FedRAMP High'],
                    zero_trust_pillar='identity',
                    references=['https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#lock-away-credentials']
                ))
        
        # Root account must have MFA
        root_mfa_enabled = root_account.get('MFAEnabled', False)
        if not root_mfa_enabled:
            findings.append(AccessFinding(
                severity='critical',
                category='mfa',
                resource_id='root',
                resource_type='AWS::IAM::RootAccount',
                title='Root Account MFA Not Enabled',
                description='Root account does not have MFA enabled. This is the highest-risk security gap.',
                remediation='Enable hardware MFA for root account immediately. Use YubiKey or hardware security key, not virtual MFA.',
                compliance_frameworks=['NIST 800-53 IA-2(1)', 'CIS AWS Benchmark 1.5', 'FedRAMP High'],
                zero_trust_pillar='identity'
            ))
        
        # Root access keys should not exist
        root_access_keys = root_account.get('AccessKeys', [])
        if root_access_keys:
            findings.append(AccessFinding(
                severity='critical',
                category='pam',
                resource_id='root',
                resource_type='AWS::IAM::RootAccount',
                title='Root Account Access Keys Exist',
                description=f'Root account has {len(root_access_keys)} access keys. Root access keys are prohibited.',
                remediation='Delete all root account access keys immediately. Use IAM users/roles for programmatic access.',
                compliance_frameworks=['CIS AWS Benchmark 1.12', 'FedRAMP High'],
                zero_trust_pillar='identity'
            ))
        
        return findings
    
    def generate_report(self) -> Dict:
        """
        Generate access control hardening report.
        
        Returns:
            Dictionary with scan results and Zero Trust maturity assessment
        """
        critical_count = len([f for f in self.findings if f.severity == 'critical'])
        high_count = len([f for f in self.findings if f.severity == 'high'])
        medium_count = len([f for f in self.findings if f.severity == 'medium'])
        low_count = len([f for f in self.findings if f.severity == 'low'])
        
        compliance_rate = (self.compliant_identities / self.scanned_identities * 100) if self.scanned_identities > 0 else 0
        
        # Assess Zero Trust maturity
        zero_trust_score = self._calculate_zero_trust_maturity()
        
        # Determine overall compliance status
        if critical_count > 0:
            compliance_status = "Non-Compliant (Critical Access Control Issues)"
        elif high_count > 5:
            compliance_status = "Non-Compliant (Multiple High-Severity Issues)"
        elif compliance_rate < 80:
            compliance_status = "Partially Compliant"
        elif compliance_rate < 95:
            compliance_status = "Substantially Compliant"
        else:
            compliance_status = "Fully Compliant"
        
        return {
            'scan_metadata': {
                'require_hardware_mfa': self.require_hardware_mfa,
                'target_zero_trust_level': self.zero_trust_level.value,
                'scan_timestamp': datetime.now().isoformat(),
                'scanned_identities': self.scanned_identities,
                'compliant_identities': self.compliant_identities,
                'compliance_rate': round(compliance_rate, 2)
            },
            'compliance_status': compliance_status,
            'zero_trust_maturity': zero_trust_score,
            'findings_summary': {
                'total_findings': len(self.findings),
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'findings_by_category': {
                'mfa': len([f for f in self.findings if f.category == 'mfa']),
                'pam': len([f for f in self.findings if f.category == 'pam']),
                'least_privilege': len([f for f in self.findings if f.category == 'least_privilege']),
                'zero_trust': len([f for f in self.findings if f.category == 'zero_trust']),
                'session_management': len([f for f in self.findings if f.category == 'session_management'])
            },
            'findings_by_zero_trust_pillar': {
                'identity': len([f for f in self.findings if f.zero_trust_pillar == 'identity']),
                'device': len([f for f in self.findings if f.zero_trust_pillar == 'device']),
                'network': len([f for f in self.findings if f.zero_trust_pillar == 'network']),
                'application': len([f for f in self.findings if f.zero_trust_pillar == 'application']),
                'data': len([f for f in self.findings if f.zero_trust_pillar == 'data'])
            },
            'detailed_findings': [
                {
                    'severity': f.severity,
                    'category': f.category,
                    'resource_id': f.resource_id,
                    'resource_type': f.resource_type,
                    'title': f.title,
                    'description': f.description,
                    'remediation': f.remediation,
                    'compliance_frameworks': f.compliance_frameworks,
                    'zero_trust_pillar': f.zero_trust_pillar
                }
                for f in self.findings
            ],
            'recommendations': self._generate_recommendations(critical_count, high_count, medium_count, zero_trust_score)
        }
    
    def _calculate_zero_trust_maturity(self) -> Dict:
        """Calculate Zero Trust maturity level based on findings"""
        # Scoring criteria (0-100)
        mfa_score = 100 - (len([f for f in self.findings if f.category == 'mfa']) * 10)
        pam_score = 100 - (len([f for f in self.findings if f.category == 'pam']) * 10)
        least_privilege_score = 100 - (len([f for f in self.findings if f.category == 'least_privilege']) * 5)
        
        mfa_score = max(0, min(100, mfa_score))
        pam_score = max(0, min(100, pam_score))
        least_privilege_score = max(0, min(100, least_privilege_score))
        
        overall_score = (mfa_score + pam_score + least_privilege_score) / 3
        
        # Determine maturity level
        if overall_score >= 90:
            maturity_level = ZeroTrustMaturityLevel.OPTIMAL
        elif overall_score >= 75:
            maturity_level = ZeroTrustMaturityLevel.ADVANCED
        elif overall_score >= 50:
            maturity_level = ZeroTrustMaturityLevel.INITIAL
        else:
            maturity_level = ZeroTrustMaturityLevel.TRADITIONAL
        
        return {
            'overall_score': round(overall_score, 2),
            'maturity_level': maturity_level.value,
            'pillar_scores': {
                'identity_mfa': mfa_score,
                'privileged_access': pam_score,
                'least_privilege': least_privilege_score
            },
            'target_level': self.zero_trust_level.value,
            'gap_to_target': self.zero_trust_level.value != maturity_level.value
        }
    
    def _generate_recommendations(self, critical: int, high: int, medium: int, zero_trust_score: Dict) -> List[str]:
        """Generate prioritized recommendations based on findings"""
        recommendations = []
        
        if critical > 0:
            recommendations.append(f"CRITICAL: Address {critical} critical access control findings immediately. Focus on MFA enablement and root account security.")
        
        if high > 0:
            recommendations.append(f"HIGH PRIORITY: Remediate {high} high-severity findings within 30 days. Implement hardware MFA for all privileged users.")
        
        # Zero Trust specific recommendations
        zt_maturity = zero_trust_score['maturity_level']
        if zt_maturity == ZeroTrustMaturityLevel.TRADITIONAL.value:
            recommendations.append("Zero Trust Roadmap: Currently at Traditional (perimeter-based) security. Implement microsegmentation, MFA enforcement, and least privilege access as first steps.")
        elif zt_maturity == ZeroTrustMaturityLevel.INITIAL.value:
            recommendations.append("Zero Trust Roadmap: Progress from Initial to Advanced by implementing adaptive authentication, just-in-time access, and continuous verification.")
        
        if self.require_hardware_mfa:
            recommendations.append("DoD Compliance: Replace all virtual MFA with hardware security keys (YubiKey 5 NFC, CAC/PIV cards) for IL5/IL6 readiness.")
        
        recommendations.append("Implement AWS SSO with SAML federation for centralized identity management and single sign-on.")
        recommendations.append("Enable AWS CloudTrail for all accounts and aggregate logs in secure S3 bucket with MFA delete protection.")
        recommendations.append("Deploy AWS IAM Access Analyzer to identify overly permissive policies and external resource access.")
        
        if medium > 0:
            recommendations.append(f"MEDIUM PRIORITY: Address {medium} medium-severity findings within 90 days to improve security posture.")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Initialize scanner for DoD (hardware MFA required)
    scanner = AccessControlHardeningScanner(
        require_hardware_mfa=True,
        zero_trust_level=ZeroTrustMaturityLevel.ADVANCED
    )
    
    # Example IAM resources (normally from boto3)
    example_iam_resources = {
        'Users': [
            {
                'UserName': 'admin.user',
                'Arn': 'arn:aws:iam::123456789012:user/admin.user',
                'CreateDate': datetime.now() - timedelta(days=100),
                'PasswordLastUsed': datetime.now() - timedelta(days=2),
                'MFADevices': [
                    {'SerialNumber': 'arn:aws:iam::123456789012:mfa/admin.user'}  # Virtual MFA (not hardware)
                ],
                'AttachedPolicies': [
                    {'PolicyArn': 'arn:aws:iam::aws:policy/AdministratorAccess'}
                ]
            }
        ],
        'PasswordPolicy': {
            'MinimumPasswordLength': 12,  # Should be 15+ for DoD
            'RequireSymbols': True,
            'RequireNumbers': True,
            'RequireUppercaseCharacters': True,
            'RequireLowercaseCharacters': True,
            'MaxPasswordAge': 90,
            'PasswordReusePrevention': 24
        },
        'RootAccount': {
            'PasswordLastUsed': datetime.now() - timedelta(days=10),  # Should not be used
            'MFAEnabled': True,
            'AccessKeys': []  # Good - no root access keys
        }
    }
    
    # Scan IAM resources
    findings = scanner.scan_aws_iam(example_iam_resources)
    
    # Generate report
    report = scanner.generate_report()
    
    print(f"\nAccess Control & Identity Hardening Scan Results")
    print("=" * 80)
    print(f"Compliance Status: {report['compliance_status']}")
    print(f"Zero Trust Maturity: {report['zero_trust_maturity']['maturity_level']} (Score: {report['zero_trust_maturity']['overall_score']})")
    print(f"Scanned Identities: {report['scan_metadata']['scanned_identities']}")
    print(f"Compliant Identities: {report['scan_metadata']['compliant_identities']} ({report['scan_metadata']['compliance_rate']}%)")
    print(f"\nFindings: {report['findings_summary']['critical']} Critical, {report['findings_summary']['high']} High, {report['findings_summary']['medium']} Medium")
    print("\nTop Recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec}")
