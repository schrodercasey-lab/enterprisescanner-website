"""
Jupiter ARIA - Multi-Avatar Management System
Manages multiple avatars for team representation and collaboration
"""

import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum


class AvatarRole(Enum):
    """Avatar role in team"""
    PRIMARY = "primary"              # Main AI assistant
    ANALYST = "analyst"              # Security analyst
    MANAGER = "manager"              # Security manager
    EXECUTIVE = "executive"          # Executive/CISO
    SPECIALIST = "specialist"        # Domain specialist
    SUPPORT = "support"              # Support assistant


class AvatarPersonality(Enum):
    """Avatar personality type"""
    PROFESSIONAL = "professional"    # Formal, business-focused
    FRIENDLY = "friendly"            # Warm, approachable
    TECHNICAL = "technical"          # Detail-oriented, technical
    EXECUTIVE = "executive"          # Strategic, high-level
    ENERGETIC = "energetic"          # Dynamic, enthusiastic


@dataclass
class AvatarConfig:
    """Avatar configuration"""
    avatar_id: str
    name: str
    role: AvatarRole
    personality: AvatarPersonality
    appearance: Dict[str, any] = field(default_factory=dict)
    voice_settings: Dict[str, any] = field(default_factory=dict)
    expertise: List[str] = field(default_factory=list)
    active: bool = True


@dataclass
class AvatarPosition:
    """3D position and orientation"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    scale: float = 1.0


@dataclass
class TeamLayout(Enum):
    """Multi-avatar layout configurations"""
    SINGLE = "single"                # One avatar
    SIDE_BY_SIDE = "side_by_side"    # Two avatars side by side
    PANEL = "panel"                  # Multiple avatars in panel
    SEMICIRCLE = "semicircle"        # Avatars in semicircle
    CONFERENCE = "conference"        # Conference table layout


class MultiAvatarManager:
    """
    Manages multiple avatars for team representation
    Handles positioning, coordination, and synchronized interactions
    """
    
    def __init__(self, db_path: str = "jupiter_multiavatar.db"):
        self.db_path = db_path
        self.active_avatars: Dict[str, AvatarConfig] = {}
        self.avatar_positions: Dict[str, AvatarPosition] = {}
        self.current_layout = TeamLayout.SINGLE
        self._init_database()
    
    def _init_database(self):
        """Initialize multi-avatar database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Avatar configurations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avatars (
                avatar_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                personality TEXT NOT NULL,
                appearance_data TEXT,
                voice_settings TEXT,
                expertise TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        
        # Avatar positions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avatar_positions (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                avatar_id TEXT NOT NULL,
                layout TEXT NOT NULL,
                x REAL, y REAL, z REAL,
                rotation_x REAL, rotation_y REAL, rotation_z REAL,
                scale REAL DEFAULT 1.0,
                FOREIGN KEY (avatar_id) REFERENCES avatars(avatar_id)
            )
        """)
        
        # Team interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                speaker_id TEXT NOT NULL,
                listener_ids TEXT,
                interaction_type TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        self._create_default_team()
    
    def _create_default_team(self):
        """Create default team avatars"""
        
        default_team = [
            {
                'avatar_id': 'aria_primary',
                'name': 'ARIA',
                'role': AvatarRole.PRIMARY,
                'personality': AvatarPersonality.FRIENDLY,
                'expertise': ['General AI', 'Security Analysis', 'Vulnerability Management']
            },
            {
                'avatar_id': 'max_analyst',
                'name': 'Max',
                'role': AvatarRole.ANALYST,
                'personality': AvatarPersonality.TECHNICAL,
                'expertise': ['Threat Intelligence', 'CVE Analysis', 'Penetration Testing']
            },
            {
                'avatar_id': 'sarah_manager',
                'name': 'Sarah',
                'role': AvatarRole.MANAGER,
                'personality': AvatarPersonality.PROFESSIONAL,
                'expertise': ['Risk Management', 'Compliance', 'Security Operations']
            },
            {
                'avatar_id': 'james_exec',
                'name': 'James',
                'role': AvatarRole.EXECUTIVE,
                'personality': AvatarPersonality.EXECUTIVE,
                'expertise': ['Strategic Planning', 'Business Risk', 'Executive Reporting']
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for avatar_data in default_team:
            cursor.execute("""
                INSERT OR IGNORE INTO avatars 
                (avatar_id, name, role, personality, expertise, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                avatar_data['avatar_id'],
                avatar_data['name'],
                avatar_data['role'].value,
                avatar_data['personality'].value,
                json.dumps(avatar_data['expertise']),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def add_avatar(self, config: AvatarConfig):
        """Add new avatar to team"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO avatars 
            (avatar_id, name, role, personality, appearance_data, 
             voice_settings, expertise, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.avatar_id,
            config.name,
            config.role.value,
            config.personality.value,
            json.dumps(config.appearance),
            json.dumps(config.voice_settings),
            json.dumps(config.expertise),
            1 if config.active else 0,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.active_avatars[config.avatar_id] = config
    
    def set_layout(self, layout: TeamLayout, avatar_ids: List[str]):
        """
        Configure avatar layout
        
        Args:
            layout: Layout type
            avatar_ids: List of avatar IDs to position
        """
        
        self.current_layout = layout
        positions = self._calculate_positions(layout, avatar_ids)
        
        for avatar_id, position in positions.items():
            self.avatar_positions[avatar_id] = position
            self._save_position(avatar_id, layout, position)
    
    def _calculate_positions(
        self,
        layout: TeamLayout,
        avatar_ids: List[str]
    ) -> Dict[str, AvatarPosition]:
        """Calculate avatar positions based on layout"""
        
        positions = {}
        
        if layout == TeamLayout.SINGLE:
            # Single centered avatar
            positions[avatar_ids[0]] = AvatarPosition(x=0, y=0, z=0)
        
        elif layout == TeamLayout.SIDE_BY_SIDE:
            # Two avatars side by side
            spacing = 2.0
            for i, avatar_id in enumerate(avatar_ids[:2]):
                x = (i - 0.5) * spacing
                positions[avatar_id] = AvatarPosition(x=x, y=0, z=0)
        
        elif layout == TeamLayout.PANEL:
            # Multiple avatars in horizontal panel
            spacing = 2.5
            count = len(avatar_ids)
            start_x = -(count - 1) * spacing / 2
            
            for i, avatar_id in enumerate(avatar_ids):
                x = start_x + i * spacing
                positions[avatar_id] = AvatarPosition(x=x, y=0, z=0)
        
        elif layout == TeamLayout.SEMICIRCLE:
            # Avatars arranged in semicircle
            import math
            radius = 3.0
            count = len(avatar_ids)
            angle_step = math.pi / (count + 1)
            
            for i, avatar_id in enumerate(avatar_ids):
                angle = (i + 1) * angle_step
                x = radius * math.cos(angle + math.pi / 2)
                z = radius * math.sin(angle + math.pi / 2)
                rotation_y = -angle * 180 / math.pi
                
                positions[avatar_id] = AvatarPosition(
                    x=x, y=0, z=z, rotation_y=rotation_y
                )
        
        elif layout == TeamLayout.CONFERENCE:
            # Conference table arrangement
            positions_list = [
                (-2.5, 0, 1.5),  # Left front
                (2.5, 0, 1.5),   # Right front
                (-3.0, 0, -1.0), # Left back
                (3.0, 0, -1.0),  # Right back
            ]
            
            for i, avatar_id in enumerate(avatar_ids[:4]):
                x, y, z = positions_list[i]
                rotation_y = 180 if z < 0 else 0
                positions[avatar_id] = AvatarPosition(
                    x=x, y=y, z=z, rotation_y=rotation_y
                )
        
        return positions
    
    def _save_position(
        self,
        avatar_id: str,
        layout: TeamLayout,
        position: AvatarPosition
    ):
        """Save avatar position to database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO avatar_positions 
            (avatar_id, layout, x, y, z, rotation_x, rotation_y, rotation_z, scale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            avatar_id,
            layout.value,
            position.x, position.y, position.z,
            position.rotation_x, position.rotation_y, position.rotation_z,
            position.scale
        ))
        
        conn.commit()
        conn.close()
    
    def coordinate_interaction(
        self,
        speaker_id: str,
        listener_ids: List[str],
        interaction_type: str = "speak"
    ):
        """
        Coordinate interaction between avatars
        
        Args:
            speaker_id: ID of speaking avatar
            listener_ids: IDs of listening avatars
            interaction_type: Type of interaction (speak, gesture, look_at)
        """
        
        # Log interaction
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO team_interactions 
            (speaker_id, listener_ids, interaction_type, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            speaker_id,
            json.dumps(listener_ids),
            interaction_type,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Trigger avatar behaviors
        if interaction_type == "speak":
            # Make listeners look at speaker
            self._make_look_at(listener_ids, speaker_id)
        elif interaction_type == "gesture":
            # Make listeners respond to gesture
            self._trigger_reactions(listener_ids)
    
    def _make_look_at(self, avatar_ids: List[str], target_id: str):
        """Make avatars look at target"""
        
        if target_id not in self.avatar_positions:
            return
        
        target_pos = self.avatar_positions[target_id]
        
        for avatar_id in avatar_ids:
            if avatar_id in self.avatar_positions:
                pos = self.avatar_positions[avatar_id]
                
                # Calculate rotation to face target
                import math
                dx = target_pos.x - pos.x
                dz = target_pos.z - pos.z
                
                if abs(dx) > 0.1 or abs(dz) > 0.1:
                    angle = math.atan2(dx, dz) * 180 / math.pi
                    pos.rotation_y = angle
    
    def _trigger_reactions(self, avatar_ids: List[str]):
        """Trigger reaction animations on avatars"""
        # Placeholder for reaction system
        # Would trigger nods, smiles, etc.
        pass
    
    def get_avatar_by_role(self, role: AvatarRole) -> Optional[AvatarConfig]:
        """Get avatar by role"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT avatar_id, name, role, personality, expertise 
            FROM avatars 
            WHERE role = ? AND is_active = 1
            LIMIT 1
        """, (role.value,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return AvatarConfig(
                avatar_id=row[0],
                name=row[1],
                role=AvatarRole(row[2]),
                personality=AvatarPersonality(row[3]),
                expertise=json.loads(row[4]) if row[4] else []
            )
        
        return None
    
    def get_active_avatars(self) -> List[AvatarConfig]:
        """Get all active avatars"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT avatar_id, name, role, personality, expertise 
            FROM avatars 
            WHERE is_active = 1
        """)
        
        avatars = []
        for row in cursor.fetchall():
            avatars.append(AvatarConfig(
                avatar_id=row[0],
                name=row[1],
                role=AvatarRole(row[2]),
                personality=AvatarPersonality(row[3]),
                expertise=json.loads(row[4]) if row[4] else []
            ))
        
        conn.close()
        return avatars
    
    def get_statistics(self) -> Dict:
        """Get multi-avatar statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = 1")
        stats['active_avatars'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM team_interactions")
        stats['total_interactions'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT role, COUNT(*) 
            FROM avatars 
            WHERE is_active = 1 
            GROUP BY role
        """)
        stats['avatars_by_role'] = dict(cursor.fetchall())
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    manager = MultiAvatarManager()
    
    print("Multi-Avatar Manager - Team Configuration\n")
    
    # Get active team
    team = manager.get_active_avatars()
    print(f"Active Team Members: {len(team)}")
    for avatar in team:
        print(f"  - {avatar.name} ({avatar.role.value}): {', '.join(avatar.expertise)}")
    
    print()
    
    # Test different layouts
    layouts = [
        TeamLayout.SIDE_BY_SIDE,
        TeamLayout.PANEL,
        TeamLayout.SEMICIRCLE,
        TeamLayout.CONFERENCE
    ]
    
    avatar_ids = [a.avatar_id for a in team]
    
    for layout in layouts:
        print(f"\nLayout: {layout.value}")
        manager.set_layout(layout, avatar_ids)
        
        for avatar_id in avatar_ids[:3]:  # Show first 3
            if avatar_id in manager.avatar_positions:
                pos = manager.avatar_positions[avatar_id]
                print(f"  {avatar_id}: x={pos.x:.1f}, z={pos.z:.1f}, rotation={pos.rotation_y:.0f}°")
    
    # Simulate team interaction
    print("\n\nSimulating Team Interaction:")
    primary = manager.get_avatar_by_role(AvatarRole.PRIMARY)
    analyst = manager.get_avatar_by_role(AvatarRole.ANALYST)
    
    if primary and analyst:
        print(f"{primary.name} speaking to {analyst.name}")
        manager.coordinate_interaction(
            primary.avatar_id,
            [analyst.avatar_id],
            "speak"
        )
    
    # Statistics
    stats = manager.get_statistics()
    print(f"\nStatistics: {stats}")
