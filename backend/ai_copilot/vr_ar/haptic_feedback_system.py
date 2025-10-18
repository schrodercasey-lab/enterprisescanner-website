"""
JUPITER Haptic Feedback System
Module G.3.7: Tactile VR Interactions for Cybersecurity

Provides tactile feedback for VR threat interactions:
- Severity-based vibration patterns (critical threats = intense vibration)
- Gesture confirmation feedback (haptic click when gesture recognized)
- Object collision feedback (feel virtual threat nodes)
- Alert notifications (haptic pulse for new threats)
- Investigation progress feedback (haptic rhythm for automated tasks)

Supported Devices:
- Meta Quest 3 (hand controllers)
- HTC Vive (hand controllers)
- Valve Index (finger tracking + haptic)
- PlayStation VR2 (adaptive triggers)

Author: Enterprise Scanner Development Team
Date: October 17, 2025
Version: 1.0.0
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class HapticDeviceType(Enum):
    """Supported VR controller types"""
    META_QUEST_3 = "meta_quest_3"
    HTC_VIVE = "htc_vive"
    VALVE_INDEX = "valve_index"
    PLAYSTATION_VR2 = "playstation_vr2"
    GENERIC = "generic"


class HapticIntensity(Enum):
    """Haptic feedback intensity levels"""
    NONE = 0
    VERY_LIGHT = 1
    LIGHT = 2
    MEDIUM = 3
    STRONG = 4
    VERY_STRONG = 5
    MAXIMUM = 6


class VibrationPattern(Enum):
    """Pre-defined vibration patterns"""
    SINGLE_PULSE = "single_pulse"
    DOUBLE_PULSE = "double_pulse"
    TRIPLE_PULSE = "triple_pulse"
    CONTINUOUS = "continuous"
    WAVE = "wave"
    HEARTBEAT = "heartbeat"
    ALERT = "alert"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    CRITICAL = "critical"


class ThreatSeverity(Enum):
    """Threat severity levels for haptic mapping"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class GestureType(Enum):
    """Gesture types for haptic confirmation"""
    POINT = "point"
    GRAB = "grab"
    SWIPE = "swipe"
    PINCH = "pinch"
    ROTATE = "rotate"
    PUSH = "push"
    PULL = "pull"
    THROW = "throw"


@dataclass
class HapticEvent:
    """Haptic feedback event"""
    event_id: str
    device_type: HapticDeviceType
    hand: str  # "left" or "right"
    intensity: HapticIntensity
    duration_ms: int
    pattern: VibrationPattern
    frequency_hz: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HapticPattern:
    """Custom haptic vibration pattern"""
    pattern_id: str
    name: str
    pulses: List[Tuple[int, int]]  # List of (duration_ms, intensity) tuples
    repeat_count: int = 1
    delay_between_repeats_ms: int = 0


@dataclass
class ThreatHapticProfile:
    """Haptic profile for threat types"""
    threat_type: str
    severity: ThreatSeverity
    pattern: VibrationPattern
    intensity: HapticIntensity
    duration_ms: int
    continuous: bool = False


# ============================================================================
# HAPTIC CONTROLLER
# ============================================================================

class HapticController:
    """
    Main haptic feedback controller
    
    Manages haptic feedback for VR controllers:
    - Device capability detection
    - Vibration pattern generation
    - Intensity scaling
    - Multi-device synchronization
    """
    
    def __init__(self):
        self.devices: Dict[str, HapticDeviceType] = {}
        self.device_capabilities: Dict[str, Dict[str, Any]] = {}
        self.active_patterns: Dict[str, HapticPattern] = {}
        
        # Device-specific settings
        self.max_frequency_hz = {
            HapticDeviceType.META_QUEST_3: 320,
            HapticDeviceType.HTC_VIVE: 160,
            HapticDeviceType.VALVE_INDEX: 256,
            HapticDeviceType.PLAYSTATION_VR2: 400,
            HapticDeviceType.GENERIC: 160
        }
        
        self.max_intensity = {
            HapticDeviceType.META_QUEST_3: HapticIntensity.VERY_STRONG,
            HapticDeviceType.HTC_VIVE: HapticIntensity.STRONG,
            HapticDeviceType.VALVE_INDEX: HapticIntensity.MAXIMUM,
            HapticDeviceType.PLAYSTATION_VR2: HapticIntensity.MAXIMUM,
            HapticDeviceType.GENERIC: HapticIntensity.MEDIUM
        }
        
        # Pattern library
        self._initialize_pattern_library()
        
        logger.info("Haptic controller initialized")
    
    def _initialize_pattern_library(self):
        """Initialize pre-defined haptic patterns"""
        self.active_patterns = {
            # Simple patterns
            VibrationPattern.SINGLE_PULSE.value: HapticPattern(
                pattern_id="single_pulse",
                name="Single Pulse",
                pulses=[(100, 4)]  # 100ms at intensity 4
            ),
            VibrationPattern.DOUBLE_PULSE.value: HapticPattern(
                pattern_id="double_pulse",
                name="Double Pulse",
                pulses=[(80, 4), (80, 4)],
                delay_between_repeats_ms=100
            ),
            VibrationPattern.TRIPLE_PULSE.value: HapticPattern(
                pattern_id="triple_pulse",
                name="Triple Pulse",
                pulses=[(60, 4), (60, 4), (60, 4)],
                delay_between_repeats_ms=80
            ),
            
            # Alert patterns
            VibrationPattern.ALERT.value: HapticPattern(
                pattern_id="alert",
                name="Alert Pattern",
                pulses=[(200, 5), (100, 0), (200, 5)],
                repeat_count=2
            ),
            VibrationPattern.WARNING.value: HapticPattern(
                pattern_id="warning",
                name="Warning Pattern",
                pulses=[(150, 4), (50, 0), (150, 4), (50, 0), (150, 4)]
            ),
            VibrationPattern.CRITICAL.value: HapticPattern(
                pattern_id="critical",
                name="Critical Threat",
                pulses=[(300, 6), (100, 3), (300, 6)],
                repeat_count=3,
                delay_between_repeats_ms=200
            ),
            
            # Special patterns
            VibrationPattern.HEARTBEAT.value: HapticPattern(
                pattern_id="heartbeat",
                name="Heartbeat",
                pulses=[(80, 5), (50, 0), (120, 4)],
                repeat_count=3,
                delay_between_repeats_ms=600
            ),
            VibrationPattern.WAVE.value: HapticPattern(
                pattern_id="wave",
                name="Wave",
                pulses=[
                    (100, 2), (100, 3), (100, 4), (100, 5), 
                    (100, 6), (100, 5), (100, 4), (100, 3)
                ]
            ),
            VibrationPattern.SUCCESS.value: HapticPattern(
                pattern_id="success",
                name="Success",
                pulses=[(50, 3), (50, 4), (100, 5)]
            ),
            VibrationPattern.ERROR.value: HapticPattern(
                pattern_id="error",
                name="Error",
                pulses=[(200, 5), (100, 0), (200, 5), (100, 0), (200, 5)]
            )
        }
    
    async def register_device(self, device_id: str, 
                            device_type: HapticDeviceType) -> bool:
        """
        Register haptic device
        
        Args:
            device_id: Unique device identifier
            device_type: Type of VR controller
            
        Returns:
            True if successfully registered
        """
        self.devices[device_id] = device_type
        
        # Set device capabilities
        self.device_capabilities[device_id] = {
            'max_frequency': self.max_frequency_hz[device_type],
            'max_intensity': self.max_intensity[device_type].value,
            'supports_finger_tracking': device_type == HapticDeviceType.VALVE_INDEX,
            'supports_adaptive_triggers': device_type == HapticDeviceType.PLAYSTATION_VR2,
            'supports_dual_actuators': device_type in [
                HapticDeviceType.META_QUEST_3,
                HapticDeviceType.PLAYSTATION_VR2
            ]
        }
        
        logger.info(f"Registered haptic device: {device_id} ({device_type.value})")
        return True
    
    async def trigger_haptic(self, device_id: str, hand: str,
                           pattern: VibrationPattern,
                           intensity: HapticIntensity = HapticIntensity.MEDIUM,
                           duration_ms: Optional[int] = None) -> str:
        """
        Trigger haptic feedback
        
        Args:
            device_id: Target device
            hand: "left" or "right"
            pattern: Vibration pattern
            intensity: Feedback intensity
            duration_ms: Duration (overrides pattern default)
            
        Returns:
            Event ID
        """
        if device_id not in self.devices:
            logger.warning(f"Device not registered: {device_id}")
            return None
        
        device_type = self.devices[device_id]
        
        # Scale intensity to device capabilities
        max_intensity = self.device_capabilities[device_id]['max_intensity']
        scaled_intensity = min(intensity.value, max_intensity)
        
        # Get pattern
        haptic_pattern = self.active_patterns.get(pattern.value)
        if not haptic_pattern:
            logger.warning(f"Pattern not found: {pattern.value}")
            return None
        
        # Calculate total duration if not specified
        if duration_ms is None:
            duration_ms = sum(pulse[0] for pulse in haptic_pattern.pulses)
            duration_ms *= haptic_pattern.repeat_count
        
        # Create haptic event
        event = HapticEvent(
            event_id=f"haptic_{datetime.now().timestamp()}",
            device_type=device_type,
            hand=hand,
            intensity=HapticIntensity(scaled_intensity),
            duration_ms=duration_ms,
            pattern=pattern
        )
        
        # Execute haptic feedback
        await self._execute_haptic_pattern(event, haptic_pattern)
        
        logger.debug(f"Triggered haptic: {pattern.value} on {hand} hand")
        return event.event_id
    
    async def _execute_haptic_pattern(self, event: HapticEvent, 
                                     pattern: HapticPattern):
        """Execute haptic vibration pattern"""
        # In production, this would send commands to VR hardware
        # For now, we simulate the execution
        
        for repeat in range(pattern.repeat_count):
            for duration_ms, intensity in pattern.pulses:
                # Scale intensity to event intensity
                scaled_intensity = min(
                    intensity * (event.intensity.value / HapticIntensity.MEDIUM.value),
                    HapticIntensity.MAXIMUM.value
                )
                
                # Simulate vibration
                await asyncio.sleep(duration_ms / 1000.0)
            
            if repeat < pattern.repeat_count - 1:
                await asyncio.sleep(pattern.delay_between_repeats_ms / 1000.0)
    
    async def trigger_custom_pattern(self, device_id: str, hand: str,
                                    pulses: List[Tuple[int, int]]) -> str:
        """
        Trigger custom haptic pattern
        
        Args:
            device_id: Target device
            hand: "left" or "right"
            pulses: List of (duration_ms, intensity) tuples
            
        Returns:
            Event ID
        """
        custom_pattern = HapticPattern(
            pattern_id="custom",
            name="Custom Pattern",
            pulses=pulses
        )
        
        event = HapticEvent(
            event_id=f"haptic_{datetime.now().timestamp()}",
            device_type=self.devices.get(device_id, HapticDeviceType.GENERIC),
            hand=hand,
            intensity=HapticIntensity.MEDIUM,
            duration_ms=sum(p[0] for p in pulses),
            pattern=VibrationPattern.CONTINUOUS
        )
        
        await self._execute_haptic_pattern(event, custom_pattern)
        return event.event_id
    
    async def stop_haptic(self, device_id: str, hand: str):
        """Stop all haptic feedback on device"""
        # In production, send stop command to VR hardware
        logger.debug(f"Stopped haptic on {device_id} {hand} hand")
    
    def get_device_capabilities(self, device_id: str) -> Dict[str, Any]:
        """Get device haptic capabilities"""
        return self.device_capabilities.get(device_id, {})


# ============================================================================
# THREAT HAPTICS
# ============================================================================

class ThreatHaptics:
    """
    Haptic feedback for cybersecurity threats
    
    Maps threat severity to haptic patterns:
    - Critical threats = intense, rapid vibration
    - Medium threats = moderate pulsing
    - Low threats = gentle notification
    """
    
    def __init__(self, haptic_controller: HapticController):
        self.haptic_controller = haptic_controller
        
        # Threat haptic profiles
        self.threat_profiles: Dict[ThreatSeverity, ThreatHapticProfile] = {
            ThreatSeverity.INFO: ThreatHapticProfile(
                threat_type="info",
                severity=ThreatSeverity.INFO,
                pattern=VibrationPattern.SINGLE_PULSE,
                intensity=HapticIntensity.VERY_LIGHT,
                duration_ms=50
            ),
            ThreatSeverity.LOW: ThreatHapticProfile(
                threat_type="low",
                severity=ThreatSeverity.LOW,
                pattern=VibrationPattern.SINGLE_PULSE,
                intensity=HapticIntensity.LIGHT,
                duration_ms=100
            ),
            ThreatSeverity.MEDIUM: ThreatHapticProfile(
                threat_type="medium",
                severity=ThreatSeverity.MEDIUM,
                pattern=VibrationPattern.DOUBLE_PULSE,
                intensity=HapticIntensity.MEDIUM,
                duration_ms=200
            ),
            ThreatSeverity.HIGH: ThreatHapticProfile(
                threat_type="high",
                severity=ThreatSeverity.HIGH,
                pattern=VibrationPattern.WARNING,
                intensity=HapticIntensity.STRONG,
                duration_ms=400
            ),
            ThreatSeverity.CRITICAL: ThreatHapticProfile(
                threat_type="critical",
                severity=ThreatSeverity.CRITICAL,
                pattern=VibrationPattern.CRITICAL,
                intensity=HapticIntensity.VERY_STRONG,
                duration_ms=800,
                continuous=True
            ),
            ThreatSeverity.EMERGENCY: ThreatHapticProfile(
                threat_type="emergency",
                severity=ThreatSeverity.EMERGENCY,
                pattern=VibrationPattern.CRITICAL,
                intensity=HapticIntensity.MAXIMUM,
                duration_ms=1000,
                continuous=True
            )
        }
        
        # Threat interaction feedback
        self.interaction_feedback = {
            'hover': (VibrationPattern.SINGLE_PULSE, HapticIntensity.VERY_LIGHT, 30),
            'select': (VibrationPattern.SINGLE_PULSE, HapticIntensity.MEDIUM, 50),
            'isolate': (VibrationPattern.DOUBLE_PULSE, HapticIntensity.STRONG, 150),
            'remediate': (VibrationPattern.SUCCESS, HapticIntensity.MEDIUM, 200),
            'escalate': (VibrationPattern.ALERT, HapticIntensity.STRONG, 300)
        }
    
    async def notify_threat_detected(self, device_id: str, hand: str,
                                    threat_severity: ThreatSeverity) -> str:
        """
        Haptic notification for new threat detection
        
        Args:
            device_id: VR controller
            hand: Which hand to vibrate
            threat_severity: Severity of detected threat
            
        Returns:
            Event ID
        """
        profile = self.threat_profiles[threat_severity]
        
        return await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=profile.pattern,
            intensity=profile.intensity,
            duration_ms=profile.duration_ms
        )
    
    async def feedback_threat_interaction(self, device_id: str, hand: str,
                                         interaction_type: str,
                                         threat_severity: ThreatSeverity) -> str:
        """
        Haptic feedback for threat interaction
        
        Args:
            device_id: VR controller
            hand: Which hand
            interaction_type: Type of interaction (hover, select, etc.)
            threat_severity: Severity of threat being interacted with
            
        Returns:
            Event ID
        """
        if interaction_type not in self.interaction_feedback:
            logger.warning(f"Unknown interaction type: {interaction_type}")
            return None
        
        pattern, base_intensity, duration = self.interaction_feedback[interaction_type]
        
        # Scale intensity based on threat severity
        severity_multiplier = {
            ThreatSeverity.INFO: 0.5,
            ThreatSeverity.LOW: 0.7,
            ThreatSeverity.MEDIUM: 1.0,
            ThreatSeverity.HIGH: 1.3,
            ThreatSeverity.CRITICAL: 1.6,
            ThreatSeverity.EMERGENCY: 2.0
        }
        
        multiplier = severity_multiplier.get(threat_severity, 1.0)
        scaled_intensity = min(
            int(base_intensity.value * multiplier),
            HapticIntensity.MAXIMUM.value
        )
        
        return await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=pattern,
            intensity=HapticIntensity(scaled_intensity),
            duration_ms=duration
        )
    
    async def feedback_threat_proximity(self, device_id: str, hand: str,
                                       distance: float, 
                                       threat_severity: ThreatSeverity):
        """
        Continuous haptic feedback based on proximity to threat
        
        Args:
            device_id: VR controller
            hand: Which hand
            distance: Distance to threat (0.0 = touching, 1.0 = far)
            threat_severity: Threat severity
        """
        if distance > 1.0:
            return  # Too far for haptic feedback
        
        # Calculate intensity based on proximity
        proximity_intensity = int((1.0 - distance) * HapticIntensity.VERY_STRONG.value)
        
        # Frequency increases with severity and proximity
        base_pulse_duration = 200
        pulse_duration = int(base_pulse_duration * distance)
        
        # Create proximity pulse pattern
        pulses = [(pulse_duration, proximity_intensity)]
        
        await self.haptic_controller.trigger_custom_pattern(
            device_id=device_id,
            hand=hand,
            pulses=pulses
        )
    
    async def feedback_attack_path(self, device_id: str, hand: str,
                                  hop_count: int, severity: ThreatSeverity):
        """
        Haptic feedback for tracing attack paths
        
        Number of pulses = number of hops in attack path
        
        Args:
            device_id: VR controller
            hand: Which hand
            hop_count: Number of hops in attack path
            severity: Overall path severity
        """
        # Create pulse pattern for each hop
        base_intensity = self.threat_profiles[severity].intensity.value
        pulses = [
            (80, base_intensity) for _ in range(min(hop_count, 10))
        ]
        
        await self.haptic_controller.trigger_custom_pattern(
            device_id=device_id,
            hand=hand,
            pulses=pulses
        )
    
    async def feedback_remediation_progress(self, device_id: str, hand: str,
                                           progress_percent: float):
        """
        Rhythmic haptic feedback during automated remediation
        
        Pulse frequency increases as remediation progresses
        
        Args:
            device_id: VR controller
            hand: Which hand
            progress_percent: Remediation progress (0.0 to 1.0)
        """
        # Calculate pulse rate based on progress
        base_interval = 500  # ms
        interval = int(base_interval * (1.0 - progress_percent * 0.7))
        
        # Single pulse at current progress rate
        await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=VibrationPattern.SINGLE_PULSE,
            intensity=HapticIntensity.LIGHT,
            duration_ms=50
        )
        
        # Schedule next pulse
        await asyncio.sleep(interval / 1000.0)


# ============================================================================
# GESTURE HAPTICS
# ============================================================================

class GestureHaptics:
    """
    Haptic feedback for gesture recognition
    
    Provides tactile confirmation when gestures are recognized:
    - Point gesture = directional pulse
    - Grab gesture = gripping sensation
    - Swipe gesture = sliding vibration
    - Pinch gesture = pinch confirmation
    """
    
    def __init__(self, haptic_controller: HapticController):
        self.haptic_controller = haptic_controller
        
        # Gesture feedback patterns
        self.gesture_patterns = {
            GestureType.POINT: {
                'start': (VibrationPattern.SINGLE_PULSE, HapticIntensity.LIGHT, 50),
                'confirm': (VibrationPattern.DOUBLE_PULSE, HapticIntensity.MEDIUM, 100)
            },
            GestureType.GRAB: {
                'start': (VibrationPattern.SINGLE_PULSE, HapticIntensity.MEDIUM, 100),
                'holding': (VibrationPattern.CONTINUOUS, HapticIntensity.LIGHT, 50),
                'release': (VibrationPattern.SINGLE_PULSE, HapticIntensity.LIGHT, 50)
            },
            GestureType.SWIPE: {
                'start': (VibrationPattern.WAVE, HapticIntensity.LIGHT, 200)
            },
            GestureType.PINCH: {
                'start': (VibrationPattern.SINGLE_PULSE, HapticIntensity.MEDIUM, 80),
                'confirm': (VibrationPattern.SINGLE_PULSE, HapticIntensity.STRONG, 50)
            },
            GestureType.ROTATE: {
                'start': (VibrationPattern.WAVE, HapticIntensity.LIGHT, 150)
            },
            GestureType.PUSH: {
                'start': (VibrationPattern.SINGLE_PULSE, HapticIntensity.STRONG, 100)
            },
            GestureType.PULL: {
                'start': (VibrationPattern.DOUBLE_PULSE, HapticIntensity.MEDIUM, 120)
            },
            GestureType.THROW: {
                'start': (VibrationPattern.WAVE, HapticIntensity.STRONG, 200)
            }
        }
    
    async def feedback_gesture_start(self, device_id: str, hand: str,
                                    gesture_type: GestureType) -> str:
        """
        Haptic feedback when gesture starts
        
        Args:
            device_id: VR controller
            hand: Which hand
            gesture_type: Type of gesture being performed
            
        Returns:
            Event ID
        """
        if gesture_type not in self.gesture_patterns:
            return None
        
        pattern_data = self.gesture_patterns[gesture_type].get('start')
        if not pattern_data:
            return None
        
        pattern, intensity, duration = pattern_data
        
        return await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=pattern,
            intensity=intensity,
            duration_ms=duration
        )
    
    async def feedback_gesture_confirm(self, device_id: str, hand: str,
                                      gesture_type: GestureType,
                                      success: bool = True) -> str:
        """
        Haptic feedback when gesture is recognized/confirmed
        
        Args:
            device_id: VR controller
            hand: Which hand
            gesture_type: Type of gesture
            success: Whether gesture was successful
            
        Returns:
            Event ID
        """
        if success:
            pattern = VibrationPattern.SUCCESS
            intensity = HapticIntensity.MEDIUM
        else:
            pattern = VibrationPattern.ERROR
            intensity = HapticIntensity.LIGHT
        
        return await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=pattern,
            intensity=intensity,
            duration_ms=100
        )
    
    async def feedback_object_collision(self, device_id: str, hand: str,
                                       collision_force: float):
        """
        Haptic feedback for virtual object collision
        
        Args:
            device_id: VR controller
            hand: Which hand
            collision_force: Force of collision (0.0 to 1.0)
        """
        # Scale intensity by collision force
        intensity = int(collision_force * HapticIntensity.VERY_STRONG.value)
        intensity = min(intensity, HapticIntensity.MAXIMUM.value)
        
        # Duration proportional to force
        duration = int(50 + (collision_force * 150))
        
        await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=VibrationPattern.SINGLE_PULSE,
            intensity=HapticIntensity(intensity),
            duration_ms=duration
        )
    
    async def feedback_grab_holding(self, device_id: str, hand: str,
                                   object_weight: float = 0.5):
        """
        Continuous haptic feedback while holding virtual object
        
        Args:
            device_id: VR controller
            hand: Which hand
            object_weight: Perceived weight (0.0 to 1.0)
        """
        # Light continuous vibration representing object weight
        intensity = int(HapticIntensity.VERY_LIGHT.value + 
                       object_weight * (HapticIntensity.MEDIUM.value - HapticIntensity.VERY_LIGHT.value))
        
        await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=VibrationPattern.CONTINUOUS,
            intensity=HapticIntensity(intensity),
            duration_ms=100
        )
    
    async def feedback_button_press(self, device_id: str, hand: str):
        """Haptic feedback for virtual button press"""
        await self.haptic_controller.trigger_haptic(
            device_id=device_id,
            hand=hand,
            pattern=VibrationPattern.SINGLE_PULSE,
            intensity=HapticIntensity.MEDIUM,
            duration_ms=50
        )
    
    async def feedback_slider_move(self, device_id: str, hand: str,
                                  position: float):
        """
        Haptic feedback for slider/dial movement
        
        Provides notched feedback at regular intervals
        
        Args:
            device_id: VR controller
            hand: Which hand
            position: Slider position (0.0 to 1.0)
        """
        # Trigger pulse at 10% increments
        notch_size = 0.1
        if position % notch_size < 0.05:  # Near a notch
            await self.haptic_controller.trigger_haptic(
                device_id=device_id,
                hand=hand,
                pattern=VibrationPattern.SINGLE_PULSE,
                intensity=HapticIntensity.LIGHT,
                duration_ms=30
            )


# ============================================================================
# HAPTIC FEEDBACK SYSTEM (MAIN)
# ============================================================================

class HapticFeedbackSystem:
    """
    Main haptic feedback system integrating all components
    
    Usage:
        haptic_system = HapticFeedbackSystem()
        await haptic_system.register_controller("left_controller", HapticDeviceType.META_QUEST_3)
        await haptic_system.threat_detected("left_controller", "left", ThreatSeverity.CRITICAL)
    """
    
    def __init__(self):
        self.haptic_controller = HapticController()
        self.threat_haptics = ThreatHaptics(self.haptic_controller)
        self.gesture_haptics = GestureHaptics(self.haptic_controller)
        
        # Statistics
        self.total_haptic_events = 0
        self.events_by_type: Dict[str, int] = {}
        
        logger.info("Haptic feedback system initialized")
    
    async def register_controller(self, controller_id: str, 
                                 device_type: HapticDeviceType) -> bool:
        """Register VR controller for haptic feedback"""
        return await self.haptic_controller.register_device(controller_id, device_type)
    
    # ========================================================================
    # THREAT HAPTICS
    # ========================================================================
    
    async def threat_detected(self, controller_id: str, hand: str,
                            severity: ThreatSeverity) -> str:
        """Notify user of detected threat via haptics"""
        event_id = await self.threat_haptics.notify_threat_detected(
            controller_id, hand, severity
        )
        self._track_event('threat_detected')
        return event_id
    
    async def threat_interaction(self, controller_id: str, hand: str,
                               interaction: str, severity: ThreatSeverity) -> str:
        """Haptic feedback for threat interaction"""
        event_id = await self.threat_haptics.feedback_threat_interaction(
            controller_id, hand, interaction, severity
        )
        self._track_event(f'threat_{interaction}')
        return event_id
    
    async def threat_proximity(self, controller_id: str, hand: str,
                             distance: float, severity: ThreatSeverity):
        """Continuous proximity feedback"""
        await self.threat_haptics.feedback_threat_proximity(
            controller_id, hand, distance, severity
        )
    
    # ========================================================================
    # GESTURE HAPTICS
    # ========================================================================
    
    async def gesture_started(self, controller_id: str, hand: str,
                            gesture: GestureType) -> str:
        """Haptic feedback when gesture starts"""
        event_id = await self.gesture_haptics.feedback_gesture_start(
            controller_id, hand, gesture
        )
        self._track_event(f'gesture_{gesture.value}_start')
        return event_id
    
    async def gesture_confirmed(self, controller_id: str, hand: str,
                              gesture: GestureType, success: bool = True) -> str:
        """Haptic feedback when gesture confirmed"""
        event_id = await self.gesture_haptics.feedback_gesture_confirm(
            controller_id, hand, gesture, success
        )
        self._track_event(f'gesture_{gesture.value}_confirm')
        return event_id
    
    async def object_collision(self, controller_id: str, hand: str,
                             force: float):
        """Haptic feedback for object collision"""
        await self.gesture_haptics.feedback_object_collision(
            controller_id, hand, force
        )
        self._track_event('collision')
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def _track_event(self, event_type: str):
        """Track haptic event for statistics"""
        self.total_haptic_events += 1
        self.events_by_type[event_type] = self.events_by_type.get(event_type, 0) + 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get haptic system statistics"""
        return {
            'total_events': self.total_haptic_events,
            'events_by_type': self.events_by_type,
            'registered_devices': len(self.haptic_controller.devices)
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_haptic_feedback():
    """Example: Haptic feedback during threat investigation"""
    
    # Initialize system
    haptic_system = HapticFeedbackSystem()
    
    # Register VR controllers
    await haptic_system.register_controller("left_controller", HapticDeviceType.META_QUEST_3)
    await haptic_system.register_controller("right_controller", HapticDeviceType.META_QUEST_3)
    
    # Example 1: Critical threat detected
    print("Scenario 1: Critical ransomware detected")
    await haptic_system.threat_detected(
        controller_id="right_controller",
        hand="right",
        severity=ThreatSeverity.CRITICAL
    )
    
    await asyncio.sleep(1)
    
    # Example 2: User points at threat
    print("Scenario 2: User points at threat")
    await haptic_system.gesture_started(
        controller_id="right_controller",
        hand="right",
        gesture=GestureType.POINT
    )
    
    await asyncio.sleep(0.5)
    
    # Example 3: User selects threat for investigation
    print("Scenario 3: User selects threat")
    await haptic_system.threat_interaction(
        controller_id="right_controller",
        hand="right",
        interaction="select",
        severity=ThreatSeverity.CRITICAL
    )
    
    await asyncio.sleep(1)
    
    # Example 4: Proximity to threat
    print("Scenario 4: Moving closer to threat")
    for distance in [1.0, 0.7, 0.4, 0.1]:
        await haptic_system.threat_proximity(
            controller_id="right_controller",
            hand="right",
            distance=distance,
            severity=ThreatSeverity.HIGH
        )
        await asyncio.sleep(0.3)
    
    # Example 5: Grab and isolate threat
    print("Scenario 5: Grab and isolate threat")
    await haptic_system.gesture_started(
        controller_id="right_controller",
        hand="right",
        gesture=GestureType.GRAB
    )
    
    await asyncio.sleep(0.5)
    
    await haptic_system.threat_interaction(
        controller_id="right_controller",
        hand="right",
        interaction="isolate",
        severity=ThreatSeverity.CRITICAL
    )
    
    # Print statistics
    stats = haptic_system.get_statistics()
    print(f"\nHaptic Statistics: {stats}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_haptic_feedback())
