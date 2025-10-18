"""
Jupiter v3.0 - Module G.1: Patch Engine
Multi-source patch acquisition, verification, and management

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

import sqlite3
import hashlib
import subprocess
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import requests
from contextlib import contextmanager

try:
    from .config import get_config
    from .exceptions import (
        PatchError,
        ValidationError,
        DependencyError,
        RemediationDatabaseError
    )
except ImportError:
    # Fallback for standalone execution
    class PatchError(Exception):
        pass
    class ValidationError(Exception):
        pass
    class DependencyError(Exception):
        pass
    class RemediationDatabaseError(Exception):
        pass
    
    class MockConfig:
        database_path = "jupiter_remediation.db"
        patch_signature_verification = True
        patch_maturity_threshold_days = 7
        trusted_patch_sources = ['vendor_official', 'os_package_manager', 'docker_registry']
    
    def get_config():
        return MockConfig()


class PatchSource(Enum):
    """Patch source types"""
    VENDOR_OFFICIAL = "vendor_official"
    OS_PACKAGE_MANAGER = "os_package_manager"
    DOCKER_REGISTRY = "docker_registry"
    GITHUB_RELEASE = "github_release"
    CUSTOM_REPOSITORY = "custom_repository"
    MANUAL_UPLOAD = "manual_upload"


class PatchStatus(Enum):
    """Patch status in catalog"""
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    FAILED_VERIFICATION = "failed_verification"
    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    RECALLED = "recalled"


@dataclass
class PatchMetadata:
    """Patch metadata structure"""
    patch_id: str
    cve_id: str
    vendor: str
    product: str
    version: str
    source: PatchSource
    
    # File information
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    sha256_checksum: Optional[str] = None
    
    # Signature verification
    signature: Optional[str] = None
    signature_verified: bool = False
    
    # Dependencies
    prerequisites: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    superseded_by: Optional[str] = None
    
    # Impact information
    requires_reboot: bool = False
    requires_downtime: bool = False
    estimated_downtime_minutes: int = 0
    
    # Success tracking
    success_rate: float = 0.0
    total_applications: int = 0
    successful_applications: int = 0
    
    # Metadata
    release_date: Optional[datetime] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    release_notes_url: Optional[str] = None
    
    # Status
    status: PatchStatus = PatchStatus.PENDING_VERIFICATION
    created_at: datetime = field(default_factory=datetime.now)
    verified_at: Optional[datetime] = None


class VendorPatchRepository:
    """Fetch patches from official vendor sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JupiterRemediationEngine/1.0'
        })
    
    def fetch_microsoft_patch(self, cve_id: str, product: str) -> Optional[PatchMetadata]:
        """
        Fetch patch from Microsoft Update Catalog
        
        Args:
            cve_id: CVE identifier
            product: Microsoft product name
            
        Returns:
            PatchMetadata if found, None otherwise
        """
        try:
            self.logger.info(f"Fetching Microsoft patch for {cve_id}")
            
            # Microsoft Update Catalog API (example - actual API varies)
            url = f"https://www.catalog.update.microsoft.com/api/v1/patches/{cve_id}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                return PatchMetadata(
                    patch_id=data.get('kb_number', f"MS-{cve_id}"),
                    cve_id=cve_id,
                    vendor="Microsoft",
                    product=product,
                    version=data.get('version', '1.0'),
                    source=PatchSource.VENDOR_OFFICIAL,
                    file_url=data.get('download_url'),
                    sha256_checksum=data.get('sha256'),
                    requires_reboot=data.get('requires_reboot', False),
                    release_date=datetime.fromisoformat(data.get('release_date')),
                    description=data.get('description'),
                    release_notes_url=data.get('release_notes')
                )
            else:
                self.logger.warning(f"Microsoft patch not found: {cve_id} (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching Microsoft patch: {e}")
            return None
    
    def fetch_redhat_patch(self, cve_id: str, product: str) -> Optional[PatchMetadata]:
        """
        Fetch patch from Red Hat Security Data API
        
        Args:
            cve_id: CVE identifier
            product: Red Hat product name
            
        Returns:
            PatchMetadata if found, None otherwise
        """
        try:
            self.logger.info(f"Fetching Red Hat patch for {cve_id}")
            
            # Red Hat Security Data API
            url = f"https://access.redhat.com/hydra/rest/securitydata/cve/{cve_id}.json"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract RHSA (Red Hat Security Advisory)
                advisories = data.get('advisories', [])
                if advisories:
                    advisory = advisories[0]
                    
                    return PatchMetadata(
                        patch_id=advisory.get('rhsa', f"RHSA-{cve_id}"),
                        cve_id=cve_id,
                        vendor="Red Hat",
                        product=product,
                        version=advisory.get('version', '1.0'),
                        source=PatchSource.VENDOR_OFFICIAL,
                        file_url=advisory.get('portal_url'),
                        release_date=datetime.fromisoformat(advisory.get('release_date')),
                        severity=advisory.get('severity'),
                        description=data.get('bugzilla', {}).get('description'),
                        release_notes_url=advisory.get('portal_url')
                    )
            
            return None
                
        except Exception as e:
            self.logger.error(f"Error fetching Red Hat patch: {e}")
            return None
    
    def fetch_vendor_patch(self, cve_id: str, vendor: str, product: str) -> Optional[PatchMetadata]:
        """
        Fetch patch from appropriate vendor source
        
        Args:
            cve_id: CVE identifier
            vendor: Vendor name
            product: Product name
            
        Returns:
            PatchMetadata if found, None otherwise
        """
        vendor_lower = vendor.lower()
        
        if 'microsoft' in vendor_lower:
            return self.fetch_microsoft_patch(cve_id, product)
        elif 'red hat' in vendor_lower or 'redhat' in vendor_lower:
            return self.fetch_redhat_patch(cve_id, product)
        else:
            self.logger.warning(f"Unsupported vendor for patch fetch: {vendor}")
            return None


class OSPackageManager:
    """Manage patches through OS package managers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_available_update(self, package_name: str, os_type: str) -> Optional[PatchMetadata]:
        """
        Check for available package updates
        
        Args:
            package_name: Package name
            os_type: Operating system (ubuntu, centos, debian, etc.)
            
        Returns:
            PatchMetadata if update available, None otherwise
        """
        try:
            os_lower = os_type.lower()
            
            if 'ubuntu' in os_lower or 'debian' in os_lower:
                return self._apt_check_update(package_name)
            elif 'centos' in os_lower or 'rhel' in os_lower or 'redhat' in os_lower:
                return self._yum_check_update(package_name)
            elif 'fedora' in os_lower:
                return self._dnf_check_update(package_name)
            else:
                self.logger.warning(f"Unsupported OS type: {os_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error checking package update: {e}")
            return None
    
    def _apt_check_update(self, package_name: str) -> Optional[PatchMetadata]:
        """Check for updates using apt (Debian/Ubuntu)"""
        try:
            # Check if package has updates available
            result = subprocess.run(
                ['apt-cache', 'policy', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse installed and candidate versions
                installed_match = re.search(r'Installed: (.+)', output)
                candidate_match = re.search(r'Candidate: (.+)', output)
                
                if installed_match and candidate_match:
                    installed = installed_match.group(1)
                    candidate = candidate_match.group(1)
                    
                    if installed != candidate and candidate != '(none)':
                        return PatchMetadata(
                            patch_id=f"apt-{package_name}-{candidate}",
                            cve_id="N/A",  # APT updates may not have CVE
                            vendor="Debian/Ubuntu",
                            product=package_name,
                            version=candidate,
                            source=PatchSource.OS_PACKAGE_MANAGER,
                            description=f"Update {package_name} from {installed} to {candidate}"
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in apt check: {e}")
            return None
    
    def _yum_check_update(self, package_name: str) -> Optional[PatchMetadata]:
        """Check for updates using yum (CentOS/RHEL)"""
        try:
            result = subprocess.run(
                ['yum', 'list', 'updates', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and package_name in result.stdout:
                # Parse version from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if package_name in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            version = parts[1]
                            
                            return PatchMetadata(
                                patch_id=f"yum-{package_name}-{version}",
                                cve_id="N/A",
                                vendor="Red Hat/CentOS",
                                product=package_name,
                                version=version,
                                source=PatchSource.OS_PACKAGE_MANAGER,
                                description=f"Update {package_name} to {version}"
                            )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in yum check: {e}")
            return None
    
    def _dnf_check_update(self, package_name: str) -> Optional[PatchMetadata]:
        """Check for updates using dnf (Fedora)"""
        try:
            result = subprocess.run(
                ['dnf', 'list', 'updates', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and package_name in result.stdout:
                # Similar parsing to yum
                lines = result.stdout.split('\n')
                for line in lines:
                    if package_name in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            version = parts[1]
                            
                            return PatchMetadata(
                                patch_id=f"dnf-{package_name}-{version}",
                                cve_id="N/A",
                                vendor="Fedora",
                                product=package_name,
                                version=version,
                                source=PatchSource.OS_PACKAGE_MANAGER,
                                description=f"Update {package_name} to {version}"
                            )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in dnf check: {e}")
            return None


class ContainerRegistryClient:
    """Fetch patched container images from registries"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
    
    def get_patched_image(self, image_name: str, cve_id: str, registry: str = "docker.io") -> Optional[PatchMetadata]:
        """
        Find patched container image version
        
        Args:
            image_name: Container image name (e.g., nginx, redis)
            cve_id: CVE identifier to patch
            registry: Container registry (docker.io, gcr.io, etc.)
            
        Returns:
            PatchMetadata with patched image info, None if not found
        """
        try:
            self.logger.info(f"Searching for patched image: {image_name} for {cve_id}")
            
            if registry == "docker.io":
                return self._dockerhub_search(image_name, cve_id)
            else:
                self.logger.warning(f"Unsupported registry: {registry}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error searching container registry: {e}")
            return None
    
    def _dockerhub_search(self, image_name: str, cve_id: str) -> Optional[PatchMetadata]:
        """Search Docker Hub for patched images"""
        try:
            # Docker Hub API
            url = f"https://hub.docker.com/v2/repositories/library/{image_name}/tags"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tags = data.get('results', [])
                
                # Find latest tag (simple heuristic - production would be more sophisticated)
                if tags:
                    latest_tag = tags[0]
                    
                    return PatchMetadata(
                        patch_id=f"docker-{image_name}-{latest_tag['name']}",
                        cve_id=cve_id,
                        vendor="Docker Official",
                        product=image_name,
                        version=latest_tag['name'],
                        source=PatchSource.DOCKER_REGISTRY,
                        file_url=f"docker.io/library/{image_name}:{latest_tag['name']}",
                        file_size=latest_tag.get('full_size'),
                        release_date=datetime.fromisoformat(latest_tag['last_updated'].replace('Z', '+00:00')),
                        description=f"Patched {image_name} container image"
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching Docker Hub: {e}")
            return None


class PatchVerifier:
    """Verify patch integrity and authenticity"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
    
    def verify_checksum(self, file_path: str, expected_sha256: str) -> bool:
        """
        Verify file SHA256 checksum
        
        Args:
            file_path: Path to file
            expected_sha256: Expected SHA256 hash
            
        Returns:
            True if checksum matches, False otherwise
        """
        try:
            self.logger.info(f"Verifying checksum for {file_path}")
            
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            
            calculated = sha256_hash.hexdigest()
            matches = calculated.lower() == expected_sha256.lower()
            
            if matches:
                self.logger.info(f"✅ Checksum verified: {calculated}")
            else:
                self.logger.error(f"❌ Checksum mismatch! Expected: {expected_sha256}, Got: {calculated}")
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error verifying checksum: {e}")
            return False
    
    def verify_signature(self, file_path: str, signature_path: str = None) -> bool:
        """
        Verify file digital signature (GPG/PGP)
        
        Args:
            file_path: Path to file
            signature_path: Path to signature file (optional, may be embedded)
            
        Returns:
            True if signature valid, False otherwise
        """
        try:
            if not self.config.patch_signature_verification:
                self.logger.warning("Signature verification disabled in config")
                return True
            
            self.logger.info(f"Verifying signature for {file_path}")
            
            # Try GPG verification
            cmd = ['gpg', '--verify']
            if signature_path:
                cmd.extend([signature_path, file_path])
            else:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ Signature verified")
                return True
            else:
                self.logger.error(f"❌ Signature verification failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            self.logger.warning("GPG not available, skipping signature verification")
            return True  # Don't fail if GPG not installed
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    def verify_patch_maturity(self, release_date: datetime) -> Tuple[bool, int]:
        """
        Verify patch has sufficient maturity (age)
        
        Args:
            release_date: Patch release date
            
        Returns:
            Tuple of (is_mature, days_old)
        """
        try:
            age = datetime.now() - release_date
            days_old = age.days
            
            is_mature = days_old >= self.config.patch_maturity_threshold_days
            
            if is_mature:
                self.logger.info(f"✅ Patch mature: {days_old} days old")
            else:
                self.logger.warning(f"⚠️  Patch immature: {days_old} days old (threshold: {self.config.patch_maturity_threshold_days})")
            
            return is_mature, days_old
            
        except Exception as e:
            self.logger.error(f"Error checking patch maturity: {e}")
            return False, 0


class PatchEngine:
    """Main patch engine orchestrating all sources"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize patch engine
        
        Args:
            db_path: Path to database (default from config)
        """
        self.config = get_config()
        self.db_path = db_path or self.config.database_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize sources
        self.vendor_repo = VendorPatchRepository()
        self.os_package_mgr = OSPackageManager()
        self.container_registry = ContainerRegistryClient()
        self.verifier = PatchVerifier()
    
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
    
    def find_patch(self, vulnerability: Dict, asset: Dict) -> Optional[PatchMetadata]:
        """
        Find appropriate patch from all sources
        
        Args:
            vulnerability: Vulnerability data with cve_id, vendor, product
            asset: Asset data with os_type, asset_type
            
        Returns:
            PatchMetadata if found, None otherwise
        """
        try:
            cve_id = vulnerability.get('cve_id')
            vendor = vulnerability.get('vendor', 'Unknown')
            product = vulnerability.get('product', 'Unknown')
            
            self.logger.info(f"Searching for patch: {cve_id} ({vendor} {product})")
            
            # Try vendor repository first
            if 'vendor_official' in self.config.trusted_patch_sources:
                patch = self.vendor_repo.fetch_vendor_patch(cve_id, vendor, product)
                if patch:
                    self.logger.info(f"✅ Found patch from vendor: {patch.patch_id}")
                    return patch
            
            # Try OS package manager
            if 'os_package_manager' in self.config.trusted_patch_sources:
                os_type = asset.get('os_type', 'Unknown')
                package_name = product.lower()
                
                patch = self.os_package_mgr.get_available_update(package_name, os_type)
                if patch:
                    patch.cve_id = cve_id  # Associate with CVE
                    self.logger.info(f"✅ Found patch from package manager: {patch.patch_id}")
                    return patch
            
            # Try container registry
            if 'docker_registry' in self.config.trusted_patch_sources:
                if asset.get('asset_type') == 'container':
                    image_name = asset.get('container_image', product).split(':')[0]
                    
                    patch = self.container_registry.get_patched_image(image_name, cve_id)
                    if patch:
                        self.logger.info(f"✅ Found patch from container registry: {patch.patch_id}")
                        return patch
            
            self.logger.warning(f"❌ No patch found for {cve_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding patch: {e}")
            raise PatchError(f"Failed to find patch: {e}")
    
    def verify_patch(self, patch: PatchMetadata, file_path: str = None) -> bool:
        """
        Verify patch integrity and authenticity
        
        Args:
            patch: Patch metadata
            file_path: Path to downloaded patch file
            
        Returns:
            True if all verifications pass, False otherwise
        """
        try:
            self.logger.info(f"Verifying patch: {patch.patch_id}")
            
            # Verify checksum if available
            if file_path and patch.sha256_checksum:
                if not self.verifier.verify_checksum(file_path, patch.sha256_checksum):
                    patch.status = PatchStatus.FAILED_VERIFICATION
                    return False
            
            # Verify signature if required
            if file_path and patch.signature:
                if not self.verifier.verify_signature(file_path):
                    patch.status = PatchStatus.FAILED_VERIFICATION
                    return False
            
            # Verify patch maturity
            if patch.release_date:
                is_mature, days_old = self.verifier.verify_patch_maturity(patch.release_date)
                if not is_mature:
                    self.logger.warning(f"Patch not mature enough: {days_old} days old")
                    # Note: Don't fail verification, just warn
            
            # All verifications passed
            patch.status = PatchStatus.VERIFIED
            patch.signature_verified = True
            patch.verified_at = datetime.now()
            
            self.logger.info(f"✅ Patch verified successfully: {patch.patch_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying patch: {e}")
            patch.status = PatchStatus.FAILED_VERIFICATION
            return False
    
    def save_patch(self, patch: PatchMetadata) -> str:
        """
        Save patch to database catalog
        
        Args:
            patch: Patch metadata
            
        Returns:
            Patch ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO patches (
                        patch_id, cve_id, vendor, product, version, source,
                        file_path, file_url, sha256_checksum, signature_verified,
                        prerequisites, requires_reboot, requires_downtime,
                        release_date, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patch.patch_id,
                    patch.cve_id,
                    patch.vendor,
                    patch.product,
                    patch.version,
                    patch.source.value,
                    patch.file_path,
                    patch.file_url,
                    patch.sha256_checksum,
                    patch.signature_verified,
                    json.dumps(patch.prerequisites),
                    patch.requires_reboot,
                    patch.requires_downtime,
                    patch.release_date.isoformat() if patch.release_date else None,
                    patch.status.value,
                    patch.created_at.isoformat()
                ))
                
                self.logger.info(f"✅ Saved patch to catalog: {patch.patch_id}")
                return patch.patch_id
                
        except sqlite3.IntegrityError:
            # Patch already exists, update instead
            self.logger.info(f"Patch exists, updating: {patch.patch_id}")
            return self.update_patch(patch)
        except Exception as e:
            self.logger.error(f"Error saving patch: {e}")
            raise RemediationDatabaseError(f"Failed to save patch: {e}")
    
    def update_patch(self, patch: PatchMetadata) -> str:
        """
        Update existing patch in catalog
        
        Args:
            patch: Updated patch metadata
            
        Returns:
            Patch ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE patches SET
                        file_path = ?,
                        file_url = ?,
                        sha256_checksum = ?,
                        signature_verified = ?,
                        status = ?,
                        success_rate = ?,
                        total_applications = ?,
                        successful_applications = ?
                    WHERE patch_id = ?
                """, (
                    patch.file_path,
                    patch.file_url,
                    patch.sha256_checksum,
                    patch.signature_verified,
                    patch.status.value,
                    patch.success_rate,
                    patch.total_applications,
                    patch.successful_applications,
                    patch.patch_id
                ))
                
                self.logger.info(f"✅ Updated patch: {patch.patch_id}")
                return patch.patch_id
                
        except Exception as e:
            self.logger.error(f"Error updating patch: {e}")
            raise RemediationDatabaseError(f"Failed to update patch: {e}")
    
    def get_patch(self, patch_id: str) -> Optional[PatchMetadata]:
        """
        Retrieve patch from catalog
        
        Args:
            patch_id: Patch identifier
            
        Returns:
            PatchMetadata if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM patches WHERE patch_id = ?
                """, (patch_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_patch(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving patch: {e}")
            return None
    
    def _row_to_patch(self, row: sqlite3.Row) -> PatchMetadata:
        """Convert database row to PatchMetadata"""
        return PatchMetadata(
            patch_id=row['patch_id'],
            cve_id=row['cve_id'],
            vendor=row['vendor'],
            product=row['product'],
            version=row['version'],
            source=PatchSource(row['source']),
            file_path=row['file_path'],
            file_url=row['file_url'],
            sha256_checksum=row['sha256_checksum'],
            signature_verified=bool(row['signature_verified']),
            prerequisites=json.loads(row['prerequisites']) if row['prerequisites'] else [],
            requires_reboot=bool(row['requires_reboot']),
            requires_downtime=bool(row['requires_downtime']),
            success_rate=row['success_rate'],
            total_applications=row['total_applications'],
            successful_applications=row['successful_applications'],
            release_date=datetime.fromisoformat(row['release_date']) if row['release_date'] else None,
            status=PatchStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at'])
        )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize patch engine
    engine = PatchEngine()
    
    # Example: Find patch for vulnerability
    vulnerability = {
        'vuln_id': 'V-2024-001',
        'cve_id': 'CVE-2024-12345',
        'vendor': 'Microsoft',
        'product': 'Windows Server',
        'severity': 9.8
    }
    
    asset = {
        'asset_id': 'A-1001',
        'os_type': 'Windows Server 2022',
        'asset_type': 'server'
    }
    
    # Find patch
    patch = engine.find_patch(vulnerability, asset)
    
    if patch:
        print(f"\n✅ Found patch: {patch.patch_id}")
        print(f"   Vendor: {patch.vendor}")
        print(f"   Product: {patch.product}")
        print(f"   Version: {patch.version}")
        print(f"   Source: {patch.source.value}")
        print(f"   Requires reboot: {patch.requires_reboot}")
        
        # Save to catalog
        patch_id = engine.save_patch(patch)
        print(f"   Saved to catalog: {patch_id}")
    else:
        print(f"\n❌ No patch found for {vulnerability['cve_id']}")
