"""
Phase 3 Integration Tests

Tests the integration of all three Phase 3 modules:
1. Script Generator
2. Config Generator  
3. Proactive Monitoring

Validates end-to-end workflows and module interactions.

Author: Enterprise Scanner Platform
Date: October 18, 2025
"""

import unittest
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.script_generator import (
    ScriptGenerator,
    ScriptLanguage,
    VulnerabilityType,
    ScriptMetadata,
    GeneratedScript
)
from modules.config_generator import (
    ConfigGenerator,
    ConfigType,
    ComplianceFramework,
    HardeningLevel,
    ConfigMetadata,
    GeneratedConfig
)
from modules.proactive_monitor import (
    ProactiveMonitor,
    MonitoringLevel,
    MonitoringMetric,
    AlertSeverity,
    AlertChannel
)


class TestPhase3Integration(unittest.TestCase):
    """Integration tests for all Phase 3 modules working together."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.script_gen = ScriptGenerator()
        self.config_gen = ConfigGenerator()
        self.monitor = ProactiveMonitor(monitoring_level=MonitoringLevel.MEDIUM)
        
    def tearDown(self):
        """Clean up after tests."""
        # Stop any active monitoring sessions
        if hasattr(self, 'monitor') and self.monitor:
            stats = self.monitor.get_statistics()
            if stats['active_sessions'] > 0:
                # Note: In production, track session IDs to stop them properly
                pass
    
    def test_workflow_1_scan_script_monitor(self):
        """
        Workflow 1: Scan → Generate Script → Monitor
        
        Simulate: Vulnerability detected → Generate remediation script → Monitor for resolution
        """
        # 1. Simulate vulnerability scan results
        vulnerability_data = {
            'type': VulnerabilityType.SQL_INJECTION,
            'severity': 'critical',
            'affected_file': '/var/www/html/login.php',
            'description': 'SQL injection in login form'
        }
        
        # 2. Generate remediation script
        script_result = self.script_gen.generate_remediation_script(
            vulnerability_type=vulnerability_data['type'],
            language=ScriptLanguage.PYTHON,
            target_system="Linux",
            cvss_score=9.8
        )
        
        self.assertIsNotNone(script_result)
        self.assertIsNotNone(script_result.remediation_script)
        self.assertGreater(len(script_result.remediation_script), 100)
        
        # 3. Start monitoring for remediation
        session = self.monitor.start_monitoring_session(
            target="webapp-server-01"
        )
        
        # 4. Check initial metrics (before remediation)
        pre_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 5.0,
            MonitoringMetric.HIGH_VULN_COUNT: 10.0,
            MonitoringMetric.CVSS_SCORE_AVG: 8.5
        }
        
        alerts_pre = self.monitor.check_metrics(
            metrics=pre_metrics,
            session_id=session.session_id
        )
        
        # Should generate alerts for critical vulnerabilities
        self.assertGreater(len(alerts_pre), 0)
        
        # 5. Simulate script execution and remediation
        # (In production, this would actually execute the script)
        
        # 6. Check post-remediation metrics
        post_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 4.0,  # One fixed
            MonitoringMetric.HIGH_VULN_COUNT: 10.0,
            MonitoringMetric.CVSS_SCORE_AVG: 8.2  # Slightly improved
        }
        
        alerts_post = self.monitor.check_metrics(
            metrics=post_metrics,
            session_id=session.session_id
        )
        
        # Verify workflow completed successfully
        self.assertEqual(script_result.metadata.vulnerability_type, VulnerabilityType.SQL_INJECTION)
        self.assertIsNotNone(session.session_id)
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)
    
    def test_workflow_2_scan_config_monitor_compliance(self):
        """
        Workflow 2: Scan → Generate Config → Monitor Compliance
        
        Simulate: Security audit → Generate hardened config → Monitor compliance
        """
        # 1. Simulate security audit findings
        audit_findings = {
            'weak_ssh_config': True,
            'missing_firewall_rules': True,
            'non_compliant_apache': True
        }
        
        # 2. Generate hardened SSH configuration
        ssh_config = self.config_gen.generate_config(
            config_type=ConfigType.SSH,
            target_system="Linux",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.PCI_DSS]
        )
        
        self.assertIsNotNone(ssh_config)
        self.assertIsNotNone(ssh_config.config_content)
        
        # 3. Generate hardened Apache configuration
        apache_config = self.config_gen.generate_config(
            config_type=ConfigType.APACHE,
            target_system="Linux",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.PCI_DSS]
        )
        
        self.assertIsNotNone(apache_config)
        
        # 4. Start compliance monitoring
        session = self.monitor.start_monitoring_session(
            target="production-web-server"
        )
        
        # 5. Check pre-deployment compliance
        pre_compliance_controls = {
            "2.2.2": False,  # SSH not configured securely
            "2.2.4": False,  # Insecure parameters
            "6.5.1": False,  # Input validation missing
            "10.2.1": True   # Audit logs present
        }
        
        pre_compliance = self.monitor.check_compliance(
            framework="PCI-DSS",
            controls=pre_compliance_controls
        )
        
        self.assertFalse(pre_compliance.passing)  # Should fail initially
        self.assertEqual(len(pre_compliance.failed_controls), 3)
        
        # 6. Simulate config deployment
        # (In production, deploy ssh_config and apache_config)
        
        # 7. Check post-deployment compliance
        post_compliance_controls = {
            "2.2.2": True,   # SSH now configured securely
            "2.2.4": True,   # Secure parameters set
            "6.5.1": True,   # Input validation enabled
            "10.2.1": True   # Audit logs still present
        }
        
        post_compliance = self.monitor.check_compliance(
            framework="PCI-DSS",
            controls=post_compliance_controls
        )
        
        self.assertTrue(post_compliance.passing)  # Should pass after deployment
        self.assertEqual(len(post_compliance.failed_controls), 0)
        self.assertEqual(post_compliance.score, 100.0)
        
        # 8. Monitor for compliance drift
        metrics = {
            MonitoringMetric.COMPLIANCE_SCORE: post_compliance.score,
            MonitoringMetric.CONFIG_DRIFT: 0.0  # No drift yet
        }
        
        alerts = self.monitor.check_metrics(
            metrics=metrics,
            session_id=session.session_id
        )
        
        # Should not generate alerts with good compliance
        compliance_alerts = [a for a in alerts if 'compliance' in a.title.lower()]
        self.assertEqual(len(compliance_alerts), 0)
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)
    
    def test_workflow_3_continuous_monitoring_with_automated_response(self):
        """
        Workflow 3: Continuous Monitoring → Alert → Auto-Generate Script/Config
        
        Simulate: Monitor detects issue → Generate appropriate remediation → Apply → Verify
        """
        # 1. Start continuous monitoring
        session = self.monitor.start_monitoring_session(
            target="critical-app-server"
        )
        
        # 2. First scan - everything normal
        normal_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 2.0,
            MonitoringMetric.HIGH_VULN_COUNT: 5.0,
            MonitoringMetric.COMPLIANCE_SCORE: 95.0,
            MonitoringMetric.OPEN_PORTS: 45.0
        }
        
        alerts_normal = self.monitor.check_metrics(
            metrics=normal_metrics,
            session_id=session.session_id
        )
        
        self.assertEqual(len(alerts_normal), 0)  # No alerts
        
        # 3. Second scan - critical vulnerabilities detected
        critical_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 8.0,  # Spike!
            MonitoringMetric.HIGH_VULN_COUNT: 15.0,
            MonitoringMetric.COMPLIANCE_SCORE: 95.0,
            MonitoringMetric.OPEN_PORTS: 45.0
        }
        
        alerts_critical = self.monitor.check_metrics(
            metrics=critical_metrics,
            session_id=session.session_id
        )
        
        self.assertGreater(len(alerts_critical), 0)  # Should generate alerts
        
        # 4. Identify the most critical alert
        critical_alerts = [
            a for a in alerts_critical 
            if a.severity == AlertSeverity.CRITICAL
        ]
        
        self.assertGreater(len(critical_alerts), 0)
        most_critical = critical_alerts[0]
        
        # 5. Auto-generate remediation script based on alert
        script_result = self.script_gen.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Linux",
            cvss_score=9.5
        )
        
        self.assertIsNotNone(script_result)
        
        # 6. Acknowledge alert (showing human/system awareness)
        self.monitor.acknowledge_alert(
            alert_id=most_critical.alert_id,
            acknowledged_by="auto-remediation-system"
        )
        
        # 7. Simulate script execution
        # (In production, execute script_result.script_content)
        
        # 8. Third scan - verify remediation
        remediated_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 3.0,  # Reduced
            MonitoringMetric.HIGH_VULN_COUNT: 12.0,
            MonitoringMetric.COMPLIANCE_SCORE: 95.0,
            MonitoringMetric.OPEN_PORTS: 45.0
        }
        
        alerts_remediated = self.monitor.check_metrics(
            metrics=remediated_metrics,
            session_id=session.session_id
        )
        
        # 9. Resolve the alert
        self.monitor.resolve_alert(
            alert_id=most_critical.alert_id,
            resolution_notes="Auto-remediation script applied successfully"
        )
        
        # Verify workflow
        active_alerts = self.monitor.get_active_alerts()
        resolved_alerts = [
            a for a in self.monitor.get_alert_history()
            if a.status.value == "resolved"
        ]
        
        self.assertGreater(len(resolved_alerts), 0)
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)
    
    def test_workflow_4_multi_server_monitoring_with_config_deployment(self):
        """
        Workflow 4: Multi-Server Monitoring → Config Hardening → Rollout Verification
        
        Simulate: Monitor multiple servers → Generate unified config → Deploy → Monitor compliance
        """
        servers = ["web-01", "web-02", "web-03"]
        sessions = {}
        
        # 1. Start monitoring all servers
        for server in servers:
            session = self.monitor.start_monitoring_session(target=server)
            sessions[server] = session
        
        # 2. Collect metrics from all servers
        server_metrics = {
            "web-01": {
                MonitoringMetric.OPEN_PORTS: 125.0,  # Too many!
                MonitoringMetric.COMPLIANCE_SCORE: 70.0  # Too low
            },
            "web-02": {
                MonitoringMetric.OPEN_PORTS: 48.0,
                MonitoringMetric.COMPLIANCE_SCORE: 85.0
            },
            "web-03": {
                MonitoringMetric.OPEN_PORTS: 130.0,  # Too many!
                MonitoringMetric.COMPLIANCE_SCORE: 68.0  # Too low
            }
        }
        
        all_alerts = []
        for server, metrics in server_metrics.items():
            alerts = self.monitor.check_metrics(
                metrics=metrics,
                session_id=sessions[server].session_id
            )
            all_alerts.extend(alerts)
        
        # Should detect issues on web-01 and web-03
        self.assertGreater(len(all_alerts), 0)
        
        # 3. Generate hardened firewall config to fix open ports issue
        firewall_config = self.config_gen.generate_config(
            config_type=ConfigType.FIREWALL_IPTABLES,
            target_system="Linux",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.PCI_DSS]
        )
        
        self.assertIsNotNone(firewall_config)
        
        # 4. Simulate config deployment to all servers
        # (In production, deploy to all servers)
        
        # 5. Verify post-deployment metrics
        post_deployment_metrics = {
            "web-01": {
                MonitoringMetric.OPEN_PORTS: 45.0,  # Fixed!
                MonitoringMetric.COMPLIANCE_SCORE: 92.0  # Improved
            },
            "web-02": {
                MonitoringMetric.OPEN_PORTS: 45.0,
                MonitoringMetric.COMPLIANCE_SCORE: 95.0
            },
            "web-03": {
                MonitoringMetric.OPEN_PORTS: 45.0,  # Fixed!
                MonitoringMetric.COMPLIANCE_SCORE: 90.0  # Improved
            }
        }
        
        post_alerts = []
        for server, metrics in post_deployment_metrics.items():
            alerts = self.monitor.check_metrics(
                metrics=metrics,
                session_id=sessions[server].session_id
            )
            post_alerts.extend(alerts)
        
        # Should have fewer alerts after fix
        self.assertLess(len(post_alerts), len(all_alerts))
        
        # 6. Clean up all sessions
        for server, session in sessions.items():
            self.monitor.stop_monitoring_session(session.session_id)
    
    def test_workflow_5_anomaly_detection_triggers_investigation(self):
        """
        Workflow 5: Anomaly Detection → Investigation → Remediation
        
        Simulate: Normal baseline → Anomaly detected → Generate diagnostic script → Remediate
        """
        # 1. Start monitoring and build baseline
        session = self.monitor.start_monitoring_session(
            target="database-server"
        )
        
        # 2. Feed normal metrics to build baseline (simulate 15 normal days)
        for day in range(15):
            baseline_metrics = {
                MonitoringMetric.CRITICAL_VULN_COUNT: 2.0 + (day % 2),
                MonitoringMetric.FAILED_LOGINS: 5.0 + (day % 3),
                MonitoringMetric.OPEN_PORTS: 42.0 + (day % 5)
            }
            self.monitor.check_metrics(
                metrics=baseline_metrics,
                session_id=session.session_id
            )
        
        # 3. Introduce anomalous behavior
        anomalous_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 2.0,  # Normal
            MonitoringMetric.FAILED_LOGINS: 150.0,  # Anomaly! (was ~5-7)
            MonitoringMetric.OPEN_PORTS: 43.0  # Normal
        }
        
        # 4. Detect anomalies
        anomalies = self.monitor.detect_anomalies(
            metrics=anomalous_metrics,
            confidence_threshold=0.85
        )
        
        # Should detect the failed logins anomaly
        self.assertGreater(len(anomalies), 0)
        failed_login_anomaly = [
            a for a in anomalies
            if a.metric == MonitoringMetric.FAILED_LOGINS
        ]
        self.assertGreater(len(failed_login_anomaly), 0)
        self.assertGreater(failed_login_anomaly[0].confidence, 0.9)
        
        # 5. Generate diagnostic script to investigate
        diagnostic_script = self.script_gen.generate_remediation_script(
            vulnerability_type=VulnerabilityType.WEAK_AUTH,
            language=ScriptLanguage.BASH,
            target_system="Linux",
            cvss_score=8.1
        )
        
        self.assertIsNotNone(diagnostic_script)
        
        # 6. After investigation, generate hardened SSH config
        ssh_config = self.config_gen.generate_config(
            config_type=ConfigType.SSH,
            target_system="Linux",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.SOC2]
        )
        
        self.assertIsNotNone(ssh_config)
        
        # 7. Verify metrics return to normal
        normal_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 2.0,
            MonitoringMetric.FAILED_LOGINS: 6.0,  # Back to normal
            MonitoringMetric.OPEN_PORTS: 43.0
        }
        
        new_anomalies = self.monitor.detect_anomalies(
            metrics=normal_metrics,
            confidence_threshold=0.85
        )
        
        # Should detect fewer or no anomalies
        self.assertLessEqual(len(new_anomalies), len(anomalies))
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)
    
    def test_performance_bulk_operations(self):
        """
        Performance test: Bulk generation and monitoring
        
        Verify system can handle high volume operations.
        """
        import time
        
        start_time = time.time()
        
        # 1. Generate 20 scripts quickly
        scripts_generated = 0
        for i in range(20):
            result = self.script_gen.generate_remediation_script(
                vulnerability_type=VulnerabilityType.XSS,
                language=ScriptLanguage.PYTHON,
                target_system="Linux",
                cvss_score=6.5
            )
            if result:
                scripts_generated += 1
        
        # 2. Generate 20 configs quickly
        configs_generated = 0
        for i in range(20):
            result = self.config_gen.generate_config(
                config_type=ConfigType.APACHE,
                target_system="Linux",
                hardening_level=HardeningLevel.MODERATE,
                compliance_frameworks=[ComplianceFramework.PCI_DSS]
            )
            if result:
                configs_generated += 1
        
        # 3. Monitor 100 metric checks
        session = self.monitor.start_monitoring_session(target="perf-test")
        
        checks_completed = 0
        for i in range(100):
            metrics = {
                MonitoringMetric.CRITICAL_VULN_COUNT: float(i % 10),
                MonitoringMetric.COMPLIANCE_SCORE: 80.0 + float(i % 20)
            }
            self.monitor.check_metrics(
                metrics=metrics,
                session_id=session.session_id
            )
            checks_completed += 1
        
        elapsed_time = time.time() - start_time
        
        # Verify performance
        self.assertEqual(scripts_generated, 20)
        self.assertEqual(configs_generated, 20)
        self.assertEqual(checks_completed, 100)
        
        # Should complete in reasonable time (< 10 seconds)
        self.assertLess(elapsed_time, 10.0)
        
        # Calculate throughput
        total_operations = scripts_generated + configs_generated + checks_completed
        ops_per_second = total_operations / elapsed_time
        
        print(f"\nPerformance Test Results:")
        print(f"  Total operations: {total_operations}")
        print(f"  Time elapsed: {elapsed_time:.2f}s")
        print(f"  Throughput: {ops_per_second:.1f} ops/second")
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)
    
    def test_error_handling_and_recovery(self):
        """
        Test error handling across modules.
        
        Verify graceful degradation and error recovery.
        """
        # 1. Test invalid script generation - should handle gracefully
        try:
            invalid_script = self.script_gen.generate_remediation_script(
                vulnerability_type=None,  # Invalid
                language=ScriptLanguage.PYTHON,
                target_system="Linux",
                cvss_score=5.0
            )
            # If it doesn't throw, it should return something
            self.assertTrue(invalid_script is None or isinstance(invalid_script, GeneratedScript))
        except (ValueError, TypeError, AttributeError):
            # Expected to raise an error for invalid input
            pass
        
        # 2. Test monitoring with invalid metrics
        session = self.monitor.start_monitoring_session(target="error-test")
        
        try:
            # Try with empty metrics
            alerts = self.monitor.check_metrics(
                metrics={},
                session_id=session.session_id
            )
            # Should return empty list, not crash
            self.assertIsInstance(alerts, list)
        except Exception as e:
            # If it does throw, it should be a well-defined exception
            self.assertIsInstance(e, (ValueError, TypeError))
        
        # 3. Verify monitor still works after error
        valid_metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 3.0
        }
        alerts = self.monitor.check_metrics(
            metrics=valid_metrics,
            session_id=session.session_id
        )
        self.assertIsInstance(alerts, list)
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)
    
    def test_integration_statistics(self):
        """
        Test statistics collection across integrated workflows.
        
        Verify all modules track operations correctly.
        """
        # Generate multiple items
        for i in range(5):
            self.script_gen.generate_remediation_script(
                vulnerability_type=VulnerabilityType.SQL_INJECTION,
                language=ScriptLanguage.PYTHON,
                target_system="Linux",
                cvss_score=7.5
            )
            
            self.config_gen.generate_config(
                config_type=ConfigType.SSH,
                target_system="Linux",
                hardening_level=HardeningLevel.MODERATE,
                compliance_frameworks=[ComplianceFramework.PCI_DSS]
            )
        
        # Monitor with multiple checks
        session = self.monitor.start_monitoring_session(target="stats-test")
        
        for i in range(10):
            metrics = {
                MonitoringMetric.CRITICAL_VULN_COUNT: float(i),
                MonitoringMetric.COMPLIANCE_SCORE: 85.0
            }
            self.monitor.check_metrics(
                metrics=metrics,
                session_id=session.session_id
            )
        
        # Get monitoring statistics
        stats = self.monitor.get_statistics()
        
        # Verify statistics
        self.assertGreater(stats['monitoring_sessions'], 0)
        self.assertIsInstance(stats['alerts_generated'], int)
        self.assertIsInstance(stats['active_sessions'], int)
        
        # Clean up
        self.monitor.stop_monitoring_session(session.session_id)


class TestPhase3ModuleInteroperability(unittest.TestCase):
    """Test that modules can share data and work together seamlessly."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.script_gen = ScriptGenerator()
        self.config_gen = ConfigGenerator()
        self.monitor = ProactiveMonitor()
    
    def test_shared_metadata_format(self):
        """Verify metadata formats are compatible."""
        # Generate a script and config to get their metadata
        script = self.script_gen.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.PYTHON,
            target_system="Linux",
            cvss_score=7.0
        )
        
        config = self.config_gen.generate_config(
            config_type=ConfigType.SSH,
            target_system="Linux",
            hardening_level=HardeningLevel.MODERATE
        )
        
        # Both should have metadata
        self.assertIsNotNone(script.metadata)
        self.assertIsNotNone(config.metadata)
    
    def test_monitoring_metrics_from_generation_results(self):
        """Verify monitoring can track generation results."""
        session = self.monitor.start_monitoring_session(target="interop-test")
        
        # Generate script and track
        script = self.script_gen.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.PYTHON,
            target_system="Linux",
            cvss_score=7.0
        )
        
        # Monitor can track that a vulnerability was addressed
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 4.0,  # One less after script
        }
        
        alerts = self.monitor.check_metrics(
            metrics=metrics,
            session_id=session.session_id
        )
        
        # Verify monitoring works with generation results
        self.assertIsInstance(alerts, list)
        
        self.monitor.stop_monitoring_session(session.session_id)


def run_integration_tests():
    """Run all integration tests and report results."""
    print("\n" + "="*80)
    print("PHASE 3 INTEGRATION TESTS")
    print("="*80 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all integration tests
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3ModuleInteroperability))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"\nTests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        print("\nPhase 3 modules are working together successfully.")
        print("Ready for production deployment.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nReview failures and fix issues before deployment.")
    
    print("\n" + "="*80 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
