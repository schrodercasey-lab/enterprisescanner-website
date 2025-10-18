"""
ARIA (AI Response Interactive Assistant) - Module E.1

Visual AI assistant with professional avatar, voice synthesis, and animated responses.
Named after the Greek/Roman goddess of intelligence and wisdom.

Features:
- Professional AI avatar with multiple expressions
- Text-to-speech voice synthesis
- Animated responses and gestures
- Accessibility features (screen reader support)
- Multi-language foundation
- Emotion-aware responses

Business Impact: +$10K ARPU
- Premium user experience differentiation
- Higher user engagement and satisfaction
- Accessibility compliance (ADA, WCAG 2.1)
- Competitive advantage in enterprise market

Author: Enterprise Scanner Team
Version: 2.0.0 (Phase 1 - Static Avatar)
Date: October 17, 2025
"""

from .aria_avatar import (
    ARIAAvatar,
    AvatarExpression,
    AvatarGesture,
    AvatarConfig
)

from .voice_synthesizer import (
    ARIAVoiceSynthesizer,
    VoiceConfig,
    VoiceGender,
    VoiceEmotion
)

__all__ = [
    'ARIAAvatar',
    'AvatarExpression',
    'AvatarGesture',
    'AvatarConfig',
    'ARIAVoiceSynthesizer',
    'VoiceConfig',
    'VoiceGender',
    'VoiceEmotion'
]
