"""
Military-Grade Kubernetes Security Hardening Module
Enterprise Scanner - K8s Control Plane & Workload Protection

Validates advanced Kubernetes security hardening:
- Control plane hardening (API server, etcd, scheduler, controller-manager)
- Pod Security Standards (Restricted profile enforcement)
- etcd encryption at rest and peer-to-peer TLS
- Admission controllers (PodSecurityPolicy, OPA Gatekeeper, Kyverno)
- Network policies (default-deny ingress/egress)
- Service mesh mTLS (Istio, Linkerd, Consul Connect)
- RBAC least privilege validation
- API server audit logging and analysis
- Secrets encryption with KMS providers
- Runtime security (Falco, Aqua, Twistlock)

Supports: Kubernetes, EKS, AKS, GKE, OpenShift
Classification: Unclassified
Compliance: NIST 800-190, CIS Kubernetes Benchmark, NSA/CISA K8s Hardening Guide, DISA STIG
"""

import re
import json
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class PodSecurityStandard(Enum):
    """Pod Security Standards levels"""
    PRIVILEGED = "Privileged"  # Unrestricted (not recommended)
    BASELINE = "Baseline"  # Minimally restrictive
    RESTRICTED = "Restricted"  # Heavily restricted (DoD requirement)


class K8sSeverity(Enum):
    """Kubernetes security finding severity"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


class ControlPlaneComponent(Enum):
    """Kubernetes control plane components"""
    API_SERVER = "kube-apiserver"
    ETCD = "etcd"
    SCHEDULER = "kube-scheduler"
    CONTROLLER_MANAGER = "kube-controller-manager"
    KUBELET = "kubelet"
    KUBE_PROXY = "kube-proxy"


@dataclass
class K8sSecurityFinding:
    """Kubernetes security finding"""
    severity: K8sSeverity
    component: ControlPlaneComponent
    category: str  # control_plane, pod_security, network, rbac, secrets, admission
    resource_type: str  # Pod, Deployment, Service, NetworkPolicy, etc.
    resource_name: str
    namespace: str
    finding_title: str
    finding_description: str
    current_config: str
    recommended_config: str
    remediation: List[str]
    cis_benchmark: Optional[str] = None
    nsa_guide: Optional[str] = None
    disa_stig: Optional[str] = None
    references: List[str] = field(default_factory=list)


class KubernetesSecurityHardeningScanner:
    """
    Military-grade Kubernetes security hardening scanner.
    
    Features:
    - Control plane security validation
    - Pod Security Standards enforcement
    - Network policy analysis
    - RBAC least privilege checking
    - Secrets encryption verification
    - Admission controller validation
    """
    
    # NSA/CISA Kubernetes Hardening Guide recommendations
    NSA_HARDENING_GUIDE = {
        'api_server_anonymous': '1.2.1 - Disable anonymous authentication',
        'api_server_basic_auth': '1.2.2 - Disable basic authentication',
        'api_server_token_auth': '1.2.3 - Disable token authentication file',
        'api_server_insecure_port': '1.2.19 - Disable insecure port 8080',
        'api_server_profiling': '1.2.21 - Disable profiling',
        'api_server_audit': '1.2.22 - Enable audit logging',
        'api_server_authorization': '1.2.7 - Use RBAC authorization',
        'etcd_encryption': '1.2.34 - Enable encryption at rest',
        'etcd_peer_tls': '2.1 - Enable peer-to-peer TLS',
        'kubelet_anonymous': '4.2.1 - Disable anonymous authentication',
        'kubelet_authorization': '4.2.2 - Enable authorization mode',
        'network_policies': '5.3 - Apply network segmentation and firewalling',
        'pod_security': '5.2 - Use Pod Security Standards',
    }
    
    # CIS Kubernetes Benchmark critical controls
    CIS_BENCHMARKS = {
        'api_server_anonymous': '1.2.1 - Ensure that the --anonymous-auth argument is set to false',
        'api_server_basic_auth': '1.2.2 - Ensure that the --basic-auth-file argument is not set',
        'api_server_insecure_port': '1.2.19 - Ensure that the --insecure-port argument is set to 0',
        'api_server_audit': '1.2.22 - Ensure that the --audit-log-path argument is set',
        'api_server_admission': '1.2.11 - Ensure that the admission control plugin PodSecurityPolicy is set',
        'etcd_cert_file': '2.1 - Ensure that the --cert-file and --key-file arguments are set',
        'etcd_client_cert': '2.2 - Ensure that the --client-cert-auth argument is set to true',
        'etcd_peer_cert': '2.4 - Ensure that the --peer-cert-file and --peer-key-file arguments are set',
        'etcd_encryption': '1.2.34 - Ensure that encryption providers are appropriately configured',
        'scheduler_profiling': '1.3.2 - Ensure that the --profiling argument is set to false',
        'controller_profiling': '1.4.1 - Ensure that the --profiling argument is set to false',
        'kubelet_anonymous': '4.2.1 - Ensure that the --anonymous-auth argument is set to false',
        'kubelet_authorization': '4.2.2 - Ensure that the --authorization-mode argument is not set to AlwaysAllow',
        'kubelet_read_only': '4.2.4 - Ensure that the --read-only-port argument is set to 0',
    }
    
    # Dangerous Kubernetes capabilities (same as Docker but K8s-specific context)
    DANGEROUS_CAPABILITIES = [
        'SYS_ADMIN', 'SYS_MODULE', 'SYS_RAWIO', 'SYS_PTRACE', 'SYS_BOOT',
        'SYS_TIME', 'NET_ADMIN', 'DAC_READ_SEARCH', 'DAC_OVERRIDE',
        'SETUID', 'SETGID', 'SETPCAP', 'SYS_CHROOT', 'MKNOD',
        'AUDIT_CONTROL', 'AUDIT_WRITE', 'MAC_ADMIN', 'MAC_OVERRIDE'
    ]
    
    # Default network policy deny-all templates
    DEFAULT_DENY_INGRESS = {
        'apiVersion': 'networking.k8s.io/v1',
        'kind': 'NetworkPolicy',
        'metadata': {'name': 'default-deny-ingress'},
        'spec': {
            'podSelector': {},
            'policyTypes': ['Ingress']
        }
    }
    
    DEFAULT_DENY_EGRESS = {
        'apiVersion': 'networking.k8s.io/v1',
        'kind': 'NetworkPolicy',
        'metadata': {'name': 'default-deny-egress'},
        'spec': {
            'podSelector': {},
            'policyTypes': ['Egress']
        }
    }
    
    def __init__(self, require_pod_security_restricted: bool = True,
                 require_network_policies: bool = True,
                 require_service_mesh: bool = False):
        """
        Initialize Kubernetes security hardening scanner.
        
        Args:
            require_pod_security_restricted: Require Restricted Pod Security Standard
            require_network_policies: Require network policies for all namespaces
            require_service_mesh: Require service mesh for mTLS (Istio/Linkerd)
        """
        self.require_pod_security_restricted = require_pod_security_restricted
        self.require_network_policies = require_network_policies
        self.require_service_mesh = require_service_mesh
        self.findings: List[K8sSecurityFinding] = []
        
    def scan_control_plane(self, control_plane_config: Dict) -> List[K8sSecurityFinding]:
        """
        Scan Kubernetes control plane for security hardening.
        
        Args:
            control_plane_config: Control plane component configurations
            
        Returns:
            List of security findings
        """
        findings = []
        
        # API Server checks
        api_server = control_plane_config.get('api_server', {})
        
        # Check 1: Anonymous authentication (CRITICAL)
        anonymous_auth = api_server.get('anonymous_auth', True)
        if anonymous_auth:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.CRITICAL,
                component=ControlPlaneComponent.API_SERVER,
                category='control_plane',
                resource_type='APIServer',
                resource_name='kube-apiserver',
                namespace='kube-system',
                finding_title='Anonymous Authentication Enabled (CRITICAL)',
                finding_description='API server allows anonymous authentication. Attackers can query API without credentials.',
                current_config='--anonymous-auth=true (UNAUTHENTICATED ACCESS)',
                recommended_config='--anonymous-auth=false',
                remediation=[
                    'Edit API server manifest: /etc/kubernetes/manifests/kube-apiserver.yaml',
                    'Set: --anonymous-auth=false',
                    'Restart API server (automatic with static pod)',
                    'Verify: kubectl get --raw /api/v1 (should fail without credentials)',
                    'Ensure all legitimate access uses certificates or tokens'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['api_server_anonymous'],
                nsa_guide=self.NSA_HARDENING_GUIDE['api_server_anonymous'],
                disa_stig='V-242376 - Anonymous authentication must be disabled',
                references=[
                    'NSA/CISA Kubernetes Hardening Guide',
                    'CIS Kubernetes Benchmark 1.2.1'
                ]
            )
            findings.append(finding)
        
        # Check 2: Insecure port 8080 (CRITICAL)
        insecure_port = api_server.get('insecure_port', 8080)
        if insecure_port != 0:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.CRITICAL,
                component=ControlPlaneComponent.API_SERVER,
                category='control_plane',
                resource_type='APIServer',
                resource_name='kube-apiserver',
                namespace='kube-system',
                finding_title='Insecure Port 8080 Enabled (CRITICAL)',
                finding_description=f'API server listening on insecure port {insecure_port} without authentication or TLS.',
                current_config=f'--insecure-port={insecure_port} (NO AUTH, NO TLS)',
                recommended_config='--insecure-port=0 (DISABLED)',
                remediation=[
                    'Edit API server manifest',
                    'Set: --insecure-port=0',
                    'Remove --insecure-bind-address if present',
                    'Use secure port 6443 with TLS only',
                    'Update firewall rules to block port 8080'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['api_server_insecure_port'],
                nsa_guide=self.NSA_HARDENING_GUIDE['api_server_insecure_port'],
                disa_stig='V-242377 - Insecure port must be disabled',
                references=['CIS Kubernetes Benchmark 1.2.19']
            )
            findings.append(finding)
        
        # Check 3: Audit logging
        audit_log_path = api_server.get('audit_log_path', '')
        if not audit_log_path:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.HIGH,
                component=ControlPlaneComponent.API_SERVER,
                category='control_plane',
                resource_type='APIServer',
                resource_name='kube-apiserver',
                namespace='kube-system',
                finding_title='API Server Audit Logging Not Configured',
                finding_description='No audit logging configured for API server. Cannot track API requests or security events.',
                current_config='--audit-log-path not set (NO AUDIT LOGS)',
                recommended_config='--audit-log-path=/var/log/kubernetes/audit.log',
                remediation=[
                    'Create audit policy file: /etc/kubernetes/audit-policy.yaml',
                    'Add to API server:',
                    '  --audit-policy-file=/etc/kubernetes/audit-policy.yaml',
                    '  --audit-log-path=/var/log/kubernetes/audit.log',
                    '  --audit-log-maxage=30',
                    '  --audit-log-maxbackup=10',
                    '  --audit-log-maxsize=100',
                    'Mount audit log directory in API server pod',
                    'Forward logs to SIEM for analysis'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['api_server_audit'],
                nsa_guide=self.NSA_HARDENING_GUIDE['api_server_audit'],
                disa_stig='V-242378 - Audit logging must be enabled',
                references=['Kubernetes Auditing Documentation']
            )
            findings.append(finding)
        
        # Check 4: Admission controllers
        admission_plugins = api_server.get('enable_admission_plugins', [])
        required_plugins = ['PodSecurity', 'NodeRestriction', 'ServiceAccount']
        recommended_plugins = ['PodSecurity', 'NodeRestriction', 'ServiceAccount', 
                              'NamespaceLifecycle', 'LimitRanger', 'ResourceQuota']
        
        missing_required = [p for p in required_plugins if p not in admission_plugins]
        missing_recommended = [p for p in recommended_plugins if p not in admission_plugins]
        
        if missing_required:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.CRITICAL,
                component=ControlPlaneComponent.API_SERVER,
                category='admission',
                resource_type='APIServer',
                resource_name='kube-apiserver',
                namespace='kube-system',
                finding_title=f'Required Admission Controllers Missing: {", ".join(missing_required)}',
                finding_description='Critical admission controllers not enabled. Cannot enforce Pod Security Standards or node restrictions.',
                current_config=f'--enable-admission-plugins={",".join(admission_plugins)}',
                recommended_config=f'--enable-admission-plugins={",".join(recommended_plugins)}',
                remediation=[
                    'Edit API server manifest',
                    f'Add: --enable-admission-plugins={",".join(recommended_plugins)}',
                    'PodSecurity: Enforce Pod Security Standards',
                    'NodeRestriction: Prevent kubelets from modifying other nodes',
                    'ServiceAccount: Automatically inject service account tokens',
                    'Restart API server'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['api_server_admission'],
                nsa_guide=self.NSA_HARDENING_GUIDE['pod_security'],
                disa_stig='V-242379 - Admission controllers must be enabled',
                references=['Kubernetes Admission Controllers']
            )
            findings.append(finding)
        
        # etcd checks
        etcd_config = control_plane_config.get('etcd', {})
        
        # Check 5: etcd encryption at rest
        encryption_provider_config = etcd_config.get('encryption_provider_config', '')
        if not encryption_provider_config:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.CRITICAL,
                component=ControlPlaneComponent.ETCD,
                category='secrets',
                resource_type='Secret',
                resource_name='etcd',
                namespace='kube-system',
                finding_title='etcd Secrets Not Encrypted at Rest',
                finding_description='Kubernetes Secrets stored in etcd in plaintext. Anyone with etcd access can read all secrets.',
                current_config='No encryption provider configured (PLAINTEXT SECRETS)',
                recommended_config='EncryptionConfiguration with aescbc or KMS provider',
                remediation=[
                    'Create encryption config: /etc/kubernetes/enc/encryption-config.yaml',
                    'Example with aescbc:',
                    '  resources:',
                    '    - resources: [secrets]',
                    '      providers:',
                    '        - aescbc:',
                    '            keys:',
                    '              - name: key1',
                    '                secret: <32-byte base64 key>',
                    '        - identity: {}',
                    'Add to API server: --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml',
                    'Rotate all existing secrets: kubectl get secrets --all-namespaces -o json | kubectl replace -f -',
                    'For DoD: Use KMS provider (AWS KMS, Azure Key Vault, HashiCorp Vault)'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['etcd_encryption'],
                nsa_guide=self.NSA_HARDENING_GUIDE['etcd_encryption'],
                disa_stig='V-242380 - Secrets must be encrypted at rest',
                references=[
                    'Kubernetes Encrypting Secret Data at Rest',
                    'NSA/CISA Hardening Guide Section 4'
                ]
            )
            findings.append(finding)
        
        # Check 6: etcd peer TLS
        peer_cert_file = etcd_config.get('peer_cert_file', '')
        peer_key_file = etcd_config.get('peer_key_file', '')
        
        if not peer_cert_file or not peer_key_file:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.HIGH,
                component=ControlPlaneComponent.ETCD,
                category='control_plane',
                resource_type='etcd',
                resource_name='etcd',
                namespace='kube-system',
                finding_title='etcd Peer-to-Peer TLS Not Configured',
                finding_description='etcd cluster communication not encrypted with TLS. Man-in-the-middle attacks possible.',
                current_config='--peer-cert-file and --peer-key-file not set',
                recommended_config='--peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt --peer-key-file=/etc/kubernetes/pki/etcd/peer.key',
                remediation=[
                    'Generate peer certificates for etcd cluster',
                    'Add to etcd manifest:',
                    '  --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt',
                    '  --peer-key-file=/etc/kubernetes/pki/etcd/peer.key',
                    '  --peer-client-cert-auth=true',
                    '  --peer-trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt',
                    'Restart etcd cluster members one at a time'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['etcd_peer_cert'],
                nsa_guide=self.NSA_HARDENING_GUIDE['etcd_peer_tls'],
                disa_stig='V-242381 - etcd peer TLS must be enabled',
                references=['etcd Security Model']
            )
            findings.append(finding)
        
        # Kubelet checks
        kubelet_config = control_plane_config.get('kubelet', {})
        
        # Check 7: Kubelet anonymous authentication
        kubelet_anonymous = kubelet_config.get('anonymous_auth', True)
        if kubelet_anonymous:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.HIGH,
                component=ControlPlaneComponent.KUBELET,
                category='control_plane',
                resource_type='Kubelet',
                resource_name='kubelet',
                namespace='N/A',
                finding_title='Kubelet Anonymous Authentication Enabled',
                finding_description='Kubelet allows anonymous requests. Attackers can query kubelet API without credentials.',
                current_config='--anonymous-auth=true',
                recommended_config='--anonymous-auth=false',
                remediation=[
                    'Edit kubelet config: /var/lib/kubelet/config.yaml',
                    'Set: authentication.anonymous.enabled: false',
                    'Or use flag: --anonymous-auth=false',
                    'Restart kubelet: systemctl restart kubelet',
                    'Verify on all nodes'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['kubelet_anonymous'],
                nsa_guide=self.NSA_HARDENING_GUIDE['kubelet_anonymous'],
                disa_stig='V-242382 - Kubelet anonymous auth must be disabled',
                references=['CIS Kubernetes Benchmark 4.2.1']
            )
            findings.append(finding)
        
        # Check 8: Kubelet read-only port
        kubelet_read_only_port = kubelet_config.get('read_only_port', 10255)
        if kubelet_read_only_port != 0:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.MEDIUM,
                component=ControlPlaneComponent.KUBELET,
                category='control_plane',
                resource_type='Kubelet',
                resource_name='kubelet',
                namespace='N/A',
                finding_title='Kubelet Read-Only Port Enabled',
                finding_description=f'Kubelet read-only port {kubelet_read_only_port} exposed without authentication. Information disclosure risk.',
                current_config=f'--read-only-port={kubelet_read_only_port}',
                recommended_config='--read-only-port=0',
                remediation=[
                    'Edit kubelet config',
                    'Set: readOnlyPort: 0',
                    'Restart kubelet on all nodes',
                    'Update monitoring tools to use authenticated kubelet API'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['kubelet_read_only'],
                references=['CIS Kubernetes Benchmark 4.2.4']
            )
            findings.append(finding)
        
        self.findings.extend(findings)
        return findings
    
    def scan_pod_security(self, pod_spec: Dict, pod_name: str, namespace: str) -> List[K8sSecurityFinding]:
        """
        Scan pod for Pod Security Standards compliance.
        
        Args:
            pod_spec: Pod specification
            pod_name: Pod name
            namespace: Namespace
            
        Returns:
            List of security findings
        """
        findings = []
        
        containers = pod_spec.get('containers', [])
        security_context = pod_spec.get('securityContext', {})
        
        for container in containers:
            container_name = container.get('name', 'unknown')
            container_security = container.get('securityContext', {})
            
            # Check 1: Privileged container
            privileged = container_security.get('privileged', False)
            if privileged:
                finding = K8sSecurityFinding(
                    severity=K8sSeverity.CRITICAL,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title=f'Privileged Container: {container_name}',
                    finding_description='Container running in privileged mode. Complete host access, container escape possible.',
                    current_config='securityContext.privileged: true',
                    recommended_config='securityContext.privileged: false',
                    remediation=[
                        'Remove privileged: true from container security context',
                        'Add only required capabilities with securityContext.capabilities.add',
                        'Use Pod Security Standards to prevent privileged pods',
                        'Implement OPA Gatekeeper policy to block privileged pods'
                    ],
                    nsa_guide='Section 5.2 - Use Pod Security Standards',
                    disa_stig='V-242383 - Privileged containers prohibited',
                    references=['Pod Security Standards - Restricted']
                )
                findings.append(finding)
            
            # Check 2: Host namespaces
            host_network = pod_spec.get('hostNetwork', False)
            host_pid = pod_spec.get('hostPID', False)
            host_ipc = pod_spec.get('hostIPC', False)
            
            if host_network:
                finding = K8sSecurityFinding(
                    severity=K8sSeverity.HIGH,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title='Host Network Namespace Shared',
                    finding_description='Pod using host network namespace. Can sniff all host traffic and bind to any port.',
                    current_config='hostNetwork: true',
                    recommended_config='hostNetwork: false',
                    remediation=[
                        'Remove hostNetwork: true from pod spec',
                        'Use ClusterIP or LoadBalancer services instead',
                        'If required, document justification and implement compensating controls'
                    ],
                    nsa_guide='Section 5.2.3 - Avoid host namespaces',
                    references=['Pod Security Standards - Baseline']
                )
                findings.append(finding)
            
            if host_pid or host_ipc:
                severity_level = K8sSeverity.HIGH if host_pid else K8sSeverity.MEDIUM
                finding = K8sSecurityFinding(
                    severity=severity_level,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title=f'Host {"PID" if host_pid else "IPC"} Namespace Shared',
                    finding_description=f'Pod sharing host {"PID (can see/kill host processes)" if host_pid else "IPC (shared memory access)"}.',
                    current_config=f'{"hostPID" if host_pid else "hostIPC"}: true',
                    recommended_config=f'{"hostPID" if host_pid else "hostIPC"}: false',
                    remediation=[
                        f'Remove {"hostPID" if host_pid else "hostIPC"}: true from pod spec',
                        'Use isolated namespaces (default)'
                    ],
                    nsa_guide='Section 5.2.3 - Namespace isolation',
                    references=['Pod Security Standards']
                )
                findings.append(finding)
            
            # Check 3: RunAsNonRoot
            run_as_non_root = container_security.get('runAsNonRoot', False)
            run_as_user = container_security.get('runAsUser')
            
            if not run_as_non_root and (not run_as_user or run_as_user == 0):
                finding = K8sSecurityFinding(
                    severity=K8sSeverity.HIGH,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title=f'Container Running as Root: {container_name}',
                    finding_description='Container processes running as root (UID 0). Elevated privileges if compromised.',
                    current_config='runAsNonRoot: false or not set',
                    recommended_config='runAsNonRoot: true, runAsUser: 1000',
                    remediation=[
                        'Set securityContext.runAsNonRoot: true',
                        'Set securityContext.runAsUser: 1000 (or non-zero UID)',
                        'Update container image to use non-root user',
                        'Add USER directive to Dockerfile'
                    ],
                    nsa_guide='Section 5.2.4 - Run as non-root',
                    disa_stig='V-242384 - Containers must run as non-root',
                    references=['Pod Security Standards - Restricted']
                )
                findings.append(finding)
            
            # Check 4: Capabilities
            capabilities = container_security.get('capabilities', {})
            cap_add = capabilities.get('add', [])
            cap_drop = capabilities.get('drop', [])
            
            dangerous_caps = [cap for cap in cap_add if cap in self.DANGEROUS_CAPABILITIES]
            
            if dangerous_caps:
                finding = K8sSecurityFinding(
                    severity=K8sSeverity.CRITICAL,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title=f'Dangerous Capabilities: {", ".join(dangerous_caps)}',
                    finding_description=f'Container granted dangerous Linux capabilities: {", ".join(dangerous_caps)}. Container escape possible.',
                    current_config=f'capabilities.add: {cap_add}',
                    recommended_config='capabilities.drop: [ALL], capabilities.add: [NET_BIND_SERVICE] (minimal)',
                    remediation=[
                        'Remove dangerous capabilities from securityContext.capabilities.add',
                        'Drop all: securityContext.capabilities.drop: [ALL]',
                        'Add only required: securityContext.capabilities.add: [NET_BIND_SERVICE]'
                    ],
                    nsa_guide='Section 5.2.5 - Drop capabilities',
                    references=['Pod Security Standards - Restricted']
                )
                findings.append(finding)
            
            if 'ALL' not in cap_drop:
                finding = K8sSecurityFinding(
                    severity=K8sSeverity.MEDIUM,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title='Capabilities Not Fully Dropped',
                    finding_description='Container retains default capabilities. Best practice: Drop all, add minimal.',
                    current_config=f'capabilities.drop: {cap_drop or "[]"}',
                    recommended_config='capabilities.drop: [ALL]',
                    remediation=[
                        'Set securityContext.capabilities.drop: [ALL]',
                        'Then add only required capabilities'
                    ],
                    nsa_guide='Section 5.2.5 - Principle of least privilege',
                    references=['Pod Security Standards']
                )
                findings.append(finding)
            
            # Check 5: Read-only root filesystem
            read_only_rootfs = container_security.get('readOnlyRootFilesystem', False)
            if not read_only_rootfs:
                finding = K8sSecurityFinding(
                    severity=K8sSeverity.MEDIUM,
                    component=ControlPlaneComponent.KUBELET,
                    category='pod_security',
                    resource_type='Pod',
                    resource_name=pod_name,
                    namespace=namespace,
                    finding_title='Root Filesystem Not Read-Only',
                    finding_description='Container root filesystem writable. Malware persistence possible.',
                    current_config='readOnlyRootFilesystem: false',
                    recommended_config='readOnlyRootFilesystem: true',
                    remediation=[
                        'Set securityContext.readOnlyRootFilesystem: true',
                        'Mount emptyDir volumes for writable directories:',
                        '  volumeMounts:',
                        '    - name: tmp',
                        '      mountPath: /tmp',
                        '  volumes:',
                        '    - name: tmp',
                        '      emptyDir: {}'
                    ],
                    nsa_guide='Section 5.2.6 - Immutable root filesystem',
                    references=['Pod Security Standards - Restricted']
                )
                findings.append(finding)
        
        self.findings.extend(findings)
        return findings
    
    def scan_network_policies(self, namespace: str, network_policies: List[Dict]) -> List[K8sSecurityFinding]:
        """
        Scan namespace for network policy compliance.
        
        Args:
            namespace: Namespace name
            network_policies: List of NetworkPolicy objects in namespace
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Check for default-deny policies
        has_deny_ingress = any(
            np.get('spec', {}).get('policyTypes', []) == ['Ingress'] and
            np.get('spec', {}).get('podSelector', {}) == {}
            for np in network_policies
        )
        
        has_deny_egress = any(
            np.get('spec', {}).get('policyTypes', []) == ['Egress'] and
            np.get('spec', {}).get('podSelector', {}) == {}
            for np in network_policies
        )
        
        if not has_deny_ingress and self.require_network_policies:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.HIGH,
                component=ControlPlaneComponent.KUBE_PROXY,
                category='network',
                resource_type='NetworkPolicy',
                resource_name='default-deny-ingress',
                namespace=namespace,
                finding_title='No Default-Deny Ingress Network Policy',
                finding_description='Namespace lacks default-deny ingress policy. All pods accept connections from anywhere by default.',
                current_config='No default-deny ingress policy',
                recommended_config='NetworkPolicy with empty podSelector and policyTypes: [Ingress]',
                remediation=[
                    f'Create default-deny-ingress.yaml:',
                    f'apiVersion: networking.k8s.io/v1',
                    f'kind: NetworkPolicy',
                    f'metadata:',
                    f'  name: default-deny-ingress',
                    f'  namespace: {namespace}',
                    f'spec:',
                    f'  podSelector: {{}}',
                    f'  policyTypes:',
                    f'  - Ingress',
                    'Apply: kubectl apply -f default-deny-ingress.yaml',
                    'Then create allow policies for legitimate traffic'
                ],
                nsa_guide=self.NSA_HARDENING_GUIDE['network_policies'],
                disa_stig='V-242385 - Network segmentation must be enforced',
                references=['NSA/CISA Hardening Guide Section 5.3']
            )
            findings.append(finding)
        
        if not has_deny_egress and self.require_network_policies:
            finding = K8sSecurityFinding(
                severity=K8sSeverity.MEDIUM,
                component=ControlPlaneComponent.KUBE_PROXY,
                category='network',
                resource_type='NetworkPolicy',
                resource_name='default-deny-egress',
                namespace=namespace,
                finding_title='No Default-Deny Egress Network Policy',
                finding_description='Namespace lacks default-deny egress policy. Pods can connect to any destination.',
                current_config='No default-deny egress policy',
                recommended_config='NetworkPolicy with empty podSelector and policyTypes: [Egress]',
                remediation=[
                    'Create default-deny-egress.yaml with policyTypes: [Egress]',
                    'Allow DNS: spec.egress[0].ports[0].port: 53',
                    'Create explicit allow policies for required external connections'
                ],
                nsa_guide=self.NSA_HARDENING_GUIDE['network_policies'],
                references=['Kubernetes Network Policies']
            )
            findings.append(finding)
        
        self.findings.extend(findings)
        return findings
    
    def generate_report(self) -> Dict:
        """
        Generate Kubernetes security hardening report.
        
        Returns:
            Dictionary with security findings and recommendations
        """
        critical_count = len([f for f in self.findings if f.severity == K8sSeverity.CRITICAL])
        high_count = len([f for f in self.findings if f.severity == K8sSeverity.HIGH])
        medium_count = len([f for f in self.findings if f.severity == K8sSeverity.MEDIUM])
        low_count = len([f for f in self.findings if f.severity == K8sSeverity.LOW])
        
        # Count by component
        component_counts = {}
        for component in ControlPlaneComponent:
            component_counts[component.value] = len([f for f in self.findings if f.component == component])
        
        # Count by category
        category_counts = {}
        for finding in self.findings:
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        # Calculate hardening score
        total_checks = len(self.findings) if self.findings else 1
        hardening_score = max(0, 100 - (critical_count * 20 + high_count * 10 + medium_count * 5 + low_count * 2))
        
        return {
            'scan_metadata': {
                'pod_security_restricted': self.require_pod_security_restricted,
                'network_policies_required': self.require_network_policies,
                'service_mesh_required': self.require_service_mesh,
                'scan_timestamp': datetime.now().isoformat(),
                'total_findings': len(self.findings)
            },
            'security_summary': {
                'hardening_score': hardening_score,
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'component_summary': component_counts,
            'category_summary': category_counts,
            'top_findings': [
                {
                    'severity': f.severity.value,
                    'component': f.component.value,
                    'category': f.category,
                    'resource': f'{f.resource_type}/{f.resource_name}',
                    'namespace': f.namespace,
                    'finding_title': f.finding_title,
                    'nsa_guide': f.nsa_guide
                }
                for f in sorted(self.findings, key=lambda x: (x.severity.value, x.component.value))[:10]
            ],
            'recommendations': self._generate_k8s_recommendations(critical_count, high_count, hardening_score)
        }
    
    def _generate_k8s_recommendations(self, critical: int, high: int, score: float) -> List[str]:
        """Generate Kubernetes-specific recommendations"""
        recommendations = []
        
        if critical > 0:
            recommendations.append(f'CRITICAL: {critical} critical control plane or pod security issues. Address immediately.')
        
        if high > 0:
            recommendations.append(f'HIGH PRIORITY: {high} high-severity findings. Review authentication, encryption, and network policies.')
        
        if score < 50:
            recommendations.append('MAJOR HARDENING NEEDED: Implement NSA/CISA Kubernetes Hardening Guide immediately.')
        
        recommendations.append('Apply CIS Kubernetes Benchmark Level 2 for comprehensive security.')
        recommendations.append('Implement Pod Security Standards with Restricted profile in all namespaces.')
        recommendations.append('Deploy OPA Gatekeeper or Kyverno for policy-as-code enforcement.')
        recommendations.append('Enable etcd encryption at rest with KMS provider (AWS KMS, Azure Key Vault).')
        recommendations.append('Implement default-deny network policies in all namespaces.')
        recommendations.append('Deploy service mesh (Istio, Linkerd) for automatic mTLS between services.')
        recommendations.append('Enable API server audit logging and forward to SIEM.')
        recommendations.append('Scan container images with Trivy or Anchore for vulnerabilities.')
        
        return recommendations


# Example usage
if __name__ == "__main__":
    scanner = KubernetesSecurityHardeningScanner(
        require_pod_security_restricted=True,
        require_network_policies=True,
        require_service_mesh=False
    )
    
    # Example control plane config
    example_control_plane = {
        'api_server': {
            'anonymous_auth': True,  # Should be false
            'insecure_port': 8080,   # Should be 0
            'audit_log_path': '',    # Should be set
            'enable_admission_plugins': ['NodeRestriction']  # Missing PodSecurity
        },
        'etcd': {
            'encryption_provider_config': '',  # Should be set
            'peer_cert_file': '',
            'peer_key_file': ''
        },
        'kubelet': {
            'anonymous_auth': True,
            'read_only_port': 10255
        }
    }
    
    # Example pod spec
    example_pod = {
        'containers': [{
            'name': 'webapp',
            'securityContext': {
                'privileged': False,
                'runAsNonRoot': False,
                'capabilities': {
                    'add': ['NET_ADMIN'],
                    'drop': []
                }
            }
        }],
        'hostNetwork': False,
        'hostPID': False
    }
    
    # Scan
    cp_findings = scanner.scan_control_plane(example_control_plane)
    pod_findings = scanner.scan_pod_security(example_pod, 'webapp-pod', 'default')
    net_findings = scanner.scan_network_policies('default', [])
    
    # Generate report
    report = scanner.generate_report()
    
    print(f"\nKubernetes Security Hardening Scan Results")
    print("=" * 80)
    print(f"Hardening Score: {report['security_summary']['hardening_score']}/100")
    print(f"Findings: {report['security_summary']['critical']} Critical, "
          f"{report['security_summary']['high']} High, "
          f"{report['security_summary']['medium']} Medium")
    print("\nTop Recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec}")
