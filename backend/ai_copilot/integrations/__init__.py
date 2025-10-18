"""
Jupiter AI Copilot - Third-Party Integrations Module
Connects Jupiter with enterprise security tools and communication platforms

Version: 2.0.0 (Phase 3)
"""

# Phase 3: Real SIEM Integration Module
try:
    from .siem_integration import (
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
    SIEM_AVAILABLE = True
except ImportError as e:
    SIEM_AVAILABLE = False
    print(f"SIEM Integration not available: {e}")
    
    # Fallback classes
    class SIEMIntegration:
        pass
    class SplunkIntegration:
        pass
    class QRadarIntegration:
        pass
    class SentinelIntegration:
        pass

# Phase 3: Ticketing Integration Module
try:
    from .ticketing_integration import (
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
    TICKETING_AVAILABLE = True
except ImportError as e:
    TICKETING_AVAILABLE = False
    print(f"Ticketing Integration not available: {e}")
    
    # Fallback classes
    class TicketingIntegration:
        pass
    class JiraIntegration:
        pass
    class ServiceNowIntegration:
        pass

# Phase 3: Communication Integration Module
try:
    from .communication_integration import (
        CommunicationIntegration,
        CommunicationPlatform,
        MessagePriority,
        MessageFormat,
        Message,
        MessageResponse,
        SlackIntegration,
        TeamsIntegration,
        EmailIntegration,
        create_communication_integration
    )
    COMMUNICATION_AVAILABLE = True
except ImportError as e:
    COMMUNICATION_AVAILABLE = False
    print(f"Communication Integration not available: {e}")
    
    # Fallback classes
    class CommunicationIntegration:
        pass
    class SlackIntegration:
        pass
    class TeamsIntegration:
        pass
    class EmailIntegration:
        pass

__all__ = [
    # SIEM Integration
    'SIEMIntegration',
    'SIEMPlatform',
    'EventSeverity',
    'SIEMEvent',
    'SIEMResponse',
    'SplunkIntegration',
    'QRadarIntegration',
    'SentinelIntegration',
    'create_siem_integration',
    'SIEM_AVAILABLE',
    
    # Ticketing Integration
    'TicketingIntegration',
    'TicketingPlatform',
    'TicketPriority',
    'TicketStatus',
    'Ticket',
    'TicketResponse',
    'JiraIntegration',
    'ServiceNowIntegration',
    'create_ticketing_integration',
    'TICKETING_AVAILABLE',
    
    # Communication Integration
    'CommunicationIntegration',
    'CommunicationPlatform',
    'MessagePriority',
    'MessageFormat',
    'Message',
    'MessageResponse',
    'SlackIntegration',
    'TeamsIntegration',
    'EmailIntegration',
    'create_communication_integration',
    'COMMUNICATION_AVAILABLE'
]
