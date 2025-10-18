"""
War Room Collaboration and Coordination System
Real-time incident response collaboration platform

This module provides virtual war room capabilities for coordinating
incident response across distributed security teams:

- Slack/Teams channel creation and management
- Video conference bridge setup (Zoom/WebEx)
- Shared documentation (Google Docs/Confluence)
- Real-time status updates and broadcasting
- Command execution via chat interfaces
- Stakeholder management and notifications
- Crisis communication workflows

Integration Support:
- Slack API
- Microsoft Teams API
- Zoom API
- WebEx API
- Google Workspace API
- Atlassian Confluence API

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import requests


class WarRoomStatus(Enum):
    """War room operational status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    STANDBY = "standby"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class ParticipantRole(Enum):
    """Participant roles in war room"""
    INCIDENT_COMMANDER = "incident_commander"
    LEAD_ANALYST = "lead_analyst"
    ANALYST = "analyst"
    SUBJECT_MATTER_EXPERT = "sme"
    EXECUTIVE = "executive"
    OBSERVER = "observer"
    SCRIBE = "scribe"


class UpdatePriority(Enum):
    """Status update priority levels"""
    CRITICAL = "critical"    # Immediate broadcast to all
    HIGH = "high"            # Important updates
    NORMAL = "normal"        # Standard updates
    LOW = "low"              # Informational only


@dataclass
class WarRoomParticipant:
    """War room participant"""
    user_id: str
    name: str
    email: str
    role: ParticipantRole
    
    # Contact
    phone: Optional[str] = None
    slack_id: Optional[str] = None
    teams_id: Optional[str] = None
    
    # Status
    joined_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class WarRoomChannel:
    """Communication channel"""
    channel_id: str
    platform: str  # slack, teams, discord
    channel_name: str
    channel_url: str
    webhook_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WarRoomBridge:
    """Video/audio conference bridge"""
    bridge_id: str
    platform: str  # zoom, webex, teams, google_meet
    meeting_url: str
    meeting_id: str
    passcode: Optional[str] = None
    dial_in_numbers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WarRoomDocument:
    """Shared documentation"""
    document_id: str
    title: str
    platform: str  # google_docs, confluence, sharepoint
    document_url: str
    document_type: str  # timeline, evidence, notes, playbook
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)


@dataclass
class StatusUpdate:
    """War room status update"""
    update_id: str
    timestamp: datetime
    author: str  # user_id
    priority: UpdatePriority
    message: str
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    broadcast_sent: bool = False


@dataclass
class WarRoom:
    """Virtual war room for incident coordination"""
    room_id: str
    incident_id: str
    name: str
    created_at: datetime
    
    # Status
    status: WarRoomStatus = WarRoomStatus.INITIALIZING
    severity: str = "high"
    
    # Participants
    participants: List[WarRoomParticipant] = field(default_factory=list)
    incident_commander: Optional[str] = None  # user_id
    
    # Communication channels
    channels: List[WarRoomChannel] = field(default_factory=list)
    bridges: List[WarRoomBridge] = field(default_factory=list)
    documents: List[WarRoomDocument] = field(default_factory=list)
    
    # Updates
    status_updates: List[StatusUpdate] = field(default_factory=list)
    
    # Metrics
    participant_count: int = 0
    total_updates: int = 0
    duration_minutes: float = 0.0


class WarRoomManager:
    """
    War Room Collaboration and Coordination System
    
    Manages virtual war rooms for coordinating incident response across
    distributed teams with real-time communication and collaboration tools.
    """
    
    def __init__(self):
        self.war_rooms: Dict[str, WarRoom] = {}
        
        # Integration credentials
        self.slack_bot_token: Optional[str] = None
        self.teams_webhook_url: Optional[str] = None
        self.zoom_api_key: Optional[str] = None
        self.zoom_api_secret: Optional[str] = None
        self.webex_access_token: Optional[str] = None
        self.google_credentials: Optional[Dict] = None
        self.confluence_api_token: Optional[str] = None
    
    def create_war_room(
        self,
        incident_id: str,
        severity: str,
        name: Optional[str] = None,
        incident_commander_id: Optional[str] = None
    ) -> WarRoom:
        """
        Create new war room for incident coordination.
        
        Args:
            incident_id: Associated incident ID
            severity: Incident severity (critical, high, medium, low)
            name: Optional war room name
            incident_commander_id: Optional IC user ID
            
        Returns:
            Created WarRoom object
        """
        room_id = f"WAR-{datetime.now().strftime('%Y%m%d%H%M')}-{str(uuid.uuid4())[:8]}"
        
        if not name:
            name = f"Incident {incident_id} War Room"
        
        war_room = WarRoom(
            room_id=room_id,
            incident_id=incident_id,
            name=name,
            created_at=datetime.now(),
            severity=severity,
            incident_commander=incident_commander_id
        )
        
        self.war_rooms[room_id] = war_room
        
        print(f"🚨 War Room Created: {room_id}")
        print(f"   Incident: {incident_id}")
        print(f"   Severity: {severity.upper()}")
        print(f"   Name: {name}")
        
        # Auto-provision communication channels
        self._provision_communication_channels(war_room)
        
        return war_room
    
    def _provision_communication_channels(self, war_room: WarRoom) -> None:
        """Automatically provision communication channels"""
        
        # Create Slack channel
        if self.slack_bot_token:
            slack_channel = self._create_slack_channel(war_room)
            if slack_channel:
                war_room.channels.append(slack_channel)
        
        # Create Teams channel
        if self.teams_webhook_url:
            teams_channel = self._create_teams_channel(war_room)
            if teams_channel:
                war_room.channels.append(teams_channel)
        
        # Create video bridge
        if self.zoom_api_key:
            zoom_bridge = self._create_zoom_bridge(war_room)
            if zoom_bridge:
                war_room.bridges.append(zoom_bridge)
        elif self.webex_access_token:
            webex_bridge = self._create_webex_bridge(war_room)
            if webex_bridge:
                war_room.bridges.append(webex_bridge)
        
        # Create shared documentation
        if self.google_credentials:
            timeline_doc = self._create_google_doc(war_room, "timeline")
            evidence_doc = self._create_google_doc(war_room, "evidence")
            if timeline_doc:
                war_room.documents.append(timeline_doc)
            if evidence_doc:
                war_room.documents.append(evidence_doc)
    
    def _create_slack_channel(self, war_room: WarRoom) -> Optional[WarRoomChannel]:
        """Create Slack channel for war room"""
        try:
            channel_name = f"incident-{war_room.incident_id.lower()}"
            channel_name = channel_name.replace('_', '-')[:80]  # Slack name limits
            
            # Slack API: conversations.create
            headers = {
                'Authorization': f'Bearer {self.slack_bot_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'name': channel_name,
                'is_private': True,  # Private channel for security
                'team_id': None  # Use default workspace
            }
            
            # In production: Actually call Slack API
            # response = requests.post(
            #     'https://slack.com/api/conversations.create',
            #     headers=headers,
            #     json=payload
            # )
            # channel_data = response.json()
            
            # Simulated response
            channel_data = {
                'ok': True,
                'channel': {
                    'id': f'C{str(uuid.uuid4()).replace("-", "")[:10].upper()}',
                    'name': channel_name
                }
            }
            
            if channel_data.get('ok'):
                channel_id = channel_data['channel']['id']
                channel_url = f"https://app.slack.com/client/T000000/{channel_id}"
                
                # Set channel topic
                self._set_slack_channel_topic(
                    channel_id,
                    f"🚨 {war_room.name} | Severity: {war_room.severity.upper()}"
                )
                
                # Post welcome message
                self._post_slack_message(
                    channel_id,
                    f"Welcome to the {war_room.name} war room. This channel is for coordinating response to incident {war_room.incident_id}."
                )
                
                channel = WarRoomChannel(
                    channel_id=channel_id,
                    platform="slack",
                    channel_name=channel_name,
                    channel_url=channel_url
                )
                
                print(f"   ✅ Slack channel created: #{channel_name}")
                return channel
            else:
                print(f"   ❌ Failed to create Slack channel: {channel_data.get('error')}")
                return None
                
        except Exception as e:
            print(f"   ❌ Slack channel creation error: {e}")
            return None
    
    def _set_slack_channel_topic(self, channel_id: str, topic: str) -> None:
        """Set Slack channel topic"""
        # In production: conversations.setTopic
        pass
    
    def _post_slack_message(self, channel_id: str, text: str, blocks: Optional[List] = None) -> None:
        """Post message to Slack channel"""
        # In production: chat.postMessage
        pass
    
    def _create_teams_channel(self, war_room: WarRoom) -> Optional[WarRoomChannel]:
        """Create Microsoft Teams channel"""
        try:
            channel_name = f"Incident {war_room.incident_id}"
            
            # Teams API: Create channel in team
            # In production: POST /teams/{team-id}/channels
            
            # Simulated response
            channel_id = str(uuid.uuid4())
            channel_url = f"https://teams.microsoft.com/l/channel/{channel_id}"
            
            channel = WarRoomChannel(
                channel_id=channel_id,
                platform="teams",
                channel_name=channel_name,
                channel_url=channel_url,
                webhook_url=self.teams_webhook_url
            )
            
            # Post welcome message
            self._post_teams_message(
                channel,
                f"🚨 {war_room.name} | Severity: {war_room.severity.upper()}"
            )
            
            print(f"   ✅ Teams channel created: {channel_name}")
            return channel
            
        except Exception as e:
            print(f"   ❌ Teams channel creation error: {e}")
            return None
    
    def _post_teams_message(self, channel: WarRoomChannel, text: str) -> None:
        """Post message to Teams channel"""
        if not channel.webhook_url:
            return
        
        try:
            payload = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'summary': 'War Room Update',
                'themeColor': 'D70000',
                'title': '🚨 War Room Active',
                'text': text
            }
            
            # In production: Actually post to Teams
            # requests.post(channel.webhook_url, json=payload)
            
        except Exception as e:
            print(f"      Teams message error: {e}")
    
    def _create_zoom_bridge(self, war_room: WarRoom) -> Optional[WarRoomBridge]:
        """Create Zoom meeting bridge"""
        try:
            # Zoom API: Create meeting
            # In production: POST /users/{userId}/meetings
            
            # Simulated response
            meeting_id = f"{str(uuid.uuid4().int)[:11]}"
            meeting_url = f"https://zoom.us/j/{meeting_id}"
            passcode = f"{str(uuid.uuid4().int)[:6]}"
            
            bridge = WarRoomBridge(
                bridge_id=str(uuid.uuid4()),
                platform="zoom",
                meeting_url=meeting_url,
                meeting_id=meeting_id,
                passcode=passcode,
                dial_in_numbers=["+1-555-ZOOM-123"]
            )
            
            print(f"   ✅ Zoom bridge created: {meeting_id}")
            print(f"      URL: {meeting_url}")
            print(f"      Passcode: {passcode}")
            
            return bridge
            
        except Exception as e:
            print(f"   ❌ Zoom bridge creation error: {e}")
            return None
    
    def _create_webex_bridge(self, war_room: WarRoom) -> Optional[WarRoomBridge]:
        """Create WebEx meeting bridge"""
        try:
            # WebEx API: Create meeting
            
            # Simulated response
            meeting_id = str(uuid.uuid4())
            meeting_url = f"https://webex.com/meet/{meeting_id}"
            
            bridge = WarRoomBridge(
                bridge_id=str(uuid.uuid4()),
                platform="webex",
                meeting_url=meeting_url,
                meeting_id=meeting_id
            )
            
            print(f"   ✅ WebEx bridge created: {meeting_id}")
            
            return bridge
            
        except Exception as e:
            print(f"   ❌ WebEx bridge creation error: {e}")
            return None
    
    def _create_google_doc(self, war_room: WarRoom, doc_type: str) -> Optional[WarRoomDocument]:
        """Create Google Doc for collaboration"""
        try:
            # Google Docs API: Create document
            
            # Simulated response
            document_id = str(uuid.uuid4())
            title = f"{war_room.name} - {doc_type.title()}"
            document_url = f"https://docs.google.com/document/d/{document_id}"
            
            document = WarRoomDocument(
                document_id=document_id,
                title=title,
                platform="google_docs",
                document_url=document_url,
                document_type=doc_type,
                created_by="system"
            )
            
            print(f"   ✅ Google Doc created: {title}")
            
            return document
            
        except Exception as e:
            print(f"   ❌ Google Doc creation error: {e}")
            return None
    
    def add_participant(
        self,
        room_id: str,
        user_id: str,
        name: str,
        email: str,
        role: ParticipantRole,
        phone: Optional[str] = None
    ) -> Optional[WarRoomParticipant]:
        """Add participant to war room"""
        
        if room_id not in self.war_rooms:
            print(f"❌ War room {room_id} not found")
            return None
        
        war_room = self.war_rooms[room_id]
        
        # Check if already participant
        for p in war_room.participants:
            if p.user_id == user_id:
                print(f"⚠️  {name} is already a participant")
                return p
        
        participant = WarRoomParticipant(
            user_id=user_id,
            name=name,
            email=email,
            role=role,
            phone=phone
        )
        
        war_room.participants.append(participant)
        war_room.participant_count = len(war_room.participants)
        
        print(f"👤 Added to war room: {name} ({role.value})")
        
        # Invite to channels
        self._invite_to_channels(war_room, participant)
        
        # Send welcome notification
        self._send_participant_welcome(war_room, participant)
        
        return participant
    
    def _invite_to_channels(self, war_room: WarRoom, participant: WarRoomParticipant) -> None:
        """Invite participant to all war room channels"""
        for channel in war_room.channels:
            if channel.platform == "slack":
                # In production: conversations.invite
                print(f"   📨 Invited to Slack: #{channel.channel_name}")
            elif channel.platform == "teams":
                # In production: Add member to channel
                print(f"   📨 Invited to Teams: {channel.channel_name}")
    
    def _send_participant_welcome(self, war_room: WarRoom, participant: WarRoomParticipant) -> None:
        """Send welcome message to new participant"""
        message = f"""
Welcome to {war_room.name}!

**Your Role:** {participant.role.value}
**Incident ID:** {war_room.incident_id}
**Severity:** {war_room.severity.upper()}

**Resources:**
"""
        
        if war_room.bridges:
            bridge = war_room.bridges[0]
            message += f"\n**Video Bridge:** {bridge.meeting_url}"
            if bridge.passcode:
                message += f" (Passcode: {bridge.passcode})"
        
        if war_room.documents:
            message += "\n\n**Documents:**"
            for doc in war_room.documents:
                message += f"\n- {doc.title}: {doc.document_url}"
        
        # Send via email or chat
        print(f"   📧 Welcome message sent to {participant.email}")
    
    def post_status_update(
        self,
        room_id: str,
        author_id: str,
        message: str,
        priority: UpdatePriority = UpdatePriority.NORMAL,
        tags: Optional[List[str]] = None
    ) -> Optional[StatusUpdate]:
        """Post status update to war room"""
        
        if room_id not in self.war_rooms:
            print(f"❌ War room {room_id} not found")
            return None
        
        war_room = self.war_rooms[room_id]
        
        update = StatusUpdate(
            update_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            author=author_id,
            priority=priority,
            message=message,
            tags=tags or []
        )
        
        war_room.status_updates.append(update)
        war_room.total_updates = len(war_room.status_updates)
        
        # Broadcast to all channels
        self._broadcast_update(war_room, update)
        
        print(f"📢 Status update posted [{priority.value}]")
        print(f"   Message: {message[:100]}")
        
        return update
    
    def _broadcast_update(self, war_room: WarRoom, update: StatusUpdate) -> None:
        """Broadcast update to all communication channels"""
        
        # Get author name
        author_name = "Unknown"
        for p in war_room.participants:
            if p.user_id == update.author:
                author_name = p.name
                break
        
        # Format message
        priority_emoji = {
            UpdatePriority.CRITICAL: "🔴",
            UpdatePriority.HIGH: "🟠",
            UpdatePriority.NORMAL: "🟢",
            UpdatePriority.LOW: "⚪"
        }
        
        emoji = priority_emoji.get(update.priority, "🟢")
        formatted_message = f"{emoji} **{update.priority.value.upper()}** | {author_name}\n{update.message}"
        
        # Broadcast to Slack channels
        for channel in war_room.channels:
            if channel.platform == "slack":
                self._post_slack_message(channel.channel_id, formatted_message)
            elif channel.platform == "teams":
                self._post_teams_message(channel, formatted_message)
        
        update.broadcast_sent = True
    
    def activate_war_room(self, room_id: str) -> bool:
        """Activate war room for incident response"""
        if room_id not in self.war_rooms:
            return False
        
        war_room = self.war_rooms[room_id]
        war_room.status = WarRoomStatus.ACTIVE
        
        print(f"✅ War room {room_id} is now ACTIVE")
        
        # Send activation notification
        self.post_status_update(
            room_id=room_id,
            author_id="system",
            message=f"🚨 War room activated for {war_room.incident_id}. All hands on deck!",
            priority=UpdatePriority.CRITICAL
        )
        
        return True
    
    def resolve_war_room(self, room_id: str, resolution_summary: str) -> bool:
        """Resolve and deactivate war room"""
        if room_id not in self.war_rooms:
            return False
        
        war_room = self.war_rooms[room_id]
        war_room.status = WarRoomStatus.RESOLVED
        
        # Calculate duration
        duration = (datetime.now() - war_room.created_at).total_seconds() / 60
        war_room.duration_minutes = duration
        
        print(f"✅ War room {room_id} RESOLVED")
        print(f"   Duration: {duration:.1f} minutes")
        print(f"   Participants: {war_room.participant_count}")
        print(f"   Updates: {war_room.total_updates}")
        
        # Send resolution notification
        self.post_status_update(
            room_id=room_id,
            author_id="system",
            message=f"✅ Incident resolved. {resolution_summary}\n\nDuration: {duration:.1f} minutes | Participants: {war_room.participant_count} | Updates: {war_room.total_updates}",
            priority=UpdatePriority.HIGH
        )
        
        return True
    
    def get_war_room_summary(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get war room summary and metrics"""
        if room_id not in self.war_rooms:
            return None
        
        war_room = self.war_rooms[room_id]
        
        # Calculate metrics
        duration = (datetime.now() - war_room.created_at).total_seconds() / 60
        
        # Count updates by priority
        updates_by_priority = {}
        for update in war_room.status_updates:
            priority = update.priority.value
            updates_by_priority[priority] = updates_by_priority.get(priority, 0) + 1
        
        # Get participant breakdown
        participants_by_role = {}
        for participant in war_room.participants:
            role = participant.role.value
            participants_by_role[role] = participants_by_role.get(role, 0) + 1
        
        summary = {
            'room_id': war_room.room_id,
            'incident_id': war_room.incident_id,
            'name': war_room.name,
            'status': war_room.status.value,
            'severity': war_room.severity,
            'created_at': war_room.created_at.isoformat(),
            'duration_minutes': duration,
            'participant_count': war_room.participant_count,
            'participants_by_role': participants_by_role,
            'total_updates': war_room.total_updates,
            'updates_by_priority': updates_by_priority,
            'channels': len(war_room.channels),
            'bridges': len(war_room.bridges),
            'documents': len(war_room.documents)
        }
        
        return summary


# Example usage
if __name__ == "__main__":
    # Initialize war room manager
    manager = WarRoomManager()
    
    # Simulate API credentials (in production, load from secure config)
    manager.slack_bot_token = "xoxb-fake-token"
    manager.teams_webhook_url = "https://fake-webhook-url"
    manager.zoom_api_key = "fake-api-key"
    
    # Create war room for critical ransomware incident
    war_room = manager.create_war_room(
        incident_id="INC-20251017-RANSOM-001",
        severity="critical",
        name="Ransomware Response War Room",
        incident_commander_id="USR-001"
    )
    
    # Add participants
    manager.add_participant(
        room_id=war_room.room_id,
        user_id="USR-001",
        name="Alice Johnson",
        email="alice@enterprisescanner.com",
        role=ParticipantRole.INCIDENT_COMMANDER,
        phone="+1-555-0101"
    )
    
    manager.add_participant(
        room_id=war_room.room_id,
        user_id="USR-002",
        name="Bob Smith",
        email="bob@enterprisescanner.com",
        role=ParticipantRole.LEAD_ANALYST,
        phone="+1-555-0102"
    )
    
    manager.add_participant(
        room_id=war_room.room_id,
        user_id="USR-003",
        name="Carol White",
        email="carol@enterprisescanner.com",
        role=ParticipantRole.SUBJECT_MATTER_EXPERT,
        phone="+1-555-0103"
    )
    
    # Activate war room
    manager.activate_war_room(war_room.room_id)
    
    # Post status updates
    manager.post_status_update(
        room_id=war_room.room_id,
        author_id="USR-001",
        message="Ransomware identified: REvil variant. 15 servers affected.",
        priority=UpdatePriority.CRITICAL,
        tags=["ransomware", "revil", "containment"]
    )
    
    manager.post_status_update(
        room_id=war_room.room_id,
        author_id="USR-002",
        message="Network segmentation in place. Affected servers isolated.",
        priority=UpdatePriority.HIGH,
        tags=["containment", "network"]
    )
    
    manager.post_status_update(
        room_id=war_room.room_id,
        author_id="USR-003",
        message="Backup verification complete. Clean backups available from 2 hours ago.",
        priority=UpdatePriority.HIGH,
        tags=["recovery", "backups"]
    )
    
    # Resolve war room
    manager.resolve_war_room(
        room_id=war_room.room_id,
        resolution_summary="Ransomware contained and eradicated. Systems restored from backups. No data loss."
    )
    
    # Get summary
    summary = manager.get_war_room_summary(war_room.room_id)
    print(f"\n📊 War Room Summary:")
    print(f"   Status: {summary['status']}")
    print(f"   Duration: {summary['duration_minutes']:.1f} minutes")
    print(f"   Participants: {summary['participant_count']}")
    print(f"   Updates: {summary['total_updates']}")
