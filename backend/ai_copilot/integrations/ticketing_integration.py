"""
Jupiter AI Copilot - Ticketing System Integration Module
Integrates with Jira and ServiceNow for automated ticket creation and management

Supports:
- Jira REST API v3 (Cloud and Server)
- ServiceNow Table API

Features:
- Ticket creation from vulnerabilities
- Priority mapping (CVSS → ticket priority)
- Status transitions and updates
- Custom field support
- Attachment handling
- Comment/note management

Version: 1.0.0
Author: Jupiter Development Team
"""

import aiohttp
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import base64


# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class TicketingPlatform(Enum):
    """Supported ticketing platforms"""
    JIRA = "jira"
    SERVICENOW = "servicenow"


class TicketPriority(Enum):
    """Ticket priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class TicketStatus(Enum):
    """Ticket status values"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    PENDING = "pending"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Ticket:
    """
    Represents a ticket in a ticketing system
    
    Attributes:
        title: Short summary of the issue
        description: Detailed description with context
        priority: Ticket priority level
        ticket_type: Type of ticket (bug, task, incident, etc.)
        project_key: Project identifier (Jira) or assignment group (ServiceNow)
        assignee: Optional user to assign ticket to
        labels: Optional list of labels/tags
        custom_fields: Optional dictionary of custom field values
        vulnerability_data: Optional vulnerability metadata
    """
    title: str
    description: str
    priority: TicketPriority
    ticket_type: str = "bug"
    project_key: Optional[str] = None
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    vulnerability_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "type": self.ticket_type,
            "project_key": self.project_key,
            "assignee": self.assignee,
            "labels": self.labels,
            "custom_fields": self.custom_fields,
            "vulnerability_data": self.vulnerability_data
        }


@dataclass
class TicketResponse:
    """
    Response from ticketing system operations
    
    Attributes:
        success: Whether operation succeeded
        platform: Platform name (jira, servicenow)
        ticket_id: Created/updated ticket ID
        ticket_key: Ticket key/number (e.g., PROJ-123, INC0001234)
        url: Direct URL to ticket
        timestamp: Operation timestamp
        error_message: Error details if failed
    """
    success: bool
    platform: str
    ticket_id: Optional[str] = None
    ticket_key: Optional[str] = None
    url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "success": self.success,
            "platform": self.platform,
            "ticket_id": self.ticket_id,
            "ticket_key": self.ticket_key,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message
        }


# ============================================================================
# Base Ticketing Integration Class
# ============================================================================

class TicketingIntegration:
    """
    Base class for ticketing system integrations
    
    Provides common functionality for ticket management:
    - Connection management
    - Ticket creation and updates
    - Status transitions
    - Comment/note management
    - Statistics tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ticketing integration
        
        Args:
            config: Configuration dictionary with platform-specific settings
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.tickets_created = 0
        self.tickets_updated = 0
        self.tickets_failed = 0
        self.last_error: Optional[str] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to ticketing system"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        logger.info(f"Connected to ticketing system")
    
    async def disconnect(self):
        """Close connection to ticketing system"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(f"Disconnected from ticketing system")
    
    async def create_ticket(self, ticket: Ticket) -> TicketResponse:
        """
        Create a new ticket
        
        Args:
            ticket: Ticket object with details
            
        Returns:
            TicketResponse with created ticket information
        """
        raise NotImplementedError("Subclasses must implement create_ticket()")
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> TicketResponse:
        """
        Update an existing ticket
        
        Args:
            ticket_id: Ticket identifier
            updates: Dictionary of fields to update
            
        Returns:
            TicketResponse with update status
        """
        raise NotImplementedError("Subclasses must implement update_ticket()")
    
    async def add_comment(self, ticket_id: str, comment: str) -> TicketResponse:
        """
        Add comment to ticket
        
        Args:
            ticket_id: Ticket identifier
            comment: Comment text
            
        Returns:
            TicketResponse with operation status
        """
        raise NotImplementedError("Subclasses must implement add_comment()")
    
    async def transition_status(self, ticket_id: str, status: TicketStatus) -> TicketResponse:
        """
        Transition ticket to new status
        
        Args:
            ticket_id: Ticket identifier
            status: New status
            
        Returns:
            TicketResponse with operation status
        """
        raise NotImplementedError("Subclasses must implement transition_status()")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check integration health
        
        Returns:
            Dictionary with health status
        """
        return {
            "platform": self.__class__.__name__.lower().replace("integration", ""),
            "connected": self.session is not None,
            "tickets_created": self.tickets_created,
            "tickets_updated": self.tickets_updated,
            "tickets_failed": self.tickets_failed,
            "last_error": self.last_error,
            "status": "healthy" if self.session and not self.last_error else "degraded"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get operation statistics
        
        Returns:
            Dictionary with statistics
        """
        total_operations = self.tickets_created + self.tickets_updated + self.tickets_failed
        success_rate = 0.0
        if total_operations > 0:
            success_rate = ((self.tickets_created + self.tickets_updated) / total_operations) * 100
        
        return {
            "platform": self.__class__.__name__.lower().replace("integration", ""),
            "tickets_created": self.tickets_created,
            "tickets_updated": self.tickets_updated,
            "tickets_failed": self.tickets_failed,
            "success_rate": round(success_rate, 2),
            "last_error": self.last_error
        }


# ============================================================================
# Jira Integration
# ============================================================================

class JiraIntegration(TicketingIntegration):
    """
    Jira REST API v3 Integration
    
    Supports Jira Cloud and Jira Server/Data Center
    
    Configuration:
        url: Jira instance URL (e.g., https://company.atlassian.net)
        username: Jira username/email
        api_token: API token (Cloud) or password (Server)
        verify_ssl: Whether to verify SSL certificates (default: True)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", "").rstrip("/")
        self.username = config.get("username")
        self.api_token = config.get("api_token")
        self.verify_ssl = config.get("verify_ssl", True)
        
        # Create auth header
        credentials = f"{self.username}:{self.api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {encoded}"
    
    def _map_priority_to_jira(self, priority: TicketPriority) -> str:
        """Map Jupiter priority to Jira priority name"""
        mapping = {
            TicketPriority.CRITICAL: "Highest",
            TicketPriority.HIGH: "High",
            TicketPriority.MEDIUM: "Medium",
            TicketPriority.LOW: "Low",
            TicketPriority.TRIVIAL: "Lowest"
        }
        return mapping.get(priority, "Medium")
    
    def _map_cvss_to_priority(self, cvss_score: float) -> TicketPriority:
        """Map CVSS score to ticket priority"""
        if cvss_score >= 9.0:
            return TicketPriority.CRITICAL
        elif cvss_score >= 7.0:
            return TicketPriority.HIGH
        elif cvss_score >= 4.0:
            return TicketPriority.MEDIUM
        elif cvss_score >= 0.1:
            return TicketPriority.LOW
        else:
            return TicketPriority.TRIVIAL
    
    async def create_ticket(self, ticket: Ticket) -> TicketResponse:
        """
        Create Jira issue
        
        Args:
            ticket: Ticket details
            
        Returns:
            TicketResponse with created issue information
        """
        try:
            endpoint = f"{self.url}/rest/api/3/issue"
            
            # Build Jira issue payload
            payload = {
                "fields": {
                    "project": {"key": ticket.project_key},
                    "summary": ticket.title,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": ticket.description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": ticket.ticket_type.capitalize()},
                    "priority": {"name": self._map_priority_to_jira(ticket.priority)}
                }
            }
            
            # Add assignee if specified
            if ticket.assignee:
                payload["fields"]["assignee"] = {"name": ticket.assignee}
            
            # Add labels if specified
            if ticket.labels:
                payload["fields"]["labels"] = ticket.labels
            
            # Add custom fields
            if ticket.custom_fields:
                payload["fields"].update(ticket.custom_fields)
            
            # Add vulnerability data as custom field if present
            if ticket.vulnerability_data:
                # Store as description addition
                vuln_text = f"\n\n*Vulnerability Details:*\n"
                for key, value in ticket.vulnerability_data.items():
                    vuln_text += f"* {key}: {value}\n"
                
                payload["fields"]["description"]["content"].append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": vuln_text
                        }
                    ]
                })
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status in [200, 201]:
                    data = await response.json()
                    issue_id = data.get("id")
                    issue_key = data.get("key")
                    issue_url = f"{self.url}/browse/{issue_key}"
                    
                    self.tickets_created += 1
                    logger.info(f"Jira ticket created: {issue_key}")
                    
                    return TicketResponse(
                        success=True,
                        platform="jira",
                        ticket_id=issue_id,
                        ticket_key=issue_key,
                        url=issue_url
                    )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    self.tickets_failed += 1
                    logger.error(f"Jira ticket creation failed: {error_msg}")
                    
                    return TicketResponse(
                        success=False,
                        platform="jira",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"Jira ticket creation error: {str(e)}"
            self.last_error = error_msg
            self.tickets_failed += 1
            logger.error(error_msg)
            
            return TicketResponse(
                success=False,
                platform="jira",
                error_message=error_msg
            )
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> TicketResponse:
        """Update Jira issue"""
        try:
            endpoint = f"{self.url}/rest/api/3/issue/{ticket_id}"
            
            payload = {"fields": updates}
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            async with self.session.put(
                endpoint,
                json=payload,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status in [200, 204]:
                    self.tickets_updated += 1
                    logger.info(f"Jira ticket updated: {ticket_id}")
                    
                    return TicketResponse(
                        success=True,
                        platform="jira",
                        ticket_id=ticket_id
                    )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    self.tickets_failed += 1
                    
                    return TicketResponse(
                        success=False,
                        platform="jira",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"Jira update error: {str(e)}"
            self.last_error = error_msg
            self.tickets_failed += 1
            
            return TicketResponse(
                success=False,
                platform="jira",
                error_message=error_msg
            )
    
    async def add_comment(self, ticket_id: str, comment: str) -> TicketResponse:
        """Add comment to Jira issue"""
        try:
            endpoint = f"{self.url}/rest/api/3/issue/{ticket_id}/comment"
            
            payload = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status in [200, 201]:
                    logger.info(f"Comment added to Jira ticket: {ticket_id}")
                    
                    return TicketResponse(
                        success=True,
                        platform="jira",
                        ticket_id=ticket_id
                    )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    
                    return TicketResponse(
                        success=False,
                        platform="jira",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"Jira comment error: {str(e)}"
            self.last_error = error_msg
            
            return TicketResponse(
                success=False,
                platform="jira",
                error_message=error_msg
            )
    
    async def transition_status(self, ticket_id: str, status: TicketStatus) -> TicketResponse:
        """Transition Jira issue status"""
        try:
            # Get available transitions
            transitions_endpoint = f"{self.url}/rest/api/3/issue/{ticket_id}/transitions"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                transitions_endpoint,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    transitions = data.get("transitions", [])
                    
                    # Find matching transition
                    target_status = status.value.replace("_", " ").title()
                    transition_id = None
                    
                    for trans in transitions:
                        if trans["name"].lower() == target_status.lower():
                            transition_id = trans["id"]
                            break
                    
                    if not transition_id:
                        error_msg = f"No transition found for status: {target_status}"
                        self.last_error = error_msg
                        return TicketResponse(
                            success=False,
                            platform="jira",
                            error_message=error_msg
                        )
                    
                    # Execute transition
                    payload = {"transition": {"id": transition_id}}
                    
                    async with self.session.post(
                        transitions_endpoint,
                        json=payload,
                        headers=headers,
                        ssl=self.verify_ssl
                    ) as trans_response:
                        
                        if trans_response.status in [200, 204]:
                            logger.info(f"Jira ticket transitioned: {ticket_id} -> {target_status}")
                            
                            return TicketResponse(
                                success=True,
                                platform="jira",
                                ticket_id=ticket_id
                            )
                        else:
                            error_text = await trans_response.text()
                            error_msg = f"HTTP {trans_response.status}: {error_text}"
                            self.last_error = error_msg
                            
                            return TicketResponse(
                                success=False,
                                platform="jira",
                                error_message=error_msg
                            )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    
                    return TicketResponse(
                        success=False,
                        platform="jira",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"Jira transition error: {str(e)}"
            self.last_error = error_msg
            
            return TicketResponse(
                success=False,
                platform="jira",
                error_message=error_msg
            )


# ============================================================================
# ServiceNow Integration
# ============================================================================

class ServiceNowIntegration(TicketingIntegration):
    """
    ServiceNow Table API Integration
    
    Creates and manages incidents in ServiceNow
    
    Configuration:
        instance: ServiceNow instance name (e.g., 'dev12345')
        username: ServiceNow username
        password: ServiceNow password
        table: Table to use (default: 'incident')
        verify_ssl: Whether to verify SSL certificates (default: True)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.instance = config.get("instance")
        self.username = config.get("username")
        self.password = config.get("password")
        self.table = config.get("table", "incident")
        self.verify_ssl = config.get("verify_ssl", True)
        
        self.url = f"https://{self.instance}.service-now.com"
        
        # Create auth header
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {encoded}"
    
    def _map_priority_to_servicenow(self, priority: TicketPriority) -> str:
        """Map Jupiter priority to ServiceNow priority (1-5)"""
        mapping = {
            TicketPriority.CRITICAL: "1",  # Critical
            TicketPriority.HIGH: "2",      # High
            TicketPriority.MEDIUM: "3",    # Moderate
            TicketPriority.LOW: "4",       # Low
            TicketPriority.TRIVIAL: "5"    # Planning
        }
        return mapping.get(priority, "3")
    
    def _map_priority_to_impact(self, priority: TicketPriority) -> str:
        """Map priority to impact (1-3)"""
        if priority == TicketPriority.CRITICAL:
            return "1"  # High
        elif priority in [TicketPriority.HIGH, TicketPriority.MEDIUM]:
            return "2"  # Medium
        else:
            return "3"  # Low
    
    async def create_ticket(self, ticket: Ticket) -> TicketResponse:
        """
        Create ServiceNow incident
        
        Args:
            ticket: Ticket details
            
        Returns:
            TicketResponse with created incident information
        """
        try:
            endpoint = f"{self.url}/api/now/table/{self.table}"
            
            # Build ServiceNow payload
            payload = {
                "short_description": ticket.title,
                "description": ticket.description,
                "priority": self._map_priority_to_servicenow(ticket.priority),
                "impact": self._map_priority_to_impact(ticket.priority),
                "urgency": self._map_priority_to_servicenow(ticket.priority),
                "category": "Security",
                "subcategory": "Vulnerability"
            }
            
            # Add assignment group if specified
            if ticket.project_key:
                payload["assignment_group"] = ticket.project_key
            
            # Add assigned_to if specified
            if ticket.assignee:
                payload["assigned_to"] = ticket.assignee
            
            # Add custom fields
            if ticket.custom_fields:
                payload.update(ticket.custom_fields)
            
            # Add vulnerability data as work notes
            if ticket.vulnerability_data:
                work_notes = "Vulnerability Details:\n"
                for key, value in ticket.vulnerability_data.items():
                    work_notes += f"{key}: {value}\n"
                payload["work_notes"] = work_notes
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status in [200, 201]:
                    data = await response.json()
                    result = data.get("result", {})
                    
                    incident_id = result.get("sys_id")
                    incident_number = result.get("number")
                    incident_url = f"{self.url}/nav_to.do?uri=incident.do?sys_id={incident_id}"
                    
                    self.tickets_created += 1
                    logger.info(f"ServiceNow incident created: {incident_number}")
                    
                    return TicketResponse(
                        success=True,
                        platform="servicenow",
                        ticket_id=incident_id,
                        ticket_key=incident_number,
                        url=incident_url
                    )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    self.tickets_failed += 1
                    logger.error(f"ServiceNow incident creation failed: {error_msg}")
                    
                    return TicketResponse(
                        success=False,
                        platform="servicenow",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"ServiceNow incident creation error: {str(e)}"
            self.last_error = error_msg
            self.tickets_failed += 1
            logger.error(error_msg)
            
            return TicketResponse(
                success=False,
                platform="servicenow",
                error_message=error_msg
            )
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> TicketResponse:
        """Update ServiceNow incident"""
        try:
            endpoint = f"{self.url}/api/now/table/{self.table}/{ticket_id}"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            async with self.session.patch(
                endpoint,
                json=updates,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                if response.status == 200:
                    self.tickets_updated += 1
                    logger.info(f"ServiceNow incident updated: {ticket_id}")
                    
                    return TicketResponse(
                        success=True,
                        platform="servicenow",
                        ticket_id=ticket_id
                    )
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    self.last_error = error_msg
                    self.tickets_failed += 1
                    
                    return TicketResponse(
                        success=False,
                        platform="servicenow",
                        error_message=error_msg
                    )
        
        except Exception as e:
            error_msg = f"ServiceNow update error: {str(e)}"
            self.last_error = error_msg
            self.tickets_failed += 1
            
            return TicketResponse(
                success=False,
                platform="servicenow",
                error_message=error_msg
            )
    
    async def add_comment(self, ticket_id: str, comment: str) -> TicketResponse:
        """Add work note to ServiceNow incident"""
        return await self.update_ticket(ticket_id, {"work_notes": comment})
    
    async def transition_status(self, ticket_id: str, status: TicketStatus) -> TicketResponse:
        """Transition ServiceNow incident state"""
        # ServiceNow incident states
        state_mapping = {
            TicketStatus.OPEN: "1",           # New
            TicketStatus.IN_PROGRESS: "2",    # In Progress
            TicketStatus.PENDING: "3",        # On Hold
            TicketStatus.RESOLVED: "6",       # Resolved
            TicketStatus.CLOSED: "7"          # Closed
        }
        
        state = state_mapping.get(status, "1")
        return await self.update_ticket(ticket_id, {"state": state})


# ============================================================================
# Factory Function
# ============================================================================

def create_ticketing_integration(platform: str, config: Dict[str, Any]) -> TicketingIntegration:
    """
    Factory function to create ticketing integration
    
    Args:
        platform: Platform name ('jira' or 'servicenow')
        config: Platform-specific configuration
        
    Returns:
        TicketingIntegration instance
        
    Raises:
        ValueError: If platform not supported
    """
    platform = platform.lower()
    
    if platform == "jira":
        return JiraIntegration(config)
    elif platform == "servicenow":
        return ServiceNowIntegration(config)
    else:
        raise ValueError(f"Unsupported ticketing platform: {platform}")
