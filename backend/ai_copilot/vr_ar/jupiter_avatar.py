"""
G.3.2: JUPITER Avatar System

PATENT PENDING - Intelligent 3D AI Security Assistant

Enterprise-grade AI avatar system providing immersive, personality-driven
cybersecurity assistance in VR/AR environments. JUPITER serves as proactive
threat analyst, mentor, and interactive guide.

Patent Claims:
- Emotionally-aware AI security assistant with dynamic personality
- 3D spatial audio voice synthesis with directional positioning
- Proactive threat alerting with context-aware interruptions
- Attention and gaze tracking for natural interaction
- Proximity-based behavior adaptation
- Animation and gesture system synchronized with speech
- Multi-modal interaction (voice, gesture, gaze)

Author: Enterprise Scanner Development Team
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import json
import uuid
import random
import math


class EmotionalState(Enum):
    """JUPITER's emotional states"""
    NEUTRAL = "neutral"                # Normal operations
    ALERT = "alert"                    # Threat detected
    FOCUSED = "focused"                # Analyzing data
    CONCERNED = "concerned"            # Critical situation
    SATISFIED = "satisfied"            # Threat mitigated
    ANXIOUS = "anxious"                # Multiple threats
    CALM = "calm"                      # All clear
    ENGAGED = "engaged"                # Active conversation
    THINKING = "thinking"              # Processing request


class VoiceCharacteristic(Enum):
    """Voice profile options"""
    PROFESSIONAL_MALE = "professional_male"        # Default male voice
    PROFESSIONAL_FEMALE = "professional_female"    # Default female voice
    PROFESSIONAL_NEUTRAL = "professional_neutral"  # Gender-neutral
    MILITARY_COMMANDER = "military_commander"      # Authoritative
    FRIENDLY_MENTOR = "friendly_mentor"            # Approachable
    TECHNICAL_EXPERT = "technical_expert"          # Analytical


class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"      # Immediate interruption
    HIGH = "high"              # Important but can wait
    MEDIUM = "medium"          # Notify when appropriate
    LOW = "low"                # Background notification
    INFO = "info"              # Informational only


class InteractionMode(Enum):
    """JUPITER interaction modes"""
    TOUR_GUIDE = "tour_guide"          # Guiding through environment
    MENTOR = "mentor"                  # Educational explanations
    ASSISTANT = "assistant"            # Responding to commands
    ALERT_SYSTEM = "alert_system"      # Proactive notifications
    PRESENTER = "presenter"            # Delivering briefings
    STANDBY = "standby"                # Idle state


@dataclass
class AvatarPersonality:
    """
    JUPITER's personality configuration.
    
    Defines behavioral traits, communication style, and interaction patterns.
    """
    personality_id: str
    name: str = "JUPITER"
    voice_characteristic: VoiceCharacteristic = VoiceCharacteristic.PROFESSIONAL_NEUTRAL
    
    # Personality traits (0.0 - 1.0)
    formality: float = 0.7              # How formal in speech
    proactivity: float = 0.8            # How proactive in alerting
    verbosity: float = 0.5              # How much detail in responses
    empathy: float = 0.6                # Emotional awareness
    humor: float = 0.2                  # Occasional lightness
    urgency_sensitivity: float = 0.9    # Response to critical threats
    
    # Interaction preferences
    preferred_distance: float = 2.0     # Preferred distance from user (meters)
    eye_contact_frequency: float = 0.7  # How often to make eye contact
    gesture_frequency: float = 0.5      # How animated
    interruption_threshold: int = 85    # Risk score to interrupt user
    
    def get_greeting(self, time_of_day: str = "morning") -> str:
        """Generate contextual greeting"""
        greetings = {
            'morning': [
                "Good morning. I've prepared your security briefing.",
                "Good morning. Let's review overnight activity.",
                "Morning. I have important updates to share."
            ],
            'afternoon': [
                "Good afternoon. Security operations are stable.",
                "Afternoon. Ready to continue our work.",
                "Good afternoon. How can I assist you?"
            ],
            'evening': [
                "Good evening. End-of-day summary is ready.",
                "Evening. Let's review today's incidents.",
                "Good evening. Time to wrap up operations."
            ]
        }
        
        options = greetings.get(time_of_day, greetings['morning'])
        return random.choice(options)
    
    def get_response_style(self, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Get communication style based on emotion"""
        styles = {
            EmotionalState.ALERT: {
                'speed': 1.2,      # Speak faster
                'volume': 1.1,     # Slightly louder
                'tone': 'urgent',
                'prefix': "Attention: "
            },
            EmotionalState.CONCERNED: {
                'speed': 1.1,
                'volume': 1.0,
                'tone': 'serious',
                'prefix': "We have a situation: "
            },
            EmotionalState.SATISFIED: {
                'speed': 0.9,
                'volume': 0.95,
                'tone': 'pleased',
                'prefix': "Good news: "
            },
            EmotionalState.CALM: {
                'speed': 1.0,
                'volume': 1.0,
                'tone': 'neutral',
                'prefix': ""
            }
        }
        
        return styles.get(
            emotional_state,
            {'speed': 1.0, 'volume': 1.0, 'tone': 'neutral', 'prefix': ''}
        )


@dataclass
class SpatialPresence:
    """
    JUPITER's spatial positioning and movement in VR space.
    
    Handles avatar placement relative to user, environmental awareness,
    and natural movement behaviors.
    """
    position: Tuple[float, float, float]  # (x, y, z) in meters
    rotation: Tuple[float, float, float]  # (pitch, yaw, roll) in degrees
    scale: float = 1.0                    # Avatar size multiplier
    
    # Movement parameters
    movement_speed: float = 2.0           # Meters per second
    rotation_speed: float = 120.0         # Degrees per second
    follow_distance: float = 2.0          # Distance to maintain from user
    hover_height: float = 0.0             # Height offset from ground
    
    def calculate_distance_to(self, target_position: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance to target"""
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        dz = target_position[2] - self.position[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def calculate_look_at_rotation(self, target_position: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Calculate rotation to look at target"""
        dx = target_position[0] - self.position[0]
        dz = target_position[2] - self.position[2]
        dy = target_position[1] - self.position[1]
        
        # Calculate yaw (horizontal rotation)
        yaw = math.degrees(math.atan2(dx, dz))
        
        # Calculate pitch (vertical rotation)
        horizontal_distance = math.sqrt(dx*dx + dz*dz)
        pitch = math.degrees(math.atan2(dy, horizontal_distance))
        
        return (pitch, yaw, 0.0)  # Roll typically stays 0
    
    def move_towards(
        self,
        target_position: Tuple[float, float, float],
        delta_time: float
    ) -> Tuple[float, float, float]:
        """Move towards target position"""
        distance = self.calculate_distance_to(target_position)
        
        if distance < 0.1:  # Close enough
            return self.position
        
        # Calculate movement vector
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        dz = target_position[2] - self.position[2]
        
        # Normalize
        dx /= distance
        dy /= distance
        dz /= distance
        
        # Apply movement
        move_distance = min(self.movement_speed * delta_time, distance)
        
        new_x = self.position[0] + dx * move_distance
        new_y = self.position[1] + dy * move_distance
        new_z = self.position[2] + dz * move_distance
        
        return (new_x, new_y, new_z)
    
    def should_reposition(self, user_position: Tuple[float, float, float]) -> bool:
        """Check if avatar should reposition relative to user"""
        distance = self.calculate_distance_to(user_position)
        
        # Too close or too far
        if distance < self.follow_distance * 0.5:
            return True
        if distance > self.follow_distance * 2.0:
            return True
        
        return False


@dataclass
class VoiceEmitter:
    """
    3D spatial audio voice system.
    
    Handles text-to-speech with spatial positioning, emotional inflection,
    and dynamic audio properties.
    """
    emitter_id: str
    position: Tuple[float, float, float]
    voice_characteristic: VoiceCharacteristic
    
    # Audio properties
    base_volume: float = 1.0              # 0.0 - 1.0
    base_pitch: float = 1.0               # 0.5 - 2.0
    speaking_rate: float = 1.0            # 0.5 - 2.0
    
    # Spatial audio
    attenuation_distance: float = 10.0    # Distance for volume falloff
    doppler_effect: bool = True           # Enable doppler shift
    reverb_enabled: bool = True           # Environmental reverb
    
    def calculate_spatial_volume(
        self,
        listener_position: Tuple[float, float, float]
    ) -> float:
        """Calculate volume based on distance"""
        dx = listener_position[0] - self.position[0]
        dy = listener_position[1] - self.position[1]
        dz = listener_position[2] - self.position[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Inverse square law with minimum
        volume = self.base_volume / max(1.0, (distance / self.attenuation_distance) ** 2)
        return min(1.0, volume)
    
    def apply_emotional_modulation(
        self,
        emotional_state: EmotionalState
    ) -> Dict[str, float]:
        """Modulate voice properties based on emotion"""
        modulations = {
            EmotionalState.ALERT: {
                'volume': 1.2,
                'pitch': 1.1,
                'rate': 1.2
            },
            EmotionalState.CONCERNED: {
                'volume': 1.1,
                'pitch': 0.95,
                'rate': 1.0
            },
            EmotionalState.SATISFIED: {
                'volume': 1.0,
                'pitch': 1.05,
                'rate': 0.95
            },
            EmotionalState.CALM: {
                'volume': 0.9,
                'pitch': 1.0,
                'rate': 0.9
            },
            EmotionalState.ANXIOUS: {
                'volume': 1.15,
                'pitch': 1.15,
                'rate': 1.3
            }
        }
        
        default = {'volume': 1.0, 'pitch': 1.0, 'rate': 1.0}
        mods = modulations.get(emotional_state, default)
        
        return {
            'volume': self.base_volume * mods['volume'],
            'pitch': self.base_pitch * mods['pitch'],
            'rate': self.speaking_rate * mods['rate']
        }
    
    def synthesize_speech(
        self,
        text: str,
        emotional_state: EmotionalState = EmotionalState.NEUTRAL
    ) -> Dict[str, Any]:
        """Generate speech synthesis parameters"""
        mods = self.apply_emotional_modulation(emotional_state)
        
        return {
            'text': text,
            'voice': self.voice_characteristic.value,
            'volume': mods['volume'],
            'pitch': mods['pitch'],
            'rate': mods['rate'],
            'position': self.position,
            'spatial_audio': True,
            'reverb': self.reverb_enabled
        }


@dataclass
class AnimationController:
    """
    Avatar animation and gesture system.
    
    Synchronizes animations with speech, emotional states,
    and user interactions.
    """
    controller_id: str
    current_animation: str = "idle"
    animation_speed: float = 1.0
    
    # Animation library
    animations = {
        'idle': {'duration': 2.0, 'loop': True},
        'speaking': {'duration': 1.0, 'loop': True},
        'pointing': {'duration': 1.5, 'loop': False},
        'gesturing': {'duration': 2.0, 'loop': True},
        'alert': {'duration': 1.0, 'loop': False},
        'thinking': {'duration': 3.0, 'loop': True},
        'nodding': {'duration': 1.0, 'loop': False},
        'shaking_head': {'duration': 1.0, 'loop': False},
        'wave': {'duration': 1.5, 'loop': False},
        'presenting': {'duration': 2.5, 'loop': True}
    }
    
    def play_animation(
        self,
        animation_name: str,
        blend_time: float = 0.3
    ) -> Dict[str, Any]:
        """Play animation with blending"""
        if animation_name not in self.animations:
            animation_name = 'idle'
        
        anim_data = self.animations[animation_name]
        
        return {
            'animation': animation_name,
            'speed': self.animation_speed,
            'blend_time': blend_time,
            'loop': anim_data['loop'],
            'duration': anim_data['duration']
        }
    
    def get_animation_for_emotion(
        self,
        emotional_state: EmotionalState
    ) -> str:
        """Get appropriate animation for emotional state"""
        emotion_animations = {
            EmotionalState.ALERT: 'alert',
            EmotionalState.THINKING: 'thinking',
            EmotionalState.SATISFIED: 'nodding',
            EmotionalState.ENGAGED: 'speaking',
            EmotionalState.NEUTRAL: 'idle'
        }
        
        return emotion_animations.get(emotional_state, 'idle')
    
    def synchronize_with_speech(
        self,
        speech_text: str,
        speech_duration: float
    ) -> List[Dict[str, Any]]:
        """Generate animation sequence synchronized with speech"""
        animations = []
        
        # Start with speaking animation
        animations.append({
            'animation': 'speaking',
            'start_time': 0.0,
            'duration': speech_duration
        })
        
        # Add occasional gestures
        gesture_interval = 3.0
        current_time = 0.0
        
        while current_time < speech_duration:
            if random.random() < 0.3:  # 30% chance of gesture
                animations.append({
                    'animation': random.choice(['pointing', 'gesturing']),
                    'start_time': current_time,
                    'duration': 1.5
                })
            current_time += gesture_interval
        
        return animations


@dataclass
class AttentionSystem:
    """
    Eye tracking and attention focus system.
    
    Manages where JUPITER looks, tracks user gaze, and determines
    focus of attention for natural interaction.
    """
    attention_id: str
    current_focus: Optional[str] = None    # Object ID being focused on
    focus_duration: float = 0.0            # How long focused (seconds)
    
    # Attention parameters
    max_focus_duration: float = 5.0        # Before looking away
    distraction_probability: float = 0.1   # Chance to look at something else
    user_priority: float = 0.8             # Priority for looking at user
    
    def update_focus(
        self,
        user_position: Tuple[float, float, float],
        threat_positions: List[Tuple[str, Tuple[float, float, float]]],
        delta_time: float
    ) -> Optional[str]:
        """Update attention focus"""
        self.focus_duration += delta_time
        
        # Check if should change focus
        if self.focus_duration >= self.max_focus_duration:
            return self._select_new_focus(user_position, threat_positions)
        
        # Random distraction
        if random.random() < self.distraction_probability * delta_time:
            return self._select_new_focus(user_position, threat_positions)
        
        return self.current_focus
    
    def _select_new_focus(
        self,
        user_position: Tuple[float, float, float],
        threat_positions: List[Tuple[str, Tuple[float, float, float]]]
    ) -> Optional[str]:
        """Select new focus point"""
        # Prioritize user
        if random.random() < self.user_priority:
            self.current_focus = "user"
            self.focus_duration = 0.0
            return "user"
        
        # Look at threats
        if threat_positions and random.random() < 0.3:
            threat_id, position = random.choice(threat_positions)
            self.current_focus = threat_id
            self.focus_duration = 0.0
            return threat_id
        
        # Look at environment
        self.current_focus = None
        self.focus_duration = 0.0
        return None
    
    def should_make_eye_contact(
        self,
        eye_contact_frequency: float = 0.7
    ) -> bool:
        """Determine if should make eye contact"""
        return random.random() < eye_contact_frequency


@dataclass
class ProximityManager:
    """
    Personal space and proximity management.
    
    Handles avatar behavior based on distance to user and other objects.
    Respects personal space boundaries.
    """
    manager_id: str
    
    # Proximity zones (meters)
    intimate_zone: float = 0.5      # Too close
    personal_zone: float = 1.5      # Comfortable distance
    social_zone: float = 3.5        # Normal interaction
    public_zone: float = 7.0        # Far but visible
    
    def get_proximity_zone(
        self,
        distance: float
    ) -> str:
        """Determine proximity zone"""
        if distance < self.intimate_zone:
            return "intimate"
        elif distance < self.personal_zone:
            return "personal"
        elif distance < self.social_zone:
            return "social"
        elif distance < self.public_zone:
            return "public"
        else:
            return "distant"
    
    def get_behavior_for_proximity(
        self,
        distance: float
    ) -> Dict[str, Any]:
        """Get appropriate behavior based on proximity"""
        zone = self.get_proximity_zone(distance)
        
        behaviors = {
            "intimate": {
                'action': 'back_away',
                'voice_volume': 0.7,
                'gesture_size': 0.5
            },
            "personal": {
                'action': 'maintain',
                'voice_volume': 1.0,
                'gesture_size': 1.0
            },
            "social": {
                'action': 'maintain',
                'voice_volume': 1.1,
                'gesture_size': 1.2
            },
            "public": {
                'action': 'move_closer',
                'voice_volume': 1.3,
                'gesture_size': 1.5
            },
            "distant": {
                'action': 'move_closer',
                'voice_volume': 1.5,
                'gesture_size': 2.0
            }
        }
        
        return behaviors.get(zone, behaviors["social"])
    
    def calculate_ideal_position(
        self,
        user_position: Tuple[float, float, float],
        user_forward: Tuple[float, float, float],
        preferred_distance: float = 2.0
    ) -> Tuple[float, float, float]:
        """Calculate ideal avatar position relative to user"""
        # Position slightly to the side and in front
        angle_offset = 30.0  # degrees
        angle_rad = math.radians(angle_offset)
        
        # Calculate position
        forward_x = user_forward[0]
        forward_z = user_forward[2]
        
        # Rotate by offset angle
        offset_x = forward_x * math.cos(angle_rad) - forward_z * math.sin(angle_rad)
        offset_z = forward_x * math.sin(angle_rad) + forward_z * math.cos(angle_rad)
        
        # Apply distance
        ideal_x = user_position[0] + offset_x * preferred_distance
        ideal_y = user_position[1]  # Same height
        ideal_z = user_position[2] + offset_z * preferred_distance
        
        return (ideal_x, ideal_y, ideal_z)


class JupiterAvatar:
    """
    Main JUPITER Avatar controller.
    
    Coordinates all avatar systems: personality, spatial presence, voice,
    animations, attention, and proximity management.
    
    PATENT CLAIM: Integrated AI security assistant with emotional awareness,
    spatial intelligence, and multi-modal interaction in VR/AR.
    """
    
    def __init__(
        self,
        avatar_id: str,
        personality: Optional[AvatarPersonality] = None,
        db_path: str = "jupiter_avatar.db"
    ):
        self.avatar_id = avatar_id
        self.personality = personality or AvatarPersonality(personality_id=avatar_id)
        self.db_path = db_path
        
        # Initialize subsystems
        self.spatial_presence = SpatialPresence(
            position=(0.0, 0.0, 2.0),
            rotation=(0.0, 0.0, 0.0),
            follow_distance=self.personality.preferred_distance
        )
        
        self.voice_emitter = VoiceEmitter(
            emitter_id=f"{avatar_id}_voice",
            position=self.spatial_presence.position,
            voice_characteristic=self.personality.voice_characteristic
        )
        
        self.animation_controller = AnimationController(
            controller_id=f"{avatar_id}_anim"
        )
        
        self.attention_system = AttentionSystem(
            attention_id=f"{avatar_id}_attention"
        )
        
        self.proximity_manager = ProximityManager(
            manager_id=f"{avatar_id}_proximity"
        )
        
        # State
        self.emotional_state = EmotionalState.NEUTRAL
        self.interaction_mode = InteractionMode.STANDBY
        self.is_speaking = False
        self.current_conversation_context: Dict[str, Any] = {}
        
        self._init_database()
    
    def _init_database(self):
        """Initialize avatar database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Avatar state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avatar_state (
                avatar_id TEXT PRIMARY KEY,
                emotional_state TEXT NOT NULL,
                interaction_mode TEXT NOT NULL,
                position TEXT NOT NULL,
                rotation TEXT NOT NULL,
                is_speaking INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Interaction history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_history (
                interaction_id TEXT PRIMARY KEY,
                avatar_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                user_input TEXT,
                avatar_response TEXT,
                emotional_state TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (avatar_id) REFERENCES avatar_state(avatar_id)
            )
        """)
        
        # Alert history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                alert_id TEXT PRIMARY KEY,
                avatar_id TEXT NOT NULL,
                alert_priority TEXT NOT NULL,
                alert_message TEXT NOT NULL,
                threat_id TEXT,
                user_acknowledged INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (avatar_id) REFERENCES avatar_state(avatar_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def update(
        self,
        user_position: Tuple[float, float, float],
        user_forward: Tuple[float, float, float],
        threats: List[Tuple[str, Tuple[float, float, float]]],
        delta_time: float
    ):
        """
        Update avatar state (called each frame).
        
        PATENT CLAIM: Real-time avatar behavior adaptation based on
        user position, threats, and environmental context.
        """
        # Update spatial presence
        if self.spatial_presence.should_reposition(user_position):
            ideal_pos = self.proximity_manager.calculate_ideal_position(
                user_position,
                user_forward,
                self.personality.preferred_distance
            )
            self.spatial_presence.position = self.spatial_presence.move_towards(
                ideal_pos,
                delta_time
            )
        
        # Update look-at target
        self.attention_system.update_focus(
            user_position,
            threats,
            delta_time
        )
        
        if self.attention_system.current_focus == "user":
            self.spatial_presence.rotation = self.spatial_presence.calculate_look_at_rotation(
                user_position
            )
        
        # Update voice emitter position
        self.voice_emitter.position = self.spatial_presence.position
        
        # Update animation based on state
        if not self.is_speaking:
            anim = self.animation_controller.get_animation_for_emotion(
                self.emotional_state
            )
            self.animation_controller.play_animation(anim)
    
    def speak(
        self,
        text: str,
        priority: AlertPriority = AlertPriority.INFO
    ) -> Dict[str, Any]:
        """
        Make JUPITER speak with 3D spatial audio.
        
        PATENT CLAIM: Emotionally-modulated spatial voice synthesis
        for security communications.
        """
        self.is_speaking = True
        
        # Get speech parameters
        speech_params = self.voice_emitter.synthesize_speech(
            text,
            self.emotional_state
        )
        
        # Get animation sequence
        estimated_duration = len(text.split()) * 0.4  # ~400ms per word
        animations = self.animation_controller.synchronize_with_speech(
            text,
            estimated_duration
        )
        
        # Log interaction
        self._log_interaction("speech", text, None)
        
        return {
            'speech': speech_params,
            'animations': animations,
            'duration': estimated_duration,
            'priority': priority.value
        }
    
    def alert_threat(
        self,
        threat_description: str,
        threat_id: str,
        risk_score: int,
        threat_position: Optional[Tuple[float, float, float]] = None
    ) -> Dict[str, Any]:
        """
        Proactive threat alerting.
        
        PATENT CLAIM: Context-aware threat interruption with
        risk-based priority determination.
        """
        # Determine if should interrupt
        should_interrupt = risk_score >= self.personality.interruption_threshold
        
        # Set emotional state
        if risk_score >= 90:
            self.emotional_state = EmotionalState.ALERT
            priority = AlertPriority.CRITICAL
        elif risk_score >= 70:
            self.emotional_state = EmotionalState.CONCERNED
            priority = AlertPriority.HIGH
        else:
            self.emotional_state = EmotionalState.FOCUSED
            priority = AlertPriority.MEDIUM
        
        # Generate alert message
        style = self.personality.get_response_style(self.emotional_state)
        message = f"{style['prefix']}{threat_description}"
        
        # Point at threat if position provided
        if threat_position:
            self.spatial_presence.rotation = self.spatial_presence.calculate_look_at_rotation(
                threat_position
            )
            self.animation_controller.play_animation('pointing')
        
        # Log alert
        self._log_alert(threat_id, priority, message)
        
        return {
            'message': message,
            'priority': priority,
            'should_interrupt': should_interrupt,
            'emotional_state': self.emotional_state.value,
            'speech': self.speak(message, priority)
        }
    
    def respond_to_command(
        self,
        user_command: str,
        command_result: Dict[str, Any]
    ) -> str:
        """
        Generate natural language response to user command.
        
        PATENT CLAIM: Context-aware conversational responses
        for security operations.
        """
        # Store context
        self.current_conversation_context['last_command'] = user_command
        self.current_conversation_context['last_result'] = command_result
        
        # Set mode
        self.interaction_mode = InteractionMode.ASSISTANT
        self.emotional_state = EmotionalState.ENGAGED
        
        # Generate response based on command type
        if 'error' in command_result:
            response = f"I encountered an issue: {command_result['error']}"
        elif 'success' in command_result and command_result['success']:
            response = self._generate_success_response(user_command, command_result)
        else:
            response = self._generate_info_response(user_command, command_result)
        
        # Log interaction
        self._log_interaction("command_response", user_command, response)
        
        return response
    
    def _generate_success_response(
        self,
        command: str,
        result: Dict[str, Any]
    ) -> str:
        """Generate success response"""
        responses = [
            f"Done. {result.get('message', 'Operation completed successfully.')}",
            f"Completed. {result.get('message', 'All set.')}",
            f"Finished. {result.get('message', 'Ready for next task.')}"
        ]
        
        return random.choice(responses)
    
    def _generate_info_response(
        self,
        command: str,
        result: Dict[str, Any]
    ) -> str:
        """Generate informational response"""
        count = result.get('count', 0)
        
        if 'vulnerabilities' in command.lower():
            return f"Found {count} vulnerabilities. Displaying them now."
        elif 'threats' in command.lower():
            return f"Showing {count} active threats in your environment."
        elif 'network' in command.lower():
            return f"Here's your network topology with {count} assets."
        else:
            return f"Here are the results: {count} items found."
    
    def set_emotional_state(
        self,
        state: EmotionalState,
        duration: Optional[float] = None
    ):
        """Manually set emotional state"""
        self.emotional_state = state
        
        # Update animation
        anim = self.animation_controller.get_animation_for_emotion(state)
        self.animation_controller.play_animation(anim)
    
    def _log_interaction(
        self,
        interaction_type: str,
        user_input: Optional[str],
        avatar_response: Optional[str]
    ):
        """Log interaction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        interaction_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO interaction_history
            (interaction_id, avatar_id, interaction_type, user_input,
             avatar_response, emotional_state, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction_id,
            self.avatar_id,
            interaction_type,
            user_input,
            avatar_response,
            self.emotional_state.value,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _log_alert(
        self,
        threat_id: str,
        priority: AlertPriority,
        message: str
    ):
        """Log alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        alert_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO alert_history
            (alert_id, avatar_id, alert_priority, alert_message,
             threat_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert_id,
            self.avatar_id,
            priority.value,
            message,
            threat_id,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current avatar state summary"""
        return {
            'avatar_id': self.avatar_id,
            'name': self.personality.name,
            'emotional_state': self.emotional_state.value,
            'interaction_mode': self.interaction_mode.value,
            'position': self.spatial_presence.position,
            'rotation': self.spatial_presence.rotation,
            'is_speaking': self.is_speaking,
            'current_animation': self.animation_controller.current_animation,
            'attention_focus': self.attention_system.current_focus,
            'voice_characteristic': self.personality.voice_characteristic.value
        }


# Example usage
if __name__ == "__main__":
    print("=== JUPITER Avatar System ===\n")
    print("PATENT PENDING - Intelligent 3D AI Security Assistant\n")
    
    # Create JUPITER avatar
    jupiter = JupiterAvatar(
        avatar_id="jupiter_001",
        personality=AvatarPersonality(
            personality_id="default",
            formality=0.7,
            proactivity=0.8,
            verbosity=0.6
        )
    )
    
    print(f"Avatar: {jupiter.personality.name}")
    print(f"Voice: {jupiter.personality.voice_characteristic.value}")
    print(f"Emotional State: {jupiter.emotional_state.value}")
    print(f"Position: {jupiter.spatial_presence.position}")
    
    # Example 1: Greeting
    print("\n=== Greeting ===\n")
    greeting = jupiter.personality.get_greeting("morning")
    print(f"JUPITER: {greeting}")
    speech = jupiter.speak(greeting)
    print(f"Speech duration: {speech['duration']:.2f}s")
    print(f"Animations: {len(speech['animations'])}")
    
    # Example 2: Threat alert
    print("\n=== Critical Threat Alert ===\n")
    
    alert = jupiter.alert_threat(
        threat_description="Critical vulnerability CVE-2025-1234 detected on web servers",
        threat_id="CVE-2025-1234",
        risk_score=95,
        threat_position=(5.0, 1.5, 3.0)
    )
    
    print(f"Priority: {alert['priority'].value}")
    print(f"Should interrupt: {alert['should_interrupt']}")
    print(f"Emotional state: {alert['emotional_state']}")
    print(f"Message: {alert['message']}")
    
    # Example 3: Command response
    print("\n=== Command Response ===\n")
    
    response = jupiter.respond_to_command(
        user_command="Show me all critical vulnerabilities",
        command_result={
            'success': True,
            'count': 12,
            'message': '12 critical vulnerabilities found'
        }
    )
    
    print(f"JUPITER: {response}")
    
    # Example 4: Update loop simulation
    print("\n=== Position Update ===\n")
    
    user_pos = (0.0, 0.0, 0.0)
    user_forward = (0.0, 0.0, 1.0)
    threats = [
        ("threat_001", (3.0, 1.0, 2.0)),
        ("threat_002", (-2.0, 1.5, 4.0))
    ]
    
    jupiter.update(user_pos, user_forward, threats, delta_time=0.016)  # ~60 FPS
    
    print(f"Avatar position: {jupiter.spatial_presence.position}")
    print(f"Avatar rotation: {jupiter.spatial_presence.rotation}")
    print(f"Attention focus: {jupiter.attention_system.current_focus}")
    
    # Example 5: Proximity management
    print("\n=== Proximity Management ===\n")
    
    distance = jupiter.spatial_presence.calculate_distance_to(user_pos)
    zone = jupiter.proximity_manager.get_proximity_zone(distance)
    behavior = jupiter.proximity_manager.get_behavior_for_proximity(distance)
    
    print(f"Distance to user: {distance:.2f}m")
    print(f"Proximity zone: {zone}")
    print(f"Recommended action: {behavior['action']}")
    print(f"Voice volume adjustment: {behavior['voice_volume']:.1f}x")
    
    # Example 6: State summary
    print("\n=== Avatar State Summary ===\n")
    
    state = jupiter.get_state_summary()
    for key, value in state.items():
        print(f"{key}: {value}")
    
    print("\n✓ JUPITER Avatar System operational!")
    print("🎯 G.3.2 COMPLETE - AI companion ready for VR!")
