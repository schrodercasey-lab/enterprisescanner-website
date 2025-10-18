"""
Module 3: Context Manager - Conversation State Management

Manages conversation history and context:
- Message history per user/session
- Intent detection from user messages
- Active context tracking (scans, threats, assets)
- Context injection for LLM prompts
- Memory management and summarization

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict


class MessageRole(Enum):
    """Message roles in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class UserIntent(Enum):
    """Detected user intents"""
    EXPLAIN_VULNERABILITY = "explain_vulnerability"
    HOW_TO_FIX = "how_to_fix"
    THREAT_SEVERITY = "threat_severity"
    COMPLIANCE_CHECK = "compliance_check"
    GENERATE_REPORT = "generate_report"
    CODE_GENERATION = "code_generation"
    SYSTEM_STATUS = "system_status"
    COMPARE_SCANS = "compare_scans"
    GENERAL_QUESTION = "general_question"


@dataclass
class Message:
    """Single message in conversation"""
    message_id: str
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadata
    tokens: int = 0
    intent: Optional[UserIntent] = None
    entities: Dict[str, List[str]] = field(default_factory=dict)  # Extracted entities
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Complete conversation context for a user session"""
    user_id: str
    session_id: str
    messages: List[Message] = field(default_factory=list)
    
    # Active context
    active_scan: Optional[str] = None
    active_threats: List[str] = field(default_factory=list)
    active_assets: List[str] = field(default_factory=list)
    active_vulnerabilities: List[str] = field(default_factory=list)
    
    # Intent tracking
    current_intent: Optional[UserIntent] = None
    intent_history: List[UserIntent] = field(default_factory=list)
    
    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    total_messages: int = 0
    
    # User preferences
    preferred_format: str = "markdown"
    language: str = "en"
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """
    Conversation Context Manager
    
    Maintains conversation state, tracks intent, manages memory
    """
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        UserIntent.EXPLAIN_VULNERABILITY: [
            'explain', 'what is', 'tell me about', 'describe',
            'cve-', 'vulnerability', 'weakness'
        ],
        UserIntent.HOW_TO_FIX: [
            'how to fix', 'remediate', 'patch', 'resolve',
            'how do i', 'steps to', 'fix this'
        ],
        UserIntent.THREAT_SEVERITY: [
            'how bad', 'severity', 'critical', 'dangerous',
            'risk level', 'priority', 'how serious'
        ],
        UserIntent.COMPLIANCE_CHECK: [
            'compliance', 'regulation', 'standard', 'pci', 'hipaa',
            'gdpr', 'iso', 'nist', 'compliant'
        ],
        UserIntent.GENERATE_REPORT: [
            'report', 'summary', 'export', 'generate report',
            'create report', 'executive summary'
        ],
        UserIntent.CODE_GENERATION: [
            'generate code', 'script', 'automate', 'create script',
            'write code', 'generate script'
        ],
        UserIntent.SYSTEM_STATUS: [
            'status', 'health', 'metrics', 'dashboard',
            'how is', 'check status'
        ],
        UserIntent.COMPARE_SCANS: [
            'compare', 'difference', 'vs', 'versus',
            'compare to', 'last scan', 'previous scan'
        ]
    }
    
    def __init__(
        self,
        max_messages_per_session: int = 100,
        session_timeout_hours: int = 24,
        storage_backend: str = "memory"
    ):
        """
        Initialize Context Manager
        
        Args:
            max_messages_per_session: Max messages to keep in memory
            session_timeout_hours: Hours before session expires
            storage_backend: 'memory' or 'database'
        """
        self.logger = logging.getLogger(__name__)
        self.max_messages = max_messages_per_session
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.storage_backend = storage_backend
        
        # In-memory storage: {(user_id, session_id): ConversationContext}
        self.contexts: Dict[tuple, ConversationContext] = {}
        
        # Statistics
        self.stats = {
            'active_sessions': 0,
            'total_messages': 0,
            'intents_detected': defaultdict(int),
            'expired_sessions': 0
        }
        
        self.logger.info("ContextManager initialized")
    
    def get_context(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[ConversationContext]:
        """
        Get conversation context for user/session
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            ConversationContext or None if not found
        """
        key = (user_id, session_id)
        
        # Check if exists
        if key not in self.contexts:
            return None
        
        context = self.contexts[key]
        
        # Check if expired
        if datetime.now() - context.last_activity > self.session_timeout:
            self.logger.info(f"Session expired: {session_id}")
            del self.contexts[key]
            self.stats['expired_sessions'] += 1
            self.stats['active_sessions'] -= 1
            return None
        
        return context
    
    def create_context(
        self,
        user_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """
        Create new conversation context
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            metadata: Optional metadata
            
        Returns:
            New ConversationContext
        """
        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        key = (user_id, session_id)
        self.contexts[key] = context
        self.stats['active_sessions'] += 1
        
        self.logger.info(f"Context created: user={user_id}, session={session_id}")
        
        return context
    
    def update_context(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        assistant_response: str,
        query_type: Optional[str] = None
    ):
        """
        Update context with new message exchange
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            user_message: User's message
            assistant_response: Assistant's response
            query_type: Detected query type (optional)
        """
        # Get or create context
        key = (user_id, session_id)
        context = self.get_context(user_id, session_id)
        
        if not context:
            context = self.create_context(user_id, session_id)
        
        # Detect intent from user message
        intent = self._detect_intent(user_message)
        
        # Extract entities (CVE IDs, IPs, hostnames, etc.)
        entities = self._extract_entities(user_message)
        
        # Add user message
        user_msg = Message(
            message_id=f"msg_{len(context.messages)+1}",
            role=MessageRole.USER,
            content=user_message,
            intent=intent,
            entities=entities
        )
        context.messages.append(user_msg)
        
        # Add assistant response
        assistant_msg = Message(
            message_id=f"msg_{len(context.messages)+1}",
            role=MessageRole.ASSISTANT,
            content=assistant_response
        )
        context.messages.append(assistant_msg)
        
        # Update context state
        context.last_activity = datetime.now()
        context.total_messages += 2
        context.current_intent = intent
        context.intent_history.append(intent)
        
        # Update active entities
        self._update_active_entities(context, entities)
        
        # Manage memory (trim if too long)
        self._manage_memory(context)
        
        # Update statistics
        self.stats['total_messages'] += 2
        self.stats['intents_detected'][intent.value] += 1
        
        self.logger.debug(
            f"Context updated: {session_id}, intent={intent.value}, "
            f"messages={len(context.messages)}"
        )
    
    def _detect_intent(self, message: str) -> UserIntent:
        """
        Detect user intent from message
        
        Uses pattern matching on keywords
        """
        message_lower = message.lower()
        
        # Check each intent's patterns
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return intent
        
        # Default to general question
        return UserIntent.GENERAL_QUESTION
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        Extract entities from message
        
        Entities: CVE IDs, IP addresses, hostnames, etc.
        """
        entities = defaultdict(list)
        
        # Extract CVE IDs (CVE-YYYY-NNNNN)
        import re
        cve_pattern = r'CVE-\d{4}-\d{4,7}'
        cves = re.findall(cve_pattern, message, re.IGNORECASE)
        if cves:
            entities['cve_ids'] = cves
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, message)
        if ips:
            entities['ip_addresses'] = ips
        
        # Extract hostnames (simple pattern)
        hostname_pattern = r'\b[a-z0-9][-a-z0-9]{0,62}(?:\.[a-z0-9][-a-z0-9]{0,62})+\b'
        hostnames = re.findall(hostname_pattern, message, re.IGNORECASE)
        if hostnames:
            entities['hostnames'] = hostnames
        
        # Extract scan IDs (scan_XXXXX pattern)
        scan_pattern = r'scan[_-]?\d+'
        scans = re.findall(scan_pattern, message, re.IGNORECASE)
        if scans:
            entities['scan_ids'] = scans
        
        return dict(entities)
    
    def _update_active_entities(
        self,
        context: ConversationContext,
        entities: Dict[str, List[str]]
    ):
        """Update active entities in context"""
        # Update active scan
        if 'scan_ids' in entities and entities['scan_ids']:
            context.active_scan = entities['scan_ids'][0]
        
        # Update active threats (CVEs)
        if 'cve_ids' in entities:
            context.active_threats.extend(entities['cve_ids'])
            # Keep only unique, recent ones
            context.active_threats = list(set(context.active_threats))[-10:]
        
        # Update active assets
        if 'hostnames' in entities:
            context.active_assets.extend(entities['hostnames'])
            context.active_assets = list(set(context.active_assets))[-10:]
        
        if 'ip_addresses' in entities:
            context.active_assets.extend(entities['ip_addresses'])
            context.active_assets = list(set(context.active_assets))[-10:]
    
    def _manage_memory(self, context: ConversationContext):
        """
        Manage context memory
        
        Keeps most recent messages, summarizes older ones
        """
        if len(context.messages) <= self.max_messages:
            return
        
        # Keep most recent messages
        recent_messages = context.messages[-self.max_messages:]
        
        # In production, would summarize older messages
        # For now, just truncate
        context.messages = recent_messages
        
        self.logger.debug(f"Context memory managed: {context.session_id}")
    
    def set_active_scan(
        self,
        user_id: str,
        session_id: str,
        scan_id: str
    ):
        """
        Set active scan for context
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            scan_id: Scan identifier to set as active
        """
        context = self.get_context(user_id, session_id)
        if context:
            context.active_scan = scan_id
            context.last_activity = datetime.now()
            self.logger.info(f"Active scan set: {scan_id} for session {session_id}")
    
    def get_relevant_history(
        self,
        user_id: str,
        session_id: str,
        max_messages: int = 10
    ) -> List[Message]:
        """
        Get relevant recent messages
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            max_messages: Maximum messages to return
            
        Returns:
            List of recent Message objects
        """
        context = self.get_context(user_id, session_id)
        if not context:
            return []
        
        # Return most recent messages
        return context.messages[-max_messages:]
    
    def get_conversation_summary(
        self,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get conversation summary
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Summary dict with key information
        """
        context = self.get_context(user_id, session_id)
        if not context:
            return {}
        
        return {
            'session_id': context.session_id,
            'user_id': context.user_id,
            'created_at': context.created_at.isoformat(),
            'last_activity': context.last_activity.isoformat(),
            'total_messages': context.total_messages,
            'current_intent': context.current_intent.value if context.current_intent else None,
            'active_scan': context.active_scan,
            'active_threats_count': len(context.active_threats),
            'active_assets_count': len(context.active_assets),
            'recent_intents': [i.value for i in context.intent_history[-5:]]
        }
    
    def clear_context(
        self,
        user_id: str,
        session_id: str
    ):
        """
        Clear conversation context (new session)
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        key = (user_id, session_id)
        if key in self.contexts:
            del self.contexts[key]
            self.stats['active_sessions'] -= 1
            self.logger.info(f"Context cleared: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.now()
        expired_keys = []
        
        for key, context in self.contexts.items():
            if now - context.last_activity > self.session_timeout:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.contexts[key]
            self.stats['expired_sessions'] += 1
            self.stats['active_sessions'] -= 1
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired sessions")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        return {
            'active_sessions': self.stats['active_sessions'],
            'total_messages': self.stats['total_messages'],
            'intents_detected': dict(self.stats['intents_detected']),
            'expired_sessions': self.stats['expired_sessions'],
            'average_messages_per_session': (
                self.stats['total_messages'] / max(self.stats['active_sessions'], 1)
            )
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("CONTEXT MANAGER - MODULE 3")
    print("="*70)
    
    # Initialize
    print("\n1. Initializing Context Manager...")
    cm = ContextManager()
    
    # Create context
    print("\n2. Creating Conversation Context:")
    user_id = "customer_alice"
    session_id = "session_12345"
    
    context = cm.create_context(user_id, session_id)
    print(f"   Created: {context.session_id}")
    print(f"   User: {context.user_id}")
    
    # Simulate conversation
    print("\n3. Simulating Conversation:")
    
    conversation = [
        ("Explain CVE-2024-12345", "CVE-2024-12345 is a critical SQL injection..."),
        ("How do I fix this vulnerability?", "To fix this, you should: 1) Apply patch..."),
        ("Is server-db-01 affected?", "Yes, server-db-01 is affected by this vulnerability..."),
        ("Generate a remediation report", "Here's the remediation report...")
    ]
    
    for user_msg, assistant_resp in conversation:
        cm.update_context(user_id, session_id, user_msg, assistant_resp)
        print(f"   User: {user_msg[:50]}...")
        print(f"   Intent detected: {cm.get_context(user_id, session_id).current_intent.value}")
    
    # Get context summary
    print("\n4. Conversation Summary:")
    summary = cm.get_conversation_summary(user_id, session_id)
    print(json.dumps(summary, indent=2))
    
    # Get active context
    print("\n5. Active Context:")
    context = cm.get_context(user_id, session_id)
    print(f"   Active Scan: {context.active_scan}")
    print(f"   Active Threats: {context.active_threats}")
    print(f"   Active Assets: {context.active_assets}")
    
    # Get recent history
    print("\n6. Recent Message History:")
    history = cm.get_relevant_history(user_id, session_id, max_messages=4)
    for msg in history:
        role_emoji = "👤" if msg.role == MessageRole.USER else "🤖"
        print(f"   {role_emoji} {msg.role.value}: {msg.content[:60]}...")
    
    # Statistics
    print("\n7. Context Manager Statistics:")
    stats = cm.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("MODULE 3 COMPLETE ✅")
    print("="*70)
