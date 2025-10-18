"""
Jupiter ARIA - Advanced Lip-Sync Engine
Phoneme-based lip synchronization for realistic avatar speech animation
"""

import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re


class Phoneme(Enum):
    """International Phonetic Alphabet (IPA) phonemes for English"""
    # Vowels
    AA = "aa"  # f<a>ther
    AE = "ae"  # c<a>t
    AH = "ah"  # c<u>t
    AO = "ao"  # c<au>ght
    AW = "aw"  # c<ow>
    AY = "ay"  # b<i>te
    EH = "eh"  # b<e>t
    ER = "er"  # b<ir>d
    EY = "ey"  # b<a>it
    IH = "ih"  # b<i>t
    IY = "iy"  # b<ee>t
    OW = "ow"  # b<oa>t
    OY = "oy"  # b<oy>
    UH = "uh"  # b<oo>k
    UW = "uw"  # b<oo>t
    
    # Consonants
    B = "b"    # <b>at
    CH = "ch"  # <ch>at
    D = "d"    # <d>og
    DH = "dh"  # <th>is
    F = "f"    # <f>at
    G = "g"    # <g>o
    HH = "hh"  # <h>ot
    JH = "jh"  # <j>ump
    K = "k"    # <c>at
    L = "l"    # <l>et
    M = "m"    # <m>an
    N = "n"    # <n>o
    NG = "ng"  # si<ng>
    P = "p"    # <p>at
    R = "r"    # <r>un
    S = "s"    # <s>it
    SH = "sh"  # <sh>e
    T = "t"    # <t>op
    TH = "th"  # <th>in
    V = "v"    # <v>an
    W = "w"    # <w>et
    Y = "y"    # <y>es
    Z = "z"    # <z>oo
    ZH = "zh"  # vi<s>ion
    
    # Special
    SILENCE = "sil"  # pause


class Viseme(Enum):
    """
    Visemes: Visual phonemes (mouth shapes)
    Simplified from 44 phonemes to 15 visemes for animation
    """
    SILENCE = 0        # Mouth closed
    PP_BB_MM = 1       # Lips together (P, B, M)
    FF_VV = 2          # Lower lip to upper teeth (F, V)
    TH_DH = 3          # Tongue between teeth (TH, DH)
    DD_SS_TT = 4       # Tongue behind teeth (D, S, T, Z)
    KK_GG_NN = 5       # Back of tongue raised (K, G, NG)
    CH_JH_SH = 6       # Lips rounded forward (CH, JH, SH, ZH)
    RR = 7             # Lips slightly rounded (R)
    AA = 8             # Wide open mouth (AA, AE)
    EE = 9             # Lips spread wide (IY, EY)
    II = 10            # Slightly open, relaxed (IH, EH)
    OH = 11            # Rounded lips (OW, AO)
    OO = 12            # Very rounded, pursed lips (UW, UH)
    AH = 13            # Medium open (AH, ER)
    LL = 14            # Tongue up (L)
    WW = 15            # Lips rounded (W, OY, AW, AY)


@dataclass
class PhonemeSegment:
    """A phoneme with timing information"""
    phoneme: Phoneme
    viseme: Viseme
    start_time: float  # seconds
    duration: float    # seconds
    intensity: float   # 0.0-1.0 (volume/emphasis)
    
    @property
    def end_time(self) -> float:
        return self.start_time + self.duration


@dataclass
class LipSyncSequence:
    """Complete lip-sync animation sequence"""
    sequence_id: str
    text: str
    language: str
    phoneme_segments: List[PhonemeSegment] = field(default_factory=list)
    total_duration: float = 0.0
    frame_rate: int = 30  # FPS
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_viseme_at_time(self, time: float) -> Viseme:
        """Get the viseme that should be displayed at a given time"""
        for segment in self.phoneme_segments:
            if segment.start_time <= time <= segment.end_time:
                return segment.viseme
        return Viseme.SILENCE
    
    def get_frame_sequence(self) -> List[Viseme]:
        """Generate viseme sequence for each frame"""
        frames = []
        frame_duration = 1.0 / self.frame_rate
        
        for frame in range(int(self.total_duration * self.frame_rate)):
            time = frame * frame_duration
            viseme = self.get_viseme_at_time(time)
            frames.append(viseme)
        
        return frames


class PhonemeMapper:
    """
    Maps text to phonemes using pronunciation rules
    Simplified rule-based system (production would use CMU Pronouncing Dictionary)
    """
    
    def __init__(self):
        self.db_path = "jupiter_lipsync.db"
        self._init_database()
        self._load_pronunciation_rules()
    
    def _init_database(self):
        """Initialize lip-sync database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pronunciation dictionary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pronunciations (
                word TEXT PRIMARY KEY,
                phonemes TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_used TEXT
            )
        """)
        
        # Lip-sync sequences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lipsync_sequences (
                sequence_id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                phoneme_data TEXT NOT NULL,
                total_duration REAL,
                frame_rate INTEGER,
                created_at TEXT
            )
        """)
        
        # Viseme templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viseme_templates (
                viseme_id INTEGER PRIMARY KEY,
                viseme_name TEXT NOT NULL,
                mouth_shape_data TEXT,
                blend_shape_weights TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_pronunciation_rules(self):
        """Load basic pronunciation rules (simplified)"""
        # In production, would load CMU Pronouncing Dictionary
        # This is a simplified rule-based system
        
        self.vowel_map = {
            'a': Phoneme.AE,  # cat
            'e': Phoneme.EH,  # bet
            'i': Phoneme.IH,  # bit
            'o': Phoneme.AO,  # dot
            'u': Phoneme.AH,  # cut
            'ee': Phoneme.IY,  # beet
            'oo': Phoneme.UW,  # boot
            'ay': Phoneme.AY,  # bay
            'oy': Phoneme.OY,  # boy
            'ow': Phoneme.OW,  # bow
        }
        
        self.consonant_map = {
            'b': Phoneme.B,
            'c': Phoneme.K,
            'ch': Phoneme.CH,
            'd': Phoneme.D,
            'f': Phoneme.F,
            'g': Phoneme.G,
            'h': Phoneme.HH,
            'j': Phoneme.JH,
            'k': Phoneme.K,
            'l': Phoneme.L,
            'm': Phoneme.M,
            'n': Phoneme.N,
            'ng': Phoneme.NG,
            'p': Phoneme.P,
            'r': Phoneme.R,
            's': Phoneme.S,
            'sh': Phoneme.SH,
            't': Phoneme.T,
            'th': Phoneme.TH,
            'v': Phoneme.V,
            'w': Phoneme.W,
            'y': Phoneme.Y,
            'z': Phoneme.Z,
        }
    
    def text_to_phonemes(self, text: str) -> List[Phoneme]:
        """
        Convert text to phoneme sequence
        Simplified rule-based conversion
        """
        phonemes = []
        words = text.lower().split()
        
        for word in words:
            # Check database first
            word_phonemes = self._lookup_word(word)
            
            if not word_phonemes:
                # Apply rules (simplified)
                word_phonemes = self._apply_rules(word)
                self._cache_word(word, word_phonemes)
            
            phonemes.extend(word_phonemes)
            phonemes.append(Phoneme.SILENCE)  # Word boundary
        
        return phonemes
    
    def _lookup_word(self, word: str) -> Optional[List[Phoneme]]:
        """Look up word in pronunciation dictionary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT phonemes FROM pronunciations WHERE word = ?
        """, (word,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            phoneme_codes = result[0].split()
            return [Phoneme(code) for code in phoneme_codes]
        
        return None
    
    def _apply_rules(self, word: str) -> List[Phoneme]:
        """Apply pronunciation rules to unknown word"""
        phonemes = []
        i = 0
        
        while i < len(word):
            # Try two-character patterns first
            if i < len(word) - 1:
                two_char = word[i:i+2]
                if two_char in self.consonant_map:
                    phonemes.append(self.consonant_map[two_char])
                    i += 2
                    continue
                elif two_char in self.vowel_map:
                    phonemes.append(self.vowel_map[two_char])
                    i += 2
                    continue
            
            # Single character
            char = word[i]
            if char in self.consonant_map:
                phonemes.append(self.consonant_map[char])
            elif char in self.vowel_map:
                phonemes.append(self.vowel_map[char])
            
            i += 1
        
        return phonemes
    
    def _cache_word(self, word: str, phonemes: List[Phoneme]):
        """Cache word pronunciation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        phoneme_string = ' '.join([p.value for p in phonemes])
        
        cursor.execute("""
            INSERT OR REPLACE INTO pronunciations 
            (word, phonemes, last_used)
            VALUES (?, ?, ?)
        """, (word, phoneme_string, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()


class VisemeMapper:
    """Maps phonemes to visemes (mouth shapes)"""
    
    # Phoneme to viseme mapping
    PHONEME_TO_VISEME = {
        # Bilabial (lips together)
        Phoneme.P: Viseme.PP_BB_MM,
        Phoneme.B: Viseme.PP_BB_MM,
        Phoneme.M: Viseme.PP_BB_MM,
        
        # Labiodental (lip to teeth)
        Phoneme.F: Viseme.FF_VV,
        Phoneme.V: Viseme.FF_VV,
        
        # Dental (tongue between teeth)
        Phoneme.TH: Viseme.TH_DH,
        Phoneme.DH: Viseme.TH_DH,
        
        # Alveolar (tongue behind teeth)
        Phoneme.T: Viseme.DD_SS_TT,
        Phoneme.D: Viseme.DD_SS_TT,
        Phoneme.S: Viseme.DD_SS_TT,
        Phoneme.Z: Viseme.DD_SS_TT,
        Phoneme.N: Viseme.DD_SS_TT,
        
        # Velar (back of tongue)
        Phoneme.K: Viseme.KK_GG_NN,
        Phoneme.G: Viseme.KK_GG_NN,
        Phoneme.NG: Viseme.KK_GG_NN,
        
        # Palatal (tongue to palate)
        Phoneme.CH: Viseme.CH_JH_SH,
        Phoneme.JH: Viseme.CH_JH_SH,
        Phoneme.SH: Viseme.CH_JH_SH,
        Phoneme.ZH: Viseme.CH_JH_SH,
        Phoneme.Y: Viseme.CH_JH_SH,
        
        # Rhotic
        Phoneme.R: Viseme.RR,
        
        # Lateral
        Phoneme.L: Viseme.LL,
        
        # Glides
        Phoneme.W: Viseme.WW,
        Phoneme.HH: Viseme.SILENCE,
        
        # Vowels - open
        Phoneme.AA: Viseme.AA,
        Phoneme.AE: Viseme.AA,
        
        # Vowels - spread
        Phoneme.IY: Viseme.EE,
        Phoneme.EY: Viseme.EE,
        
        # Vowels - mid
        Phoneme.IH: Viseme.II,
        Phoneme.EH: Viseme.II,
        
        # Vowels - rounded
        Phoneme.OW: Viseme.OH,
        Phoneme.AO: Viseme.OH,
        
        # Vowels - very rounded
        Phoneme.UW: Viseme.OO,
        Phoneme.UH: Viseme.OO,
        
        # Vowels - neutral
        Phoneme.AH: Viseme.AH,
        Phoneme.ER: Viseme.AH,
        
        # Diphthongs
        Phoneme.AY: Viseme.WW,
        Phoneme.OY: Viseme.WW,
        Phoneme.AW: Viseme.WW,
        
        # Silence
        Phoneme.SILENCE: Viseme.SILENCE,
    }
    
    @classmethod
    def phoneme_to_viseme(cls, phoneme: Phoneme) -> Viseme:
        """Convert phoneme to viseme"""
        return cls.PHONEME_TO_VISEME.get(phoneme, Viseme.SILENCE)


class LipSyncEngine:
    """
    Main lip-sync engine
    Generates synchronized mouth animations from text
    """
    
    def __init__(self, db_path: str = "jupiter_lipsync.db"):
        self.db_path = db_path
        self.phoneme_mapper = PhonemeMapper()
        self.viseme_mapper = VisemeMapper()
        self._init_viseme_templates()
    
    def _init_viseme_templates(self):
        """Initialize viseme mouth shape templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define blend shape weights for each viseme
        # These control 3D avatar facial muscles
        viseme_shapes = {
            Viseme.SILENCE.value: {
                'jaw_open': 0.0,
                'lip_upper_up': 0.0,
                'lip_lower_down': 0.0,
                'lip_pucker': 0.0,
                'lip_stretch': 0.0
            },
            Viseme.PP_BB_MM.value: {
                'jaw_open': 0.0,
                'lip_upper_up': 0.0,
                'lip_lower_down': 0.0,
                'lip_pucker': 1.0,  # Lips together
                'lip_stretch': 0.0
            },
            Viseme.FF_VV.value: {
                'jaw_open': 0.2,
                'lip_upper_up': 0.0,
                'lip_lower_down': 0.8,  # Lower lip to teeth
                'lip_pucker': 0.0,
                'lip_stretch': 0.0
            },
            Viseme.AA.value: {
                'jaw_open': 0.9,  # Wide open
                'lip_upper_up': 0.3,
                'lip_lower_down': 0.3,
                'lip_pucker': 0.0,
                'lip_stretch': 0.7
            },
            Viseme.EE.value: {
                'jaw_open': 0.3,
                'lip_upper_up': 0.0,
                'lip_lower_down': 0.0,
                'lip_pucker': 0.0,
                'lip_stretch': 1.0  # Lips spread wide
            },
            Viseme.OH.value: {
                'jaw_open': 0.5,
                'lip_upper_up': 0.2,
                'lip_lower_down': 0.2,
                'lip_pucker': 0.8,  # Rounded
                'lip_stretch': 0.0
            },
            Viseme.OO.value: {
                'jaw_open': 0.3,
                'lip_upper_up': 0.0,
                'lip_lower_down': 0.0,
                'lip_pucker': 1.0,  # Very rounded
                'lip_stretch': 0.0
            },
        }
        
        for viseme_id, shape_data in viseme_shapes.items():
            cursor.execute("""
                INSERT OR REPLACE INTO viseme_templates 
                (viseme_id, viseme_name, blend_shape_weights)
                VALUES (?, ?, ?)
            """, (
                viseme_id,
                Viseme(viseme_id).name,
                json.dumps(shape_data)
            ))
        
        conn.commit()
        conn.close()
    
    def generate_lipsync(
        self,
        text: str,
        duration: float,
        language: str = "en",
        frame_rate: int = 30
    ) -> LipSyncSequence:
        """
        Generate complete lip-sync sequence from text
        
        Args:
            text: Text to speak
            duration: Total audio duration in seconds
            language: Language code
            frame_rate: Animation frame rate (FPS)
        
        Returns:
            LipSyncSequence with frame-by-frame visemes
        """
        
        # Convert text to phonemes
        phonemes = self.phoneme_mapper.text_to_phonemes(text)
        
        # Calculate timing for each phoneme
        phoneme_segments = self._calculate_timing(phonemes, duration)
        
        # Create sequence
        sequence = LipSyncSequence(
            sequence_id=f"lipsync_{datetime.now().timestamp()}",
            text=text,
            language=language,
            phoneme_segments=phoneme_segments,
            total_duration=duration,
            frame_rate=frame_rate
        )
        
        # Save to database
        self._save_sequence(sequence)
        
        return sequence
    
    def _calculate_timing(
        self,
        phonemes: List[Phoneme],
        total_duration: float
    ) -> List[PhonemeSegment]:
        """Calculate timing for each phoneme"""
        
        segments = []
        
        # Simple equal distribution (production would use speech rate analysis)
        phoneme_count = len(phonemes)
        base_duration = total_duration / phoneme_count if phoneme_count > 0 else 0.1
        
        current_time = 0.0
        
        for phoneme in phonemes:
            # Adjust duration based on phoneme type
            if phoneme == Phoneme.SILENCE:
                duration = base_duration * 0.5  # Shorter pauses
            elif phoneme in [Phoneme.AE, Phoneme.AA, Phoneme.AO]:
                duration = base_duration * 1.2  # Longer vowels
            else:
                duration = base_duration
            
            # Map to viseme
            viseme = self.viseme_mapper.phoneme_to_viseme(phoneme)
            
            segment = PhonemeSegment(
                phoneme=phoneme,
                viseme=viseme,
                start_time=current_time,
                duration=duration,
                intensity=0.8  # Default intensity
            )
            
            segments.append(segment)
            current_time += duration
        
        return segments
    
    def _save_sequence(self, sequence: LipSyncSequence):
        """Save lip-sync sequence to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize phoneme segments
        phoneme_data = []
        for segment in sequence.phoneme_segments:
            phoneme_data.append({
                'phoneme': segment.phoneme.value,
                'viseme': segment.viseme.value,
                'start_time': segment.start_time,
                'duration': segment.duration,
                'intensity': segment.intensity
            })
        
        cursor.execute("""
            INSERT OR REPLACE INTO lipsync_sequences 
            (sequence_id, text, language, phoneme_data, total_duration, 
             frame_rate, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sequence.sequence_id,
            sequence.text,
            sequence.language,
            json.dumps(phoneme_data),
            sequence.total_duration,
            sequence.frame_rate,
            sequence.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_blend_shapes_at_time(
        self,
        sequence: LipSyncSequence,
        time: float
    ) -> Dict[str, float]:
        """
        Get facial blend shape weights at specific time
        Used by 3D avatar renderer
        """
        viseme = sequence.get_viseme_at_time(time)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT blend_shape_weights FROM viseme_templates 
            WHERE viseme_id = ?
        """, (viseme.value,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        
        # Default neutral pose
        return {
            'jaw_open': 0.0,
            'lip_upper_up': 0.0,
            'lip_lower_down': 0.0,
            'lip_pucker': 0.0,
            'lip_stretch': 0.0
        }
    
    def export_animation(
        self,
        sequence: LipSyncSequence,
        format: str = "json"
    ) -> str:
        """
        Export animation sequence for external renderers
        
        Formats:
        - json: JSON keyframes
        - fbx: Autodesk FBX format
        - bvh: Biovision Hierarchy (motion capture)
        """
        
        if format == "json":
            frames = []
            frame_duration = 1.0 / sequence.frame_rate
            
            for frame_num in range(int(sequence.total_duration * sequence.frame_rate)):
                time = frame_num * frame_duration
                blend_shapes = self.get_blend_shapes_at_time(sequence, time)
                viseme = sequence.get_viseme_at_time(time)
                
                frames.append({
                    'frame': frame_num,
                    'time': time,
                    'viseme': viseme.name,
                    'blend_shapes': blend_shapes
                })
            
            return json.dumps({
                'sequence_id': sequence.sequence_id,
                'text': sequence.text,
                'duration': sequence.total_duration,
                'frame_rate': sequence.frame_rate,
                'frames': frames
            }, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_statistics(self) -> Dict:
        """Get lip-sync engine statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM lipsync_sequences")
        stats['total_sequences'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pronunciations")
        stats['cached_words'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(total_duration) FROM lipsync_sequences")
        stats['avg_duration'] = cursor.fetchone()[0] or 0.0
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    engine = LipSyncEngine()
    
    # Generate lip-sync for a sentence
    text = "Critical vulnerability detected in your system"
    duration = 3.5  # 3.5 seconds audio
    
    sequence = engine.generate_lipsync(text, duration)
    
    print(f"Generated lip-sync sequence:")
    print(f"Text: {sequence.text}")
    print(f"Duration: {sequence.total_duration}s")
    print(f"Phonemes: {len(sequence.phoneme_segments)}")
    print(f"Frame rate: {sequence.frame_rate} FPS")
    
    # Get viseme at 1.5 seconds
    viseme = sequence.get_viseme_at_time(1.5)
    print(f"\nViseme at 1.5s: {viseme.name}")
    
    # Get blend shapes for rendering
    blend_shapes = engine.get_blend_shapes_at_time(sequence, 1.5)
    print(f"Blend shapes: {blend_shapes}")
    
    # Export animation
    animation_json = engine.export_animation(sequence)
    print(f"\nAnimation data exported ({len(animation_json)} bytes)")
    
    # Statistics
    stats = engine.get_statistics()
    print(f"\nEngine stats: {stats}")
