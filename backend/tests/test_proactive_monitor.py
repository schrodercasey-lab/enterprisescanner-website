#!/usr/bin/env python3
"""
Test Suite for Proactive Monitoring Module
===========================================

Comprehensive tests for the ProactiveMonitor class.

Author: Enterprise Scanner Platform
Version: 1.0.0
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.proactive_monitor import (
    ProactiveMonitor,
    MonitoringLevel,
    AlertSeverity,
    AlertChannel,
    MonitoringMetric,
    AlertStatus,
    MonitoringThreshold,
    AlertRule,
    SecurityAlert,
    MonitoringSession,
    AnomalyDetection,
    ComplianceStatus
)


class TestProactiveMonitor(unittest.TestCase):
    """Test cases for ProactiveMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = ProactiveMonitor(monitoring_level=MonitoringLevel.MEDIUM)
    
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.monitoring_level, MonitoringLevel.MEDIUM)
        self.assertGreater(len(self.monitor.alert_rules), 0)
        self.assertEqual(len(self.monitor.active_alerts), 0)
    
    def test_default_rules_created(self):
        """Test default alert rules are created"""
        self.assertIn("RULE-001", self.monitor.alert_rules)
        self.assertIn("RULE-002", self.monitor.alert_rules)
        self.assertIn("RULE-003", self.monitor.alert_rules)
        self.assertIn("RULE-004", self.monitor.alert_rules)
        self.assertIn("RULE-005", self.monitor.alert_rules)
    
    def test_add_alert_rule(self):
        """Test adding custom alert rule"""
        rule = AlertRule(
            rule_id="CUSTOM-001",
            name="Custom Rule",
            description="Test rule",
            threshold=MonitoringThreshold(
                metric=MonitoringMetric.OPEN_PORTS,
                operator="gt",
                value=100.0,
                severity=AlertSeverity.HIGH,
                description="Too many open ports"
            ),
            channels=[AlertChannel.EMAIL]
        )
        
        result = self.monitor.add_alert_rule(rule)
        self.assertTrue(result)
        self.assertIn("CUSTOM-001", self.monitor.alert_rules)
    
    def test_remove_alert_rule(self):
        """Test removing alert rule"""
        result = self.monitor.remove_alert_rule("RULE-001")
        self.assertTrue(result)
        self.assertNotIn("RULE-001", self.monitor.alert_rules)
        
        # Try removing non-existent rule
        result = self.monitor.remove_alert_rule("NONEXISTENT")
        self.assertFalse(result)
    
    def test_start_monitoring_session(self):
        """Test starting monitoring session"""
        session = self.monitor.start_monitoring_session(target="test-server")
        
        self.assertIsNotNone(session)
        self.assertEqual(session.target, "test-server")
        self.assertEqual(session.monitoring_level, MonitoringLevel.MEDIUM)
        self.assertIn(session.session_id, self.monitor.monitoring_sessions)
    
    def test_stop_monitoring_session(self):
        """Test stopping monitoring session"""
        session = self.monitor.start_monitoring_session(target="test-server")
        session_id = session.session_id
        
        result = self.monitor.stop_monitoring_session(session_id)
        self.assertTrue(result)
        self.assertNotIn(session_id, self.monitor.monitoring_sessions)
    
    def test_check_metrics_no_alerts(self):
        """Test checking metrics that don't trigger alerts"""
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 2.0,  # Below threshold (5)
            MonitoringMetric.HIGH_VULN_COUNT: 5.0,      # Below threshold (10)
            MonitoringMetric.CVSS_SCORE_AVG: 5.0,       # Below threshold (7.5)
        }
        
        alerts = self.monitor.check_metrics(metrics)
        self.assertEqual(len(alerts), 0)
    
    def test_check_metrics_with_alerts(self):
        """Test checking metrics that trigger alerts"""
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 10.0,  # Above threshold (5)
            MonitoringMetric.HIGH_VULN_COUNT: 15.0,      # Above threshold (10)
        }
        
        alerts = self.monitor.check_metrics(metrics)
        self.assertGreater(len(alerts), 0)
        
        # Check alert details
        critical_alert = next(
            (a for a in alerts if a.metric == MonitoringMetric.CRITICAL_VULN_COUNT),
            None
        )
        self.assertIsNotNone(critical_alert)
        self.assertEqual(critical_alert.severity, AlertSeverity.CRITICAL)
        self.assertEqual(critical_alert.current_value, 10.0)
    
    def test_threshold_evaluation_greater_than(self):
        """Test threshold evaluation - greater than"""
        result = self.monitor._evaluate_threshold(10.0, "gt", 5.0)
        self.assertTrue(result)
        
        result = self.monitor._evaluate_threshold(5.0, "gt", 10.0)
        self.assertFalse(result)
    
    def test_threshold_evaluation_less_than(self):
        """Test threshold evaluation - less than"""
        result = self.monitor._evaluate_threshold(5.0, "lt", 10.0)
        self.assertTrue(result)
        
        result = self.monitor._evaluate_threshold(10.0, "lt", 5.0)
        self.assertFalse(result)
    
    def test_threshold_evaluation_equal(self):
        """Test threshold evaluation - equal"""
        result = self.monitor._evaluate_threshold(10.0, "eq", 10.0)
        self.assertTrue(result)
        
        result = self.monitor._evaluate_threshold(10.0, "eq", 5.0)
        self.assertFalse(result)
    
    def test_alert_cooldown(self):
        """Test alert cooldown prevents duplicate alerts"""
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 10.0,
        }
        
        # First check should generate alert
        alerts1 = self.monitor.check_metrics(metrics)
        self.assertGreater(len(alerts1), 0)
        
        # Second check immediately should not generate alert (cooldown)
        alerts2 = self.monitor.check_metrics(metrics)
        self.assertEqual(len(alerts2), 0)
    
    def test_acknowledge_alert(self):
        """Test acknowledging alert"""
        # Generate alert
        metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 10.0}
        alerts = self.monitor.check_metrics(metrics)
        alert_id = alerts[0].alert_id
        
        # Acknowledge it
        result = self.monitor.acknowledge_alert(alert_id, "admin")
        self.assertTrue(result)
        
        alert = self.monitor.active_alerts[alert_id]
        self.assertEqual(alert.status, AlertStatus.ACKNOWLEDGED)
        self.assertEqual(alert.acknowledged_by, "admin")
        self.assertIsNotNone(alert.acknowledged_at)
    
    def test_resolve_alert(self):
        """Test resolving alert"""
        # Generate alert
        metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 10.0}
        alerts = self.monitor.check_metrics(metrics)
        alert_id = alerts[0].alert_id
        
        # Resolve it
        result = self.monitor.resolve_alert(alert_id, "Fixed vulnerabilities")
        self.assertTrue(result)
        
        # Should be removed from active alerts
        self.assertNotIn(alert_id, self.monitor.active_alerts)
        
        # Should be in history
        historical = self.monitor.get_alert_history()
        resolved_alert = next((a for a in historical if a.alert_id == alert_id), None)
        self.assertIsNotNone(resolved_alert)
        self.assertEqual(resolved_alert.status, AlertStatus.RESOLVED)
    
    def test_get_active_alerts_no_filter(self):
        """Test getting active alerts without filtering"""
        # Generate some alerts
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 10.0,
            MonitoringMetric.HIGH_VULN_COUNT: 15.0,
        }
        self.monitor.check_metrics(metrics)
        
        active = self.monitor.get_active_alerts()
        self.assertGreater(len(active), 0)
    
    def test_get_active_alerts_filter_severity(self):
        """Test getting active alerts filtered by severity"""
        # Generate alerts
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 10.0,
            MonitoringMetric.HIGH_VULN_COUNT: 15.0,
        }
        self.monitor.check_metrics(metrics)
        
        critical_alerts = self.monitor.get_active_alerts(severity=AlertSeverity.CRITICAL)
        self.assertGreater(len(critical_alerts), 0)
        
        for alert in critical_alerts:
            self.assertEqual(alert.severity, AlertSeverity.CRITICAL)
    
    def test_get_active_alerts_filter_metric(self):
        """Test getting active alerts filtered by metric"""
        # Generate alerts
        metrics = {
            MonitoringMetric.CRITICAL_VULN_COUNT: 10.0,
            MonitoringMetric.HIGH_VULN_COUNT: 15.0,
        }
        self.monitor.check_metrics(metrics)
        
        vuln_alerts = self.monitor.get_active_alerts(
            metric=MonitoringMetric.CRITICAL_VULN_COUNT
        )
        
        for alert in vuln_alerts:
            self.assertEqual(alert.metric, MonitoringMetric.CRITICAL_VULN_COUNT)
    
    def test_get_alert_history(self):
        """Test getting alert history"""
        # Generate and resolve some alerts
        metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 10.0}
        alerts = self.monitor.check_metrics(metrics)
        alert_id = alerts[0].alert_id
        self.monitor.resolve_alert(alert_id)
        
        history = self.monitor.get_alert_history()
        self.assertGreater(len(history), 0)
    
    def test_get_alert_history_time_filter(self):
        """Test getting alert history with time filtering"""
        # Generate alert
        metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 10.0}
        self.monitor.check_metrics(metrics)
        
        # Get history from 1 hour ago
        start_time = datetime.now() - timedelta(hours=1)
        history = self.monitor.get_alert_history(start_time=start_time)
        self.assertGreater(len(history), 0)
        
        # Get history from future (should be empty)
        future_time = datetime.now() + timedelta(hours=1)
        history = self.monitor.get_alert_history(start_time=future_time)
        self.assertEqual(len(history), 0)
    
    def test_detect_anomalies_insufficient_data(self):
        """Test anomaly detection with insufficient historical data"""
        metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 5.0}
        
        anomalies = self.monitor.detect_anomalies(metrics)
        self.assertEqual(len(anomalies), 0)  # Need at least 10 data points
    
    def test_detect_anomalies_with_history(self):
        """Test anomaly detection with sufficient historical data"""
        # Build up history with normal values
        for i in range(15):
            metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 5.0 + (i % 3)}
            self.monitor.check_metrics(metrics)
        
        # Now check with anomalous value
        anomalous_metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 50.0}
        anomalies = self.monitor.detect_anomalies(anomalous_metrics)
        
        # Should detect anomaly
        self.assertGreater(len(anomalies), 0)
        anomaly = anomalies[0]
        self.assertEqual(anomaly.metric, MonitoringMetric.CRITICAL_VULN_COUNT)
        self.assertTrue(anomaly.is_anomaly)
        self.assertGreater(anomaly.confidence, 0.8)
    
    def test_check_compliance_passing(self):
        """Test compliance check - passing"""
        controls = {
            "CTRL-001": True,
            "CTRL-002": True,
            "CTRL-003": True,
            "CTRL-004": True,
        }
        
        status = self.monitor.check_compliance("PCI-DSS", controls)
        
        self.assertEqual(status.framework, "PCI-DSS")
        self.assertEqual(status.score, 100.0)
        self.assertTrue(status.passing)
        self.assertEqual(len(status.failed_controls), 0)
    
    def test_check_compliance_failing(self):
        """Test compliance check - failing"""
        controls = {
            "CTRL-001": True,
            "CTRL-002": False,
            "CTRL-003": False,
            "CTRL-004": True,
        }
        
        status = self.monitor.check_compliance("HIPAA", controls)
        
        self.assertEqual(status.framework, "HIPAA")
        self.assertEqual(status.score, 50.0)
        self.assertFalse(status.passing)
        self.assertEqual(len(status.failed_controls), 2)
        self.assertIn("CTRL-002", status.failed_controls)
        self.assertIn("CTRL-003", status.failed_controls)
    
    def test_get_metric_trends_no_data(self):
        """Test getting metric trends with no data"""
        trends = self.monitor.get_metric_trends(
            MonitoringMetric.CRITICAL_VULN_COUNT,
            time_window_minutes=60
        )
        
        self.assertEqual(trends, {})
    
    def test_get_metric_trends_with_data(self):
        """Test getting metric trends with data"""
        # Add some historical data
        for i in range(10):
            metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: float(i)}
            self.monitor.check_metrics(metrics)
        
        trends = self.monitor.get_metric_trends(
            MonitoringMetric.CRITICAL_VULN_COUNT,
            time_window_minutes=60
        )
        
        self.assertIn('metric', trends)
        self.assertIn('current', trends)
        self.assertIn('min', trends)
        self.assertIn('max', trends)
        self.assertIn('mean', trends)
        self.assertIn('trend', trends)
        self.assertEqual(trends['current'], 9.0)
        self.assertEqual(trends['min'], 0.0)
        self.assertEqual(trends['max'], 9.0)
    
    def test_get_statistics(self):
        """Test getting monitoring statistics"""
        stats = self.monitor.get_statistics()
        
        self.assertIn('monitoring_sessions', stats)
        self.assertIn('alerts_generated', stats)
        self.assertIn('alerts_by_severity', stats)
        self.assertIn('alerts_by_channel', stats)
        self.assertIn('active_alerts', stats)
        self.assertIn('active_sessions', stats)
        self.assertIn('total_rules', stats)
        self.assertIn('enabled_rules', stats)
    
    def test_export_configuration(self):
        """Test exporting configuration"""
        config = self.monitor.export_configuration()
        
        self.assertIn('monitoring_level', config)
        self.assertIn('alert_rules', config)
        self.assertIn('statistics', config)
        self.assertEqual(config['monitoring_level'], 'medium')
        self.assertGreater(len(config['alert_rules']), 0)
    
    def test_monitoring_session_tracking(self):
        """Test monitoring session tracks alerts"""
        session = self.monitor.start_monitoring_session(target="test-server")
        session_id = session.session_id
        
        # Generate alert
        metrics = {MonitoringMetric.CRITICAL_VULN_COUNT: 10.0}
        self.monitor.check_metrics(metrics, session_id=session_id)
        
        # Check session alert count
        session = self.monitor.monitoring_sessions[session_id]
        self.assertGreater(session.alerts_generated, 0)
        self.assertIsNotNone(session.last_check)


class TestEnums(unittest.TestCase):
    """Test enum definitions"""
    
    def test_monitoring_level_enum(self):
        """Test MonitoringLevel enum"""
        self.assertEqual(MonitoringLevel.LOW.value, "low")
        self.assertEqual(MonitoringLevel.MEDIUM.value, "medium")
        self.assertEqual(MonitoringLevel.HIGH.value, "high")
        self.assertEqual(MonitoringLevel.PARANOID.value, "paranoid")
    
    def test_alert_severity_enum(self):
        """Test AlertSeverity enum"""
        self.assertEqual(AlertSeverity.INFO.value, "info")
        self.assertEqual(AlertSeverity.LOW.value, "low")
        self.assertEqual(AlertSeverity.MEDIUM.value, "medium")
        self.assertEqual(AlertSeverity.HIGH.value, "high")
        self.assertEqual(AlertSeverity.CRITICAL.value, "critical")
    
    def test_alert_channel_enum(self):
        """Test AlertChannel enum"""
        self.assertEqual(AlertChannel.EMAIL.value, "email")
        self.assertEqual(AlertChannel.SMS.value, "sms")
        self.assertEqual(AlertChannel.SLACK.value, "slack")
        self.assertEqual(AlertChannel.WEBHOOK.value, "webhook")
        self.assertEqual(AlertChannel.DASHBOARD.value, "dashboard")
        self.assertEqual(AlertChannel.SYSLOG.value, "syslog")
    
    def test_monitoring_metric_enum(self):
        """Test MonitoringMetric enum"""
        self.assertEqual(MonitoringMetric.VULNERABILITY_COUNT.value, "vulnerability_count")
        self.assertEqual(MonitoringMetric.CRITICAL_VULN_COUNT.value, "critical_vuln_count")
        self.assertEqual(MonitoringMetric.CVSS_SCORE_AVG.value, "cvss_score_avg")
    
    def test_alert_status_enum(self):
        """Test AlertStatus enum"""
        self.assertEqual(AlertStatus.PENDING.value, "pending")
        self.assertEqual(AlertStatus.SENT.value, "sent")
        self.assertEqual(AlertStatus.ACKNOWLEDGED.value, "acknowledged")
        self.assertEqual(AlertStatus.RESOLVED.value, "resolved")


class TestDataClasses(unittest.TestCase):
    """Test dataclass definitions"""
    
    def test_monitoring_threshold_creation(self):
        """Test MonitoringThreshold creation"""
        threshold = MonitoringThreshold(
            metric=MonitoringMetric.CRITICAL_VULN_COUNT,
            operator="gt",
            value=5.0,
            severity=AlertSeverity.CRITICAL,
            description="Test threshold"
        )
        
        self.assertEqual(threshold.metric, MonitoringMetric.CRITICAL_VULN_COUNT)
        self.assertEqual(threshold.operator, "gt")
        self.assertEqual(threshold.value, 5.0)
        self.assertTrue(threshold.enabled)
    
    def test_alert_rule_creation(self):
        """Test AlertRule creation"""
        rule = AlertRule(
            rule_id="TEST-001",
            name="Test Rule",
            description="Test description",
            threshold=MonitoringThreshold(
                metric=MonitoringMetric.CRITICAL_VULN_COUNT,
                operator="gt",
                value=5.0,
                severity=AlertSeverity.HIGH,
                description="Test"
            ),
            channels=[AlertChannel.EMAIL]
        )
        
        self.assertEqual(rule.rule_id, "TEST-001")
        self.assertEqual(rule.name, "Test Rule")
        self.assertTrue(rule.enabled)
        self.assertEqual(len(rule.channels), 1)
    
    def test_security_alert_creation(self):
        """Test SecurityAlert creation"""
        alert = SecurityAlert(
            alert_id="ALERT-001",
            rule_id="RULE-001",
            severity=AlertSeverity.CRITICAL,
            title="Test Alert",
            description="Test description",
            metric=MonitoringMetric.CRITICAL_VULN_COUNT,
            current_value=10.0,
            threshold_value=5.0,
            timestamp=datetime.now()
        )
        
        self.assertEqual(alert.alert_id, "ALERT-001")
        self.assertEqual(alert.severity, AlertSeverity.CRITICAL)
        self.assertEqual(alert.status, AlertStatus.PENDING)
        self.assertEqual(len(alert.channels_notified), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
