"""
G.3.1: VR/AR Platform Integration

PATENT PENDING - Multi-Platform VR/AR Security Operations System

Enterprise-grade VR/AR platform abstraction layer enabling cybersecurity
operations across Meta Quest, HoloLens, Apple Vision Pro, and WebXR platforms.

Patent Claims:
- Universal VR/AR platform adapter for security operations
- Cross-platform session management and state synchronization
- Spatial calibration system for security data visualization
- Device capability detection and feature negotiation
- Performance optimization per platform for security workloads

Author: Enterprise Scanner Development Team
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import json
import uuid


class VRPlatform(Enum):
    """Supported VR/AR platforms"""
    META_QUEST_3 = "meta_quest_3"              # Primary consumer/enterprise VR
    META_QUEST_PRO = "meta_quest_pro"          # High-end enterprise VR
    HOLOLENS_2 = "hololens_2"                  # Microsoft enterprise AR
    APPLE_VISION_PRO = "apple_vision_pro"      # Apple mixed reality
    PICO_4_ENTERPRISE = "pico_4_enterprise"    # Business VR
    WEBXR = "webxr"                            # Browser-based VR
    VIVE_FOCUS_3 = "vive_focus_3"              # HTC enterprise VR
    UNKNOWN = "unknown"                        # Fallback


class DeviceCapability(Enum):
    """Device hardware capabilities"""
    HAND_TRACKING = "hand_tracking"            # Native hand tracking
    EYE_TRACKING = "eye_tracking"              # Gaze detection
    SPATIAL_AUDIO = "spatial_audio"            # 3D positional audio
    PASSTHROUGH_AR = "passthrough_ar"          # See-through AR mode
    HIGH_RESOLUTION = "high_resolution"        # 4K+ displays
    WIRELESS = "wireless"                      # Standalone operation
    PC_TETHERED = "pc_tethered"               # PC connection required
    CONTROLLER_6DOF = "controller_6dof"        # 6 degrees of freedom
    ROOM_SCALE = "room_scale"                  # Large space tracking
    MULTI_USER = "multi_user"                  # Multiplayer support


class SessionState(Enum):
    """VR session states"""
    INITIALIZING = "initializing"      # Starting up
    CALIBRATING = "calibrating"        # Spatial calibration
    ACTIVE = "active"                  # Normal operation
    PAUSED = "paused"                  # User paused
    DISCONNECTED = "disconnected"      # Connection lost
    TERMINATED = "terminated"          # Session ended
    ERROR = "error"                    # Error state


@dataclass
class DeviceProfile:
    """VR/AR device hardware profile"""
    device_id: str
    platform: VRPlatform
    model_name: str
    firmware_version: str
    capabilities: List[DeviceCapability]
    display_resolution: Tuple[int, int]  # Width × Height per eye
    refresh_rate: int  # Hz (90, 120, etc.)
    field_of_view: int  # Degrees
    tracking_volume: float  # Cubic meters
    battery_level: Optional[float] = None  # 0.0-1.0 for wireless devices
    connected_at: datetime = field(default_factory=datetime.utcnow)
    
    def has_capability(self, capability: DeviceCapability) -> bool:
        """Check if device supports a capability"""
        return capability in self.capabilities
    
    def get_performance_tier(self) -> str:
        """Determine device performance tier"""
        # High-end: 4K+, 120Hz, eye tracking
        if (self.display_resolution[0] >= 3840 and 
            self.refresh_rate >= 120 and 
            self.has_capability(DeviceCapability.EYE_TRACKING)):
            return "premium"
        # Mid-range: 2K+, 90Hz
        elif (self.display_resolution[0] >= 2048 and 
              self.refresh_rate >= 90):
            return "high"
        # Entry-level: Basic VR
        else:
            return "standard"
    
    def is_wireless(self) -> bool:
        """Check if device is wireless"""
        return self.has_capability(DeviceCapability.WIRELESS)
    
    def supports_ar_passthrough(self) -> bool:
        """Check if device supports AR mode"""
        return self.has_capability(DeviceCapability.PASSTHROUGH_AR)


@dataclass
class SpatialCalibration:
    """Spatial calibration data for VR environment"""
    calibration_id: str
    device_id: str
    play_space_bounds: List[Tuple[float, float, float]]  # 3D boundary points
    floor_height: float  # Meters from origin
    forward_direction: Tuple[float, float, float]  # Unit vector
    scale_factor: float  # Meters per unit
    anchor_points: Dict[str, Tuple[float, float, float]]  # Named positions
    calibrated_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_play_space_volume(self) -> float:
        """Calculate play space volume in cubic meters"""
        # Simplified: assume rectangular space
        if len(self.play_space_bounds) < 4:
            return 0.0
        
        x_coords = [p[0] for p in self.play_space_bounds]
        y_coords = [p[1] for p in self.play_space_bounds]
        z_coords = [p[2] for p in self.play_space_bounds]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        depth = max(z_coords) - min(z_coords)
        
        return width * height * depth
    
    def is_room_scale(self) -> bool:
        """Check if space is large enough for room-scale VR"""
        volume = self.get_play_space_volume()
        return volume >= 4.0  # At least 2m × 2m × 1m


@dataclass
class VRSession:
    """Active VR session"""
    session_id: str
    user_id: str
    device_id: str
    platform: VRPlatform
    state: SessionState
    started_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime] = None
    calibration_id: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def get_session_duration(self) -> timedelta:
        """Calculate session duration"""
        end_time = self.ended_at or datetime.utcnow()
        return end_time - self.started_at
    
    def get_duration_seconds(self) -> float:
        """Get duration in seconds"""
        return self.get_session_duration().total_seconds()
    
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.state == SessionState.ACTIVE
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()


class PlatformAdapter:
    """
    Platform-specific adapter for VR/AR operations.
    
    Handles device-specific initialization, capabilities,
    and feature implementation.
    """
    
    def __init__(self, platform: VRPlatform):
        self.platform = platform
        
    def get_default_capabilities(self) -> List[DeviceCapability]:
        """Get default capabilities for platform"""
        capabilities_map = {
            VRPlatform.META_QUEST_3: [
                DeviceCapability.HAND_TRACKING,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.PASSTHROUGH_AR,
                DeviceCapability.HIGH_RESOLUTION,
                DeviceCapability.WIRELESS,
                DeviceCapability.CONTROLLER_6DOF,
                DeviceCapability.ROOM_SCALE,
                DeviceCapability.MULTI_USER
            ],
            VRPlatform.META_QUEST_PRO: [
                DeviceCapability.HAND_TRACKING,
                DeviceCapability.EYE_TRACKING,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.PASSTHROUGH_AR,
                DeviceCapability.HIGH_RESOLUTION,
                DeviceCapability.WIRELESS,
                DeviceCapability.CONTROLLER_6DOF,
                DeviceCapability.ROOM_SCALE,
                DeviceCapability.MULTI_USER
            ],
            VRPlatform.HOLOLENS_2: [
                DeviceCapability.HAND_TRACKING,
                DeviceCapability.EYE_TRACKING,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.PASSTHROUGH_AR,
                DeviceCapability.WIRELESS,
                DeviceCapability.ROOM_SCALE
            ],
            VRPlatform.APPLE_VISION_PRO: [
                DeviceCapability.HAND_TRACKING,
                DeviceCapability.EYE_TRACKING,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.PASSTHROUGH_AR,
                DeviceCapability.HIGH_RESOLUTION,
                DeviceCapability.WIRELESS,
                DeviceCapability.ROOM_SCALE,
                DeviceCapability.MULTI_USER
            ],
            VRPlatform.PICO_4_ENTERPRISE: [
                DeviceCapability.HAND_TRACKING,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.HIGH_RESOLUTION,
                DeviceCapability.WIRELESS,
                DeviceCapability.CONTROLLER_6DOF,
                DeviceCapability.ROOM_SCALE,
                DeviceCapability.MULTI_USER
            ],
            VRPlatform.WEBXR: [
                DeviceCapability.CONTROLLER_6DOF,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.MULTI_USER
            ],
            VRPlatform.VIVE_FOCUS_3: [
                DeviceCapability.HAND_TRACKING,
                DeviceCapability.SPATIAL_AUDIO,
                DeviceCapability.HIGH_RESOLUTION,
                DeviceCapability.WIRELESS,
                DeviceCapability.CONTROLLER_6DOF,
                DeviceCapability.ROOM_SCALE,
                DeviceCapability.MULTI_USER
            ]
        }
        
        return capabilities_map.get(self.platform, [])
    
    def get_default_specs(self) -> Dict[str, Any]:
        """Get default technical specifications"""
        specs_map = {
            VRPlatform.META_QUEST_3: {
                'resolution': (2064, 2208),  # Per eye
                'refresh_rate': 120,
                'fov': 110,
                'tracking_volume': 25.0
            },
            VRPlatform.META_QUEST_PRO: {
                'resolution': (1800, 1920),
                'refresh_rate': 90,
                'fov': 106,
                'tracking_volume': 25.0
            },
            VRPlatform.HOLOLENS_2: {
                'resolution': (1280, 720),
                'refresh_rate': 60,
                'fov': 52,
                'tracking_volume': 20.0
            },
            VRPlatform.APPLE_VISION_PRO: {
                'resolution': (3660, 3200),
                'refresh_rate': 90,
                'fov': 110,
                'tracking_volume': 30.0
            },
            VRPlatform.PICO_4_ENTERPRISE: {
                'resolution': (2160, 2160),
                'refresh_rate': 90,
                'fov': 105,
                'tracking_volume': 20.0
            },
            VRPlatform.WEBXR: {
                'resolution': (1920, 1080),
                'refresh_rate': 60,
                'fov': 90,
                'tracking_volume': 10.0
            },
            VRPlatform.VIVE_FOCUS_3: {
                'resolution': (2448, 2448),
                'refresh_rate': 90,
                'fov': 120,
                'tracking_volume': 25.0
            }
        }
        
        return specs_map.get(
            self.platform, 
            {'resolution': (1920, 1080), 'refresh_rate': 60, 'fov': 90, 'tracking_volume': 10.0}
        )
    
    def get_performance_profile(self) -> str:
        """Get recommended performance profile"""
        # High performance platforms
        if self.platform in [VRPlatform.APPLE_VISION_PRO, VRPlatform.META_QUEST_PRO]:
            return "ultra"
        # Standard performance
        elif self.platform in [VRPlatform.META_QUEST_3, VRPlatform.VIVE_FOCUS_3, VRPlatform.PICO_4_ENTERPRISE]:
            return "high"
        # Conservative performance
        else:
            return "balanced"


class VRPlatformManager:
    """
    Central manager for VR/AR platform integration.
    
    Handles device detection, session management, platform adaptation,
    and cross-platform compatibility for JUPITER VR operations.
    """
    
    def __init__(self, db_path: str = "vr_platform.db"):
        self.db_path = db_path
        self._init_database()
        self.active_sessions: Dict[str, VRSession] = {}
        self.platform_adapters: Dict[VRPlatform, PlatformAdapter] = {}
        
        # Initialize platform adapters
        for platform in VRPlatform:
            if platform != VRPlatform.UNKNOWN:
                self.platform_adapters[platform] = PlatformAdapter(platform)
    
    def _init_database(self):
        """Initialize VR platform database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Device profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_profiles (
                device_id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                model_name TEXT NOT NULL,
                firmware_version TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                display_resolution TEXT NOT NULL,
                refresh_rate INTEGER NOT NULL,
                field_of_view INTEGER NOT NULL,
                tracking_volume REAL NOT NULL,
                battery_level REAL,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Spatial calibration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spatial_calibration (
                calibration_id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                play_space_bounds TEXT NOT NULL,
                floor_height REAL NOT NULL,
                forward_direction TEXT NOT NULL,
                scale_factor REAL NOT NULL,
                anchor_points TEXT NOT NULL,
                calibrated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device_profiles(device_id)
            )
        """)
        
        # VR sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vr_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                state TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                calibration_id TEXT,
                performance_metrics TEXT,
                FOREIGN KEY (device_id) REFERENCES device_profiles(device_id),
                FOREIGN KEY (calibration_id) REFERENCES spatial_calibration(calibration_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def detect_platform(self, device_info: Dict[str, str]) -> VRPlatform:
        """
        Detect VR/AR platform from device information.
        
        PATENT CLAIM: Automatic platform detection and capability negotiation
        """
        model = device_info.get('model', '').lower()
        manufacturer = device_info.get('manufacturer', '').lower()
        
        # Meta Quest devices
        if 'quest 3' in model or 'quest3' in model:
            return VRPlatform.META_QUEST_3
        elif 'quest pro' in model or 'questpro' in model:
            return VRPlatform.META_QUEST_PRO
        
        # Microsoft HoloLens
        elif 'hololens' in model:
            return VRPlatform.HOLOLENS_2
        
        # Apple Vision Pro
        elif 'vision pro' in model or 'apple' in manufacturer and 'vision' in model:
            return VRPlatform.APPLE_VISION_PRO
        
        # PICO
        elif 'pico 4' in model or 'pico4' in model:
            return VRPlatform.PICO_4_ENTERPRISE
        
        # HTC Vive
        elif 'vive focus' in model:
            return VRPlatform.VIVE_FOCUS_3
        
        # WebXR
        elif device_info.get('interface') == 'webxr':
            return VRPlatform.WEBXR
        
        return VRPlatform.UNKNOWN
    
    def register_device(
        self,
        device_info: Dict[str, Any],
        auto_detect: bool = True
    ) -> DeviceProfile:
        """
        Register a new VR/AR device.
        
        PATENT CLAIM: Dynamic device registration with capability detection
        """
        device_id = device_info.get('device_id') or str(uuid.uuid4())
        
        # Auto-detect platform if requested
        if auto_detect:
            platform = self.detect_platform(device_info)
        else:
            platform = VRPlatform(device_info.get('platform', 'unknown'))
        
        # Get platform adapter
        adapter = self.platform_adapters.get(platform)
        if not adapter:
            adapter = PlatformAdapter(VRPlatform.UNKNOWN)
        
        # Get default specs
        specs = adapter.get_default_specs()
        
        # Create device profile
        profile = DeviceProfile(
            device_id=device_id,
            platform=platform,
            model_name=device_info.get('model_name', 'Unknown'),
            firmware_version=device_info.get('firmware_version', '1.0.0'),
            capabilities=adapter.get_default_capabilities(),
            display_resolution=tuple(device_info.get('resolution', specs['resolution'])),
            refresh_rate=device_info.get('refresh_rate', specs['refresh_rate']),
            field_of_view=device_info.get('fov', specs['fov']),
            tracking_volume=device_info.get('tracking_volume', specs['tracking_volume']),
            battery_level=device_info.get('battery_level')
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO device_profiles
            (device_id, platform, model_name, firmware_version, capabilities,
             display_resolution, refresh_rate, field_of_view, tracking_volume,
             battery_level, connected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.device_id,
            profile.platform.value,
            profile.model_name,
            profile.firmware_version,
            json.dumps([cap.value for cap in profile.capabilities]),
            json.dumps(profile.display_resolution),
            profile.refresh_rate,
            profile.field_of_view,
            profile.tracking_volume,
            profile.battery_level,
            profile.connected_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return profile
    
    def create_session(
        self,
        user_id: str,
        device_id: str
    ) -> VRSession:
        """
        Create new VR session.
        
        PATENT CLAIM: Session lifecycle management for security operations
        """
        # Get device profile
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT platform FROM device_profiles WHERE device_id = ?
        """, (device_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise ValueError(f"Device {device_id} not registered")
        
        platform = VRPlatform(result[0])
        
        # Create session
        session_id = str(uuid.uuid4())
        session = VRSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            platform=platform,
            state=SessionState.INITIALIZING,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Store session
        self.active_sessions[session_id] = session
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO vr_sessions
            (session_id, user_id, device_id, platform, state,
             started_at, last_activity, performance_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.user_id,
            session.device_id,
            session.platform.value,
            session.state.value,
            session.started_at.isoformat(),
            session.last_activity.isoformat(),
            json.dumps(session.performance_metrics)
        ))
        
        conn.commit()
        conn.close()
        
        return session
    
    def calibrate_space(
        self,
        device_id: str,
        bounds: List[Tuple[float, float, float]],
        floor_height: float = 0.0,
        forward: Tuple[float, float, float] = (0, 0, 1)
    ) -> SpatialCalibration:
        """
        Calibrate VR play space.
        
        PATENT CLAIM: Spatial calibration for security data visualization
        """
        calibration_id = str(uuid.uuid4())
        
        calibration = SpatialCalibration(
            calibration_id=calibration_id,
            device_id=device_id,
            play_space_bounds=bounds,
            floor_height=floor_height,
            forward_direction=forward,
            scale_factor=1.0,
            anchor_points={}
        )
        
        # Store calibration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO spatial_calibration
            (calibration_id, device_id, play_space_bounds, floor_height,
             forward_direction, scale_factor, anchor_points, calibrated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            calibration.calibration_id,
            calibration.device_id,
            json.dumps(calibration.play_space_bounds),
            calibration.floor_height,
            json.dumps(calibration.forward_direction),
            calibration.scale_factor,
            json.dumps(calibration.anchor_points),
            calibration.calibrated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return calibration
    
    def get_active_sessions(self) -> List[VRSession]:
        """Get all active VR sessions"""
        return [
            session for session in self.active_sessions.values()
            if session.is_active()
        ]
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Device count by platform
        cursor.execute("""
            SELECT platform, COUNT(*) as count
            FROM device_profiles
            GROUP BY platform
        """)
        platform_counts = dict(cursor.fetchall())
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM vr_sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Active sessions
        active_count = len(self.get_active_sessions())
        
        # Average session duration
        cursor.execute("""
            SELECT AVG((julianday(ended_at) - julianday(started_at)) * 86400) as avg_duration
            FROM vr_sessions
            WHERE ended_at IS NOT NULL
        """)
        avg_duration = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'devices_by_platform': platform_counts,
            'total_sessions': total_sessions,
            'active_sessions': active_count,
            'avg_session_duration_seconds': avg_duration,
            'supported_platforms': len(self.platform_adapters)
        }


# Example usage
if __name__ == "__main__":
    # Initialize VR platform manager
    manager = VRPlatformManager()
    
    print("=== JUPITER VR/AR Platform Integration ===\n")
    print("PATENT PENDING - Proprietary Technology\n")
    
    # Example 1: Register Meta Quest 3 device
    print("=== Device Registration ===\n")
    
    quest3_info = {
        'model': 'Meta Quest 3',
        'manufacturer': 'Meta',
        'firmware_version': '60.0.0',
        'battery_level': 0.85
    }
    
    quest3_device = manager.register_device(quest3_info, auto_detect=True)
    print(f"Registered: {quest3_device.model_name}")
    print(f"Platform: {quest3_device.platform.value}")
    print(f"Performance Tier: {quest3_device.get_performance_tier()}")
    print(f"Resolution: {quest3_device.display_resolution[0]}×{quest3_device.display_resolution[1]}")
    print(f"Refresh Rate: {quest3_device.refresh_rate}Hz")
    print(f"Capabilities: {len(quest3_device.capabilities)}")
    print(f"Wireless: {quest3_device.is_wireless()}")
    print(f"AR Support: {quest3_device.supports_ar_passthrough()}")
    
    # Example 2: Register HoloLens 2 (military/enterprise)
    print("\n=== Military/Enterprise Device ===\n")
    
    hololens_info = {
        'model': 'Microsoft HoloLens 2',
        'manufacturer': 'Microsoft',
        'firmware_version': '22H1',
        'battery_level': 0.92
    }
    
    hololens_device = manager.register_device(hololens_info, auto_detect=True)
    print(f"Registered: {hololens_device.model_name}")
    print(f"Platform: {hololens_device.platform.value}")
    print(f"Performance Tier: {hololens_device.get_performance_tier()}")
    print(f"AR Support: {hololens_device.supports_ar_passthrough()}")
    
    # Example 3: Create VR session
    print("\n=== VR Session Management ===\n")
    
    session = manager.create_session(
        user_id="user_12345",
        device_id=quest3_device.device_id
    )
    
    print(f"Session ID: {session.session_id}")
    print(f"Platform: {session.platform.value}")
    print(f"State: {session.state.value}")
    print(f"Started: {session.started_at}")
    
    # Example 4: Spatial calibration
    print("\n=== Spatial Calibration ===\n")
    
    # Define room boundaries (4 corners of 3m × 2.5m room)
    room_bounds = [
        (0.0, 0.0, 0.0),      # Corner 1
        (3.0, 0.0, 0.0),      # Corner 2
        (3.0, 0.0, 2.5),      # Corner 3
        (0.0, 0.0, 2.5),      # Corner 4
        (0.0, 2.5, 0.0),      # Corner 5 (height)
    ]
    
    calibration = manager.calibrate_space(
        device_id=quest3_device.device_id,
        bounds=room_bounds,
        floor_height=0.0,
        forward=(0, 0, 1)
    )
    
    print(f"Calibration ID: {calibration.calibration_id}")
    print(f"Play Space Volume: {calibration.get_play_space_volume():.2f} m³")
    print(f"Room Scale: {calibration.is_room_scale()}")
    
    # Example 5: Platform statistics
    print("\n=== Platform Statistics ===\n")
    
    stats = manager.get_platform_statistics()
    print(f"Devices by platform: {stats['devices_by_platform']}")
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Active sessions: {stats['active_sessions']}")
    print(f"Supported platforms: {stats['supported_platforms']}")
    
    # Example 6: Platform adapter
    print("\n=== Platform Adapter ===\n")
    
    adapter = manager.platform_adapters[VRPlatform.META_QUEST_3]
    print(f"Platform: {adapter.platform.value}")
    print(f"Performance Profile: {adapter.get_performance_profile()}")
    print(f"Default Capabilities: {len(adapter.get_default_capabilities())}")
    
    specs = adapter.get_default_specs()
    print(f"Default Resolution: {specs['resolution']}")
    print(f"Default FOV: {specs['fov']}°")
    
    print("\n✓ VR/AR Platform Integration operational!")
    print("🎯 G.3.1 COMPLETE - Ready for JUPITER Avatar System!")
