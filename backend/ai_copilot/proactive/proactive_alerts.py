"""
Jupiter Proactive Alerts
Automated alerting system for vulnerabilities and threats
Sends notifications through multiple channels
"""

import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Callable
from enum import Enum
import hashlib
import re


class AlertType(Enum):
    """Types of security alerts"""
    CRITICAL_VULNERABILITY = "critical_vulnerability"
    ZERO_DAY = "zero_day"
    EXPLOIT_AVAILABLE = "exploit_available"
    ACTIVE_EXPLOITATION = "active_exploitation"
    PATCH_AVAILABLE = "patch_available"
    THREAT_DETECTED = "threat_detected"
    SYSTEM_VULNERABLE = "system_vulnerable"
    COMPLIANCE_VIOLATION = "compliance_violation"
    ANOMALY_DETECTED = "anomaly_detected"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action required within hours
    MEDIUM = "medium"  # Action required within days
    LOW = "low"  # Informational
    INFO = "info"  # General information


class AlertStatus(Enum):
    """Alert lifecycle status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SNOOZED = "snoozed"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    JUPITER_CHAT = "jupiter_chat"  # Internal team chat


@dataclass
class Alert:
    """Security alert"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    created_at: datetime
    status: AlertStatus = AlertStatus.NEW
    cve_id: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    notification_sent: bool = False
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def get_age_hours(self) -> float:
        """Get alert age in hours"""
        return (datetime.now() - self.created_at).total_seconds() / 3600
    
    def is_overdue(self) -> bool:
        """Check if alert is overdue based on severity"""
        age_hours = self.get_age_hours()
        
        if self.severity == AlertSeverity.CRITICAL:
            return age_hours > 4  # 4 hours
        elif self.severity == AlertSeverity.HIGH:
            return age_hours > 24  # 1 day
        elif self.severity == AlertSeverity.MEDIUM:
            return age_hours > 72  # 3 days
        else:
            return False


@dataclass
class AlertRule:
    """Alert generation rule"""
    rule_id: str
    rule_name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    conditions: Dict  # Conditions that trigger alert
    notification_channels: List[NotificationChannel]
    is_enabled: bool = True
    throttle_minutes: int = 60  # Minimum time between alerts
    last_triggered: Optional[datetime] = None


class JupiterProactiveAlerts:
    """
    Proactive alerting system for Jupiter AI Copilot
    Monitors threats and generates automated alerts
    """
    
    def __init__(self, db_path: str = "jupiter_alerts.db"):
        self.db_path = db_path
        self._init_database()
        self._init_default_rules()
    
    def _init_database(self):
        """Initialize alerts database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                cve_id TEXT,
                affected_systems TEXT,
                recommended_actions TEXT,
                references TEXT,
                assigned_to TEXT,
                acknowledged_at TEXT,
                resolved_at TEXT,
                resolution_notes TEXT,
                notification_sent INTEGER DEFAULT 0,
                notification_channels TEXT,
                metadata TEXT
            )
        """)
        
        # Alert rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_rules (
                rule_id TEXT PRIMARY KEY,
                rule_name TEXT NOT NULL,
                description TEXT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                conditions TEXT NOT NULL,
                notification_channels TEXT NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                throttle_minutes INTEGER DEFAULT 60,
                last_triggered TEXT
            )
        """)
        
        # Alert history/changelog
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id TEXT,
                notes TEXT,
                FOREIGN KEY (alert_id) REFERENCES alerts(alert_id)
            )
        """)
        
        # Notification log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                recipient TEXT,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (alert_id) REFERENCES alerts(alert_id)
            )
        """)
        
        # Alert subscriptions (user preferences)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_subscriptions (
                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                min_severity TEXT NOT NULL,
                notification_channels TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="critical_cve",
                rule_name="Critical CVE Published",
                description="Alert when critical CVE (CVSS >= 9.0) is published",
                alert_type=AlertType.CRITICAL_VULNERABILITY,
                severity=AlertSeverity.CRITICAL,
                conditions={'min_cvss': 9.0, 'severity': 'critical'},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, 
                                      NotificationChannel.PAGERDUTY]
            ),
            AlertRule(
                rule_id="zero_day",
                rule_name="Zero-Day Vulnerability",
                description="Alert on zero-day vulnerabilities",
                alert_type=AlertType.ZERO_DAY,
                severity=AlertSeverity.CRITICAL,
                conditions={'is_zero_day': True},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK,
                                      NotificationChannel.SMS]
            ),
            AlertRule(
                rule_id="exploit_public",
                rule_name="Public Exploit Available",
                description="Alert when public exploit becomes available for high/critical CVE",
                alert_type=AlertType.EXPLOIT_AVAILABLE,
                severity=AlertSeverity.HIGH,
                conditions={'exploit_status': 'exploit_public', 'min_cvss': 7.0},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            AlertRule(
                rule_id="active_exploitation",
                rule_name="Active Exploitation Detected",
                description="Alert when vulnerability is being actively exploited in the wild",
                alert_type=AlertType.ACTIVE_EXPLOITATION,
                severity=AlertSeverity.CRITICAL,
                conditions={'exploit_status': 'in_the_wild'},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK,
                                      NotificationChannel.PAGERDUTY, NotificationChannel.SMS],
                throttle_minutes=30
            ),
            AlertRule(
                rule_id="patch_available",
                rule_name="Patch Available for Open Vulnerability",
                description="Alert when patch becomes available for tracked vulnerability",
                alert_type=AlertType.PATCH_AVAILABLE,
                severity=AlertSeverity.MEDIUM,
                conditions={'patch_available': True, 'had_no_patch': True},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.JUPITER_CHAT]
            )
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for rule in default_rules:
            cursor.execute("""
                INSERT OR IGNORE INTO alert_rules VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_id,
                rule.rule_name,
                rule.description,
                rule.alert_type.value,
                rule.severity.value,
                json.dumps(rule.conditions),
                json.dumps([ch.value for ch in rule.notification_channels]),
                rule.is_enabled,
                rule.throttle_minutes,
                None
            ))
        
        conn.commit()
        conn.close()
    
    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        cve_id: str = None,
        affected_systems: List[str] = None,
        recommended_actions: List[str] = None,
        references: List[str] = None,
        notification_channels: List[NotificationChannel] = None
    ) -> Alert:
        """Create new security alert"""
        
        alert_id = hashlib.sha256(
            f"{alert_type.value}{title}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            created_at=datetime.now(),
            cve_id=cve_id,
            affected_systems=affected_systems or [],
            recommended_actions=recommended_actions or [],
            references=references or [],
            notification_channels=notification_channels or []
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.alert_type.value,
            alert.severity.value,
            alert.title,
            alert.description,
            alert.created_at.isoformat(),
            alert.status.value,
            alert.cve_id,
            json.dumps(alert.affected_systems),
            json.dumps(alert.recommended_actions),
            json.dumps(alert.references),
            alert.assigned_to,
            None,
            None,
            alert.resolution_notes,
            alert.notification_sent,
            json.dumps([ch.value for ch in alert.notification_channels]),
            json.dumps(alert.metadata)
        ))
        
        # Log creation
        cursor.execute("""
            INSERT INTO alert_history (alert_id, timestamp, action, user_id, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (alert_id, datetime.now().isoformat(), "created", "system", f"Alert created: {title}"))
        
        conn.commit()
        conn.close()
        
        # Send notifications
        if notification_channels:
            self._send_notifications(alert)
        
        return alert
    
    def _send_notifications(self, alert: Alert):
        """Send notifications through configured channels"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for channel in alert.notification_channels:
            try:
                # In production, integrate with actual notification services
                # For now, just log the notification
                status = "sent"
                error_message = None
                
                # Simulate channel-specific logic
                if channel == NotificationChannel.EMAIL:
                    recipient = "security-team@company.com"
                elif channel == NotificationChannel.SLACK:
                    recipient = "#security-alerts"
                elif channel == NotificationChannel.PAGERDUTY:
                    recipient = "pagerduty-integration"
                else:
                    recipient = "default"
                
                cursor.execute("""
                    INSERT INTO notification_log 
                    (alert_id, channel, sent_at, recipient, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    channel.value,
                    datetime.now().isoformat(),
                    recipient,
                    status,
                    error_message
                ))
                
            except Exception as e:
                cursor.execute("""
                    INSERT INTO notification_log 
                    (alert_id, channel, sent_at, recipient, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    channel.value,
                    datetime.now().isoformat(),
                    None,
                    "failed",
                    str(e)
                ))
        
        # Mark notifications as sent
        cursor.execute("""
            UPDATE alerts SET notification_sent = 1 WHERE alert_id = ?
        """, (alert.alert_id,))
        
        conn.commit()
        conn.close()
    
    def acknowledge_alert(self, alert_id: str, user_id: str, notes: str = "") -> bool:
        """Acknowledge alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts 
            SET status = ?, acknowledged_at = ?, assigned_to = ?
            WHERE alert_id = ?
        """, (AlertStatus.ACKNOWLEDGED.value, datetime.now().isoformat(), user_id, alert_id))
        
        cursor.execute("""
            INSERT INTO alert_history (alert_id, timestamp, action, user_id, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (alert_id, datetime.now().isoformat(), "acknowledged", user_id, notes))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str) -> bool:
        """Resolve alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts 
            SET status = ?, resolved_at = ?, resolution_notes = ?
            WHERE alert_id = ?
        """, (AlertStatus.RESOLVED.value, datetime.now().isoformat(), resolution_notes, alert_id))
        
        cursor.execute("""
            INSERT INTO alert_history (alert_id, timestamp, action, user_id, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (alert_id, datetime.now().isoformat(), "resolved", user_id, resolution_notes))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def get_active_alerts(
        self,
        severity: AlertSeverity = None,
        alert_type: AlertType = None,
        assigned_to: str = None
    ) -> List[Alert]:
        """Get active (unresolved) alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM alerts WHERE status NOT IN ('resolved', 'false_positive')"
        params = []
        
        if severity:
            query += " AND severity = ?"
            params.append(severity.value)
        
        if alert_type:
            query += " AND alert_type = ?"
            params.append(alert_type.value)
        
        if assigned_to:
            query += " AND assigned_to = ?"
            params.append(assigned_to)
        
        query += " ORDER BY severity DESC, created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        alerts = []
        for row in rows:
            alert = Alert(
                alert_id=row[0],
                alert_type=AlertType(row[1]),
                severity=AlertSeverity(row[2]),
                title=row[3],
                description=row[4],
                created_at=datetime.fromisoformat(row[5]),
                status=AlertStatus(row[6]),
                cve_id=row[7],
                affected_systems=json.loads(row[8]),
                recommended_actions=json.loads(row[9]),
                references=json.loads(row[10]),
                assigned_to=row[11],
                acknowledged_at=datetime.fromisoformat(row[12]) if row[12] else None,
                resolved_at=datetime.fromisoformat(row[13]) if row[13] else None,
                resolution_notes=row[14],
                notification_sent=bool(row[15]),
                notification_channels=[NotificationChannel(ch) for ch in json.loads(row[16])],
                metadata=json.loads(row[17])
            )
            alerts.append(alert)
        
        conn.close()
        return alerts
    
    def get_overdue_alerts(self) -> List[Alert]:
        """Get alerts that are overdue for response"""
        all_alerts = self.get_active_alerts()
        return [alert for alert in all_alerts if alert.is_overdue()]
    
    def get_critical_alerts(self) -> List[Alert]:
        """Get critical severity alerts"""
        return self.get_active_alerts(severity=AlertSeverity.CRITICAL)
    
    def subscribe_user(
        self,
        user_id: str,
        alert_type: AlertType,
        min_severity: AlertSeverity,
        notification_channels: List[NotificationChannel]
    ) -> bool:
        """Subscribe user to specific alert types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alert_subscriptions 
            (user_id, alert_type, min_severity, notification_channels, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            alert_type.value,
            min_severity.value,
            json.dumps([ch.value for ch in notification_channels]),
            1
        ))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total alerts
        cursor.execute("SELECT COUNT(*) FROM alerts")
        stats['total_alerts'] = cursor.fetchone()[0]
        
        # By severity
        cursor.execute("""
            SELECT severity, COUNT(*) FROM alerts GROUP BY severity
        """)
        stats['by_severity'] = dict(cursor.fetchall())
        
        # By status
        cursor.execute("""
            SELECT status, COUNT(*) FROM alerts GROUP BY status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # By type
        cursor.execute("""
            SELECT alert_type, COUNT(*) FROM alerts GROUP BY alert_type
        """)
        stats['by_type'] = dict(cursor.fetchall())
        
        # Active alerts
        cursor.execute("""
            SELECT COUNT(*) FROM alerts 
            WHERE status NOT IN ('resolved', 'false_positive')
        """)
        stats['active_alerts'] = cursor.fetchone()[0]
        
        # Critical unresolved
        cursor.execute("""
            SELECT COUNT(*) FROM alerts 
            WHERE severity = 'critical' AND status NOT IN ('resolved', 'false_positive')
        """)
        stats['critical_unresolved'] = cursor.fetchone()[0]
        
        # Average resolution time (hours)
        cursor.execute("""
            SELECT AVG(
                (julianday(resolved_at) - julianday(created_at)) * 24
            ) FROM alerts WHERE resolved_at IS NOT NULL
        """)
        stats['avg_resolution_hours'] = cursor.fetchone()[0] or 0.0
        
        # Alerts today
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM alerts WHERE date(created_at) = ?
        """, (today,))
        stats['alerts_today'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def generate_alert_report(self, days: int = 7) -> Dict:
        """Generate alert activity report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        report = {
            'period_days': days,
            'generated_at': datetime.now().isoformat()
        }
        
        # Alerts created in period
        cursor.execute("""
            SELECT COUNT(*) FROM alerts WHERE created_at >= ?
        """, (cutoff_date,))
        report['alerts_created'] = cursor.fetchone()[0]
        
        # Alerts resolved in period
        cursor.execute("""
            SELECT COUNT(*) FROM alerts WHERE resolved_at >= ?
        """, (cutoff_date,))
        report['alerts_resolved'] = cursor.fetchone()[0]
        
        # Critical alerts in period
        cursor.execute("""
            SELECT COUNT(*) FROM alerts 
            WHERE created_at >= ? AND severity = 'critical'
        """, (cutoff_date,))
        report['critical_alerts'] = cursor.fetchone()[0]
        
        # Most common alert types
        cursor.execute("""
            SELECT alert_type, COUNT(*) as count FROM alerts 
            WHERE created_at >= ?
            GROUP BY alert_type
            ORDER BY count DESC
            LIMIT 5
        """, (cutoff_date,))
        report['top_alert_types'] = dict(cursor.fetchall())
        
        # Most affected systems
        cursor.execute("""
            SELECT affected_systems FROM alerts WHERE created_at >= ?
        """, (cutoff_date,))
        
        all_systems = []
        for row in cursor.fetchall():
            systems = json.loads(row[0])
            all_systems.extend(systems)
        
        from collections import Counter
        system_counts = Counter(all_systems)
        report['most_affected_systems'] = dict(system_counts.most_common(10))
        
        conn.close()
        return report


# Example usage
if __name__ == "__main__":
    alerts = JupiterProactiveAlerts()
    
    # Create critical alert
    alert = alerts.create_alert(
        alert_type=AlertType.CRITICAL_VULNERABILITY,
        severity=AlertSeverity.CRITICAL,
        title="CVE-2024-12345: Critical RCE in Web Framework",
        description="A critical remote code execution vulnerability has been discovered...",
        cve_id="CVE-2024-12345",
        affected_systems=["webserver-01", "webserver-02", "webserver-03"],
        recommended_actions=[
            "Immediately apply security patch",
            "Restart affected services",
            "Monitor for exploitation attempts"
        ],
        references=[
            "https://nvd.nist.gov/vuln/detail/CVE-2024-12345",
            "https://vendor.com/security/advisory-123"
        ],
        notification_channels=[
            NotificationChannel.EMAIL,
            NotificationChannel.SLACK,
            NotificationChannel.PAGERDUTY
        ]
    )
    
    print(f"Created alert: {alert.alert_id}")
    print(f"Severity: {alert.severity.value}")
    print(f"Status: {alert.status.value}")
    
    # Get active alerts
    active = alerts.get_active_alerts()
    print(f"\nActive alerts: {len(active)}")
    
    # Get statistics
    stats = alerts.get_alert_statistics()
    print(f"\nAlert statistics:")
    print(f"  Total: {stats['total_alerts']}")
    print(f"  Active: {stats['active_alerts']}")
    print(f"  Critical unresolved: {stats['critical_unresolved']}")
