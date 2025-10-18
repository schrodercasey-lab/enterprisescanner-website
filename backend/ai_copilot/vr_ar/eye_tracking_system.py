"""
JUPITER Eye Tracking Analytics System
Module G.3.8: Gaze-Based Interaction and Attention Analytics

Provides advanced eye tracking for VR cybersecurity:
- Gaze-based interaction (look at threat to select)
- Attention heatmaps (where analysts focus most)
- Eye-controlled navigation (look to move)
- Cognitive load detection (pupil dilation analysis)
- UI optimization (detect hard-to-read elements)
- Expertise level detection (gaze patterns of experts vs. novices)

Supported Devices:
- Meta Quest Pro (eye tracking built-in)
- Apple Vision Pro (high-precision eye tracking)
- Valve Index with eye tracking module
- HTC Vive Pro Eye

Author: Enterprise Scanner Development Team
Date: October 17, 2025
Version: 1.0.0
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class EyeTrackingDevice(Enum):
    """Supported eye tracking devices"""
    META_QUEST_PRO = "meta_quest_pro"
    APPLE_VISION_PRO = "apple_vision_pro"
    VALVE_INDEX_EYE = "valve_index_eye"
    HTC_VIVE_PRO_EYE = "htc_vive_pro_eye"
    GENERIC = "generic"


class GazeTarget(Enum):
    """Types of objects user can gaze at"""
    THREAT_NODE = "threat_node"
    NETWORK_DEVICE = "network_device"
    ALERT_PANEL = "alert_panel"
    MENU_ITEM = "menu_item"
    JUPITER_AVATAR = "jupiter_avatar"
    DATA_VISUALIZATION = "data_visualization"
    EMPTY_SPACE = "empty_space"


class InteractionMode(Enum):
    """Eye-based interaction modes"""
    DWELL_SELECT = "dwell_select"  # Look for X seconds to select
    BLINK_SELECT = "blink_select"  # Blink to select
    GAZE_POINT = "gaze_point"  # Just point, no selection
    SMOOTH_PURSUIT = "smooth_pursuit"  # Follow moving object
    SACCADE = "saccade"  # Quick eye movement


class AttentionLevel(Enum):
    """User attention/focus levels"""
    HIGHLY_FOCUSED = "highly_focused"
    FOCUSED = "focused"
    NORMAL = "normal"
    DISTRACTED = "distracted"
    FATIGUED = "fatigued"


@dataclass
class EyeGazeData:
    """Raw eye gaze data from VR headset"""
    timestamp: datetime
    left_eye_position: Tuple[float, float, float]  # (x, y, z) in VR space
    right_eye_position: Tuple[float, float, float]
    left_eye_direction: Tuple[float, float, float]  # Direction vector
    right_eye_direction: Tuple[float, float, float]
    combined_gaze_point: Tuple[float, float, float]  # Where user is looking
    pupil_diameter_left: float  # mm
    pupil_diameter_right: float
    confidence: float  # 0.0 to 1.0


@dataclass
class GazeEvent:
    """Processed gaze event"""
    event_id: str
    user_id: str
    timestamp: datetime
    gaze_target: Optional[str]  # ID of object being gazed at
    target_type: GazeTarget
    gaze_duration: float  # seconds
    interaction_mode: InteractionMode
    attention_level: AttentionLevel


@dataclass
class AttentionMetrics:
    """Attention and cognitive load metrics"""
    average_fixation_duration: float  # seconds
    saccade_frequency: float  # per minute
    pupil_diameter_avg: float  # mm
    pupil_dilation_rate: float  # change per second
    blink_rate: float  # per minute
    gaze_stability: float  # 0.0 to 1.0 (higher = more stable)
    cognitive_load: float  # 0.0 to 1.0 (estimated)
    attention_level: AttentionLevel


@dataclass
class HeatmapPoint:
    """Point in attention heatmap"""
    position: Tuple[float, float, float]  # VR space coordinates
    dwell_time: float  # Total time gazed at this point
    visit_count: int  # Number of times gazed here
    importance_score: float  # Calculated importance


# ============================================================================
# EYE TRACKER
# ============================================================================

class EyeTracker:
    """
    Core eye tracking system
    
    Processes raw eye gaze data:
    - Calibration and validation
    - Gaze point calculation
    - Fixation detection
    - Saccade detection
    - Blink detection
    """
    
    def __init__(self, device_type: EyeTrackingDevice):
        self.device_type = device_type
        self.is_calibrated = False
        self.calibration_quality = 0.0
        
        # Device capabilities
        self.sampling_rate_hz = {
            EyeTrackingDevice.META_QUEST_PRO: 90,
            EyeTrackingDevice.APPLE_VISION_PRO: 120,
            EyeTrackingDevice.VALVE_INDEX_EYE: 120,
            EyeTrackingDevice.HTC_VIVE_PRO_EYE: 120,
            EyeTrackingDevice.GENERIC: 60
        }[device_type]
        
        # Gaze history for smoothing
        self.gaze_history: deque = deque(maxlen=10)
        
        # Fixation detection parameters
        self.fixation_threshold_degrees = 1.0  # Max eye movement for fixation
        self.fixation_min_duration_ms = 100  # Min duration to count as fixation
        
        # Current state
        self.current_fixation_start: Optional[datetime] = None
        self.current_fixation_point: Optional[Tuple[float, float, float]] = None
        
        # Statistics
        self.total_samples = 0
        self.total_fixations = 0
        self.total_saccades = 0
        self.total_blinks = 0
        
        logger.info(f"Eye tracker initialized: {device_type.value} @ {self.sampling_rate_hz} Hz")
    
    async def calibrate(self, calibration_points: List[Tuple[float, float, float]]) -> float:
        """
        Calibrate eye tracking
        
        Args:
            calibration_points: List of 3D points to look at for calibration
            
        Returns:
            Calibration quality score (0.0 to 1.0)
        """
        logger.info(f"Starting calibration with {len(calibration_points)} points...")
        
        # In production, this would run actual calibration routine
        # For now, simulate calibration
        await asyncio.sleep(len(calibration_points) * 0.5)  # Simulate time
        
        # Simulate calibration quality
        self.calibration_quality = 0.85 + (np.random.random() * 0.15)
        self.is_calibrated = True
        
        logger.info(f"Calibration complete. Quality: {self.calibration_quality:.2f}")
        return self.calibration_quality
    
    async def process_gaze_sample(self, gaze_data: EyeGazeData) -> Optional[GazeEvent]:
        """
        Process raw gaze sample
        
        Args:
            gaze_data: Raw gaze data from headset
            
        Returns:
            GazeEvent if significant event detected, None otherwise
        """
        self.total_samples += 1
        
        # Add to history
        self.gaze_history.append(gaze_data)
        
        # Smooth gaze point using recent history
        smoothed_gaze = self._smooth_gaze_point()
        
        # Detect fixation
        if self._is_fixation(smoothed_gaze):
            if self.current_fixation_start is None:
                # Start new fixation
                self.current_fixation_start = gaze_data.timestamp
                self.current_fixation_point = smoothed_gaze
            else:
                # Continue existing fixation
                fixation_duration = (gaze_data.timestamp - self.current_fixation_start).total_seconds()
                
                # Check if fixation is long enough for dwell selection
                if fixation_duration >= 0.8:  # 800ms dwell time
                    return GazeEvent(
                        event_id=f"gaze_{gaze_data.timestamp.timestamp()}",
                        user_id="",  # To be filled by caller
                        timestamp=gaze_data.timestamp,
                        gaze_target=None,  # To be determined by hit testing
                        target_type=GazeTarget.EMPTY_SPACE,
                        gaze_duration=fixation_duration,
                        interaction_mode=InteractionMode.DWELL_SELECT,
                        attention_level=AttentionLevel.FOCUSED
                    )
        else:
            # Not a fixation - could be saccade
            if self.current_fixation_start is not None:
                # End of fixation
                self.total_fixations += 1
                self.current_fixation_start = None
                self.current_fixation_point = None
                
                # Detect saccade
                if len(self.gaze_history) >= 2:
                    prev_gaze = self.gaze_history[-2]
                    movement = self._calculate_angular_distance(
                        prev_gaze.combined_gaze_point,
                        gaze_data.combined_gaze_point
                    )
                    
                    if movement > 5.0:  # Degrees
                        self.total_saccades += 1
        
        return None
    
    def _smooth_gaze_point(self) -> Tuple[float, float, float]:
        """Smooth gaze point using exponential moving average"""
        if not self.gaze_history:
            return (0.0, 0.0, 0.0)
        
        # Weighted average (more recent = higher weight)
        weights = np.exp(np.linspace(-1, 0, len(self.gaze_history)))
        weights /= weights.sum()
        
        smoothed = np.zeros(3)
        for i, gaze in enumerate(self.gaze_history):
            smoothed += np.array(gaze.combined_gaze_point) * weights[i]
        
        return tuple(smoothed)
    
    def _is_fixation(self, gaze_point: Tuple[float, float, float]) -> bool:
        """Check if current gaze is part of a fixation"""
        if self.current_fixation_point is None:
            return True  # First point is always start of potential fixation
        
        # Calculate angular distance from fixation center
        distance = self._calculate_angular_distance(
            self.current_fixation_point,
            gaze_point
        )
        
        return distance < self.fixation_threshold_degrees
    
    def _calculate_angular_distance(self, point1: Tuple[float, float, float],
                                   point2: Tuple[float, float, float]) -> float:
        """Calculate angular distance between two gaze points (in degrees)"""
        # Convert to unit vectors
        v1 = np.array(point1)
        v2 = np.array(point2)
        
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-6)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-6)
        
        # Calculate angle
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg
    
    async def detect_blink(self, gaze_data: EyeGazeData) -> bool:
        """Detect eye blink based on confidence drop"""
        # Blink detection: confidence drops below threshold
        if gaze_data.confidence < 0.3:
            self.total_blinks += 1
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get eye tracking statistics"""
        return {
            'device': self.device_type.value,
            'sampling_rate': self.sampling_rate_hz,
            'calibrated': self.is_calibrated,
            'calibration_quality': self.calibration_quality,
            'total_samples': self.total_samples,
            'total_fixations': self.total_fixations,
            'total_saccades': self.total_saccades,
            'total_blinks': self.total_blinks
        }


# ============================================================================
# GAZE INTERACTION
# ============================================================================

class GazeInteraction:
    """
    Gaze-based interaction system
    
    Enables eye-controlled UI interaction:
    - Dwell selection (look at object for X seconds to select)
    - Gaze-directed navigation (look to move)
    - Focus highlighting (highlight gazed objects)
    - Eye-controlled menus
    """
    
    def __init__(self, eye_tracker: EyeTracker):
        self.eye_tracker = eye_tracker
        
        # Interaction settings
        self.dwell_duration_ms = 800  # Time to dwell for selection
        self.highlight_enabled = True
        self.navigation_enabled = True
        
        # Current state
        self.current_gaze_target: Optional[str] = None
        self.gaze_start_time: Optional[datetime] = None
        self.highlighted_objects: Set[str] = set()
        
        # Gaze targets registry
        self.gaze_targets: Dict[str, Dict[str, Any]] = {}
        
        # Selection history
        self.selection_history: List[GazeEvent] = []
        
        logger.info("Gaze interaction system initialized")
    
    def register_gaze_target(self, object_id: str, object_type: GazeTarget,
                           position: Tuple[float, float, float],
                           radius: float = 0.5):
        """
        Register object as gaze-interactable
        
        Args:
            object_id: Unique object identifier
            object_type: Type of object
            position: 3D position in VR space
            radius: Interaction radius
        """
        self.gaze_targets[object_id] = {
            'type': object_type,
            'position': position,
            'radius': radius,
            'gaze_count': 0,
            'total_gaze_time': 0.0
        }
    
    async def update_gaze(self, gaze_point: Tuple[float, float, float],
                         user_id: str) -> Optional[GazeEvent]:
        """
        Update gaze and check for interactions
        
        Args:
            gaze_point: Current gaze point in VR space
            user_id: User identifier
            
        Returns:
            GazeEvent if interaction occurred
        """
        # Find what user is looking at
        target_id, target_info = self._find_gaze_target(gaze_point)
        
        # Handle highlight
        if self.highlight_enabled:
            await self._update_highlights(target_id)
        
        # Check for dwell selection
        if target_id:
            if target_id == self.current_gaze_target:
                # Continue gazing at same target
                if self.gaze_start_time:
                    dwell_time = (datetime.now() - self.gaze_start_time).total_seconds()
                    
                    # Update target stats
                    self.gaze_targets[target_id]['total_gaze_time'] += 0.016  # ~60 FPS
                    
                    # Check for selection
                    if dwell_time >= (self.dwell_duration_ms / 1000.0):
                        # Selection triggered!
                        event = GazeEvent(
                            event_id=f"selection_{datetime.now().timestamp()}",
                            user_id=user_id,
                            timestamp=datetime.now(),
                            gaze_target=target_id,
                            target_type=target_info['type'],
                            gaze_duration=dwell_time,
                            interaction_mode=InteractionMode.DWELL_SELECT,
                            attention_level=AttentionLevel.FOCUSED
                        )
                        
                        self.selection_history.append(event)
                        
                        # Reset gaze state
                        self.gaze_start_time = None
                        self.current_gaze_target = None
                        
                        logger.info(f"Dwell selection: {target_id} ({target_info['type'].value})")
                        return event
            else:
                # New gaze target
                self.current_gaze_target = target_id
                self.gaze_start_time = datetime.now()
                self.gaze_targets[target_id]['gaze_count'] += 1
        else:
            # Not looking at any target
            self.current_gaze_target = None
            self.gaze_start_time = None
        
        return None
    
    def _find_gaze_target(self, gaze_point: Tuple[float, float, float]
                         ) -> Tuple[Optional[str], Optional[Dict]]:
        """Find which registered target user is gazing at"""
        gaze_np = np.array(gaze_point)
        
        # Find closest target within interaction radius
        closest_target = None
        closest_distance = float('inf')
        
        for target_id, target_info in self.gaze_targets.items():
            target_pos = np.array(target_info['position'])
            distance = np.linalg.norm(gaze_np - target_pos)
            
            if distance < target_info['radius'] and distance < closest_distance:
                closest_target = target_id
                closest_distance = distance
        
        if closest_target:
            return closest_target, self.gaze_targets[closest_target]
        return None, None
    
    async def _update_highlights(self, current_target: Optional[str]):
        """Update highlighted objects based on gaze"""
        # Remove old highlights
        for obj_id in list(self.highlighted_objects):
            if obj_id != current_target:
                self.highlighted_objects.remove(obj_id)
                # In production, send unhighlight event to renderer
        
        # Add new highlight
        if current_target and current_target not in self.highlighted_objects:
            self.highlighted_objects.add(current_target)
            # In production, send highlight event to renderer
    
    async def navigate_by_gaze(self, gaze_direction: Tuple[float, float, float],
                              speed: float = 1.0) -> Tuple[float, float, float]:
        """
        Calculate camera movement based on gaze direction
        
        Args:
            gaze_direction: Direction vector of gaze
            speed: Movement speed multiplier
            
        Returns:
            Movement vector (dx, dy, dz)
        """
        if not self.navigation_enabled:
            return (0.0, 0.0, 0.0)
        
        # Normalize gaze direction
        direction = np.array(gaze_direction)
        direction_norm = direction / (np.linalg.norm(direction) + 1e-6)
        
        # Scale by speed
        movement = direction_norm * speed * 0.1  # 0.1 = base movement rate
        
        return tuple(movement)
    
    def get_gaze_statistics(self, object_id: str) -> Dict[str, Any]:
        """Get gaze statistics for specific object"""
        if object_id not in self.gaze_targets:
            return {}
        
        target = self.gaze_targets[object_id]
        return {
            'object_id': object_id,
            'type': target['type'].value,
            'gaze_count': target['gaze_count'],
            'total_gaze_time': target['total_gaze_time'],
            'average_gaze_time': target['total_gaze_time'] / max(target['gaze_count'], 1)
        }


# ============================================================================
# ATTENTION ANALYTICS
# ============================================================================

class AttentionAnalytics:
    """
    Attention and cognitive load analytics
    
    Analyzes gaze patterns to determine:
    - User attention level
    - Cognitive load
    - Fatigue detection
    - Expertise level (expert vs. novice gaze patterns)
    - UI optimization opportunities
    """
    
    def __init__(self):
        # Metrics history
        self.fixation_durations: deque = deque(maxlen=100)
        self.saccade_intervals: deque = deque(maxlen=100)
        self.pupil_diameters: deque = deque(maxlen=100)
        self.blink_intervals: deque = deque(maxlen=50)
        
        # Attention heatmap
        self.heatmap_points: Dict[Tuple[int, int, int], HeatmapPoint] = {}
        self.heatmap_resolution = 0.5  # Grid cell size in VR units
        
        # Session tracking
        self.session_start: datetime = datetime.now()
        self.last_analysis: datetime = datetime.now()
        
        # Thresholds
        self.high_cognitive_load_threshold = 0.7
        self.fatigue_threshold = 0.6
        
        logger.info("Attention analytics initialized")
    
    async def add_fixation(self, duration: float, position: Tuple[float, float, float]):
        """Record fixation event"""
        self.fixation_durations.append(duration)
        
        # Add to heatmap
        grid_pos = self._position_to_grid(position)
        if grid_pos not in self.heatmap_points:
            self.heatmap_points[grid_pos] = HeatmapPoint(
                position=position,
                dwell_time=0.0,
                visit_count=0,
                importance_score=0.0
            )
        
        self.heatmap_points[grid_pos].dwell_time += duration
        self.heatmap_points[grid_pos].visit_count += 1
    
    async def add_pupil_data(self, diameter_mm: float):
        """Record pupil diameter measurement"""
        self.pupil_diameters.append(diameter_mm)
    
    async def add_blink(self, timestamp: datetime):
        """Record blink event"""
        if self.blink_intervals:
            last_blink = self.blink_intervals[-1] if self.blink_intervals else None
            if last_blink:
                interval = (timestamp - last_blink).total_seconds()
                self.blink_intervals.append(timestamp)
    
    async def calculate_metrics(self) -> AttentionMetrics:
        """Calculate current attention metrics"""
        # Average fixation duration
        avg_fixation = np.mean(self.fixation_durations) if self.fixation_durations else 0.3
        
        # Saccade frequency (per minute)
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60.0
        saccade_freq = len(self.saccade_intervals) / max(session_duration, 0.01)
        
        # Pupil diameter
        avg_pupil = np.mean(self.pupil_diameters) if self.pupil_diameters else 4.0
        pupil_std = np.std(self.pupil_diameters) if len(self.pupil_diameters) > 1 else 0.0
        
        # Blink rate (per minute)
        blink_rate = len(self.blink_intervals) / max(session_duration, 0.01)
        
        # Gaze stability (inverse of fixation variability)
        fixation_std = np.std(self.fixation_durations) if len(self.fixation_durations) > 1 else 0.0
        gaze_stability = 1.0 / (1.0 + fixation_std)
        
        # Cognitive load estimation
        # High cognitive load indicators:
        # - Increased pupil dilation
        # - Shorter fixations
        # - More saccades
        # - Reduced blink rate
        
        cognitive_load = 0.0
        cognitive_load += min(pupil_std / 2.0, 0.3)  # Pupil variability
        cognitive_load += min((1.0 - avg_fixation) * 0.5, 0.3)  # Short fixations
        cognitive_load += min(saccade_freq / 100.0, 0.2)  # High saccade rate
        cognitive_load += min((20.0 - blink_rate) / 20.0 * 0.2, 0.2)  # Low blink rate
        
        # Determine attention level
        if cognitive_load > 0.8:
            attention = AttentionLevel.FATIGUED
        elif cognitive_load > 0.6:
            attention = AttentionLevel.DISTRACTED
        elif avg_fixation > 0.5:
            attention = AttentionLevel.HIGHLY_FOCUSED
        elif avg_fixation > 0.3:
            attention = AttentionLevel.FOCUSED
        else:
            attention = AttentionLevel.NORMAL
        
        return AttentionMetrics(
            average_fixation_duration=avg_fixation,
            saccade_frequency=saccade_freq,
            pupil_diameter_avg=avg_pupil,
            pupil_dilation_rate=pupil_std,
            blink_rate=blink_rate,
            gaze_stability=gaze_stability,
            cognitive_load=cognitive_load,
            attention_level=attention
        )
    
    def get_attention_heatmap(self, top_n: int = 20) -> List[HeatmapPoint]:
        """
        Get attention heatmap (most-gazed areas)
        
        Args:
            top_n: Number of top points to return
            
        Returns:
            List of heatmap points sorted by importance
        """
        # Calculate importance scores
        for point in self.heatmap_points.values():
            # Importance = dwell time * visit count
            point.importance_score = point.dwell_time * np.sqrt(point.visit_count)
        
        # Sort by importance
        sorted_points = sorted(
            self.heatmap_points.values(),
            key=lambda p: p.importance_score,
            reverse=True
        )
        
        return sorted_points[:top_n]
    
    def _position_to_grid(self, position: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Convert VR position to heatmap grid coordinates"""
        return (
            int(position[0] / self.heatmap_resolution),
            int(position[1] / self.heatmap_resolution),
            int(position[2] / self.heatmap_resolution)
        )
    
    async def detect_ui_issues(self) -> List[Dict[str, Any]]:
        """
        Detect UI/UX issues based on gaze patterns
        
        Returns:
            List of detected issues with recommendations
        """
        issues = []
        
        # Issue 1: Areas with very short fixations (hard to read?)
        heatmap = self.get_attention_heatmap(top_n=100)
        for point in heatmap:
            avg_fixation_time = point.dwell_time / max(point.visit_count, 1)
            if avg_fixation_time < 0.2 and point.visit_count > 5:
                issues.append({
                    'type': 'short_fixations',
                    'position': point.position,
                    'severity': 'medium',
                    'description': 'Users struggling to read this area',
                    'recommendation': 'Increase font size or contrast'
                })
        
        # Issue 2: Areas with many visits but low dwell time (confusing?)
        for point in heatmap:
            if point.visit_count > 10 and point.dwell_time < 2.0:
                issues.append({
                    'type': 'high_visits_low_dwell',
                    'position': point.position,
                    'severity': 'high',
                    'description': 'Users repeatedly checking this area without engaging',
                    'recommendation': 'Clarify information or improve visibility'
                })
        
        return issues


# ============================================================================
# EYE TRACKING SYSTEM (MAIN)
# ============================================================================

class EyeTrackingSystem:
    """
    Main eye tracking system integrating all components
    
    Usage:
        eye_system = EyeTrackingSystem(EyeTrackingDevice.META_QUEST_PRO)
        await eye_system.calibrate()
        await eye_system.process_gaze_frame(gaze_data)
    """
    
    def __init__(self, device_type: EyeTrackingDevice):
        self.eye_tracker = EyeTracker(device_type)
        self.gaze_interaction = GazeInteraction(self.eye_tracker)
        self.attention_analytics = AttentionAnalytics()
        
        # Statistics
        self.total_gaze_events = 0
        self.total_selections = 0
        
        logger.info("Eye tracking system initialized")
    
    async def calibrate(self, num_points: int = 9) -> float:
        """Calibrate eye tracking system"""
        # Generate calibration points (3x3 grid in VR space)
        calibration_points = []
        for x in [-1.0, 0.0, 1.0]:
            for y in [-1.0, 0.0, 1.0]:
                calibration_points.append((x, y, -2.0))  # 2 meters in front
        
        return await self.eye_tracker.calibrate(calibration_points)
    
    async def process_gaze_frame(self, gaze_data: EyeGazeData,
                                 user_id: str) -> Optional[GazeEvent]:
        """
        Process single frame of gaze data
        
        Args:
            gaze_data: Raw gaze data
            user_id: User identifier
            
        Returns:
            GazeEvent if significant event occurred
        """
        # Process raw gaze
        gaze_event = await self.eye_tracker.process_gaze_sample(gaze_data)
        
        # Check for blink
        await self.eye_tracker.detect_blink(gaze_data)
        
        # Update interaction system
        selection_event = await self.gaze_interaction.update_gaze(
            gaze_data.combined_gaze_point,
            user_id
        )
        
        # Update analytics
        if gaze_event and gaze_event.interaction_mode == InteractionMode.DWELL_SELECT:
            await self.attention_analytics.add_fixation(
                gaze_event.gaze_duration,
                gaze_data.combined_gaze_point
            )
        
        await self.attention_analytics.add_pupil_data(
            (gaze_data.pupil_diameter_left + gaze_data.pupil_diameter_right) / 2.0
        )
        
        if selection_event:
            self.total_selections += 1
            return selection_event
        
        return gaze_event
    
    def register_threat_node(self, threat_id: str, position: Tuple[float, float, float]):
        """Register threat node as gaze target"""
        self.gaze_interaction.register_gaze_target(
            threat_id,
            GazeTarget.THREAT_NODE,
            position,
            radius=0.3
        )
    
    async def get_attention_metrics(self) -> AttentionMetrics:
        """Get current attention metrics"""
        return await self.attention_analytics.calculate_metrics()
    
    def get_attention_heatmap(self) -> List[HeatmapPoint]:
        """Get attention heatmap"""
        return self.attention_analytics.get_attention_heatmap()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        tracker_stats = self.eye_tracker.get_statistics()
        
        return {
            **tracker_stats,
            'total_gaze_events': self.total_gaze_events,
            'total_selections': self.total_selections,
            'registered_targets': len(self.gaze_interaction.gaze_targets)
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_eye_tracking():
    """Example: Eye tracking during threat investigation"""
    
    # Initialize system
    eye_system = EyeTrackingSystem(EyeTrackingDevice.META_QUEST_PRO)
    
    # Calibrate
    print("Calibrating eye tracking...")
    quality = await eye_system.calibrate()
    print(f"Calibration quality: {quality:.2f}")
    
    # Register threat nodes
    print("\nRegistering threat nodes...")
    eye_system.register_threat_node("threat-001", (0.5, 0.0, -2.0))
    eye_system.register_threat_node("threat-002", (-0.5, 0.5, -2.5))
    eye_system.register_threat_node("threat-003", (0.0, -0.5, -3.0))
    
    # Simulate gaze data
    print("\nSimulating gaze tracking...")
    for i in range(100):
        # Generate simulated gaze data
        gaze_data = EyeGazeData(
            timestamp=datetime.now(),
            left_eye_position=(0.0, 0.0, 0.0),
            right_eye_position=(0.0, 0.0, 0.0),
            left_eye_direction=(0.5 + np.random.randn()*0.1, 0.0, -2.0),
            right_eye_direction=(0.5 + np.random.randn()*0.1, 0.0, -2.0),
            combined_gaze_point=(0.5 + np.random.randn()*0.05, 0.0, -2.0),
            pupil_diameter_left=4.0 + np.random.randn()*0.3,
            pupil_diameter_right=4.0 + np.random.randn()*0.3,
            confidence=0.95
        )
        
        # Process gaze
        event = await eye_system.process_gaze_frame(gaze_data, "user-123")
        
        if event and event.gaze_target:
            print(f"Selection detected: {event.gaze_target} after {event.gaze_duration:.2f}s")
        
        await asyncio.sleep(0.016)  # ~60 FPS
    
    # Get metrics
    print("\nAttention Metrics:")
    metrics = await eye_system.get_attention_metrics()
    print(f"  Avg fixation: {metrics.average_fixation_duration:.3f}s")
    print(f"  Cognitive load: {metrics.cognitive_load:.2f}")
    print(f"  Attention level: {metrics.attention_level.value}")
    
    # Get heatmap
    print("\nAttention Heatmap (top 5):")
    heatmap = eye_system.get_attention_heatmap()
    for i, point in enumerate(heatmap[:5], 1):
        print(f"  {i}. Position {point.position}, Dwell: {point.dwell_time:.2f}s, Visits: {point.visit_count}")
    
    # Statistics
    stats = eye_system.get_statistics()
    print(f"\nStatistics: {stats}")


if __name__ == "__main__":
    asyncio.run(example_eye_tracking())
