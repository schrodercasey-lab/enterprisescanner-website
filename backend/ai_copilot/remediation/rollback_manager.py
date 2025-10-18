"""
Jupiter v3.0 - Module G.1: Rollback Manager
Instant rollback capability with multi-platform snapshot management

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

import subprocess
import logging
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import hashlib

try:
    from .config import get_config
    from .exceptions import (
        RollbackError,
        ValidationError,
        TimeoutError as RemediationTimeoutError,
        RemediationDatabaseError
    )
except ImportError:
    # Fallback for standalone execution
    class RollbackError(Exception):
        pass
    class ValidationError(Exception):
        pass
    class RemediationTimeoutError(Exception):
        pass
    class RemediationDatabaseError(Exception):
        pass
    
    class MockConfig:
        database_path = "jupiter_remediation.db"
        snapshot_retention_days = 30
        auto_cleanup_expired_snapshots = True
        snapshot_verification_enabled = True
    
    def get_config():
        return MockConfig()


class SnapshotStatus(Enum):
    """Snapshot lifecycle status"""
    CREATING = "creating"
    READY = "ready"
    RESTORING = "restoring"
    FAILED = "failed"
    EXPIRED = "expired"
    DELETED = "deleted"


class SnapshotType(Enum):
    """Types of snapshots"""
    KUBERNETES_DEPLOYMENT = "kubernetes_deployment"
    DOCKER_CONTAINER = "docker_container"
    DOCKER_IMAGE = "docker_image"
    VM_SNAPSHOT = "vm_snapshot"
    FILE_BACKUP = "file_backup"


@dataclass
class Snapshot:
    """Snapshot metadata and configuration"""
    snapshot_id: str
    execution_id: str
    snapshot_type: SnapshotType
    
    # Platform-specific identifiers
    deployment_name: Optional[str] = None  # Kubernetes
    namespace: Optional[str] = None  # Kubernetes
    container_id: Optional[str] = None  # Docker
    image_tag: Optional[str] = None  # Docker
    vm_id: Optional[str] = None  # VM
    snapshot_name: Optional[str] = None  # VM
    
    # Snapshot details
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    # Status tracking
    status: SnapshotStatus = SnapshotStatus.CREATING
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    verified: bool = False
    
    # Restoration tracking
    restored_at: Optional[datetime] = None
    restore_duration_seconds: float = 0.0


class KubernetesRollback:
    """Kubernetes deployment rollback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_snapshot(self, execution_id: str, deployment: str, namespace: str = "default") -> Snapshot:
        """
        Create snapshot of Kubernetes deployment
        
        Args:
            execution_id: Execution identifier
            deployment: Deployment name
            namespace: Kubernetes namespace
            
        Returns:
            Snapshot object
        """
        try:
            snapshot_id = f"k8s-{deployment}-{int(time.time())}"
            self.logger.info(f"Creating K8s snapshot: {snapshot_id}")
            
            # Get current deployment YAML
            result = subprocess.run(
                ['kubectl', 'get', 'deployment', deployment, '-n', namespace, '-o', 'yaml'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Failed to get deployment: {result.stderr}")
            
            deployment_yaml = result.stdout
            
            # Calculate checksum
            checksum = hashlib.sha256(deployment_yaml.encode()).hexdigest()
            
            # Store in metadata
            metadata = {
                'deployment_yaml': deployment_yaml,
                'revision': self._get_deployment_revision(deployment, namespace)
            }
            
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                execution_id=execution_id,
                snapshot_type=SnapshotType.KUBERNETES_DEPLOYMENT,
                deployment_name=deployment,
                namespace=namespace,
                size_bytes=len(deployment_yaml.encode()),
                checksum=checksum,
                metadata=metadata,
                status=SnapshotStatus.READY,
                verified=True
            )
            
            self.logger.info(f"✅ K8s snapshot created: {snapshot_id}")
            return snapshot
            
        except subprocess.TimeoutExpired:
            raise RemediationTimeoutError(f"Timeout creating snapshot", operation="create_snapshot", timeout_seconds=30)
        except Exception as e:
            self.logger.error(f"Error creating K8s snapshot: {e}")
            raise RollbackError(f"K8s snapshot creation failed: {e}", snapshot_id=snapshot_id)
    
    def _get_deployment_revision(self, deployment: str, namespace: str) -> Optional[int]:
        """Get current deployment revision number"""
        try:
            result = subprocess.run(
                ['kubectl', 'rollout', 'history', 'deployment', deployment, '-n', namespace],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse revision from output (last line)
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    last_line = lines[-1]
                    revision = last_line.split()[0]
                    return int(revision) if revision.isdigit() else None
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not get revision: {e}")
            return None
    
    def rollback(self, snapshot: Snapshot, timeout: int = 30) -> bool:
        """
        Rollback Kubernetes deployment
        
        Args:
            snapshot: Snapshot to restore
            timeout: Timeout in seconds
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Rolling back K8s deployment: {snapshot.deployment_name}")
            start_time = time.time()
            
            # Use kubectl rollout undo
            result = subprocess.run(
                ['kubectl', 'rollout', 'undo', 'deployment', snapshot.deployment_name, 
                 '-n', snapshot.namespace],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Rollback failed: {result.stderr}")
            
            # Wait for rollout to complete
            self._wait_for_rollout(snapshot.deployment_name, snapshot.namespace, timeout)
            
            snapshot.restored_at = datetime.now()
            snapshot.restore_duration_seconds = time.time() - start_time
            snapshot.status = SnapshotStatus.READY
            
            self.logger.info(f"✅ K8s rollback complete in {snapshot.restore_duration_seconds:.2f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back K8s deployment: {e}")
            snapshot.status = SnapshotStatus.FAILED
            raise RollbackError(f"K8s rollback failed: {e}", snapshot_id=snapshot.snapshot_id)
    
    def _wait_for_rollout(self, deployment: str, namespace: str, timeout: int) -> None:
        """Wait for deployment rollout to complete"""
        try:
            result = subprocess.run(
                ['kubectl', 'rollout', 'status', 'deployment', deployment, '-n', namespace,
                 f'--timeout={timeout}s'],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Rollout did not complete: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RemediationTimeoutError(f"Rollout timeout", operation="wait_rollout", timeout_seconds=timeout)


class DockerRollback:
    """Docker container/image rollback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_container_snapshot(self, execution_id: str, container_id: str) -> Snapshot:
        """
        Create snapshot of Docker container (commit as image)
        
        Args:
            execution_id: Execution identifier
            container_id: Container ID
            
        Returns:
            Snapshot object
        """
        try:
            snapshot_id = f"docker-{container_id[:12]}-{int(time.time())}"
            image_tag = f"snapshot-{snapshot_id}"
            
            self.logger.info(f"Creating Docker snapshot: {snapshot_id}")
            
            # Commit container as image
            result = subprocess.run(
                ['docker', 'commit', container_id, image_tag],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Failed to commit container: {result.stderr}")
            
            image_id = result.stdout.strip()
            
            # Get image size
            result = subprocess.run(
                ['docker', 'inspect', '--format={{.Size}}', image_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            size_bytes = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                execution_id=execution_id,
                snapshot_type=SnapshotType.DOCKER_IMAGE,
                container_id=container_id,
                image_tag=image_tag,
                size_bytes=size_bytes,
                metadata={'image_id': image_id},
                status=SnapshotStatus.READY,
                verified=True
            )
            
            self.logger.info(f"✅ Docker snapshot created: {image_tag}")
            return snapshot
            
        except subprocess.TimeoutExpired:
            raise RemediationTimeoutError(f"Timeout creating snapshot", operation="docker_commit", timeout_seconds=60)
        except Exception as e:
            self.logger.error(f"Error creating Docker snapshot: {e}")
            raise RollbackError(f"Docker snapshot creation failed: {e}", snapshot_id=snapshot_id)
    
    def rollback(self, snapshot: Snapshot, timeout: int = 30) -> bool:
        """
        Rollback Docker container by recreating from snapshot image
        
        Args:
            snapshot: Snapshot to restore
            timeout: Timeout in seconds
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Rolling back Docker container: {snapshot.container_id[:12]}")
            start_time = time.time()
            
            # Get original container configuration
            result = subprocess.run(
                ['docker', 'inspect', snapshot.container_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Cannot inspect original container: {result.stderr}")
            
            config = json.loads(result.stdout)[0]
            container_name = config['Name'].lstrip('/')
            
            # Stop and remove current container
            subprocess.run(['docker', 'stop', snapshot.container_id], timeout=30)
            subprocess.run(['docker', 'rm', snapshot.container_id], timeout=10)
            
            # Create new container from snapshot image
            result = subprocess.run(
                ['docker', 'run', '-d', '--name', container_name, snapshot.image_tag],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Failed to recreate container: {result.stderr}")
            
            new_container_id = result.stdout.strip()
            
            snapshot.restored_at = datetime.now()
            snapshot.restore_duration_seconds = time.time() - start_time
            snapshot.status = SnapshotStatus.READY
            snapshot.metadata['new_container_id'] = new_container_id
            
            self.logger.info(f"✅ Docker rollback complete in {snapshot.restore_duration_seconds:.2f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back Docker container: {e}")
            snapshot.status = SnapshotStatus.FAILED
            raise RollbackError(f"Docker rollback failed: {e}", snapshot_id=snapshot.snapshot_id)
    
    def cleanup_snapshot(self, snapshot: Snapshot) -> bool:
        """Delete snapshot image"""
        try:
            self.logger.info(f"Cleaning up Docker snapshot: {snapshot.image_tag}")
            
            result = subprocess.run(
                ['docker', 'rmi', snapshot.image_tag],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                snapshot.status = SnapshotStatus.DELETED
                self.logger.info(f"✅ Snapshot deleted: {snapshot.image_tag}")
                return True
            else:
                self.logger.warning(f"Failed to delete snapshot: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cleaning up snapshot: {e}")
            return False


class VMRollback:
    """Virtual machine snapshot rollback"""
    
    def __init__(self, hypervisor: str = "vmware"):
        """
        Initialize VM rollback
        
        Args:
            hypervisor: Hypervisor type (vmware, kvm, hyperv)
        """
        self.logger = logging.getLogger(__name__)
        self.hypervisor = hypervisor.lower()
    
    def create_snapshot(self, execution_id: str, vm_id: str, snapshot_name: str = None) -> Snapshot:
        """
        Create VM snapshot
        
        Args:
            execution_id: Execution identifier
            vm_id: VM identifier
            snapshot_name: Optional snapshot name
            
        Returns:
            Snapshot object
        """
        try:
            if snapshot_name is None:
                snapshot_name = f"remediation-{execution_id}-{int(time.time())}"
            
            snapshot_id = f"vm-{vm_id}-{int(time.time())}"
            self.logger.info(f"Creating VM snapshot: {snapshot_id}")
            
            if self.hypervisor == "vmware":
                return self._create_vmware_snapshot(execution_id, snapshot_id, vm_id, snapshot_name)
            elif self.hypervisor == "kvm":
                return self._create_kvm_snapshot(execution_id, snapshot_id, vm_id, snapshot_name)
            elif self.hypervisor == "hyperv":
                return self._create_hyperv_snapshot(execution_id, snapshot_id, vm_id, snapshot_name)
            else:
                raise RollbackError(f"Unsupported hypervisor: {self.hypervisor}")
                
        except Exception as e:
            self.logger.error(f"Error creating VM snapshot: {e}")
            raise RollbackError(f"VM snapshot creation failed: {e}", snapshot_id=snapshot_id)
    
    def _create_vmware_snapshot(self, execution_id: str, snapshot_id: str, vm_id: str, name: str) -> Snapshot:
        """Create VMware snapshot using vmrun"""
        try:
            result = subprocess.run(
                ['vmrun', 'snapshot', vm_id, name],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise RollbackError(f"VMware snapshot failed: {result.stderr}")
            
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                execution_id=execution_id,
                snapshot_type=SnapshotType.VM_SNAPSHOT,
                vm_id=vm_id,
                snapshot_name=name,
                status=SnapshotStatus.READY,
                verified=True
            )
            
            self.logger.info(f"✅ VMware snapshot created: {name}")
            return snapshot
            
        except Exception as e:
            raise RollbackError(f"VMware snapshot error: {e}")
    
    def _create_kvm_snapshot(self, execution_id: str, snapshot_id: str, vm_id: str, name: str) -> Snapshot:
        """Create KVM snapshot using virsh"""
        try:
            result = subprocess.run(
                ['virsh', 'snapshot-create-as', vm_id, name, '--atomic'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise RollbackError(f"KVM snapshot failed: {result.stderr}")
            
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                execution_id=execution_id,
                snapshot_type=SnapshotType.VM_SNAPSHOT,
                vm_id=vm_id,
                snapshot_name=name,
                status=SnapshotStatus.READY,
                verified=True
            )
            
            self.logger.info(f"✅ KVM snapshot created: {name}")
            return snapshot
            
        except Exception as e:
            raise RollbackError(f"KVM snapshot error: {e}")
    
    def _create_hyperv_snapshot(self, execution_id: str, snapshot_id: str, vm_id: str, name: str) -> Snapshot:
        """Create Hyper-V checkpoint using PowerShell"""
        try:
            ps_script = f'Checkpoint-VM -Name "{vm_id}" -SnapshotName "{name}"'
            
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise RollbackError(f"Hyper-V snapshot failed: {result.stderr}")
            
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                execution_id=execution_id,
                snapshot_type=SnapshotType.VM_SNAPSHOT,
                vm_id=vm_id,
                snapshot_name=name,
                status=SnapshotStatus.READY,
                verified=True
            )
            
            self.logger.info(f"✅ Hyper-V snapshot created: {name}")
            return snapshot
            
        except Exception as e:
            raise RollbackError(f"Hyper-V snapshot error: {e}")
    
    def rollback(self, snapshot: Snapshot, timeout: int = 60) -> bool:
        """
        Restore VM from snapshot
        
        Args:
            snapshot: Snapshot to restore
            timeout: Timeout in seconds
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Rolling back VM: {snapshot.vm_id}")
            start_time = time.time()
            
            if self.hypervisor == "vmware":
                success = self._rollback_vmware(snapshot, timeout)
            elif self.hypervisor == "kvm":
                success = self._rollback_kvm(snapshot, timeout)
            elif self.hypervisor == "hyperv":
                success = self._rollback_hyperv(snapshot, timeout)
            else:
                raise RollbackError(f"Unsupported hypervisor: {self.hypervisor}")
            
            if success:
                snapshot.restored_at = datetime.now()
                snapshot.restore_duration_seconds = time.time() - start_time
                snapshot.status = SnapshotStatus.READY
                self.logger.info(f"✅ VM rollback complete in {snapshot.restore_duration_seconds:.2f}s")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error rolling back VM: {e}")
            snapshot.status = SnapshotStatus.FAILED
            raise RollbackError(f"VM rollback failed: {e}", snapshot_id=snapshot.snapshot_id)
    
    def _rollback_vmware(self, snapshot: Snapshot, timeout: int) -> bool:
        """Rollback VMware VM using vmrun"""
        try:
            result = subprocess.run(
                ['vmrun', 'revertToSnapshot', snapshot.vm_id, snapshot.snapshot_name],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode == 0
            
        except Exception as e:
            raise RollbackError(f"VMware rollback error: {e}")
    
    def _rollback_kvm(self, snapshot: Snapshot, timeout: int) -> bool:
        """Rollback KVM VM using virsh"""
        try:
            result = subprocess.run(
                ['virsh', 'snapshot-revert', snapshot.vm_id, snapshot.snapshot_name],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode == 0
            
        except Exception as e:
            raise RollbackError(f"KVM rollback error: {e}")
    
    def _rollback_hyperv(self, snapshot: Snapshot, timeout: int) -> bool:
        """Rollback Hyper-V VM using PowerShell"""
        try:
            ps_script = f'Restore-VMSnapshot -Name "{snapshot.snapshot_name}" -VMName "{snapshot.vm_id}" -Confirm:$false'
            
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode == 0
            
        except Exception as e:
            raise RollbackError(f"Hyper-V rollback error: {e}")


class HealthChecker:
    """Post-rollback health verification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def verify_rollback(self, snapshot: Snapshot, health_checks: List[Dict]) -> bool:
        """
        Verify system health after rollback
        
        Args:
            snapshot: Snapshot that was restored
            health_checks: List of health check configurations
            
        Returns:
            True if all checks pass
        """
        try:
            self.logger.info(f"Verifying rollback for {snapshot.snapshot_id}")
            
            all_passed = True
            for check in health_checks:
                check_type = check.get('type', 'http')
                
                if check_type == 'http':
                    passed = self._http_health_check(check)
                elif check_type == 'command':
                    passed = self._command_health_check(check)
                elif check_type == 'port':
                    passed = self._port_health_check(check)
                else:
                    self.logger.warning(f"Unknown check type: {check_type}")
                    passed = False
                
                if not passed:
                    all_passed = False
                    self.logger.error(f"Health check failed: {check.get('name', 'Unknown')}")
            
            if all_passed:
                self.logger.info(f"✅ All health checks passed")
            else:
                self.logger.error(f"❌ Some health checks failed")
            
            return all_passed
            
        except Exception as e:
            self.logger.error(f"Error verifying rollback: {e}")
            return False
    
    def _http_health_check(self, check: Dict) -> bool:
        """HTTP endpoint health check"""
        try:
            import requests
            
            url = check.get('url')
            expected_status = check.get('expected_status', 200)
            timeout = check.get('timeout', 10)
            
            response = requests.get(url, timeout=timeout)
            return response.status_code == expected_status
            
        except Exception as e:
            self.logger.error(f"HTTP check failed: {e}")
            return False
    
    def _command_health_check(self, check: Dict) -> bool:
        """Command execution health check"""
        try:
            command = check.get('command')
            expected_exit_code = check.get('expected_exit_code', 0)
            timeout = check.get('timeout', 30)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=timeout
            )
            
            return result.returncode == expected_exit_code
            
        except Exception as e:
            self.logger.error(f"Command check failed: {e}")
            return False
    
    def _port_health_check(self, check: Dict) -> bool:
        """TCP port availability check"""
        try:
            import socket
            
            host = check.get('host', 'localhost')
            port = check.get('port')
            timeout = check.get('timeout', 5)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except Exception as e:
            self.logger.error(f"Port check failed: {e}")
            return False


class RollbackManager:
    """Main rollback orchestrator"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize rollback manager
        
        Args:
            db_path: Path to database (default from config)
        """
        self.config = get_config()
        self.db_path = db_path or self.config.database_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform-specific handlers
        self.k8s_rollback = KubernetesRollback()
        self.docker_rollback = DockerRollback()
        self.vm_rollback = VMRollback()
        
        # Health checker
        self.health_checker = HealthChecker()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_snapshot(self, execution_id: str, asset: Dict) -> Snapshot:
        """
        Create snapshot based on asset type
        
        Args:
            execution_id: Execution identifier
            asset: Asset information
            
        Returns:
            Snapshot object
        """
        try:
            asset_type = asset.get('asset_type', 'server')
            self.logger.info(f"Creating snapshot for {asset_type}")
            
            if asset_type == 'kubernetes_cluster':
                deployment = asset.get('deployment_name')
                namespace = asset.get('namespace', 'default')
                snapshot = self.k8s_rollback.create_snapshot(execution_id, deployment, namespace)
            
            elif asset_type == 'container':
                container_id = asset.get('container_id')
                snapshot = self.docker_rollback.create_container_snapshot(execution_id, container_id)
            
            elif asset_type in ['vm', 'server']:
                vm_id = asset.get('vm_id') or asset.get('hostname')
                snapshot = self.vm_rollback.create_snapshot(execution_id, vm_id)
            
            else:
                raise ValidationError(f"Unsupported asset type: {asset_type}", field='asset_type', value=asset_type)
            
            # Save to database
            self.save_snapshot(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error creating snapshot: {e}")
            raise RollbackError(f"Snapshot creation failed: {e}")
    
    def rollback_to_snapshot(
        self,
        snapshot: Snapshot,
        health_checks: List[Dict] = None,
        verify: bool = True
    ) -> bool:
        """
        Perform rollback to snapshot
        
        Args:
            snapshot: Snapshot to restore
            health_checks: Optional health checks to run
            verify: Whether to verify rollback success
            
        Returns:
            True if rollback successful
        """
        try:
            self.logger.info(f"Performing rollback to snapshot: {snapshot.snapshot_id}")
            
            # Perform platform-specific rollback
            if snapshot.snapshot_type == SnapshotType.KUBERNETES_DEPLOYMENT:
                success = self.k8s_rollback.rollback(snapshot)
            elif snapshot.snapshot_type in [SnapshotType.DOCKER_CONTAINER, SnapshotType.DOCKER_IMAGE]:
                success = self.docker_rollback.rollback(snapshot)
            elif snapshot.snapshot_type == SnapshotType.VM_SNAPSHOT:
                success = self.vm_rollback.rollback(snapshot)
            else:
                raise ValidationError(f"Unsupported snapshot type: {snapshot.snapshot_type}")
            
            if not success:
                raise RollbackError(f"Rollback operation failed", snapshot_id=snapshot.snapshot_id)
            
            # Verify if requested
            if verify and health_checks:
                if not self.health_checker.verify_rollback(snapshot, health_checks):
                    self.logger.warning("Health checks failed after rollback")
                    return False
            
            # Update database
            self.update_snapshot(snapshot)
            
            self.logger.info(f"✅ Rollback successful: {snapshot.snapshot_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing rollback: {e}")
            raise RollbackError(f"Rollback failed: {e}", snapshot_id=snapshot.snapshot_id)
    
    def save_snapshot(self, snapshot: Snapshot) -> None:
        """Save snapshot to database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO system_snapshots (
                        snapshot_id, execution_id, snapshot_type, platform_config,
                        size_bytes, checksum, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot.snapshot_id,
                    snapshot.execution_id,
                    snapshot.snapshot_type.value,
                    json.dumps({
                        'deployment_name': snapshot.deployment_name,
                        'namespace': snapshot.namespace,
                        'container_id': snapshot.container_id,
                        'image_tag': snapshot.image_tag,
                        'vm_id': snapshot.vm_id,
                        'snapshot_name': snapshot.snapshot_name,
                        'metadata': snapshot.metadata
                    }),
                    snapshot.size_bytes,
                    snapshot.checksum,
                    snapshot.status.value,
                    snapshot.created_at.isoformat()
                ))
                
                self.logger.info(f"✅ Snapshot saved to database: {snapshot.snapshot_id}")
                
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
            raise RemediationDatabaseError(f"Failed to save snapshot: {e}")
    
    def update_snapshot(self, snapshot: Snapshot) -> None:
        """Update snapshot in database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE system_snapshots
                    SET status = ?, restored_at = ?
                    WHERE snapshot_id = ?
                """, (
                    snapshot.status.value,
                    snapshot.restored_at.isoformat() if snapshot.restored_at else None,
                    snapshot.snapshot_id
                ))
                
                self.logger.info(f"✅ Snapshot updated: {snapshot.snapshot_id}")
                
        except Exception as e:
            self.logger.error(f"Error updating snapshot: {e}")
            raise RemediationDatabaseError(f"Failed to update snapshot: {e}")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize manager
    manager = RollbackManager()
    
    # Example: Kubernetes rollback
    k8s_asset = {
        'asset_id': 'K8S-001',
        'asset_type': 'kubernetes_cluster',
        'deployment_name': 'web-app',
        'namespace': 'production'
    }
    
    # Create snapshot
    snapshot = manager.create_snapshot('exec-123', k8s_asset)
    print(f"\n✅ Snapshot created: {snapshot.snapshot_id}")
    
    # Simulate patch application
    time.sleep(2)
    
    # Rollback
    health_checks = [
        {
            'type': 'http',
            'name': 'API Health',
            'url': 'http://web-app.production.svc.cluster.local/health',
            'expected_status': 200
        }
    ]
    
    success = manager.rollback_to_snapshot(snapshot, health_checks=health_checks)
    print(f"\n{'✅' if success else '❌'} Rollback {'successful' if success else 'failed'}")
    print(f"Duration: {snapshot.restore_duration_seconds:.2f}s")
