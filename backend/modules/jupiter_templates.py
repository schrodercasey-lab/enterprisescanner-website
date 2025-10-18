#!/usr/bin/env python3
"""
Jupiter Integration Templates - Quick Start Solutions

Pre-built templates for common Jupiter integration scenarios.
Copy-paste ready with best practices built-in.

Templates:
1. Quick Integration - Process scan in 5 lines
2. Automated Remediation - Full remediation pipeline
3. Continuous Monitoring - 24/7 monitoring setup
4. Compliance Reporting - Generate compliance reports
5. CI/CD Pipeline - Integrate with automated testing

Author: Enterprise Scanner Platform
Date: October 18, 2025
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from modules.jupiter_integration_hub import JupiterIntegrationHub, IntegrationResult
from modules.test_report_generator import TestReportGenerator, ReportFormat
from modules.config_generator import ComplianceFramework
from modules.proactive_monitor import MonitoringLevel


class QuickIntegration:
    """
    Template 1: Quick Integration
    
    Process Jupiter scan results in minimal code.
    Perfect for: Quick testing, one-off scans, debugging
    
    Example:
        from modules.jupiter_templates import QuickIntegration
        
        result = QuickIntegration.process("scan.json")
        print(result.get_summary())
    """
    
    @staticmethod
    def process(
        scan_file: str,
        output_dir: str = "./jupiter_output",
        enable_monitoring: bool = True,
        generate_report: bool = True
    ) -> IntegrationResult:
        """
        Process a Jupiter scan file with one function call.
        
        Args:
            scan_file: Path to Jupiter scan JSON file
            output_dir: Output directory for results
            enable_monitoring: Enable proactive monitoring
            generate_report: Generate HTML test report
        
        Returns:
            IntegrationResult with all processing details
        """
        # Initialize hub
        hub = JupiterIntegrationHub(
            output_dir=output_dir,
            enable_monitoring=enable_monitoring
        )
        
        # Process scan
        result = hub.process_scan_file(scan_file)
        
        # Generate report if requested
        if generate_report:
            generator = TestReportGenerator()
            report_path = Path(output_dir) / "test_report.html"
            generator.generate_report(result, str(report_path), ReportFormat.HTML)
            print(f"\n📋 Test report: {report_path}")
        
        return result


class AutomatedRemediation:
    """
    Template 2: Automated Remediation Pipeline
    
    Full end-to-end remediation with all modules.
    Perfect for: Production deployments, automated workflows
    
    Example:
        from modules.jupiter_templates import AutomatedRemediation
        
        pipeline = AutomatedRemediation(
            scan_file="scan.json",
            target_system="Ubuntu 22.04 LTS",
            compliance=['pci_dss', 'hipaa']
        )
        
        result = pipeline.run()
        pipeline.generate_deployment_plan()
    """
    
    def __init__(
        self,
        scan_file: str,
        target_system: str = "Ubuntu 22.04 LTS",
        compliance: Optional[List[str]] = None,
        output_dir: str = "./remediation_pipeline"
    ):
        """
        Initialize automated remediation pipeline.
        
        Args:
            scan_file: Path to Jupiter scan file
            target_system: Target operating system
            compliance: Compliance frameworks (pci_dss, hipaa, soc2, etc.)
            output_dir: Output directory
        """
        self.scan_file = scan_file
        self.target_system = target_system
        self.compliance = self._parse_compliance(compliance) if compliance else None
        self.output_dir = Path(output_dir)
        self.result = None
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
        (self.output_dir / "configs").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "deployment").mkdir(exist_ok=True)
    
    def run(self) -> IntegrationResult:
        """
        Run the full remediation pipeline.
        
        Returns:
            IntegrationResult with all details
        """
        print("\n" + "="*80)
        print("AUTOMATED REMEDIATION PIPELINE")
        print("="*80 + "\n")
        
        # Step 1: Process scan
        print("Step 1: Processing Jupiter scan...")
        hub = JupiterIntegrationHub(
            output_dir=str(self.output_dir),
            enable_monitoring=True
        )
        
        self.result = hub.process_scan_file(
            scan_file=self.scan_file,
            target_system=self.target_system,
            compliance_frameworks=self.compliance
        )
        
        print(f"✅ Processed {self.result.metrics.total_vulnerabilities} vulnerabilities")
        
        # Step 2: Generate reports
        print("\nStep 2: Generating test reports...")
        self._generate_reports()
        print("✅ Reports generated")
        
        # Step 3: Create deployment plan
        print("\nStep 3: Creating deployment plan...")
        self.generate_deployment_plan()
        print("✅ Deployment plan created")
        
        # Step 4: Summary
        print("\n" + "="*80)
        print("PIPELINE COMPLETE")
        print("="*80)
        print(self.result.get_summary())
        
        return self.result
    
    def _generate_reports(self):
        """Generate all report formats"""
        generator = TestReportGenerator()
        
        formats = [
            (ReportFormat.HTML, "test_report.html"),
            (ReportFormat.MARKDOWN, "test_report.md"),
            (ReportFormat.JSON, "test_report.json")
        ]
        
        for format_type, filename in formats:
            report_path = self.output_dir / "reports" / filename
            generator.generate_report(self.result, str(report_path), format_type)
            print(f"   📋 {filename}")
    
    def generate_deployment_plan(self):
        """Generate deployment plan document"""
        plan_path = self.output_dir / "deployment" / "DEPLOYMENT_PLAN.md"
        
        plan = []
        plan.append("# Automated Remediation Deployment Plan")
        plan.append(f"\n**Generated:** {self.result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        plan.append(f"**Target:** {self.result.scan_data.get('target')}")
        plan.append(f"**Vulnerabilities:** {self.result.metrics.total_vulnerabilities}")
        plan.append("")
        
        plan.append("## Pre-Deployment Checklist")
        plan.append("")
        plan.append("- [ ] Review all generated scripts and configurations")
        plan.append("- [ ] Test in development environment")
        plan.append("- [ ] Schedule maintenance window")
        plan.append("- [ ] Notify stakeholders")
        plan.append("- [ ] Verify backup systems")
        plan.append("")
        
        plan.append("## Deployment Steps")
        plan.append("")
        
        # Scripts
        if self.result.remediation_scripts:
            plan.append(f"### 1. Apply Remediation Scripts ({len(self.result.remediation_scripts)} scripts)")
            plan.append("")
            plan.append("```bash")
            plan.append(f"cd {self.output_dir}/scripts")
            plan.append("# Review each script before execution")
            plan.append("# Execute remediation scripts")
            plan.append("# Verify with test scripts")
            plan.append("```")
            plan.append("")
        
        # Configs
        if self.result.security_configs:
            plan.append(f"### 2. Apply Security Configurations ({len(self.result.security_configs)} configs)")
            plan.append("")
            plan.append("```bash")
            plan.append(f"cd {self.output_dir}/configs")
            plan.append("# Backup current configurations")
            plan.append("# Apply new configurations")
            plan.append("# Test configurations")
            plan.append("```")
            plan.append("")
        
        # Monitoring
        if self.result.monitoring_session:
            plan.append("### 3. Verify Monitoring")
            plan.append("")
            plan.append(f"Session ID: `{self.result.monitoring_session.session_id}`")
            plan.append("")
            plan.append("```bash")
            plan.append("phase3-cli list-alerts")
            plan.append("```")
            plan.append("")
        
        plan.append("## Post-Deployment")
        plan.append("")
        plan.append("- [ ] Verify all services running")
        plan.append("- [ ] Monitor logs for 24 hours")
        plan.append("- [ ] Run follow-up vulnerability scan")
        plan.append("- [ ] Document any issues")
        plan.append("")
        
        plan_path.write_text("\n".join(plan), encoding='utf-8')
        print(f"   📋 {plan_path}")
    
    def _parse_compliance(self, compliance_list: List[str]) -> List[ComplianceFramework]:
        """Parse compliance framework strings"""
        framework_map = {
            'pci_dss': ComplianceFramework.PCI_DSS,
            'hipaa': ComplianceFramework.HIPAA,
            'soc2': ComplianceFramework.SOC2,
            'cis': ComplianceFramework.CIS,
            'nist': ComplianceFramework.NIST,
            'gdpr': ComplianceFramework.GDPR
        }
        return [framework_map[c.lower()] for c in compliance_list if c.lower() in framework_map]


class ContinuousMonitoring:
    """
    Template 3: Continuous Monitoring Setup
    
    Set up 24/7 continuous security monitoring.
    Perfect for: Production systems, critical infrastructure
    
    Example:
        from modules.jupiter_templates import ContinuousMonitoring
        
        monitor = ContinuousMonitoring(
            target="prod-web-01",
            level="high"
        )
        
        monitor.start()
    """
    
    def __init__(
        self,
        target: str,
        level: str = "medium",
        output_dir: str = "./monitoring"
    ):
        """
        Initialize continuous monitoring.
        
        Args:
            target: Target system identifier
            level: Monitoring level (low, medium, high, paranoid)
            output_dir: Output directory for monitoring data
        """
        self.target = target
        self.level = self._parse_monitoring_level(level)
        self.output_dir = Path(output_dir)
        self.hub = None
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start continuous monitoring"""
        print("\n" + "="*80)
        print("CONTINUOUS MONITORING SETUP")
        print("="*80 + "\n")
        
        print(f"🎯 Target: {self.target}")
        print(f"📡 Level: {self.level.value}")
        print(f"📁 Output: {self.output_dir}")
        print("")
        
        # Initialize hub
        self.hub = JupiterIntegrationHub(
            output_dir=str(self.output_dir),
            monitoring_level=self.level,
            enable_monitoring=True
        )
        
        print("✅ Monitoring system initialized")
        print("\n💡 Next steps:")
        print("   1. Integrate with Jupiter scanner")
        print("   2. Configure alert channels")
        print("   3. Set up dashboards")
        print("   4. Test alerting workflows")
        print("")
    
    def _parse_monitoring_level(self, level: str) -> MonitoringLevel:
        """Parse monitoring level string"""
        level_map = {
            'low': MonitoringLevel.LOW,
            'medium': MonitoringLevel.MEDIUM,
            'high': MonitoringLevel.HIGH,
            'paranoid': MonitoringLevel.PARANOID
        }
        return level_map.get(level.lower(), MonitoringLevel.MEDIUM)


class ComplianceReporting:
    """
    Template 4: Compliance Reporting
    
    Generate compliance-focused reports.
    Perfect for: Audits, compliance reviews, certifications
    
    Example:
        from modules.jupiter_templates import ComplianceReporting
        
        reporter = ComplianceReporting(
            scan_file="scan.json",
            frameworks=['pci_dss', 'hipaa', 'soc2']
        )
        
        reporter.generate_compliance_report()
    """
    
    def __init__(
        self,
        scan_file: str,
        frameworks: List[str],
        output_dir: str = "./compliance_reports"
    ):
        """
        Initialize compliance reporter.
        
        Args:
            scan_file: Path to Jupiter scan file
            frameworks: Compliance frameworks to report on
            output_dir: Output directory for reports
        """
        self.scan_file = scan_file
        self.frameworks = frameworks
        self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_compliance_report(self):
        """Generate compliance report"""
        print("\n" + "="*80)
        print("COMPLIANCE REPORTING")
        print("="*80 + "\n")
        
        print(f"📋 Frameworks: {', '.join([f.upper() for f in self.frameworks])}")
        print(f"📁 Output: {self.output_dir}")
        print("")
        
        # Process scan with compliance focus
        hub = JupiterIntegrationHub(output_dir=str(self.output_dir))
        
        # Parse compliance frameworks
        compliance_map = {
            'pci_dss': ComplianceFramework.PCI_DSS,
            'hipaa': ComplianceFramework.HIPAA,
            'soc2': ComplianceFramework.SOC2,
            'cis': ComplianceFramework.CIS,
            'nist': ComplianceFramework.NIST,
            'gdpr': ComplianceFramework.GDPR
        }
        compliance_frameworks = [compliance_map[f.lower()] for f in self.frameworks if f.lower() in compliance_map]
        
        result = hub.process_scan_file(
            scan_file=self.scan_file,
            compliance_frameworks=compliance_frameworks
        )
        
        # Generate compliance-focused report
        generator = TestReportGenerator()
        report_path = self.output_dir / "compliance_report.html"
        generator.generate_report(result, str(report_path), ReportFormat.HTML)
        
        print(f"✅ Compliance report generated: {report_path}")
        print("")


class CICDPipeline:
    """
    Template 5: CI/CD Pipeline Integration
    
    Integrate Jupiter scanning with CI/CD pipelines.
    Perfect for: DevSecOps, automated testing, continuous security
    
    Example:
        from modules.jupiter_templates import CICDPipeline
        
        # In your CI/CD script
        pipeline = CICDPipeline(scan_file="scan.json")
        
        if not pipeline.run():
            sys.exit(1)  # Fail the build
    """
    
    def __init__(
        self,
        scan_file: str,
        fail_on_critical: bool = True,
        fail_on_high: bool = False,
        max_vulnerabilities: Optional[int] = None
    ):
        """
        Initialize CI/CD pipeline integration.
        
        Args:
            scan_file: Path to Jupiter scan file
            fail_on_critical: Fail build if critical vulnerabilities found
            fail_on_high: Fail build if high vulnerabilities found
            max_vulnerabilities: Maximum allowed vulnerabilities (any severity)
        """
        self.scan_file = scan_file
        self.fail_on_critical = fail_on_critical
        self.fail_on_high = fail_on_high
        self.max_vulnerabilities = max_vulnerabilities
    
    def run(self) -> bool:
        """
        Run CI/CD pipeline check.
        
        Returns:
            True if build should pass, False if should fail
        """
        print("\n" + "="*80)
        print("CI/CD SECURITY GATE")
        print("="*80 + "\n")
        
        # Process scan
        hub = JupiterIntegrationHub(
            output_dir="./cicd_output",
            enable_monitoring=False  # Not needed for CI/CD
        )
        
        result = hub.process_scan_file(self.scan_file)
        
        # Check failure conditions
        should_pass = True
        
        if self.fail_on_critical and result.metrics.total_vulnerabilities > 0:
            # Check for critical vulnerabilities in scan data
            critical_count = result.scan_data.get('summary', {}).get('critical', 0)
            if critical_count > 0:
                print(f"❌ FAIL: {critical_count} critical vulnerabilities found")
                should_pass = False
        
        if self.fail_on_high and result.metrics.total_vulnerabilities > 0:
            # Check for high vulnerabilities
            high_count = result.scan_data.get('summary', {}).get('high', 0)
            if high_count > 0:
                print(f"❌ FAIL: {high_count} high vulnerabilities found")
                should_pass = False
        
        if self.max_vulnerabilities and result.metrics.total_vulnerabilities > self.max_vulnerabilities:
            print(f"❌ FAIL: {result.metrics.total_vulnerabilities} vulnerabilities exceed limit of {self.max_vulnerabilities}")
            should_pass = False
        
        # Generate report for CI/CD
        generator = TestReportGenerator()
        generator.generate_report(result, "./cicd_output/cicd_report.json", ReportFormat.JSON)
        
        if should_pass:
            print("✅ PASS: Security gate passed")
        
        print("")
        return should_pass


if __name__ == "__main__":
    print("\n" + "="*80)
    print("JUPITER INTEGRATION TEMPLATES")
    print("="*80 + "\n")
    
    print("Available Templates:")
    print("")
    print("1. QuickIntegration       - Process scan in 5 lines")
    print("2. AutomatedRemediation   - Full remediation pipeline")
    print("3. ContinuousMonitoring   - 24/7 monitoring setup")
    print("4. ComplianceReporting    - Generate compliance reports")
    print("5. CICDPipeline           - CI/CD integration")
    print("")
    
    print("Example Usage:")
    print("")
    print("from modules.jupiter_templates import QuickIntegration")
    print("")
    print('result = QuickIntegration.process("scan.json")')
    print("print(result.get_summary())")
    
    print("\n" + "="*80)
    print("Ready to use! 🚀")
    print("="*80 + "\n")
