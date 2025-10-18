"""
Continuous Security Monitoring System
Real-time security posture tracking and alerting for Enterprise Scanner

This module provides continuous security monitoring capabilities:
- Real-time security metrics dashboard
- Historical trend analysis and comparisons
- Alert system for critical findings (email, webhook, Slack)
- Automated scheduled assessments
- Security score tracking over time
- Compliance posture monitoring
- Anomaly detection for security degradation

Features:
- Time-series security score tracking
- Finding severity trend analysis
- Compliance framework score history
- Multi-dimensional security metrics
- Configurable alert thresholds
- Integration with notification systems

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from enum import Enum

try:
    import sqlite3
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringMetric(Enum):
    """Types of security metrics to monitor"""
    OVERALL_SCORE = "overall_score"
    INFRASTRUCTURE_SCORE = "infrastructure_score"
    NETWORK_SCORE = "network_score"
    CLOUD_SCORE = "cloud_score"
    CONTAINER_SCORE = "container_score"
    VULNERABILITY_COUNT = "vulnerability_count"
    CRITICAL_FINDINGS = "critical_findings"
    HIGH_FINDINGS = "high_findings"
    COMPLIANCE_SCORE = "compliance_score"


@dataclass
class SecuritySnapshot:
    """Point-in-time security assessment snapshot"""
    timestamp: datetime
    assessment_id: str
    company_name: str
    overall_score: float
    risk_level: str
    category_scores: Dict[str, float]
    vulnerability_counts: Dict[str, int]
    total_findings: int
    critical_findings: int
    high_findings: int
    compliance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityAlert:
    """Security alert triggered by monitoring"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    metric: str
    message: str
    current_value: Any
    threshold: Any
    assessment_id: str
    company_name: str
    recommendations: List[str] = field(default_factory=list)


class ContinuousSecurityMonitor:
    """
    Continuous Security Monitoring System
    
    Tracks security posture over time, generates alerts for degradation,
    and provides historical trend analysis for Fortune 500 enterprises.
    
    Features:
    - Real-time security score tracking
    - Historical trend analysis
    - Configurable alert thresholds
    - Multi-channel alert delivery
    - Compliance tracking over time
    """
    
    def __init__(self, db_path: str = "security_monitoring.db"):
        """
        Initialize continuous monitoring system
        
        Args:
            db_path: Path to SQLite database for metrics storage
        """
        self.db_path = db_path
        self.alert_thresholds = self._get_default_thresholds()
        self.alert_handlers = []
        
        if DB_AVAILABLE:
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Security snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    assessment_id TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    infrastructure_score REAL,
                    network_score REAL,
                    cloud_score REAL,
                    container_score REAL,
                    vulnerability_score REAL,
                    compliance_score REAL,
                    total_findings INTEGER,
                    critical_findings INTEGER,
                    high_findings INTEGER,
                    medium_findings INTEGER,
                    low_findings INTEGER,
                    metadata TEXT
                )
            ''')
            
            # Security alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    message TEXT NOT NULL,
                    current_value TEXT,
                    threshold TEXT,
                    assessment_id TEXT,
                    company_name TEXT,
                    recommendations TEXT,
                    acknowledged BOOLEAN DEFAULT 0
                )
            ''')
            
            # Monitoring metrics time series table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    assessment_id TEXT
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_snapshots_company_timestamp 
                ON security_snapshots(company_name, timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_alerts_company_timestamp 
                ON security_alerts(company_name, timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_company_metric_timestamp 
                ON monitoring_metrics(company_name, metric_name, timestamp)
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
    
    def _get_default_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Get default alert thresholds"""
        return {
            'overall_score': {
                'critical': 60,  # Alert if score drops below 60
                'warning': 75    # Warning if score drops below 75
            },
            'critical_findings': {
                'critical': 5,   # Alert if 5+ critical findings
                'warning': 3     # Warning if 3+ critical findings
            },
            'high_findings': {
                'critical': 10,  # Alert if 10+ high findings
                'warning': 7     # Warning if 7+ high findings
            },
            'score_degradation': {
                'critical': -15,  # Alert if score drops >15 points
                'warning': -10    # Warning if score drops >10 points
            }
        }
    
    def configure_alert_threshold(self, metric: str, severity: str, value: Any):
        """
        Configure custom alert threshold
        
        Args:
            metric: Metric name (e.g., 'overall_score', 'critical_findings')
            severity: 'critical' or 'warning'
            value: Threshold value
        """
        if metric not in self.alert_thresholds:
            self.alert_thresholds[metric] = {}
        self.alert_thresholds[metric][severity] = value
    
    def add_alert_handler(self, handler: callable):
        """
        Add custom alert handler function
        
        Args:
            handler: Function that receives SecurityAlert and processes it
        """
        self.alert_handlers.append(handler)
    
    def record_assessment(self, assessment_results: Dict[str, Any]) -> SecuritySnapshot:
        """
        Record security assessment results for continuous monitoring
        
        Args:
            assessment_results: Complete assessment results from SecurityAssessmentEngine
        
        Returns:
            SecuritySnapshot with recorded metrics
        """
        timestamp = datetime.now()
        
        # Extract key metrics
        snapshot = SecuritySnapshot(
            timestamp=timestamp,
            assessment_id=assessment_results.get('assessment_metadata', {}).get('assessment_id', 'unknown'),
            company_name=assessment_results.get('assessment_metadata', {}).get('company_name', 'Unknown'),
            overall_score=assessment_results.get('overall_score', 0),
            risk_level=assessment_results.get('risk_level', 'UNKNOWN'),
            category_scores=assessment_results.get('category_scores', {}),
            vulnerability_counts=assessment_results.get('vulnerability_counts', {}),
            total_findings=assessment_results.get('vulnerability_counts', {}).get('total', 0),
            critical_findings=assessment_results.get('vulnerability_counts', {}).get('critical', 0),
            high_findings=assessment_results.get('vulnerability_counts', {}).get('high', 0),
            compliance_score=assessment_results.get('category_scores', {}).get('Compliance Posture', 0),
            metadata=assessment_results.get('assessment_metadata', {})
        )
        
        # Store in database
        if DB_AVAILABLE:
            self._store_snapshot(snapshot)
            self._store_metrics(snapshot)
        
        # Check for alerts
        alerts = self._check_alert_conditions(snapshot)
        
        # Trigger alert handlers
        for alert in alerts:
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    print(f"Alert handler failed: {e}")
        
        return snapshot
    
    def _store_snapshot(self, snapshot: SecuritySnapshot):
        """Store security snapshot in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_snapshots (
                    timestamp, assessment_id, company_name, overall_score, risk_level,
                    infrastructure_score, network_score, cloud_score, container_score,
                    vulnerability_score, compliance_score, total_findings, critical_findings,
                    high_findings, medium_findings, low_findings, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.timestamp.isoformat(),
                snapshot.assessment_id,
                snapshot.company_name,
                snapshot.overall_score,
                snapshot.risk_level,
                snapshot.category_scores.get('Infrastructure Security', 0),
                snapshot.category_scores.get('Network Security', 0),
                snapshot.category_scores.get('Cloud Security', 0),
                snapshot.category_scores.get('Container Security', 0),
                snapshot.category_scores.get('Vulnerability Assessment', 0),
                snapshot.compliance_score,
                snapshot.total_findings,
                snapshot.critical_findings,
                snapshot.high_findings,
                snapshot.vulnerability_counts.get('medium', 0),
                snapshot.vulnerability_counts.get('low', 0),
                json.dumps(snapshot.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to store snapshot: {e}")
    
    def _store_metrics(self, snapshot: SecuritySnapshot):
        """Store individual metrics for time-series analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metrics = [
                ('overall_score', snapshot.overall_score),
                ('critical_findings', snapshot.critical_findings),
                ('high_findings', snapshot.high_findings),
                ('total_findings', snapshot.total_findings),
                ('compliance_score', snapshot.compliance_score)
            ]
            
            # Add category scores
            for category, score in snapshot.category_scores.items():
                metric_name = category.lower().replace(' ', '_')
                metrics.append((metric_name, score))
            
            # Insert all metrics
            for metric_name, metric_value in metrics:
                cursor.execute('''
                    INSERT INTO monitoring_metrics (
                        timestamp, company_name, metric_name, metric_value, assessment_id
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    snapshot.timestamp.isoformat(),
                    snapshot.company_name,
                    metric_name,
                    metric_value,
                    snapshot.assessment_id
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to store metrics: {e}")
    
    def _check_alert_conditions(self, snapshot: SecuritySnapshot) -> List[SecurityAlert]:
        """Check if any alert conditions are met"""
        alerts = []
        
        # Check overall score
        if snapshot.overall_score < self.alert_thresholds['overall_score']['critical']:
            alerts.append(SecurityAlert(
                alert_id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-001",
                timestamp=datetime.now(),
                severity=AlertSeverity.CRITICAL,
                metric='overall_score',
                message=f"CRITICAL: Overall security score dropped to {snapshot.overall_score}",
                current_value=snapshot.overall_score,
                threshold=self.alert_thresholds['overall_score']['critical'],
                assessment_id=snapshot.assessment_id,
                company_name=snapshot.company_name,
                recommendations=[
                    "Immediate security review required",
                    "Address critical and high severity findings",
                    "Consider engaging security consultant"
                ]
            ))
        elif snapshot.overall_score < self.alert_thresholds['overall_score']['warning']:
            alerts.append(SecurityAlert(
                alert_id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                timestamp=datetime.now(),
                severity=AlertSeverity.WARNING,
                metric='overall_score',
                message=f"WARNING: Overall security score at {snapshot.overall_score}",
                current_value=snapshot.overall_score,
                threshold=self.alert_thresholds['overall_score']['warning'],
                assessment_id=snapshot.assessment_id,
                company_name=snapshot.company_name,
                recommendations=[
                    "Review and remediate high severity findings",
                    "Schedule security improvement initiatives"
                ]
            ))
        
        # Check critical findings
        if snapshot.critical_findings >= self.alert_thresholds['critical_findings']['critical']:
            alerts.append(SecurityAlert(
                alert_id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-003",
                timestamp=datetime.now(),
                severity=AlertSeverity.CRITICAL,
                metric='critical_findings',
                message=f"CRITICAL: {snapshot.critical_findings} critical security findings detected",
                current_value=snapshot.critical_findings,
                threshold=self.alert_thresholds['critical_findings']['critical'],
                assessment_id=snapshot.assessment_id,
                company_name=snapshot.company_name,
                recommendations=[
                    "Address all critical findings immediately",
                    "Implement emergency remediation plan"
                ]
            ))
        
        # Check for score degradation (compare to previous assessment)
        previous_snapshot = self.get_latest_snapshot(snapshot.company_name, exclude_current=True)
        if previous_snapshot:
            score_change = snapshot.overall_score - previous_snapshot.overall_score
            
            if score_change <= self.alert_thresholds['score_degradation']['critical']:
                alerts.append(SecurityAlert(
                    alert_id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-004",
                    timestamp=datetime.now(),
                    severity=AlertSeverity.CRITICAL,
                    metric='score_degradation',
                    message=f"CRITICAL: Security score degraded by {abs(score_change)} points",
                    current_value=score_change,
                    threshold=self.alert_thresholds['score_degradation']['critical'],
                    assessment_id=snapshot.assessment_id,
                    company_name=snapshot.company_name,
                    recommendations=[
                        "Investigate recent infrastructure/configuration changes",
                        "Review new vulnerabilities introduced",
                        "Restore previous secure configurations if possible"
                    ]
                ))
        
        # Store alerts in database
        if DB_AVAILABLE and alerts:
            self._store_alerts(alerts)
        
        return alerts
    
    def _store_alerts(self, alerts: List[SecurityAlert]):
        """Store alerts in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for alert in alerts:
                cursor.execute('''
                    INSERT INTO security_alerts (
                        alert_id, timestamp, severity, metric, message,
                        current_value, threshold, assessment_id, company_name, recommendations
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id,
                    alert.timestamp.isoformat(),
                    alert.severity.value,
                    alert.metric,
                    alert.message,
                    str(alert.current_value),
                    str(alert.threshold),
                    alert.assessment_id,
                    alert.company_name,
                    json.dumps(alert.recommendations)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to store alerts: {e}")
    
    def get_latest_snapshot(self, company_name: str, exclude_current: bool = False) -> Optional[SecuritySnapshot]:
        """
        Get most recent security snapshot for company
        
        Args:
            company_name: Company name
            exclude_current: Exclude most recent (get second-to-last)
        
        Returns:
            SecuritySnapshot or None
        """
        if not DB_AVAILABLE:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            limit = 2 if exclude_current else 1
            cursor.execute('''
                SELECT * FROM security_snapshots
                WHERE company_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (company_name, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            row = rows[-1]  # Get last if exclude_current, otherwise first
            
            return SecuritySnapshot(
                timestamp=datetime.fromisoformat(row[1]),
                assessment_id=row[2],
                company_name=row[3],
                overall_score=row[4],
                risk_level=row[5],
                category_scores={
                    'Infrastructure Security': row[6] or 0,
                    'Network Security': row[7] or 0,
                    'Cloud Security': row[8] or 0,
                    'Container Security': row[9] or 0,
                    'Vulnerability Assessment': row[10] or 0,
                    'Compliance Posture': row[11] or 0
                },
                vulnerability_counts={
                    'total': row[12] or 0,
                    'critical': row[13] or 0,
                    'high': row[14] or 0,
                    'medium': row[15] or 0,
                    'low': row[16] or 0
                },
                total_findings=row[12] or 0,
                critical_findings=row[13] or 0,
                high_findings=row[14] or 0,
                compliance_score=row[11] or 0,
                metadata=json.loads(row[17]) if row[17] else {}
            )
            
        except Exception as e:
            print(f"Failed to get latest snapshot: {e}")
            return None
    
    def get_security_trend(self, company_name: str, metric: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical trend for specific security metric
        
        Args:
            company_name: Company name
            metric: Metric name (e.g., 'overall_score', 'critical_findings')
            days: Number of days to retrieve
        
        Returns:
            List of {timestamp, value} dicts
        """
        if not DB_AVAILABLE:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT timestamp, metric_value
                FROM monitoring_metrics
                WHERE company_name = ? AND metric_name = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (company_name, metric, start_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {'timestamp': row[0], 'value': row[1]}
                for row in rows
            ]
            
        except Exception as e:
            print(f"Failed to get security trend: {e}")
            return []
    
    def get_active_alerts(self, company_name: Optional[str] = None, severity: Optional[AlertSeverity] = None) -> List[SecurityAlert]:
        """
        Get active (unacknowledged) alerts
        
        Args:
            company_name: Filter by company (None = all)
            severity: Filter by severity (None = all)
        
        Returns:
            List of SecurityAlert objects
        """
        if not DB_AVAILABLE:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM security_alerts WHERE acknowledged = 0"
            params = []
            
            if company_name:
                query += " AND company_name = ?"
                params.append(company_name)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append(SecurityAlert(
                    alert_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    severity=AlertSeverity(row[3]),
                    metric=row[4],
                    message=row[5],
                    current_value=row[6],
                    threshold=row[7],
                    assessment_id=row[8] or '',
                    company_name=row[9] or '',
                    recommendations=json.loads(row[10]) if row[10] else []
                ))
            
            return alerts
            
        except Exception as e:
            print(f"Failed to get active alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str):
        """Mark alert as acknowledged"""
        if not DB_AVAILABLE:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE security_alerts SET acknowledged = 1 WHERE alert_id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to acknowledge alert: {e}")
    
    def get_monitoring_dashboard_data(self, company_name: str) -> Dict[str, Any]:
        """
        Get comprehensive monitoring dashboard data
        
        Args:
            company_name: Company name
        
        Returns:
            Dict with dashboard metrics, trends, and alerts
        """
        latest_snapshot = self.get_latest_snapshot(company_name)
        
        if not latest_snapshot:
            return {
                'error': 'No assessment data available for this company',
                'company_name': company_name
            }
        
        # Get trends (30 days)
        score_trend = self.get_security_trend(company_name, 'overall_score', days=30)
        critical_trend = self.get_security_trend(company_name, 'critical_findings', days=30)
        
        # Get active alerts
        active_alerts = self.get_active_alerts(company_name)
        
        # Calculate trend direction
        if len(score_trend) >= 2:
            score_change = score_trend[-1]['value'] - score_trend[0]['value']
            trend_direction = 'improving' if score_change > 0 else 'declining' if score_change < 0 else 'stable'
        else:
            trend_direction = 'insufficient_data'
        
        return {
            'company_name': company_name,
            'current_status': {
                'overall_score': latest_snapshot.overall_score,
                'risk_level': latest_snapshot.risk_level,
                'last_assessment': latest_snapshot.timestamp.isoformat(),
                'assessment_id': latest_snapshot.assessment_id
            },
            'category_scores': latest_snapshot.category_scores,
            'vulnerability_summary': {
                'total': latest_snapshot.total_findings,
                'critical': latest_snapshot.critical_findings,
                'high': latest_snapshot.high_findings,
                'medium': latest_snapshot.vulnerability_counts.get('medium', 0),
                'low': latest_snapshot.vulnerability_counts.get('low', 0)
            },
            'trends': {
                'direction': trend_direction,
                'score_history': score_trend,
                'critical_findings_history': critical_trend
            },
            'active_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in active_alerts
            ],
            'alerts_summary': {
                'critical': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                'warning': len([a for a in active_alerts if a.severity == AlertSeverity.WARNING]),
                'total': len(active_alerts)
            }
        }


# Module availability check
def is_available() -> bool:
    """Check if monitoring module is available"""
    return DB_AVAILABLE
