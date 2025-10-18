"""
Jupiter ARIA - Emotion Detection System
Analyzes user input to detect emotional state and adjust avatar expression
"""

import sqlite3
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
from collections import defaultdict


class EmotionType(Enum):
    """Primary emotions for avatar expression"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CONFUSED = "confused"
    EXCITED = "excited"
    WORRIED = "worried"
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"


class EmotionIntensity(Enum):
    """Intensity levels for emotions"""
    SUBTLE = "subtle"      # 0.0-0.3
    MILD = "mild"          # 0.3-0.5
    MODERATE = "moderate"  # 0.5-0.7
    STRONG = "strong"      # 0.7-0.9
    INTENSE = "intense"    # 0.9-1.0


@dataclass
class EmotionState:
    """Detected emotional state"""
    primary_emotion: EmotionType
    intensity: float  # 0.0-1.0
    secondary_emotions: Dict[EmotionType, float] = field(default_factory=dict)
    confidence: float = 0.0  # 0.0-1.0
    detected_at: datetime = field(default_factory=datetime.now)
    trigger_words: List[str] = field(default_factory=list)
    
    @property
    def intensity_level(self) -> EmotionIntensity:
        """Get intensity as categorical level"""
        if self.intensity < 0.3:
            return EmotionIntensity.SUBTLE
        elif self.intensity < 0.5:
            return EmotionIntensity.MILD
        elif self.intensity < 0.7:
            return EmotionIntensity.MODERATE
        elif self.intensity < 0.9:
            return EmotionIntensity.STRONG
        else:
            return EmotionIntensity.INTENSE


@dataclass
class FacialExpression:
    """Avatar facial expression parameters"""
    emotion: EmotionType
    intensity: float
    
    # Facial muscle groups (0.0-1.0)
    eyebrow_raise: float = 0.0
    eyebrow_furrow: float = 0.0
    eye_open: float = 0.5
    eye_squint: float = 0.0
    nose_wrinkle: float = 0.0
    mouth_smile: float = 0.0
    mouth_frown: float = 0.0
    mouth_open: float = 0.0
    jaw_clench: float = 0.0
    cheek_raise: float = 0.0
    
    # Head pose
    head_tilt: float = 0.0  # -1.0 to 1.0 (left/right)
    head_nod: float = 0.0   # -1.0 to 1.0 (up/down)


class EmotionLexicon:
    """Emotion word lexicon with weights"""
    
    # Emotion keywords with intensity weights
    EMOTION_KEYWORDS = {
        EmotionType.HAPPY: {
            'excellent': 0.9, 'great': 0.8, 'good': 0.6, 'nice': 0.5,
            'wonderful': 0.9, 'fantastic': 0.9, 'amazing': 0.9,
            'pleased': 0.7, 'glad': 0.7, 'delighted': 0.8,
            'happy': 0.8, 'joy': 0.8, 'cheerful': 0.7,
            'perfect': 0.9, 'awesome': 0.9, 'love': 0.8,
            'yay': 0.7, 'hooray': 0.8, '👍': 0.7, '😊': 0.8, '🎉': 0.9
        },
        EmotionType.SAD: {
            'sad': 0.8, 'unhappy': 0.7, 'depressed': 0.9,
            'disappointed': 0.7, 'upset': 0.7, 'down': 0.6,
            'miserable': 0.9, 'terrible': 0.8, 'awful': 0.8,
            'bad': 0.6, 'unfortunate': 0.6, 'regret': 0.7,
            'sorry': 0.6, 'cry': 0.8, '😢': 0.8, '😞': 0.7
        },
        EmotionType.ANGRY: {
            'angry': 0.9, 'mad': 0.8, 'furious': 1.0,
            'irritated': 0.7, 'annoyed': 0.6, 'frustrated': 0.7,
            'outraged': 0.9, 'hate': 0.9, 'rage': 1.0,
            'damn': 0.7, 'stupid': 0.7, 'ridiculous': 0.7,
            'unacceptable': 0.8, '😠': 0.9, '🤬': 1.0
        },
        EmotionType.SURPRISED: {
            'surprised': 0.8, 'shocked': 0.9, 'amazed': 0.8,
            'astonished': 0.9, 'unexpected': 0.7, 'wow': 0.8,
            'unbelievable': 0.8, 'incredible': 0.8,
            'what': 0.5, 'really': 0.5, '😮': 0.8, '🤯': 0.9
        },
        EmotionType.FEARFUL: {
            'scared': 0.8, 'afraid': 0.8, 'fearful': 0.8,
            'terrified': 1.0, 'worried': 0.7, 'anxious': 0.7,
            'nervous': 0.6, 'panic': 0.9, 'threat': 0.8,
            'danger': 0.8, 'risk': 0.6, '😨': 0.8, '😰': 0.7
        },
        EmotionType.CONFUSED: {
            'confused': 0.8, 'puzzled': 0.7, 'unclear': 0.6,
            'uncertain': 0.6, 'don\'t understand': 0.7,
            'what': 0.4, 'huh': 0.6, 'why': 0.4,
            'how': 0.4, '🤔': 0.7, '😕': 0.6
        },
        EmotionType.EXCITED: {
            'excited': 0.9, 'thrilled': 0.9, 'enthusiastic': 0.8,
            'eager': 0.7, 'pumped': 0.8, 'stoked': 0.8,
            'can\'t wait': 0.9, '🎉': 0.9, '🔥': 0.8
        },
        EmotionType.WORRIED: {
            'worried': 0.8, 'concerned': 0.7, 'anxious': 0.7,
            'nervous': 0.6, 'uneasy': 0.6, 'troubled': 0.7,
            'critical': 0.8, 'urgent': 0.8, 'serious': 0.7
        },
        EmotionType.CONFIDENT: {
            'confident': 0.8, 'sure': 0.7, 'certain': 0.7,
            'absolutely': 0.8, 'definitely': 0.8, 'know': 0.6,
            'guaranteed': 0.8, 'positive': 0.7
        },
        EmotionType.FRUSTRATED: {
            'frustrated': 0.8, 'irritated': 0.7, 'annoyed': 0.7,
            'stuck': 0.6, 'difficult': 0.6, 'challenging': 0.6,
            'ugh': 0.7, 'argh': 0.7
        }
    }
    
    # Intensifiers and dampeners
    INTENSIFIERS = {
        'very': 1.3,
        'extremely': 1.5,
        'really': 1.3,
        'so': 1.2,
        'incredibly': 1.5,
        'absolutely': 1.4,
        'totally': 1.3,
        'completely': 1.4,
        '!!!': 1.5,
        '!!': 1.3,
        '!': 1.1
    }
    
    DAMPENERS = {
        'slightly': 0.5,
        'somewhat': 0.6,
        'a bit': 0.6,
        'kind of': 0.7,
        'sort of': 0.7,
        'a little': 0.6,
        'maybe': 0.7,
        'perhaps': 0.7
    }
    
    # Negation words
    NEGATIONS = ['not', 'no', 'never', 'neither', 'nor', 'none', "n't"]


class EmotionDetector:
    """
    Main emotion detection engine
    Analyzes text input to detect user emotional state
    """
    
    def __init__(self, db_path: str = "jupiter_emotion.db"):
        self.db_path = db_path
        self.lexicon = EmotionLexicon()
        self._init_database()
    
    def _init_database(self):
        """Initialize emotion detection database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Emotion detections history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_history (
                detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                input_text TEXT NOT NULL,
                primary_emotion TEXT NOT NULL,
                intensity REAL,
                confidence REAL,
                trigger_words TEXT,
                detected_at TEXT
            )
        """)
        
        # User emotion profile
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_profiles (
                user_id TEXT PRIMARY KEY,
                dominant_emotion TEXT,
                emotion_distribution TEXT,
                total_interactions INTEGER DEFAULT 0,
                last_interaction TEXT
            )
        """)
        
        # Expression templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expression_templates (
                emotion TEXT PRIMARY KEY,
                facial_parameters TEXT NOT NULL,
                animation_duration REAL DEFAULT 0.5
            )
        """)
        
        conn.commit()
        conn.close()
        
        self._init_expression_templates()
    
    def _init_expression_templates(self):
        """Initialize facial expression templates for each emotion"""
        
        templates = {
            EmotionType.NEUTRAL.value: {
                'eyebrow_raise': 0.0,
                'eyebrow_furrow': 0.0,
                'eye_open': 0.5,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.0,
                'mouth_frown': 0.0,
                'mouth_open': 0.0,
                'jaw_clench': 0.0,
                'cheek_raise': 0.0,
                'head_tilt': 0.0,
                'head_nod': 0.0
            },
            EmotionType.HAPPY.value: {
                'eyebrow_raise': 0.2,
                'eyebrow_furrow': 0.0,
                'eye_open': 0.6,
                'eye_squint': 0.3,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.8,
                'mouth_frown': 0.0,
                'mouth_open': 0.2,
                'jaw_clench': 0.0,
                'cheek_raise': 0.7,
                'head_tilt': 0.1,
                'head_nod': 0.2
            },
            EmotionType.SAD.value: {
                'eyebrow_raise': 0.3,
                'eyebrow_furrow': 0.5,
                'eye_open': 0.3,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.0,
                'mouth_frown': 0.7,
                'mouth_open': 0.0,
                'jaw_clench': 0.0,
                'cheek_raise': 0.0,
                'head_tilt': 0.0,
                'head_nod': -0.3
            },
            EmotionType.ANGRY.value: {
                'eyebrow_raise': 0.0,
                'eyebrow_furrow': 0.9,
                'eye_open': 0.7,
                'eye_squint': 0.4,
                'nose_wrinkle': 0.5,
                'mouth_smile': 0.0,
                'mouth_frown': 0.6,
                'mouth_open': 0.3,
                'jaw_clench': 0.8,
                'cheek_raise': 0.0,
                'head_tilt': 0.0,
                'head_nod': 0.0
            },
            EmotionType.SURPRISED.value: {
                'eyebrow_raise': 0.9,
                'eyebrow_furrow': 0.0,
                'eye_open': 0.9,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.0,
                'mouth_frown': 0.0,
                'mouth_open': 0.7,
                'jaw_clench': 0.0,
                'cheek_raise': 0.0,
                'head_tilt': 0.0,
                'head_nod': 0.1
            },
            EmotionType.FEARFUL.value: {
                'eyebrow_raise': 0.7,
                'eyebrow_furrow': 0.3,
                'eye_open': 0.8,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.0,
                'mouth_frown': 0.5,
                'mouth_open': 0.4,
                'jaw_clench': 0.3,
                'cheek_raise': 0.0,
                'head_tilt': -0.2,
                'head_nod': -0.2
            },
            EmotionType.CONFUSED.value: {
                'eyebrow_raise': 0.5,
                'eyebrow_furrow': 0.4,
                'eye_open': 0.6,
                'eye_squint': 0.2,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.0,
                'mouth_frown': 0.3,
                'mouth_open': 0.2,
                'jaw_clench': 0.0,
                'cheek_raise': 0.0,
                'head_tilt': 0.3,
                'head_nod': 0.0
            },
            EmotionType.EXCITED.value: {
                'eyebrow_raise': 0.6,
                'eyebrow_furrow': 0.0,
                'eye_open': 0.8,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.9,
                'mouth_frown': 0.0,
                'mouth_open': 0.5,
                'jaw_clench': 0.0,
                'cheek_raise': 0.8,
                'head_tilt': 0.2,
                'head_nod': 0.3
            },
            EmotionType.WORRIED.value: {
                'eyebrow_raise': 0.4,
                'eyebrow_furrow': 0.7,
                'eye_open': 0.5,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.0,
                'mouth_frown': 0.5,
                'mouth_open': 0.0,
                'jaw_clench': 0.2,
                'cheek_raise': 0.0,
                'head_tilt': 0.0,
                'head_nod': -0.1
            },
            EmotionType.CONFIDENT.value: {
                'eyebrow_raise': 0.2,
                'eyebrow_furrow': 0.0,
                'eye_open': 0.6,
                'eye_squint': 0.0,
                'nose_wrinkle': 0.0,
                'mouth_smile': 0.5,
                'mouth_frown': 0.0,
                'mouth_open': 0.0,
                'jaw_clench': 0.0,
                'cheek_raise': 0.3,
                'head_tilt': 0.0,
                'head_nod': 0.2
            }
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for emotion, params in templates.items():
            cursor.execute("""
                INSERT OR REPLACE INTO expression_templates 
                (emotion, facial_parameters)
                VALUES (?, ?)
            """, (emotion, json.dumps(params)))
        
        conn.commit()
        conn.close()
    
    def detect_emotion(self, text: str, user_id: Optional[str] = None) -> EmotionState:
        """
        Detect emotion from user input text
        
        Args:
            text: User input text
            user_id: Optional user identifier for profile tracking
        
        Returns:
            EmotionState with detected emotion and intensity
        """
        
        # Normalize text
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b|[!?]+|[\U0001F600-\U0001F64F]', text_lower)
        
        # Score each emotion
        emotion_scores = defaultdict(float)
        trigger_words = []
        
        # Check for emotion keywords
        for i, word in enumerate(words):
            # Check for negation
            is_negated = False
            if i > 0 and words[i-1] in self.lexicon.NEGATIONS:
                is_negated = True
            
            # Check each emotion
            for emotion_type, keywords in self.lexicon.EMOTION_KEYWORDS.items():
                if word in keywords:
                    score = keywords[word]
                    
                    # Apply intensifiers/dampeners
                    if i > 0:
                        prev_word = words[i-1]
                        if prev_word in self.lexicon.INTENSIFIERS:
                            score *= self.lexicon.INTENSIFIERS[prev_word]
                        elif prev_word in self.lexicon.DAMPENERS:
                            score *= self.lexicon.DAMPENERS[prev_word]
                    
                    # Handle negation (invert emotion)
                    if is_negated:
                        score *= 0.3  # Reduce but don't eliminate
                    
                    emotion_scores[emotion_type] += score
                    trigger_words.append(word)
        
        # Check for exclamation/question marks (intensity indicators)
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        if exclamation_count >= 2:
            # Amplify all emotions
            for emotion in emotion_scores:
                emotion_scores[emotion] *= (1 + exclamation_count * 0.15)
        
        if question_count >= 2:
            # Boost confusion
            emotion_scores[EmotionType.CONFUSED] += 0.3
        
        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            raw_intensity = emotion_scores[primary_emotion]
            
            # Normalize intensity to 0.0-1.0
            intensity = min(raw_intensity, 1.0)
            
            # Calculate confidence based on score separation
            total_score = sum(emotion_scores.values())
            confidence = (emotion_scores[primary_emotion] / total_score) if total_score > 0 else 0.5
            
            # Get secondary emotions
            secondary = {
                emotion: score / total_score
                for emotion, score in emotion_scores.items()
                if emotion != primary_emotion and score > 0.1
            }
        else:
            # No emotion detected - neutral
            primary_emotion = EmotionType.NEUTRAL
            intensity = 0.3
            confidence = 0.5
            secondary = {}
        
        # Create emotion state
        emotion_state = EmotionState(
            primary_emotion=primary_emotion,
            intensity=intensity,
            secondary_emotions=secondary,
            confidence=confidence,
            trigger_words=trigger_words
        )
        
        # Save to history
        self._save_detection(text, emotion_state, user_id)
        
        # Update user profile
        if user_id:
            self._update_user_profile(user_id, emotion_state)
        
        return emotion_state
    
    def _save_detection(self, text: str, emotion: EmotionState, user_id: Optional[str]):
        """Save emotion detection to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO emotion_history 
            (user_id, input_text, primary_emotion, intensity, confidence, 
             trigger_words, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            text,
            emotion.primary_emotion.value,
            emotion.intensity,
            emotion.confidence,
            json.dumps(emotion.trigger_words),
            emotion.detected_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _update_user_profile(self, user_id: str, emotion: EmotionState):
        """Update user emotion profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing profile
        cursor.execute("""
            SELECT emotion_distribution, total_interactions 
            FROM emotion_profiles WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            distribution = json.loads(result[0])
            total = result[1] + 1
        else:
            distribution = {}
            total = 1
        
        # Update distribution
        emotion_key = emotion.primary_emotion.value
        distribution[emotion_key] = distribution.get(emotion_key, 0) + 1
        
        # Find dominant emotion
        dominant = max(distribution, key=distribution.get)
        
        cursor.execute("""
            INSERT OR REPLACE INTO emotion_profiles 
            (user_id, dominant_emotion, emotion_distribution, 
             total_interactions, last_interaction)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            dominant,
            json.dumps(distribution),
            total,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_facial_expression(self, emotion_state: EmotionState) -> FacialExpression:
        """
        Convert emotion state to facial expression parameters
        
        Args:
            emotion_state: Detected emotion state
        
        Returns:
            FacialExpression with muscle group weights
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT facial_parameters FROM expression_templates 
            WHERE emotion = ?
        """, (emotion_state.primary_emotion.value,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            params = json.loads(result[0])
            
            # Scale by intensity
            scaled_params = {
                key: value * emotion_state.intensity
                for key, value in params.items()
            }
            
            return FacialExpression(
                emotion=emotion_state.primary_emotion,
                intensity=emotion_state.intensity,
                **scaled_params
            )
        
        # Default neutral expression
        return FacialExpression(
            emotion=EmotionType.NEUTRAL,
            intensity=0.0
        )
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user's emotion profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dominant_emotion, emotion_distribution, 
                   total_interactions, last_interaction
            FROM emotion_profiles WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': user_id,
                'dominant_emotion': result[0],
                'emotion_distribution': json.loads(result[1]),
                'total_interactions': result[2],
                'last_interaction': result[3]
            }
        
        return None
    
    def get_statistics(self) -> Dict:
        """Get emotion detection statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM emotion_history")
        stats['total_detections'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT primary_emotion, COUNT(*) 
            FROM emotion_history 
            GROUP BY primary_emotion
        """)
        stats['emotion_distribution'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT AVG(confidence) FROM emotion_history")
        stats['avg_confidence'] = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT COUNT(*) FROM emotion_profiles")
        stats['tracked_users'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    detector = EmotionDetector()
    
    # Test various inputs
    test_inputs = [
        "This is absolutely fantastic! Great work!",
        "I'm very worried about this critical vulnerability",
        "This is confusing, I don't understand what's happening",
        "I'm so frustrated with these constant errors",
        "Excellent! The patch worked perfectly",
        "Oh no, this is terrible news"
    ]
    
    print("Emotion Detection Examples:\n")
    
    for text in test_inputs:
        emotion = detector.detect_emotion(text, user_id="test_user")
        expression = detector.get_facial_expression(emotion)
        
        print(f"Input: \"{text}\"")
        print(f"Emotion: {emotion.primary_emotion.value} ({emotion.intensity_level.value})")
        print(f"Intensity: {emotion.intensity:.2f}")
        print(f"Confidence: {emotion.confidence:.2f}")
        print(f"Triggers: {', '.join(emotion.trigger_words)}")
        print(f"Expression: smile={expression.mouth_smile:.2f}, "
              f"frown={expression.mouth_frown:.2f}, "
              f"eyebrow_raise={expression.eyebrow_raise:.2f}")
        print()
    
    # Statistics
    stats = detector.get_statistics()
    print(f"Statistics: {stats}")
    
    # User profile
    profile = detector.get_user_profile("test_user")
    print(f"\nUser profile: {profile}")
