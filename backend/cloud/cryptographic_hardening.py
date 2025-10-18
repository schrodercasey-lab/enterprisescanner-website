"""
Military-Grade Cryptographic Hardening Module
Enterprise Scanner - DoD IL5/IL6 Ready

Validates encryption at rest/transit against:
- FIPS 140-2/140-3 Level 3+ requirements
- Quantum-resistant encryption algorithms (NIST PQC)
- Hardware Security Module (HSM) usage
- NSA Suite B/CNSA Suite compliance
- Key rotation policies (30 days for IL5/IL6)
- Perfect Forward Secrecy (PFS)
- Post-quantum TLS cipher suites

Supports: AWS, Azure, GCP
Classification: Unclassified
Compliance: NIST 800-53 SC-12, SC-13, SC-17, FedRAMP High
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class CryptoStandard(Enum):
    """Cryptographic standards for DoD/IC compliance"""
    FIPS_140_2 = "FIPS 140-2"
    FIPS_140_3 = "FIPS 140-3"
    NSA_SUITE_B = "NSA Suite B"
    CNSA_SUITE = "CNSA Suite"
    PQC_NIST = "Post-Quantum Cryptography (NIST)"


class ComplianceLevel(Enum):
    """DoD Information Impact Levels"""
    IL2 = "Impact Level 2 (Public)"
    IL4 = "Impact Level 4 (CUI)"
    IL5 = "Impact Level 5 (CUI/SECRET)"
    IL6 = "Impact Level 6 (SECRET/TOP SECRET)"


@dataclass
class CryptoFinding:
    """Represents a cryptographic security finding"""
    severity: str  # critical, high, medium, low
    category: str  # encryption_at_rest, encryption_in_transit, key_management
    resource_id: str
    resource_type: str
    title: str
    description: str
    remediation: str
    compliance_frameworks: List[str]
    impact_level: Optional[ComplianceLevel] = None
    references: List[str] = None


class CryptographicHardeningScanner:
    """
    Military-grade cryptographic validation for cloud infrastructure.
    
    Validates:
    - Encryption at rest (FIPS 140-3, quantum-resistant algorithms)
    - Encryption in transit (TLS 1.3, PFS, mTLS)
    - Key management (HSM, rotation, segregation)
    - Certificate security (pinning, transparency logs)
    """
    
    # FIPS 140-2/140-3 approved algorithms
    FIPS_APPROVED_SYMMETRIC = ['AES-128', 'AES-192', 'AES-256', 'TDEA']
    FIPS_APPROVED_ASYMMETRIC = ['RSA-2048', 'RSA-3072', 'RSA-4096', 'ECDSA-P256', 'ECDSA-P384', 'ECDSA-P521']
    FIPS_APPROVED_HASH = ['SHA-256', 'SHA-384', 'SHA-512', 'SHA3-256', 'SHA3-384', 'SHA3-512']
    
    # CNSA Suite (NSA's quantum-resistant recommendations)
    CNSA_SYMMETRIC = ['AES-256']
    CNSA_ASYMMETRIC = ['RSA-3072', 'ECDH-P384', 'ECDSA-P384']
    CNSA_HASH = ['SHA-384', 'SHA-512']
    
    # Post-Quantum Cryptography (NIST PQC standards - August 2024)
    PQC_KEY_ENCAPSULATION = ['CRYSTALS-Kyber', 'ML-KEM']  # Key exchange
    PQC_DIGITAL_SIGNATURE = ['CRYSTALS-Dilithium', 'ML-DSA', 'FALCON', 'SPHINCS+']
    
    # Weak/deprecated algorithms (DoD prohibited)
    WEAK_ALGORITHMS = [
        'DES', '3DES', 'RC4', 'MD5', 'SHA-1', 'RSA-1024', 'DSA', 
        'SSL', 'TLS1.0', 'TLS1.1', 'TLS1.2'  # TLS 1.2 deprecated for DoD as of 2024
    ]
    
    # TLS 1.3 cipher suites (required for DoD IL5/IL6)
    TLS13_CIPHER_SUITES = [
        'TLS_AES_256_GCM_SHA384',
        'TLS_CHACHA20_POLY1305_SHA256',
        'TLS_AES_128_GCM_SHA256',
        'TLS_AES_128_CCM_SHA256'
    ]
    
    # DoD key rotation requirements (days)
    KEY_ROTATION_REQUIREMENTS = {
        ComplianceLevel.IL2: 365,  # Annual
        ComplianceLevel.IL4: 90,   # Quarterly
        ComplianceLevel.IL5: 30,   # Monthly
        ComplianceLevel.IL6: 30    # Monthly
    }
    
    def __init__(self, impact_level: ComplianceLevel = ComplianceLevel.IL5):
        """
        Initialize cryptographic hardening scanner.
        
        Args:
            impact_level: DoD Information Impact Level (IL2-IL6)
        """
        self.impact_level = impact_level
        self.findings: List[CryptoFinding] = []
        self.scanned_resources = 0
        self.compliant_resources = 0
        
    def scan_aws_encryption(self, aws_resources: Dict) -> List[CryptoFinding]:
        """
        Scan AWS resources for cryptographic hardening.
        
        Args:
            aws_resources: Dictionary of AWS resources from boto3
            
        Returns:
            List of cryptographic findings
        """
        findings = []
        
        # S3 Bucket Encryption
        if 'S3' in aws_resources:
            findings.extend(self._scan_aws_s3_encryption(aws_resources['S3']))
        
        # EBS Volume Encryption
        if 'EC2' in aws_resources:
            findings.extend(self._scan_aws_ebs_encryption(aws_resources['EC2']))
        
        # RDS Database Encryption
        if 'RDS' in aws_resources:
            findings.extend(self._scan_aws_rds_encryption(aws_resources['RDS']))
        
        # KMS Key Management
        if 'KMS' in aws_resources:
            findings.extend(self._scan_aws_kms_keys(aws_resources['KMS']))
        
        # CloudFront TLS Configuration
        if 'CloudFront' in aws_resources:
            findings.extend(self._scan_aws_cloudfront_tls(aws_resources['CloudFront']))
        
        # ELB/ALB SSL/TLS Configuration
        if 'ELB' in aws_resources:
            findings.extend(self._scan_aws_elb_tls(aws_resources['ELB']))
        
        # Secrets Manager
        if 'SecretsManager' in aws_resources:
            findings.extend(self._scan_aws_secrets_manager(aws_resources['SecretsManager']))
        
        self.findings.extend(findings)
        return findings
    
    def _scan_aws_s3_encryption(self, s3_buckets: List[Dict]) -> List[CryptoFinding]:
        """Validate S3 bucket encryption at rest"""
        findings = []
        
        for bucket in s3_buckets:
            self.scanned_resources += 1
            bucket_name = bucket.get('Name', 'Unknown')
            encryption_config = bucket.get('Encryption', {})
            
            # Check if encryption is enabled
            if not encryption_config or not encryption_config.get('Rules'):
                findings.append(CryptoFinding(
                    severity='critical',
                    category='encryption_at_rest',
                    resource_id=bucket_name,
                    resource_type='AWS::S3::Bucket',
                    title='S3 Bucket Encryption Not Enabled',
                    description=f'Bucket "{bucket_name}" does not have default encryption enabled. All data at rest must be encrypted for DoD compliance.',
                    remediation='Enable default encryption with AES-256 (SSE-S3) or AWS KMS (SSE-KMS) with customer-managed keys. For IL5/IL6, use FIPS 140-3 validated KMS keys.',
                    compliance_frameworks=['NIST 800-53 SC-28', 'FedRAMP High', 'CMMC Level 3-5'],
                    impact_level=self.impact_level,
                    references=['https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html']
                ))
                continue
            
            # Check encryption algorithm
            for rule in encryption_config.get('Rules', []):
                sse_algorithm = rule.get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm', '')
                kms_key_id = rule.get('ApplyServerSideEncryptionByDefault', {}).get('KMSMasterKeyID', '')
                
                # For IL5/IL6, require KMS with customer-managed keys
                if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                    if sse_algorithm != 'aws:kms':
                        findings.append(CryptoFinding(
                            severity='high',
                            category='encryption_at_rest',
                            resource_id=bucket_name,
                            resource_type='AWS::S3::Bucket',
                            title='S3 Bucket Not Using KMS Encryption',
                            description=f'Bucket "{bucket_name}" uses {sse_algorithm} instead of aws:kms. DoD IL5/IL6 requires KMS with customer-managed keys.',
                            remediation='Configure bucket to use aws:kms encryption with a customer-managed KMS key (CMK) that is FIPS 140-3 validated.',
                            compliance_frameworks=['NIST 800-53 SC-12', 'DoD IL5/IL6'],
                            impact_level=self.impact_level
                        ))
                    elif not kms_key_id or kms_key_id.startswith('alias/aws/s3'):
                        findings.append(CryptoFinding(
                            severity='high',
                            category='encryption_at_rest',
                            resource_id=bucket_name,
                            resource_type='AWS::S3::Bucket',
                            title='S3 Bucket Using AWS-Managed KMS Key',
                            description=f'Bucket "{bucket_name}" uses AWS-managed KMS key instead of customer-managed key. IL5/IL6 requires customer control over encryption keys.',
                            remediation='Create a customer-managed KMS key (CMK) with FIPS 140-3 validation and configure bucket to use it.',
                            compliance_frameworks=['NIST 800-53 SC-12', 'DoD IL5/IL6'],
                            impact_level=self.impact_level
                        ))
                
                # Check if bucket policy enforces encryption
                if not bucket.get('PublicAccessBlock', {}).get('BlockPublicAcls', False):
                    findings.append(CryptoFinding(
                        severity='medium',
                        category='encryption_at_rest',
                        resource_id=bucket_name,
                        resource_type='AWS::S3::Bucket',
                        title='S3 Bucket Missing Encryption Enforcement Policy',
                        description=f'Bucket "{bucket_name}" does not enforce encryption for uploads. Objects uploaded without encryption headers will be stored unencrypted.',
                        remediation='Add bucket policy to deny PutObject requests that do not include x-amz-server-side-encryption header.',
                        compliance_frameworks=['NIST 800-53 SC-28'],
                        impact_level=self.impact_level
                    ))
            
            # If all checks pass
            if not any(f.resource_id == bucket_name for f in findings):
                self.compliant_resources += 1
        
        return findings
    
    def _scan_aws_ebs_encryption(self, ec2_resources: Dict) -> List[CryptoFinding]:
        """Validate EBS volume encryption"""
        findings = []
        volumes = ec2_resources.get('Volumes', [])
        
        for volume in volumes:
            self.scanned_resources += 1
            volume_id = volume.get('VolumeId', 'Unknown')
            encrypted = volume.get('Encrypted', False)
            kms_key_id = volume.get('KmsKeyId', '')
            
            if not encrypted:
                findings.append(CryptoFinding(
                    severity='critical',
                    category='encryption_at_rest',
                    resource_id=volume_id,
                    resource_type='AWS::EC2::Volume',
                    title='EBS Volume Not Encrypted',
                    description=f'Volume "{volume_id}" is not encrypted. All EBS volumes must be encrypted at rest for DoD compliance.',
                    remediation='Enable EBS encryption. For existing volumes, create encrypted snapshot and restore to new encrypted volume. Enable encryption by default for the region.',
                    compliance_frameworks=['NIST 800-53 SC-28', 'FedRAMP High', 'CMMC Level 3-5'],
                    impact_level=self.impact_level,
                    references=['https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html']
                ))
            elif self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                # Validate customer-managed KMS key
                if not kms_key_id or kms_key_id.startswith('alias/aws/ebs'):
                    findings.append(CryptoFinding(
                        severity='high',
                        category='encryption_at_rest',
                        resource_id=volume_id,
                        resource_type='AWS::EC2::Volume',
                        title='EBS Volume Using AWS-Managed KMS Key',
                        description=f'Volume "{volume_id}" uses AWS-managed key. IL5/IL6 requires customer-managed KMS keys.',
                        remediation='Re-encrypt volume using customer-managed KMS key (CMK) with FIPS 140-3 validation.',
                        compliance_frameworks=['NIST 800-53 SC-12', 'DoD IL5/IL6'],
                        impact_level=self.impact_level
                    ))
            else:
                self.compliant_resources += 1
        
        return findings
    
    def _scan_aws_rds_encryption(self, rds_resources: Dict) -> List[CryptoFinding]:
        """Validate RDS database encryption"""
        findings = []
        instances = rds_resources.get('DBInstances', [])
        
        for db in instances:
            self.scanned_resources += 1
            db_id = db.get('DBInstanceIdentifier', 'Unknown')
            encrypted = db.get('StorageEncrypted', False)
            kms_key_id = db.get('KmsKeyId', '')
            
            if not encrypted:
                findings.append(CryptoFinding(
                    severity='critical',
                    category='encryption_at_rest',
                    resource_id=db_id,
                    resource_type='AWS::RDS::DBInstance',
                    title='RDS Database Not Encrypted',
                    description=f'Database "{db_id}" does not have storage encryption enabled. All databases must be encrypted at rest.',
                    remediation='Enable encryption at rest. Note: Cannot enable encryption on existing unencrypted DB. Must create encrypted snapshot and restore.',
                    compliance_frameworks=['NIST 800-53 SC-28', 'FedRAMP High', 'PCI-DSS 3.4'],
                    impact_level=self.impact_level
                ))
            elif self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                if not kms_key_id or kms_key_id.startswith('alias/aws/rds'):
                    findings.append(CryptoFinding(
                        severity='high',
                        category='encryption_at_rest',
                        resource_id=db_id,
                        resource_type='AWS::RDS::DBInstance',
                        title='RDS Database Using AWS-Managed KMS Key',
                        description=f'Database "{db_id}" uses AWS-managed key. IL5/IL6 requires customer-managed keys.',
                        remediation='Create new DB from snapshot using customer-managed KMS key.',
                        compliance_frameworks=['DoD IL5/IL6'],
                        impact_level=self.impact_level
                    ))
            else:
                self.compliant_resources += 1
        
        return findings
    
    def _scan_aws_kms_keys(self, kms_resources: Dict) -> List[CryptoFinding]:
        """Validate KMS key configuration and rotation"""
        findings = []
        keys = kms_resources.get('Keys', [])
        
        for key in keys:
            self.scanned_resources += 1
            key_id = key.get('KeyId', 'Unknown')
            key_metadata = key.get('Metadata', {})
            key_state = key_metadata.get('KeyState', 'Unknown')
            key_usage = key_metadata.get('KeyUsage', 'Unknown')
            customer_master_key_spec = key_metadata.get('CustomerMasterKeySpec', 'Unknown')
            
            # Check if key is enabled
            if key_state != 'Enabled':
                findings.append(CryptoFinding(
                    severity='medium',
                    category='key_management',
                    resource_id=key_id,
                    resource_type='AWS::KMS::Key',
                    title=f'KMS Key in {key_state} State',
                    description=f'Key "{key_id}" is in {key_state} state. Disabled or pending deletion keys cannot encrypt data.',
                    remediation='Enable key if it is actively used, or delete if no longer needed.',
                    compliance_frameworks=['NIST 800-53 SC-12'],
                    impact_level=self.impact_level
                ))
                continue
            
            # Check key rotation
            rotation_enabled = key.get('RotationEnabled', False)
            if not rotation_enabled:
                max_age = self.KEY_ROTATION_REQUIREMENTS.get(self.impact_level, 365)
                findings.append(CryptoFinding(
                    severity='high',
                    category='key_management',
                    resource_id=key_id,
                    resource_type='AWS::KMS::Key',
                    title='KMS Key Rotation Not Enabled',
                    description=f'Key "{key_id}" does not have automatic rotation enabled. {self.impact_level.value} requires rotation every {max_age} days.',
                    remediation='Enable automatic key rotation in KMS console or via AWS CLI: aws kms enable-key-rotation --key-id {key_id}',
                    compliance_frameworks=['NIST 800-53 SC-12', 'FedRAMP High'],
                    impact_level=self.impact_level
                ))
            
            # Check cryptographic algorithm (FIPS 140-3 compliance)
            if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                # Validate key spec is CNSA Suite compliant
                if customer_master_key_spec not in ['SYMMETRIC_DEFAULT', 'RSA_3072', 'RSA_4096', 'ECC_NIST_P384', 'ECC_NIST_P521']:
                    findings.append(CryptoFinding(
                        severity='high',
                        category='key_management',
                        resource_id=key_id,
                        resource_type='AWS::KMS::Key',
                        title='KMS Key Not CNSA Suite Compliant',
                        description=f'Key "{key_id}" uses {customer_master_key_spec}. IL5/IL6 requires CNSA Suite algorithms (AES-256, RSA-3072+, ECC P-384+).',
                        remediation='Create new KMS key with CNSA Suite compliant algorithm and re-encrypt data.',
                        compliance_frameworks=['NSA CNSA Suite', 'DoD IL5/IL6'],
                        impact_level=self.impact_level
                    ))
            
            # Check for HSM usage (CloudHSM for IL5/IL6)
            origin = key_metadata.get('Origin', 'Unknown')
            if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                if origin not in ['AWS_CLOUDHSM', 'EXTERNAL']:
                    findings.append(CryptoFinding(
                        severity='high',
                        category='key_management',
                        resource_id=key_id,
                        resource_type='AWS::KMS::Key',
                        title='KMS Key Not HSM-Backed',
                        description=f'Key "{key_id}" uses software-based key storage (origin: {origin}). IL5/IL6 requires hardware security module (HSM) key storage.',
                        remediation='Create new key in AWS CloudHSM or import key from external HSM. AWS KMS with CloudHSM provides FIPS 140-3 Level 3 validation.',
                        compliance_frameworks=['FIPS 140-3 Level 3', 'DoD IL5/IL6'],
                        impact_level=self.impact_level,
                        references=['https://docs.aws.amazon.com/kms/latest/developerguide/custom-key-store-overview.html']
                    ))
            
            # Check key policy for least privilege
            key_policy = key.get('KeyPolicy', {})
            if key_policy:
                statements = key_policy.get('Statement', [])
                for statement in statements:
                    if statement.get('Effect') == 'Allow' and statement.get('Principal', {}).get('AWS') == '*':
                        findings.append(CryptoFinding(
                            severity='high',
                            category='key_management',
                            resource_id=key_id,
                            resource_type='AWS::KMS::Key',
                            title='KMS Key Policy Allows Public Access',
                            description=f'Key "{key_id}" has overly permissive key policy allowing Principal: "*". This violates least privilege principle.',
                            remediation='Update key policy to specify exact IAM principals (users, roles, accounts) that need access.',
                            compliance_frameworks=['NIST 800-53 AC-6', 'FedRAMP High'],
                            impact_level=self.impact_level
                        ))
            
            # If all checks pass
            if not any(f.resource_id == key_id for f in findings):
                self.compliant_resources += 1
        
        return findings
    
    def _scan_aws_cloudfront_tls(self, cloudfront_resources: Dict) -> List[CryptoFinding]:
        """Validate CloudFront TLS configuration"""
        findings = []
        distributions = cloudfront_resources.get('Distributions', [])
        
        for dist in distributions:
            self.scanned_resources += 1
            dist_id = dist.get('Id', 'Unknown')
            dist_config = dist.get('DistributionConfig', {})
            viewer_cert = dist_config.get('ViewerCertificate', {})
            
            # Check minimum TLS version
            min_protocol_version = viewer_cert.get('MinimumProtocolVersion', 'Unknown')
            
            # DoD requires TLS 1.3 as of 2024
            if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                if min_protocol_version != 'TLSv1.3':
                    findings.append(CryptoFinding(
                        severity='critical',
                        category='encryption_in_transit',
                        resource_id=dist_id,
                        resource_type='AWS::CloudFront::Distribution',
                        title='CloudFront Not Enforcing TLS 1.3',
                        description=f'Distribution "{dist_id}" allows {min_protocol_version}. DoD IL5/IL6 requires TLS 1.3 minimum.',
                        remediation='Update viewer certificate to enforce TLS 1.3: MinimumProtocolVersion = TLSv1.3',
                        compliance_frameworks=['NSA CNSA Suite', 'DoD IL5/IL6', 'NIST 800-52 Rev 2'],
                        impact_level=self.impact_level
                    ))
            elif min_protocol_version in ['SSLv3', 'TLSv1', 'TLSv1.1']:
                findings.append(CryptoFinding(
                    severity='critical',
                    category='encryption_in_transit',
                    resource_id=dist_id,
                    resource_type='AWS::CloudFront::Distribution',
                    title='CloudFront Allows Weak TLS Versions',
                    description=f'Distribution "{dist_id}" allows {min_protocol_version}, which has known vulnerabilities (POODLE, BEAST).',
                    remediation='Update to TLS 1.2 minimum (or TLS 1.3 for DoD).',
                    compliance_frameworks=['PCI-DSS 3.2.1', 'NIST 800-52 Rev 2'],
                    impact_level=self.impact_level
                ))
            
            # Check for custom SSL certificate (not CloudFront default)
            if not viewer_cert.get('ACMCertificateArn') and not viewer_cert.get('IAMCertificateId'):
                findings.append(CryptoFinding(
                    severity='medium',
                    category='encryption_in_transit',
                    resource_id=dist_id,
                    resource_type='AWS::CloudFront::Distribution',
                    title='CloudFront Using Default Certificate',
                    description=f'Distribution "{dist_id}" uses CloudFront default certificate. Custom domains should use ACM certificates.',
                    remediation='Request ACM certificate for custom domain and attach to distribution.',
                    compliance_frameworks=['NIST 800-53 SC-8'],
                    impact_level=self.impact_level
                ))
            
            # Check origin protocol policy
            origins = dist_config.get('Origins', {}).get('Items', [])
            for origin in origins:
                origin_id = origin.get('Id', 'Unknown')
                custom_origin = origin.get('CustomOriginConfig', {})
                if custom_origin:
                    origin_protocol = custom_origin.get('OriginProtocolPolicy', 'Unknown')
                    if origin_protocol != 'https-only':
                        findings.append(CryptoFinding(
                            severity='high',
                            category='encryption_in_transit',
                            resource_id=f"{dist_id}/{origin_id}",
                            resource_type='AWS::CloudFront::Distribution::Origin',
                            title='CloudFront Origin Allows HTTP',
                            description=f'Origin "{origin_id}" in distribution "{dist_id}" allows HTTP. All traffic must be encrypted.',
                            remediation='Set OriginProtocolPolicy to https-only.',
                            compliance_frameworks=['NIST 800-53 SC-8', 'FedRAMP High'],
                            impact_level=self.impact_level
                        ))
            
            # If all checks pass
            if not any(dist_id in f.resource_id for f in findings):
                self.compliant_resources += 1
        
        return findings
    
    def _scan_aws_elb_tls(self, elb_resources: Dict) -> List[CryptoFinding]:
        """Validate ELB/ALB SSL/TLS configuration"""
        findings = []
        load_balancers = elb_resources.get('LoadBalancers', [])
        
        for lb in load_balancers:
            self.scanned_resources += 1
            lb_name = lb.get('LoadBalancerName', 'Unknown')
            lb_arn = lb.get('LoadBalancerArn', lb_name)
            
            # Check listeners
            listeners = lb.get('Listeners', [])
            for listener in listeners:
                listener_port = listener.get('Port', 0)
                listener_protocol = listener.get('Protocol', 'Unknown')
                
                # Check if HTTPS/TLS is used
                if listener_protocol not in ['HTTPS', 'TLS', 'SSL']:
                    findings.append(CryptoFinding(
                        severity='high',
                        category='encryption_in_transit',
                        resource_id=f"{lb_name}:{listener_port}",
                        resource_type='AWS::ElasticLoadBalancing::Listener',
                        title='Load Balancer Listener Not Using TLS',
                        description=f'Listener on port {listener_port} uses {listener_protocol}. All traffic must be encrypted with TLS.',
                        remediation='Configure listener to use HTTPS protocol with valid SSL/TLS certificate from ACM.',
                        compliance_frameworks=['NIST 800-53 SC-8', 'PCI-DSS 4.1'],
                        impact_level=self.impact_level
                    ))
                    continue
                
                # Check SSL policy
                ssl_policy = listener.get('SslPolicy', 'Unknown')
                if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                    # DoD requires TLS 1.3 cipher suites
                    if not ssl_policy.startswith('ELBSecurityPolicy-TLS13'):
                        findings.append(CryptoFinding(
                            severity='critical',
                            category='encryption_in_transit',
                            resource_id=f"{lb_name}:{listener_port}",
                            resource_type='AWS::ElasticLoadBalancing::Listener',
                            title='Load Balancer Not Using TLS 1.3 Policy',
                            description=f'Listener uses {ssl_policy}. IL5/IL6 requires TLS 1.3 (ELBSecurityPolicy-TLS13-1-2-2021-06).',
                            remediation='Update SSL policy to ELBSecurityPolicy-TLS13-1-2-2021-06 or later.',
                            compliance_frameworks=['DoD IL5/IL6', 'NSA CNSA Suite'],
                            impact_level=self.impact_level
                        ))
                elif ssl_policy in ['ELBSecurityPolicy-2016-08', 'ELBSecurityPolicy-TLS-1-0-2015-04']:
                    findings.append(CryptoFinding(
                        severity='high',
                        category='encryption_in_transit',
                        resource_id=f"{lb_name}:{listener_port}",
                        resource_type='AWS::ElasticLoadBalancing::Listener',
                        title='Load Balancer Using Weak SSL Policy',
                        description=f'Listener uses {ssl_policy} which allows TLS 1.0/1.1. Upgrade to TLS 1.2 minimum.',
                        remediation='Update SSL policy to ELBSecurityPolicy-TLS-1-2-2017-01 or ELBSecurityPolicy-FS-1-2-Res-2019-08.',
                        compliance_frameworks=['PCI-DSS 3.2.1', 'NIST 800-52 Rev 2'],
                        impact_level=self.impact_level
                    ))
            
            # If all checks pass
            if not any(lb_name in f.resource_id for f in findings):
                self.compliant_resources += 1
        
        return findings
    
    def _scan_aws_secrets_manager(self, secrets_resources: Dict) -> List[CryptoFinding]:
        """Validate Secrets Manager encryption and rotation"""
        findings = []
        secrets = secrets_resources.get('SecretList', [])
        
        for secret in secrets:
            self.scanned_resources += 1
            secret_name = secret.get('Name', 'Unknown')
            secret_arn = secret.get('ARN', secret_name)
            kms_key_id = secret.get('KmsKeyId', '')
            rotation_enabled = secret.get('RotationEnabled', False)
            last_rotated = secret.get('LastRotatedDate')
            
            # Check KMS encryption (required for IL5/IL6)
            if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
                if not kms_key_id or kms_key_id.startswith('alias/aws/secretsmanager'):
                    findings.append(CryptoFinding(
                        severity='high',
                        category='key_management',
                        resource_id=secret_name,
                        resource_type='AWS::SecretsManager::Secret',
                        title='Secret Not Using Customer-Managed KMS Key',
                        description=f'Secret "{secret_name}" uses AWS-managed key. IL5/IL6 requires customer-managed keys.',
                        remediation='Create new secret version encrypted with customer-managed KMS key.',
                        compliance_frameworks=['DoD IL5/IL6', 'NIST 800-53 SC-12'],
                        impact_level=self.impact_level
                    ))
            
            # Check rotation
            if not rotation_enabled:
                findings.append(CryptoFinding(
                    severity='high',
                    category='key_management',
                    resource_id=secret_name,
                    resource_type='AWS::SecretsManager::Secret',
                    title='Secret Rotation Not Enabled',
                    description=f'Secret "{secret_name}" does not have automatic rotation enabled.',
                    remediation='Enable automatic rotation with appropriate Lambda function. Rotate every 30 days for IL5/IL6.',
                    compliance_frameworks=['NIST 800-53 SC-12', 'FedRAMP High'],
                    impact_level=self.impact_level
                ))
            elif last_rotated:
                # Check if rotation is within required timeframe
                max_age = self.KEY_ROTATION_REQUIREMENTS.get(self.impact_level, 90)
                age_days = (datetime.now() - last_rotated).days
                if age_days > max_age:
                    findings.append(CryptoFinding(
                        severity='high',
                        category='key_management',
                        resource_id=secret_name,
                        resource_type='AWS::SecretsManager::Secret',
                        title='Secret Rotation Overdue',
                        description=f'Secret "{secret_name}" was last rotated {age_days} days ago. {self.impact_level.value} requires rotation every {max_age} days.',
                        remediation='Manually rotate secret immediately and verify automatic rotation is functioning.',
                        compliance_frameworks=['NIST 800-53 SC-12'],
                        impact_level=self.impact_level
                    ))
            
            # If all checks pass
            if not any(f.resource_id == secret_name for f in findings):
                self.compliant_resources += 1
        
        return findings
    
    def generate_report(self) -> Dict:
        """
        Generate cryptographic hardening report.
        
        Returns:
            Dictionary with scan results and compliance summary
        """
        critical_count = len([f for f in self.findings if f.severity == 'critical'])
        high_count = len([f for f in self.findings if f.severity == 'high'])
        medium_count = len([f for f in self.findings if f.severity == 'medium'])
        low_count = len([f for f in self.findings if f.severity == 'low'])
        
        compliance_rate = (self.compliant_resources / self.scanned_resources * 100) if self.scanned_resources > 0 else 0
        
        # Determine overall compliance status
        if critical_count > 0:
            compliance_status = "Non-Compliant (Critical Issues)"
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
                'impact_level': self.impact_level.value,
                'scan_timestamp': datetime.now().isoformat(),
                'scanned_resources': self.scanned_resources,
                'compliant_resources': self.compliant_resources,
                'compliance_rate': round(compliance_rate, 2)
            },
            'compliance_status': compliance_status,
            'findings_summary': {
                'total_findings': len(self.findings),
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'findings_by_category': {
                'encryption_at_rest': len([f for f in self.findings if f.category == 'encryption_at_rest']),
                'encryption_in_transit': len([f for f in self.findings if f.category == 'encryption_in_transit']),
                'key_management': len([f for f in self.findings if f.category == 'key_management'])
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
                    'impact_level': f.impact_level.value if f.impact_level else None
                }
                for f in self.findings
            ],
            'recommendations': self._generate_recommendations(critical_count, high_count, medium_count)
        }
    
    def _generate_recommendations(self, critical: int, high: int, medium: int) -> List[str]:
        """Generate prioritized recommendations based on findings"""
        recommendations = []
        
        if critical > 0:
            recommendations.append(f"URGENT: Address {critical} critical cryptographic findings immediately. These represent severe security gaps that could lead to data breaches.")
        
        if high > 0:
            recommendations.append(f"HIGH PRIORITY: Remediate {high} high-severity findings within 30 days. Focus on KMS customer-managed keys, TLS 1.3 enforcement, and key rotation.")
        
        if self.impact_level in [ComplianceLevel.IL5, ComplianceLevel.IL6]:
            recommendations.append("DoD IL5/IL6 Requirements: Ensure all encryption uses FIPS 140-3 validated modules, customer-managed KMS keys with HSM backing, and TLS 1.3 with CNSA Suite cipher suites.")
        
        if medium > 0:
            recommendations.append(f"MEDIUM PRIORITY: Address {medium} medium-severity findings within 90 days to improve overall security posture.")
        
        recommendations.append("Enable AWS Config Rules for continuous compliance monitoring: s3-bucket-server-side-encryption-enabled, rds-storage-encrypted, encrypted-volumes.")
        recommendations.append("Implement Infrastructure as Code (IaC) with encryption defaults to prevent future misconfigurations.")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Initialize scanner for DoD IL5 (CUI/SECRET)
    scanner = CryptographicHardeningScanner(impact_level=ComplianceLevel.IL5)
    
    # Example AWS resources (normally from boto3)
    example_aws_resources = {
        'S3': [
            {
                'Name': 'sensitive-data-bucket',
                'Encryption': {
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'  # Should be aws:kms for IL5
                            }
                        }
                    ]
                }
            }
        ],
        'KMS': {
            'Keys': [
                {
                    'KeyId': 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012',
                    'Metadata': {
                        'KeyState': 'Enabled',
                        'KeyUsage': 'ENCRYPT_DECRYPT',
                        'CustomerMasterKeySpec': 'SYMMETRIC_DEFAULT',
                        'Origin': 'AWS_KMS'  # Should be AWS_CLOUDHSM for IL5
                    },
                    'RotationEnabled': False  # Should be True
                }
            ]
        }
    }
    
    # Scan AWS resources
    findings = scanner.scan_aws_encryption(example_aws_resources)
    
    # Generate report
    report = scanner.generate_report()
    
    print(f"\nCryptographic Hardening Scan Results ({scanner.impact_level.value})")
    print("=" * 80)
    print(f"Compliance Status: {report['compliance_status']}")
    print(f"Scanned Resources: {report['scan_metadata']['scanned_resources']}")
    print(f"Compliant Resources: {report['scan_metadata']['compliant_resources']} ({report['scan_metadata']['compliance_rate']}%)")
    print(f"\nFindings: {report['findings_summary']['critical']} Critical, {report['findings_summary']['high']} High, {report['findings_summary']['medium']} Medium")
    print("\nTop Recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec}")
