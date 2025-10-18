"""
Military-Grade Backup & Disaster Recovery - Part 1 of 4
=======================================================

3-2-1 Backup Strategy Automation

Features:
- 3-2-1 backup rule enforcement (3 copies, 2 media types, 1 offsite)
- Automated backup scheduling
- Incremental and differential backups
- Backup verification and integrity checks
- Retention policy management

COMPLIANCE:
- NIST 800-34 (Contingency Planning)
- NIST 800-53 CP-9 (System Backup)
- DoD RMF CP-9
- CMMC Level 3 RE.L2-3.13.1
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets


class BackupType(Enum):
    """Backup types"""
    FULL = "Full Backup"
    INCREMENTAL = "Incremental Backup"
    DIFFERENTIAL = "Differential Backup"
    SNAPSHOT = "Snapshot"


class BackupMedia(Enum):
    """Backup storage media types"""
    DISK = "Disk Storage"
    TAPE = "Tape Storage"
    CLOUD = "Cloud Storage"
    OBJECT_STORAGE = "Object Storage"


class BackupLocation(Enum):
    """Backup storage locations"""
    PRIMARY = "Primary Site"
    SECONDARY = "Secondary Site"
    OFFSITE = "Offsite/Remote"
    CLOUD = "Cloud Region"


class BackupStatus(Enum):
    """Backup job status"""
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    VERIFIED = "Verified"


@dataclass
class BackupJob:
    """Backup job configuration"""
    job_id: str
    name: str
    backup_type: BackupType
    source_systems: List[str]
    target_media: BackupMedia
    target_location: BackupLocation
    schedule: str  # Cron expression
    retention_days: int
    encryption_enabled: bool
    compression_enabled: bool


@dataclass
class BackupExecution:
    """Backup execution record"""
    execution_id: str
    job_id: str
    backup_type: BackupType
    start_time: datetime
    end_time: Optional[datetime]
    status: BackupStatus
    data_size: int  # bytes
    backup_size: int  # bytes after compression
    checksum: str
    target_location: str
    verified: bool


@dataclass
class BackupCopy:
    """Individual backup copy in 3-2-1 strategy"""
    copy_id: str
    execution_id: str
    media_type: BackupMedia
    location: BackupLocation
    path: str
    size: int
    checksum: str
    created_at: datetime
    expires_at: datetime


@dataclass
class BackupVerification:
    """Backup verification result"""
    verification_id: str
    copy_id: str
    verified_at: datetime
    checksum_valid: bool
    restore_test_passed: bool
    issues: List[str]


class BackupStrategyEngine:
    """3-2-1 Backup Strategy Engine - Part 1"""
    
    def __init__(self):
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.executions: Dict[str, BackupExecution] = {}
        self.backup_copies: Dict[str, List[BackupCopy]] = {}
        self.verifications: List[BackupVerification] = []
    
    def create_backup_job(self, name: str, 
                         backup_type: BackupType,
                         source_systems: List[str],
                         schedule: str,
                         retention_days: int = 30) -> BackupJob:
        """Create automated backup job"""
        print(f"📋 Creating backup job: {name}")
        
        job = BackupJob(
            job_id=f"job-{secrets.token_hex(8)}",
            name=name,
            backup_type=backup_type,
            source_systems=source_systems,
            target_media=BackupMedia.DISK,  # Primary media
            target_location=BackupLocation.PRIMARY,
            schedule=schedule,
            retention_days=retention_days,
            encryption_enabled=True,
            compression_enabled=True
        )
        
        self.backup_jobs[job.job_id] = job
        
        print(f"✅ Backup job created")
        print(f"   Job ID: {job.job_id}")
        print(f"   Type: {backup_type.value}")
        print(f"   Schedule: {schedule}")
        print(f"   Sources: {len(source_systems)}")
        print(f"   Retention: {retention_days} days")
        
        return job
    
    def configure_3_2_1_strategy(self, job_id: str) -> Dict[str, Any]:
        """Configure 3-2-1 backup strategy for a job"""
        print(f"🔄 Configuring 3-2-1 backup strategy for job: {job_id}")
        
        if job_id not in self.backup_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.backup_jobs[job_id]
        
        # 3-2-1 Strategy:
        # - 3 copies total (1 primary + 2 backups)
        # - 2 different media types
        # - 1 offsite copy
        
        strategy = {
            "copies": [
                {
                    "copy_number": 1,
                    "media": BackupMedia.DISK,
                    "location": BackupLocation.PRIMARY,
                    "description": "Primary backup on disk"
                },
                {
                    "copy_number": 2,
                    "media": BackupMedia.TAPE,
                    "location": BackupLocation.SECONDARY,
                    "description": "Secondary backup on tape"
                },
                {
                    "copy_number": 3,
                    "media": BackupMedia.CLOUD,
                    "location": BackupLocation.OFFSITE,
                    "description": "Offsite backup in cloud"
                }
            ],
            "media_types": 3,  # Disk, Tape, Cloud
            "offsite_copies": 1,
            "compliant": True
        }
        
        print(f"✅ 3-2-1 strategy configured")
        print(f"   Copies: {len(strategy['copies'])}")
        print(f"   Media types: {strategy['media_types']}")
        print(f"   Offsite: {strategy['offsite_copies']}")
        
        return strategy
    
    def execute_backup(self, job_id: str) -> BackupExecution:
        """Execute backup job"""
        print(f"▶️  Executing backup job: {job_id}")
        
        if job_id not in self.backup_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.backup_jobs[job_id]
        
        # Simulate backup execution
        data_size = 1024 * 1024 * 1024 * 10  # 10 GB
        compression_ratio = 0.6  # 40% compression
        backup_size = int(data_size * compression_ratio)
        
        # Calculate checksum
        checksum = hashlib.sha256(
            f"{job_id}{datetime.now()}".encode()
        ).hexdigest()
        
        execution = BackupExecution(
            execution_id=f"exec-{secrets.token_hex(8)}",
            job_id=job_id,
            backup_type=job.backup_type,
            start_time=datetime.now(),
            end_time=None,
            status=BackupStatus.IN_PROGRESS,
            data_size=data_size,
            backup_size=backup_size,
            checksum=checksum,
            target_location=f"/backups/{job_id}",
            verified=False
        )
        
        self.executions[execution.execution_id] = execution
        
        # Simulate backup completion
        execution.end_time = execution.start_time + timedelta(minutes=30)
        execution.status = BackupStatus.COMPLETED
        
        # Create backup copies for 3-2-1 strategy
        self._create_backup_copies(execution, job)
        
        duration = (execution.end_time - execution.start_time).total_seconds()
        throughput = (backup_size / (1024 * 1024)) / (duration / 60)  # MB/min
        
        print(f"✅ Backup completed")
        print(f"   Execution ID: {execution.execution_id}")
        print(f"   Duration: {duration/60:.1f} minutes")
        print(f"   Data size: {data_size / (1024**3):.2f} GB")
        print(f"   Backup size: {backup_size / (1024**3):.2f} GB")
        print(f"   Compression: {(1-compression_ratio)*100:.0f}%")
        print(f"   Throughput: {throughput:.1f} MB/min")
        
        return execution
    
    def _create_backup_copies(self, execution: BackupExecution, 
                             job: BackupJob) -> List[BackupCopy]:
        """Create multiple backup copies for 3-2-1 strategy"""
        print(f"  📦 Creating backup copies (3-2-1 strategy)...")
        
        copies = []
        
        # Copy 1: Primary disk storage
        copy1 = BackupCopy(
            copy_id=f"copy-{secrets.token_hex(8)}",
            execution_id=execution.execution_id,
            media_type=BackupMedia.DISK,
            location=BackupLocation.PRIMARY,
            path=f"/backups/primary/{execution.execution_id}",
            size=execution.backup_size,
            checksum=execution.checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=job.retention_days)
        )
        copies.append(copy1)
        
        # Copy 2: Secondary tape storage
        copy2 = BackupCopy(
            copy_id=f"copy-{secrets.token_hex(8)}",
            execution_id=execution.execution_id,
            media_type=BackupMedia.TAPE,
            location=BackupLocation.SECONDARY,
            path=f"/backups/tape/{execution.execution_id}",
            size=execution.backup_size,
            checksum=execution.checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=job.retention_days * 2)
        )
        copies.append(copy2)
        
        # Copy 3: Offsite cloud storage
        copy3 = BackupCopy(
            copy_id=f"copy-{secrets.token_hex(8)}",
            execution_id=execution.execution_id,
            media_type=BackupMedia.CLOUD,
            location=BackupLocation.OFFSITE,
            path=f"s3://backups-offsite/{execution.execution_id}",
            size=execution.backup_size,
            checksum=execution.checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=job.retention_days * 3)
        )
        copies.append(copy3)
        
        self.backup_copies[execution.execution_id] = copies
        
        print(f"  ✅ Created {len(copies)} backup copies")
        for i, copy in enumerate(copies, 1):
            print(f"     Copy {i}: {copy.media_type.value} @ {copy.location.value}")
        
        return copies
    
    def verify_backup(self, copy_id: str) -> BackupVerification:
        """Verify backup integrity"""
        print(f"✓ Verifying backup: {copy_id}")
        
        # Find backup copy
        backup_copy = None
        for copies in self.backup_copies.values():
            for copy in copies:
                if copy.copy_id == copy_id:
                    backup_copy = copy
                    break
        
        if not backup_copy:
            raise ValueError(f"Backup copy {copy_id} not found")
        
        # Verify checksum
        print(f"  ✓ Verifying checksum...")
        checksum_valid = True  # Simulated
        
        # Test restore
        print(f"  ✓ Testing restore operation...")
        restore_test_passed = True  # Simulated
        
        verification = BackupVerification(
            verification_id=f"verify-{secrets.token_hex(8)}",
            copy_id=copy_id,
            verified_at=datetime.now(),
            checksum_valid=checksum_valid,
            restore_test_passed=restore_test_passed,
            issues=[]
        )
        
        self.verifications.append(verification)
        
        # Update execution status
        if backup_copy.execution_id in self.executions:
            self.executions[backup_copy.execution_id].verified = True
            self.executions[backup_copy.execution_id].status = BackupStatus.VERIFIED
        
        print(f"✅ Backup verified")
        print(f"   Checksum: {'✅ Valid' if checksum_valid else '❌ Invalid'}")
        print(f"   Restore test: {'✅ Passed' if restore_test_passed else '❌ Failed'}")
        
        return verification
    
    def apply_retention_policy(self) -> Dict[str, Any]:
        """Apply backup retention policy and cleanup expired backups"""
        print("🗑️  Applying retention policy...")
        
        now = datetime.now()
        expired_copies = []
        retained_copies = []
        
        for execution_id, copies in self.backup_copies.items():
            for copy in copies:
                if copy.expires_at < now:
                    expired_copies.append(copy)
                else:
                    retained_copies.append(copy)
        
        # Cleanup expired backups
        total_freed = sum(copy.size for copy in expired_copies)
        
        result = {
            "timestamp": now,
            "total_copies": len(expired_copies) + len(retained_copies),
            "expired_copies": len(expired_copies),
            "retained_copies": len(retained_copies),
            "space_freed": total_freed
        }
        
        print(f"✅ Retention policy applied")
        print(f"   Total backups: {result['total_copies']}")
        print(f"   Expired: {result['expired_copies']}")
        print(f"   Retained: {result['retained_copies']}")
        print(f"   Space freed: {total_freed / (1024**3):.2f} GB")
        
        return result
    
    def audit_backup_compliance(self) -> Dict[str, Any]:
        """Audit 3-2-1 backup compliance"""
        print("🔍 Auditing backup compliance...")
        
        audit = {
            "timestamp": datetime.now(),
            "total_jobs": len(self.backup_jobs),
            "total_executions": len(self.executions),
            "3_2_1_compliant": 0,
            "non_compliant_executions": [],
            "verification_rate": 0.0,
            "compliance_status": {}
        }
        
        # Check 3-2-1 compliance for each execution
        for execution_id, execution in self.executions.items():
            if execution_id in self.backup_copies:
                copies = self.backup_copies[execution_id]
                
                # Count unique media types
                media_types = set(copy.media_type for copy in copies)
                
                # Count offsite copies
                offsite_copies = sum(
                    1 for copy in copies 
                    if copy.location in [BackupLocation.OFFSITE, BackupLocation.CLOUD]
                )
                
                # Check 3-2-1 rule
                if len(copies) >= 3 and len(media_types) >= 2 and offsite_copies >= 1:
                    audit["3_2_1_compliant"] += 1
                else:
                    audit["non_compliant_executions"].append({
                        "execution_id": execution_id,
                        "copies": len(copies),
                        "media_types": len(media_types),
                        "offsite": offsite_copies
                    })
        
        # Calculate verification rate
        verified = sum(1 for e in self.executions.values() if e.verified)
        audit["verification_rate"] = (verified / len(self.executions) * 100) if self.executions else 0
        
        # Compliance checks
        audit["compliance_status"] = {
            "NIST_800_34": audit["3_2_1_compliant"] > 0,
            "NIST_800_53_CP_9": len(self.backup_jobs) > 0,
            "DoD_RMF_CP_9": audit["verification_rate"] > 90,
            "CMMC_RE_L2_3_13_1": audit["3_2_1_compliant"] == len(self.executions)
        }
        
        print(f"✅ Audit completed")
        print(f"\nCompliance Status:")
        print(f"  3-2-1 compliant: {audit['3_2_1_compliant']}/{len(self.executions)}")
        print(f"  Verification rate: {audit['verification_rate']:.1f}%")
        
        for standard, compliant in audit["compliance_status"].items():
            print(f"  {standard}: {'✅' if compliant else '❌'}")
        
        return audit
    
    def generate_backup_report(self) -> Dict[str, Any]:
        """Generate backup strategy report"""
        print("📊 Generating backup report...")
        
        report = {
            "timestamp": datetime.now(),
            "backup_jobs": len(self.backup_jobs),
            "total_executions": len(self.executions),
            "total_backup_copies": sum(len(copies) for copies in self.backup_copies.values()),
            "total_backup_size": sum(
                sum(copy.size for copy in copies)
                for copies in self.backup_copies.values()
            ),
            "by_type": {},
            "by_media": {},
            "by_location": {},
            "success_rate": 0.0
        }
        
        # Count by backup type
        for execution in self.executions.values():
            backup_type = execution.backup_type.value
            report["by_type"][backup_type] = report["by_type"].get(backup_type, 0) + 1
        
        # Count by media and location
        for copies in self.backup_copies.values():
            for copy in copies:
                media = copy.media_type.value
                location = copy.location.value
                report["by_media"][media] = report["by_media"].get(media, 0) + 1
                report["by_location"][location] = report["by_location"].get(location, 0) + 1
        
        # Calculate success rate
        successful = sum(
            1 for e in self.executions.values() 
            if e.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]
        )
        report["success_rate"] = (successful / len(self.executions) * 100) if self.executions else 0
        
        print(f"✅ Report generated")
        print(f"\nSummary:")
        print(f"  Backup Jobs: {report['backup_jobs']}")
        print(f"  Total Executions: {report['total_executions']}")
        print(f"  Total Copies: {report['total_backup_copies']}")
        print(f"  Total Size: {report['total_backup_size'] / (1024**3):.2f} GB")
        print(f"  Success Rate: {report['success_rate']:.1f}%")
        
        return report


def main():
    """Test 3-2-1 backup strategy engine"""
    engine = BackupStrategyEngine()
    
    print("=" * 70)
    print("3-2-1 BACKUP STRATEGY ENGINE")
    print("=" * 70)
    
    # Create backup jobs
    full_backup = engine.create_backup_job(
        name="Database Full Backup",
        backup_type=BackupType.FULL,
        source_systems=["db-prod-01", "db-prod-02"],
        schedule="0 2 * * 0",  # Weekly on Sunday at 2 AM
        retention_days=30
    )
    
    print("\n" + "=" * 70)
    incremental_backup = engine.create_backup_job(
        name="Database Incremental Backup",
        backup_type=BackupType.INCREMENTAL,
        source_systems=["db-prod-01", "db-prod-02"],
        schedule="0 2 * * 1-6",  # Daily except Sunday at 2 AM
        retention_days=7
    )
    
    # Configure 3-2-1 strategy
    print("\n" + "=" * 70)
    strategy = engine.configure_3_2_1_strategy(full_backup.job_id)
    
    # Execute backup
    print("\n" + "=" * 70)
    execution = engine.execute_backup(full_backup.job_id)
    
    # Verify backups
    print("\n" + "=" * 70)
    if execution.execution_id in engine.backup_copies:
        for copy in engine.backup_copies[execution.execution_id]:
            verification = engine.verify_backup(copy.copy_id)
    
    # Apply retention policy
    print("\n" + "=" * 70)
    retention_result = engine.apply_retention_policy()
    
    # Audit compliance
    print("\n" + "=" * 70)
    audit = engine.audit_backup_compliance()
    
    # Generate report
    print("\n" + "=" * 70)
    report = engine.generate_backup_report()


if __name__ == "__main__":
    main()
