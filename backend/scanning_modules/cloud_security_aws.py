"""
Cloud Security Scanner Module - AWS
Enterprise-grade AWS security assessment and misconfiguration detection
"""

import boto3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class CloudSecurityFinding:
    """Cloud security finding"""
    cloud_provider: str  # 'AWS', 'Azure', 'GCP'
    service: str  # 'S3', 'EC2', 'IAM', etc.
    resource_id: str
    finding_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    recommendation: str
    compliance_frameworks: List[str]  # ['CIS', 'NIST', 'PCI-DSS']
    remediation_steps: List[str]


class AWSSecurityScanner:
    """
    AWS Security Scanner for Enterprise Scanner
    
    Features:
    - S3 bucket security analysis
    - IAM policy review
    - EC2 security group analysis
    - CloudTrail logging verification
    - Encryption checks
    - Public exposure detection
    - Compliance mapping (CIS, NIST, PCI-DSS)
    """
    
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None, 
                 region: str = 'us-east-1', profile_name: Optional[str] = None):
        """
        Initialize AWS security scanner
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            region: AWS region to scan
            profile_name: AWS CLI profile name (alternative to keys)
        """
        self.region = region
        self.findings = []
        
        # Initialize boto3 session
        if profile_name:
            self.session = boto3.Session(profile_name=profile_name, region_name=region)
        elif access_key and secret_key:
            self.session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        else:
            # Use default credentials (environment variables or IAM role)
            self.session = boto3.Session(region_name=region)
        
        logger.info(f"AWS Security Scanner initialized for region {region}")
    
    def scan_account(self) -> List[CloudSecurityFinding]:
        """
        Perform comprehensive AWS account security scan
        
        Returns:
            List of security findings
        """
        logger.info("Starting comprehensive AWS security scan...")
        self.findings = []
        
        # Scan S3 buckets
        self._scan_s3_buckets()
        
        # Scan IAM
        self._scan_iam_configuration()
        
        # Scan EC2 security groups
        self._scan_ec2_security_groups()
        
        # Check CloudTrail
        self._check_cloudtrail_logging()
        
        # Check encryption
        self._check_encryption_settings()
        
        # Check for public exposures
        self._check_public_exposures()
        
        logger.info(f"AWS security scan complete. Found {len(self.findings)} issues.")
        return self.findings
    
    def _scan_s3_buckets(self):
        """Scan S3 buckets for security misconfigurations"""
        try:
            s3_client = self.session.client('s3')
            
            # List all buckets
            response = s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            
            logger.info(f"Scanning {len(buckets)} S3 buckets...")
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                
                try:
                    # Check bucket public access
                    acl = s3_client.get_bucket_acl(Bucket=bucket_name)
                    for grant in acl.get('Grants', []):
                        grantee = grant.get('Grantee', {})
                        if grantee.get('Type') == 'Group' and 'AllUsers' in grantee.get('URI', ''):
                            self.findings.append(CloudSecurityFinding(
                                cloud_provider='AWS',
                                service='S3',
                                resource_id=bucket_name,
                                finding_type='Public Bucket Access',
                                severity='critical',
                                description=f'S3 bucket {bucket_name} is publicly accessible',
                                recommendation='Remove public access and use IAM policies for access control',
                                compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                remediation_steps=[
                                    'Navigate to S3 console',
                                    f'Select bucket {bucket_name}',
                                    'Click Permissions > Block public access',
                                    'Enable all block public access settings'
                                ]
                            ))
                    
                    # Check bucket encryption
                    try:
                        s3_client.get_bucket_encryption(Bucket=bucket_name)
                    except s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
                        self.findings.append(CloudSecurityFinding(
                            cloud_provider='AWS',
                            service='S3',
                            resource_id=bucket_name,
                            finding_type='Unencrypted Bucket',
                            severity='high',
                            description=f'S3 bucket {bucket_name} does not have encryption enabled',
                            recommendation='Enable default encryption (AES-256 or KMS)',
                            compliance_frameworks=['CIS', 'NIST', 'HIPAA', 'PCI-DSS'],
                            remediation_steps=[
                                'Navigate to S3 console',
                                f'Select bucket {bucket_name}',
                                'Click Properties > Default encryption',
                                'Enable AES-256 or AWS-KMS encryption'
                            ]
                        ))
                    
                    # Check bucket versioning
                    versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
                    if versioning.get('Status') != 'Enabled':
                        self.findings.append(CloudSecurityFinding(
                            cloud_provider='AWS',
                            service='S3',
                            resource_id=bucket_name,
                            finding_type='Versioning Disabled',
                            severity='medium',
                            description=f'S3 bucket {bucket_name} does not have versioning enabled',
                            recommendation='Enable versioning for data protection and recovery',
                            compliance_frameworks=['CIS', 'NIST'],
                            remediation_steps=[
                                'Navigate to S3 console',
                                f'Select bucket {bucket_name}',
                                'Click Properties > Bucket Versioning',
                                'Enable versioning'
                            ]
                        ))
                    
                    # Check bucket logging
                    try:
                        logging_config = s3_client.get_bucket_logging(Bucket=bucket_name)
                        if 'LoggingEnabled' not in logging_config:
                            self.findings.append(CloudSecurityFinding(
                                cloud_provider='AWS',
                                service='S3',
                                resource_id=bucket_name,
                                finding_type='Access Logging Disabled',
                                severity='medium',
                                description=f'S3 bucket {bucket_name} does not have access logging enabled',
                                recommendation='Enable server access logging for audit trail',
                                compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                remediation_steps=[
                                    'Create a separate bucket for logs',
                                    f'Navigate to bucket {bucket_name}',
                                    'Click Properties > Server access logging',
                                    'Enable logging and specify target bucket'
                                ]
                            ))
                    except Exception as e:
                        logger.debug(f"Error checking logging for {bucket_name}: {e}")
                        
                except Exception as e:
                    logger.debug(f"Error scanning bucket {bucket_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scanning S3 buckets: {e}")
    
    def _scan_iam_configuration(self):
        """Scan IAM configuration for security issues"""
        try:
            iam_client = self.session.client('iam')
            
            logger.info("Scanning IAM configuration...")
            
            # Check for root account usage
            try:
                credential_report = iam_client.generate_credential_report()
                # Note: Would need to parse credential report for root access keys
                self.findings.append(CloudSecurityFinding(
                    cloud_provider='AWS',
                    service='IAM',
                    resource_id='root-account',
                    finding_type='Root Account Security',
                    severity='high',
                    description='Verify root account has MFA enabled and no access keys',
                    recommendation='Enable MFA on root account and delete root access keys',
                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                    remediation_steps=[
                        'Sign in as root user',
                        'Navigate to IAM > My Security Credentials',
                        'Enable MFA',
                        'Delete any access keys'
                    ]
                ))
            except Exception as e:
                logger.debug(f"Error checking root account: {e}")
            
            # Check IAM password policy
            try:
                password_policy = iam_client.get_account_password_policy()
                policy = password_policy.get('PasswordPolicy', {})
                
                if policy.get('MinimumPasswordLength', 0) < 14:
                    self.findings.append(CloudSecurityFinding(
                        cloud_provider='AWS',
                        service='IAM',
                        resource_id='password-policy',
                        finding_type='Weak Password Policy',
                        severity='high',
                        description='IAM password policy requires minimum 14 characters',
                        recommendation='Update password policy to require at least 14 characters',
                        compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                        remediation_steps=[
                            'Navigate to IAM > Account settings',
                            'Click Change password policy',
                            'Set minimum password length to 14',
                            'Enable complexity requirements'
                        ]
                    ))
                
                if not policy.get('RequireSymbols', False):
                    self.findings.append(CloudSecurityFinding(
                        cloud_provider='AWS',
                        service='IAM',
                        resource_id='password-policy',
                        finding_type='Password Complexity',
                        severity='medium',
                        description='Password policy should require symbols',
                        recommendation='Enable symbol requirement in password policy',
                        compliance_frameworks=['CIS', 'PCI-DSS'],
                        remediation_steps=[
                            'Navigate to IAM > Account settings',
                            'Enable "Require at least one symbol"'
                        ]
                    ))
                    
            except iam_client.exceptions.NoSuchEntityException:
                self.findings.append(CloudSecurityFinding(
                    cloud_provider='AWS',
                    service='IAM',
                    resource_id='password-policy',
                    finding_type='No Password Policy',
                    severity='critical',
                    description='No IAM password policy is configured',
                    recommendation='Create a strong password policy immediately',
                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                    remediation_steps=[
                        'Navigate to IAM > Account settings',
                        'Click Set password policy',
                        'Configure: 14+ chars, symbols, numbers, uppercase, lowercase',
                        'Enable password expiration (90 days)'
                    ]
                ))
            
            # Check for users with access keys
            users = iam_client.list_users()
            for user in users.get('Users', []):
                username = user['UserName']
                access_keys = iam_client.list_access_keys(UserName=username)
                
                for key in access_keys.get('AccessKeyMetadata', []):
                    key_age = (datetime.now() - key['CreateDate'].replace(tzinfo=None)).days
                    
                    if key_age > 90:
                        self.findings.append(CloudSecurityFinding(
                            cloud_provider='AWS',
                            service='IAM',
                            resource_id=f"{username}/{key['AccessKeyId']}",
                            finding_type='Old Access Key',
                            severity='high',
                            description=f'Access key for user {username} is {key_age} days old',
                            recommendation='Rotate access keys every 90 days',
                            compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                            remediation_steps=[
                                'Create new access key',
                                'Update applications with new key',
                                'Deactivate old key',
                                'Delete old key after verification'
                            ]
                        ))
                        
        except Exception as e:
            logger.error(f"Error scanning IAM configuration: {e}")
    
    def _scan_ec2_security_groups(self):
        """Scan EC2 security groups for overly permissive rules"""
        try:
            ec2_client = self.session.client('ec2')
            
            logger.info("Scanning EC2 security groups...")
            
            security_groups = ec2_client.describe_security_groups()
            
            for sg in security_groups.get('SecurityGroups', []):
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                
                # Check for open SSH (port 22)
                for rule in sg.get('IpPermissions', []):
                    if rule.get('FromPort') == 22 or rule.get('ToPort') == 22:
                        for ip_range in rule.get('IpRanges', []):
                            if ip_range.get('CidrIp') == '0.0.0.0/0':
                                self.findings.append(CloudSecurityFinding(
                                    cloud_provider='AWS',
                                    service='EC2',
                                    resource_id=f"{sg_id} ({sg_name})",
                                    finding_type='SSH Open to Internet',
                                    severity='critical',
                                    description=f'Security group {sg_name} allows SSH from 0.0.0.0/0',
                                    recommendation='Restrict SSH access to specific IP addresses',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to EC2 > Security Groups',
                                        f'Select {sg_name}',
                                        'Edit inbound rules',
                                        'Change SSH source from 0.0.0.0/0 to specific IPs'
                                    ]
                                ))
                    
                    # Check for open RDP (port 3389)
                    if rule.get('FromPort') == 3389 or rule.get('ToPort') == 3389:
                        for ip_range in rule.get('IpRanges', []):
                            if ip_range.get('CidrIp') == '0.0.0.0/0':
                                self.findings.append(CloudSecurityFinding(
                                    cloud_provider='AWS',
                                    service='EC2',
                                    resource_id=f"{sg_id} ({sg_name})",
                                    finding_type='RDP Open to Internet',
                                    severity='critical',
                                    description=f'Security group {sg_name} allows RDP from 0.0.0.0/0',
                                    recommendation='Restrict RDP access to specific IP addresses',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to EC2 > Security Groups',
                                        f'Select {sg_name}',
                                        'Edit inbound rules',
                                        'Change RDP source from 0.0.0.0/0 to specific IPs'
                                    ]
                                ))
                    
                    # Check for unrestricted access (all ports)
                    if rule.get('IpProtocol') == '-1':  # All protocols
                        for ip_range in rule.get('IpRanges', []):
                            if ip_range.get('CidrIp') == '0.0.0.0/0':
                                self.findings.append(CloudSecurityFinding(
                                    cloud_provider='AWS',
                                    service='EC2',
                                    resource_id=f"{sg_id} ({sg_name})",
                                    finding_type='Unrestricted Access',
                                    severity='critical',
                                    description=f'Security group {sg_name} allows all traffic from internet',
                                    recommendation='Implement least privilege access controls',
                                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                                    remediation_steps=[
                                        'Navigate to EC2 > Security Groups',
                                        f'Select {sg_name}',
                                        'Delete unrestricted rule',
                                        'Add specific rules for required services only'
                                    ]
                                ))
                                
        except Exception as e:
            logger.error(f"Error scanning EC2 security groups: {e}")
    
    def _check_cloudtrail_logging(self):
        """Check CloudTrail logging configuration"""
        try:
            cloudtrail_client = self.session.client('cloudtrail')
            
            logger.info("Checking CloudTrail configuration...")
            
            trails = cloudtrail_client.describe_trails()
            
            if not trails.get('trailList'):
                self.findings.append(CloudSecurityFinding(
                    cloud_provider='AWS',
                    service='CloudTrail',
                    resource_id='account',
                    finding_type='No CloudTrail',
                    severity='critical',
                    description='No CloudTrail is configured for this account',
                    recommendation='Enable CloudTrail to log all API calls',
                    compliance_frameworks=['CIS', 'NIST', 'PCI-DSS', 'HIPAA'],
                    remediation_steps=[
                        'Navigate to CloudTrail console',
                        'Click Create trail',
                        'Enable for all regions',
                        'Configure S3 bucket for logs',
                        'Enable log file validation'
                    ]
                ))
            else:
                for trail in trails.get('trailList', []):
                    trail_name = trail['Name']
                    
                    # Check if trail is multi-region
                    if not trail.get('IsMultiRegionTrail', False):
                        self.findings.append(CloudSecurityFinding(
                            cloud_provider='AWS',
                            service='CloudTrail',
                            resource_id=trail_name,
                            finding_type='Single Region Trail',
                            severity='high',
                            description=f'CloudTrail {trail_name} is not multi-region',
                            recommendation='Enable multi-region trail to capture all activity',
                            compliance_frameworks=['CIS', 'NIST'],
                            remediation_steps=[
                                'Navigate to CloudTrail console',
                                f'Select trail {trail_name}',
                                'Click Edit',
                                'Enable "Apply to all regions"'
                            ]
                        ))
                    
                    # Check log file validation
                    if not trail.get('LogFileValidationEnabled', False):
                        self.findings.append(CloudSecurityFinding(
                            cloud_provider='AWS',
                            service='CloudTrail',
                            resource_id=trail_name,
                            finding_type='Log Validation Disabled',
                            severity='medium',
                            description=f'CloudTrail {trail_name} log validation is disabled',
                            recommendation='Enable log file validation for integrity',
                            compliance_frameworks=['CIS', 'NIST', 'PCI-DSS'],
                            remediation_steps=[
                                'Navigate to CloudTrail console',
                                f'Select trail {trail_name}',
                                'Click Edit',
                                'Enable log file validation'
                            ]
                        ))
                        
        except Exception as e:
            logger.error(f"Error checking CloudTrail: {e}")
    
    def _check_encryption_settings(self):
        """Check encryption settings across services"""
        try:
            # Check EBS encryption by default
            ec2_client = self.session.client('ec2')
            
            logger.info("Checking encryption settings...")
            
            ebs_encryption = ec2_client.get_ebs_encryption_by_default()
            if not ebs_encryption.get('EbsEncryptionByDefault', False):
                self.findings.append(CloudSecurityFinding(
                    cloud_provider='AWS',
                    service='EC2',
                    resource_id='ebs-encryption',
                    finding_type='EBS Encryption Disabled',
                    severity='high',
                    description='EBS encryption by default is not enabled',
                    recommendation='Enable EBS encryption by default',
                    compliance_frameworks=['CIS', 'NIST', 'HIPAA', 'PCI-DSS'],
                    remediation_steps=[
                        'Navigate to EC2 > Account Attributes',
                        'Click EBS encryption',
                        'Enable "Always encrypt new EBS volumes"'
                    ]
                ))
                
        except Exception as e:
            logger.error(f"Error checking encryption settings: {e}")
    
    def _check_public_exposures(self):
        """Check for publicly exposed resources"""
        try:
            ec2_client = self.session.client('ec2')
            
            logger.info("Checking for public exposures...")
            
            # Check for instances with public IPs
            instances = ec2_client.describe_instances()
            
            public_instance_count = 0
            for reservation in instances.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance.get('PublicIpAddress'):
                        public_instance_count += 1
            
            if public_instance_count > 0:
                self.findings.append(CloudSecurityFinding(
                    cloud_provider='AWS',
                    service='EC2',
                    resource_id='public-instances',
                    finding_type='Public EC2 Instances',
                    severity='medium',
                    description=f'{public_instance_count} EC2 instances have public IP addresses',
                    recommendation='Review necessity of public IPs, use NAT gateway or VPN',
                    compliance_frameworks=['CIS', 'NIST'],
                    remediation_steps=[
                        'Review each instance for public access requirement',
                        'Move instances to private subnets where possible',
                        'Use NAT gateway for outbound internet access',
                        'Implement VPN for administrative access'
                    ]
                ))
                
        except Exception as e:
            logger.error(f"Error checking public exposures: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of security scan results"""
        critical = len([f for f in self.findings if f.severity == 'critical'])
        high = len([f for f in self.findings if f.severity == 'high'])
        medium = len([f for f in self.findings if f.severity == 'medium'])
        low = len([f for f in self.findings if f.severity == 'low'])
        
        # Calculate risk score (0-100, lower is better)
        risk_score = min(100, (critical * 25) + (high * 10) + (medium * 5) + (low * 2))
        
        # Determine security posture
        if risk_score >= 80:
            posture = 'Critical'
        elif risk_score >= 60:
            posture = 'High Risk'
        elif risk_score >= 40:
            posture = 'Medium Risk'
        elif risk_score >= 20:
            posture = 'Low Risk'
        else:
            posture = 'Good'
        
        return {
            'cloud_provider': 'AWS',
            'region': self.region,
            'total_findings': len(self.findings),
            'severity_breakdown': {
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            },
            'risk_score': risk_score,
            'security_posture': posture,
            'services_scanned': ['S3', 'IAM', 'EC2', 'CloudTrail'],
            'compliance_frameworks': ['CIS', 'NIST', 'PCI-DSS', 'HIPAA']
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage (requires AWS credentials)
    # scanner = AWSSecurityScanner(profile_name='default')
    # findings = scanner.scan_account()
    # summary = scanner.get_summary()
    
    print("AWS Security Scanner initialized")
    print("Note: Requires AWS credentials to perform actual scans")
    print("\nFeatures:")
    print("  • S3 bucket security analysis")
    print("  • IAM policy review")
    print("  • EC2 security group analysis")
    print("  • CloudTrail logging verification")
    print("  • Encryption checks")
    print("  • Public exposure detection")
    print("  • CIS, NIST, PCI-DSS compliance mapping")
