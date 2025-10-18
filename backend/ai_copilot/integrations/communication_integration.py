"""
Jupiter AI Copilot - Communication Integration Module
Integrates with Slack, Microsoft Teams, and Email for real-time notifications

Supports:
- Slack Web API
- Microsoft Teams (Webhooks + Graph API)
- Email (SMTP, SendGrid, AWS SES)

Features:
- Real-time vulnerability alerts
- Rich message formatting (Markdown, cards, HTML)
- Message threading
- Attachment support
- Channel/team routing
- Priority-based notifications

Version: 1.0.0
Author: Jupiter Development Team
"""

import aiohttp
import asyncio
import logging
import json
import smtplib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class CommunicationPlatform(Enum):
    """Supported communication platforms"""
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MessageFormat(Enum):
    """Message formatting types"""
    PLAIN = "plain"
    MARKDOWN = "markdown"
    HTML = "html"
    ADAPTIVE_CARD = "adaptive_card"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Message:
    """
    Represents a communication message
    
    Attributes:
        title: Message title/subject
        body: Message body content
        priority: Message priority level
        format: Message formatting type
        channel: Target channel/team/recipient
        thread_id: Optional thread identifier for replies
        attachments: Optional list of attachment paths
        metadata: Optional metadata dictionary
    """
    title: str
    body: str
    priority: MessagePriority = MessagePriority.MEDIUM
    format: MessageFormat = MessageFormat.MARKDOWN
    channel: Optional[str] = None
    thread_id: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "title": self.title,
            "body": self.body,
            "priority": self.priority.value,
            "format": self.format.value,
            "channel": self.channel,
            "thread_id": self.thread_id,
            "attachments": self.attachments,
            "metadata": self.metadata
        }


@dataclass
class MessageResponse:
    """
    Response from communication operations
    
    Attributes:
        success: Whether operation succeeded
        platform: Platform name (slack, teams, email)
        message_id: Sent message identifier
        channel: Channel/recipient where sent
        timestamp: Operation timestamp
        error_message: Error details if failed
    """
    success: bool
    platform: str
    message_id: Optional[str] = None
    channel: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "success": self.success,
            "platform": self.platform,
            "message_id": self.message_id,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message
        }


# ============================================================================
# Base Communication Integration Class
# ============================================================================

class CommunicationIntegration:
    """
    Base class for communication integrations
    
    Provides common functionality for messaging:
    - Connection management
    - Message sending
    - Threading support
    - Statistics tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize communication integration
        
        Args:
            config: Configuration dictionary with platform-specific settings
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.messages_sent = 0
        self.messages_failed = 0
        self.last_error: Optional[str] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to communication platform"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        logger.info(f"Connected to communication platform")
    
    async def disconnect(self):
        """Close connection to communication platform"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(f"Disconnected from communication platform")
    
    async def send_message(self, message: Message) -> MessageResponse:
        """
        Send a message
        
        Args:
            message: Message object with details
            
        Returns:
            MessageResponse with sent message information
        """
        raise NotImplementedError("Subclasses must implement send_message()")
    
    async def send_batch(self, messages: List[Message]) -> List[MessageResponse]:
        """
        Send multiple messages
        
        Args:
            messages: List of Message objects
            
        Returns:
            List of MessageResponse objects
        """
        responses = []
        for message in messages:
            response = await self.send_message(message)
            responses.append(response)
        return responses
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check integration health
        
        Returns:
            Dictionary with health status
        """
        return {
            "platform": self.__class__.__name__.lower().replace("integration", ""),
            "connected": self.session is not None,
            "messages_sent": self.messages_sent,
            "messages_failed": self.messages_failed,
            "last_error": self.last_error,
            "status": "healthy" if self.session and not self.last_error else "degraded"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get operation statistics
        
        Returns:
            Dictionary with statistics
        """
        total_messages = self.messages_sent + self.messages_failed
        success_rate = 0.0
        if total_messages > 0:
            success_rate = (self.messages_sent / total_messages) * 100
        
        return {
            "platform": self.__class__.__name__.lower().replace("integration", ""),
            "messages_sent": self.messages_sent,
            "messages_failed": self.messages_failed,
            "success_rate": round(success_rate, 2),
            "last_error": self.last_error
        }


# ============================================================================
# Slack Integration
# ============================================================================

class SlackIntegration(CommunicationIntegration):
    """
    Slack Web API Integration
    
    Sends messages to Slack channels using Bot tokens
    
    Configuration:
        token: Slack Bot token (xoxb-...)
        default_channel: Default channel to post to
        username: Optional bot username
        icon_emoji: Optional bot icon emoji
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get("token")
        self.default_channel = config.get("default_channel", "#general")
        self.username = config.get("username", "Jupiter Security Bot")
        self.icon_emoji = config.get("icon_emoji", ":shield:")
        self.api_url = "https://slack.com/api"
    
    def _priority_to_color(self, priority: MessagePriority) -> str:
        """Map priority to Slack attachment color"""
        mapping = {
            MessagePriority.CRITICAL: "#ff0000",  # Red
            MessagePriority.HIGH: "#ff6600",      # Orange
            MessagePriority.MEDIUM: "#ffcc00",    # Yellow
            MessagePriority.LOW: "#0099ff",       # Blue
            MessagePriority.INFO: "#999999"       # Gray
        }
        return mapping.get(priority, "#999999")
    
    def _build_blocks(self, message: Message) -> List[Dict[str, Any]]:
        """Build Slack Block Kit format"""
        blocks = []
        
        # Header block
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": message.title,
                "emoji": True
            }
        })
        
        # Body block
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message.body
            }
        })
        
        # Metadata fields if present
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
        
        # Divider
        blocks.append({"type": "divider"})
        
        return blocks
    
    async def send_message(self, message: Message) -> MessageResponse:
        """
        Send message to Slack
        
        Args:
            message: Message details
            
        Returns:
            MessageResponse with sent message information
        """
        try:
            endpoint = f"{self.api_url}/chat.postMessage"
            
            channel = message.channel or self.default_channel
            
            # Build payload with Block Kit
            payload = {
                "channel": channel,
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "blocks": self._build_blocks(message)
            }
            
            # Add thread_ts if replying to thread
            if message.thread_id:
                payload["thread_ts"] = message.thread_id
            
            # Add color attachment for priority
            payload["attachments"] = [{
                "color": self._priority_to_color(message.priority),
                "footer": f"Priority: {message.priority.value.upper()}",
                "ts": int(datetime.now().timestamp())
            }]
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                endpoint,
                json=payload,
                headers=headers
            ) as response:
                
                data = await response.json()
                
                if data.get("ok"):
                    message_ts = data.get("ts")
                    
                    self.messages_sent += 1
                    logger.info(f"Slack message sent to {channel}")
                    
                    return MessageResponse(
                        success=True,
                        platform="slack",
                        message_id=message_ts,
                        channel=channel
                    )
                else:
                    error_msg = data.get("error", "Unknown error")
                    self.last_error = error_msg
                    self.messages_failed += 1
                    logger.error(f"Slack send failed: {error_msg}")
                    
                    return MessageResponse(
                        success=False,
                        platform="slack",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"Slack send error: {str(e)}"
            self.last_error = error_msg
            self.messages_failed += 1
            logger.error(error_msg)
            
            return MessageResponse(
                success=False,
                platform="slack",
                error_message=error_msg
            )


# ============================================================================
# Microsoft Teams Integration
# ============================================================================

class TeamsIntegration(CommunicationIntegration):
    """
    Microsoft Teams Integration (Webhook-based)
    
    Sends messages to Teams channels using incoming webhooks
    
    Configuration:
        webhook_url: Teams incoming webhook URL
        title_color: Optional default card title color
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.title_color = config.get("title_color", "0078D4")
    
    def _priority_to_color(self, priority: MessagePriority) -> str:
        """Map priority to Teams card color"""
        mapping = {
            MessagePriority.CRITICAL: "FF0000",  # Red
            MessagePriority.HIGH: "FF6600",      # Orange
            MessagePriority.MEDIUM: "FFCC00",    # Yellow
            MessagePriority.LOW: "0099FF",       # Blue
            MessagePriority.INFO: "999999"       # Gray
        }
        return mapping.get(priority, "999999")
    
    def _build_adaptive_card(self, message: Message) -> Dict[str, Any]:
        """Build Teams Adaptive Card format"""
        card = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": []
                }
            }]
        }
        
        body = card["attachments"][0]["content"]["body"]
        
        # Title container
        body.append({
            "type": "Container",
            "style": "emphasis",
            "items": [{
                "type": "TextBlock",
                "text": message.title,
                "size": "Large",
                "weight": "Bolder",
                "color": "Accent"
            }]
        })
        
        # Body text
        body.append({
            "type": "TextBlock",
            "text": message.body,
            "wrap": True,
            "spacing": "Medium"
        })
        
        # Metadata as fact set
        if message.metadata:
            facts = []
            for key, value in message.metadata.items():
                facts.append({
                    "title": key,
                    "value": str(value)
                })
            
            body.append({
                "type": "FactSet",
                "facts": facts,
                "spacing": "Medium"
            })
        
        # Priority indicator
        priority_colors = {
            MessagePriority.CRITICAL: "Attention",
            MessagePriority.HIGH: "Warning",
            MessagePriority.MEDIUM: "Good",
            MessagePriority.LOW: "Accent",
            MessagePriority.INFO: "Default"
        }
        
        body.append({
            "type": "Container",
            "items": [{
                "type": "TextBlock",
                "text": f"**Priority:** {message.priority.value.upper()}",
                "color": priority_colors.get(message.priority, "Default"),
                "spacing": "Small"
            }]
        })
        
        return card
    
    async def send_message(self, message: Message) -> MessageResponse:
        """
        Send message to Microsoft Teams
        
        Args:
            message: Message details
            
        Returns:
            MessageResponse with sent message information
        """
        try:
            # Build Adaptive Card
            payload = self._build_adaptive_card(message)
            
            headers = {
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                self.webhook_url,
                json=payload,
                headers=headers
            ) as response:
                
                if response.status in [200, 202]:
                    self.messages_sent += 1
                    logger.info(f"Teams message sent")
                    
                    return MessageResponse(
                        success=True,
                        platform="teams",
                        message_id=str(datetime.now().timestamp())
                    )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    self.messages_failed += 1
                    logger.error(f"Teams send failed: {error_msg}")
                    
                    return MessageResponse(
                        success=False,
                        platform="teams",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"Teams send error: {str(e)}"
            self.last_error = error_msg
            self.messages_failed += 1
            logger.error(error_msg)
            
            return MessageResponse(
                success=False,
                platform="teams",
                error_message=error_msg
            )


# ============================================================================
# Email Integration
# ============================================================================

class EmailIntegration(CommunicationIntegration):
    """
    Email Integration (SMTP)
    
    Sends emails via SMTP (supports Gmail, Office365, custom SMTP)
    
    Configuration:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port (587 for TLS, 465 for SSL)
        username: SMTP username
        password: SMTP password
        from_address: Sender email address
        from_name: Sender name
        use_tls: Whether to use TLS (default: True)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_host = config.get("smtp_host")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_address = config.get("from_address")
        self.from_name = config.get("from_name", "Jupiter Security")
        self.use_tls = config.get("use_tls", True)
    
    def _priority_to_importance(self, priority: MessagePriority) -> str:
        """Map priority to email importance"""
        if priority in [MessagePriority.CRITICAL, MessagePriority.HIGH]:
            return "high"
        elif priority == MessagePriority.LOW:
            return "low"
        else:
            return "normal"
    
    def _build_html_body(self, message: Message) -> str:
        """Build HTML email body"""
        priority_colors = {
            MessagePriority.CRITICAL: "#ff0000",
            MessagePriority.HIGH: "#ff6600",
            MessagePriority.MEDIUM: "#ffcc00",
            MessagePriority.LOW: "#0099ff",
            MessagePriority.INFO: "#999999"
        }
        
        color = priority_colors.get(message.priority, "#999999")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: {color}; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .metadata {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid {color}; }}
                .metadata-item {{ margin: 5px 0; }}
                .footer {{ padding: 20px; font-size: 12px; color: #666; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{message.title}</h1>
                <p><strong>Priority: {message.priority.value.upper()}</strong></p>
            </div>
            <div class="content">
                <p>{message.body.replace(chr(10), '<br>')}</p>
                
                {self._build_metadata_html(message.metadata) if message.metadata else ''}
            </div>
            <div class="footer">
                <p>Sent by Jupiter Security Platform</p>
                <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Build metadata section HTML"""
        html = '<div class="metadata"><h3>Additional Information</h3>'
        for key, value in metadata.items():
            html += f'<div class="metadata-item"><strong>{key}:</strong> {value}</div>'
        html += '</div>'
        return html
    
    async def send_message(self, message: Message) -> MessageResponse:
        """
        Send email message
        
        Args:
            message: Message details (channel = recipient email)
            
        Returns:
            MessageResponse with sent message information
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.title
            msg['From'] = f"{self.from_name} <{self.from_address}>"
            msg['To'] = message.channel
            msg['X-Priority'] = '1' if message.priority in [MessagePriority.CRITICAL, MessagePriority.HIGH] else '3'
            
            # Plain text version
            text_part = MIMEText(message.body, 'plain')
            msg.attach(text_part)
            
            # HTML version
            html_part = MIMEText(self._build_html_body(message), 'html')
            msg.attach(html_part)
            
            # Run SMTP in thread pool (blocking operation)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_smtp, msg, message.channel)
            
            self.messages_sent += 1
            logger.info(f"Email sent to {message.channel}")
            
            return MessageResponse(
                success=True,
                platform="email",
                channel=message.channel,
                message_id=msg['Message-ID']
            )
        
        except Exception as e:
            error_msg = f"Email send error: {str(e)}"
            self.last_error = error_msg
            self.messages_failed += 1
            logger.error(error_msg)
            
            return MessageResponse(
                success=False,
                platform="email",
                error_message=error_msg
            )
    
    def _send_smtp(self, msg: MIMEMultipart, recipient: str):
        """Send email via SMTP (blocking operation)"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


# ============================================================================
# Factory Function
# ============================================================================

def create_communication_integration(platform: str, config: Dict[str, Any]) -> CommunicationIntegration:
    """
    Factory function to create communication integration
    
    Args:
        platform: Platform name ('slack', 'teams', or 'email')
        config: Platform-specific configuration
        
    Returns:
        CommunicationIntegration instance
        
    Raises:
        ValueError: If platform not supported
    """
    platform = platform.lower()
    
    if platform == "slack":
        return SlackIntegration(config)
    elif platform == "teams":
        return TeamsIntegration(config)
    elif platform == "email":
        return EmailIntegration(config)
    else:
        raise ValueError(f"Unsupported communication platform: {platform}")
