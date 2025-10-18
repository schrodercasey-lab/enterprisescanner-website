"""
Jupiter Team Chat
Real-time chat with AI Copilot integration for collaborative security analysis
"""

import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Set
from enum import Enum
import hashlib


class MessageType(Enum):
    """Chat message types"""
    TEXT = "text"
    QUERY_SHARE = "query_share"  # Shared Jupiter query
    VULNERABILITY_ALERT = "vulnerability_alert"
    CODE_SNIPPET = "code_snippet"
    FILE_ATTACHMENT = "file_attachment"
    SYSTEM_NOTIFICATION = "system_notification"
    JUPITER_RESPONSE = "jupiter_response"  # AI Copilot response
    THREAD_REPLY = "thread_reply"


class ChannelType(Enum):
    """Chat channel types"""
    PUBLIC = "public"  # All team members
    PRIVATE = "private"  # Invite-only
    DIRECT_MESSAGE = "direct_message"  # 1-on-1
    INCIDENT_RESPONSE = "incident_response"  # Active incident
    PROJECT = "project"  # Project-specific
    JUPITER_AI = "jupiter_ai"  # Direct chat with Jupiter


@dataclass
class ChatMessage:
    """Chat message structure"""
    message_id: str
    channel_id: str
    sender_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    thread_id: Optional[str] = None  # For threaded conversations
    mentions: List[str] = field(default_factory=list)  # @mentions
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji: [user_ids]
    attachments: List[Dict] = field(default_factory=list)
    jupiter_query: Optional[Dict] = None  # Embedded Jupiter query
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_pinned: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'channel_id': self.channel_id,
            'sender_id': self.sender_id,
            'message_type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'thread_id': self.thread_id,
            'mentions': self.mentions,
            'reactions': self.reactions,
            'attachments': self.attachments,
            'jupiter_query': self.jupiter_query,
            'is_edited': self.is_edited,
            'is_pinned': self.is_pinned
        }


@dataclass
class ChatChannel:
    """Chat channel structure"""
    channel_id: str
    name: str
    channel_type: ChannelType
    description: str
    created_by: str
    created_at: datetime
    members: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    is_archived: bool = False
    topic: str = ""
    message_count: int = 0
    last_activity: Optional[datetime] = None
    settings: Dict = field(default_factory=dict)


class JupiterTeamChat:
    """
    Team chat system with Jupiter AI Copilot integration
    Enables real-time collaboration with AI assistance
    """
    
    def __init__(self, db_path: str = "jupiter_team_chat.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize chat database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Channels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                channel_type TEXT NOT NULL,
                description TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                members TEXT,
                admins TEXT,
                is_archived INTEGER DEFAULT 0,
                topic TEXT,
                message_count INTEGER DEFAULT 0,
                last_activity TEXT,
                settings TEXT
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id TEXT PRIMARY KEY,
                channel_id TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                thread_id TEXT,
                mentions TEXT,
                reactions TEXT,
                attachments TEXT,
                jupiter_query TEXT,
                is_edited INTEGER DEFAULT 0,
                edited_at TEXT,
                is_pinned INTEGER DEFAULT 0,
                FOREIGN KEY (channel_id) REFERENCES chat_channels(channel_id)
            )
        """)
        
        # User presence tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_presence (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                current_channel TEXT,
                custom_status TEXT
            )
        """)
        
        # Read receipts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_read_receipts (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                last_read_message_id TEXT NOT NULL,
                last_read_at TEXT NOT NULL
            )
        """)
        
        # Jupiter query sharing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jupiter_shared_queries (
                share_id TEXT PRIMARY KEY,
                query_id TEXT NOT NULL,
                shared_by TEXT NOT NULL,
                shared_in_channel TEXT NOT NULL,
                shared_at TEXT NOT NULL,
                query_text TEXT NOT NULL,
                query_results TEXT,
                annotations TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_channel(
        self,
        name: str,
        channel_type: ChannelType,
        created_by: str,
        description: str = "",
        members: List[str] = None
    ) -> ChatChannel:
        """Create new chat channel"""
        
        channel_id = hashlib.sha256(
            f"{name}{created_by}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        channel = ChatChannel(
            channel_id=channel_id,
            name=name,
            channel_type=channel_type,
            description=description,
            created_by=created_by,
            created_at=datetime.now(),
            members=members or [created_by],
            admins=[created_by]
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_channels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            channel.channel_id,
            channel.name,
            channel.channel_type.value,
            channel.description,
            channel.created_by,
            channel.created_at.isoformat(),
            json.dumps(channel.members),
            json.dumps(channel.admins),
            channel.is_archived,
            channel.topic,
            channel.message_count,
            None,
            json.dumps(channel.settings)
        ))
        
        conn.commit()
        conn.close()
        
        return channel
    
    def send_message(
        self,
        channel_id: str,
        sender_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        thread_id: str = None,
        mentions: List[str] = None,
        jupiter_query: Dict = None,
        attachments: List[Dict] = None
    ) -> ChatMessage:
        """Send message to channel"""
        
        message_id = hashlib.sha256(
            f"{channel_id}{sender_id}{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        message = ChatMessage(
            message_id=message_id,
            channel_id=channel_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            thread_id=thread_id,
            mentions=mentions or [],
            jupiter_query=jupiter_query,
            attachments=attachments or []
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message.message_id,
            message.channel_id,
            message.sender_id,
            message.message_type.value,
            message.content,
            message.timestamp.isoformat(),
            message.thread_id,
            json.dumps(message.mentions),
            json.dumps(message.reactions),
            json.dumps(message.attachments),
            json.dumps(message.jupiter_query) if message.jupiter_query else None,
            message.is_edited,
            None,
            message.is_pinned
        ))
        
        # Update channel stats
        cursor.execute("""
            UPDATE chat_channels 
            SET message_count = message_count + 1, last_activity = ?
            WHERE channel_id = ?
        """, (message.timestamp.isoformat(), channel_id))
        
        conn.commit()
        conn.close()
        
        # Send notifications for mentions
        if mentions:
            self._send_mention_notifications(message)
        
        return message
    
    def _send_mention_notifications(self, message: ChatMessage):
        """Send notifications for @mentions"""
        # This would integrate with notification system
        # For now, just log the mentions
        for user_id in message.mentions:
            print(f"Notification: {user_id} was mentioned in {message.channel_id}")
    
    def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50,
        before_timestamp: datetime = None,
        thread_id: str = None
    ) -> List[ChatMessage]:
        """Get messages from channel"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if thread_id:
            # Get thread messages
            cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE channel_id = ? AND thread_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (channel_id, thread_id, limit))
        elif before_timestamp:
            cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE channel_id = ? AND timestamp < ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (channel_id, before_timestamp.isoformat(), limit))
        else:
            cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE channel_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (channel_id, limit))
        
        rows = cursor.fetchall()
        messages = []
        
        for row in rows:
            message = ChatMessage(
                message_id=row[0],
                channel_id=row[1],
                sender_id=row[2],
                message_type=MessageType(row[3]),
                content=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                thread_id=row[6],
                mentions=json.loads(row[7]),
                reactions=json.loads(row[8]),
                attachments=json.loads(row[9]),
                jupiter_query=json.loads(row[10]) if row[10] else None,
                is_edited=bool(row[11]),
                edited_at=datetime.fromisoformat(row[12]) if row[12] else None,
                is_pinned=bool(row[13])
            )
            messages.append(message)
        
        conn.close()
        return messages
    
    def share_jupiter_query(
        self,
        channel_id: str,
        sender_id: str,
        query_text: str,
        query_results: str,
        annotations: str = ""
    ) -> str:
        """Share Jupiter query in chat"""
        
        share_id = hashlib.sha256(
            f"{query_text}{sender_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        query_id = hashlib.sha256(query_text.encode()).hexdigest()[:12]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jupiter_shared_queries VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            share_id,
            query_id,
            sender_id,
            channel_id,
            datetime.now().isoformat(),
            query_text,
            query_results,
            annotations
        ))
        
        conn.commit()
        conn.close()
        
        # Send as message
        jupiter_query = {
            'query_id': query_id,
            'query_text': query_text,
            'results_preview': query_results[:500] + "..." if len(query_results) > 500 else query_results,
            'share_id': share_id
        }
        
        self.send_message(
            channel_id=channel_id,
            sender_id=sender_id,
            content=f"Shared Jupiter query: {query_text[:100]}...",
            message_type=MessageType.QUERY_SHARE,
            jupiter_query=jupiter_query
        )
        
        return share_id
    
    def add_reaction(self, message_id: str, user_id: str, emoji: str) -> bool:
        """Add emoji reaction to message"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT reactions FROM chat_messages WHERE message_id = ?", (message_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        reactions = json.loads(row[0])
        
        if emoji not in reactions:
            reactions[emoji] = []
        
        if user_id not in reactions[emoji]:
            reactions[emoji].append(user_id)
        
        cursor.execute("""
            UPDATE chat_messages SET reactions = ? WHERE message_id = ?
        """, (json.dumps(reactions), message_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def pin_message(self, message_id: str, channel_id: str) -> bool:
        """Pin important message to channel"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE chat_messages SET is_pinned = 1 
            WHERE message_id = ? AND channel_id = ?
        """, (message_id, channel_id))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def get_pinned_messages(self, channel_id: str) -> List[ChatMessage]:
        """Get pinned messages from channel"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_messages 
            WHERE channel_id = ? AND is_pinned = 1
            ORDER BY timestamp DESC
        """, (channel_id,))
        
        rows = cursor.fetchall()
        messages = []
        
        for row in rows:
            message = ChatMessage(
                message_id=row[0],
                channel_id=row[1],
                sender_id=row[2],
                message_type=MessageType(row[3]),
                content=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                thread_id=row[6],
                mentions=json.loads(row[7]),
                reactions=json.loads(row[8]),
                attachments=json.loads(row[9]),
                jupiter_query=json.loads(row[10]) if row[10] else None,
                is_edited=bool(row[11]),
                edited_at=datetime.fromisoformat(row[12]) if row[12] else None,
                is_pinned=bool(row[13])
            )
            messages.append(message)
        
        conn.close()
        return messages
    
    def update_presence(
        self,
        user_id: str,
        status: str = "online",
        current_channel: str = None,
        custom_status: str = ""
    ):
        """Update user presence status"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO chat_presence VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            status,
            datetime.now().isoformat(),
            current_channel,
            custom_status
        ))
        
        conn.commit()
        conn.close()
    
    def get_online_users(self, channel_id: str = None) -> List[Dict]:
        """Get currently online users"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if channel_id:
            # Get users in specific channel
            cursor.execute("""
                SELECT p.* FROM chat_presence p
                JOIN chat_channels c ON p.current_channel = c.channel_id
                WHERE c.channel_id = ? AND p.status = 'online'
            """, (channel_id,))
        else:
            cursor.execute("""
                SELECT * FROM chat_presence WHERE status = 'online'
            """)
        
        rows = cursor.fetchall()
        users = [
            {
                'user_id': row[0],
                'status': row[1],
                'last_seen': row[2],
                'current_channel': row[3],
                'custom_status': row[4]
            }
            for row in rows
        ]
        
        conn.close()
        return users
    
    def mark_as_read(self, user_id: str, channel_id: str, message_id: str):
        """Mark messages as read"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO chat_read_receipts 
            (user_id, channel_id, last_read_message_id, last_read_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, channel_id, message_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_unread_count(self, user_id: str, channel_id: str) -> int:
        """Get unread message count"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last read message timestamp
        cursor.execute("""
            SELECT m.timestamp FROM chat_read_receipts r
            JOIN chat_messages m ON r.last_read_message_id = m.message_id
            WHERE r.user_id = ? AND r.channel_id = ?
        """, (user_id, channel_id))
        
        row = cursor.fetchone()
        
        if row:
            last_read_timestamp = row[0]
            cursor.execute("""
                SELECT COUNT(*) FROM chat_messages
                WHERE channel_id = ? AND timestamp > ?
            """, (channel_id, last_read_timestamp))
            
            count = cursor.fetchone()[0]
        else:
            # Never read, count all messages
            cursor.execute("""
                SELECT COUNT(*) FROM chat_messages WHERE channel_id = ?
            """, (channel_id,))
            
            count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def search_messages(
        self,
        query: str,
        channel_id: str = None,
        sender_id: str = None,
        limit: int = 20
    ) -> List[ChatMessage]:
        """Search messages"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM chat_messages WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if channel_id:
            sql += " AND channel_id = ?"
            params.append(channel_id)
        
        if sender_id:
            sql += " AND sender_id = ?"
            params.append(sender_id)
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            message = ChatMessage(
                message_id=row[0],
                channel_id=row[1],
                sender_id=row[2],
                message_type=MessageType(row[3]),
                content=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                thread_id=row[6],
                mentions=json.loads(row[7]),
                reactions=json.loads(row[8]),
                attachments=json.loads(row[9]),
                jupiter_query=json.loads(row[10]) if row[10] else None,
                is_edited=bool(row[11]),
                edited_at=datetime.fromisoformat(row[12]) if row[12] else None,
                is_pinned=bool(row[13])
            )
            messages.append(message)
        
        conn.close()
        return messages
    
    def get_channel_statistics(self, channel_id: str) -> Dict:
        """Get channel activity statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total messages
        cursor.execute("""
            SELECT COUNT(*) FROM chat_messages WHERE channel_id = ?
        """, (channel_id,))
        stats['total_messages'] = cursor.fetchone()[0]
        
        # Active users
        cursor.execute("""
            SELECT COUNT(DISTINCT sender_id) FROM chat_messages WHERE channel_id = ?
        """, (channel_id,))
        stats['active_users'] = cursor.fetchone()[0]
        
        # Messages by type
        cursor.execute("""
            SELECT message_type, COUNT(*) FROM chat_messages 
            WHERE channel_id = ? GROUP BY message_type
        """, (channel_id,))
        stats['by_type'] = dict(cursor.fetchall())
        
        # Shared queries count
        cursor.execute("""
            SELECT COUNT(*) FROM jupiter_shared_queries WHERE shared_in_channel = ?
        """, (channel_id,))
        stats['shared_queries'] = cursor.fetchone()[0]
        
        # Most active time (hour of day)
        cursor.execute("""
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM chat_messages
            WHERE channel_id = ?
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        """, (channel_id,))
        row = cursor.fetchone()
        stats['peak_hour'] = int(row[0]) if row else None
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    chat = JupiterTeamChat()
    
    # Create security team channel
    channel = chat.create_channel(
        name="Security Team",
        channel_type=ChannelType.PUBLIC,
        created_by="analyst_001",
        description="Main security team collaboration channel"
    )
    
    print(f"Created channel: {channel.name} ({channel.channel_id})")
    
    # Send message
    msg = chat.send_message(
        channel_id=channel.channel_id,
        sender_id="analyst_001",
        content="Found critical SQL injection vulnerability in user login endpoint"
    )
    
    print(f"Sent message: {msg.message_id}")
    
    # Share Jupiter query
    share_id = chat.share_jupiter_query(
        channel_id=channel.channel_id,
        sender_id="analyst_001",
        query_text="Analyze SQL injection vulnerability in /api/login",
        query_results="Vulnerability confirmed: Unsanitized user input...",
        annotations="Requires immediate remediation"
    )
    
    print(f"Shared query: {share_id}")
    
    # Get messages
    messages = chat.get_channel_messages(channel.channel_id)
    print(f"\nChannel has {len(messages)} messages")
