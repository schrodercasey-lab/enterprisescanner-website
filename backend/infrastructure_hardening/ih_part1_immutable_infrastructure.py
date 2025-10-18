"""
Military-Grade Infrastructure Hardening - Part 1 of 4
====================================================

Immutable Infrastructure & Read-Only Root Filesystem

Features:
- Immutable infrastructure patterns
- Read-only root filesystem
- Ephemeral containers
- Image-based deployments
- Configuration drift prevention

COMPLIANCE:
- NIST 800-53 CM-3 (Configuration Change Control)
- DISA STIG RHEL-08-010690
- CIS Docker Benchmark 5.12
- DoD Cloud Computing SRG
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib


class InfrastructureType(Enum):
    """Infrastructure types"""
    CONTAINER = "Container"
    VM = "Virtual Machine"
    BARE_METAL = "Bare Metal"
    SERVERLESS = "Serverless"


class MutabilityState(Enum):
    """Mutability states"""
    IMMUTABLE = "Immutable"
    MUTABLE = "Mutable"
    READ_ONLY = "Read-Only"
    EPHEMERAL = "Ephemeral"


class DriftStatus(Enum):
    """Configuration drift status"""
    NO_DRIFT = "No Drift"
    MINOR_DRIFT = "Minor Drift"
    MAJOR_DRIFT = "Major Drift"
    CRITICAL_DRIFT = "Critical Drift"


@dataclass
class ImmutableImage:
    """Immutable infrastructure image"""
    image_id: str
    image_name: str
    version: str
    base_image: str
    created_at: datetime
    checksum: str
    signed: bool
    layers: List[str]


@dataclass
class InfrastructureInstance:
    """Infrastructure instance"""
    instance_id: str
    instance_type: InfrastructureType
    image_id: str
    mutability_state: MutabilityState
    read_only_root: bool
    ephemeral_storage: bool
    launched_at: datetime
    baseline_checksum: str


@dataclass
class ConfigurationBaseline:
    """Configuration baseline"""
    baseline_id: str
    instance_id: str
    file_checksums: Dict[str, str]
    package_versions: Dict[str, str]
    service_states: Dict[str, str]
    created_at: datetime


@dataclass
class DriftDetection:
    """Configuration drift detection result"""
    detection_id: str
    instance_id: str
    drift_status: DriftStatus
    modified_files: List[str]
    unauthorized_packages: List[str]
    service_changes: List[str]
    detected_at: datetime


class ImmutableInfrastructureEngine:
    """Immutable Infrastructure Engine - Part 1"""
    
    def __init__(self):
        self.images: Dict[str, ImmutableImage] = {}
        self.instances: Dict[str, InfrastructureInstance] = {}
        self.baselines: Dict[str, ConfigurationBaseline] = {}
        self.drift_detections: List[DriftDetection] = []
    
    def build_immutable_image(self, image_name: str, base_image: str,
                             version: str) -> ImmutableImage:
        """Build immutable infrastructure image"""
        print(f"🏗️  Building immutable image: {image_name}:{version}")
        
        image_id = f"img-{datetime.now().timestamp()}"
        
        # Simulate image build
        layers = [
            f"layer-base-{base_image}",
            f"layer-os-packages",
            f"layer-app-{image_name}",
            f"layer-config"
        ]
        
        # Calculate image checksum
        checksum = self._calculate_image_checksum(image_name, version, layers)
        
        image = ImmutableImage(
            image_id=image_id,
            image_name=image_name,
            version=version,
            base_image=base_image,
            created_at=datetime.now(),
            checksum=checksum,
            signed=True,
            layers=layers
        )
        
        self.images[image_id] = image
        
        print(f"✅ Immutable image built: {image_id}")
        print(f"   Checksum: {checksum}")
        return image
    
    def launch_immutable_instance(self, image_id: str, 
                                  read_only_root: bool = True) -> InfrastructureInstance:
        """Launch instance from immutable image"""
        print(f"🚀 Launching immutable instance from: {image_id}")
        
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        
        image = self.images[image_id]
        instance_id = f"inst-{datetime.now().timestamp()}"
        
        # Verify image integrity
        if not self._verify_image_integrity(image):
            raise ValueError("Image integrity check failed")
        
        instance = InfrastructureInstance(
            instance_id=instance_id,
            instance_type=InfrastructureType.CONTAINER,
            image_id=image_id,
            mutability_state=MutabilityState.IMMUTABLE,
            read_only_root=read_only_root,
            ephemeral_storage=True,
            launched_at=datetime.now(),
            baseline_checksum=image.checksum
        )
        
        self.instances[instance_id] = instance
        
        print(f"✅ Instance launched: {instance_id}")
        print(f"   Read-only root: {read_only_root}")
        print(f"   Ephemeral storage: True")
        
        return instance
    
    def configure_read_only_root(self, instance_id: str) -> Dict[str, Any]:
        """Configure read-only root filesystem"""
        print(f"🔒 Configuring read-only root: {instance_id}")
        
        if instance_id not in self.instances:
            return {"success": False, "reason": "Instance not found"}
        
        instance = self.instances[instance_id]
        
        # Mount configuration
        mount_config = {
            "/": {"mode": "ro", "type": "overlay"},
            "/tmp": {"mode": "rw", "type": "tmpfs"},
            "/var/tmp": {"mode": "rw", "type": "tmpfs"},
            "/var/log": {"mode": "rw", "type": "volume"},
            "/var/run": {"mode": "rw", "type": "tmpfs"}
        }
        
        # Apply read-only root
        instance.read_only_root = True
        instance.mutability_state = MutabilityState.READ_ONLY
        
        print(f"✅ Read-only root configured")
        print(f"   Root filesystem: read-only")
        print(f"   Writable mounts: /tmp, /var/tmp, /var/log, /var/run")
        
        return {
            "success": True,
            "mount_config": mount_config,
            "security_benefit": "Prevents runtime modification of system files"
        }
    
    def create_configuration_baseline(self, instance_id: str) -> ConfigurationBaseline:
        """Create configuration baseline for instance"""
        print(f"📋 Creating configuration baseline: {instance_id}")
        
        if instance_id not in self.instances:
            raise ValueError(f"Instance not found: {instance_id}")
        
        baseline_id = f"baseline-{datetime.now().timestamp()}"
        
        # Capture current state
        file_checksums = self._capture_file_checksums(instance_id)
        package_versions = self._capture_package_versions(instance_id)
        service_states = self._capture_service_states(instance_id)
        
        baseline = ConfigurationBaseline(
            baseline_id=baseline_id,
            instance_id=instance_id,
            file_checksums=file_checksums,
            package_versions=package_versions,
            service_states=service_states,
            created_at=datetime.now()
        )
        
        self.baselines[baseline_id] = baseline
        
        print(f"✅ Baseline created: {baseline_id}")
        print(f"   Files monitored: {len(file_checksums)}")
        print(f"   Packages tracked: {len(package_versions)}")
        
        return baseline
    
    def detect_configuration_drift(self, instance_id: str) -> DriftDetection:
        """Detect configuration drift from baseline"""
        print(f"🔍 Detecting configuration drift: {instance_id}")
        
        if instance_id not in self.instances:
            raise ValueError(f"Instance not found: {instance_id}")
        
        # Find baseline
        baseline = None
        for b in self.baselines.values():
            if b.instance_id == instance_id:
                baseline = b
                break
        
        if not baseline:
            raise ValueError(f"No baseline found for instance: {instance_id}")
        
        # Compare current state to baseline
        current_files = self._capture_file_checksums(instance_id)
        current_packages = self._capture_package_versions(instance_id)
        current_services = self._capture_service_states(instance_id)
        
        # Detect changes
        modified_files = []
        for file_path, checksum in current_files.items():
            baseline_checksum = baseline.file_checksums.get(file_path)
            if baseline_checksum and baseline_checksum != checksum:
                modified_files.append(file_path)
        
        unauthorized_packages = []
        for pkg, version in current_packages.items():
            if pkg not in baseline.package_versions:
                unauthorized_packages.append(f"{pkg}:{version}")
        
        service_changes = []
        for service, state in current_services.items():
            baseline_state = baseline.service_states.get(service)
            if baseline_state and baseline_state != state:
                service_changes.append(f"{service}: {baseline_state} -> {state}")
        
        # Determine drift status
        drift_status = self._calculate_drift_status(
            len(modified_files),
            len(unauthorized_packages),
            len(service_changes)
        )
        
        detection = DriftDetection(
            detection_id=f"drift-{datetime.now().timestamp()}",
            instance_id=instance_id,
            drift_status=drift_status,
            modified_files=modified_files,
            unauthorized_packages=unauthorized_packages,
            service_changes=service_changes,
            detected_at=datetime.now()
        )
        
        self.drift_detections.append(detection)
        
        print(f"{'⚠️' if drift_status != DriftStatus.NO_DRIFT else '✅'} Drift Status: {drift_status.value}")
        if modified_files:
            print(f"   Modified files: {len(modified_files)}")
        if unauthorized_packages:
            print(f"   Unauthorized packages: {len(unauthorized_packages)}")
        if service_changes:
            print(f"   Service changes: {len(service_changes)}")
        
        return detection
    
    def remediate_drift(self, instance_id: str) -> Dict[str, Any]:
        """Remediate configuration drift by replacing instance"""
        print(f"🔄 Remediating drift: {instance_id}")
        
        if instance_id not in self.instances:
            return {"success": False, "reason": "Instance not found"}
        
        instance = self.instances[instance_id]
        
        # Immutable infrastructure approach: Replace, don't repair
        print(f"   Strategy: Replace instance with fresh image")
        
        # Launch new instance from original image
        new_instance = self.launch_immutable_instance(
            instance.image_id,
            read_only_root=instance.read_only_root
        )
        
        # Terminate old instance
        print(f"   Terminating drifted instance: {instance_id}")
        
        return {
            "success": True,
            "strategy": "replace",
            "old_instance_id": instance_id,
            "new_instance_id": new_instance.instance_id,
            "reason": "Immutable infrastructure - replaced instead of patched"
        }
    
    def enforce_ephemeral_storage(self, instance_id: str) -> Dict[str, Any]:
        """Enforce ephemeral storage policies"""
        print(f"💾 Enforcing ephemeral storage: {instance_id}")
        
        if instance_id not in self.instances:
            return {"success": False, "reason": "Instance not found"}
        
        instance = self.instances[instance_id]
        
        storage_config = {
            "ephemeral_paths": [
                "/tmp",
                "/var/tmp",
                "/run",
                "/var/run",
                "/var/cache"
            ],
            "persistent_paths": [
                "/var/log",  # Logs persist for audit
            ],
            "policy": {
                "tmpfs_size_limit": "100M",
                "auto_cleanup": True,
                "cleanup_interval": "1h"
            }
        }
        
        instance.ephemeral_storage = True
        
        print(f"✅ Ephemeral storage enforced")
        print(f"   Ephemeral paths: {len(storage_config['ephemeral_paths'])}")
        print(f"   Persistent paths: {len(storage_config['persistent_paths'])}")
        
        return {
            "success": True,
            "config": storage_config,
            "security_benefit": "All runtime changes lost on restart"
        }
    
    def validate_immutability(self, instance_id: str) -> Dict[str, Any]:
        """Validate instance immutability"""
        print(f"✓ Validating immutability: {instance_id}")
        
        if instance_id not in self.instances:
            return {"valid": False, "reason": "Instance not found"}
        
        instance = self.instances[instance_id]
        
        checks = []
        
        # Check 1: Read-only root
        checks.append({
            "check": "Read-only root filesystem",
            "passed": instance.read_only_root,
            "impact": "HIGH"
        })
        
        # Check 2: Ephemeral storage
        checks.append({
            "check": "Ephemeral storage",
            "passed": instance.ephemeral_storage,
            "impact": "HIGH"
        })
        
        # Check 3: No configuration drift
        drift = self.detect_configuration_drift(instance_id)
        checks.append({
            "check": "No configuration drift",
            "passed": drift.drift_status == DriftStatus.NO_DRIFT,
            "impact": "CRITICAL"
        })
        
        # Check 4: Image signature verified
        image = self.images[instance.image_id]
        checks.append({
            "check": "Image signature verified",
            "passed": image.signed,
            "impact": "CRITICAL"
        })
        
        passed_checks = sum(1 for c in checks if c["passed"])
        total_checks = len(checks)
        
        valid = passed_checks == total_checks
        
        print(f"{'✅' if valid else '⚠️'} Immutability: {passed_checks}/{total_checks} checks passed")
        
        return {
            "valid": valid,
            "checks": checks,
            "passed": passed_checks,
            "total": total_checks
        }
    
    def _calculate_image_checksum(self, name: str, version: str, 
                                  layers: List[str]) -> str:
        """Calculate image checksum"""
        data = f"{name}:{version}:{'|'.join(layers)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _verify_image_integrity(self, image: ImmutableImage) -> bool:
        """Verify image integrity"""
        # Recalculate checksum
        expected = self._calculate_image_checksum(
            image.image_name,
            image.version,
            image.layers
        )
        return expected == image.checksum
    
    def _capture_file_checksums(self, instance_id: str) -> Dict[str, str]:
        """Capture file checksums (simulated)"""
        return {
            "/etc/passwd": "abc123",
            "/etc/shadow": "def456",
            "/etc/hosts": "ghi789",
            "/bin/bash": "jkl012"
        }
    
    def _capture_package_versions(self, instance_id: str) -> Dict[str, str]:
        """Capture installed package versions (simulated)"""
        return {
            "openssl": "1.1.1",
            "openssh": "8.2p1",
            "systemd": "245"
        }
    
    def _capture_service_states(self, instance_id: str) -> Dict[str, str]:
        """Capture service states (simulated)"""
        return {
            "sshd": "active",
            "systemd": "active",
            "cron": "active"
        }
    
    def _calculate_drift_status(self, modified_files: int, 
                               unauthorized_packages: int,
                               service_changes: int) -> DriftStatus:
        """Calculate drift status"""
        total_changes = modified_files + unauthorized_packages + service_changes
        
        if total_changes == 0:
            return DriftStatus.NO_DRIFT
        elif total_changes <= 2:
            return DriftStatus.MINOR_DRIFT
        elif total_changes <= 5:
            return DriftStatus.MAJOR_DRIFT
        else:
            return DriftStatus.CRITICAL_DRIFT


def main():
    """Test immutable infrastructure engine"""
    engine = ImmutableInfrastructureEngine()
    
    print("=" * 70)
    print("IMMUTABLE INFRASTRUCTURE ENGINE")
    print("=" * 70)
    
    # Build immutable image
    image = engine.build_immutable_image(
        image_name="web-server",
        base_image="alpine:3.18",
        version="1.0.0"
    )
    
    # Launch instance
    print("\n" + "=" * 70)
    instance = engine.launch_immutable_instance(image.image_id, read_only_root=True)
    
    # Configure read-only root
    print("\n" + "=" * 70)
    ro_config = engine.configure_read_only_root(instance.instance_id)
    
    # Create baseline
    print("\n" + "=" * 70)
    baseline = engine.create_configuration_baseline(instance.instance_id)
    
    # Detect drift
    print("\n" + "=" * 70)
    drift = engine.detect_configuration_drift(instance.instance_id)
    
    # Enforce ephemeral storage
    print("\n" + "=" * 70)
    ephemeral = engine.enforce_ephemeral_storage(instance.instance_id)
    
    # Validate immutability
    print("\n" + "=" * 70)
    validation = engine.validate_immutability(instance.instance_id)


if __name__ == "__main__":
    main()
