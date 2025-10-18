"""
Military-Grade CI/CD Pipeline Security - Part 2 of 4
====================================================

Pipeline Security Gates & Quality Controls

Features:
- Automated security gates in CI/CD pipeline
- SAST/DAST/SCA integration
- Security policy enforcement
- Break-the-build rules
- Compliance validation gates

COMPLIANCE:
- NIST 800-218 (Secure Software Development Framework)
- OWASP CI/CD Security Top 10
- DoD DevSecOps Reference Design
- CMMC Level 3 (MA.L3)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GateType(Enum):
    """Security gate types"""
    SAST = "Static Application Security Testing"
    DAST = "Dynamic Application Security Testing"
    SCA = "Software Composition Analysis"
    SECRET_SCANNING = "Secret Detection"
    LICENSE_COMPLIANCE = "License Compliance"
    VULNERABILITY_SCAN = "Vulnerability Scanning"
    POLICY_CHECK = "Policy Compliance"


class GateStatus(Enum):
    """Gate execution status"""
    PASSED = "Passed"
    FAILED = "Failed"
    WARNING = "Warning"
    SKIPPED = "Skipped"


class Severity(Enum):
    """Finding severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


@dataclass
class SecurityFinding:
    """Security finding from gate"""
    finding_id: str
    gate_type: GateType
    severity: Severity
    title: str
    description: str
    file_path: Optional[str]
    line_number: Optional[int]
    cwe_id: Optional[str]
    remediation: str


@dataclass
class GateExecution:
    """Security gate execution result"""
    gate_id: str
    gate_type: GateType
    status: GateStatus
    execution_time: float  # seconds
    findings: List[SecurityFinding]
    break_build: bool


@dataclass
class PipelineRun:
    """CI/CD pipeline run"""
    run_id: str
    pipeline_name: str
    commit_sha: str
    branch: str
    started_at: datetime
    completed_at: Optional[datetime]
    gate_results: List[GateExecution]
    overall_status: str


class PipelineSecurityGates:
    """Pipeline Security Gates Engine - Part 2"""
    
    def __init__(self):
        self.gate_policies = self._initialize_gate_policies()
        self.pipeline_runs: List[PipelineRun] = []
    
    def execute_sast_gate(self, source_code_path: str) -> GateExecution:
        """Execute Static Application Security Testing gate"""
        print("🔍 Running SAST gate...")
        
        start_time = datetime.now()
        findings = []
        
        # Simulate SAST scanning (in production, integrate with Semgrep, SonarQube, etc.)
        findings.extend(self._scan_sql_injection(source_code_path))
        findings.extend(self._scan_xss_vulnerabilities(source_code_path))
        findings.extend(self._scan_hardcoded_secrets(source_code_path))
        findings.extend(self._scan_insecure_crypto(source_code_path))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Check break-build conditions
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)
        
        break_build = critical_count > 0 or high_count >= 5
        status = GateStatus.FAILED if break_build else GateStatus.PASSED
        
        print(f"✅ SAST gate complete: {len(findings)} findings ({critical_count} critical)")
        
        return GateExecution(
            gate_id=f"SAST-{datetime.now().timestamp()}",
            gate_type=GateType.SAST,
            status=status,
            execution_time=execution_time,
            findings=findings,
            break_build=break_build
        )
    
    def execute_dast_gate(self, application_url: str) -> GateExecution:
        """Execute Dynamic Application Security Testing gate"""
        print("🔍 Running DAST gate...")
        
        start_time = datetime.now()
        findings = []
        
        # Simulate DAST scanning (in production, integrate with OWASP ZAP, Burp Suite)
        findings.extend(self._test_authentication_bypass(application_url))
        findings.extend(self._test_api_security(application_url))
        findings.extend(self._test_session_management(application_url))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        break_build = critical_count > 0
        status = GateStatus.FAILED if break_build else GateStatus.PASSED
        
        print(f"✅ DAST gate complete: {len(findings)} findings")
        
        return GateExecution(
            gate_id=f"DAST-{datetime.now().timestamp()}",
            gate_type=GateType.DAST,
            status=status,
            execution_time=execution_time,
            findings=findings,
            break_build=break_build
        )
    
    def execute_sca_gate(self, dependencies_file: str) -> GateExecution:
        """Execute Software Composition Analysis gate"""
        print("🔍 Running SCA gate (dependency scanning)...")
        
        start_time = datetime.now()
        findings = []
        
        # Simulate SCA scanning (in production, integrate with Snyk, WhiteSource, etc.)
        findings.extend(self._scan_vulnerable_dependencies(dependencies_file))
        findings.extend(self._scan_outdated_dependencies(dependencies_file))
        findings.extend(self._scan_license_violations(dependencies_file))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        critical_vulns = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        break_build = critical_vulns > 0
        status = GateStatus.FAILED if break_build else GateStatus.PASSED
        
        print(f"✅ SCA gate complete: {len(findings)} findings")
        
        return GateExecution(
            gate_id=f"SCA-{datetime.now().timestamp()}",
            gate_type=GateType.SCA,
            status=status,
            execution_time=execution_time,
            findings=findings,
            break_build=break_build
        )
    
    def execute_secret_scanning_gate(self, repository_path: str) -> GateExecution:
        """Execute secret scanning gate"""
        print("🔍 Running secret scanning gate...")
        
        start_time = datetime.now()
        findings = []
        
        # Simulate secret scanning (in production, integrate with TruffleHog, GitGuardian)
        secret_patterns = [
            ("AWS Access Key", r"AKIA[0-9A-Z]{16}"),
            ("Private Key", r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"),
            ("GitHub Token", r"ghp_[0-9a-zA-Z]{36}"),
            ("API Key", r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[0-9a-zA-Z]{32,}")
        ]
        
        for secret_type, pattern in secret_patterns:
            # Simulated detection
            if self._detect_secret_pattern(repository_path, pattern):
                findings.append(SecurityFinding(
                    finding_id=f"SECRET-{len(findings)+1:04d}",
                    gate_type=GateType.SECRET_SCANNING,
                    severity=Severity.CRITICAL,
                    title=f"{secret_type} detected in repository",
                    description=f"Hardcoded {secret_type} found in source code",
                    file_path="config/settings.py",
                    line_number=42,
                    cwe_id="CWE-798",
                    remediation="Remove hardcoded secret and use environment variables or secret management service"
                ))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        break_build = len(findings) > 0  # Any secret = break build
        status = GateStatus.FAILED if break_build else GateStatus.PASSED
        
        print(f"✅ Secret scanning complete: {len(findings)} secrets found")
        
        return GateExecution(
            gate_id=f"SECRET-{datetime.now().timestamp()}",
            gate_type=GateType.SECRET_SCANNING,
            status=status,
            execution_time=execution_time,
            findings=findings,
            break_build=break_build
        )
    
    def execute_policy_gate(self, artifact_metadata: Dict[str, Any]) -> GateExecution:
        """Execute policy compliance gate"""
        print("🔍 Running policy compliance gate...")
        
        start_time = datetime.now()
        findings = []
        
        # Check container image policies
        if "base_image" in artifact_metadata:
            if not self._verify_approved_base_image(artifact_metadata["base_image"]):
                findings.append(SecurityFinding(
                    finding_id=f"POLICY-{len(findings)+1:04d}",
                    gate_type=GateType.POLICY_CHECK,
                    severity=Severity.HIGH,
                    title="Unapproved base image",
                    description=f"Base image {artifact_metadata['base_image']} not in approved list",
                    file_path="Dockerfile",
                    line_number=1,
                    cwe_id=None,
                    remediation="Use approved base images from enterprise registry"
                ))
        
        # Check for required labels
        required_labels = ["maintainer", "version", "security-scan-date"]
        if "labels" in artifact_metadata:
            missing_labels = [l for l in required_labels if l not in artifact_metadata["labels"]]
            if missing_labels:
                findings.append(SecurityFinding(
                    finding_id=f"POLICY-{len(findings)+1:04d}",
                    gate_type=GateType.POLICY_CHECK,
                    severity=Severity.MEDIUM,
                    title="Missing required labels",
                    description=f"Required labels missing: {', '.join(missing_labels)}",
                    file_path="Dockerfile",
                    line_number=None,
                    cwe_id=None,
                    remediation="Add required labels to Dockerfile"
                ))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        high_violations = sum(1 for f in findings if f.severity == Severity.HIGH)
        break_build = high_violations > 0
        status = GateStatus.FAILED if break_build else GateStatus.PASSED
        
        print(f"✅ Policy gate complete: {len(findings)} violations")
        
        return GateExecution(
            gate_id=f"POLICY-{datetime.now().timestamp()}",
            gate_type=GateType.POLICY_CHECK,
            status=status,
            execution_time=execution_time,
            findings=findings,
            break_build=break_build
        )
    
    def run_security_pipeline(self, pipeline_name: str, commit_sha: str,
                            branch: str) -> PipelineRun:
        """Execute complete security pipeline"""
        print(f"\n🚀 Running security pipeline: {pipeline_name}")
        print(f"   Commit: {commit_sha[:8]}")
        print(f"   Branch: {branch}\n")
        
        pipeline_run = PipelineRun(
            run_id=f"RUN-{datetime.now().timestamp()}",
            pipeline_name=pipeline_name,
            commit_sha=commit_sha,
            branch=branch,
            started_at=datetime.now(),
            completed_at=None,
            gate_results=[],
            overall_status="RUNNING"
        )
        
        # Execute all gates
        gates = [
            self.execute_secret_scanning_gate("./"),
            self.execute_sast_gate("./backend"),
            self.execute_sca_gate("requirements.txt"),
            self.execute_dast_gate("http://localhost:5000"),
            self.execute_policy_gate({"base_image": "python:3.11-slim"})
        ]
        
        pipeline_run.gate_results = gates
        pipeline_run.completed_at = datetime.now()
        
        # Determine overall status
        failed_gates = [g for g in gates if g.status == GateStatus.FAILED]
        if failed_gates:
            pipeline_run.overall_status = "FAILED"
            print(f"\n❌ Pipeline FAILED: {len(failed_gates)} gates failed")
        else:
            pipeline_run.overall_status = "PASSED"
            print(f"\n✅ Pipeline PASSED: All gates passed")
        
        self.pipeline_runs.append(pipeline_run)
        return pipeline_run
    
    def _initialize_gate_policies(self) -> Dict[str, Any]:
        """Initialize security gate policies"""
        return {
            "break_build_rules": {
                "critical_findings": 0,  # Zero tolerance for critical
                "high_findings": 5,
                "secrets_found": 0
            },
            "approved_base_images": [
                "python:3.11-slim",
                "python:3.11-alpine",
                "ubuntu:22.04",
                "nginx:alpine"
            ]
        }
    
    def _scan_sql_injection(self, path: str) -> List[SecurityFinding]:
        """Scan for SQL injection vulnerabilities (simulated)"""
        # In production, use Semgrep, CodeQL, etc.
        return []
    
    def _scan_xss_vulnerabilities(self, path: str) -> List[SecurityFinding]:
        """Scan for XSS vulnerabilities (simulated)"""
        return []
    
    def _scan_hardcoded_secrets(self, path: str) -> List[SecurityFinding]:
        """Scan for hardcoded secrets (simulated)"""
        return []
    
    def _scan_insecure_crypto(self, path: str) -> List[SecurityFinding]:
        """Scan for insecure cryptography (simulated)"""
        return []
    
    def _test_authentication_bypass(self, url: str) -> List[SecurityFinding]:
        """Test for authentication bypass (simulated)"""
        return []
    
    def _test_api_security(self, url: str) -> List[SecurityFinding]:
        """Test API security (simulated)"""
        return []
    
    def _test_session_management(self, url: str) -> List[SecurityFinding]:
        """Test session management (simulated)"""
        return []
    
    def _scan_vulnerable_dependencies(self, deps_file: str) -> List[SecurityFinding]:
        """Scan for vulnerable dependencies (simulated)"""
        return []
    
    def _scan_outdated_dependencies(self, deps_file: str) -> List[SecurityFinding]:
        """Scan for outdated dependencies (simulated)"""
        return []
    
    def _scan_license_violations(self, deps_file: str) -> List[SecurityFinding]:
        """Scan for license violations (simulated)"""
        return []
    
    def _detect_secret_pattern(self, path: str, pattern: str) -> bool:
        """Detect secret pattern (simulated)"""
        # In production, scan actual files
        return False
    
    def _verify_approved_base_image(self, base_image: str) -> bool:
        """Verify base image is approved"""
        return base_image in self.gate_policies["approved_base_images"]


def main():
    """Test pipeline security gates"""
    gates = PipelineSecurityGates()
    
    # Run complete security pipeline
    pipeline_run = gates.run_security_pipeline(
        pipeline_name="enterprise-scanner-build",
        commit_sha="abc123def456789",
        branch="main"
    )
    
    print(f"\nPipeline Run ID: {pipeline_run.run_id}")
    print(f"Overall Status: {pipeline_run.overall_status}")
    print(f"Duration: {(pipeline_run.completed_at - pipeline_run.started_at).total_seconds():.2f}s")
    
    print("\nGate Results:")
    for gate in pipeline_run.gate_results:
        print(f"  {gate.gate_type.value}: {gate.status.value} "
              f"({len(gate.findings)} findings, {gate.execution_time:.2f}s)")


if __name__ == "__main__":
    main()
