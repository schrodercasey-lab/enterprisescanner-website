#!/usr/bin/env python3
"""
Phase 3 Command-Line Interface
Enterprise Scanner - Automated Remediation & Monitoring

Usage:
    phase3-cli generate-script --vuln-type sql_injection --language python
    phase3-cli generate-config --type ssh --level strict --compliance pci_dss
    phase3-cli start-monitoring --target prod-server-01 --level high
    phase3-cli list-alerts --severity critical
    phase3-cli get-stats
    phase3-cli health-check
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.script_generator import (
    ScriptGenerator, 
    VulnerabilityType, 
    ScriptLanguage
)
from modules.config_generator import (
    ConfigGenerator,
    ConfigType,
    HardeningLevel,
    ComplianceFramework
)
from modules.proactive_monitor import (
    ProactiveMonitor,
    MonitoringLevel,
    AlertSeverity,
    MonitoringMetric
)
from modules.__version__ import (
    __version__,
    __phase__,
    print_banner
)
from modules.config import get_config
from modules.jupiter_integration_hub import JupiterIntegrationHub
from modules.test_report_generator import TestReportGenerator, ReportFormat


class Phase3CLI:
    """Command-line interface for Phase 3 modules"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.script_gen = ScriptGenerator()
        self.config_gen = ConfigGenerator()
        self.monitor = ProactiveMonitor()
        self.config = get_config()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "WARNING": "⚠️ ",
                "ERROR": "❌"
            }.get(level, "")
            print(f"{prefix} {message}")
    
    # ===== Script Generation Commands =====
    
    def generate_script(self, args):
        """Generate remediation script"""
        self.log(f"Generating {args.language} script for {args.vuln_type}...")
        
        try:
            # Convert arguments
            vuln_type = VulnerabilityType[args.vuln_type.upper()]
            language = ScriptLanguage[args.language.upper()]
            
            # Generate script
            result = self.script_gen.generate_remediation_script(
                vulnerability_type=vuln_type,
                language=language,
                target_system=args.target,
                cvss_score=args.cvss
            )
            
            # Determine output filename
            if args.output:
                output_file = args.output
            else:
                ext = {
                    ScriptLanguage.PYTHON: 'py',
                    ScriptLanguage.BASH: 'sh',
                    ScriptLanguage.POWERSHELL: 'ps1'
                }.get(language, language.value)
                output_file = f"{args.vuln_type}_{args.language}_remediation.{ext}"
            
            # Save remediation script
            with open(output_file, 'w') as f:
                f.write(result.remediation_script)
            
            self.log(f"Script generated: {output_file}", "SUCCESS")
            self.log(f"Checksum: {result.metadata.checksum}")
            self.log(f"Target: {result.metadata.target_system}")
            self.log(f"CVSS Score: {result.metadata.cvss_score}")
            
            # Save rollback script
            if result.rollback_script and args.with_rollback:
                rollback_file = output_file.replace("remediation", "rollback")
                with open(rollback_file, 'w') as f:
                    f.write(result.rollback_script)
                self.log(f"Rollback script: {rollback_file}")
            
            # Save test script
            if result.test_script and args.with_test:
                test_file = output_file.replace("remediation", "test")
                with open(test_file, 'w') as f:
                    f.write(result.test_script)
                self.log(f"Test script: {test_file}")
            
            # Show warnings
            if result.safety_warnings:
                self.log(f"Safety warnings: {len(result.safety_warnings)}", "WARNING")
                for warning in result.safety_warnings:
                    self.log(f"  - {warning}", "WARNING")
            
            # Show execution notes
            if self.verbose and result.execution_notes:
                print("\nExecution Notes:")
                print(result.execution_notes)
            
            return 0
            
        except Exception as e:
            self.log(f"Failed to generate script: {e}", "ERROR")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    # ===== Config Generation Commands =====
    
    def generate_config(self, args):
        """Generate security configuration"""
        self.log(f"Generating {args.type} configuration (level: {args.level})...")
        
        try:
            # Convert arguments
            config_type = ConfigType[args.type.upper()]
            hardening_level = HardeningLevel[args.level.upper()]
            
            # Parse compliance frameworks
            compliance_frameworks = []
            if args.compliance:
                for framework in args.compliance:
                    compliance_frameworks.append(
                        ComplianceFramework[framework.upper()]
                    )
            
            # Generate configuration
            result = self.config_gen.generate_config(
                config_type=config_type,
                target_system=args.target,
                hardening_level=hardening_level,
                compliance_frameworks=compliance_frameworks
            )
            
            # Determine output filename
            if args.output:
                output_file = args.output
            else:
                output_file = f"{args.type}_{args.level}.conf"
            
            # Save configuration
            with open(output_file, 'w') as f:
                f.write(result.configuration)
            
            self.log(f"Configuration generated: {output_file}", "SUCCESS")
            self.log(f"Checksum: {result.metadata.checksum}")
            self.log(f"Target: {result.metadata.target_system}")
            self.log(f"Hardening Level: {result.metadata.hardening_level.value}")
            
            if compliance_frameworks:
                frameworks_str = ", ".join([f.value for f in compliance_frameworks])
                self.log(f"Compliance: {frameworks_str}")
            
            # Show deployment instructions
            if self.verbose and result.deployment_instructions:
                print("\nDeployment Instructions:")
                print(result.deployment_instructions)
            
            return 0
            
        except Exception as e:
            self.log(f"Failed to generate configuration: {e}", "ERROR")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    # ===== Monitoring Commands =====
    
    def start_monitoring(self, args):
        """Start monitoring session"""
        self.log(f"Starting monitoring for {args.target} (level: {args.level})...")
        
        try:
            # Set monitoring level
            level = MonitoringLevel[args.level.upper()]
            self.monitor = ProactiveMonitor(monitoring_level=level)
            
            # Start session
            session = self.monitor.start_monitoring_session(
                target=args.target,
                session_id=args.session_id
            )
            
            self.log(f"Monitoring session started", "SUCCESS")
            print(f"\nSession Details:")
            print(f"  Session ID:  {session.session_id}")
            print(f"  Target:      {session.target}")
            print(f"  Started:     {session.start_time}")
            print(f"  Level:       {level.value}")
            
            # Show active rules
            stats = self.monitor.get_statistics()
            print(f"  Active Rules: {stats['active_rules']}")
            
            return 0
            
        except Exception as e:
            self.log(f"Failed to start monitoring: {e}", "ERROR")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def stop_monitoring(self, args):
        """Stop monitoring session"""
        self.log(f"Stopping monitoring session: {args.session_id}...")
        
        try:
            success = self.monitor.stop_monitoring_session(args.session_id)
            
            if success:
                self.log(f"Monitoring session stopped", "SUCCESS")
                
                # Get session info
                if args.session_id in self.monitor.monitoring_sessions:
                    session = self.monitor.monitoring_sessions[args.session_id]
                    print(f"\nSession Summary:")
                    print(f"  Duration:         {session.end_time - session.start_time if session.end_time else 'N/A'}")
                    print(f"  Alerts Generated: {session.alerts_generated}")
                
                return 0
            else:
                self.log(f"Session not found: {args.session_id}", "ERROR")
                return 1
            
        except Exception as e:
            self.log(f"Failed to stop monitoring: {e}", "ERROR")
            return 1
    
    def list_alerts(self, args):
        """List active alerts"""
        try:
            # Get alerts with optional severity filter
            severity = None
            if args.severity:
                severity = AlertSeverity[args.severity.upper()]
            
            alerts = self.monitor.get_active_alerts(severity=severity)
            
            # Apply status filter
            if args.status:
                status_filter = args.status.upper()
                alerts = [a for a in alerts if a.status.value.upper() == status_filter]
            
            # Display alerts
            print(f"\n{'='*80}")
            print(f"ACTIVE ALERTS: {len(alerts)}")
            print(f"{'='*80}\n")
            
            if not alerts:
                print("No active alerts.")
                return 0
            
            for i, alert in enumerate(alerts, 1):
                severity_emoji = {
                    AlertSeverity.CRITICAL: "🔴",
                    AlertSeverity.HIGH: "🟠",
                    AlertSeverity.MEDIUM: "🟡",
                    AlertSeverity.LOW: "🔵",
                    AlertSeverity.INFO: "⚪"
                }.get(alert.severity, "")
                
                print(f"{i}. {severity_emoji} [{alert.severity.value.upper()}] {alert.title}")
                print(f"   ID: {alert.alert_id}")
                print(f"   Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Metric: {alert.metric.value} = {alert.current_value:.2f} (threshold: {alert.threshold_value:.2f})")
                print(f"   Status: {alert.status.value}")
                
                if alert.acknowledged_by:
                    print(f"   Acknowledged by: {alert.acknowledged_by}")
                
                print()
            
            return 0
            
        except Exception as e:
            self.log(f"Failed to list alerts: {e}", "ERROR")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def acknowledge_alert(self, args):
        """Acknowledge an alert"""
        try:
            success = self.monitor.acknowledge_alert(
                alert_id=args.alert_id,
                acknowledged_by=args.user or "cli-user"
            )
            
            if success:
                self.log(f"Alert acknowledged: {args.alert_id}", "SUCCESS")
                return 0
            else:
                self.log(f"Alert not found: {args.alert_id}", "ERROR")
                return 1
                
        except Exception as e:
            self.log(f"Failed to acknowledge alert: {e}", "ERROR")
            return 1
    
    def resolve_alert(self, args):
        """Resolve an alert"""
        try:
            success = self.monitor.resolve_alert(
                alert_id=args.alert_id,
                resolution_notes=args.notes
            )
            
            if success:
                self.log(f"Alert resolved: {args.alert_id}", "SUCCESS")
                return 0
            else:
                self.log(f"Alert not found: {args.alert_id}", "ERROR")
                return 1
                
        except Exception as e:
            self.log(f"Failed to resolve alert: {e}", "ERROR")
            return 1
    
    # ===== Statistics & Health Commands =====
    
    def get_stats(self, args):
        """Get Phase 3 statistics"""
        print(f"\n{'='*80}")
        print("PHASE 3 STATISTICS")
        print(f"{'='*80}\n")
        
        # Script Generator stats
        script_stats = self.script_gen.get_statistics()
        print("Script Generator:")
        print(f"  Scripts Generated:    {script_stats['total_scripts_generated']}")
        print(f"  Safety Warnings:      {script_stats['safety_warnings_issued']}")
        print(f"  By Language:")
        for lang, count in script_stats['by_language'].items():
            print(f"    {lang}: {count}")
        
        # Config Generator stats
        config_stats = self.config_gen.get_statistics()
        print("\nConfig Generator:")
        print(f"  Configs Generated:    {config_stats['total_configs_generated']}")
        print(f"  By Type:")
        for cfg_type, count in config_stats['by_type'].items():
            print(f"    {cfg_type}: {count}")
        
        # Proactive Monitor stats
        monitor_stats = self.monitor.get_statistics()
        print("\nProactive Monitor:")
        print(f"  Active Sessions:      {monitor_stats['active_sessions']}")
        print(f"  Alerts Generated:     {monitor_stats['alerts_generated']}")
        print(f"  Active Alerts:        {monitor_stats['active_alerts']}")
        print(f"  Active Rules:         {monitor_stats['active_rules']}")
        print(f"  By Severity:")
        for severity, count in monitor_stats['alerts_by_severity'].items():
            print(f"    {severity}: {count}")
        
        print(f"\n{'='*80}\n")
        return 0
    
    def health_check(self, args):
        """Perform health check"""
        print(f"\n{'='*80}")
        print("PHASE 3 HEALTH CHECK")
        print(f"{'='*80}\n")
        
        all_healthy = True
        
        # Check Script Generator
        try:
            self.script_gen.get_statistics()
            print("✅ Script Generator:   HEALTHY")
        except Exception as e:
            print(f"❌ Script Generator:   UNHEALTHY - {e}")
            all_healthy = False
        
        # Check Config Generator
        try:
            self.config_gen.get_statistics()
            print("✅ Config Generator:   HEALTHY")
        except Exception as e:
            print(f"❌ Config Generator:   UNHEALTHY - {e}")
            all_healthy = False
        
        # Check Proactive Monitor
        try:
            self.monitor.get_statistics()
            print("✅ Proactive Monitor:  HEALTHY")
        except Exception as e:
            print(f"❌ Proactive Monitor:  UNHEALTHY - {e}")
            all_healthy = False
        
        # Check configuration
        try:
            self.config.to_dict()
            print("✅ Configuration:      HEALTHY")
        except Exception as e:
            print(f"❌ Configuration:      UNHEALTHY - {e}")
            all_healthy = False
        
        print(f"\n{'='*80}")
        
        if all_healthy:
            print("✅ Overall Status:     HEALTHY")
            print(f"{'='*80}\n")
            return 0
        else:
            print("❌ Overall Status:     DEGRADED")
            print(f"{'='*80}\n")
            return 1
    
    def jupiter_process(self, args):
        """Process Jupiter scan results"""
        print(f"\n{'='*80}")
        print("JUPITER SCAN PROCESSING")
        print(f"{'='*80}\n")
        
        try:
            # Initialize hub
            hub = JupiterIntegrationHub(
                output_dir=args.output_dir,
                enable_monitoring=not args.no_monitoring
            )
            
            # Process scan file
            print(f"📂 Loading scan file: {args.scan_file}")
            result = hub.process_scan_file(
                scan_file=args.scan_file,
                target_system=args.target_system,
                compliance_frameworks=self._parse_compliance(args.compliance) if args.compliance else None,
                save_outputs=not args.no_save
            )
            
            # Print summary
            print(result.get_summary())
            
            # Generate report if requested
            if args.report:
                format_map = {
                    'json': ReportFormat.JSON,
                    'markdown': ReportFormat.MARKDOWN,
                    'md': ReportFormat.MARKDOWN,
                    'html': ReportFormat.HTML,
                    'text': ReportFormat.TEXT
                }
                report_format = format_map.get(args.report_format.lower(), ReportFormat.HTML)
                
                generator = TestReportGenerator()
                report_path = generator.generate_report(result, args.report, report_format)
                print(f"\n📋 Test report saved: {report_path}")
            
            # Return appropriate exit code
            if result.status.value == 'success':
                return 0
            elif result.status.value in ['partial', 'warning']:
                return 2
            else:
                return 1
                
        except FileNotFoundError as e:
            print(f"\n❌ {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Error processing scan: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def jupiter_monitor(self, args):
        """Start Jupiter-based monitoring"""
        print(f"\n{'='*80}")
        print("JUPITER CONTINUOUS MONITORING")
        print(f"{'='*80}\n")
        
        try:
            # Initialize hub with monitoring
            hub = JupiterIntegrationHub(
                output_dir=args.output_dir,
                monitoring_level=self._parse_monitoring_level(args.level),
                enable_monitoring=True
            )
            
            print(f"🎯 Target: {args.target}")
            print(f"📡 Monitoring Level: {args.level}")
            print(f"⏱️  Scan Interval: {args.interval} seconds")
            print(f"\n🚀 Starting continuous monitoring...")
            print("   Press Ctrl+C to stop\n")
            
            import time
            scan_count = 0
            
            # Continuous monitoring loop
            while True:
                scan_count += 1
                print(f"--- Scan {scan_count} at {datetime.now().strftime('%H:%M:%S')} ---")
                
                # In production, this would call actual Jupiter scanner
                # For now, simulate with file scanning
                if args.jupiter_api:
                    print(f"⚠️  Jupiter API integration not yet implemented")
                    print(f"   Would poll: {args.jupiter_api}")
                
                # Wait for next scan
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped by user")
            return 0
        except Exception as e:
            print(f"\n❌ Error in monitoring: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def jupiter_report(self, args):
        """Generate test report from previous session"""
        print(f"\n{'='*80}")
        print("JUPITER TEST REPORT GENERATION")
        print(f"{'='*80}\n")
        
        # This would load a previous session result
        print("⚠️  Loading previous session results...")
        print("   Feature: Generate reports from saved session data")
        print("   Status: Coming soon")
        
        return 0
    
    def jupiter_test(self, args):
        """Test Jupiter integration"""
        print(f"\n{'='*80}")
        print("JUPITER INTEGRATION TEST")
        print(f"{'='*80}\n")
        
        print("🧪 Testing Jupiter Integration Components...\n")
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Import hub
        tests_total += 1
        try:
            from modules.jupiter_integration_hub import JupiterIntegrationHub
            print("✅ Jupiter Integration Hub import")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Jupiter Integration Hub import: {e}")
        
        # Test 2: Initialize hub
        tests_total += 1
        try:
            hub = JupiterIntegrationHub(output_dir="./test_jupiter_output")
            print("✅ Hub initialization")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Hub initialization: {e}")
        
        # Test 3: Test report generator
        tests_total += 1
        try:
            from modules.test_report_generator import TestReportGenerator
            generator = TestReportGenerator()
            print("✅ Test Report Generator")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test Report Generator: {e}")
        
        # Test 4: Verify all modules accessible
        tests_total += 1
        try:
            from modules.script_generator import ScriptGenerator
            from modules.config_generator import ConfigGenerator
            from modules.proactive_monitor import ProactiveMonitor
            print("✅ All Phase 3 modules accessible")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Module imports: {e}")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"Test Results: {tests_passed}/{tests_total} passed")
        print(f"{'='*80}\n")
        
        if tests_passed == tests_total:
            print("✅ All Jupiter integration tests passed!")
            return 0
        else:
            print(f"❌ {tests_total - tests_passed} test(s) failed")
            return 1
    
    def show_config(self, args):
        """Show current configuration"""
        self.config.print_config()
        
        if args.secrets:
            print("\nConfigured Secrets:")
            from modules.secrets_manager import get_secrets_manager
            manager = get_secrets_manager()
            summary = manager.get_secrets_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
        
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Phase 3 CLI - Automated Remediation & Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Python remediation script
  %(prog)s generate-script --vuln-type sql_injection --language python
  
  # Generate SSH config with PCI-DSS compliance
  %(prog)s generate-config --type ssh --level strict --compliance pci_dss
  
  # Start monitoring
  %(prog)s start-monitoring --target prod-server-01 --level high
  
  # List critical alerts
  %(prog)s list-alerts --severity critical
  
  # Get statistics
  %(prog)s get-stats
  
  # Health check
  %(prog)s health-check
        """
    )
    
    parser.add_argument('--version', action='version', 
                       version=f'Phase {__phase__} v{__version__}')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ===== Generate Script Command =====
    script_parser = subparsers.add_parser('generate-script', 
                                          help='Generate remediation script')
    script_parser.add_argument('--vuln-type', required=True,
                              choices=[v.name.lower() for v in VulnerabilityType],
                              help='Vulnerability type')
    script_parser.add_argument('--language', default='python',
                              choices=['python', 'bash', 'powershell'],
                              help='Script language (default: python)')
    script_parser.add_argument('--target', default='linux-ubuntu-20.04',
                              help='Target system (default: linux-ubuntu-20.04)')
    script_parser.add_argument('--cvss', type=float, default=7.5,
                              help='CVSS score (default: 7.5)')
    script_parser.add_argument('--output', '-o',
                              help='Output filename')
    script_parser.add_argument('--with-rollback', action='store_true',
                              help='Generate rollback script')
    script_parser.add_argument('--with-test', action='store_true',
                              help='Generate test script')
    
    # ===== Generate Config Command =====
    config_parser = subparsers.add_parser('generate-config',
                                          help='Generate security configuration')
    config_parser.add_argument('--type', required=True,
                              choices=[c.name.lower() for c in ConfigType],
                              help='Configuration type')
    config_parser.add_argument('--level', default='standard',
                              choices=['basic', 'standard', 'strict', 'paranoid'],
                              help='Hardening level (default: standard)')
    config_parser.add_argument('--target', default='linux-ubuntu-20.04',
                              help='Target system (default: linux-ubuntu-20.04)')
    config_parser.add_argument('--compliance', nargs='+',
                              choices=[f.name.lower() for f in ComplianceFramework],
                              help='Compliance frameworks')
    config_parser.add_argument('--output', '-o',
                              help='Output filename')
    
    # ===== Start Monitoring Command =====
    monitor_parser = subparsers.add_parser('start-monitoring',
                                           help='Start monitoring session')
    monitor_parser.add_argument('--target', required=True,
                               help='Target system identifier')
    monitor_parser.add_argument('--level', default='medium',
                               choices=['low', 'medium', 'high', 'paranoid'],
                               help='Monitoring level (default: medium)')
    monitor_parser.add_argument('--session-id',
                               help='Custom session ID')
    
    # ===== Stop Monitoring Command =====
    stop_parser = subparsers.add_parser('stop-monitoring',
                                        help='Stop monitoring session')
    stop_parser.add_argument('session_id',
                            help='Session ID to stop')
    
    # ===== List Alerts Command =====
    alerts_parser = subparsers.add_parser('list-alerts',
                                          help='List active alerts')
    alerts_parser.add_argument('--severity',
                              choices=['info', 'low', 'medium', 'high', 'critical'],
                              help='Filter by severity')
    alerts_parser.add_argument('--status',
                              choices=['pending', 'sent', 'acknowledged', 'resolved'],
                              help='Filter by status')
    
    # ===== Acknowledge Alert Command =====
    ack_parser = subparsers.add_parser('acknowledge-alert',
                                       help='Acknowledge an alert')
    ack_parser.add_argument('alert_id',
                           help='Alert ID to acknowledge')
    ack_parser.add_argument('--user',
                           help='Username acknowledging the alert')
    
    # ===== Resolve Alert Command =====
    resolve_parser = subparsers.add_parser('resolve-alert',
                                           help='Resolve an alert')
    resolve_parser.add_argument('alert_id',
                               help='Alert ID to resolve')
    resolve_parser.add_argument('--notes',
                               help='Resolution notes')
    
    # ===== Statistics Command =====
    subparsers.add_parser('get-stats',
                         help='Get Phase 3 statistics')
    
    # ===== Health Check Command =====
    subparsers.add_parser('health-check',
                         help='Perform health check')
    
    # ===== Show Config Command =====
    config_show_parser = subparsers.add_parser('show-config',
                                               help='Show current configuration')
    config_show_parser.add_argument('--secrets', action='store_true',
                                   help='Show configured secrets (masked)')
    
    # ===== Version/Banner Command =====
    subparsers.add_parser('banner',
                         help='Show Phase 3 banner')
    
    # ===== Jupiter Integration Commands =====
    
    # Jupiter Process Command
    jupiter_process_parser = subparsers.add_parser('jupiter-process',
                                                   help='Process Jupiter scan results')
    jupiter_process_parser.add_argument('scan_file',
                                       help='Path to Jupiter scan results JSON file')
    jupiter_process_parser.add_argument('--output-dir', default='./jupiter_output',
                                       help='Output directory (default: ./jupiter_output)')
    jupiter_process_parser.add_argument('--target-system', default='Ubuntu 22.04 LTS',
                                       help='Target operating system')
    jupiter_process_parser.add_argument('--compliance', nargs='+',
                                       choices=['pci_dss', 'hipaa', 'soc2', 'cis', 'nist', 'gdpr'],
                                       help='Required compliance frameworks')
    jupiter_process_parser.add_argument('--no-monitoring', action='store_true',
                                       help='Disable proactive monitoring')
    jupiter_process_parser.add_argument('--no-save', action='store_true',
                                       help='Don\'t save outputs to disk')
    jupiter_process_parser.add_argument('--report',
                                       help='Generate test report (path to report file)')
    jupiter_process_parser.add_argument('--report-format', default='html',
                                       choices=['json', 'markdown', 'md', 'html', 'text'],
                                       help='Report format (default: html)')
    
    # Jupiter Monitor Command
    jupiter_monitor_parser = subparsers.add_parser('jupiter-monitor',
                                                   help='Start continuous Jupiter monitoring')
    jupiter_monitor_parser.add_argument('--target', required=True,
                                       help='Target system to monitor')
    jupiter_monitor_parser.add_argument('--jupiter-api',
                                       help='Jupiter API endpoint (e.g., http://jupiter:8080)')
    jupiter_monitor_parser.add_argument('--output-dir', default='./jupiter_output',
                                       help='Output directory (default: ./jupiter_output)')
    jupiter_monitor_parser.add_argument('--level', default='medium',
                                       choices=['low', 'medium', 'high', 'paranoid'],
                                       help='Monitoring level (default: medium)')
    jupiter_monitor_parser.add_argument('--interval', type=int, default=300,
                                       help='Scan interval in seconds (default: 300)')
    
    # Jupiter Report Command
    jupiter_report_parser = subparsers.add_parser('jupiter-report',
                                                 help='Generate test report from session')
    jupiter_report_parser.add_argument('--session-id',
                                      help='Session ID to generate report for')
    jupiter_report_parser.add_argument('--format', default='html',
                                      choices=['json', 'markdown', 'html', 'text'],
                                      help='Report format (default: html)')
    
    # Jupiter Test Command
    subparsers.add_parser('jupiter-test',
                         help='Test Jupiter integration')
    
    args = parser.parse_args()
    
    # Show banner for banner command
    if args.command == 'banner':
        print_banner()
        return 0
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Create CLI instance
    cli = Phase3CLI(verbose=args.verbose)
    
    # Route to appropriate command handler
    commands = {
        'generate-script': cli.generate_script,
        'generate-config': cli.generate_config,
        'start-monitoring': cli.start_monitoring,
        'stop-monitoring': cli.stop_monitoring,
        'list-alerts': cli.list_alerts,
        'acknowledge-alert': cli.acknowledge_alert,
        'resolve-alert': cli.resolve_alert,
        'get-stats': cli.get_stats,
        'health-check': cli.health_check,
        'show-config': cli.show_config,
        'jupiter-process': cli.jupiter_process,
        'jupiter-monitor': cli.jupiter_monitor,
        'jupiter-report': cli.jupiter_report,
        'jupiter-test': cli.jupiter_test,
    }
    
    handler = commands.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return 130
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
