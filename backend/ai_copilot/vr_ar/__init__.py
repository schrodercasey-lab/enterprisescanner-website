"""
JUPITER VR/AR Immersive Security Framework
Module G.3: Next-Generation Cybersecurity in Virtual Reality

PATENT PENDING - Proprietary Technology
Copyright © 2025 Enterprise Scanner. All Rights Reserved.

This module contains patent-pending technology for AI-assisted
immersive cybersecurity operations in virtual and augmented reality.

Innovation Claims:
1. AI-driven 3D threat visualization in immersive environments
2. Natural language interaction with cybersecurity data in VR/AR
3. Spatial threat correlation and attack path visualization
4. Multi-user collaborative security operations in shared VR space
5. Real-time threat intelligence streaming in immersive 3D
6. Gesture-based security operations and remediation
7. Military-grade classified data visualization in VR
8. Immersive cyber training with AI mentor (JUPITER)

Author: Enterprise Scanner Development Team
Version: 1.0.0
Patent Status: Provisional Patent Pending
"""

__version__ = "1.0.0"
__module__ = "G.3: JUPITER VR/AR Immersive Security Framework"
__patent_status__ = "PROVISIONAL PATENT PENDING"

# G.3.1: VR/AR Platform Integration
from .platform_integration import (
    VRPlatformManager,
    DeviceProfile,
    SessionManager,
    SpatialCalibration,
    PlatformAdapter,
    VRPlatform,
    DeviceCapability,
    SessionState
)

# G.3.2: JUPITER Avatar System
from .jupiter_avatar import (
    JupiterAvatar,
    AvatarPersonality,
    SpatialPresence,
    VoiceEmitter,
    AnimationController,
    AttentionSystem,
    ProximityManager,
    EmotionalState,
    VoiceCharacteristic,
    AlertPriority,
    InteractionMode
)

__all__ = [
    # G.3.1: VR/AR Platform Integration
    'VRPlatformManager',
    'DeviceProfile',
    'SessionManager',
    'SpatialCalibration',
    'PlatformAdapter',
    'VRPlatform',
    'DeviceCapability',
    'SessionState',
    
    # G.3.2: JUPITER Avatar System
    'JupiterAvatar',
    'AvatarPersonality',
    'SpatialPresence',
    'VoiceEmitter',
    'AnimationController',
    'AttentionSystem',
    'ProximityManager',
    'EmotionalState',
    'VoiceCharacteristic',
    'AlertPriority',
    'InteractionMode',
]
