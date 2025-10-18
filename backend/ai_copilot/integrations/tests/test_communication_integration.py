"""
Tests for Communication Integration Module
Tests Slack, Microsoft Teams, and Email integrations

Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime
import aiohttp
import smtplib

from ai_copilot.integrations.communication_integration import (
    CommunicationPlatform,
    MessagePriority,
    MessageFormat,
    Message,
    MessageResponse,
    CommunicationIntegration,
    SlackIntegration,
    TeamsIntegration,
    EmailIntegration,
    create_communication_integration
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_message():
    """Sample message for testing"""
    return Message(
        title="Critical Vulnerability Detected",
        body="SQL Injection vulnerability found in login endpoint",
        priority=MessagePriority.CRITICAL,
        format=MessageFormat.MARKDOWN,
        channel="#security",
        metadata={
            "CVE": "CVE-2024-1234",
            "CVSS": "9.8",
            "Affected System": "web-app-01.example.com"
        }
    )


@pytest.fixture
def slack_config():
    """Slack configuration for testing"""
    return {
        "token": "xoxb-test-token",
        "default_channel": "#security",
        "username": "Jupiter Bot",
        "icon_emoji": ":shield:"
    }


@pytest.fixture
def teams_config():
    """Teams configuration for testing"""
    return {
        "webhook_url": "https://outlook.office.com/webhook/test-webhook-url"
    }


@pytest.fixture
def email_config():
    """Email configuration for testing"""
    return {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "security@example.com",
        "password": "test-password",
        "from_address": "security@example.com",
        "from_name": "Jupiter Security",
        "use_tls": True
    }


# ============================================================================
# Message Tests
# ============================================================================

class TestMessage:
    """Test Message data class"""
    
    def test_message_creation(self, sample_message):
        """Test creating a message"""
        assert sample_message.title == "Critical Vulnerability Detected"
        assert sample_message.priority == MessagePriority.CRITICAL
        assert sample_message.format == MessageFormat.MARKDOWN
        assert sample_message.channel == "#security"
        assert "CVE" in sample_message.metadata
    
    def test_message_to_dict(self, sample_message):
        """Test message serialization"""
        data = sample_message.to_dict()
        assert data["title"] == sample_message.title
        assert data["priority"] == "critical"
        assert data["format"] == "markdown"
        assert data["metadata"]["CVE"] == "CVE-2024-1234"
    
    def test_message_minimal(self):
        """Test message with minimal fields"""
        msg = Message(
            title="Test",
            body="Test message"
        )
        assert msg.priority == MessagePriority.MEDIUM
        assert msg.format == MessageFormat.MARKDOWN
        assert msg.attachments == []
        assert msg.metadata == {}


class TestMessageResponse:
    """Test MessageResponse data class"""
    
    def test_response_creation(self):
        """Test creating a response"""
        response = MessageResponse(
            success=True,
            platform="slack",
            message_id="1234567890.123456",
            channel="#security"
        )
        assert response.success is True
        assert response.platform == "slack"
        assert response.message_id == "1234567890.123456"
    
    def test_response_to_dict(self):
        """Test response serialization"""
        response = MessageResponse(
            success=False,
            platform="teams",
            error_message="Webhook URL invalid"
        )
        data = response.to_dict()
        assert data["success"] is False
        assert data["error_message"] == "Webhook URL invalid"


# ============================================================================
# Slack Integration Tests
# ============================================================================

class TestSlackIntegration:
    """Test Slack integration"""
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, slack_config):
        """Test Slack connection lifecycle"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        assert integration.session is not None
        
        await integration.disconnect()
        assert integration.session is None
    
    def test_priority_to_color(self, slack_config):
        """Test priority to Slack color mapping"""
        integration = SlackIntegration(slack_config)
        
        assert integration._priority_to_color(MessagePriority.CRITICAL) == "#ff0000"
        assert integration._priority_to_color(MessagePriority.HIGH) == "#ff6600"
        assert integration._priority_to_color(MessagePriority.MEDIUM) == "#ffcc00"
        assert integration._priority_to_color(MessagePriority.LOW) == "#0099ff"
        assert integration._priority_to_color(MessagePriority.INFO) == "#999999"
    
    def test_build_blocks(self, slack_config, sample_message):
        """Test Slack Block Kit building"""
        integration = SlackIntegration(slack_config)
        blocks = integration._build_blocks(sample_message)
        
        assert len(blocks) > 0
        assert blocks[0]["type"] == "header"
        assert blocks[0]["text"]["text"] == sample_message.title
        
        # Check for metadata fields
        has_metadata = any(block["type"] == "section" and "fields" in block for block in blocks)
        assert has_metadata
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, slack_config, sample_message):
        """Test successful Slack message send"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "ok": True,
            "ts": "1234567890.123456",
            "channel": "C123456"
        })
        
        # Patch session.post to return our mock response
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            response = await integration.send_message(sample_message)
        
        await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "slack"
        assert response.message_id == "1234567890.123456"
        assert integration.messages_sent == 1
    
    @pytest.mark.asyncio
    async def test_send_message_failure(self, slack_config, sample_message):
        """Test failed Slack message send"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "ok": False,
            "error": "channel_not_found"
        })
        
        # Patch session.post to return our mock response
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            response = await integration.send_message(sample_message)
        
        await integration.disconnect()
        
        assert response.success is False
        assert response.error_message == "channel_not_found"
        assert integration.messages_failed == 1
    
    @pytest.mark.asyncio
    async def test_send_with_thread(self, slack_config):
        """Test sending Slack message in thread"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        msg = Message(
            title="Thread Reply",
            body="This is a reply",
            thread_id="1234567890.123456"
        )
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "ok": True,
            "ts": "1234567890.123457"
        })
        
        # Patch session.post
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            response = await integration.send_message(msg)
        
        await integration.disconnect()
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_health_check(self, slack_config):
        """Test Slack health check"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        health = integration.health_check()
        
        assert health["platform"] == "slack"
        assert health["connected"] is True
        assert health["status"] == "healthy"
        
        await integration.disconnect()
    
    @pytest.mark.asyncio
    async def test_statistics(self, slack_config, sample_message):
        """Test Slack statistics tracking"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        # Mock successful send
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"ok": True, "ts": "123"})
        
        # Patch session.post
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            await integration.send_message(sample_message)
            await integration.send_message(sample_message)
        
        await integration.disconnect()
        
        stats = integration.get_statistics()
        
        assert stats["messages_sent"] == 2
        assert stats["messages_failed"] == 0
        assert stats["success_rate"] == 100.0


# ============================================================================
# Microsoft Teams Integration Tests
# ============================================================================

class TestTeamsIntegration:
    """Test Microsoft Teams integration"""
    
    def test_priority_to_color(self, teams_config):
        """Test priority to Teams color mapping"""
        integration = TeamsIntegration(teams_config)
        
        assert integration._priority_to_color(MessagePriority.CRITICAL) == "FF0000"
        assert integration._priority_to_color(MessagePriority.HIGH) == "FF6600"
        assert integration._priority_to_color(MessagePriority.MEDIUM) == "FFCC00"
        assert integration._priority_to_color(MessagePriority.LOW) == "0099FF"
    
    def test_build_adaptive_card(self, teams_config, sample_message):
        """Test Teams Adaptive Card building"""
        integration = TeamsIntegration(teams_config)
        card = integration._build_adaptive_card(sample_message)
        
        assert card["type"] == "message"
        assert "attachments" in card
        assert len(card["attachments"]) > 0
        
        content = card["attachments"][0]["content"]
        assert content["type"] == "AdaptiveCard"
        assert len(content["body"]) > 0
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, teams_config, sample_message):
        """Test successful Teams message send"""
        integration = TeamsIntegration(teams_config)
        await integration.connect()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        
        # Patch session.post
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            response = await integration.send_message(sample_message)
        
        await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "teams"
        assert integration.messages_sent == 1
    
    @pytest.mark.asyncio
    async def test_send_message_failure(self, teams_config, sample_message):
        """Test failed Teams message send"""
        integration = TeamsIntegration(teams_config)
        await integration.connect()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Invalid webhook")
        
        # Patch session.post
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            response = await integration.send_message(sample_message)
        
        await integration.disconnect()
        
        assert response.success is False
        assert "HTTP 400" in response.error_message
        assert integration.messages_failed == 1


# ============================================================================
# Email Integration Tests
# ============================================================================

class TestEmailIntegration:
    """Test Email integration"""
    
    def test_priority_to_importance(self, email_config):
        """Test priority to email importance mapping"""
        integration = EmailIntegration(email_config)
        
        assert integration._priority_to_importance(MessagePriority.CRITICAL) == "high"
        assert integration._priority_to_importance(MessagePriority.HIGH) == "high"
        assert integration._priority_to_importance(MessagePriority.MEDIUM) == "normal"
        assert integration._priority_to_importance(MessagePriority.LOW) == "low"
    
    def test_build_html_body(self, email_config, sample_message):
        """Test HTML email body building"""
        integration = EmailIntegration(email_config)
        html = integration._build_html_body(sample_message)
        
        assert sample_message.title in html
        assert sample_message.body in html
        assert "Priority: CRITICAL" in html
        assert "#ff0000" in html  # Critical color
    
    def test_build_metadata_html(self, email_config):
        """Test metadata HTML building"""
        integration = EmailIntegration(email_config)
        metadata = {
            "CVE": "CVE-2024-1234",
            "CVSS": "9.8"
        }
        html = integration._build_metadata_html(metadata)
        
        assert "CVE" in html
        assert "CVE-2024-1234" in html
        assert "CVSS" in html
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, email_config):
        """Test successful email send"""
        integration = EmailIntegration(email_config)
        
        msg = Message(
            title="Test Alert",
            body="Test message body",
            channel="admin@example.com"
        )
        
        # Mock SMTP
        with patch.object(integration, '_send_smtp') as mock_smtp:
            mock_smtp.return_value = None
            
            integration.session = AsyncMock()  # Fake session for context
            
            response = await integration.send_message(msg)
            
            assert response.success is True
            assert response.platform == "email"
            assert response.channel == "admin@example.com"
            assert integration.messages_sent == 1
    
    @pytest.mark.asyncio
    async def test_send_message_failure(self, email_config):
        """Test failed email send"""
        integration = EmailIntegration(email_config)
        
        msg = Message(
            title="Test Alert",
            body="Test message",
            channel="invalid@example.com"
        )
        
        # Mock SMTP to raise exception
        with patch.object(integration, '_send_smtp') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("Connection refused")
            
            integration.session = AsyncMock()
            
            response = await integration.send_message(msg)
            
            assert response.success is False
            assert "Connection refused" in response.error_message
            assert integration.messages_failed == 1


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestCreateCommunicationIntegration:
    """Test factory function"""
    
    def test_create_slack(self, slack_config):
        """Test creating Slack integration"""
        integration = create_communication_integration("slack", slack_config)
        assert isinstance(integration, SlackIntegration)
    
    def test_create_teams(self, teams_config):
        """Test creating Teams integration"""
        integration = create_communication_integration("teams", teams_config)
        assert isinstance(integration, TeamsIntegration)
    
    def test_create_email(self, email_config):
        """Test creating Email integration"""
        integration = create_communication_integration("email", email_config)
        assert isinstance(integration, EmailIntegration)
    
    def test_create_case_insensitive(self, slack_config):
        """Test factory is case-insensitive"""
        integration1 = create_communication_integration("SLACK", slack_config)
        integration2 = create_communication_integration("Slack", slack_config)
        integration3 = create_communication_integration("slack", slack_config)
        
        assert isinstance(integration1, SlackIntegration)
        assert isinstance(integration2, SlackIntegration)
        assert isinstance(integration3, SlackIntegration)
    
    def test_create_invalid_platform(self, slack_config):
        """Test factory with invalid platform"""
        with pytest.raises(ValueError) as exc_info:
            create_communication_integration("invalid", slack_config)
        
        assert "Unsupported communication platform" in str(exc_info.value)


# ============================================================================
# Context Manager Tests
# ============================================================================

class TestContextManager:
    """Test async context manager"""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, slack_config, sample_message):
        """Test using integration as context manager"""
        async with SlackIntegration(slack_config) as integration:
            assert integration.session is not None
            
            # Mock successful send
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={"ok": True, "ts": "123"})
            
            # Patch session.post
            with patch.object(integration.session, 'post') as mock_post:
                mock_post.return_value.__aenter__.return_value = mock_response
                mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
                
                response = await integration.send_message(sample_message)
                assert response.success is True


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_connection_error(self, slack_config, sample_message):
        """Test handling connection errors"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        # Mock session to raise connection error
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.side_effect = aiohttp.ClientConnectionError("Connection failed")
            
            response = await integration.send_message(sample_message)
        
        await integration.disconnect()
        
        assert response.success is False
        assert "Connection failed" in response.error_message
        assert integration.messages_failed == 1
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, teams_config, sample_message):
        """Test handling timeout errors"""
        integration = TeamsIntegration(teams_config)
        
        # Mock session to raise timeout
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(side_effect=asyncio.TimeoutError())
        
        integration.session = mock_session
        
        response = await integration.send_message(sample_message)
        
        assert response.success is False
        assert integration.messages_failed == 1


# ============================================================================
# Batch Sending Tests
# ============================================================================

class TestBatchSending:
    """Test batch message sending"""
    
    @pytest.mark.asyncio
    async def test_send_batch(self, slack_config):
        """Test sending multiple messages"""
        integration = SlackIntegration(slack_config)
        await integration.connect()
        
        messages = [
            Message(title=f"Alert {i}", body=f"Message {i}")
            for i in range(3)
        ]
        
        # Mock successful sends
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"ok": True, "ts": "123"})
        
        # Patch session.post
        with patch.object(integration.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            mock_post.return_value.__aexit__.return_value = AsyncMock(return_value=None)
            
            responses = await integration.send_batch(messages)
        
        await integration.disconnect()
        
        assert len(responses) == 3
        assert all(r.success for r in responses)
        assert integration.messages_sent == 3
