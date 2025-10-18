"""
Jupiter AI Copilot - Team Collaboration Module
Enables multi-user deployments with shared knowledge and team features
"""

from .team_knowledge_base import (
    JupiterKnowledgeBase,
    KnowledgeArticle,
    ArticleCategory,
    ArticleStatus,
    ArticleMetadata
)

from .team_chat import (
    JupiterTeamChat,
    ChatMessage,
    ChatChannel,
    MessageType,
    ChannelType
)

from .collaboration_manager import (
    JupiterCollaborationManager,
    TeamMember,
    UserRole,
    SharedQuery,
    Annotation,
    CollaborationSession
)

__all__ = [
    'JupiterKnowledgeBase',
    'KnowledgeArticle',
    'ArticleCategory',
    'ArticleStatus',
    'ArticleMetadata',
    'JupiterTeamChat',
    'ChatMessage',
    'ChatChannel',
    'MessageType',
    'ChannelType',
    'JupiterCollaborationManager',
    'TeamMember',
    'UserRole',
    'SharedQuery',
    'Annotation',
    'CollaborationSession'
]
