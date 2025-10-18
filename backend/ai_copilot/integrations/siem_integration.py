"""
Jupiter v3.0 - SIEM Integration Module
Enterprise SIEM platform integrations for security event forwarding

Supported Platforms:
- Splunk (HTTP Event Collector)
- IBM QRadar (REST API)
- Microsoft Sentinel (Azure Monitor)

Author: Jupiter Engineering Team
Created: October 18, 2025
Version: 1.0.0
"""

import asyncio
import aiohttp
import hashlib
import hmac
import base64
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import time

# Configure logging
logger = logging.getLogger(__name__)


class SIEMPlatform(Enum):
    """Supported SIEM platforms"""
    SPLUNK = "splunk"
    QRADAR = "qradar"
    SENTINEL = "sentinel"


class EventSeverity(Enum):
    """Event severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SIEMEvent:
    """Security event for SIEM forwarding"""
    event_id: str
    title: str
    severity: EventSeverity
    description: str
    timestamp: datetime
    
    # Optional fields
    vulnerability_id: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    affected_asset: Optional[str] = None
    remediation_status: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API transmission"""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "vulnerability_id": self.vulnerability_id,
            "cve_id": self.cve_id,
            "cvss_score": self.cvss_score,
            "affected_asset": self.affected_asset,
            "remediation_status": self.remediation_status,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }


@dataclass
class SIEMResponse:
    """Response from SIEM platform"""
    success: bool
    platform: str
    event_id: str
    siem_event_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_after: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "platform": self.platform,
            "event_id": self.event_id,
            "siem_event_id": self.siem_event_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "error_message": self.error_message,
            "retry_after": self.retry_after
        }


class SIEMIntegration:
    """Base class for SIEM integrations"""
    
    def __init__(self, platform: SIEMPlatform, config: dict):
        """
        Initialize SIEM integration
        
        Args:
            platform: SIEM platform type
            config: Platform-specific configuration
        """
        self.platform = platform
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Statistics
        self.events_sent = 0
        self.events_failed = 0
        self.last_error: Optional[str] = None
        
        logger.info(f"SIEM Integration initialized: {platform.value}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to SIEM platform"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info(f"Connected to {self.platform.value}")
    
    async def disconnect(self):
        """Close connection to SIEM platform"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(f"Disconnected from {self.platform.value}")
    
    async def send_event(self, event: SIEMEvent) -> SIEMResponse:
        """
        Send single event to SIEM
        
        Args:
            event: Security event to send
            
        Returns:
            SIEMResponse with send status
        """
        raise NotImplementedError("Subclass must implement send_event()")
    
    async def send_batch(self, events: List[SIEMEvent]) -> List[SIEMResponse]:
        """
        Send multiple events in batch
        
        Args:
            events: List of security events
            
        Returns:
            List of SIEMResponse objects
        """
        responses = []
        for event in events:
            response = await self.send_event(event)
            responses.append(response)
        return responses
    
    def health_check(self) -> dict:
        """
        Check SIEM platform health
        
        Returns:
            Health status dictionary
        """
        return {
            "platform": self.platform.value,
            "connected": self.session is not None,
            "events_sent": self.events_sent,
            "events_failed": self.events_failed,
            "last_error": self.last_error,
            "status": "healthy" if self.last_error is None else "degraded"
        }
    
    def get_statistics(self) -> dict:
        """Get integration statistics"""
        total = self.events_sent + self.events_failed
        success_rate = (self.events_sent / total * 100) if total > 0 else 0
        
        return {
            "platform": self.platform.value,
            "events_sent": self.events_sent,
            "events_failed": self.events_failed,
            "success_rate": round(success_rate, 2),
            "last_error": self.last_error
        }


class SplunkIntegration(SIEMIntegration):
    """Splunk HTTP Event Collector (HEC) integration"""
    
    def __init__(self, config: dict):
        """
        Initialize Splunk integration
        
        Config requires:
            - url: Splunk HEC endpoint (e.g., https://splunk:8088)
            - token: HEC authentication token
            - index: Target index name
            - sourcetype: Event sourcetype (default: jupiter:finding)
            - verify_ssl: SSL verification (default: True)
        """
        super().__init__(SIEMPlatform.SPLUNK, config)
        
        self.url = config.get("url")
        self.token = config.get("token")
        self.index = config.get("index", "security")
        self.sourcetype = config.get("sourcetype", "jupiter:finding")
        self.verify_ssl = config.get("verify_ssl", True)
        
        if not self.url or not self.token:
            raise ValueError("Splunk config requires 'url' and 'token'")
        
        # Build HEC endpoint
        self.hec_endpoint = f"{self.url}/services/collector/event"
        
        logger.info(f"Splunk HEC configured: {self.url}")
    
    async def send_event(self, event: SIEMEvent) -> SIEMResponse:
        """Send event to Splunk HEC"""
        try:
            # Ensure connection
            if self.session is None:
                await self.connect()
            
            # Build HEC payload
            payload = {
                "time": int(event.timestamp.timestamp()),
                "sourcetype": self.sourcetype,
                "source": "jupiter",
                "index": self.index,
                "event": event.to_dict()
            }
            
            # Send to HEC
            headers = {
                "Authorization": f"Splunk {self.token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                self.hec_endpoint,
                json=payload,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.events_sent += 1
                    
                    logger.info(f"Event sent to Splunk: {event.event_id}")
                    
                    return SIEMResponse(
                        success=True,
                        platform=self.platform.value,
                        event_id=event.event_id,
                        siem_event_id=result.get("ackId"),
                        timestamp=datetime.now()
                    )
                else:
                    error_text = await response.text()
                    self.events_failed += 1
                    self.last_error = f"HTTP {response.status}: {error_text}"
                    
                    logger.error(f"Splunk send failed: {self.last_error}")
                    
                    return SIEMResponse(
                        success=False,
                        platform=self.platform.value,
                        event_id=event.event_id,
                        error_message=self.last_error,
                        timestamp=datetime.now()
                    )
        
        except Exception as e:
            self.events_failed += 1
            self.last_error = str(e)
            
            logger.error(f"Splunk integration error: {e}")
            
            return SIEMResponse(
                success=False,
                platform=self.platform.value,
                event_id=event.event_id,
                error_message=str(e),
                timestamp=datetime.now()
            )


class QRadarIntegration(SIEMIntegration):
    """IBM QRadar REST API integration"""
    
    def __init__(self, config: dict):
        """
        Initialize QRadar integration
        
        Config requires:
            - url: QRadar console URL (e.g., https://qradar.company.com)
            - token: API authentication token
            - log_source: Log source identifier
            - verify_ssl: SSL verification (default: True)
        """
        super().__init__(SIEMPlatform.QRADAR, config)
        
        self.url = config.get("url")
        self.token = config.get("token")
        self.log_source = config.get("log_source", "Jupiter_Security_Platform")
        self.verify_ssl = config.get("verify_ssl", True)
        
        if not self.url or not self.token:
            raise ValueError("QRadar config requires 'url' and 'token'")
        
        # Build API endpoint
        self.api_endpoint = f"{self.url}/api/siem/offenses"
        
        logger.info(f"QRadar API configured: {self.url}")
    
    def _map_severity_to_qradar(self, severity: EventSeverity) -> int:
        """Map Jupiter severity to QRadar severity (1-10)"""
        mapping = {
            EventSeverity.CRITICAL: 10,
            EventSeverity.HIGH: 8,
            EventSeverity.MEDIUM: 5,
            EventSeverity.LOW: 3,
            EventSeverity.INFO: 1
        }
        return mapping.get(severity, 5)
    
    async def send_event(self, event: SIEMEvent) -> SIEMResponse:
        """Send event to QRadar"""
        try:
            # Ensure connection
            if self.session is None:
                await self.connect()
            
            # Build QRadar payload
            payload = {
                "offense_source": self.log_source,
                "severity": self._map_severity_to_qradar(event.severity),
                "description": f"{event.title}: {event.description}",
                "categories": ["vulnerability_detected"],
                "properties": {
                    "vulnerability_id": event.vulnerability_id,
                    "cve_id": event.cve_id,
                    "cvss_score": event.cvss_score,
                    "affected_asset": event.affected_asset,
                    "remediation_status": event.remediation_status,
                    "event_id": event.event_id
                }
            }
            
            # Send to QRadar API
            headers = {
                "SEC": self.token,
                "Content-Type": "application/json",
                "Version": "14.0"  # QRadar API version
            }
            
            async with self.session.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    self.events_sent += 1
                    
                    logger.info(f"Event sent to QRadar: {event.event_id}")
                    
                    return SIEMResponse(
                        success=True,
                        platform=self.platform.value,
                        event_id=event.event_id,
                        siem_event_id=str(result.get("id")),
                        timestamp=datetime.now()
                    )
                else:
                    error_text = await response.text()
                    self.events_failed += 1
                    self.last_error = f"HTTP {response.status}: {error_text}"
                    
                    logger.error(f"QRadar send failed: {self.last_error}")
                    
                    return SIEMResponse(
                        success=False,
                        platform=self.platform.value,
                        event_id=event.event_id,
                        error_message=self.last_error,
                        timestamp=datetime.now()
                    )
        
        except Exception as e:
            self.events_failed += 1
            self.last_error = str(e)
            
            logger.error(f"QRadar integration error: {e}")
            
            return SIEMResponse(
                success=False,
                platform=self.platform.value,
                event_id=event.event_id,
                error_message=str(e),
                timestamp=datetime.now()
            )


class SentinelIntegration(SIEMIntegration):
    """Microsoft Sentinel (Azure Monitor) integration"""
    
    def __init__(self, config: dict):
        """
        Initialize Sentinel integration
        
        Config requires:
            - workspace_id: Azure Log Analytics workspace ID
            - shared_key: Workspace shared key
            - log_type: Custom log type name (default: JupiterSecurityFindings)
        """
        super().__init__(SIEMPlatform.SENTINEL, config)
        
        self.workspace_id = config.get("workspace_id")
        self.shared_key = config.get("shared_key")
        self.log_type = config.get("log_type", "JupiterSecurityFindings")
        
        if not self.workspace_id or not self.shared_key:
            raise ValueError("Sentinel config requires 'workspace_id' and 'shared_key'")
        
        # Build Data Collector endpoint
        self.api_endpoint = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
        
        logger.info(f"Sentinel configured: workspace {self.workspace_id}")
    
    def _build_signature(self, date: str, content_length: int) -> str:
        """Build authorization signature for Azure Monitor"""
        string_to_hash = f"POST\n{content_length}\napplication/json\nx-ms-date:{date}\n/api/logs"
        bytes_to_hash = string_to_hash.encode('utf-8')
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode('utf-8')
        return f"SharedKey {self.workspace_id}:{encoded_hash}"
    
    def _map_severity_to_sentinel(self, severity: EventSeverity) -> str:
        """Map Jupiter severity to Sentinel severity"""
        mapping = {
            EventSeverity.CRITICAL: "Critical",
            EventSeverity.HIGH: "High",
            EventSeverity.MEDIUM: "Medium",
            EventSeverity.LOW: "Low",
            EventSeverity.INFO: "Informational"
        }
        return mapping.get(severity, "Medium")
    
    async def send_event(self, event: SIEMEvent) -> SIEMResponse:
        """Send event to Sentinel"""
        try:
            # Ensure connection
            if self.session is None:
                await self.connect()
            
            # Build Sentinel payload
            payload = [{
                "TimeGenerated": event.timestamp.isoformat(),
                "Severity": self._map_severity_to_sentinel(event.severity),
                "Title": event.title,
                "Description": event.description,
                "VulnerabilityId": event.vulnerability_id,
                "CVEId": event.cve_id,
                "CVSSScore": event.cvss_score,
                "AffectedAsset": event.affected_asset,
                "RemediationStatus": event.remediation_status,
                "EventId": event.event_id,
                "CorrelationId": event.correlation_id
            }]
            
            # Build request
            body = json.dumps(payload)
            content_length = len(body)
            rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            signature = self._build_signature(rfc1123date, content_length)
            
            headers = {
                "Content-Type": "application/json",
                "Log-Type": self.log_type,
                "Authorization": signature,
                "x-ms-date": rfc1123date
            }
            
            # Send to Sentinel
            async with self.session.post(
                self.api_endpoint,
                data=body,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    self.events_sent += 1
                    
                    logger.info(f"Event sent to Sentinel: {event.event_id}")
                    
                    return SIEMResponse(
                        success=True,
                        platform=self.platform.value,
                        event_id=event.event_id,
                        siem_event_id=event.event_id,  # Sentinel doesn't return ID
                        timestamp=datetime.now()
                    )
                else:
                    error_text = await response.text()
                    self.events_failed += 1
                    self.last_error = f"HTTP {response.status}: {error_text}"
                    
                    logger.error(f"Sentinel send failed: {self.last_error}")
                    
                    return SIEMResponse(
                        success=False,
                        platform=self.platform.value,
                        event_id=event.event_id,
                        error_message=self.last_error,
                        timestamp=datetime.now()
                    )
        
        except Exception as e:
            self.events_failed += 1
            self.last_error = str(e)
            
            logger.error(f"Sentinel integration error: {e}")
            
            return SIEMResponse(
                success=False,
                platform=self.platform.value,
                event_id=event.event_id,
                error_message=str(e),
                timestamp=datetime.now()
            )


def create_siem_integration(platform: str, config: dict) -> SIEMIntegration:
    """
    Factory function to create SIEM integration
    
    Args:
        platform: Platform name ('splunk', 'qradar', 'sentinel')
        config: Platform-specific configuration
        
    Returns:
        SIEMIntegration instance
    """
    platform_lower = platform.lower()
    
    if platform_lower == "splunk":
        return SplunkIntegration(config)
    elif platform_lower == "qradar":
        return QRadarIntegration(config)
    elif platform_lower == "sentinel":
        return SentinelIntegration(config)
    else:
        raise ValueError(f"Unsupported SIEM platform: {platform}")


# Export public classes
__all__ = [
    "SIEMPlatform",
    "EventSeverity",
    "SIEMEvent",
    "SIEMResponse",
    "SIEMIntegration",
    "SplunkIntegration",
    "QRadarIntegration",
    "SentinelIntegration",
    "create_siem_integration"
]
