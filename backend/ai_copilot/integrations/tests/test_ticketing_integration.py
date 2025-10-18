"""
Unit Tests for Ticketing Integration Module
Tests Jira and ServiceNow integrations with mock HTTP

Version: 1.0.0
Coverage Target: >90%
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json
import base64

from ..ticketing_integration import (
    TicketingIntegration,
    TicketingPlatform,
    TicketPriority,
    TicketStatus,
    Ticket,
    TicketResponse,
    JiraIntegration,
    ServiceNowIntegration,
    create_ticketing_integration
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_ticket():
    """Create a sample ticket for testing"""
    return Ticket(
        title="Critical SQL Injection Vulnerability",
        description="SQL injection found in user input validation module",
        priority=TicketPriority.CRITICAL,
        ticket_type="bug",
        project_key="SEC",
        assignee="security.team@example.com",
        labels=["security", "vulnerability", "sql-injection"],
        vulnerability_data={
            "cve_id": "CVE-2024-1234",
            "cvss_score": 9.8,
            "affected_asset": "web-server-01.example.com"
        }
    )


@pytest.fixture
def jira_config():
    """Jira configuration for testing"""
    return {
        "url": "https://company.atlassian.net",
        "username": "test@example.com",
        "api_token": "test_token_123",
        "verify_ssl": False
    }


@pytest.fixture
def servicenow_config():
    """ServiceNow configuration for testing"""
    return {
        "instance": "dev12345",
        "username": "admin",
        "password": "test_password",
        "table": "incident",
        "verify_ssl": False
    }


# ============================================================================
# Test Ticket Dataclass
# ============================================================================

class TestTicket:
    """Test Ticket dataclass"""
    
    def test_ticket_creation(self, sample_ticket):
        """Test creating a ticket"""
        assert sample_ticket.title == "Critical SQL Injection Vulnerability"
        assert sample_ticket.priority == TicketPriority.CRITICAL
        assert sample_ticket.project_key == "SEC"
        assert len(sample_ticket.labels) == 3
    
    def test_ticket_to_dict(self, sample_ticket):
        """Test converting ticket to dictionary"""
        ticket_dict = sample_ticket.to_dict()
        
        assert ticket_dict["title"] == "Critical SQL Injection Vulnerability"
        assert ticket_dict["priority"] == "critical"
        assert ticket_dict["type"] == "bug"
        assert "vulnerability_data" in ticket_dict
    
    def test_ticket_minimal(self):
        """Test creating ticket with minimal fields"""
        ticket = Ticket(
            title="Test Ticket",
            description="Test description",
            priority=TicketPriority.LOW
        )
        
        assert ticket.title == "Test Ticket"
        assert ticket.project_key is None
        assert ticket.assignee is None
        assert len(ticket.labels) == 0


# ============================================================================
# Test TicketResponse Dataclass
# ============================================================================

class TestTicketResponse:
    """Test TicketResponse dataclass"""
    
    def test_response_creation(self):
        """Test creating a ticket response"""
        response = TicketResponse(
            success=True,
            platform="jira",
            ticket_id="10001",
            ticket_key="SEC-123",
            url="https://jira.example.com/browse/SEC-123"
        )
        
        assert response.success is True
        assert response.platform == "jira"
        assert response.ticket_key == "SEC-123"
    
    def test_response_to_dict(self):
        """Test converting response to dictionary"""
        response = TicketResponse(
            success=True,
            platform="servicenow",
            ticket_id="abc123",
            ticket_key="INC0001234"
        )
        
        response_dict = response.to_dict()
        assert response_dict["success"] is True
        assert response_dict["platform"] == "servicenow"
        assert response_dict["ticket_key"] == "INC0001234"


# ============================================================================
# Test Jira Integration
# ============================================================================

class TestJiraIntegration:
    """Test Jira REST API integration"""
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, jira_config):
        """Test connection lifecycle"""
        integration = JiraIntegration(jira_config)
        
        await integration.connect()
        assert integration.session is not None
        
        await integration.disconnect()
    
    def test_priority_mapping(self, jira_config):
        """Test Jira priority mapping"""
        integration = JiraIntegration(jira_config)
        
        assert integration._map_priority_to_jira(TicketPriority.CRITICAL) == "Highest"
        assert integration._map_priority_to_jira(TicketPriority.HIGH) == "High"
        assert integration._map_priority_to_jira(TicketPriority.MEDIUM) == "Medium"
        assert integration._map_priority_to_jira(TicketPriority.LOW) == "Low"
        assert integration._map_priority_to_jira(TicketPriority.TRIVIAL) == "Lowest"
    
    def test_cvss_to_priority_mapping(self, jira_config):
        """Test CVSS score to priority mapping"""
        integration = JiraIntegration(jira_config)
        
        assert integration._map_cvss_to_priority(9.8) == TicketPriority.CRITICAL
        assert integration._map_cvss_to_priority(7.5) == TicketPriority.HIGH
        assert integration._map_cvss_to_priority(5.0) == TicketPriority.MEDIUM
        assert integration._map_cvss_to_priority(2.0) == TicketPriority.LOW
        assert integration._map_cvss_to_priority(0.0) == TicketPriority.TRIVIAL
    
    @pytest.mark.asyncio
    async def test_create_ticket_success(self, jira_config, sample_ticket):
        """Test successfully creating Jira ticket"""
        integration = JiraIntegration(jira_config)
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={
            "id": "10001",
            "key": "SEC-123"
        })
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.create_ticket(sample_ticket)
            await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "jira"
        assert response.ticket_key == "SEC-123"
        assert response.url == "https://company.atlassian.net/browse/SEC-123"
        assert integration.tickets_created == 1
    
    @pytest.mark.asyncio
    async def test_create_ticket_failure(self, jira_config, sample_ticket):
        """Test handling Jira ticket creation failure"""
        integration = JiraIntegration(jira_config)
        
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.create_ticket(sample_ticket)
            await integration.disconnect()
        
        assert response.success is False
        assert "400" in response.error_message
        assert integration.tickets_failed == 1
    
    @pytest.mark.asyncio
    async def test_update_ticket(self, jira_config):
        """Test updating Jira ticket"""
        integration = JiraIntegration(jira_config)
        
        mock_response = AsyncMock()
        mock_response.status = 204
        
        with patch('aiohttp.ClientSession.put') as mock_put:
            mock_put.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.update_ticket("SEC-123", {"priority": {"name": "High"}})
            await integration.disconnect()
        
        assert response.success is True
        assert integration.tickets_updated == 1
    
    @pytest.mark.asyncio
    async def test_add_comment(self, jira_config):
        """Test adding comment to Jira ticket"""
        integration = JiraIntegration(jira_config)
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"id": "comment-123"})
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.add_comment("SEC-123", "Vulnerability confirmed")
            await integration.disconnect()
        
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_health_check(self, jira_config):
        """Test Jira health check"""
        integration = JiraIntegration(jira_config)
        await integration.connect()
        
        health = integration.health_check()
        
        assert health["platform"] == "jira"
        assert "connected" in health
        assert "tickets_created" in health
        
        await integration.disconnect()
    
    @pytest.mark.asyncio
    async def test_statistics(self, jira_config, sample_ticket):
        """Test statistics tracking"""
        integration = JiraIntegration(jira_config)
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"id": "10001", "key": "SEC-123"})
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            await integration.create_ticket(sample_ticket)
            await integration.create_ticket(sample_ticket)
            
            stats = integration.get_statistics()
            
            assert stats["tickets_created"] == 2
            assert stats["tickets_failed"] == 0
            assert stats["success_rate"] == 100.0
            
            await integration.disconnect()


# ============================================================================
# Test ServiceNow Integration
# ============================================================================

class TestServiceNowIntegration:
    """Test ServiceNow Table API integration"""
    
    def test_priority_mapping(self, servicenow_config):
        """Test ServiceNow priority mapping"""
        integration = ServiceNowIntegration(servicenow_config)
        
        assert integration._map_priority_to_servicenow(TicketPriority.CRITICAL) == "1"
        assert integration._map_priority_to_servicenow(TicketPriority.HIGH) == "2"
        assert integration._map_priority_to_servicenow(TicketPriority.MEDIUM) == "3"
        assert integration._map_priority_to_servicenow(TicketPriority.LOW) == "4"
        assert integration._map_priority_to_servicenow(TicketPriority.TRIVIAL) == "5"
    
    def test_impact_mapping(self, servicenow_config):
        """Test ServiceNow impact mapping"""
        integration = ServiceNowIntegration(servicenow_config)
        
        assert integration._map_priority_to_impact(TicketPriority.CRITICAL) == "1"
        assert integration._map_priority_to_impact(TicketPriority.HIGH) == "2"
        assert integration._map_priority_to_impact(TicketPriority.MEDIUM) == "2"
        assert integration._map_priority_to_impact(TicketPriority.LOW) == "3"
    
    @pytest.mark.asyncio
    async def test_create_ticket_success(self, servicenow_config, sample_ticket):
        """Test successfully creating ServiceNow incident"""
        integration = ServiceNowIntegration(servicenow_config)
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={
            "result": {
                "sys_id": "abc123",
                "number": "INC0001234"
            }
        })
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.create_ticket(sample_ticket)
            await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "servicenow"
        assert response.ticket_key == "INC0001234"
        assert "sys_id=abc123" in response.url
        assert integration.tickets_created == 1
    
    @pytest.mark.asyncio
    async def test_create_ticket_failure(self, servicenow_config, sample_ticket):
        """Test handling ServiceNow incident creation failure"""
        integration = ServiceNowIntegration(servicenow_config)
        
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.text = AsyncMock(return_value="Forbidden")
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.create_ticket(sample_ticket)
            await integration.disconnect()
        
        assert response.success is False
        assert "403" in response.error_message
        assert integration.tickets_failed == 1
    
    @pytest.mark.asyncio
    async def test_update_ticket(self, servicenow_config):
        """Test updating ServiceNow incident"""
        integration = ServiceNowIntegration(servicenow_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": {}})
        
        with patch('aiohttp.ClientSession.patch') as mock_patch:
            mock_patch.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.update_ticket("abc123", {"priority": "2"})
            await integration.disconnect()
        
        assert response.success is True
        assert integration.tickets_updated == 1
    
    @pytest.mark.asyncio
    async def test_add_comment(self, servicenow_config):
        """Test adding work note to ServiceNow incident"""
        integration = ServiceNowIntegration(servicenow_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": {}})
        
        with patch('aiohttp.ClientSession.patch') as mock_patch:
            mock_patch.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.add_comment("abc123", "Vulnerability confirmed")
            await integration.disconnect()
        
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_transition_status(self, servicenow_config):
        """Test transitioning ServiceNow incident state"""
        integration = ServiceNowIntegration(servicenow_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": {}})
        
        with patch('aiohttp.ClientSession.patch') as mock_patch:
            mock_patch.return_value.__aenter__.return_value = mock_response
            
            await integration.connect()
            response = await integration.transition_status("abc123", TicketStatus.IN_PROGRESS)
            await integration.disconnect()
        
        assert response.success is True


# ============================================================================
# Test Factory Function
# ============================================================================

class TestCreateTicketingIntegration:
    """Test ticketing integration factory"""
    
    def test_create_jira(self, jira_config):
        """Test creating Jira integration"""
        integration = create_ticketing_integration("jira", jira_config)
        assert isinstance(integration, JiraIntegration)
    
    def test_create_servicenow(self, servicenow_config):
        """Test creating ServiceNow integration"""
        integration = create_ticketing_integration("servicenow", servicenow_config)
        assert isinstance(integration, ServiceNowIntegration)
    
    def test_create_case_insensitive(self, jira_config):
        """Test case-insensitive platform names"""
        integration1 = create_ticketing_integration("JIRA", jira_config)
        integration2 = create_ticketing_integration("Jira", jira_config)
        integration3 = create_ticketing_integration("jira", jira_config)
        
        assert all(isinstance(i, JiraIntegration) for i in [integration1, integration2, integration3])
    
    def test_create_invalid_platform(self):
        """Test creating integration with invalid platform"""
        with pytest.raises(ValueError, match="Unsupported ticketing platform"):
            create_ticketing_integration("invalid_platform", {})


# ============================================================================
# Test Context Manager
# ============================================================================

class TestContextManager:
    """Test async context manager functionality"""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, jira_config, sample_ticket):
        """Test using integration as context manager"""
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"id": "10001", "key": "SEC-123"})
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with JiraIntegration(jira_config) as integration:
                response = await integration.create_ticket(sample_ticket)
                assert response.success is True


# ============================================================================
# Test Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_connection_error(self, jira_config, sample_ticket):
        """Test handling connection errors"""
        integration = JiraIntegration(jira_config)
        
        with patch('aiohttp.ClientSession.post', side_effect=Exception("Connection refused")):
            await integration.connect()
            response = await integration.create_ticket(sample_ticket)
            await integration.disconnect()
        
        assert response.success is False
        assert "Connection refused" in response.error_message
        assert integration.tickets_failed == 1
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, servicenow_config, sample_ticket):
        """Test handling timeout errors"""
        integration = ServiceNowIntegration(servicenow_config)
        
        with patch('aiohttp.ClientSession.post', side_effect=asyncio.TimeoutError()):
            await integration.connect()
            response = await integration.create_ticket(sample_ticket)
            await integration.disconnect()
        
        assert response.success is False
        assert integration.tickets_failed == 1


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
