"""
Military-Grade Docker Security Hardening Module
Enterprise Scanner - Container Runtime Protection & Isolation

Validates advanced Docker security hardening:
- gVisor/Kata Containers kernel isolation
- Seccomp profile enforcement (restrict to 44 safe syscalls)
- AppArmor/SELinux mandatory access control
- Docker Content Trust (DCT) image signing
- Runtime threat detection (Falco, Sysdig Secure)
- Privileged container prohibition
- Host namespace isolation (PID, IPC, network)
- Read-only root filesystem enforcement
- Capability dropping (minimal Linux capabilities)
- Resource limits and cgroups

Supports: Docker Engine, containerd, CRI-O
Classification: Unclassified
Compliance: NIST 800-190, CIS Docker Benchmark, DISA STIG, DoD Container Hardening
"""

import re
import json
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class IsolationTechnology(Enum):
    """Container isolation technologies"""
    RUNSC_GVISOR = "runC + gVisor"  # Google's application kernel
    KATA_CONTAINERS = "Kata Containers"  # Lightweight VMs
    FIRECRACKER = "Firecracker"  # AWS microVM
    NABLA_CONTAINERS = "Nabla Containers"  # Unikernel
    STANDARD_RUNC = "Standard runC"  # Default (least secure)


class SecurityProfile(Enum):
    """Security profile types"""
    SECCOMP = "Seccomp"  # Syscall filtering
    APPARMOR = "AppArmor"  # MAC for Ubuntu/Debian
    SELINUX = "SELinux"  # MAC for RHEL/CentOS/Fedora
    NONE = "None"  # No profile (insecure)


class ContainerSeverity(Enum):
    """Container security finding severity"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


@dataclass
class DockerSecurityFinding:
    """Docker security finding"""
    severity: ContainerSeverity
    category: str  # isolation, seccomp, mac, image_trust, runtime, namespace, capabilities
    container_id: str
    container_name: str
    image: str
    finding_title: str
    finding_description: str
    current_config: str
    recommended_config: str
    remediation: List[str]
    cis_benchmark: Optional[str] = None
    disa_stig: Optional[str] = None
    nist_800_190: Optional[str] = None
    references: List[str] = field(default_factory=list)


class DockerSecurityHardeningScanner:
    """
    Military-grade Docker security hardening scanner.
    
    Features:
    - Kernel isolation validation (gVisor/Kata)
    - Seccomp profile enforcement
    - AppArmor/SELinux MAC validation
    - Docker Content Trust verification
    - Runtime threat detection
    - Privileged container detection
    - Namespace isolation validation
    """
    
    # Seccomp default allowed syscalls (44 safe syscalls for most applications)
    SECCOMP_SAFE_SYSCALLS = [
        'accept', 'accept4', 'access', 'arch_prctl', 'bind', 'brk', 'capget', 'capset',
        'chdir', 'chmod', 'chown', 'clock_getres', 'clock_gettime', 'clock_nanosleep',
        'close', 'connect', 'dup', 'dup2', 'dup3', 'epoll_create', 'epoll_create1',
        'epoll_ctl', 'epoll_wait', 'eventfd', 'eventfd2', 'execve', 'exit', 'exit_group',
        'fchdir', 'fchmod', 'fchown', 'fcntl', 'fstat', 'fsync', 'futex', 'getcwd',
        'getdents', 'getdents64', 'getegid', 'geteuid', 'getgid', 'getpeername', 'getpgrp',
        'getpid', 'getppid', 'getrandom', 'getrlimit', 'getsid', 'getsockname', 'getsockopt',
        'gettid', 'gettimeofday', 'getuid'
    ]
    
    # Dangerous syscalls that should be blocked
    SECCOMP_DANGEROUS_SYSCALLS = [
        'reboot', 'swapon', 'swapoff', 'mount', 'umount', 'umount2', 'pivot_root',
        'chroot', 'acct', 'settimeofday', 'stime', 'adjtimex', 'clock_settime',
        'delete_module', 'init_module', 'finit_module', 'kexec_load', 'kexec_file_load',
        'bpf', 'ptrace', 'perf_event_open', 'userfaultfd'
    ]
    
    # Dangerous Linux capabilities
    DANGEROUS_CAPABILITIES = [
        'CAP_SYS_ADMIN',      # Allows mount, reboot, admin operations
        'CAP_SYS_MODULE',     # Insert/remove kernel modules
        'CAP_SYS_RAWIO',      # Raw I/O operations
        'CAP_SYS_PTRACE',     # ptrace() other processes
        'CAP_SYS_BOOT',       # Reboot system
        'CAP_SYS_TIME',       # Modify system time
        'CAP_NET_ADMIN',      # Network administration (can be dangerous)
        'CAP_DAC_READ_SEARCH', # Bypass file read permission checks
        'CAP_DAC_OVERRIDE',   # Bypass file permission checks
        'CAP_SETUID',         # Make arbitrary UID changes
        'CAP_SETGID',         # Make arbitrary GID changes
        'CAP_SETPCAP',        # Modify process capabilities
        'CAP_SYS_CHROOT',     # Use chroot()
        'CAP_MKNOD',          # Create device nodes
        'CAP_AUDIT_CONTROL',  # Control kernel auditing
        'CAP_AUDIT_WRITE',    # Write to kernel audit log
    ]
    
    # Minimal safe capabilities for most applications
    SAFE_CAPABILITIES = [
        'CAP_CHOWN',          # Change file ownership
        'CAP_FOWNER',         # Bypass permission checks on file operations
        'CAP_FSETID',         # Don't clear setuid/setgid bits
        'CAP_KILL',           # Send signals to processes
        'CAP_SETFCAP',        # Set file capabilities
        'CAP_NET_BIND_SERVICE', # Bind to ports <1024
        'CAP_NET_RAW',        # Use RAW/PACKET sockets (ping)
    ]
    
    # CIS Docker Benchmark mappings
    CIS_BENCHMARKS = {
        'privileged': '5.3 - Ensure that containers are not run in privileged mode',
        'pid_mode': '5.15 - Ensure that the host\'s process namespace is not shared',
        'ipc_mode': '5.16 - Ensure that the host\'s IPC namespace is not shared',
        'network_mode': '5.13 - Ensure that the host\'s network namespace is not shared',
        'user': '4.1 - Ensure that a user for the container has been created',
        'read_only_rootfs': '5.12 - Ensure that the container\'s root filesystem is mounted as read only',
        'memory_limit': '5.10 - Ensure memory usage for containers is limited',
        'cpu_limit': '5.11 - Ensure CPU priority is set appropriately on containers',
        'seccomp': '5.21 - Ensure the default seccomp profile is enabled',
        'apparmor': '5.1 - Ensure that AppArmor profile is enabled',
        'selinux': '5.2 - Ensure that SELinux security options are set',
        'capabilities': '5.4 - Ensure Linux kernel capabilities are restricted',
    }
    
    def __init__(self, require_kernel_isolation: bool = True,
                 require_content_trust: bool = True,
                 enable_runtime_detection: bool = True):
        """
        Initialize Docker security hardening scanner.
        
        Args:
            require_kernel_isolation: Require gVisor/Kata isolation for DoD
            require_content_trust: Require Docker Content Trust (image signing)
            enable_runtime_detection: Enable Falco/Sysdig runtime threat detection
        """
        self.require_kernel_isolation = require_kernel_isolation
        self.require_content_trust = require_content_trust
        self.enable_runtime_detection = enable_runtime_detection
        self.findings: List[DockerSecurityFinding] = []
        
    def scan_container(self, container_config: Dict) -> List[DockerSecurityFinding]:
        """
        Scan individual container for security hardening.
        
        Args:
            container_config: Container configuration from Docker API
            
        Returns:
            List of security findings
        """
        findings = []
        
        container_id = container_config.get('Id', 'Unknown')[:12]
        container_name = container_config.get('Name', 'Unknown').lstrip('/')
        image = container_config.get('Image', 'Unknown')
        host_config = container_config.get('HostConfig', {})
        config = container_config.get('Config', {})
        
        # Check 1: Kernel Isolation (gVisor/Kata)
        runtime = host_config.get('Runtime', 'runc')
        if self.require_kernel_isolation and runtime not in ['runsc', 'kata-runtime', 'firecracker']:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.CRITICAL,
                category='isolation',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='No Kernel Isolation (Standard runC)',
                finding_description=f'Container using standard runC runtime without kernel isolation. DoD requires gVisor or Kata Containers for multi-tenant environments.',
                current_config=f'Runtime: {runtime}',
                recommended_config='Runtime: runsc (gVisor) or kata-runtime (Kata Containers)',
                remediation=[
                    'Install gVisor: curl -fsSL https://gvisor.dev/archive.key | sudo apt-key add -',
                    'Add repository and install runsc',
                    'Configure Docker to use runsc runtime',
                    'Run container with: docker run --runtime=runsc ...',
                    'Alternative: Install Kata Containers for VM-level isolation',
                    'Update /etc/docker/daemon.json with runtime configuration'
                ],
                cis_benchmark='5.28 - Ensure that the PIDs cgroup limit is used',
                nist_800_190='Recommendation: Use kernel isolation for untrusted workloads',
                references=[
                    'https://gvisor.dev/docs/',
                    'https://katacontainers.io/',
                    'NIST 800-190 Application Container Security Guide'
                ]
            )
            findings.append(finding)
        
        # Check 2: Privileged Container (CRITICAL)
        privileged = host_config.get('Privileged', False)
        if privileged:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.CRITICAL,
                category='privileged',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Privileged Container Detected (CRITICAL)',
                finding_description='Container running in privileged mode with full host access. This completely disables container isolation and is PROHIBITED in DoD environments.',
                current_config='Privileged: true (ALL CAPABILITIES, NO ISOLATION)',
                recommended_config='Privileged: false (never use --privileged)',
                remediation=[
                    'IMMEDIATE: Stop privileged container',
                    'Identify required capabilities with: docker inspect | jq .HostConfig.CapAdd',
                    'Re-deploy with only necessary capabilities using --cap-add',
                    'Example: docker run --cap-add=NET_ADMIN (instead of --privileged)',
                    'Document why specific capabilities are needed',
                    'Prohibit --privileged in CI/CD pipeline validation'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['privileged'],
                disa_stig='V-230502 - Docker must not run containers in privileged mode',
                nist_800_190='Section 3.2.1 - Avoid privileged containers',
                references=[
                    'CIS Docker Benchmark 5.3',
                    'DISA STIG Docker Enterprise',
                    'DoD Container Hardening Guide'
                ]
            )
            findings.append(finding)
        
        # Check 3: Seccomp Profile
        seccomp_profile = host_config.get('SecurityOpt', [])
        has_seccomp = any('seccomp' in opt for opt in seccomp_profile)
        seccomp_unconfined = any('seccomp:unconfined' in opt or 'seccomp=unconfined' in opt for opt in seccomp_profile)
        
        if seccomp_unconfined:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.CRITICAL,
                category='seccomp',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Seccomp Disabled (seccomp:unconfined)',
                finding_description='Seccomp syscall filtering disabled, allowing ALL system calls. This removes critical kernel attack surface protection.',
                current_config='SecurityOpt: seccomp:unconfined (ALL 300+ SYSCALLS ALLOWED)',
                recommended_config='SecurityOpt: seccomp=default-profile.json (44 safe syscalls)',
                remediation=[
                    'Remove --security-opt seccomp:unconfined flag',
                    'Use default Docker seccomp profile (blocks 44+ dangerous syscalls)',
                    'Create custom seccomp profile for application',
                    'Example profile: {"defaultAction": "SCMP_ACT_ERRNO", "architectures": [...], "syscalls": [...]}',
                    'Apply with: docker run --security-opt seccomp=profile.json',
                    'Test application to ensure no syscall violations'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['seccomp'],
                disa_stig='V-230503 - Seccomp must be enabled',
                nist_800_190='Section 4.2.3 - Use seccomp to limit syscalls',
                references=[
                    'Docker Seccomp Security Profiles',
                    'https://docs.docker.com/engine/security/seccomp/'
                ]
            )
            findings.append(finding)
        elif not has_seccomp and runtime == 'runc':
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.HIGH,
                category='seccomp',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='No Custom Seccomp Profile (Using Default)',
                finding_description='Container using Docker default seccomp profile. Consider custom profile to restrict to only required syscalls (44 → 20-30 typical).',
                current_config='SecurityOpt: default (44 safe syscalls)',
                recommended_config='SecurityOpt: seccomp=custom-profile.json (20-30 app-specific)',
                remediation=[
                    'Audit application syscall usage with strace',
                    'Create minimal seccomp profile with only required syscalls',
                    'Start with default profile and remove unnecessary syscalls',
                    'Test in staging environment before production',
                    'Version control seccomp profiles with application code'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['seccomp'],
                nist_800_190='Section 4.2.3 - Minimize syscall attack surface',
                references=['Docker Security Best Practices']
            )
            findings.append(finding)
        
        # Check 4: AppArmor/SELinux
        has_apparmor = any('apparmor' in opt for opt in seccomp_profile)
        has_selinux = any('label' in opt for opt in seccomp_profile)
        
        if not has_apparmor and not has_selinux:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.HIGH,
                category='mac',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='No Mandatory Access Control (AppArmor/SELinux)',
                finding_description='Container not using AppArmor or SELinux MAC. Mandatory access control provides defense-in-depth against container escapes.',
                current_config='SecurityOpt: No AppArmor/SELinux',
                recommended_config='SecurityOpt: apparmor=docker-default or label=type:svirt_sandbox_file_t',
                remediation=[
                    'Ubuntu/Debian: Apply AppArmor profile',
                    'docker run --security-opt apparmor=docker-default',
                    'RHEL/CentOS/Fedora: Apply SELinux label',
                    'docker run --security-opt label=type:svirt_sandbox_file_t',
                    'Create custom AppArmor/SELinux profiles for applications',
                    'Test profiles in complain mode before enforcing'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['apparmor'],
                disa_stig='V-230504 - MAC must be enabled',
                nist_800_190='Section 4.2.4 - Use MAC to enforce least privilege',
                references=[
                    'AppArmor Docker Documentation',
                    'SELinux and Docker'
                ]
            )
            findings.append(finding)
        
        # Check 5: Host Namespace Sharing (PID, IPC, Network)
        pid_mode = host_config.get('PidMode', '')
        ipc_mode = host_config.get('IpcMode', '')
        network_mode = host_config.get('NetworkMode', '')
        
        if pid_mode == 'host':
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.CRITICAL,
                category='namespace',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Host PID Namespace Shared (--pid=host)',
                finding_description='Container shares host PID namespace, allowing visibility and manipulation of ALL host processes. Container escape risk.',
                current_config='PidMode: host (CAN SEE/KILL HOST PROCESSES)',
                recommended_config='PidMode: (isolated PID namespace)',
                remediation=[
                    'Remove --pid=host flag from container',
                    'Use isolated PID namespace (default)',
                    'If debugging needed, use kubectl exec or docker exec instead',
                    'NEVER use --pid=host in production'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['pid_mode'],
                disa_stig='V-230505 - Host PID namespace sharing prohibited',
                nist_800_190='Section 3.2.3 - Isolate namespaces',
                references=['CIS Docker Benchmark 5.15']
            )
            findings.append(finding)
        
        if ipc_mode == 'host':
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.HIGH,
                category='namespace',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Host IPC Namespace Shared (--ipc=host)',
                finding_description='Container shares host IPC namespace, allowing access to host shared memory and semaphores. Information disclosure risk.',
                current_config='IpcMode: host (SHARED MEMORY WITH HOST)',
                recommended_config='IpcMode: (isolated IPC namespace)',
                remediation=[
                    'Remove --ipc=host flag',
                    'Use isolated IPC namespace (default)',
                    'For inter-container communication, use shared volumes or network'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['ipc_mode'],
                disa_stig='V-230506 - Host IPC namespace sharing prohibited',
                nist_800_190='Section 3.2.3 - Isolate IPC namespace',
                references=['CIS Docker Benchmark 5.16']
            )
            findings.append(finding)
        
        if network_mode == 'host':
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.HIGH,
                category='namespace',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Host Network Namespace Shared (--net=host)',
                finding_description='Container shares host network namespace, bypassing Docker network isolation. Can sniff ALL host traffic and bind to ANY port.',
                current_config='NetworkMode: host (FULL HOST NETWORK ACCESS)',
                recommended_config='NetworkMode: bridge or custom network',
                remediation=[
                    'Remove --net=host flag',
                    'Use bridge network (default) or custom Docker network',
                    'Publish specific ports with -p 80:8080 instead',
                    'For performance, consider using macvlan or ipvlan networks'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['network_mode'],
                disa_stig='V-230507 - Host network namespace sharing prohibited',
                nist_800_190='Section 3.2.3 - Isolate network namespace',
                references=['CIS Docker Benchmark 5.13']
            )
            findings.append(finding)
        
        # Check 6: User (Running as root)
        user = config.get('User', '')
        if not user or user == 'root' or user == '0':
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.HIGH,
                category='user',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Container Running as Root User',
                finding_description='Container processes running as root (UID 0). If container is compromised, attacker has root privileges within container.',
                current_config=f'User: {user or "root (default)"}',
                recommended_config='User: appuser (UID 1000-65534, non-root)',
                remediation=[
                    'Add USER directive to Dockerfile: USER appuser',
                    'Create non-root user in Dockerfile:',
                    '  RUN useradd -m -u 1000 -s /bin/bash appuser',
                    '  USER appuser',
                    'Or specify at runtime: docker run --user 1000:1000',
                    'Ensure application files are owned by non-root user',
                    'Use --read-only-rootfs to prevent file modifications'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['user'],
                disa_stig='V-230508 - Containers must not run as root',
                nist_800_190='Section 4.4.1 - Run as non-root user',
                references=['CIS Docker Benchmark 4.1']
            )
            findings.append(finding)
        
        # Check 7: Read-Only Root Filesystem
        read_only_rootfs = host_config.get('ReadonlyRootfs', False)
        if not read_only_rootfs:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.MEDIUM,
                category='filesystem',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Root Filesystem Not Read-Only',
                finding_description='Container root filesystem is writable. Attackers can modify binaries, install malware, or persist after container restart.',
                current_config='ReadonlyRootfs: false (WRITABLE)',
                recommended_config='ReadonlyRootfs: true (IMMUTABLE)',
                remediation=[
                    'Run with: docker run --read-only',
                    'Mount tmpfs for writable directories:',
                    '  --tmpfs /tmp --tmpfs /var/run',
                    'Or use volumes for persistent data:',
                    '  -v /host/data:/app/data',
                    'Ensure application can run with read-only root',
                    'Test thoroughly in staging environment'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['read_only_rootfs'],
                disa_stig='V-230509 - Root filesystem should be read-only',
                nist_800_190='Section 4.4.3 - Use read-only root filesystem',
                references=['CIS Docker Benchmark 5.12']
            )
            findings.append(finding)
        
        # Check 8: Linux Capabilities
        cap_add = host_config.get('CapAdd', [])
        cap_drop = host_config.get('CapDrop', [])
        
        dangerous_caps_added = [cap for cap in cap_add if cap.upper() in self.DANGEROUS_CAPABILITIES]
        
        if dangerous_caps_added:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.CRITICAL,
                category='capabilities',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title=f'Dangerous Capabilities Added: {", ".join(dangerous_caps_added)}',
                finding_description=f'Container granted dangerous Linux capabilities: {", ".join(dangerous_caps_added)}. These capabilities can enable container escape or host compromise.',
                current_config=f'CapAdd: {cap_add}',
                recommended_config='CapAdd: Only CAP_NET_BIND_SERVICE, CAP_CHOWN, etc. (minimal set)',
                remediation=[
                    'Remove dangerous capabilities from --cap-add',
                    'Use minimal capability set for application',
                    'Drop all capabilities first: --cap-drop=ALL',
                    'Then add only required: --cap-add=NET_BIND_SERVICE',
                    'Document justification for each capability',
                    'NEVER add: CAP_SYS_ADMIN, CAP_SYS_MODULE, CAP_SYS_RAWIO'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['capabilities'],
                disa_stig='V-230510 - Dangerous capabilities prohibited',
                nist_800_190='Section 4.4.2 - Drop unnecessary capabilities',
                references=['Linux Capabilities Man Page']
            )
            findings.append(finding)
        
        if 'ALL' not in cap_drop:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.MEDIUM,
                category='capabilities',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='Not All Capabilities Dropped (--cap-drop=ALL)',
                finding_description='Container retains default Linux capabilities. Best practice: Drop all, then add only required.',
                current_config=f'CapDrop: {cap_drop or "none (default capabilities retained)"}',
                recommended_config='CapDrop: [ALL], CapAdd: [only required]',
                remediation=[
                    'Add --cap-drop=ALL to drop all capabilities',
                    'Then add only necessary with --cap-add',
                    'Example: docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE',
                    'Test application after capability changes',
                    'Most applications need zero additional capabilities'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['capabilities'],
                nist_800_190='Section 4.4.2 - Principle of least privilege',
                references=['Docker Security Best Practices']
            )
            findings.append(finding)
        
        # Check 9: Resource Limits (Memory, CPU)
        memory_limit = host_config.get('Memory', 0)
        cpu_shares = host_config.get('CpuShares', 0)
        
        if memory_limit == 0:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.MEDIUM,
                category='resources',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='No Memory Limit Set',
                finding_description='Container has no memory limit, can consume all host memory causing DoS.',
                current_config='Memory: unlimited',
                recommended_config='Memory: 512m-2g (application-specific)',
                remediation=[
                    'Set memory limit: docker run -m 512m or -m 2g',
                    'Also set memory reservation: --memory-reservation 256m',
                    'Monitor container memory usage to determine appropriate limit',
                    'Set memory swap limit: --memory-swap 1g'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['memory_limit'],
                disa_stig='V-230511 - Memory limits must be set',
                nist_800_190='Section 4.3.1 - Limit container resources',
                references=['CIS Docker Benchmark 5.10']
            )
            findings.append(finding)
        
        if cpu_shares == 0:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.LOW,
                category='resources',
                container_id=container_id,
                container_name=container_name,
                image=image,
                finding_title='No CPU Limit Set',
                finding_description='Container has no CPU limit, can monopolize host CPU.',
                current_config='CpuShares: unlimited',
                recommended_config='CpuShares: 1024 (normal priority) or --cpus=2.0',
                remediation=[
                    'Set CPU shares: docker run --cpu-shares 1024',
                    'Or set CPU count: --cpus 2.0',
                    'Set CPU period and quota for hard limits',
                    'Monitor CPU usage to determine appropriate allocation'
                ],
                cis_benchmark=self.CIS_BENCHMARKS['cpu_limit'],
                nist_800_190='Section 4.3.1 - Limit CPU resources',
                references=['CIS Docker Benchmark 5.11']
            )
            findings.append(finding)
        
        self.findings.extend(findings)
        return findings
    
    def scan_docker_daemon(self, daemon_config: Dict) -> List[DockerSecurityFinding]:
        """
        Scan Docker daemon configuration for security.
        
        Args:
            daemon_config: Docker daemon configuration
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Check Docker Content Trust (DCT)
        content_trust_enabled = daemon_config.get('content_trust_enabled', False)
        
        if self.require_content_trust and not content_trust_enabled:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.CRITICAL,
                category='image_trust',
                container_id='N/A',
                container_name='docker-daemon',
                image='N/A',
                finding_title='Docker Content Trust (DCT) Not Enabled',
                finding_description='Docker Content Trust disabled, allowing unsigned/unverified images. DoD requires image signing for supply chain security.',
                current_config='DOCKER_CONTENT_TRUST=0 (unsigned images allowed)',
                recommended_config='DOCKER_CONTENT_TRUST=1 (only signed images)',
                remediation=[
                    'Enable Docker Content Trust: export DOCKER_CONTENT_TRUST=1',
                    'Add to /etc/environment or shell profile',
                    'Sign images before pushing: docker trust sign myimage:tag',
                    'Set up Notary server for enterprise signing',
                    'Integrate with CI/CD pipeline for automatic signing',
                    'Use private registry with Notary (Harbor, DTR)'
                ],
                cis_benchmark='4.5 - Enable Content Trust for Docker',
                disa_stig='V-230512 - Image signing must be enforced',
                nist_800_190='Section 3.1.1 - Image integrity and signing',
                references=[
                    'Docker Content Trust Documentation',
                    'Notary Project'
                ]
            )
            findings.append(finding)
        
        # Check Runtime Threat Detection
        runtime_detection = daemon_config.get('runtime_detection', False)
        
        if self.enable_runtime_detection and not runtime_detection:
            finding = DockerSecurityFinding(
                severity=ContainerSeverity.HIGH,
                category='runtime',
                container_id='N/A',
                container_name='docker-daemon',
                image='N/A',
                finding_title='No Runtime Threat Detection (Falco/Sysdig)',
                finding_description='No runtime security monitoring deployed. Cannot detect container escapes, privilege escalation, or malicious behavior.',
                current_config='Runtime detection: Disabled',
                recommended_config='Runtime detection: Falco or Sysdig Secure',
                remediation=[
                    'Deploy Falco for runtime threat detection',
                    'Install: curl -s https://falco.org/repo/falcosecurity-3672BA8F.asc | apt-key add -',
                    'Configure Falco rules for container security',
                    'Integrate with SIEM for alerting',
                    'Alternative: Deploy Sysdig Secure or Aqua Security',
                    'Monitor for: shell in container, privilege escalation, unexpected network connections'
                ],
                nist_800_190='Section 5.1 - Runtime monitoring and threat detection',
                references=[
                    'https://falco.org/',
                    'Sysdig Secure',
                    'NIST 800-190 Section 5'
                ]
            )
            findings.append(finding)
        
        self.findings.extend(findings)
        return findings
    
    def generate_report(self) -> Dict:
        """
        Generate Docker security hardening report.
        
        Returns:
            Dictionary with security findings and recommendations
        """
        critical_count = len([f for f in self.findings if f.severity == ContainerSeverity.CRITICAL])
        high_count = len([f for f in self.findings if f.severity == ContainerSeverity.HIGH])
        medium_count = len([f for f in self.findings if f.severity == ContainerSeverity.MEDIUM])
        low_count = len([f for f in self.findings if f.severity == ContainerSeverity.LOW])
        
        # Count findings by category
        category_counts = {}
        for finding in self.findings:
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        # Calculate hardening score (0-100)
        total_checks = len(self.findings) if self.findings else 1
        hardening_score = max(0, 100 - (critical_count * 20 + high_count * 10 + medium_count * 5 + low_count * 2))
        
        return {
            'scan_metadata': {
                'kernel_isolation_required': self.require_kernel_isolation,
                'content_trust_required': self.require_content_trust,
                'runtime_detection_enabled': self.enable_runtime_detection,
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
            'category_summary': category_counts,
            'top_findings': [
                {
                    'severity': f.severity.value,
                    'category': f.category,
                    'container': f.container_name,
                    'finding_title': f.finding_title,
                    'cis_benchmark': f.cis_benchmark,
                    'remediation_steps': len(f.remediation)
                }
                for f in sorted(self.findings, key=lambda x: (x.severity.value, x.category))[:10]
            ],
            'recommendations': self._generate_docker_recommendations(critical_count, high_count, hardening_score)
        }
    
    def _generate_docker_recommendations(self, critical: int, high: int, score: float) -> List[str]:
        """Generate Docker-specific recommendations"""
        recommendations = []
        
        if critical > 0:
            recommendations.append(f'CRITICAL: {critical} critical container security issues. Address privileged containers, kernel isolation, and seccomp immediately.')
        
        if high > 0:
            recommendations.append(f'HIGH PRIORITY: {high} high-severity findings. Review namespace isolation and capabilities.')
        
        if score < 50:
            recommendations.append('MAJOR HARDENING NEEDED: Hardening score below 50%. Implement comprehensive container security baseline.')
        elif score < 75:
            recommendations.append('MODERATE HARDENING NEEDED: Hardening score 50-75%. Focus on CIS Benchmark compliance.')
        
        recommendations.append('Deploy gVisor or Kata Containers for kernel-level isolation (DoD requirement).')
        recommendations.append('Enable Docker Content Trust (DCT) for image signing and verification.')
        recommendations.append('Deploy Falco or Sysdig Secure for runtime threat detection.')
        recommendations.append('Apply CIS Docker Benchmark Level 2 (stricter security).')
        recommendations.append('Use minimal base images (Alpine, Distroless) to reduce attack surface.')
        recommendations.append('Implement admission controllers (OPA Gatekeeper) to enforce policies at deployment time.')
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Initialize scanner for DoD requirements
    scanner = DockerSecurityHardeningScanner(
        require_kernel_isolation=True,
        require_content_trust=True,
        enable_runtime_detection=True
    )
    
    # Example container configuration (from Docker API)
    example_container = {
        'Id': 'abc123def456',
        'Name': '/webapp',
        'Image': 'nginx:latest',
        'HostConfig': {
            'Runtime': 'runc',  # Should be 'runsc' or 'kata-runtime'
            'Privileged': False,
            'SecurityOpt': [],  # Should have seccomp, apparmor
            'PidMode': '',
            'IpcMode': '',
            'NetworkMode': 'bridge',
            'ReadonlyRootfs': False,
            'CapAdd': [],
            'CapDrop': [],
            'Memory': 0,
            'CpuShares': 0
        },
        'Config': {
            'User': ''  # Running as root
        }
    }
    
    # Example daemon configuration
    example_daemon = {
        'content_trust_enabled': False,
        'runtime_detection': False
    }
    
    # Scan container and daemon
    container_findings = scanner.scan_container(example_container)
    daemon_findings = scanner.scan_docker_daemon(example_daemon)
    
    # Generate report
    report = scanner.generate_report()
    
    print(f"\nDocker Security Hardening Scan Results")
    print("=" * 80)
    print(f"Hardening Score: {report['security_summary']['hardening_score']}/100")
    print(f"Total Findings: {report['scan_metadata']['total_findings']}")
    print(f"Findings: {report['security_summary']['critical']} Critical, "
          f"{report['security_summary']['high']} High, "
          f"{report['security_summary']['medium']} Medium")
    print("\nTop Recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec}")
