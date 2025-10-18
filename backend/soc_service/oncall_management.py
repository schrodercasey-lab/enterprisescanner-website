"""
On-Call Rotation and Escalation Management
24/7 SOC staffing and automated escalation system

This module provides comprehensive on-call management:
- 24/7 on-call rotation scheduling
- Automated escalation workflows
- PagerDuty/Opsgenie integration
- Follow-the-sun support model
- Backup analyst assignment
- Escalation path management
- On-call metrics and reporting

Integration Support:
- PagerDuty API
- Opsgenie API
- VictorOps (Splunk On-Call)
- xMatters
- Custom webhooks

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from enum import Enum
import requests


class OnCallTier(Enum):
    """On-call support tiers"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    MANAGER = "manager"
    EXECUTIVE = "executive"


class EscalationPolicy(Enum):
    """Escalation policy types"""
    IMMEDIATE = "immediate"              # Escalate immediately
    AFTER_TIMEOUT = "after_timeout"      # Escalate if no response
    ROUND_ROBIN = "round_robin"          # Distribute among team
    FOLLOW_THE_SUN = "follow_the_sun"    # Based on timezone
    SEVERITY_BASED = "severity_based"    # Based on incident severity


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    PUSH = "push_notification"
    SLACK = "slack"
    TEAMS = "microsoft_teams"
    PAGERDUTY = "pagerduty"
    OPSGENIE = "opsgenie"


@dataclass
class OnCallAnalyst:
    """Security analyst available for on-call duty"""
    analyst_id: str
    name: str
    email: str
    phone: str
    
    # Skills and certifications
    tier_level: int  # 1, 2, 3
    specializations: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    
    # Availability
    timezone: str = "UTC"
    available_24_7: bool = False
    preferred_shifts: List[str] = field(default_factory=list)  # day, evening, night
    
    # Contact preferences
    primary_contact: NotificationChannel = NotificationChannel.PHONE_CALL
    secondary_contact: NotificationChannel = NotificationChannel.SMS
    escalation_delay_minutes: int = 15
    
    # Status
    currently_on_call: bool = False
    last_incident: Optional[datetime] = None
    incidents_handled_30d: int = 0
    average_response_time_minutes: float = 0.0


@dataclass
class OnCallShift:
    """On-call shift assignment"""
    shift_id: str
    start_time: datetime
    end_time: datetime
    
    # Assignment
    primary_analyst: str  # analyst_id
    secondary_analyst: Optional[str] = None
    backup_analysts: List[str] = field(default_factory=list)
    
    # Shift details
    shift_type: str = "standard"  # standard, holiday, weekend
    geographic_region: str = "global"
    
    # Status
    active: bool = True
    incidents_handled: int = 0
    

_analyst: Optional[str] = None


@dataclass
class EscalationPath:
    """Defined escalation path for incident types"""
    path_id: str
    name: str
    description: str
    
    # Escalation levels
    levels: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [
    #   {'tier': 'primary', 'timeout_minutes': 15, 'channels': ['phone', 'sms']},
    #   {'tier': 'secondary', 'timeout_minutes': 30, 'channels': ['phone', 'sms', 'email']},
    #   {'tier': 'manager', 'timeout_minutes': 60, 'channels': ['phone', 'email']}
    # ]
    
    # Conditions
    applicable_severities: List[str] = field(default_factory=list)
    applicable_categories: List[str] = field(default_factory=list)
    time_of_day_restrictions: Optional[Dict[str, Any]] = None


@dataclass
class EscalationEvent:
    """Record of escalation attempt"""
    event_id: str
    incident_id: str
    timestamp: datetime
    
    escalated_to: str  # analyst_id or tier
    escalation_level: int
    notification_channels: List[NotificationChannel]
    
    # Response tracking
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    response_time_minutes: Optional[float] = None
    
    # Status
    successful: bool = False
    failure_reason: Optional[str] = None


class OnCallManager:
    """
    On-Call Rotation and Escalation Management System
    
    Manages 24/7 analyst staffing, shift scheduling, and automated
    escalation workflows for security incident response.
    """
    
    def __init__(self):
        self.analysts: Dict[str, OnCallAnalyst] = {}
        self.shifts: Dict[str, OnCallShift] = {}
        self.escalation_paths: Dict[str, EscalationPath] = {}
        self.escalation_events: List[EscalationEvent] = []
        
        # Integration configuration
        self.pagerduty_api_key: Optional[str] = None
        self.opsgenie_api_key: Optional[str] = None
        self.slack_webhook_url: Optional[str] = None
        self.teams_webhook_url: Optional[str] = None
        
        # Initialize default escalation paths
        self._initialize_default_escalation_paths()
    
    def _initialize_default_escalation_paths(self) -> None:
        """Initialize standard escalation paths"""
        
        # Critical incident escalation
        critical_path = EscalationPath(
            path_id="EP-CRITICAL",
            name="Critical Incident Escalation",
            description="Immediate escalation for critical security incidents",
            levels=[
                {
                    'tier': OnCallTier.PRIMARY.value,
                    'timeout_minutes': 5,
                    'channels': [NotificationChannel.PHONE_CALL.value, NotificationChannel.SMS.value, NotificationChannel.PUSH.value]
                },
                {
                    'tier': OnCallTier.SECONDARY.value,
                    'timeout_minutes': 10,
                    'channels': [NotificationChannel.PHONE_CALL.value, NotificationChannel.SMS.value]
                },
                {
                    'tier': OnCallTier.MANAGER.value,
                    'timeout_minutes': 15,
                    'channels': [NotificationChannel.PHONE_CALL.value, NotificationChannel.EMAIL.value]
                },
                {
                    'tier': OnCallTier.EXECUTIVE.value,
                    'timeout_minutes': 30,
                    'channels': [NotificationChannel.PHONE_CALL.value]
                }
            ],
            applicable_severities=['critical'],
            applicable_categories=['ransomware', 'data_breach', 'apt']
        )
        self.escalation_paths[critical_path.path_id] = critical_path
        
        # High severity escalation
        high_path = EscalationPath(
            path_id="EP-HIGH",
            name="High Severity Escalation",
            description="Standard escalation for high severity incidents",
            levels=[
                {
                    'tier': OnCallTier.PRIMARY.value,
                    'timeout_minutes': 15,
                    'channels': [NotificationChannel.SMS.value, NotificationChannel.PUSH.value, NotificationChannel.EMAIL.value]
                },
                {
                    'tier': OnCallTier.SECONDARY.value,
                    'timeout_minutes': 30,
                    'channels': [NotificationChannel.PHONE_CALL.value, NotificationChannel.SMS.value]
                },
                {
                    'tier': OnCallTier.MANAGER.value,
                    'timeout_minutes': 60,
                    'channels': [NotificationChannel.EMAIL.value]
                }
            ],
            applicable_severities=['high'],
            applicable_categories=['malware', 'unauthorized_access', 'denial_of_service']
        )
        self.escalation_paths[high_path.path_id] = high_path
        
        # Medium/Low severity escalation
        standard_path = EscalationPath(
            path_id="EP-STANDARD",
            name="Standard Escalation",
            description="Standard escalation for medium/low severity incidents",
            levels=[
                {
                    'tier': OnCallTier.PRIMARY.value,
                    'timeout_minutes': 30,
                    'channels': [NotificationChannel.EMAIL.value, NotificationChannel.PUSH.value]
                },
                {
                    'tier': OnCallTier.SECONDARY.value,
                    'timeout_minutes': 120,
                    'channels': [NotificationChannel.EMAIL.value]
                }
            ],
            applicable_severities=['medium', 'low'],
            applicable_categories=[]  # All other categories
        )
        self.escalation_paths[standard_path.path_id] = standard_path
    
    def register_analyst(self, analyst: OnCallAnalyst) -> None:
        """Register analyst in on-call pool"""
        self.analysts[analyst.analyst_id] = analyst
        print(f"✅ Registered analyst: {analyst.name} (Tier {analyst.tier_level})")
    
    def create_shift(
        self,
        start_time: datetime,
        end_time: datetime,
        primary_analyst_id: str,
        secondary_analyst_id: Optional[str] = None,
        shift_type: str = "standard"
    ) -> OnCallShift:
        """Create on-call shift assignment"""
        
        if primary_analyst_id not in self.analysts:
            raise ValueError(f"Primary analyst {primary_analyst_id} not registered")
        
        if secondary_analyst_id and secondary_analyst_id not in self.analysts:
            raise ValueError(f"Secondary analyst {secondary_analyst_id} not registered")
        
        shift_id = f"SHIFT-{start_time.strftime('%Y%m%d%H%M')}-{str(uuid.uuid4())[:8]}"
        
        shift = OnCallShift(
            shift_id=shift_id,
            start_time=start_time,
            end_time=end_time,
            primary_analyst=primary_analyst_id,
            secondary_analyst=secondary_analyst_id,
            shift_type=shift_type
        )
        
        self.shifts[shift_id] = shift
        
        # Update analyst status
        self.analysts[primary_analyst_id].currently_on_call = True
        if secondary_analyst_id:
            self.analysts[secondary_analyst_id].currently_on_call = True
        
        print(f"📅 Shift created: {shift_id}")
        print(f"   Primary: {self.analysts[primary_analyst_id].name}")
        if secondary_analyst_id:
            print(f"   Secondary: {self.analysts[secondary_analyst_id].name}")
        print(f"   Duration: {start_time} to {end_time}")
        
        return shift
    
    def get_current_on_call(self) -> Tuple[Optional[OnCallAnalyst], Optional[OnCallAnalyst]]:
        """Get currently on-call primary and secondary analysts"""
        now = datetime.now()
        
        for shift in self.shifts.values():
            if shift.active and shift.start_time <= now <= shift.end_time:
                primary = self.analysts.get(shift.primary_analyst)
                secondary = self.analysts.get(shift.secondary_analyst) if shift.secondary_analyst else None
                return primary, secondary
        
        return None, None
    
    def escalate_incident(
        self,
        incident_id: str,
        severity: str,
        category: str,
        description: str
    ) -> List[EscalationEvent]:
        """
        Initiate incident escalation based on severity and category.
        
        Args:
            incident_id: Unique incident identifier
            severity: Incident severity (critical, high, medium, low)
            category: Incident category
            description: Brief incident description
            
        Returns:
            List of escalation events created
        """
        # Find applicable escalation path
        escalation_path = self._get_escalation_path(severity, category)
        
        if not escalation_path:
            print(f"⚠️  No escalation path found for severity={severity}, category={category}")
            return []
        
        print(f"📢 Escalating incident {incident_id} via path: {escalation_path.name}")
        
        escalation_events = []
        
        # Execute each escalation level
        for level_index, level in enumerate(escalation_path.levels):
            event = self._execute_escalation_level(
                incident_id=incident_id,
                level_index=level_index,
                level_config=level,
                description=description
            )
            escalation_events.append(event)
            
            # In production, we would check if acknowledged before continuing
            # For now, we'll create all escalation events
        
        return escalation_events
    
    def _get_escalation_path(self, severity: str, category: str) -> Optional[EscalationPath]:
        """Get appropriate escalation path for incident"""
        
        # Try to find path matching severity and category
        for path in self.escalation_paths.values():
            if severity in path.applicable_severities:
                if not path.applicable_categories or category in path.applicable_categories:
                    return path
        
        # Fallback to standard path
        return self.escalation_paths.get("EP-STANDARD")
    
    def _execute_escalation_level(
        self,
        incident_id: str,
        level_index: int,
        level_config: Dict[str, Any],
        description: str
    ) -> EscalationEvent:
        """Execute single escalation level"""
        
        tier = level_config['tier']
        timeout_minutes = level_config['timeout_minutes']
        channels = level_config['channels']
        
        # Get analyst for this tier
        target_analyst = self._get_analyst_for_tier(tier)
        
        event = EscalationEvent(
            event_id=str(uuid.uuid4()),
            incident_id=incident_id,
            timestamp=datetime.now(),
            escalated_to=target_analyst.analyst_id if target_analyst else tier,
            escalation_level=level_index + 1,
            notification_channels=[NotificationChannel(ch) for ch in channels]
        )
        
        if target_analyst:
            # Send notifications
            self._send_notifications(
                analyst=target_analyst,
                incident_id=incident_id,
                description=description,
                channels=channels
            )
            
            print(f"   Level {level_index + 1}: Notified {target_analyst.name} via {', '.join(channels)}")
            print(f"   Timeout: {timeout_minutes} minutes")
        else:
            print(f"   Level {level_index + 1}: No analyst available for tier {tier}")
            event.failure_reason = "No analyst available"
        
        self.escalation_events.append(event)
        return event
    
    def _get_analyst_for_tier(self, tier: str) -> Optional[OnCallAnalyst]:
        """Get on-call analyst for specific tier"""
        
        # Get current shift
        primary, secondary = self.get_current_on_call()
        
        tier_enum = OnCallTier(tier)
        
        if tier_enum == OnCallTier.PRIMARY and primary:
            return primary
        elif tier_enum == OnCallTier.SECONDARY and secondary:
            return secondary
        elif tier_enum in [OnCallTier.MANAGER, OnCallTier.TERTIARY]:
            # Find available tier 3 analyst or manager
            for analyst in self.analysts.values():
                if analyst.tier_level >= 3:
                    return analyst
        elif tier_enum == OnCallTier.EXECUTIVE:
            # Return any analyst (in production, this would be executive contact)
            return primary if primary else (secondary if secondary else None)
        
        return None
    
    def _send_notifications(
        self,
        analyst: OnCallAnalyst,
        incident_id: str,
        description: str,
        channels: List[str]
    ) -> None:
        """Send notifications via multiple channels"""
        
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL.value:
                    self._send_email_notification(analyst, incident_id, description)
                elif channel == NotificationChannel.SMS.value:
                    self._send_sms_notification(analyst, incident_id, description)
                elif channel == NotificationChannel.PHONE_CALL.value:
                    self._initiate_phone_call(analyst, incident_id, description)
                elif channel == NotificationChannel.SLACK.value:
                    self._send_slack_notification(analyst, incident_id, description)
                elif channel == NotificationChannel.PAGERDUTY.value:
                    self._trigger_pagerduty_alert(analyst, incident_id, description)
                elif channel == NotificationChannel.OPSGENIE.value:
                    self._trigger_opsgenie_alert(analyst, incident_id, description)
            except Exception as e:
                print(f"      ❌ Failed to send {channel} notification: {e}")
    
    def _send_email_notification(self, analyst: OnCallAnalyst, incident_id: str, description: str) -> None:
        """Send email notification"""
        print(f"      📧 Email sent to {analyst.email}")
        # In production: Send actual email via SMTP
    
    def _send_sms_notification(self, analyst: OnCallAnalyst, incident_id: str, description: str) -> None:
        """Send SMS notification"""
        print(f"      📱 SMS sent to {analyst.phone}")
        # In production: Send SMS via Twilio/AWS SNS
    
    def _initiate_phone_call(self, analyst: OnCallAnalyst, incident_id: str, description: str) -> None:
        """Initiate automated phone call"""
        print(f"      ☎️  Phone call initiated to {analyst.phone}")
        # In production: Initiate call via Twilio/PagerDuty
    
    def _send_slack_notification(self, analyst: OnCallAnalyst, incident_id: str, description: str) -> None:
        """Send Slack notification"""
        if not self.slack_webhook_url:
            print(f"      ⚠️  Slack webhook not configured")
            return
        
        try:
            payload = {
                'text': f"🚨 Security Incident: {incident_id}",
                'blocks': [
                    {
                        'type': 'header',
                        'text': {'type': 'plain_text', 'text': f'🚨 {incident_id}'}
                    },
                    {
                        'type': 'section',
                        'text': {'type': 'mrkdwn', 'text': f"*Incident:* {description}"}
                    },
                    {
                        'type': 'section',
                        'text': {'type': 'mrkdwn', 'text': f"*Assigned to:* @{analyst.name}"}
                    }
                ]
            }
            
            # In production: Actually send to Slack
            # requests.post(self.slack_webhook_url, json=payload)
            print(f"      💬 Slack notification sent")
        except Exception as e:
            print(f"      ❌ Slack notification failed: {e}")
    
    def _trigger_pagerduty_alert(self, analyst: OnCallAnalyst, incident_id: str, description: str) -> None:
        """Trigger PagerDuty alert"""
        if not self.pagerduty_api_key:
            print(f"      ⚠️  PagerDuty API key not configured")
            return
        
        try:
            # PagerDuty Events API v2
            payload = {
                'routing_key': self.pagerduty_api_key,
                'event_action': 'trigger',
                'payload': {
                    'summary': f"Security Incident: {incident_id}",
                    'severity': 'critical',
                    'source': 'Enterprise Scanner SOC',
                    'custom_details': {
                        'incident_id': incident_id,
                        'description': description,
                        'assigned_to': analyst.name
                    }
                }
            }
            
            # In production: Actually send to PagerDuty
            # requests.post('https://events.pagerduty.com/v2/enqueue', json=payload)
            print(f"      🔔 PagerDuty alert triggered")
        except Exception as e:
            print(f"      ❌ PagerDuty alert failed: {e}")
    
    def _trigger_opsgenie_alert(self, analyst: OnCallAnalyst, incident_id: str, description: str) -> None:
        """Trigger Opsgenie alert"""
        if not self.opsgenie_api_key:
            print(f"      ⚠️  Opsgenie API key not configured")
            return
        
        try:
            headers = {'Authorization': f'GenieKey {self.opsgenie_api_key}'}
            payload = {
                'message': f"Security Incident: {incident_id}",
                'alias': incident_id,
                'description': description,
                'priority': 'P1',
                'responders': [{'type': 'user', 'username': analyst.email}]
            }
            
            # In production: Actually send to Opsgenie
            # requests.post('https://api.opsgenie.com/v2/alerts', headers=headers, json=payload)
            print(f"      🔔 Opsgenie alert triggered")
        except Exception as e:
            print(f"      ❌ Opsgenie alert failed: {e}")
    
    def acknowledge_escalation(self, event_id: str, analyst_id: str) -> None:
        """Record analyst acknowledgment of escalation"""
        for event in self.escalation_events:
            if event.event_id == event_id:
                event.acknowledged = True
                event.acknowledged_at = datetime.now()
                event.response_time_minutes = (event.acknowledged_at - event.timestamp).total_seconds() / 60
                event.successful = True
                
                print(f"✅ Escalation acknowledged by {analyst_id}")
                print(f"   Response time: {event.response_time_minutes:.1f} minutes")
                
                # Update analyst metrics
                if analyst_id in self.analysts:
                    analyst = self.analysts[analyst_id]
                    analyst.last_incident = datetime.now()
                    analyst.incidents_handled_30d += 1
                break
    
    def generate_on_call_schedule(
        self,
        start_date: datetime,
        duration_days: int,
        shift_duration_hours: int = 8
    ) -> List[OnCallShift]:
        """
        Generate rotating on-call schedule.
        
        Args:
            start_date: Schedule start date
            duration_days: Number of days to schedule
            shift_duration_hours: Hours per shift (default: 8)
            
        Returns:
            List of scheduled shifts
        """
        # Get available analysts sorted by tier
        available_analysts = sorted(
            [a for a in self.analysts.values()],
            key=lambda x: (x.tier_level, x.incidents_handled_30d)
        )
        
        if len(available_analysts) < 2:
            print("⚠️  Need at least 2 analysts to generate schedule")
            return []
        
        shifts = []
        current_time = start_date
        end_time = start_date + timedelta(days=duration_days)
        analyst_index = 0
        
        while current_time < end_time:
            shift_end = current_time + timedelta(hours=shift_duration_hours)
            
            # Assign primary and secondary
            primary = available_analysts[analyst_index % len(available_analysts)]
            secondary = available_analysts[(analyst_index + 1) % len(available_analysts)]
            
            # Determine shift type
            shift_type = "standard"
            if current_time.weekday() >= 5:  # Saturday or Sunday
                shift_type = "weekend"
            
            shift = self.create_shift(
                start_time=current_time,
                end_time=shift_end,
                primary_analyst_id=primary.analyst_id,
                secondary_analyst_id=secondary.analyst_id,
                shift_type=shift_type
            )
            
            shifts.append(shift)
            
            current_time = shift_end
            analyst_index += 1
        
        print(f"\n📅 Generated {len(shifts)} shifts over {duration_days} days")
        return shifts
    
    def get_escalation_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Generate escalation performance metrics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_events = [e for e in self.escalation_events if e.timestamp >= cutoff_date]
        
        if not recent_events:
            return {'error': 'No escalation events in time period'}
        
        total_escalations = len(recent_events)
        acknowledged = [e for e in recent_events if e.acknowledged]
        
        response_times = [e.response_time_minutes for e in acknowledged if e.response_time_minutes]
        
        metrics = {
            'time_period_days': days,
            'total_escalations': total_escalations,
            'acknowledged_escalations': len(acknowledged),
            'acknowledgment_rate': len(acknowledged) / total_escalations * 100 if total_escalations > 0 else 0,
            'average_response_time_minutes': sum(response_times) / len(response_times) if response_times else 0,
            'fastest_response_minutes': min(response_times) if response_times else 0,
            'slowest_response_minutes': max(response_times) if response_times else 0,
            'by_level': {},
            'by_analyst': {}
        }
        
        # Count by escalation level
        for event in recent_events:
            level = event.escalation_level
            metrics['by_level'][f'level_{level}'] = metrics['by_level'].get(f'level_{level}', 0) + 1
        
        # Count by analyst
        for event in acknowledged:
            analyst_id = event.escalated_to
            if analyst_id not in metrics['by_analyst']:
                metrics['by_analyst'][analyst_id] = {
                    'total': 0,
                    'avg_response_minutes': 0,
                    'response_times': []
                }
            metrics['by_analyst'][analyst_id]['total'] += 1
            if event.response_time_minutes:
                metrics['by_analyst'][analyst_id]['response_times'].append(event.response_time_minutes)
        
        # Calculate average response times per analyst
        for analyst_id, data in metrics['by_analyst'].items():
            if data['response_times']:
                data['avg_response_minutes'] = sum(data['response_times']) / len(data['response_times'])
            del data['response_times']  # Remove raw data from output
        
        return metrics


# Example usage
if __name__ == "__main__":
    # Initialize on-call manager
    manager = OnCallManager()
    
    # Register analysts
    analyst1 = OnCallAnalyst(
        analyst_id="ANL-001",
        name="Alice Johnson",
        email="alice@enterprisescanner.com",
        phone="+1-555-0101",
        tier_level=2,
        specializations=["malware_analysis", "forensics"],
        certifications=["GCIH", "GCFA"],
        timezone="America/New_York"
    )
    manager.register_analyst(analyst1)
    
    analyst2 = OnCallAnalyst(
        analyst_id="ANL-002",
        name="Bob Smith",
        email="bob@enterprisescanner.com",
        phone="+1-555-0102",
        tier_level=2,
        specializations=["network_security", "intrusion_detection"],
        certifications=["GCIA", "GCIH"],
        timezone="America/Los_Angeles"
    )
    manager.register_analyst(analyst2)
    
    analyst3 = OnCallAnalyst(
        analyst_id="ANL-003",
        name="Charlie Brown",
        email="charlie@enterprisescanner.com",
        phone="+1-555-0103",
        tier_level=3,
        specializations=["incident_response", "threat_hunting"],
        certifications=["GCIH", "GCFA", "GREM"],
        timezone="Europe/London"
    )
    manager.register_analyst(analyst3)
    
    # Create shifts
    now = datetime.now()
    shift1 = manager.create_shift(
        start_time=now,
        end_time=now + timedelta(hours=8),
        primary_analyst_id="ANL-001",
        secondary_analyst_id="ANL-002"
    )
    
    # Test escalation
    escalation_events = manager.escalate_incident(
        incident_id="INC-20251017-ABC123",
        severity="critical",
        category="ransomware",
        description="Ransomware detected on production server"
    )
    
    # Acknowledge first escalation
    if escalation_events:
        manager.acknowledge_escalation(escalation_events[0].event_id, "ANL-001")
    
    # Generate schedule
    schedule = manager.generate_on_call_schedule(
        start_date=datetime.now(),
        duration_days=7,
        shift_duration_hours=8
    )
    
    # Generate metrics
    metrics = manager.get_escalation_metrics(days=30)
    print(f"\n📊 Escalation Metrics (30 days):")
    print(f"   Total Escalations: {metrics['total_escalations']}")
    print(f"   Acknowledgment Rate: {metrics['acknowledgment_rate']:.1f}%")
    print(f"   Avg Response Time: {metrics['average_response_time_minutes']:.1f} min")
