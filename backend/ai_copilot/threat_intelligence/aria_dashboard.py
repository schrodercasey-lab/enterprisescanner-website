"""
G.2.11: ARIA Dashboard Integration

Enterprise-grade threat intelligence visualization and dashboard integration for ARIA.
Provides real-time threat intelligence display, interactive widgets, charts, and
alert management UI for seamless integration with the ARIA security platform.

Features:
- Real-time threat intelligence visualization
- Modular widget system
- Interactive charts and graphs
- Live threat feed display
- Alert management interface
- Risk dashboard widgets
- Campaign tracking display
- Actor profile cards
- Vulnerability heat maps
- WebSocket real-time updates

Author: Enterprise Scanner Development Team
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict


class WidgetType(Enum):
    """Dashboard widget types"""
    THREAT_FEED = "threat_feed"              # Live threat intelligence feed
    RISK_SCORE = "risk_score"                # Overall risk score gauge
    THREAT_MAP = "threat_map"                # Geographic threat map
    CAMPAIGN_TRACKER = "campaign_tracker"    # Active campaign tracking
    ACTOR_PROFILE = "actor_profile"          # Threat actor profiles
    VULNERABILITY_LIST = "vulnerability_list" # Critical vulnerabilities
    ALERT_PANEL = "alert_panel"              # Active alerts
    TREND_CHART = "trend_chart"              # Threat trend charts
    COMPLIANCE_STATUS = "compliance_status"   # Compliance dashboard
    IOC_FEED = "ioc_feed"                    # Indicator of Compromise feed


class ChartType(Enum):
    """Chart visualization types"""
    LINE = "line"              # Line chart for trends
    BAR = "bar"                # Bar chart for comparisons
    PIE = "pie"                # Pie chart for distributions
    GAUGE = "gauge"            # Gauge for single metrics
    HEATMAP = "heatmap"        # Heat map for intensity
    TIMELINE = "timeline"      # Timeline for events
    SCATTER = "scatter"        # Scatter plot for correlations


class UpdateFrequency(Enum):
    """Widget update frequency"""
    REALTIME = "realtime"      # WebSocket real-time updates
    FAST = "fast"              # 5 second refresh
    NORMAL = "normal"          # 30 second refresh
    SLOW = "slow"              # 5 minute refresh
    MANUAL = "manual"          # Manual refresh only


class AlertPriority(Enum):
    """Alert display priority"""
    CRITICAL = "critical"      # Red, immediate attention
    HIGH = "high"              # Orange, urgent
    MEDIUM = "medium"          # Yellow, important
    LOW = "low"                # Blue, informational
    INFO = "info"              # Green, general information


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: WidgetType
    title: str
    position: Dict[str, int]  # {x, y, width, height}
    update_frequency: UpdateFrequency
    config: Dict[str, Any]
    is_visible: bool = True
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert widget to dictionary for JSON serialization"""
        return {
            'widget_id': self.widget_id,
            'widget_type': self.widget_type.value,
            'title': self.title,
            'position': self.position,
            'update_frequency': self.update_frequency.value,
            'config': self.config,
            'is_visible': self.is_visible,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


@dataclass
class ChartData:
    """Chart data structure"""
    chart_type: ChartType
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]  # {label, data, color, etc.}
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chart to dictionary for visualization"""
        return {
            'type': self.chart_type.value,
            'title': self.title,
            'labels': self.labels,
            'datasets': self.datasets,
            'options': self.options
        }


@dataclass
class ThreatFeedItem:
    """Threat intelligence feed item for display"""
    item_id: str
    threat_type: str
    severity: str
    title: str
    description: str
    timestamp: datetime
    source: str
    confidence: float
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            'item_id': self.item_id,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'confidence': self.confidence,
            'tags': self.tags
        }


@dataclass
class AlertNotification:
    """Alert notification for UI display"""
    alert_id: str
    priority: AlertPriority
    title: str
    message: str
    timestamp: datetime
    action_url: Optional[str] = None
    dismissible: bool = True
    auto_dismiss_seconds: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            'alert_id': self.alert_id,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'action_url': self.action_url,
            'dismissible': self.dismissible,
            'auto_dismiss_seconds': self.auto_dismiss_seconds
        }


class ARIADashboardIntegration:
    """
    ARIA dashboard integration for threat intelligence visualization.
    
    Provides real-time threat intelligence display, interactive widgets,
    charts, and alert management interface for seamless integration with
    the ARIA security platform.
    """
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        self.db_path = db_path
        self._init_database()
        
        # Widget registry
        self.widgets: Dict[str, DashboardWidget] = {}
        
        # Real-time update callbacks
        self.update_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
    def _init_database(self):
        """Initialize dashboard integration tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Dashboard widgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_widgets (
                widget_id TEXT PRIMARY KEY,
                widget_type TEXT NOT NULL,
                title TEXT NOT NULL,
                position TEXT NOT NULL,
                update_frequency TEXT NOT NULL,
                config TEXT,
                is_visible INTEGER DEFAULT 1,
                last_updated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Alert notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_notifications (
                alert_id TEXT PRIMARY KEY,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_url TEXT,
                dismissible INTEGER DEFAULT 1,
                auto_dismiss_seconds INTEGER,
                dismissed INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_widget(
        self,
        widget_type: WidgetType,
        title: str,
        position: Dict[str, int],
        update_frequency: UpdateFrequency,
        config: Optional[Dict[str, Any]] = None
    ) -> DashboardWidget:
        """Create new dashboard widget"""
        import hashlib
        import time
        
        widget_id = hashlib.sha256(
            f"{widget_type.value}{title}{time.time()}".encode()
        ).hexdigest()[:16]
        
        widget = DashboardWidget(
            widget_id=widget_id,
            widget_type=widget_type,
            title=title,
            position=position,
            update_frequency=update_frequency,
            config=config or {}
        )
        
        # Store widget
        self.widgets[widget_id] = widget
        self._store_widget(widget)
        
        return widget
    
    def _store_widget(self, widget: DashboardWidget):
        """Store widget in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO dashboard_widgets
            (widget_id, widget_type, title, position, update_frequency,
             config, is_visible, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            widget.widget_id,
            widget.widget_type.value,
            widget.title,
            json.dumps(widget.position),
            widget.update_frequency.value,
            json.dumps(widget.config),
            1 if widget.is_visible else 0,
            widget.last_updated.isoformat() if widget.last_updated else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_threat_feed_data(
        self, limit: int = 20, severity_filter: Optional[List[str]] = None
    ) -> List[ThreatFeedItem]:
        """Get threat intelligence feed data for display"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT ioc_id, indicator_type, threat_level, indicator,
                   context, first_seen, source, confidence
            FROM indicators_of_compromise
            WHERE 1=1
        """
        params = []
        
        if severity_filter:
            placeholders = ','.join('?' * len(severity_filter))
            query += f" AND threat_level IN ({placeholders})"
            params.extend(severity_filter)
        
        query += " ORDER BY first_seen DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        feed_items = []
        for row in cursor.fetchall():
            ioc_id, indicator_type, threat_level, indicator, context, first_seen, source, confidence = row
            
            item = ThreatFeedItem(
                item_id=ioc_id,
                threat_type=indicator_type,
                severity=threat_level,
                title=f"{indicator_type.upper()}: {indicator}",
                description=context or "No description available",
                timestamp=datetime.fromisoformat(first_seen),
                source=source,
                confidence=confidence or 0.5,
                tags=[threat_level, indicator_type]
            )
            feed_items.append(item)
        
        conn.close()
        return feed_items
    
    def get_risk_score_widget_data(self) -> Dict[str, Any]:
        """Get risk score gauge widget data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count critical vulnerabilities
        cursor.execute("""
            SELECT COUNT(*) FROM vulnerabilities
            WHERE severity = 'critical'
        """)
        critical_vulns = cursor.fetchone()[0]
        
        # Count active campaigns
        cursor.execute("""
            SELECT COUNT(*) FROM threat_campaigns
            WHERE status = 'active'
        """)
        active_campaigns = cursor.fetchone()[0]
        
        # Count high severity IoCs
        cursor.execute("""
            SELECT COUNT(*) FROM indicators_of_compromise
            WHERE threat_level IN ('high', 'critical')
        """)
        high_severity_iocs = cursor.fetchone()[0]
        
        conn.close()
        
        # Calculate overall risk score (0-100)
        risk_score = min(100, (
            critical_vulns * 10 +
            active_campaigns * 8 +
            high_severity_iocs * 2
        ))
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
            color = "#dc3545"  # Red
        elif risk_score >= 60:
            risk_level = "HIGH"
            color = "#fd7e14"  # Orange
        elif risk_score >= 40:
            risk_level = "MODERATE"
            color = "#ffc107"  # Yellow
        elif risk_score >= 20:
            risk_level = "LOW"
            color = "#0dcaf0"  # Cyan
        else:
            risk_level = "MINIMAL"
            color = "#198754"  # Green
        
        return {
            'score': risk_score,
            'level': risk_level,
            'color': color,
            'breakdown': {
                'critical_vulnerabilities': critical_vulns,
                'active_campaigns': active_campaigns,
                'high_severity_threats': high_severity_iocs
            }
        }
    
    def generate_threat_trend_chart(self, days: int = 30) -> ChartData:
        """Generate threat trend line chart"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        labels = []
        threat_counts = []
        
        for i in range(days):
            day = datetime.utcnow() - timedelta(days=days-i-1)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            cursor.execute("""
                SELECT COUNT(*) FROM indicators_of_compromise
                WHERE first_seen >= ? AND first_seen < ?
            """, (day_start.isoformat(), day_end.isoformat()))
            
            count = cursor.fetchone()[0]
            labels.append(day.strftime('%m/%d'))
            threat_counts.append(count)
        
        conn.close()
        
        return ChartData(
            chart_type=ChartType.LINE,
            title=f"Threat Activity - Last {days} Days",
            labels=labels,
            datasets=[{
                'label': 'Threats Detected',
                'data': threat_counts,
                'borderColor': '#0d6efd',
                'backgroundColor': 'rgba(13, 110, 253, 0.1)',
                'tension': 0.4
            }],
            options={
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {
                    'y': {'beginAtZero': True}
                }
            }
        )
    
    def generate_severity_distribution_chart(self) -> ChartData:
        """Generate severity distribution pie chart"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT threat_level, COUNT(*) as count
            FROM indicators_of_compromise
            GROUP BY threat_level
            ORDER BY 
                CASE threat_level
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        labels = []
        data = []
        colors = []
        
        color_map = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#0dcaf0',
            'info': '#198754'
        }
        
        for threat_level, count in results:
            labels.append(threat_level.title())
            data.append(count)
            colors.append(color_map.get(threat_level, '#6c757d'))
        
        return ChartData(
            chart_type=ChartType.PIE,
            title="Threat Severity Distribution",
            labels=labels,
            datasets=[{
                'data': data,
                'backgroundColor': colors,
                'borderWidth': 2
            }],
            options={
                'responsive': True,
                'plugins': {
                    'legend': {'position': 'right'}
                }
            }
        )
    
    def get_active_campaigns_widget_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get active campaign tracking data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT campaign_id, name, threat_actor, target_industries,
                   start_date, malware_families, ttps, status
            FROM threat_campaigns
            WHERE status = 'active'
            ORDER BY start_date DESC
            LIMIT ?
        """, (limit,))
        
        campaigns = []
        for row in cursor.fetchall():
            campaign_id, name, actor, industries, start_date, malware, ttps, status = row
            
            campaigns.append({
                'campaign_id': campaign_id,
                'name': name,
                'threat_actor': actor,
                'target_industries': json.loads(industries) if industries else [],
                'start_date': start_date,
                'malware_families': json.loads(malware) if malware else [],
                'ttps': json.loads(ttps) if ttps else [],
                'status': status,
                'duration_days': (datetime.utcnow() - datetime.fromisoformat(start_date)).days
            })
        
        conn.close()
        return campaigns
    
    def get_critical_vulnerabilities_widget_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get critical vulnerabilities for display"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cve_id, description, cvss_score, severity,
                   published_date, exploit_available
            FROM vulnerabilities
            WHERE severity = 'critical'
            ORDER BY cvss_score DESC, published_date DESC
            LIMIT ?
        """, (limit,))
        
        vulnerabilities = []
        for row in cursor.fetchall():
            cve_id, description, cvss_score, severity, published, exploit = row
            
            vulnerabilities.append({
                'cve_id': cve_id,
                'description': description[:200] + '...' if description and len(description) > 200 else description,
                'cvss_score': cvss_score,
                'severity': severity,
                'published_date': published,
                'exploit_available': bool(exploit),
                'age_days': (datetime.utcnow() - datetime.fromisoformat(published)).days if published else 0
            })
        
        conn.close()
        return vulnerabilities
    
    def create_alert_notification(
        self,
        priority: AlertPriority,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        auto_dismiss_seconds: Optional[int] = None
    ) -> AlertNotification:
        """Create alert notification for dashboard"""
        import hashlib
        import time
        
        alert_id = hashlib.sha256(
            f"{title}{message}{time.time()}".encode()
        ).hexdigest()[:16]
        
        alert = AlertNotification(
            alert_id=alert_id,
            priority=priority,
            title=title,
            message=message,
            timestamp=datetime.utcnow(),
            action_url=action_url,
            auto_dismiss_seconds=auto_dismiss_seconds
        )
        
        # Store alert
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alert_notifications
            (alert_id, priority, title, message, timestamp, action_url,
             dismissible, auto_dismiss_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id, alert.priority.value, alert.title, alert.message,
            alert.timestamp.isoformat(), alert.action_url,
            1 if alert.dismissible else 0, alert.auto_dismiss_seconds
        ))
        
        conn.commit()
        conn.close()
        
        # Trigger real-time update callbacks
        self._trigger_callbacks('alert_notification', alert)
        
        return alert
    
    def get_dashboard_layout(self) -> Dict[str, Any]:
        """Get complete dashboard layout configuration"""
        return {
            'widgets': [widget.to_dict() for widget in self.widgets.values()],
            'theme': {
                'primary_color': '#0d6efd',
                'danger_color': '#dc3545',
                'warning_color': '#ffc107',
                'success_color': '#198754',
                'info_color': '#0dcaf0'
            },
            'refresh_intervals': {
                'realtime': 0,  # WebSocket
                'fast': 5000,   # 5 seconds
                'normal': 30000, # 30 seconds
                'slow': 300000   # 5 minutes
            }
        }
    
    def register_update_callback(self, event_type: str, callback: Callable):
        """Register callback for real-time updates"""
        self.update_callbacks[event_type].append(callback)
    
    def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger registered callbacks for event"""
        for callback in self.update_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get complete dashboard summary for ARIA"""
        return {
            'risk_score': self.get_risk_score_widget_data(),
            'threat_feed': [item.to_dict() for item in self.get_threat_feed_data(limit=10)],
            'active_campaigns': self.get_active_campaigns_widget_data(limit=5),
            'critical_vulnerabilities': self.get_critical_vulnerabilities_widget_data(limit=5),
            'trend_chart': self.generate_threat_trend_chart(days=7).to_dict(),
            'severity_distribution': self.generate_severity_distribution_chart().to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Initialize ARIA dashboard integration
    aria = ARIADashboardIntegration()
    
    print("=== ARIA Dashboard Integration ===\n")
    
    # Example 1: Create widgets
    print("=== Dashboard Widgets ===\n")
    
    # Risk score widget
    risk_widget = aria.create_widget(
        widget_type=WidgetType.RISK_SCORE,
        title="Overall Risk Score",
        position={'x': 0, 'y': 0, 'width': 4, 'height': 2},
        update_frequency=UpdateFrequency.FAST,
        config={'show_breakdown': True}
    )
    print(f"Created widget: {risk_widget.title} ({risk_widget.widget_id})")
    
    # Threat feed widget
    feed_widget = aria.create_widget(
        widget_type=WidgetType.THREAT_FEED,
        title="Live Threat Intelligence Feed",
        position={'x': 4, 'y': 0, 'width': 8, 'height': 6},
        update_frequency=UpdateFrequency.REALTIME,
        config={'max_items': 20, 'severity_filter': ['critical', 'high']}
    )
    print(f"Created widget: {feed_widget.title} ({feed_widget.widget_id})")
    
    # Trend chart widget
    chart_widget = aria.create_widget(
        widget_type=WidgetType.TREND_CHART,
        title="Threat Activity Trends",
        position={'x': 0, 'y': 2, 'width': 6, 'height': 4},
        update_frequency=UpdateFrequency.NORMAL,
        config={'days': 30, 'chart_type': 'line'}
    )
    print(f"Created widget: {chart_widget.title} ({chart_widget.widget_id})")
    
    # Example 2: Get risk score data
    print("\n=== Risk Score Widget ===\n")
    
    risk_data = aria.get_risk_score_widget_data()
    print(f"Risk Score: {risk_data['score']}/100")
    print(f"Risk Level: {risk_data['level']}")
    print(f"Color: {risk_data['color']}")
    print(f"Breakdown:")
    for key, value in risk_data['breakdown'].items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Example 3: Get threat feed
    print("\n=== Threat Intelligence Feed ===\n")
    
    feed_items = aria.get_threat_feed_data(limit=5)
    print(f"Recent threats: {len(feed_items)}")
    for item in feed_items[:3]:
        print(f"\n{item.severity.upper()} - {item.title}")
        print(f"  Source: {item.source}")
        print(f"  Confidence: {item.confidence:.0%}")
        print(f"  Time: {item.timestamp.strftime('%Y-%m-%d %H:%M')}")
    
    # Example 4: Generate charts
    print("\n=== Threat Trend Chart ===\n")
    
    trend_chart = aria.generate_threat_trend_chart(days=7)
    print(f"Chart Type: {trend_chart.chart_type.value}")
    print(f"Title: {trend_chart.title}")
    print(f"Data Points: {len(trend_chart.labels)}")
    print(f"Latest Count: {trend_chart.datasets[0]['data'][-1]}")
    
    print("\n=== Severity Distribution Chart ===\n")
    
    severity_chart = aria.generate_severity_distribution_chart()
    print(f"Chart Type: {severity_chart.chart_type.value}")
    print(f"Title: {severity_chart.title}")
    print(f"Categories: {', '.join(severity_chart.labels)}")
    
    # Example 5: Get active campaigns
    print("\n=== Active Campaign Tracking ===\n")
    
    campaigns = aria.get_active_campaigns_widget_data(limit=3)
    print(f"Active campaigns: {len(campaigns)}")
    for campaign in campaigns:
        print(f"\n{campaign['name']}")
        print(f"  Actor: {campaign['threat_actor']}")
        print(f"  Duration: {campaign['duration_days']} days")
        print(f"  Status: {campaign['status']}")
    
    # Example 6: Create alert notification
    print("\n=== Alert Notification ===\n")
    
    alert = aria.create_alert_notification(
        priority=AlertPriority.CRITICAL,
        title="Critical Zero-Day Vulnerability Detected",
        message="New zero-day affecting Windows systems detected in the wild",
        action_url="/vulnerabilities/CVE-2025-12345",
        auto_dismiss_seconds=None  # Must be manually dismissed
    )
    print(f"Alert ID: {alert.alert_id}")
    print(f"Priority: {alert.priority.value.upper()}")
    print(f"Title: {alert.title}")
    print(f"Dismissible: {alert.dismissible}")
    
    # Example 7: Get complete dashboard summary
    print("\n=== Complete Dashboard Summary ===\n")
    
    summary = aria.get_dashboard_summary()
    print(f"Risk Score: {summary['risk_score']['score']}/100")
    print(f"Threat Feed Items: {len(summary['threat_feed'])}")
    print(f"Active Campaigns: {len(summary['active_campaigns'])}")
    print(f"Critical Vulnerabilities: {len(summary['critical_vulnerabilities'])}")
    print(f"Trend Chart Data Points: {len(summary['trend_chart']['labels'])}")
    print(f"Updated: {summary['timestamp']}")
    
    print("\n✓ ARIA Dashboard Integration operational!")
