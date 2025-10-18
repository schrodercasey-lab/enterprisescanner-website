"""
Enterprise Scanner AI Copilot

Intelligent security assistant with role-based access providing:
- Real-time scan analysis and threat explanation
- Step-by-step remediation guidance
- Natural language security queries
- Voice interface (Phase 2)
- Autonomous operations (Military mode)

Author: Enterprise Scanner Team
Version: 1.0.0
Date: October 17, 2025
"""

__version__ = "1.2.0"
__author__ = "Enterprise Scanner Team"

# Core modules
from .core.copilot_engine import CopilotEngine, QueryType
from .core.access_control import AccessControl, AccessLevel
from .core.context_manager import ContextManager

# Knowledge modules
from .knowledge.knowledge_base import KnowledgeBase
from .knowledge.rag_system import RAGSystem

# Analysis modules
from .analysis.scan_analyzer import ScanAnalyzer
from .analysis.threat_explainer import ThreatExplainer
from .analysis.remediation_advisor import RemediationAdvisor

# Interface modules
from .interfaces.chat_api import ChatAPI

# ============================================================================
# PHASE 1 INTEGRATIONS (October 18, 2025)
# ============================================================================

# Threat Intelligence modules (10 modules integrated)
try:
    from .threat_intelligence.intelligence_aggregator import ThreatIntelligenceAggregator
    from .threat_intelligence.predictive_analyzer import PredictiveAnalyzer
    from .threat_intelligence.industry_intel import IndustryIntelligence
    from .threat_intelligence.feed_api import ThreatFeedAPI
    from .threat_intelligence.actor_profiling import ThreatActorProfiler
    from .threat_intelligence.correlation_engine import CorrelationEngine
    THREAT_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    THREAT_INTELLIGENCE_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Threat Intelligence modules not available: {e}")

# Analytics modules (3 modules integrated)
try:
    from .analytics.usage_tracker import JupiterUsageTracker
    from .analytics.roi_calculator import JupiterROICalculator
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    ANALYTICS_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Analytics modules not available: {e}")

# Compliance modules (2 modules integrated)
try:
    from .compliance.audit_logger import JupiterAuditLogger
    from .compliance.compliance_reporter import JupiterComplianceReporter
    COMPLIANCE_AVAILABLE = True
except ImportError as e:
    COMPLIANCE_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Compliance modules not available: {e}")

# ============================================================================
# PHASE 2 INTEGRATIONS (October 18, 2025)
# ============================================================================

# Remediation modules (10 modules integrated)
try:
    from .remediation.script_generator import ScriptGenerator
    from .remediation.config_generator import ConfigGenerator
    from .remediation.patch_automation import PatchAutomation
    from .remediation.rollback_manager import RollbackManager
    from .remediation.testing_framework import TestingFramework
    from .remediation.validation_engine import ValidationEngine
    from .remediation.remediation_workflow import RemediationWorkflow
    from .remediation.change_management import ChangeManagement
    from .remediation.dependency_analyzer import DependencyAnalyzer
    from .remediation.remediation_reporter import RemediationReporter
    REMEDIATION_AVAILABLE = True
except ImportError as e:
    REMEDIATION_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Remediation modules not available: {e}")

# Integration modules (3 modules integrated)
try:
    from .integrations.siem_integration import SIEMIntegration
    from .integrations.ticketing_integration import TicketingIntegration
    from .integrations.communication_integration import CommunicationIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    INTEGRATIONS_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Integration modules not available: {e}")

# Proactive Monitoring modules (2 modules integrated)
try:
    from .proactive.proactive_alerts import ProactiveAlerts
    from .proactive.threat_feeds import ThreatFeeds
    PROACTIVE_AVAILABLE = True
except ImportError as e:
    PROACTIVE_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Proactive monitoring modules not available: {e}")

# Integration status
INTEGRATION_STATUS = {
    'threat_intelligence': THREAT_INTELLIGENCE_AVAILABLE,
    'analytics': ANALYTICS_AVAILABLE,
    'compliance': COMPLIANCE_AVAILABLE,
    'remediation': REMEDIATION_AVAILABLE,
    'integrations': INTEGRATIONS_AVAILABLE,
    'proactive': PROACTIVE_AVAILABLE,
}

__all__ = [
    # Core
    'CopilotEngine',
    'QueryType',
    'AccessControl',
    'AccessLevel',
    'ContextManager',
    
    # Knowledge
    'KnowledgeBase',
    'RAGSystem',
    
    # Analysis
    'ScanAnalyzer',
    'ThreatExplainer',
    'RemediationAdvisor',
    
    # Interfaces
    'ChatAPI',
    
    # Phase 1 Integrations - Threat Intelligence
    'ThreatIntelligenceAggregator',
    'PredictiveAnalyzer',
    'IndustryIntelligence',
    'ThreatFeedAPI',
    'ThreatActorProfiler',
    'CorrelationEngine',
    
    # Phase 1 Integrations - Analytics
    'JupiterUsageTracker',
    'JupiterROICalculator',
    
    # Phase 1 Integrations - Compliance
    'JupiterAuditLogger',
    'JupiterComplianceReporter',
    
    # Phase 2 Integrations - Remediation
    'ScriptGenerator',
    'ConfigGenerator',
    'PatchAutomation',
    'RollbackManager',
    'TestingFramework',
    'ValidationEngine',
    'RemediationWorkflow',
    'ChangeManagement',
    'DependencyAnalyzer',
    'RemediationReporter',
    
    # Phase 2 Integrations - Third-Party Integrations
    'SIEMIntegration',
    'TicketingIntegration',
    'CommunicationIntegration',
    
    # Phase 2 Integrations - Proactive Monitoring
    'ProactiveAlerts',
    'ThreatFeeds',
    
    # Integration status
    'INTEGRATION_STATUS',
]
