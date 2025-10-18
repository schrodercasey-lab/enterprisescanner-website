"""
Unit Tests for SIEM Integration Module
Tests all SIEM integrations (Splunk, QRadar, Sentinel) with mock HTTP

Version: 1.0.0
Coverage Target: >90%
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json
import base64
import hmac
import hashlib

from ..siem_integration import (
    SIEMIntegration,
    SIEMPlatform,
    EventSeverity,
    SIEMEvent,
    SIEMResponse,
    SplunkIntegration,
    QRadarIntegration,
    SentinelIntegration,
    create_siem_integration
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_event():
    """Create a sample SIEM event for testing"""
    return SIEMEvent(
        event_id="evt_001",
        title="Critical SQL Injection Vulnerability",
        severity=EventSeverity.CRITICAL,
        description="SQL injection found in user input validation",
        timestamp=datetime.now(),
        vulnerability_id="vuln_12345",
        cve_id="CVE-2024-1234",
        cvss_score=9.8,
        affected_asset="web-server-01.example.com",
        remediation_status="pending",
        correlation_id="corr_001",
        metadata={"scanner": "Jupiter", "version": "2.0"}
    )


@pytest.fixture
def splunk_config():
    """Splunk configuration for testing"""
    return {
        "url": "https://splunk.example.com",
        "token": "test_token_123",
        "index": "security",
        "sourcetype": "jupiter:finding",
        "verify_ssl": False
    }


@pytest.fixture
def qradar_config():
    """QRadar configuration for testing"""
    return {
        "url": "https://qradar.example.com",
        "token": "test_qradar_token",
        "log_source": "Jupiter_Security_Platform",
        "verify_ssl": False
    }


@pytest.fixture
def sentinel_config():
    """Sentinel configuration for testing"""
    return {
        "workspace_id": "test-workspace-id",
        "shared_key": base64.b64encode(b"test_shared_key").decode(),
        "log_type": "JupiterSecurityFindings"
    }


# ============================================================================
# Test SIEMEvent Dataclass
# ============================================================================

class TestSIEMEvent:
    """Test SIEMEvent dataclass"""
    
    def test_event_creation(self, sample_event):
        """Test creating a SIEM event"""
        assert sample_event.event_id == "evt_001"
        assert sample_event.title == "Critical SQL Injection Vulnerability"
        assert sample_event.severity == EventSeverity.CRITICAL
        assert sample_event.cvss_score == 9.8
    
    def test_event_to_dict(self, sample_event):
        """Test converting event to dictionary"""
        event_dict = sample_event.to_dict()
        
        assert event_dict["event_id"] == "evt_001"
        assert event_dict["severity"] == "CRITICAL"
        assert event_dict["cvss_score"] == 9.8
        assert "metadata" in event_dict
        assert event_dict["metadata"]["scanner"] == "Jupiter"
    
    def test_event_minimal(self):
        """Test creating event with minimal fields"""
        event = SIEMEvent(
            event_id="evt_002",
            title="Test Event",
            severity=EventSeverity.LOW,
            description="Test description",
            timestamp=datetime.now()
        )
        
        assert event.event_id == "evt_002"
        assert event.vulnerability_id is None
        assert event.cve_id is None


# ============================================================================
# Test SIEMResponse Dataclass
# ============================================================================

class TestSIEMResponse:
    """Test SIEMResponse dataclass"""
    
    def test_response_creation(self):
        """Test creating a SIEM response"""
        response = SIEMResponse(
            success=True,
            platform="splunk",
            event_id="evt_001",
            siem_event_id="ack_123",
            timestamp=datetime.now()
        )
        
        assert response.success is True
        assert response.platform == "splunk"
        assert response.siem_event_id == "ack_123"
    
    def test_response_to_dict(self):
        """Test converting response to dictionary"""
        now = datetime.now()
        response = SIEMResponse(
            success=True,
            platform="qradar",
            event_id="evt_001",
            timestamp=now
        )
        
        response_dict = response.to_dict()
        assert response_dict["success"] is True
        assert response_dict["platform"] == "qradar"
        assert "timestamp" in response_dict


# ============================================================================
# Test Splunk Integration
# ============================================================================

class TestSplunkIntegration:
    """Test Splunk HEC integration"""
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, splunk_config):
        """Test connection lifecycle"""
        integration = SplunkIntegration(splunk_config)
        
        await integration.connect()
        assert integration.session is not None
        
        await integration.disconnect()
        # Session should be closed (can't easily test, but no error is good)
    
    @pytest.mark.asyncio
    async def test_send_event_success(self, splunk_config, sample_event):
        """Test successfully sending event to Splunk"""
        integration = SplunkIntegration(splunk_config)
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ackId": "12345"})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "splunk"
        assert response.siem_event_id == "12345"
        assert integration.events_sent == 1
        assert integration.events_failed == 0
    
    @pytest.mark.asyncio
    async def test_send_event_failure(self, splunk_config, sample_event):
        """Test handling Splunk send failure"""
        integration = SplunkIntegration(splunk_config)
        
        # Mock HTTP error
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is False
        assert "500" in response.error_message
        assert integration.events_sent == 0
        assert integration.events_failed == 1
    
    @pytest.mark.asyncio
    async def test_send_batch(self, splunk_config, sample_event):
        """Test sending batch of events"""
        integration = SplunkIntegration(splunk_config)
        
        events = [sample_event] * 3
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ackId": "12345"})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            responses = await integration.send_batch(events)
            await integration.disconnect()
        
        assert len(responses) == 3
        assert all(r.success for r in responses)
        assert integration.events_sent == 3
    
    @pytest.mark.asyncio
    async def test_health_check(self, splunk_config):
        """Test Splunk health check"""
        integration = SplunkIntegration(splunk_config)
        await integration.connect()
        
        health = integration.health_check()  # Not async
        
        assert health["platform"] == "splunk"
        assert "connected" in health
        assert "events_sent" in health
        
        await integration.disconnect()
    
    @pytest.mark.asyncio
    async def test_statistics(self, splunk_config, sample_event):
        """Test statistics tracking"""
        integration = SplunkIntegration(splunk_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ackId": "12345"})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            await integration.send_event(sample_event)
            await integration.send_event(sample_event)
            
            stats = integration.get_statistics()
            
            assert stats["events_sent"] == 2
            assert stats["events_failed"] == 0
            assert stats["success_rate"] == 100.0
            
            await integration.disconnect()


# ============================================================================
# Test QRadar Integration
# ============================================================================

class TestQRadarIntegration:
    """Test QRadar REST API integration"""
    
    @pytest.mark.asyncio
    async def test_send_event_success(self, qradar_config, sample_event):
        """Test successfully sending event to QRadar"""
        integration = QRadarIntegration(qradar_config)
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"id": "offense_123"})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "qradar"
        assert response.siem_event_id == "offense_123"
        assert integration.events_sent == 1
    
    def test_severity_mapping(self, qradar_config):
        """Test QRadar severity mapping"""
        integration = QRadarIntegration(qradar_config)
        
        assert integration._map_severity_to_qradar(EventSeverity.CRITICAL) == 10
        assert integration._map_severity_to_qradar(EventSeverity.HIGH) == 8
        assert integration._map_severity_to_qradar(EventSeverity.MEDIUM) == 5
        assert integration._map_severity_to_qradar(EventSeverity.LOW) == 3
        assert integration._map_severity_to_qradar(EventSeverity.INFO) == 1
    
    @pytest.mark.asyncio
    async def test_send_event_failure(self, qradar_config, sample_event):
        """Test handling QRadar send failure"""
        integration = QRadarIntegration(qradar_config)
        
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.text = AsyncMock(return_value="Forbidden")
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is False
        assert "403" in response.error_message
        assert integration.events_failed == 1


# ============================================================================
# Test Sentinel Integration
# ============================================================================

class TestSentinelIntegration:
    """Test Azure Sentinel integration"""
    
    @pytest.mark.asyncio
    async def test_send_event_success(self, sentinel_config, sample_event):
        """Test successfully sending event to Sentinel"""
        integration = SentinelIntegration(sentinel_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is True
        assert response.platform == "sentinel"
        assert integration.events_sent == 1
    
    def test_severity_mapping(self, sentinel_config):
        """Test Sentinel severity mapping"""
        integration = SentinelIntegration(sentinel_config)
        
        assert integration._map_severity_to_sentinel(EventSeverity.CRITICAL) == "Critical"
        assert integration._map_severity_to_sentinel(EventSeverity.HIGH) == "High"
        assert integration._map_severity_to_sentinel(EventSeverity.MEDIUM) == "Medium"
        assert integration._map_severity_to_sentinel(EventSeverity.LOW) == "Low"
        assert integration._map_severity_to_sentinel(EventSeverity.INFO) == "Informational"
    
    def test_build_signature(self, sentinel_config):
        """Test HMAC-SHA256 signature generation"""
        integration = SentinelIntegration(sentinel_config)
        
        date = "Mon, 01 Jan 2024 00:00:00 GMT"
        content_length = 100
        
        signature = integration._build_signature(date, content_length)
        
        # Should be a base64 encoded string
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Verify it's valid base64
        try:
            base64.b64decode(signature)
        except Exception:
            pytest.fail("Signature is not valid base64")
    
    @pytest.mark.asyncio
    async def test_send_event_with_auth(self, sentinel_config, sample_event):
        """Test Sentinel authentication headers"""
        integration = SentinelIntegration(sentinel_config)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")
        
        # Capture the actual POST call
        with patch('aiohttp.ClientSession.post', return_value=mock_response) as mock_post:
            await integration.connect()
            await integration.send_event(sample_event)
            await integration.disconnect()
            
            # Verify auth headers were set
            call_kwargs = mock_post.call_args[1]
            headers = call_kwargs['headers']
            
            assert 'Authorization' in headers
            assert headers['Authorization'].startswith('SharedKey')
            assert 'x-ms-date' in headers
            assert 'Log-Type' in headers
    
    @pytest.mark.asyncio
    async def test_send_event_failure(self, sentinel_config, sample_event):
        """Test handling Sentinel send failure"""
        integration = SentinelIntegration(sentinel_config)
        
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is False
        assert "401" in response.error_message
        assert integration.events_failed == 1


# ============================================================================
# Test Factory Function
# ============================================================================

class TestCreateSIEMIntegration:
    """Test SIEM integration factory"""
    
    def test_create_splunk(self, splunk_config):
        """Test creating Splunk integration"""
        integration = create_siem_integration("splunk", splunk_config)
        assert isinstance(integration, SplunkIntegration)
    
    def test_create_qradar(self, qradar_config):
        """Test creating QRadar integration"""
        integration = create_siem_integration("qradar", qradar_config)
        assert isinstance(integration, QRadarIntegration)
    
    def test_create_sentinel(self, sentinel_config):
        """Test creating Sentinel integration"""
        integration = create_siem_integration("sentinel", sentinel_config)
        assert isinstance(integration, SentinelIntegration)
    
    def test_create_case_insensitive(self, splunk_config):
        """Test case-insensitive platform names"""
        integration1 = create_siem_integration("SPLUNK", splunk_config)
        integration2 = create_siem_integration("Splunk", splunk_config)
        integration3 = create_siem_integration("splunk", splunk_config)
        
        assert all(isinstance(i, SplunkIntegration) for i in [integration1, integration2, integration3])
    
    def test_create_invalid_platform(self):
        """Test creating integration with invalid platform"""
        with pytest.raises(ValueError, match="Unsupported SIEM platform"):
            create_siem_integration("invalid_platform", {})


# ============================================================================
# Test Context Manager
# ============================================================================

class TestContextManager:
    """Test async context manager functionality"""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, splunk_config, sample_event):
        """Test using integration as context manager"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ackId": "12345"})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with SplunkIntegration(splunk_config) as integration:
                response = await integration.send_event(sample_event)
                assert response.success is True
        
        # Session should be automatically closed after context exit


# ============================================================================
# Test Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_connection_error(self, splunk_config, sample_event):
        """Test handling connection errors"""
        integration = SplunkIntegration(splunk_config)
        
        # Mock connection error
        with patch('aiohttp.ClientSession.post', side_effect=Exception("Connection refused")):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is False
        assert "Connection refused" in response.error_message
        assert integration.events_failed == 1
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, splunk_config, sample_event):
        """Test handling timeout errors"""
        integration = SplunkIntegration(splunk_config)
        
        # Mock timeout
        with patch('aiohttp.ClientSession.post', side_effect=asyncio.TimeoutError()):
            await integration.connect()
            response = await integration.send_event(sample_event)
            await integration.disconnect()
        
        assert response.success is False
        assert integration.events_failed == 1


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
