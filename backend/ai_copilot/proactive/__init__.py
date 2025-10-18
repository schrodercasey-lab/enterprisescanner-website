"""
Jupiter AI Copilot - Proactive Intelligence Module
Automated threat monitoring and vulnerability alerting
"""

from .threat_feeds import (
    JupiterThreatFeeds,
    ThreatFeed,
    ThreatFeedType,
    Vulnerability,
    VulnerabilitySeverity,
    ExploitStatus,
    ThreatIntelligence
)

from .proactive_alerts import (
    JupiterProactiveAlerts,
    Alert,
    AlertType,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    AlertRule
)

__all__ = [
    'JupiterThreatFeeds',
    'ThreatFeed',
    'ThreatFeedType',
    'Vulnerability',
    'VulnerabilitySeverity',
    'ExploitStatus',
    'ThreatIntelligence',
    'JupiterProactiveAlerts',
    'Alert',
    'AlertType',
    'AlertSeverity',
    'AlertStatus',
    'NotificationChannel',
    'AlertRule'
]
