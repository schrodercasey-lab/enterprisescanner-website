"""
JUPITER Collaborative VR Security Operations System
Module G.3.6: Multi-User VR Threat Hunting

Enables security teams to collaborate in real-time VR environments:
- Multi-user shared investigation spaces
- Real-time avatar synchronization
- Team voice chat and annotations
- Collaborative threat analysis
- Role-based permissions and access control

Author: Enterprise Scanner Development Team
Date: October 17, 2025
Version: 1.0.0
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class UserRole(Enum):
    """User roles in collaborative VR sessions"""
    LEAD_ANALYST = "lead_analyst"           # Full control, can manage session
    SENIOR_ANALYST = "senior_analyst"       # Can modify investigations
    ANALYST = "analyst"                     # Can view and annotate
    OBSERVER = "observer"                   # Read-only access
    MANAGER = "manager"                     # Can view all, limited interaction


class SessionState(Enum):
    """Collaborative session states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    INVESTIGATION = "investigation"
    BRIEFING = "briefing"
    CLOSED = "closed"


class AnnotationType(Enum):
    """Types of collaborative annotations"""
    MARKER = "marker"                       # Point of interest marker
    HIGHLIGHT = "highlight"                 # Highlighted threat/asset
    PATH = "path"                          # Attack path annotation
    NOTE = "note"                          # Text note
    VOICE_MEMO = "voice_memo"              # Voice annotation
    SCREENSHOT = "screenshot"               # Captured view
    MEASUREMENT = "measurement"             # Distance/metric annotation


class CommunicationChannel(Enum):
    """Team communication channels"""
    TEAM_VOICE = "team_voice"              # All team members
    PRIVATE_VOICE = "private_voice"        # 1-on-1 communication
    TEXT_CHAT = "text_chat"                # Text messaging
    SYSTEM_ALERTS = "system_alerts"        # System notifications
    BROADCAST = "broadcast"                # Emergency broadcast


@dataclass
class VRPosition:
    """3D position and orientation in VR space"""
    x: float
    y: float
    z: float
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    scale: float = 1.0


@dataclass
class UserPresence:
    """Real-time user presence information"""
    user_id: str
    username: str
    role: UserRole
    avatar_id: str
    position: VRPosition
    is_speaking: bool = False
    is_pointing: bool = False
    pointed_object_id: Optional[str] = None
    focus_target_id: Optional[str] = None
    last_action: Optional[str] = None
    last_update: datetime = field(default_factory=datetime.now)
    connection_quality: float = 1.0  # 0.0 to 1.0


@dataclass
class CollaborativeAnnotation:
    """Annotation created by team members"""
    annotation_id: str
    type: AnnotationType
    created_by: str
    created_at: datetime
    position: VRPosition
    content: str
    target_object_id: Optional[str] = None
    color: str = "#FF6347"
    is_persistent: bool = True
    expires_at: Optional[datetime] = None
    upvotes: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)


@dataclass
class SharedInvestigation:
    """Shared investigation workspace"""
    investigation_id: str
    name: str
    created_by: str
    created_at: datetime
    participants: Set[str] = field(default_factory=set)
    focus_entities: List[str] = field(default_factory=list)
    timeline_start: Optional[datetime] = None
    timeline_end: Optional[datetime] = None
    annotations: List[CollaborativeAnnotation] = field(default_factory=list)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    evidence_items: List[str] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)


@dataclass
class VoiceChannel:
    """Voice communication channel"""
    channel_id: str
    channel_type: CommunicationChannel
    participants: Set[str] = field(default_factory=set)
    is_muted: bool = False
    is_recording: bool = False
    recording_start: Optional[datetime] = None


@dataclass
class TeamActivity:
    """Team activity event"""
    activity_id: str
    user_id: str
    action_type: str
    timestamp: datetime
    details: Dict[str, Any]
    is_important: bool = False


# ============================================================================
# MULTI-USER SESSION MANAGER
# ============================================================================

class MultiUserSession:
    """
    Manages multi-user VR collaboration sessions
    
    Features:
    - User presence tracking
    - Session state management
    - Permission enforcement
    - Activity logging
    """
    
    def __init__(self, session_id: str, session_name: str, created_by: str):
        self.session_id = session_id
        self.session_name = session_name
        self.created_by = created_by
        self.created_at = datetime.now()
        self.state = SessionState.INITIALIZING
        
        # User management
        self.users: Dict[str, UserPresence] = {}
        self.user_roles: Dict[str, UserRole] = {}
        self.max_users = 20  # Maximum concurrent users
        
        # Session settings
        self.settings = {
            'allow_observers': True,
            'require_approval': False,
            'auto_record': False,
            'voice_enabled': True,
            'annotation_enabled': True
        }
        
        # Activity tracking
        self.activities: List[TeamActivity] = []
        self.activity_subscribers: List[callable] = []
        
        logger.info(f"Multi-user session created: {session_id}")
    
    async def join_session(self, user_id: str, username: str, 
                          role: UserRole, avatar_id: str) -> bool:
        """
        Add user to collaborative session
        
        Args:
            user_id: Unique user identifier
            username: Display name
            role: User role in session
            avatar_id: VR avatar identifier
            
        Returns:
            True if successfully joined
        """
        # Check capacity
        if len(self.users) >= self.max_users:
            logger.warning(f"Session {self.session_id} at capacity")
            return False
        
        # Check permissions
        if role == UserRole.OBSERVER and not self.settings['allow_observers']:
            logger.warning(f"Observers not allowed in session {self.session_id}")
            return False
        
        # Create user presence
        presence = UserPresence(
            user_id=user_id,
            username=username,
            role=role,
            avatar_id=avatar_id,
            position=VRPosition(x=0, y=1.6, z=0)  # Default spawn position
        )
        
        self.users[user_id] = presence
        self.user_roles[user_id] = role
        
        # Log activity
        await self._log_activity(
            user_id=user_id,
            action_type="user_joined",
            details={
                'username': username,
                'role': role.value,
                'total_users': len(self.users)
            },
            is_important=True
        )
        
        logger.info(f"User {username} joined session {self.session_id} as {role.value}")
        return True
    
    async def leave_session(self, user_id: str) -> bool:
        """Remove user from session"""
        if user_id not in self.users:
            return False
        
        username = self.users[user_id].username
        del self.users[user_id]
        del self.user_roles[user_id]
        
        await self._log_activity(
            user_id=user_id,
            action_type="user_left",
            details={
                'username': username,
                'total_users': len(self.users)
            }
        )
        
        logger.info(f"User {username} left session {self.session_id}")
        return True
    
    async def update_user_position(self, user_id: str, position: VRPosition):
        """Update user's VR position and orientation"""
        if user_id not in self.users:
            return
        
        self.users[user_id].position = position
        self.users[user_id].last_update = datetime.now()
    
    async def update_user_action(self, user_id: str, action: str, 
                                target_id: Optional[str] = None):
        """Update user's current action"""
        if user_id not in self.users:
            return
        
        presence = self.users[user_id]
        presence.last_action = action
        presence.last_update = datetime.now()
        
        if action == "pointing":
            presence.is_pointing = True
            presence.pointed_object_id = target_id
        elif action == "speaking":
            presence.is_speaking = True
        else:
            presence.is_pointing = False
            presence.is_speaking = False
        
        # Broadcast to other users
        await self._broadcast_presence_update(user_id)
    
    async def set_user_focus(self, user_id: str, target_id: str):
        """Set what user is currently focused on"""
        if user_id not in self.users:
            return
        
        self.users[user_id].focus_target_id = target_id
        
        await self._log_activity(
            user_id=user_id,
            action_type="focus_changed",
            details={'target_id': target_id}
        )
    
    async def get_all_users(self) -> List[UserPresence]:
        """Get all active users in session"""
        return list(self.users.values())
    
    async def get_user_by_role(self, role: UserRole) -> List[UserPresence]:
        """Get all users with specific role"""
        return [
            user for user in self.users.values()
            if user.role == role
        ]
    
    async def set_session_state(self, new_state: SessionState, changed_by: str):
        """Change session state"""
        old_state = self.state
        self.state = new_state
        
        await self._log_activity(
            user_id=changed_by,
            action_type="state_changed",
            details={
                'old_state': old_state.value,
                'new_state': new_state.value
            },
            is_important=True
        )
        
        logger.info(f"Session {self.session_id} state: {old_state.value} → {new_state.value}")
    
    async def check_permission(self, user_id: str, action: str) -> bool:
        """Check if user has permission for action"""
        if user_id not in self.user_roles:
            return False
        
        role = self.user_roles[user_id]
        
        # Permission matrix
        permissions = {
            UserRole.LEAD_ANALYST: ['all'],
            UserRole.SENIOR_ANALYST: ['modify', 'annotate', 'voice', 'view'],
            UserRole.ANALYST: ['annotate', 'voice', 'view'],
            UserRole.OBSERVER: ['view'],
            UserRole.MANAGER: ['view', 'voice']
        }
        
        allowed_actions = permissions.get(role, [])
        return 'all' in allowed_actions or action in allowed_actions
    
    async def _log_activity(self, user_id: str, action_type: str, 
                           details: Dict[str, Any], is_important: bool = False):
        """Log team activity"""
        activity = TeamActivity(
            activity_id=str(uuid.uuid4()),
            user_id=user_id,
            action_type=action_type,
            timestamp=datetime.now(),
            details=details,
            is_important=is_important
        )
        
        self.activities.append(activity)
        
        # Notify subscribers
        for subscriber in self.activity_subscribers:
            await subscriber(activity)
    
    async def _broadcast_presence_update(self, user_id: str):
        """Broadcast user presence update to all users"""
        # In production, this would use WebRTC or WebSocket
        pass
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            'session_id': self.session_id,
            'session_name': self.session_name,
            'state': self.state.value,
            'total_users': len(self.users),
            'users_by_role': {
                role.value: len(await self.get_user_by_role(role))
                for role in UserRole
            },
            'total_activities': len(self.activities),
            'uptime': (datetime.now() - self.created_at).total_seconds()
        }


# ============================================================================
# SHARED INVESTIGATION SPACE
# ============================================================================

class SharedInvestigationSpace:
    """
    Manages shared investigation workspace in VR
    
    Features:
    - Collaborative threat analysis
    - Shared evidence collection
    - Real-time annotation sync
    - Investigation timeline
    """
    
    def __init__(self, session: MultiUserSession):
        self.session = session
        self.investigations: Dict[str, SharedInvestigation] = {}
        self.active_investigation_id: Optional[str] = None
        
        # Synchronization
        self.sync_interval = 0.1  # 100ms sync rate
        self.pending_updates: List[Dict[str, Any]] = []
    
    async def create_investigation(self, name: str, created_by: str,
                                  focus_entities: List[str]) -> str:
        """
        Create new shared investigation
        
        Args:
            name: Investigation name
            created_by: User who created it
            focus_entities: Initial entities to investigate
            
        Returns:
            Investigation ID
        """
        investigation_id = str(uuid.uuid4())
        
        investigation = SharedInvestigation(
            investigation_id=investigation_id,
            name=name,
            created_by=created_by,
            created_at=datetime.now(),
            participants={created_by},
            focus_entities=focus_entities
        )
        
        self.investigations[investigation_id] = investigation
        self.active_investigation_id = investigation_id
        
        logger.info(f"Created investigation: {name} ({investigation_id})")
        return investigation_id
    
    async def join_investigation(self, investigation_id: str, user_id: str) -> bool:
        """Add user to investigation"""
        if investigation_id not in self.investigations:
            return False
        
        # Check permissions
        if not await self.session.check_permission(user_id, 'view'):
            return False
        
        investigation = self.investigations[investigation_id]
        investigation.participants.add(user_id)
        
        logger.info(f"User {user_id} joined investigation {investigation_id}")
        return True
    
    async def add_annotation(self, investigation_id: str, user_id: str,
                           annotation_type: AnnotationType, position: VRPosition,
                           content: str, target_id: Optional[str] = None) -> str:
        """
        Add collaborative annotation
        
        Args:
            investigation_id: Target investigation
            user_id: User creating annotation
            annotation_type: Type of annotation
            position: 3D position in VR
            content: Annotation content
            target_id: Optional target object
            
        Returns:
            Annotation ID
        """
        if investigation_id not in self.investigations:
            return None
        
        # Check permissions
        if not await self.session.check_permission(user_id, 'annotate'):
            return None
        
        annotation_id = str(uuid.uuid4())
        
        annotation = CollaborativeAnnotation(
            annotation_id=annotation_id,
            type=annotation_type,
            created_by=user_id,
            created_at=datetime.now(),
            position=position,
            content=content,
            target_object_id=target_id
        )
        
        investigation = self.investigations[investigation_id]
        investigation.annotations.append(annotation)
        
        # Queue for sync
        await self._queue_sync_update({
            'type': 'annotation_added',
            'investigation_id': investigation_id,
            'annotation': annotation
        })
        
        logger.info(f"Annotation added: {annotation_type.value} by {user_id}")
        return annotation_id
    
    async def upvote_annotation(self, investigation_id: str, 
                               annotation_id: str, user_id: str):
        """Upvote an annotation to highlight importance"""
        if investigation_id not in self.investigations:
            return
        
        investigation = self.investigations[investigation_id]
        
        for annotation in investigation.annotations:
            if annotation.annotation_id == annotation_id:
                annotation.upvotes.add(user_id)
                
                await self._queue_sync_update({
                    'type': 'annotation_upvoted',
                    'investigation_id': investigation_id,
                    'annotation_id': annotation_id,
                    'upvote_count': len(annotation.upvotes)
                })
                break
    
    async def add_evidence(self, investigation_id: str, user_id: str,
                          evidence_id: str, evidence_type: str, 
                          description: str) -> bool:
        """Add evidence item to investigation"""
        if investigation_id not in self.investigations:
            return False
        
        if not await self.session.check_permission(user_id, 'modify'):
            return False
        
        investigation = self.investigations[investigation_id]
        investigation.evidence_items.append({
            'evidence_id': evidence_id,
            'type': evidence_type,
            'description': description,
            'added_by': user_id,
            'added_at': datetime.now().isoformat()
        })
        
        await self._queue_sync_update({
            'type': 'evidence_added',
            'investigation_id': investigation_id,
            'evidence_id': evidence_id
        })
        
        return True
    
    async def add_conclusion(self, investigation_id: str, user_id: str,
                            conclusion: str) -> bool:
        """Add investigation conclusion"""
        if investigation_id not in self.investigations:
            return False
        
        if not await self.session.check_permission(user_id, 'modify'):
            return False
        
        investigation = self.investigations[investigation_id]
        investigation.conclusions.append({
            'conclusion': conclusion,
            'author': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
        await self._queue_sync_update({
            'type': 'conclusion_added',
            'investigation_id': investigation_id,
            'conclusion': conclusion
        })
        
        return True
    
    async def set_timeline(self, investigation_id: str, 
                          start: datetime, end: datetime):
        """Set investigation timeline window"""
        if investigation_id not in self.investigations:
            return
        
        investigation = self.investigations[investigation_id]
        investigation.timeline_start = start
        investigation.timeline_end = end
        
        await self._queue_sync_update({
            'type': 'timeline_updated',
            'investigation_id': investigation_id,
            'start': start.isoformat(),
            'end': end.isoformat()
        })
    
    async def get_investigation_summary(self, investigation_id: str) -> Dict[str, Any]:
        """Get investigation summary for display"""
        if investigation_id not in self.investigations:
            return None
        
        investigation = self.investigations[investigation_id]
        
        return {
            'investigation_id': investigation_id,
            'name': investigation.name,
            'created_by': investigation.created_by,
            'created_at': investigation.created_at.isoformat(),
            'participants': list(investigation.participants),
            'participant_count': len(investigation.participants),
            'annotation_count': len(investigation.annotations),
            'evidence_count': len(investigation.evidence_items),
            'conclusion_count': len(investigation.conclusions),
            'focus_entities': investigation.focus_entities,
            'timeline': {
                'start': investigation.timeline_start.isoformat() if investigation.timeline_start else None,
                'end': investigation.timeline_end.isoformat() if investigation.timeline_end else None
            }
        }
    
    async def get_annotations_by_type(self, investigation_id: str,
                                     annotation_type: AnnotationType) -> List[CollaborativeAnnotation]:
        """Get all annotations of specific type"""
        if investigation_id not in self.investigations:
            return []
        
        investigation = self.investigations[investigation_id]
        return [
            ann for ann in investigation.annotations
            if ann.type == annotation_type
        ]
    
    async def get_top_annotations(self, investigation_id: str, 
                                 limit: int = 10) -> List[CollaborativeAnnotation]:
        """Get most upvoted annotations"""
        if investigation_id not in self.investigations:
            return []
        
        investigation = self.investigations[investigation_id]
        sorted_annotations = sorted(
            investigation.annotations,
            key=lambda a: len(a.upvotes),
            reverse=True
        )
        
        return sorted_annotations[:limit]
    
    async def _queue_sync_update(self, update: Dict[str, Any]):
        """Queue update for synchronization"""
        self.pending_updates.append(update)
    
    async def sync_updates(self) -> List[Dict[str, Any]]:
        """Get and clear pending updates for sync"""
        updates = self.pending_updates.copy()
        self.pending_updates.clear()
        return updates


# ============================================================================
# TEAM COMMUNICATION
# ============================================================================

class TeamCommunication:
    """
    Manages team voice chat and text communication
    
    Features:
    - Multi-channel voice chat
    - Spatial audio positioning
    - Text chat with mentions
    - Private messaging
    - Communication recording
    """
    
    def __init__(self, session: MultiUserSession):
        self.session = session
        self.voice_channels: Dict[str, VoiceChannel] = {}
        self.chat_history: List[Dict[str, Any]] = []
        self.max_chat_history = 1000
        
        # Spatial audio settings
        self.spatial_audio_enabled = True
        self.audio_range = 50.0  # Maximum hearing distance in VR units
        self.volume_falloff = 0.5  # Volume reduction per unit distance
    
    async def create_voice_channel(self, channel_type: CommunicationChannel,
                                  created_by: str, 
                                  participants: Optional[List[str]] = None) -> str:
        """Create new voice communication channel"""
        channel_id = str(uuid.uuid4())
        
        channel = VoiceChannel(
            channel_id=channel_id,
            channel_type=channel_type,
            participants=set(participants) if participants else {created_by}
        )
        
        self.voice_channels[channel_id] = channel
        
        logger.info(f"Voice channel created: {channel_type.value} ({channel_id})")
        return channel_id
    
    async def join_voice_channel(self, channel_id: str, user_id: str) -> bool:
        """Join voice channel"""
        if channel_id not in self.voice_channels:
            return False
        
        channel = self.voice_channels[channel_id]
        channel.participants.add(user_id)
        
        # Update user presence
        presence = self.session.users.get(user_id)
        if presence:
            presence.is_speaking = False
        
        return True
    
    async def leave_voice_channel(self, channel_id: str, user_id: str):
        """Leave voice channel"""
        if channel_id in self.voice_channels:
            self.voice_channels[channel_id].participants.discard(user_id)
    
    async def mute_channel(self, channel_id: str, muted_by: str):
        """Mute voice channel"""
        if channel_id in self.voice_channels:
            # Check permissions
            if await self.session.check_permission(muted_by, 'modify'):
                self.voice_channels[channel_id].is_muted = True
    
    async def start_recording(self, channel_id: str, started_by: str) -> bool:
        """Start recording voice channel"""
        if channel_id not in self.voice_channels:
            return False
        
        # Check permissions
        if not await self.session.check_permission(started_by, 'modify'):
            return False
        
        channel = self.voice_channels[channel_id]
        channel.is_recording = True
        channel.recording_start = datetime.now()
        
        logger.info(f"Recording started on channel {channel_id}")
        return True
    
    async def calculate_spatial_audio(self, speaker_id: str, 
                                     listener_id: str) -> float:
        """
        Calculate audio volume based on spatial positioning
        
        Args:
            speaker_id: User who is speaking
            listener_id: User who is listening
            
        Returns:
            Volume multiplier (0.0 to 1.0)
        """
        if not self.spatial_audio_enabled:
            return 1.0
        
        speaker = self.session.users.get(speaker_id)
        listener = self.session.users.get(listener_id)
        
        if not speaker or not listener:
            return 0.0
        
        # Calculate distance
        distance = np.sqrt(
            (speaker.position.x - listener.position.x) ** 2 +
            (speaker.position.y - listener.position.y) ** 2 +
            (speaker.position.z - listener.position.z) ** 2
        )
        
        # Apply falloff
        if distance > self.audio_range:
            return 0.0
        
        volume = max(0.0, 1.0 - (distance / self.audio_range) * self.volume_falloff)
        return volume
    
    async def send_text_message(self, user_id: str, message: str,
                               channel: CommunicationChannel = CommunicationChannel.TEXT_CHAT,
                               mentions: Optional[List[str]] = None) -> str:
        """Send text chat message"""
        message_id = str(uuid.uuid4())
        
        chat_message = {
            'message_id': message_id,
            'user_id': user_id,
            'username': self.session.users.get(user_id).username if user_id in self.session.users else 'Unknown',
            'message': message,
            'channel': channel.value,
            'mentions': mentions or [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.chat_history.append(chat_message)
        
        # Trim history if needed
        if len(self.chat_history) > self.max_chat_history:
            self.chat_history = self.chat_history[-self.max_chat_history:]
        
        return message_id
    
    async def send_private_message(self, from_user: str, to_user: str,
                                  message: str) -> str:
        """Send private message to specific user"""
        return await self.send_text_message(
            user_id=from_user,
            message=f"[Private to {to_user}] {message}",
            channel=CommunicationChannel.PRIVATE_VOICE
        )
    
    async def broadcast_alert(self, message: str, severity: str = 'info'):
        """Broadcast system alert to all users"""
        await self.send_text_message(
            user_id='system',
            message=f"[{severity.upper()}] {message}",
            channel=CommunicationChannel.SYSTEM_ALERTS
        )
    
    async def get_recent_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent chat messages"""
        return self.chat_history[-limit:]
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        return {
            'voice_channels': len(self.voice_channels),
            'active_channels': sum(1 for c in self.voice_channels.values() if len(c.participants) > 0),
            'total_messages': len(self.chat_history),
            'recording_channels': sum(1 for c in self.voice_channels.values() if c.is_recording)
        }


# ============================================================================
# AVATAR SYNCHRONIZATION
# ============================================================================

class AvatarSync:
    """
    Synchronizes avatar positions and animations across users
    
    Features:
    - Real-time position sync
    - Animation state sync
    - Gesture replication
    - Latency compensation
    """
    
    def __init__(self, session: MultiUserSession):
        self.session = session
        self.sync_rate = 20  # Updates per second
        self.interpolation_enabled = True
        self.prediction_enabled = True
        
        # Sync queues
        self.position_updates: Dict[str, List[VRPosition]] = defaultdict(list)
        self.animation_states: Dict[str, str] = {}
        self.gesture_queue: List[Dict[str, Any]] = []
    
    async def sync_avatar_position(self, user_id: str, position: VRPosition):
        """Sync avatar position to all users"""
        if user_id not in self.session.users:
            return
        
        # Store position update
        self.position_updates[user_id].append(position)
        
        # Keep only recent positions for interpolation
        if len(self.position_updates[user_id]) > 5:
            self.position_updates[user_id] = self.position_updates[user_id][-5:]
        
        # Update session presence
        await self.session.update_user_position(user_id, position)
    
    async def sync_animation(self, user_id: str, animation_name: str,
                           animation_time: float):
        """Sync avatar animation state"""
        if user_id not in self.session.users:
            return
        
        self.animation_states[user_id] = {
            'animation': animation_name,
            'time': animation_time,
            'timestamp': datetime.now().timestamp()
        }
    
    async def sync_gesture(self, user_id: str, gesture_name: str,
                         target_position: Optional[VRPosition] = None):
        """Sync gesture to all users"""
        gesture_event = {
            'user_id': user_id,
            'gesture': gesture_name,
            'target_position': target_position,
            'timestamp': datetime.now().timestamp()
        }
        
        self.gesture_queue.append(gesture_event)
        
        # Keep queue manageable
        if len(self.gesture_queue) > 100:
            self.gesture_queue = self.gesture_queue[-100:]
    
    async def get_interpolated_position(self, user_id: str) -> Optional[VRPosition]:
        """Get interpolated position for smooth movement"""
        if user_id not in self.position_updates:
            return None
        
        positions = self.position_updates[user_id]
        if len(positions) < 2:
            return positions[-1] if positions else None
        
        # Simple linear interpolation between last two positions
        pos1 = positions[-2]
        pos2 = positions[-1]
        
        # Interpolation factor (0.0 to 1.0)
        t = 0.5  # Middle point
        
        interpolated = VRPosition(
            x=pos1.x + (pos2.x - pos1.x) * t,
            y=pos1.y + (pos2.y - pos1.y) * t,
            z=pos1.z + (pos2.z - pos1.z) * t,
            rotation_x=pos1.rotation_x + (pos2.rotation_x - pos1.rotation_x) * t,
            rotation_y=pos1.rotation_y + (pos2.rotation_y - pos1.rotation_y) * t,
            rotation_z=pos1.rotation_z + (pos2.rotation_z - pos1.rotation_z) * t
        )
        
        return interpolated
    
    async def predict_position(self, user_id: str, 
                              time_ahead_ms: float = 50) -> Optional[VRPosition]:
        """Predict future position to compensate for latency"""
        if not self.prediction_enabled:
            return None
        
        if user_id not in self.position_updates or len(self.position_updates[user_id]) < 2:
            return None
        
        # Calculate velocity from recent positions
        positions = self.position_updates[user_id]
        pos1 = positions[-2]
        pos2 = positions[-1]
        
        # Time delta (assume 50ms between updates)
        dt = 0.05
        
        # Calculate velocity
        vx = (pos2.x - pos1.x) / dt
        vy = (pos2.y - pos1.y) / dt
        vz = (pos2.z - pos1.z) / dt
        
        # Predict position
        time_ahead = time_ahead_ms / 1000.0
        predicted = VRPosition(
            x=pos2.x + vx * time_ahead,
            y=pos2.y + vy * time_ahead,
            z=pos2.z + vz * time_ahead,
            rotation_x=pos2.rotation_x,
            rotation_y=pos2.rotation_y,
            rotation_z=pos2.rotation_z
        )
        
        return predicted
    
    async def get_all_avatar_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all avatars"""
        states = {}
        
        for user_id, presence in self.session.users.items():
            states[user_id] = {
                'username': presence.username,
                'position': presence.position,
                'animation': self.animation_states.get(user_id),
                'is_speaking': presence.is_speaking,
                'is_pointing': presence.is_pointing,
                'pointed_object': presence.pointed_object_id
            }
        
        return states
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        total_position_updates = sum(len(updates) for updates in self.position_updates.values())
        
        return {
            'sync_rate': self.sync_rate,
            'tracked_users': len(self.position_updates),
            'total_position_updates': total_position_updates,
            'active_animations': len(self.animation_states),
            'queued_gestures': len(self.gesture_queue),
            'interpolation_enabled': self.interpolation_enabled,
            'prediction_enabled': self.prediction_enabled
        }


# ============================================================================
# COLLABORATIVE VR SYSTEM (MAIN)
# ============================================================================

class CollaborativeVRSystem:
    """
    Main collaborative VR system integrating all components
    
    Usage:
        collab_system = CollaborativeVRSystem()
        session_id = await collab_system.create_session("Threat Hunt Team", "user123")
        await collab_system.join_session(session_id, "user456", "Alice", UserRole.ANALYST)
    """
    
    def __init__(self):
        self.sessions: Dict[str, MultiUserSession] = {}
        self.investigation_spaces: Dict[str, SharedInvestigationSpace] = {}
        self.communication_systems: Dict[str, TeamCommunication] = {}
        self.avatar_syncs: Dict[str, AvatarSync] = {}
        
        logger.info("Collaborative VR System initialized")
    
    async def create_session(self, session_name: str, created_by: str) -> str:
        """Create new collaborative session"""
        session_id = str(uuid.uuid4())
        
        # Create session
        session = MultiUserSession(session_id, session_name, created_by)
        self.sessions[session_id] = session
        
        # Initialize subsystems
        self.investigation_spaces[session_id] = SharedInvestigationSpace(session)
        self.communication_systems[session_id] = TeamCommunication(session)
        self.avatar_syncs[session_id] = AvatarSync(session)
        
        # Auto-join creator
        await session.join_session(
            user_id=created_by,
            username="Session Creator",
            role=UserRole.LEAD_ANALYST,
            avatar_id="default_avatar"
        )
        
        logger.info(f"Created collaborative session: {session_name} ({session_id})")
        return session_id
    
    async def join_session(self, session_id: str, user_id: str,
                          username: str, role: UserRole,
                          avatar_id: str = "default_avatar") -> bool:
        """Join existing session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        return await session.join_session(user_id, username, role, avatar_id)
    
    async def get_session(self, session_id: str) -> Optional[MultiUserSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def get_investigation_space(self, session_id: str) -> Optional[SharedInvestigationSpace]:
        """Get investigation space for session"""
        return self.investigation_spaces.get(session_id)
    
    async def get_communication(self, session_id: str) -> Optional[TeamCommunication]:
        """Get communication system for session"""
        return self.communication_systems.get(session_id)
    
    async def get_avatar_sync(self, session_id: str) -> Optional[AvatarSync]:
        """Get avatar sync for session"""
        return self.avatar_syncs.get(session_id)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_users = sum(len(session.users) for session in self.sessions.values())
        active_sessions = sum(1 for s in self.sessions.values() if s.state == SessionState.ACTIVE)
        
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': active_sessions,
            'total_users': total_users,
            'total_investigations': sum(
                len(space.investigations) for space in self.investigation_spaces.values()
            ),
            'system_uptime': 'active'
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_collaborative_session():
    """Example: Multi-user threat hunting session"""
    
    # Initialize system
    collab_system = CollaborativeVRSystem()
    
    # Create session
    session_id = await collab_system.create_session(
        session_name="Ransomware Investigation Team",
        created_by="lead_analyst_001"
    )
    
    # Add team members
    await collab_system.join_session(
        session_id=session_id,
        user_id="analyst_002",
        username="Alice Johnson",
        role=UserRole.SENIOR_ANALYST,
        avatar_id="avatar_alice"
    )
    
    await collab_system.join_session(
        session_id=session_id,
        user_id="analyst_003",
        username="Bob Smith",
        role=UserRole.ANALYST,
        avatar_id="avatar_bob"
    )
    
    # Create shared investigation
    inv_space = await collab_system.get_investigation_space(session_id)
    investigation_id = await inv_space.create_investigation(
        name="WannaCry Outbreak Analysis",
        created_by="lead_analyst_001",
        focus_entities=["ransomware", "lateral_movement", "patient_zero"]
    )
    
    # Add annotations
    await inv_space.add_annotation(
        investigation_id=investigation_id,
        user_id="analyst_002",
        annotation_type=AnnotationType.MARKER,
        position=VRPosition(x=10.5, y=2.0, z=5.3),
        content="Patient zero identified: workstation-042",
        target_id="ws-042"
    )
    
    # Start voice chat
    comm = await collab_system.get_communication(session_id)
    voice_channel = await comm.create_voice_channel(
        channel_type=CommunicationChannel.TEAM_VOICE,
        created_by="lead_analyst_001"
    )
    
    # Send team message
    await comm.send_text_message(
        user_id="analyst_002",
        message="Found the entry point - it's an email attachment",
        mentions=["lead_analyst_001"]
    )
    
    # Get session stats
    session = await collab_system.get_session(session_id)
    stats = session.get_session_stats()
    
    print(f"Session Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_collaborative_session())
