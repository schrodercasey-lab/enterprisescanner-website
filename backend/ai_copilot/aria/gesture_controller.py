"""
Jupiter ARIA - Gesture Control System
Natural gesture and body language animation for avatar
"""

import sqlite3
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
from emotion_detector import EmotionType, EmotionState


class GestureType(Enum):
    """Avatar gesture types"""
    # Head gestures
    NOD_YES = "nod_yes"
    SHAKE_NO = "shake_no"
    TILT_CURIOUS = "tilt_curious"
    TILT_SYMPATHETIC = "tilt_sympathetic"
    
    # Hand gestures
    POINT_FORWARD = "point_forward"
    POINT_SCREEN = "point_screen"
    WAVE_HELLO = "wave_hello"
    WAVE_GOODBYE = "wave_goodbye"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    OPEN_PALM = "open_palm"
    STOP_HAND = "stop_hand"
    COUNTING_ONE = "counting_one"
    COUNTING_TWO = "counting_two"
    COUNTING_THREE = "counting_three"
    
    # Arm gestures
    CROSS_ARMS = "cross_arms"
    HANDS_HIP = "hands_hip"
    SHRUG = "shrug"
    ARM_RAISE = "arm_raise"
    
    # Body language
    LEAN_FORWARD = "lean_forward"
    LEAN_BACK = "lean_back"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    
    # Idle animations
    IDLE_BREATHE = "idle_breathe"
    IDLE_BLINK = "idle_blink"
    IDLE_LOOK_AROUND = "idle_look_around"
    IDLE_SHIFT_WEIGHT = "idle_shift_weight"


class GestureIntensity(Enum):
    """Gesture animation intensity"""
    SUBTLE = "subtle"      # Small, minimal movement
    NORMAL = "normal"      # Natural, moderate movement
    EMPHATIC = "emphatic"  # Large, exaggerated movement


@dataclass
class GestureKeyframe:
    """Animation keyframe for gesture"""
    time: float  # seconds
    bone_transforms: Dict[str, Dict[str, float]]  # bone_name -> {x, y, z, rotation}
    easing: str = "linear"  # linear, ease-in, ease-out, ease-in-out


@dataclass
class GestureAnimation:
    """Complete gesture animation sequence"""
    gesture_type: GestureType
    duration: float  # seconds
    keyframes: List[GestureKeyframe] = field(default_factory=list)
    loop: bool = False
    blend_time: float = 0.2  # Transition blend time
    
    def get_transform_at_time(self, time: float) -> Dict[str, Dict[str, float]]:
        """Interpolate transforms at given time"""
        if not self.keyframes:
            return {}
        
        # Find surrounding keyframes
        prev_frame = self.keyframes[0]
        next_frame = self.keyframes[-1]
        
        for i, frame in enumerate(self.keyframes):
            if frame.time <= time:
                prev_frame = frame
                if i < len(self.keyframes) - 1:
                    next_frame = self.keyframes[i + 1]
        
        # Interpolate between frames
        if prev_frame.time == next_frame.time:
            return prev_frame.bone_transforms
        
        t = (time - prev_frame.time) / (next_frame.time - prev_frame.time)
        t = self._apply_easing(t, next_frame.easing)
        
        interpolated = {}
        for bone_name in prev_frame.bone_transforms:
            if bone_name in next_frame.bone_transforms:
                prev_trans = prev_frame.bone_transforms[bone_name]
                next_trans = next_frame.bone_transforms[bone_name]
                
                interpolated[bone_name] = {
                    key: prev_trans[key] + (next_trans[key] - prev_trans[key]) * t
                    for key in prev_trans
                }
        
        return interpolated
    
    def _apply_easing(self, t: float, easing: str) -> float:
        """Apply easing function to interpolation"""
        if easing == "ease-in":
            return t * t
        elif easing == "ease-out":
            return t * (2 - t)
        elif easing == "ease-in-out":
            return t * t * (3 - 2 * t)
        else:  # linear
            return t


@dataclass
class BodyPose:
    """Current body pose state"""
    head_rotation: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    neck_rotation: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    torso_rotation: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    left_arm_rotation: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    right_arm_rotation: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    left_hand_position: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    right_hand_position: Dict[str, float] = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})


class GestureLibrary:
    """Pre-defined gesture animation library"""
    
    @staticmethod
    def get_nod_yes() -> GestureAnimation:
        """Head nod affirmative"""
        keyframes = [
            GestureKeyframe(0.0, {'head': {'x': 0, 'y': 0, 'z': 0}}),
            GestureKeyframe(0.2, {'head': {'x': 15, 'y': 0, 'z': 0}}, "ease-out"),
            GestureKeyframe(0.4, {'head': {'x': -5, 'y': 0, 'z': 0}}, "ease-in-out"),
            GestureKeyframe(0.6, {'head': {'x': 10, 'y': 0, 'z': 0}}, "ease-in-out"),
            GestureKeyframe(0.8, {'head': {'x': 0, 'y': 0, 'z': 0}}, "ease-in"),
        ]
        return GestureAnimation(GestureType.NOD_YES, 0.8, keyframes)
    
    @staticmethod
    def get_shake_no() -> GestureAnimation:
        """Head shake negative"""
        keyframes = [
            GestureKeyframe(0.0, {'head': {'x': 0, 'y': 0, 'z': 0}}),
            GestureKeyframe(0.2, {'head': {'x': 0, 'y': -20, 'z': 0}}, "ease-out"),
            GestureKeyframe(0.5, {'head': {'x': 0, 'y': 20, 'z': 0}}, "ease-in-out"),
            GestureKeyframe(0.8, {'head': {'x': 0, 'y': -15, 'z': 0}}, "ease-in-out"),
            GestureKeyframe(1.0, {'head': {'x': 0, 'y': 0, 'z': 0}}, "ease-in"),
        ]
        return GestureAnimation(GestureType.SHAKE_NO, 1.0, keyframes)
    
    @staticmethod
    def get_point_forward() -> GestureAnimation:
        """Point finger forward"""
        keyframes = [
            GestureKeyframe(0.0, {
                'right_arm': {'x': 0, 'y': 0, 'z': 0},
                'right_hand': {'x': 0, 'y': 0, 'z': 0}
            }),
            GestureKeyframe(0.3, {
                'right_arm': {'x': -45, 'y': 90, 'z': 0},
                'right_hand': {'x': 0, 'y': 0, 'z': 50}
            }, "ease-out"),
            GestureKeyframe(1.5, {
                'right_arm': {'x': -45, 'y': 90, 'z': 0},
                'right_hand': {'x': 0, 'y': 0, 'z': 50}
            }),
            GestureKeyframe(1.8, {
                'right_arm': {'x': 0, 'y': 0, 'z': 0},
                'right_hand': {'x': 0, 'y': 0, 'z': 0}
            }, "ease-in"),
        ]
        return GestureAnimation(GestureType.POINT_FORWARD, 1.8, keyframes)
    
    @staticmethod
    def get_thumbs_up() -> GestureAnimation:
        """Thumbs up gesture"""
        keyframes = [
            GestureKeyframe(0.0, {
                'right_arm': {'x': 0, 'y': 0, 'z': 0},
                'right_hand': {'x': 0, 'y': 0, 'z': 0, 'thumb': 0}
            }),
            GestureKeyframe(0.4, {
                'right_arm': {'x': -90, 'y': 45, 'z': 0},
                'right_hand': {'x': 0, 'y': 20, 'z': 30, 'thumb': 90}
            }, "ease-out"),
            GestureKeyframe(1.2, {
                'right_arm': {'x': -90, 'y': 45, 'z': 0},
                'right_hand': {'x': 0, 'y': 20, 'z': 30, 'thumb': 90}
            }),
            GestureKeyframe(1.6, {
                'right_arm': {'x': 0, 'y': 0, 'z': 0},
                'right_hand': {'x': 0, 'y': 0, 'z': 0, 'thumb': 0}
            }, "ease-in"),
        ]
        return GestureAnimation(GestureType.THUMBS_UP, 1.6, keyframes)
    
    @staticmethod
    def get_shrug() -> GestureAnimation:
        """Shoulder shrug (uncertainty)"""
        keyframes = [
            GestureKeyframe(0.0, {
                'left_arm': {'x': 0, 'y': 0, 'z': 0},
                'right_arm': {'x': 0, 'y': 0, 'z': 0},
                'torso': {'x': 0, 'y': 0, 'z': 0}
            }),
            GestureKeyframe(0.3, {
                'left_arm': {'x': 45, 'y': -30, 'z': 0},
                'right_arm': {'x': 45, 'y': 30, 'z': 0},
                'torso': {'x': 0, 'y': 0, 'z': 0}
            }, "ease-out"),
            GestureKeyframe(1.0, {
                'left_arm': {'x': 45, 'y': -30, 'z': 0},
                'right_arm': {'x': 45, 'y': 30, 'z': 0},
                'torso': {'x': 0, 'y': 0, 'z': 0}
            }),
            GestureKeyframe(1.3, {
                'left_arm': {'x': 0, 'y': 0, 'z': 0},
                'right_arm': {'x': 0, 'y': 0, 'z': 0},
                'torso': {'x': 0, 'y': 0, 'z': 0}
            }, "ease-in"),
        ]
        return GestureAnimation(GestureType.SHRUG, 1.3, keyframes)
    
    @staticmethod
    def get_idle_breathe() -> GestureAnimation:
        """Subtle breathing animation"""
        keyframes = [
            GestureKeyframe(0.0, {'torso': {'x': 0, 'y': 0, 'z': 0}}),
            GestureKeyframe(2.0, {'torso': {'x': 2, 'y': 0, 'z': 0}}, "ease-in-out"),
            GestureKeyframe(4.0, {'torso': {'x': 0, 'y': 0, 'z': 0}}, "ease-in-out"),
        ]
        return GestureAnimation(GestureType.IDLE_BREATHE, 4.0, keyframes, loop=True)


class GestureController:
    """
    Main gesture control system
    Manages avatar gestures, body language, and idle animations
    """
    
    def __init__(self, db_path: str = "jupiter_gestures.db"):
        self.db_path = db_path
        self.library = GestureLibrary()
        self.current_pose = BodyPose()
        self.active_gestures: List[GestureAnimation] = []
        self._init_database()
    
    def _init_database(self):
        """Initialize gesture control database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Gesture animations library
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gesture_library (
                gesture_type TEXT PRIMARY KEY,
                animation_data TEXT NOT NULL,
                duration REAL,
                is_looping INTEGER DEFAULT 0,
                category TEXT
            )
        """)
        
        # Gesture usage history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gesture_history (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gesture_type TEXT NOT NULL,
                context TEXT,
                emotion TEXT,
                triggered_at TEXT
            )
        """)
        
        # Context-based gesture rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gesture_rules (
                rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emotion TEXT,
                keyword TEXT,
                gesture_type TEXT,
                probability REAL DEFAULT 0.5
            )
        """)
        
        conn.commit()
        conn.close()
        
        self._init_gesture_rules()
    
    def _init_gesture_rules(self):
        """Initialize context-based gesture triggering rules"""
        
        rules = [
            # Affirmative gestures
            ('happy', 'yes', GestureType.NOD_YES.value, 0.8),
            ('happy', 'correct', GestureType.NOD_YES.value, 0.7),
            ('happy', 'great', GestureType.THUMBS_UP.value, 0.6),
            ('excited', 'excellent', GestureType.THUMBS_UP.value, 0.8),
            
            # Negative gestures
            ('sad', 'no', GestureType.SHAKE_NO.value, 0.7),
            ('angry', 'unacceptable', GestureType.SHAKE_NO.value, 0.8),
            ('frustrated', 'wrong', GestureType.SHAKE_NO.value, 0.6),
            
            # Pointing gestures
            ('neutral', 'here', GestureType.POINT_SCREEN.value, 0.6),
            ('neutral', 'this', GestureType.POINT_SCREEN.value, 0.5),
            ('confident', 'look', GestureType.POINT_FORWARD.value, 0.7),
            
            # Uncertainty gestures
            ('confused', 'maybe', GestureType.SHRUG.value, 0.7),
            ('confused', 'unsure', GestureType.TILT_CURIOUS.value, 0.6),
            ('worried', 'uncertain', GestureType.SHRUG.value, 0.5),
            
            # Greeting gestures
            ('happy', 'hello', GestureType.WAVE_HELLO.value, 0.8),
            ('happy', 'hi', GestureType.WAVE_HELLO.value, 0.7),
            ('neutral', 'goodbye', GestureType.WAVE_GOODBYE.value, 0.8),
            
            # Counting gestures
            ('neutral', 'first', GestureType.COUNTING_ONE.value, 0.6),
            ('neutral', 'second', GestureType.COUNTING_TWO.value, 0.6),
            ('neutral', 'third', GestureType.COUNTING_THREE.value, 0.6),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for emotion, keyword, gesture, prob in rules:
            cursor.execute("""
                INSERT OR IGNORE INTO gesture_rules 
                (emotion, keyword, gesture_type, probability)
                VALUES (?, ?, ?, ?)
            """, (emotion, keyword, gesture, prob))
        
        conn.commit()
        conn.close()
    
    def suggest_gesture(
        self,
        text: str,
        emotion_state: Optional[EmotionState] = None
    ) -> Optional[GestureType]:
        """
        Suggest appropriate gesture based on context and emotion
        
        Args:
            text: Current speech text
            emotion_state: Detected emotional state
        
        Returns:
            Suggested GestureType or None
        """
        
        text_lower = text.lower()
        emotion = emotion_state.primary_emotion.value if emotion_state else 'neutral'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find matching rules
        cursor.execute("""
            SELECT gesture_type, probability 
            FROM gesture_rules 
            WHERE emotion = ? 
            ORDER BY probability DESC
        """, (emotion,))
        
        candidates = []
        
        for gesture_type, prob in cursor.fetchall():
            # Check if keyword in text
            cursor.execute("""
                SELECT keyword FROM gesture_rules 
                WHERE gesture_type = ? AND emotion = ?
            """, (gesture_type, emotion))
            
            keywords = [row[0] for row in cursor.fetchall()]
            
            for keyword in keywords:
                if keyword in text_lower:
                    candidates.append((gesture_type, prob))
                    break
        
        conn.close()
        
        if candidates:
            # Probabilistic selection
            if random.random() < candidates[0][1]:
                return GestureType(candidates[0][0])
        
        return None
    
    def play_gesture(self, gesture_type: GestureType) -> GestureAnimation:
        """
        Play gesture animation
        
        Args:
            gesture_type: Type of gesture to play
        
        Returns:
            GestureAnimation object
        """
        
        # Get animation from library
        if gesture_type == GestureType.NOD_YES:
            animation = self.library.get_nod_yes()
        elif gesture_type == GestureType.SHAKE_NO:
            animation = self.library.get_shake_no()
        elif gesture_type == GestureType.POINT_FORWARD:
            animation = self.library.get_point_forward()
        elif gesture_type == GestureType.THUMBS_UP:
            animation = self.library.get_thumbs_up()
        elif gesture_type == GestureType.SHRUG:
            animation = self.library.get_shrug()
        elif gesture_type == GestureType.IDLE_BREATHE:
            animation = self.library.get_idle_breathe()
        else:
            # Default idle
            animation = self.library.get_idle_breathe()
        
        self.active_gestures.append(animation)
        
        # Log usage
        self._log_gesture(gesture_type)
        
        return animation
    
    def _log_gesture(self, gesture_type: GestureType, context: str = "", emotion: str = ""):
        """Log gesture usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO gesture_history 
            (gesture_type, context, emotion, triggered_at)
            VALUES (?, ?, ?, ?)
        """, (
            gesture_type.value,
            context,
            emotion,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def update_pose(self, delta_time: float):
        """
        Update current body pose based on active animations
        
        Args:
            delta_time: Time since last update (seconds)
        """
        
        # Blend all active animations
        blended_transforms = {}
        
        for animation in self.active_gestures[:]:
            # Get current time in animation
            # (In production, would track animation start time)
            transforms = animation.get_transform_at_time(delta_time)
            
            # Blend with existing transforms
            for bone, transform in transforms.items():
                if bone not in blended_transforms:
                    blended_transforms[bone] = transform
                else:
                    # Average blend (simplified)
                    for key in transform:
                        blended_transforms[bone][key] = (
                            blended_transforms[bone][key] + transform[key]
                        ) / 2
        
        # Apply to current pose
        if 'head' in blended_transforms:
            self.current_pose.head_rotation = blended_transforms['head']
        if 'torso' in blended_transforms:
            self.current_pose.torso_rotation = blended_transforms['torso']
        if 'right_arm' in blended_transforms:
            self.current_pose.right_arm_rotation = blended_transforms['right_arm']
    
    def get_idle_gesture(self) -> GestureType:
        """Get random idle gesture"""
        idle_gestures = [
            GestureType.IDLE_BREATHE,
            GestureType.IDLE_BLINK,
            GestureType.IDLE_LOOK_AROUND,
            GestureType.IDLE_SHIFT_WEIGHT
        ]
        return random.choice(idle_gestures)
    
    def get_statistics(self) -> Dict:
        """Get gesture usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM gesture_history")
        stats['total_gestures'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT gesture_type, COUNT(*) 
            FROM gesture_history 
            GROUP BY gesture_type 
            ORDER BY COUNT(*) DESC 
            LIMIT 5
        """)
        stats['most_used'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM gesture_rules")
        stats['total_rules'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    from emotion_detector import EmotionDetector
    
    controller = GestureController()
    detector = EmotionDetector()
    
    # Test gesture suggestions
    test_cases = [
        "Yes, that's absolutely correct!",
        "I'm not sure about this, maybe we should check",
        "Hello! Welcome to Jupiter",
        "Look at this critical vulnerability here",
        "No, that's not the right approach"
    ]
    
    print("Gesture Suggestion Examples:\n")
    
    for text in test_cases:
        emotion = detector.detect_emotion(text)
        gesture = controller.suggest_gesture(text, emotion)
        
        print(f"Text: \"{text}\"")
        print(f"Emotion: {emotion.primary_emotion.value}")
        print(f"Suggested Gesture: {gesture.value if gesture else 'None'}")
        
        if gesture:
            animation = controller.play_gesture(gesture)
            print(f"Animation Duration: {animation.duration}s")
            print(f"Keyframes: {len(animation.keyframes)}")
        print()
    
    # Statistics
    stats = controller.get_statistics()
    print(f"Statistics: {stats}")
