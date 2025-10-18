"""
Jupiter Communication Platform Integrations
Connect with enterprise messaging and collaboration platforms
Supports Slack, Microsoft Teams, generic webhooks
"""

import sqlite3
import json
import requests
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import hashlib
from abc import ABC, abstractmethod


class CommunicationType(Enum):
    """Supported communication platforms"""
    SLACK = "slack"
    TEAMS = "microsoft_teams"
    WEBHOOK = "generic_webhook"
    DISCORD = "discord"
    MATTERMOST = "mattermost"


class MessagePriority(Enum):
    """Message priority/urgency"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Message:
    """Universal message representation"""
    message_id: str
    title: str
    text: str
    priority: MessagePriority
    timestamp: datetime
    channel: Optional[str] = None
    mentions: List[str] = field(default_factory=list)  # @username or @channel
    attachments: List[Dict] = field(default_factory=list)
    buttons: List[Dict] = field(default_factory=list)  # Interactive buttons
    metadata: Dict = field(default_factory=dict)


class CommunicationIntegrationBase(ABC):
    """Base class for communication integrations"""
    
    def __init__(self, webhook_url: str, verify_ssl: bool = True):
        self.webhook_url = webhook_url
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
    
    @abstractmethod
    def send_message(self, message: Message) -> bool:
        """Send message to communication platform"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to platform"""
        pass


class SlackIntegration(CommunicationIntegrationBase):
    """Slack workspace integration"""
    
    def __init__(
        self,
        webhook_url: str,
        bot_token: Optional[str] = None,
        verify_ssl: bool = True
    ):
        super().__init__(webhook_url, verify_ssl)
        self.bot_token = bot_token
        
        if bot_token:
            self.session.headers.update({
                'Authorization': f'Bearer {bot_token}',
                'Content-Type': 'application/json'
            })
    
    def send_message(self, message: Message) -> bool:
        """Send message to Slack channel"""
        try:
            # Build Slack message with blocks for rich formatting
            slack_payload = self._build_slack_payload(message)
            
            # Send via webhook
            response = self.session.post(
                self.webhook_url,
                json=slack_payload,
                verify=self.verify_ssl
            )
            
            return response.status_code == 200 and response.text == "ok"
            
        except Exception as e:
            print(f"Slack send error: {e}")
            return False
    
    def _build_slack_payload(self, message: Message) -> Dict:
        """Build Slack message payload with blocks"""
        
        # Color coding by priority
        color_map = {
            MessagePriority.URGENT: "#ff0000",
            MessagePriority.HIGH: "#ff9900",
            MessagePriority.NORMAL: "#36a64f",
            MessagePriority.LOW: "#cccccc"
        }
        
        blocks = []
        
        # Header section
        if message.title:
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": message.title,
                    "emoji": True
                }
            })
        
        # Message text section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message.text
            }
        })
        
        # Add metadata fields if present
        if message.metadata:
            fields = []
            for key, value in message.metadata.items():
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{key}:*\n{value}"
                })
            
            if fields:
                blocks.append({
                    "type": "section",
                    "fields": fields
                })
        
        # Add action buttons if present
        if message.buttons:
            actions = []
            for button in message.buttons:
                actions.append({
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": button.get('text', 'Action')
                    },
                    "value": button.get('value', ''),
                    "action_id": button.get('action_id', 'button_click')
                })
            
            blocks.append({
                "type": "actions",
                "elements": actions
            })
        
        # Build final payload
        payload = {
            "blocks": blocks,
            "attachments": [{
                "color": color_map.get(message.priority, "#36a64f"),
                "footer": "Jupiter AI Copilot",
                "ts": int(message.timestamp.timestamp())
            }]
        }
        
        # Add channel if specified
        if message.channel:
            payload["channel"] = message.channel
        
        # Add mentions
        if message.mentions:
            mention_text = " ".join([f"<@{m}>" for m in message.mentions])
            payload["text"] = mention_text
        
        return payload
    
    def send_thread_reply(self, message: Message, thread_ts: str) -> bool:
        """Reply to an existing thread"""
        if not self.bot_token:
            print("Bot token required for thread replies")
            return False
        
        try:
            url = "https://slack.com/api/chat.postMessage"
            
            payload = self._build_slack_payload(message)
            payload["thread_ts"] = thread_ts
            
            response = self.session.post(url, json=payload, verify=self.verify_ssl)
            result = response.json()
            
            return result.get("ok", False)
            
        except Exception as e:
            print(f"Slack thread reply error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Slack webhook"""
        try:
            test_payload = {
                "text": "Jupiter AI Copilot - Connection Test",
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ Connection test successful"
                    }
                }]
            }
            
            response = self.session.post(
                self.webhook_url,
                json=test_payload,
                verify=self.verify_ssl
            )
            
            return response.status_code == 200
        except:
            return False


class TeamsIntegration(CommunicationIntegrationBase):
    """Microsoft Teams integration via webhooks"""
    
    def __init__(self, webhook_url: str, verify_ssl: bool = True):
        super().__init__(webhook_url, verify_ssl)
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def send_message(self, message: Message) -> bool:
        """Send message to Teams channel via webhook"""
        try:
            # Build Teams adaptive card
            teams_payload = self._build_teams_payload(message)
            
            response = self.session.post(
                self.webhook_url,
                json=teams_payload,
                verify=self.verify_ssl
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Teams send error: {e}")
            return False
    
    def _build_teams_payload(self, message: Message) -> Dict:
        """Build Microsoft Teams adaptive card payload"""
        
        # Theme color by priority
        color_map = {
            MessagePriority.URGENT: "FF0000",
            MessagePriority.HIGH: "FF9900",
            MessagePriority.NORMAL: "36A64F",
            MessagePriority.LOW: "CCCCCC"
        }
        
        # Build adaptive card
        card_body = []
        
        # Title
        if message.title:
            card_body.append({
                "type": "TextBlock",
                "text": message.title,
                "size": "Large",
                "weight": "Bolder",
                "wrap": True
            })
        
        # Message text
        card_body.append({
            "type": "TextBlock",
            "text": message.text,
            "wrap": True
        })
        
        # Metadata as fact set
        if message.metadata:
            facts = []
            for key, value in message.metadata.items():
                facts.append({
                    "title": key,
                    "value": str(value)
                })
            
            card_body.append({
                "type": "FactSet",
                "facts": facts
            })
        
        # Action buttons
        actions = []
        if message.buttons:
            for button in message.buttons:
                actions.append({
                    "type": "Action.OpenUrl",
                    "title": button.get('text', 'Action'),
                    "url": button.get('url', '#')
                })
        
        # Build final payload
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": message.title or "Jupiter AI Copilot Notification",
            "themeColor": color_map.get(message.priority, "36A64F"),
            "sections": [{
                "activityTitle": message.title,
                "activitySubtitle": f"Priority: {message.priority.value.upper()}",
                "activityImage": "https://enterprisescanner.com/assets/jupiter-icon.png",
                "facts": [
                    {"name": key, "value": str(value)}
                    for key, value in message.metadata.items()
                ] if message.metadata else [],
                "text": message.text
            }]
        }
        
        if actions:
            payload["potentialAction"] = actions
        
        return payload
    
    def test_connection(self) -> bool:
        """Test Teams webhook"""
        try:
            test_payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "Connection Test",
                "themeColor": "36A64F",
                "sections": [{
                    "text": "✅ Jupiter AI Copilot - Connection test successful"
                }]
            }
            
            response = self.session.post(
                self.webhook_url,
                json=test_payload,
                verify=self.verify_ssl
            )
            
            return response.status_code == 200
        except:
            return False


class WebhookIntegration(CommunicationIntegrationBase):
    """Generic webhook integration for custom endpoints"""
    
    def __init__(
        self,
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True
    ):
        super().__init__(webhook_url, verify_ssl)
        
        if headers:
            self.session.headers.update(headers)
        
        if auth:
            if 'bearer_token' in auth:
                self.session.headers['Authorization'] = f"Bearer {auth['bearer_token']}"
            elif 'api_key' in auth:
                self.session.headers['X-API-Key'] = auth['api_key']
            elif 'username' in auth and 'password' in auth:
                self.session.auth = (auth['username'], auth['password'])
    
    def send_message(self, message: Message) -> bool:
        """Send message to generic webhook endpoint"""
        try:
            # Build generic JSON payload
            payload = {
                'message_id': message.message_id,
                'title': message.title,
                'text': message.text,
                'priority': message.priority.value,
                'timestamp': message.timestamp.isoformat(),
                'channel': message.channel,
                'mentions': message.mentions,
                'metadata': message.metadata,
                'source': 'Jupiter AI Copilot'
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=10
            )
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"Webhook send error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test webhook endpoint"""
        try:
            test_payload = {
                'test': True,
                'message': 'Jupiter AI Copilot - Connection test',
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.session.post(
                self.webhook_url,
                json=test_payload,
                verify=self.verify_ssl,
                timeout=10
            )
            
            return response.status_code in [200, 201, 202]
        except:
            return False


class JupiterCommunicationIntegration:
    """
    Jupiter Communication Integration Manager
    Manages connections to multiple communication platforms
    """
    
    def __init__(self, db_path: str = "jupiter_communication.db"):
        self.db_path = db_path
        self.connections: Dict[str, CommunicationIntegrationBase] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize communication integration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Communication connections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS communication_connections (
                connection_id TEXT PRIMARY KEY,
                connection_name TEXT NOT NULL,
                platform_type TEXT NOT NULL,
                webhook_url TEXT NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                last_tested TEXT,
                test_status TEXT,
                messages_sent INTEGER DEFAULT 0
            )
        """)
        
        # Message log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                connection_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                title TEXT,
                priority TEXT,
                sent_at TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (connection_id) REFERENCES communication_connections(connection_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_connection(
        self,
        connection_name: str,
        platform_type: CommunicationType,
        webhook_url: str,
        **kwargs
    ) -> str:
        """Add communication platform connection"""
        
        connection_id = hashlib.sha256(
            f"{connection_name}{platform_type.value}".encode()
        ).hexdigest()[:16]
        
        # Create integration instance
        if platform_type == CommunicationType.SLACK:
            integration = SlackIntegration(
                webhook_url,
                bot_token=kwargs.get('bot_token')
            )
        elif platform_type == CommunicationType.TEAMS:
            integration = TeamsIntegration(webhook_url)
        elif platform_type == CommunicationType.WEBHOOK:
            integration = WebhookIntegration(
                webhook_url,
                headers=kwargs.get('headers'),
                auth=kwargs.get('auth')
            )
        else:
            raise ValueError(f"Unsupported platform type: {platform_type}")
        
        # Test connection
        test_result = integration.test_connection()
        
        # Store connection
        self.connections[connection_id] = integration
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO communication_connections 
            (connection_id, connection_name, platform_type, webhook_url, 
             is_enabled, last_tested, test_status, messages_sent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            connection_id,
            connection_name,
            platform_type.value,
            webhook_url,
            1,
            datetime.now().isoformat(),
            "success" if test_result else "failed",
            0
        ))
        
        conn.commit()
        conn.close()
        
        return connection_id
    
    def send_message_to_all(self, message: Message) -> Dict[str, bool]:
        """Send message to all enabled connections"""
        results = {}
        
        for connection_id, integration in self.connections.items():
            try:
                success = integration.send_message(message)
                results[connection_id] = success
                
                # Log message
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO message_log 
                    (connection_id, message_id, title, priority, sent_at, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    connection_id,
                    message.message_id,
                    message.title,
                    message.priority.value,
                    datetime.now().isoformat(),
                    "success" if success else "failed",
                    None if success else "Send failed"
                ))
                
                if success:
                    cursor.execute("""
                        UPDATE communication_connections 
                        SET messages_sent = messages_sent + 1
                        WHERE connection_id = ?
                    """, (connection_id,))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                results[connection_id] = False
                print(f"Error sending to {connection_id}: {e}")
        
        return results
    
    def send_message(self, connection_id: str, message: Message) -> bool:
        """Send message to specific connection"""
        
        if connection_id not in self.connections:
            print(f"Connection {connection_id} not found")
            return False
        
        integration = self.connections[connection_id]
        success = integration.send_message(message)
        
        if success:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO message_log 
                (connection_id, message_id, title, priority, sent_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                connection_id,
                message.message_id,
                message.title,
                message.priority.value,
                datetime.now().isoformat(),
                "success"
            ))
            
            cursor.execute("""
                UPDATE communication_connections 
                SET messages_sent = messages_sent + 1
                WHERE connection_id = ?
            """, (connection_id,))
            
            conn.commit()
            conn.close()
        
        return success
    
    def get_statistics(self) -> Dict:
        """Get communication integration statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM communication_connections WHERE is_enabled = 1")
        stats['active_connections'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(messages_sent) FROM communication_connections")
        stats['total_messages_sent'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT platform_type, COUNT(*) FROM communication_connections GROUP BY platform_type")
        stats['by_platform'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT priority, COUNT(*) FROM message_log GROUP BY priority")
        stats['by_priority'] = dict(cursor.fetchall())
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    comm = JupiterCommunicationIntegration()
    
    # Add Slack connection
    slack_id = comm.add_connection(
        connection_name="Security Team Slack",
        platform_type=CommunicationType.SLACK,
        webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    )
    
    # Add Teams connection
    teams_id = comm.add_connection(
        connection_name="Executive Team Teams",
        platform_type=CommunicationType.TEAMS,
        webhook_url="https://outlook.office.com/webhook/YOUR-WEBHOOK-URL"
    )
    
    # Create message
    message = Message(
        message_id="msg_12345",
        title="🚨 Critical Vulnerability Detected",
        text="CVE-2024-1234: SQL injection vulnerability found in production web application. Immediate action required.",
        priority=MessagePriority.URGENT,
        timestamp=datetime.now(),
        metadata={
            "CVE ID": "CVE-2024-1234",
            "CVSS Score": "9.8",
            "Affected Systems": "web-01, web-02",
            "Patch Status": "Available"
        },
        buttons=[
            {"text": "View Details", "url": "https://enterprisescanner.com/vulns/12345"},
            {"text": "Create Ticket", "action_id": "create_ticket"}
        ]
    )
    
    # Send to all platforms
    results = comm.send_message_to_all(message)
    print(f"Message sent: {results}")
    
    # Get statistics
    stats = comm.get_statistics()
    print(f"Communication stats: {stats}")
