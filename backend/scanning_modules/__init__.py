"""
Enterprise Scanner - Advanced Scanning Modules
Enhanced vulnerability detection, security assessment, multi-cloud and container security
Version: 3.0.0
"""

from .advanced_port_scanner import AdvancedPortScanner
from .web_app_scanner import WebAppScanner
from .api_security_scanner import APISecurityScanner
from .cve_integration import CVEIntegration
from .multi_cloud_scanner import MultiCloudSecurityScanner

# Container security orchestration
from .container_security_orchestrator import ContainerSecurityOrchestrator

# Individual cloud scanners (optional imports)
try:
    from .cloud_security_aws import AWSSecurityScanner
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from .cloud_security_azure import AzureSecurityScanner
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from .cloud_security_gcp import GCPSecurityScanner
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

# Container security scanners (optional imports)
try:
    from .container_security_docker import DockerSecurityScanner
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    from .container_security_k8s import KubernetesSecurityScanner
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False

__all__ = [
    'AdvancedPortScanner',
    'WebAppScanner',
    'APISecurityScanner',
    'CVEIntegration',
    'MultiCloudSecurityScanner',
    'ContainerSecurityOrchestrator',
    'AWSSecurityScanner',
    'AzureSecurityScanner',
    'GCPSecurityScanner',
    'DockerSecurityScanner',
    'KubernetesSecurityScanner',
    'AWS_AVAILABLE',
    'AZURE_AVAILABLE',
    'GCP_AVAILABLE',
    'DOCKER_AVAILABLE',
    'KUBERNETES_AVAILABLE'
]

__version__ = '3.0.0'  # Container security support added

