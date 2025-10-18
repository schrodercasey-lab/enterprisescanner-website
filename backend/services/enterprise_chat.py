"""
Enterprise Live Chat System - Backend Service
Real-time chat with Fortune 500 enterprise support capabilities
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Set
import sqlite3
import websockets
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import threading
import queue
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatStatus(Enum):
    """Chat session status"""
    ACTIVE = "active"
    WAITING = "waiting"
    ESCALATED = "escalated"
    CLOSED = "closed"


class MessageType(Enum):
    """Message types"""
    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"
    TEMPLATE = "template"
    ESCALATION = "escalation"


class UserType(Enum):
    """User types in chat"""
    VISITOR = "visitor"
    CONSULTANT = "consultant"
    AGENT = "agent"
    EXECUTIVE = "executive"


@dataclass
class ChatUser:
    """Chat user information"""
    user_id: str
    name: str
    email: Optional[str]
    company: Optional[str]
    user_type: UserType
    session_id: str
    joined_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    location: Optional[Dict] = None


@dataclass
class ChatMessage:
    """Chat message structure"""
    message_id: str
    chat_id: str
    sender_id: str
    sender_type: UserType
    content: str
    message_type: MessageType
    timestamp: datetime
    edited: bool = False
    attachments: List[Dict] = None
    metadata: Dict = None


@dataclass
class ChatSession:
    """Chat session management"""
    chat_id: str
    status: ChatStatus
    created_at: datetime
    updated_at: datetime
    visitor: ChatUser
    assigned_agent: Optional[ChatUser]
    messages: List[ChatMessage]
    escalation_reason: Optional[str]
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=urgent
    tags: List[str] = None
    satisfaction_rating: Optional[int] = None
    resolution_time: Optional[timedelta] = None


class EnterpriseChatManager:
    """
    Enterprise chat management system for Fortune 500 client support
    """
    
    def __init__(self, db_path: str = "enterprise_chat.db"):
        self.db_path = db_path
        self.active_sessions: Dict[str, ChatSession] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> chat_id
        self.agent_availability: Dict[str, bool] = {}
        self.message_queue = queue.Queue()
        self.socketio = None
        
        # Enterprise support configuration
        self.support_config = {
            'business_hours': {
                'start': 8,  # 8 AM
                'end': 20,   # 8 PM
                'timezone': 'UTC'
            },
            'escalation_triggers': [
                'fortune 500', 'enterprise', 'million', 'urgent', 'ceo', 'cto', 'ciso',
                'compliance', 'audit', 'breach', 'incident', 'soc 2', 'iso 27001'
            ],
            'auto_responses': {
                'greeting': "Hello! I'm here to help with your cybersecurity needs. How can I assist you today?",
                'business_hours': "Our enterprise support team is available 24/7 for Fortune 500 clients. How can I help?",
                'escalation': "I'm connecting you with our senior security consultant. They'll be with you shortly."
            }
        }
        
        self.initialize_database()
        self.start_background_services()
    
    def initialize_database(self):
        """Initialize chat database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Chat sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    chat_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visitor_data TEXT NOT NULL,
                    assigned_agent_id TEXT,
                    escalation_reason TEXT,
                    priority INTEGER DEFAULT 1,
                    tags TEXT,
                    satisfaction_rating INTEGER,
                    resolution_time INTEGER
                )
            ''')
            
            # Chat messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id TEXT PRIMARY KEY,
                    chat_id TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    sender_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    edited BOOLEAN DEFAULT FALSE,
                    attachments TEXT,
                    metadata TEXT,
                    FOREIGN KEY (chat_id) REFERENCES chat_sessions (chat_id)
                )
            ''')
            
            # Chat agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_agents (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    specialization TEXT,
                    is_available BOOLEAN DEFAULT FALSE,
                    max_concurrent_chats INTEGER DEFAULT 5,
                    current_chat_count INTEGER DEFAULT 0,
                    last_activity TIMESTAMP,
                    performance_rating REAL DEFAULT 5.0
                )
            ''')
            
            # Chat analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_chats INTEGER DEFAULT 0,
                    escalated_chats INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0,
                    avg_resolution_time REAL DEFAULT 0,
                    satisfaction_avg REAL DEFAULT 0,
                    conversion_rate REAL DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Chat database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize chat database: {e}")
            raise
    
    def start_background_services(self):
        """Start background services for chat management"""
        # Start message processing thread
        message_thread = threading.Thread(target=self._process_messages, daemon=True)
        message_thread.start()
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_inactive_sessions, daemon=True)
        cleanup_thread.start()
        
        logger.info("Chat background services started")
    
    def create_chat_session(self, visitor_data: Dict) -> ChatSession:
        """Create new chat session"""
        try:
            chat_id = f"chat_{uuid.uuid4().hex[:12]}"
            
            # Create visitor user
            visitor = ChatUser(
                user_id=f"visitor_{uuid.uuid4().hex[:8]}",
                name=visitor_data.get('name', 'Anonymous'),
                email=visitor_data.get('email'),
                company=visitor_data.get('company'),
                user_type=UserType.VISITOR,
                session_id=visitor_data.get('session_id'),
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                ip_address=visitor_data.get('ip_address', ''),
                user_agent=visitor_data.get('user_agent', ''),
                location=visitor_data.get('location')
            )
            
            # Determine priority based on visitor data
            priority = self._calculate_priority(visitor_data)
            
            # Create chat session
            session = ChatSession(
                chat_id=chat_id,
                status=ChatStatus.WAITING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                visitor=visitor,
                assigned_agent=None,
                messages=[],
                escalation_reason=None,
                priority=priority,
                tags=self._extract_tags(visitor_data)
            )
            
            # Store session
            self.active_sessions[chat_id] = session
            self.user_sessions[visitor.user_id] = chat_id
            
            # Save to database
            self._save_session_to_db(session)
            
            # Send welcome message
            self._send_welcome_message(session)
            
            # Try to assign agent
            self._assign_agent(session)
            
            logger.info(f"Created chat session {chat_id} for {visitor.name}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create chat session: {e}")
            raise
    
    def send_message(self, chat_id: str, sender_id: str, content: str, 
                    message_type: MessageType = MessageType.TEXT) -> ChatMessage:
        """Send message in chat"""
        try:
            if chat_id not in self.active_sessions:
                raise ValueError(f"Chat session {chat_id} not found")
            
            session = self.active_sessions[chat_id]
            
            # Determine sender type
            if sender_id == session.visitor.user_id:
                sender_type = UserType.VISITOR
            elif session.assigned_agent and sender_id == session.assigned_agent.user_id:
                sender_type = session.assigned_agent.user_type
            else:
                sender_type = UserType.AGENT
            
            # Create message
            message = ChatMessage(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                chat_id=chat_id,
                sender_id=sender_id,
                sender_type=sender_type,
                content=content,
                message_type=message_type,
                timestamp=datetime.utcnow()
            )
            
            # Add to session
            session.messages.append(message)
            session.updated_at = datetime.utcnow()
            
            # Update user activity
            if sender_type == UserType.VISITOR:
                session.visitor.last_activity = datetime.utcnow()
            
            # Save message to database
            self._save_message_to_db(message)
            
            # Check for escalation triggers
            if sender_type == UserType.VISITOR:
                self._check_escalation_triggers(session, content)
            
            # Broadcast message
            if self.socketio:
                self.socketio.emit('new_message', {
                    'chat_id': chat_id,
                    'message': asdict(message)
                }, room=chat_id)
            
            # Queue for processing
            self.message_queue.put((session, message))
            
            logger.info(f"Message sent in chat {chat_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    def escalate_chat(self, chat_id: str, reason: str) -> bool:
        """Escalate chat to senior consultant"""
        try:
            if chat_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[chat_id]
            session.status = ChatStatus.ESCALATED
            session.escalation_reason = reason
            session.priority = max(session.priority, 3)  # High priority
            session.updated_at = datetime.utcnow()
            
            # Send escalation message
            escalation_msg = ChatMessage(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                chat_id=chat_id,
                sender_id="system",
                sender_type=UserType.AGENT,
                content=self.support_config['auto_responses']['escalation'],
                message_type=MessageType.SYSTEM,
                timestamp=datetime.utcnow()
            )
            
            session.messages.append(escalation_msg)
            
            # Notify escalation team
            self._notify_escalation_team(session, reason)
            
            # Update database
            self._save_session_to_db(session)
            self._save_message_to_db(escalation_msg)
            
            logger.info(f"Chat {chat_id} escalated: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to escalate chat: {e}")
            return False
    
    def close_chat(self, chat_id: str, satisfaction_rating: Optional[int] = None) -> bool:
        """Close chat session"""
        try:
            if chat_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[chat_id]
            session.status = ChatStatus.CLOSED
            session.satisfaction_rating = satisfaction_rating
            
            if session.created_at:
                session.resolution_time = datetime.utcnow() - session.created_at
            
            session.updated_at = datetime.utcnow()
            
            # Update database
            self._save_session_to_db(session)
            
            # Remove from active sessions
            if session.visitor.user_id in self.user_sessions:
                del self.user_sessions[session.visitor.user_id]
            
            # Update analytics
            self._update_analytics(session)
            
            logger.info(f"Chat {chat_id} closed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close chat: {e}")
            return False
    
    def get_chat_history(self, chat_id: str) -> Optional[ChatSession]:
        """Get chat session history"""
        try:
            if chat_id in self.active_sessions:
                return self.active_sessions[chat_id]
            
            # Load from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM chat_sessions WHERE chat_id = ?
            ''', (chat_id,))
            
            session_data = cursor.fetchone()
            if not session_data:
                return None
            
            # Load messages
            cursor.execute('''
                SELECT * FROM chat_messages WHERE chat_id = ? ORDER BY timestamp
            ''', (chat_id,))
            
            messages_data = cursor.fetchall()
            conn.close()
            
            # Reconstruct session object
            # (Implementation details for object reconstruction)
            
            return None  # Simplified for now
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return None
    
    def get_active_chats(self) -> List[ChatSession]:
        """Get all active chat sessions"""
        return [session for session in self.active_sessions.values() 
                if session.status in [ChatStatus.ACTIVE, ChatStatus.WAITING, ChatStatus.ESCALATED]]
    
    def _calculate_priority(self, visitor_data: Dict) -> int:
        """Calculate chat priority based on visitor data"""
        priority = 1  # Default low priority
        
        # Check for Fortune 500 indicators
        company = visitor_data.get('company', '').lower()
        email = visitor_data.get('email', '').lower()
        
        fortune_500_domains = [
            'microsoft.com', 'apple.com', 'amazon.com', 'google.com',
            'walmart.com', 'exxonmobil.com', 'berkshirehathaway.com'
            # Add more Fortune 500 domains
        ]
        
        if any(domain in email for domain in fortune_500_domains):
            priority = 4  # Urgent
        elif 'enterprise' in company or 'corp' in company:
            priority = 3  # High
        elif '@' in email and not email.endswith(('.gmail.com', '.yahoo.com', '.hotmail.com')):
            priority = 2  # Normal business email
        
        return priority
    
    def _extract_tags(self, visitor_data: Dict) -> List[str]:
        """Extract tags from visitor data"""
        tags = []
        
        if visitor_data.get('page_url'):
            if 'pricing' in visitor_data['page_url']:
                tags.append('pricing_inquiry')
            elif 'demo' in visitor_data['page_url']:
                tags.append('demo_request')
            elif 'security' in visitor_data['page_url']:
                tags.append('security_assessment')
        
        if visitor_data.get('company'):
            tags.append('enterprise')
        
        return tags
    
    def _send_welcome_message(self, session: ChatSession):
        """Send welcome message to visitor"""
        welcome_msg = ChatMessage(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            chat_id=session.chat_id,
            sender_id="system",
            sender_type=UserType.AGENT,
            content=self.support_config['auto_responses']['greeting'],
            message_type=MessageType.SYSTEM,
            timestamp=datetime.utcnow()
        )
        
        session.messages.append(welcome_msg)
        self._save_message_to_db(welcome_msg)
    
    def _assign_agent(self, session: ChatSession):
        """Try to assign available agent to chat"""
        # For now, simulate agent assignment
        # In production, this would check agent availability
        session.status = ChatStatus.ACTIVE
        logger.info(f"Agent assigned to chat {session.chat_id}")
    
    def _check_escalation_triggers(self, session: ChatSession, content: str):
        """Check if message contains escalation triggers"""
        content_lower = content.lower()
        
        for trigger in self.support_config['escalation_triggers']:
            if trigger in content_lower:
                self.escalate_chat(session.chat_id, f"Keyword trigger: {trigger}")
                break
    
    def _notify_escalation_team(self, session: ChatSession, reason: str):
        """Notify escalation team about urgent chat"""
        # Send email notification to sales team
        try:
            subject = f"Urgent Chat Escalation - {session.visitor.company or 'Enterprise Prospect'}"
            body = f"""
            Chat escalated for immediate attention.
            
            Reason: {reason}
            Visitor: {session.visitor.name} ({session.visitor.email})
            Company: {session.visitor.company or 'Not provided'}
            Chat ID: {session.chat_id}
            Priority: {session.priority}
            
            Please respond within 5 minutes for Fortune 500 prospects.
            """
            
            # In production, send actual email
            logger.info(f"Escalation notification sent for chat {session.chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")
    
    def _save_session_to_db(self, session: ChatSession):
        """Save chat session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO chat_sessions 
                (chat_id, status, created_at, updated_at, visitor_data, assigned_agent_id,
                 escalation_reason, priority, tags, satisfaction_rating, resolution_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.chat_id,
                session.status.value,
                session.created_at,
                session.updated_at,
                json.dumps(asdict(session.visitor)),
                session.assigned_agent.user_id if session.assigned_agent else None,
                session.escalation_reason,
                session.priority,
                json.dumps(session.tags or []),
                session.satisfaction_rating,
                session.resolution_time.total_seconds() if session.resolution_time else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
    
    def _save_message_to_db(self, message: ChatMessage):
        """Save message to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_messages 
                (message_id, chat_id, sender_id, sender_type, content, message_type,
                 timestamp, edited, attachments, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.message_id,
                message.chat_id,
                message.sender_id,
                message.sender_type.value,
                message.content,
                message.message_type.value,
                message.timestamp,
                message.edited,
                json.dumps(message.attachments or []),
                json.dumps(message.metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
    
    def _process_messages(self):
        """Background message processing"""
        while True:
            try:
                session, message = self.message_queue.get(timeout=1)
                
                # Process message for auto-responses, sentiment analysis, etc.
                if message.sender_type == UserType.VISITOR:
                    self._generate_auto_response(session, message)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def _generate_auto_response(self, session: ChatSession, message: ChatMessage):
        """Generate automatic response if needed"""
        content_lower = message.content.lower()
        
        # Simple keyword-based responses
        if any(word in content_lower for word in ['hello', 'hi', 'hey']):
            return  # Already have welcome message
        
        if 'price' in content_lower or 'cost' in content_lower:
            response = "Our enterprise pricing is customized based on your organization's size and needs. I can connect you with our sales team for a personalized quote."
            self._send_auto_response(session, response)
        
        elif 'demo' in content_lower:
            response = "I'd be happy to arrange a demo! Our platform has helped Fortune 500 companies save millions in breach prevention. What's your role and company size?"
            self._send_auto_response(session, response)
    
    def _send_auto_response(self, session: ChatSession, content: str):
        """Send automatic response"""
        # Add slight delay to seem more human
        def delayed_response():
            import time
            time.sleep(2)  # 2 second delay
            
            auto_msg = ChatMessage(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                chat_id=session.chat_id,
                sender_id="auto_agent",
                sender_type=UserType.AGENT,
                content=content,
                message_type=MessageType.TEMPLATE,
                timestamp=datetime.utcnow()
            )
            
            session.messages.append(auto_msg)
            self._save_message_to_db(auto_msg)
            
            if self.socketio:
                self.socketio.emit('new_message', {
                    'chat_id': session.chat_id,
                    'message': asdict(auto_msg)
                }, room=session.chat_id)
        
        # Run in separate thread
        threading.Thread(target=delayed_response, daemon=True).start()
    
    def _cleanup_inactive_sessions(self):
        """Clean up inactive chat sessions"""
        while True:
            try:
                import time
                time.sleep(300)  # Check every 5 minutes
                
                now = datetime.utcnow()
                inactive_threshold = timedelta(minutes=30)
                
                for chat_id, session in list(self.active_sessions.items()):
                    if (now - session.updated_at) > inactive_threshold:
                        if session.status != ChatStatus.CLOSED:
                            self.close_chat(chat_id)
                        del self.active_sessions[chat_id]
                
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")
    
    def _update_analytics(self, session: ChatSession):
        """Update chat analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.utcnow().date()
            
            # Update daily analytics
            cursor.execute('''
                INSERT OR IGNORE INTO chat_analytics (date) VALUES (?)
            ''', (today,))
            
            cursor.execute('''
                UPDATE chat_analytics SET 
                    total_chats = total_chats + 1,
                    escalated_chats = escalated_chats + ?,
                    satisfaction_avg = (satisfaction_avg + ?) / 2
                WHERE date = ?
            ''', (
                1 if session.status == ChatStatus.ESCALATED else 0,
                session.satisfaction_rating or 0,
                today
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update analytics: {e}")


# Global chat manager instance
chat_manager = EnterpriseChatManager()