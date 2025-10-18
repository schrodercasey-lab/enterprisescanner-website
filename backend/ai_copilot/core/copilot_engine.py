"""
Module 1: Copilot Engine - Core Orchestration

Central AI orchestration engine that:
- Routes user queries to appropriate modules
- Manages LLM API calls (GPT-4)
- Coordinates responses from specialized modules
- Handles error recovery and fallback
- Logs all interactions for audit

This is the brain of the AI Copilot system.

Author: Enterprise Scanner Team
Version: 1.4.0 (Phase 2 Integration: Third-Party Integrations Connected - SIEM, Ticketing, Communication)
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

# Import other modules (will be created)
from ..utils.llm_providers import LLMProvider
from .access_control import AccessControl, AccessLevel
from .context_manager import ContextManager

# Phase 1 Integration: Analytics modules
try:
    from ..analytics import JupiterUsageTracker, JupiterROICalculator
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Analytics modules not available: {e}")
    ANALYTICS_AVAILABLE = False

# Phase 1 Integration: Compliance modules
try:
    from ..compliance import JupiterAuditLogger, JupiterComplianceReporter
    COMPLIANCE_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Compliance modules not available: {e}")
    COMPLIANCE_AVAILABLE = False

# Phase 2 Integration: Third-Party Integration modules
try:
    from ..integrations import SIEMIntegration, TicketingIntegration, CommunicationIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Integration modules not available: {e}")
    INTEGRATIONS_AVAILABLE = False


class QueryType(Enum):
    """Types of queries the system can handle"""
    GENERAL_QUESTION = "general_question"
    SCAN_ANALYSIS = "scan_analysis"
    VULNERABILITY_EXPLANATION = "vulnerability_explanation"
    THREAT_LOOKUP = "threat_lookup"
    REMEDIATION_REQUEST = "remediation_request"
    CODE_GENERATION = "code_generation"
    REPORT_GENERATION = "report_generation"
    COMPLIANCE_CHECK = "compliance_check"
    SYSTEM_STATUS = "system_status"
    
    # Threat Intelligence queries (Phase 1 Integration)
    THREAT_INTELLIGENCE_LOOKUP = "threat_intelligence_lookup"
    THREAT_ACTOR_PROFILE = "threat_actor_profile"
    INDUSTRY_THREAT_BRIEF = "industry_threat_brief"
    PREDICTIVE_THREAT_ANALYSIS = "predictive_threat_analysis"
    
    # Analytics queries (Phase 1 Integration)
    ROI_CALCULATION = "roi_calculation"
    USAGE_ANALYTICS = "usage_analytics"
    
    # Compliance queries (Phase 1 Integration)
    AUDIT_LOG_QUERY = "audit_log_query"
    COMPLIANCE_REPORT = "compliance_report"
    
    # Automated Remediation queries (Phase 2 Integration)
    GENERATE_SCRIPT = "generate_script"
    GENERATE_CONFIG = "generate_config"
    AUTOMATE_PATCH = "automate_patch"
    CREATE_ROLLBACK = "create_rollback"
    TEST_REMEDIATION = "test_remediation"
    VALIDATE_FIX = "validate_fix"
    REMEDIATION_WORKFLOW = "remediation_workflow"
    TRACK_CHANGES = "track_changes"
    
    # Third-Party Integration queries (Phase 2 Integration)
    SEND_TO_SIEM = "send_to_siem"
    CREATE_TICKET = "create_ticket"
    SEND_ALERT = "send_alert"
    
    # Proactive Monitoring queries (Phase 2 Integration)
    SETUP_MONITORING = "setup_monitoring"
    CONFIGURE_ALERTS = "configure_alerts"


class ResponseFormat(Enum):
    """Response formatting options"""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


@dataclass
class Query:
    """User query object"""
    query_id: str
    user_id: str
    session_id: str
    message: str
    query_type: QueryType
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Context
    access_level: Optional[str] = None
    active_scan: Optional[str] = None
    active_threats: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    """AI Copilot response"""
    query_id: str
    response_text: str
    response_format: ResponseFormat = ResponseFormat.MARKDOWN
    
    # Sources and citations
    sources: List[str] = field(default_factory=list)
    citations: List[Dict[str, str]] = field(default_factory=list)
    
    # Suggestions and actions
    suggested_actions: List[str] = field(default_factory=list)
    quick_replies: List[str] = field(default_factory=list)
    
    # Metadata
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    tokens_used: int = 0
    model_used: str = ""
    
    # Error handling
    error: Optional[str] = None
    fallback_used: bool = False
    
    timestamp: datetime = field(default_factory=datetime.now)


class CopilotEngine:
    """
    Main AI Copilot orchestration engine
    
    Responsibilities:
    - Query routing and processing
    - LLM interaction management
    - Response formatting and enrichment
    - Error handling and recovery
    - Audit logging
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model: str = "gpt-4-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        log_level: str = "INFO"
    ):
        """
        Initialize Copilot Engine
        
        Args:
            llm_provider: LLM provider ('openai', 'anthropic', 'google')
            model: Model name
            temperature: LLM temperature (0-1)
            max_tokens: Max response tokens
            log_level: Logging level
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level))
        
        # Initialize LLM provider
        self.llm = LLMProvider(provider=llm_provider, model=model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize subsystems (will fail gracefully if not available)
        try:
            self.access_control = AccessControl()
        except Exception as e:
            self.logger.warning(f"AccessControl initialization failed: {e}")
            self.access_control = None
            
        try:
            self.context_manager = ContextManager()
        except Exception as e:
            self.logger.warning(f"ContextManager initialization failed: {e}")
            self.context_manager = None
        
        # Phase 1 Integration: Initialize analytics modules
        self.analytics_available = False
        if ANALYTICS_AVAILABLE:
            try:
                self.usage_tracker = JupiterUsageTracker()
                self.roi_calculator = JupiterROICalculator()
                self.analytics_available = True
                self.logger.info("Analytics modules initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize analytics: {e}")
        
        # Phase 1 Integration: Initialize compliance modules
        self.compliance_available = False
        if COMPLIANCE_AVAILABLE:
            try:
                self.audit_logger = JupiterAuditLogger()
                self.compliance_reporter = JupiterComplianceReporter()
                self.compliance_available = True
                self.logger.info("Compliance modules initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize compliance: {e}")
        
        # Phase 2 Integration: Initialize third-party integration modules
        self.integrations_available = False
        if INTEGRATIONS_AVAILABLE:
            try:
                self.siem_integration = SIEMIntegration()
                self.ticketing_integration = TicketingIntegration()
                self.communication_integration = CommunicationIntegration()
                self.integrations_available = True
                self.logger.info("Phase 2 integration modules initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Phase 2 integrations: {e}")
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'total_tokens_used': 0,
            'average_response_time_ms': 0,
            'analytics_tracked': 0,  # Phase 1: Track analytics events
            'audit_logs_created': 0,  # Phase 1: Track compliance logs
            'siem_alerts_sent': 0,  # Phase 2: Track SIEM integrations
            'tickets_created': 0,  # Phase 2: Track ticket creation
            'alerts_sent': 0  # Phase 2: Track communication alerts
        }
        
        self.logger.info(f"CopilotEngine initialized with {llm_provider}/{model}")
    
    def process_query(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None,
        access_level: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Main query processing pipeline
        
        Args:
            user_id: User identifier
            message: User's message/question
            session_id: Session identifier (for conversation tracking)
            access_level: User's access level override
            context: Additional context (active_scan, threats, etc.)
            
        Returns:
            Response object with AI response and metadata
        """
        start_time = time.time()
        query_id = self._generate_query_id()
        
        self.stats['total_queries'] += 1
        
        # Phase 1 Integration: Track query start with analytics
        if self.analytics_available:
            try:
                self.usage_tracker.track_query_start(
                    query_id=query_id,
                    user_id=user_id,
                    session_id=session_id or self._generate_session_id(user_id),
                    timestamp=datetime.now()
                )
            except Exception as e:
                self.logger.debug(f"Analytics tracking (start) failed: {e}")
        
        try:
            # 1. Create query object
            query = self._create_query(
                query_id=query_id,
                user_id=user_id,
                message=message,
                session_id=session_id or self._generate_session_id(user_id),
                access_level=access_level,
                context=context or {}
            )
            
            # 2. Verify access permissions
            if not self._verify_access(query):
                return self._create_error_response(
                    query_id,
                    "Access denied: Insufficient permissions"
                )
            
            # 3. Detect query type
            query.query_type = self._detect_query_type(message)
            
            # Phase 1 Integration: Log query for compliance (SOC 2)
            if self.compliance_available:
                try:
                    self.audit_logger.log_query(
                        query_id=query_id,
                        user_id=user_id,
                        session_id=query.session_id,
                        query_type=query.query_type.value,
                        message=message,
                        access_level=query.access_level,
                        timestamp=datetime.now(),
                        ip_address=query.metadata.get('ip_address'),
                        user_agent=query.metadata.get('user_agent')
                    )
                    self.stats['audit_logs_created'] += 1
                except Exception as e:
                    self.logger.debug(f"Compliance logging (query) failed: {e}")
            
            # 4. Get conversation context
            conversation_context = self._get_conversation_context(query)
            
            # 5. Build system prompt
            system_prompt = self._build_system_prompt(query)
            
            # 6. Route query to appropriate handler
            response_text = self._route_query(query, system_prompt, conversation_context)
            
            # 7. Post-process response
            response = self._build_response(
                query_id=query_id,
                response_text=response_text,
                query=query,
                start_time=start_time
            )
            
            # 8. Update context
            self._update_context(query, response)
            
            # 9. Log interaction
            self._log_interaction(query, response)
            
            # Phase 1 Integration: Log response for compliance (SOC 2)
            if self.compliance_available:
                try:
                    self.audit_logger.log_response(
                        query_id=query_id,
                        user_id=user_id,
                        response_length=len(response.response_text),
                        tokens_used=response.tokens_used,
                        processing_time_ms=response.processing_time_ms,
                        success=True,
                        confidence_score=response.confidence_score,
                        timestamp=datetime.now(),
                        model_used=response.model_used
                    )
                except Exception as e:
                    self.logger.debug(f"Compliance logging (response) failed: {e}")
            
            # Phase 1 Integration: Track query completion with analytics
            if self.analytics_available:
                try:
                    processing_time_ms = response.processing_time_ms
                    
                    self.usage_tracker.track_query_complete(
                        query_id=query_id,
                        user_id=user_id,
                        query_type=query.query_type.value,
                        duration_ms=processing_time_ms,
                        tokens_used=response.tokens_used,
                        success=True,
                        timestamp=datetime.now()
                    )
                    
                    # Calculate ROI for this query
                    roi_data = self.roi_calculator.calculate_query_roi(
                        query_type=query.query_type.value,
                        tokens_used=response.tokens_used,
                        processing_time_ms=processing_time_ms,
                        user_id=user_id
                    )
                    
                    # Add ROI data to response metadata (if available)
                    if roi_data and hasattr(response, 'metadata'):
                        response.metadata = response.metadata or {}
                        response.metadata['roi'] = roi_data
                    
                    self.stats['analytics_tracked'] += 1
                    
                except Exception as e:
                    self.logger.debug(f"Analytics tracking (complete) failed: {e}")
            
            self.stats['successful_queries'] += 1
            
            return response
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}", exc_info=True)
            self.stats['failed_queries'] += 1
            
            # Phase 1 Integration: Log failed response for compliance
            if self.compliance_available:
                try:
                    processing_time_ms = int((time.time() - start_time) * 1000)
                    
                    self.audit_logger.log_response(
                        query_id=query_id,
                        user_id=user_id,
                        response_length=0,
                        tokens_used=0,
                        processing_time_ms=processing_time_ms,
                        success=False,
                        error_message=str(e),
                        timestamp=datetime.now()
                    )
                except Exception as compliance_error:
                    self.logger.debug(f"Compliance logging (failed response) error: {compliance_error}")
            
            # Phase 1 Integration: Track failed query
            if self.analytics_available:
                try:
                    processing_time_ms = int((time.time() - start_time) * 1000)
                    
                    self.usage_tracker.track_query_complete(
                        query_id=query_id,
                        user_id=user_id,
                        query_type="unknown",
                        duration_ms=processing_time_ms,
                        tokens_used=0,
                        success=False,
                        error_message=str(e),
                        timestamp=datetime.now()
                    )
                except Exception as analytics_error:
                    self.logger.debug(f"Analytics tracking (failed query) error: {analytics_error}")
            
            return self._create_error_response(
                query_id,
                f"Query processing error: {str(e)}"
            )
    
    def _create_query(
        self,
        query_id: str,
        user_id: str,
        message: str,
        session_id: str,
        access_level: Optional[str],
        context: Dict[str, Any]
    ) -> Query:
        """Create query object from inputs"""
        return Query(
            query_id=query_id,
            user_id=user_id,
            session_id=session_id,
            message=message,
            query_type=QueryType.GENERAL_QUESTION,  # Will be detected
            access_level=access_level or self._get_user_access_level(user_id),
            active_scan=context.get('active_scan'),
            active_threats=context.get('active_threats', []),
            metadata=context.get('metadata', {})
        )
    
    def _verify_access(self, query: Query) -> bool:
        """Verify user has access to requested feature"""
        if not self.access_control:
            return True  # Fail open if access control not initialized
        
        try:
            # Check rate limiting
            if not self.access_control.check_rate_limit(query.user_id):
                self.logger.warning(f"Rate limit exceeded for user {query.user_id}")
                return False
            
            # Check feature access
            feature = self._query_type_to_feature(query.query_type)
            if not self.access_control.verify_access(query.user_id, feature):
                self.logger.warning(
                    f"Access denied for user {query.user_id} to feature {feature}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Access verification failed: {e}")
            return True  # Fail open
    
    def _detect_query_type(self, message: str) -> QueryType:
        """
        Detect query type from message content
        
        Uses pattern matching and keyword detection
        """
        message_lower = message.lower()
        
        # Threat Intelligence patterns (Phase 1 Integration)
        if any(word in message_lower for word in ['threat intelligence', 'threat actor', 'apt', 'threat landscape']):
            return QueryType.THREAT_INTELLIGENCE_LOOKUP
        
        if any(word in message_lower for word in ['apt group', 'threat actor profile', 'who is attacking']):
            return QueryType.THREAT_ACTOR_PROFILE
        
        if any(word in message_lower for word in ['industry threats', 'sector threats', 'industry brief']):
            return QueryType.INDUSTRY_THREAT_BRIEF
        
        if any(word in message_lower for word in ['predict', 'forecas', 'future threat', 'trend']):
            return QueryType.PREDICTIVE_THREAT_ANALYSIS
        
        # Analytics patterns (Phase 1 Integration)
        if any(word in message_lower for word in ['roi', 'return on investment', 'cost savings', 'calculate roi']):
            return QueryType.ROI_CALCULATION
        
        if any(word in message_lower for word in ['usage', 'statistics', 'analytics', 'metrics']):
            return QueryType.USAGE_ANALYTICS
        
        # Compliance patterns (Phase 1 Integration)
        if any(word in message_lower for word in ['audit log', 'audit trail', 'who accessed', 'activity log']):
            return QueryType.AUDIT_LOG_QUERY
        
        if any(word in message_lower for word in ['compliance report', 'audit report', 'compliance status']):
            return QueryType.COMPLIANCE_REPORT
        
        # Automated Remediation patterns (Phase 2 Integration)
        if any(word in message_lower for word in ['generate script', 'create script', 'remediation script']):
            return QueryType.GENERATE_SCRIPT
        
        if any(word in message_lower for word in ['generate config', 'create config', 'configuration file']):
            return QueryType.GENERATE_CONFIG
        
        if any(word in message_lower for word in ['automate patch', 'automatic patching', 'deploy patch']):
            return QueryType.AUTOMATE_PATCH
        
        if any(word in message_lower for word in ['rollback', 'create snapshot', 'backup before']):
            return QueryType.CREATE_ROLLBACK
        
        if any(word in message_lower for word in ['test remediation', 'test the remediation', 'test fix', 'test script', 'validate script']):
            return QueryType.TEST_REMEDIATION
        
        if any(word in message_lower for word in ['validate fix', 'verify fix', 'check if fixed']):
            return QueryType.VALIDATE_FIX
        
        if any(word in message_lower for word in ['remediation workflow', 'fix workflow', 'remediation process']):
            return QueryType.REMEDIATION_WORKFLOW
        
        if any(word in message_lower for word in ['track changes', 'change log', 'change history']):
            return QueryType.TRACK_CHANGES
        
        # Third-Party Integration patterns (Phase 2 Integration)
        if any(word in message_lower for word in ['send to siem', 'send to splunk', 'send to qradar', 'send to sentinel']):
            return QueryType.SEND_TO_SIEM
        
        if any(word in message_lower for word in ['create ticket', 'create jira', 'create servicenow', 'open ticket']):
            return QueryType.CREATE_TICKET
        
        if any(word in message_lower for word in ['send alert', 'notify', 'send to slack', 'send to teams', 'email alert']):
            return QueryType.SEND_ALERT
        
        # Proactive Monitoring patterns (Phase 2 Integration)
        if any(word in message_lower for word in ['setup monitoring', 'enable monitoring', 'continuous monitoring']):
            return QueryType.SETUP_MONITORING
        
        if any(word in message_lower for word in ['configure alert', 'setup alert', 'alert threshold']):
            return QueryType.CONFIGURE_ALERTS
        
        # Scan analysis patterns
        if any(word in message_lower for word in ['scan', 'result', 'findings', 'vulnerabilities found']):
            return QueryType.SCAN_ANALYSIS
        
        # Vulnerability explanation patterns
        if any(word in message_lower for word in ['explain', 'cve-', 'vulnerability', 'what is']):
            return QueryType.VULNERABILITY_EXPLANATION
        
        # Threat lookup patterns
        if any(word in message_lower for word in ['threat', 'attack', 'exploit', 'mitre']):
            return QueryType.THREAT_LOOKUP
        
        # Remediation patterns
        if any(word in message_lower for word in ['fix', 'remediate', 'patch', 'how to resolve']):
            return QueryType.REMEDIATION_REQUEST
        
        # Code generation patterns
        if any(word in message_lower for word in ['generate', 'script', 'code', 'automate']):
            return QueryType.CODE_GENERATION
        
        # Report generation patterns
        if any(word in message_lower for word in ['report', 'summary', 'export', 'generate report']):
            return QueryType.REPORT_GENERATION
        
        # Compliance check patterns
        if any(word in message_lower for word in ['compliance', 'regulation', 'standard', 'pci', 'hipaa', 'gdpr']):
            return QueryType.COMPLIANCE_CHECK
        
        # System status patterns
        if any(word in message_lower for word in ['status', 'health', 'metrics', 'dashboard']):
            return QueryType.SYSTEM_STATUS
        
        # Default to general question
        return QueryType.GENERAL_QUESTION
    
    def _get_conversation_context(self, query: Query) -> List[Dict[str, str]]:
        """
        Retrieve conversation context for LLM
        
        Returns recent message history formatted for LLM
        """
        if not self.context_manager:
            return []
        
        try:
            # Get recent conversation history
            context = self.context_manager.get_context(
                query.user_id,
                query.session_id
            )
            
            if not context:
                return []
            
            # Format as LLM messages
            messages = []
            for msg in context.messages[-10:]:  # Last 10 messages
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            return messages
            
        except Exception as e:
            self.logger.warning(f"Failed to get conversation context: {e}")
            return []
    
    def _build_system_prompt(self, query: Query) -> str:
        """
        Build system prompt based on access level and query type
        
        Different access levels get different system prompts
        """
        # Base system prompt
        base_prompt = """You are Enterprise Scanner AI Copilot, an expert security assistant.

You help users understand security vulnerabilities, analyze scan results, and provide remediation guidance.

Key principles:
- Be precise and actionable
- Explain technical concepts in plain English
- Prioritize by risk and impact
- Cite sources when possible
- If unsure, say so rather than guess

"""
        
        # Add access level specific instructions
        access_level = query.access_level or 'customer'
        
        if access_level == 'public':
            base_prompt += """
Your audience: Website visitors (non-customers)
- Answer general security questions
- Explain product features
- Don't access scan data or customer information
- Encourage them to sign up for full features
"""
        
        elif access_level == 'customer':
            base_prompt += """
Your audience: Paying customers
- Analyze their scan results in detail
- Explain vulnerabilities found in their systems
- Provide step-by-step remediation guidance
- Access their scan history and context
- Be technical but clear
"""
        
        elif access_level == 'admin':
            base_prompt += """
Your audience: System administrators
- Provide deep technical analysis
- System configuration guidance
- Performance optimization advice
- User management assistance
- Full platform access
"""
        
        elif access_level == 'military':
            base_prompt += """
Your audience: Advanced security professionals
- Autonomous threat response capabilities
- Predictive threat intelligence
- Advanced exploit analysis
- Command and control operations
- Full system authority
"""
        
        # Add query type specific instructions
        if query.query_type == QueryType.SCAN_ANALYSIS:
            base_prompt += """
CURRENT TASK: Scan result analysis
- Review scan findings systematically
- Prioritize by CVSS score and exploitability
- Identify attack paths and critical assets
- Provide executive summary + technical details
"""
        
        elif query.query_type == QueryType.VULNERABILITY_EXPLANATION:
            base_prompt += """
CURRENT TASK: Vulnerability explanation
- Explain what the vulnerability is in plain English
- Describe potential impact on their systems
- Explain why it's rated as critical/high/medium/low
- Provide real-world attack scenarios
- Link to remediation steps
"""
        
        elif query.query_type == QueryType.REMEDIATION_REQUEST:
            base_prompt += """
CURRENT TASK: Remediation guidance
- Provide step-by-step fix instructions
- Include code examples and commands
- Warn about potential impacts
- Suggest testing procedures
- Provide rollback steps if needed
"""
        
        return base_prompt.strip()
    
    def _route_query(
        self,
        query: Query,
        system_prompt: str,
        conversation_context: List[Dict[str, str]]
    ) -> str:
        """
        Route query to appropriate handler
        
        Can route to:
        - Direct LLM response
        - Specialized modules (ScanAnalyzer, ThreatExplainer, etc.)
        - Knowledge base retrieval (RAG)
        - Phase 2: Third-party integrations (SIEM, Ticketing, Communication)
        """
        try:
            # Phase 2: Route integration queries to specialized handlers
            if query.query_type == QueryType.SEND_TO_SIEM:
                # Extract finding data from query metadata or context
                finding_data = query.metadata.get('finding_data', {
                    'title': 'Security Finding',
                    'description': query.message,
                    'severity': query.metadata.get('severity', 'medium')
                })
                return self._handle_siem_alert(query, finding_data)
            
            elif query.query_type == QueryType.CREATE_TICKET:
                # Extract issue data from query metadata or context
                issue_data = query.metadata.get('issue_data', {
                    'title': 'Security Issue from Copilot',
                    'description': query.message,
                    'severity': query.metadata.get('severity', 'medium')
                })
                return self._handle_ticket_creation(query, issue_data)
            
            elif query.query_type == QueryType.SEND_ALERT:
                # Extract alert data from query metadata or context
                alert_data = query.metadata.get('alert_data', {
                    'title': 'Security Alert',
                    'description': query.message,
                    'severity': query.metadata.get('severity', 'medium')
                })
                return self._handle_communication_alert(query, alert_data)
            
            # Default: All other queries go through LLM with RAG enhancement
            
            # Build messages for LLM
            messages = [
                {'role': 'system', 'content': system_prompt}
            ]
            
            # Add conversation history
            messages.extend(conversation_context)
            
            # Add current query
            messages.append({
                'role': 'user',
                'content': query.message
            })
            
            # Call LLM
            response = self.llm.complete(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response['content']
            
        except Exception as e:
            self.logger.error(f"Query routing failed: {e}", exc_info=True)
            
            # Fallback response
            return (
                "I apologize, but I'm having trouble processing your request right now. "
                "Please try again in a moment, or contact support if the issue persists."
            )
    
    def _build_response(
        self,
        query_id: str,
        response_text: str,
        query: Query,
        start_time: float
    ) -> Response:
        """Build response object with metadata"""
        processing_time = int((time.time() - start_time) * 1000)  # milliseconds
        
        # Extract quick replies and suggestions (simple implementation)
        quick_replies = self._generate_quick_replies(query.query_type)
        suggested_actions = self._generate_suggested_actions(response_text)
        
        return Response(
            query_id=query_id,
            response_text=response_text,
            response_format=ResponseFormat.MARKDOWN,
            sources=[],  # Will be populated by RAG module
            citations=[],
            suggested_actions=suggested_actions,
            quick_replies=quick_replies,
            confidence_score=0.85,  # Placeholder
            processing_time_ms=processing_time,
            tokens_used=0,  # Will be tracked by LLM provider
            model_used=self.llm.model
        )
    
    def _generate_quick_replies(self, query_type: QueryType) -> List[str]:
        """Generate contextual quick reply suggestions"""
        quick_replies_map = {
            QueryType.SCAN_ANALYSIS: [
                "Show critical vulnerabilities",
                "Generate executive summary",
                "Compare to previous scan"
            ],
            QueryType.VULNERABILITY_EXPLANATION: [
                "How do I fix this?",
                "Show affected assets",
                "Check if exploit exists"
            ],
            QueryType.REMEDIATION_REQUEST: [
                "Generate patching script",
                "Test the fix",
                "Create WAF rule"
            ],
            QueryType.GENERAL_QUESTION: [
                "Tell me more",
                "Show examples",
                "Related topics"
            ],
            # Phase 2: Integration quick replies
            QueryType.SEND_TO_SIEM: [
                "Send to Splunk",
                "Send to QRadar",
                "Send to Sentinel"
            ],
            QueryType.CREATE_TICKET: [
                "Create Jira ticket",
                "Create ServiceNow ticket",
                "Set priority to P1"
            ],
            QueryType.SEND_ALERT: [
                "Send to Slack",
                "Send to Teams",
                "Email security team"
            ]
        }
        
        return quick_replies_map.get(query_type, [])
    
    def _generate_suggested_actions(self, response_text: str) -> List[str]:
        """Generate suggested actions from response"""
        # Simple implementation - could be enhanced with NLP
        actions = []
        
        if 'patch' in response_text.lower():
            actions.append("Generate patching script")
        
        if 'critical' in response_text.lower():
            actions.append("Escalate to security team")
        
        if 'scan' in response_text.lower():
            actions.append("Run new scan")
        
        return actions[:3]  # Limit to 3 actions
    
    # ==========================================
    # Phase 2: Third-Party Integration Handlers
    # ==========================================
    
    def _handle_siem_alert(self, query: Query, finding_data: Dict[str, Any]) -> str:
        """
        Send security finding to SIEM (Splunk, QRadar, Sentinel)
        
        Args:
            query: Original query
            finding_data: Security finding/alert data to send
            
        Returns:
            Response message
        """
        if not self.integrations_available:
            return "SIEM integration not available. Please configure integration modules."
        
        try:
            # Extract SIEM target from query or use default
            siem_target = self._extract_siem_target(query.message)
            
            # Send to SIEM
            result = self.siem_integration.send_alert(
                finding=finding_data,
                target=siem_target,
                severity=finding_data.get('severity', 'medium'),
                source='enterprise_scanner_copilot',
                metadata={
                    'query_id': query.query_id,
                    'user_id': query.user_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            self.stats['siem_alerts_sent'] += 1
            
            if result.get('success'):
                return f"✅ Alert sent to {siem_target} successfully!\n\n" \
                       f"Event ID: {result.get('event_id', 'N/A')}\n" \
                       f"Severity: {finding_data.get('severity', 'medium').upper()}\n" \
                       f"Status: {result.get('status', 'Delivered')}"
            else:
                return f"⚠️ Failed to send alert to {siem_target}: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error(f"SIEM integration failed: {e}", exc_info=True)
            return f"❌ Error sending to SIEM: {str(e)}"
    
    def _handle_ticket_creation(self, query: Query, issue_data: Dict[str, Any]) -> str:
        """
        Create ticket in ticketing system (Jira, ServiceNow)
        
        Args:
            query: Original query
            issue_data: Issue/vulnerability data for ticket
            
        Returns:
            Response message with ticket details
        """
        if not self.integrations_available:
            return "Ticketing integration not available. Please configure integration modules."
        
        try:
            # Extract ticketing system from query or use default
            ticket_system = self._extract_ticket_system(query.message)
            
            # Create ticket
            result = self.ticketing_integration.create_ticket(
                title=issue_data.get('title', 'Security Finding from Enterprise Scanner'),
                description=issue_data.get('description', ''),
                priority=self._severity_to_priority(issue_data.get('severity', 'medium')),
                system=ticket_system,
                assignee=issue_data.get('assignee'),
                labels=issue_data.get('labels', ['security', 'vulnerability']),
                metadata={
                    'query_id': query.query_id,
                    'user_id': query.user_id,
                    'source': 'enterprise_scanner_copilot'
                }
            )
            
            self.stats['tickets_created'] += 1
            
            if result.get('success'):
                return f"🎫 Ticket created in {ticket_system} successfully!\n\n" \
                       f"Ticket ID: {result.get('ticket_id', 'N/A')}\n" \
                       f"Priority: {result.get('priority', 'Medium')}\n" \
                       f"Status: {result.get('status', 'Open')}\n" \
                       f"URL: {result.get('url', 'N/A')}"
            else:
                return f"⚠️ Failed to create ticket in {ticket_system}: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error(f"Ticketing integration failed: {e}", exc_info=True)
            return f"❌ Error creating ticket: {str(e)}"
    
    def _handle_communication_alert(self, query: Query, alert_data: Dict[str, Any]) -> str:
        """
        Send alert via communication platform (Slack, Teams, Email)
        
        Args:
            query: Original query
            alert_data: Alert data to send
            
        Returns:
            Response message
        """
        if not self.integrations_available:
            return "Communication integration not available. Please configure integration modules."
        
        try:
            # Extract communication platform from query or use default
            platform = self._extract_communication_platform(query.message)
            
            # Prepare alert message
            alert_message = self._format_alert_message(alert_data)
            
            # Send alert
            result = self.communication_integration.send_alert(
                message=alert_message,
                platform=platform,
                severity=alert_data.get('severity', 'medium'),
                channel=alert_data.get('channel', 'security-alerts'),
                recipients=alert_data.get('recipients', []),
                metadata={
                    'query_id': query.query_id,
                    'user_id': query.user_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            self.stats['alerts_sent'] += 1
            
            if result.get('success'):
                return f"📢 Alert sent via {platform} successfully!\n\n" \
                       f"Channel: {result.get('channel', 'N/A')}\n" \
                       f"Recipients: {len(alert_data.get('recipients', []))} people\n" \
                       f"Message ID: {result.get('message_id', 'N/A')}"
            else:
                return f"⚠️ Failed to send alert via {platform}: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error(f"Communication integration failed: {e}", exc_info=True)
            return f"❌ Error sending alert: {str(e)}"
    
    def _extract_siem_target(self, message: str) -> str:
        """Extract SIEM target from user message"""
        message_lower = message.lower()
        if 'splunk' in message_lower:
            return 'splunk'
        elif 'qradar' in message_lower:
            return 'qradar'
        elif 'sentinel' in message_lower:
            return 'sentinel'
        else:
            return 'splunk'  # Default
    
    def _extract_ticket_system(self, message: str) -> str:
        """Extract ticketing system from user message"""
        message_lower = message.lower()
        if 'jira' in message_lower:
            return 'jira'
        elif 'servicenow' in message_lower or 'service now' in message_lower:
            return 'servicenow'
        else:
            return 'jira'  # Default
    
    def _extract_communication_platform(self, message: str) -> str:
        """Extract communication platform from user message"""
        message_lower = message.lower()
        if 'slack' in message_lower:
            return 'slack'
        elif 'teams' in message_lower or 'microsoft teams' in message_lower:
            return 'teams'
        elif 'email' in message_lower:
            return 'email'
        else:
            return 'slack'  # Default
    
    def _severity_to_priority(self, severity: str) -> str:
        """Convert vulnerability severity to ticket priority"""
        severity_map = {
            'critical': 'P1',
            'high': 'P2',
            'medium': 'P3',
            'low': 'P4',
            'info': 'P5'
        }
        return severity_map.get(severity.lower(), 'P3')
    
    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert data into readable message"""
        severity = alert_data.get('severity', 'medium').upper()
        title = alert_data.get('title', 'Security Alert')
        description = alert_data.get('description', 'No description provided')
        
        # Add emoji based on severity
        emoji_map = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '⚡',
            'LOW': 'ℹ️',
            'INFO': '📋'
        }
        emoji = emoji_map.get(severity, '📢')
        
        message = f"{emoji} **{severity} ALERT**\n\n"
        message += f"**{title}**\n\n"
        message += f"{description}\n\n"
        
        if 'affected_assets' in alert_data:
            message += f"**Affected Assets:** {', '.join(alert_data['affected_assets'])}\n"
        
        if 'recommended_action' in alert_data:
            message += f"**Recommended Action:** {alert_data['recommended_action']}\n"
        
        return message
    
    # ==========================================
    # End Phase 2 Integration Handlers
    # ==========================================
    
    def _update_context(self, query: Query, response: Response):
        """Update conversation context"""
        if not self.context_manager:
            return
        
        try:
            self.context_manager.update_context(
                user_id=query.user_id,
                session_id=query.session_id,
                user_message=query.message,
                assistant_response=response.response_text,
                query_type=query.query_type.value
            )
        except Exception as e:
            self.logger.warning(f"Failed to update context: {e}")
    
    def _log_interaction(self, query: Query, response: Response):
        """Log interaction for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query_id': query.query_id,
            'user_id': query.user_id,
            'session_id': query.session_id,
            'query_type': query.query_type.value,
            'access_level': query.access_level,
            'processing_time_ms': response.processing_time_ms,
            'tokens_used': response.tokens_used,
            'error': response.error
        }
        
        self.logger.info(f"Query processed: {json.dumps(log_entry)}")
        
        # Could also write to database for long-term storage
    
    def _create_error_response(self, query_id: str, error_message: str) -> Response:
        """Create error response"""
        return Response(
            query_id=query_id,
            response_text="I apologize, but I encountered an error processing your request.",
            error=error_message,
            fallback_used=True
        )
    
    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        return f"query_{int(time.time() * 1000)}_{self.stats['total_queries']}"
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate session ID"""
        return f"session_{user_id}_{int(time.time())}"
    
    def _get_user_access_level(self, user_id: str) -> str:
        """Get user's access level (placeholder)"""
        # In production, would query user database
        return "customer"
    
    def _query_type_to_feature(self, query_type: QueryType) -> str:
        """Map query type to feature name for access control"""
        feature_map = {
            QueryType.GENERAL_QUESTION: 'general_questions',
            QueryType.SCAN_ANALYSIS: 'scan_analysis',
            QueryType.VULNERABILITY_EXPLANATION: 'vulnerability_explanation',
            QueryType.THREAT_LOOKUP: 'threat_intelligence',
            QueryType.REMEDIATION_REQUEST: 'remediation_guidance',
            QueryType.CODE_GENERATION: 'code_generation',
            QueryType.REPORT_GENERATION: 'report_generation',
            QueryType.COMPLIANCE_CHECK: 'compliance_check',
            QueryType.SYSTEM_STATUS: 'system_status'
        }
        return feature_map.get(query_type, 'general_questions')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        if self.stats['successful_queries'] > 0:
            self.stats['average_response_time_ms'] = (
                self.stats.get('total_response_time_ms', 0) /
                self.stats['successful_queries']
            )
        
        return self.stats.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """System health check"""
        health = {
            'status': 'healthy',
            'llm_provider': self.llm.provider,
            'model': self.llm.model,
            'components': {
                'access_control': self.access_control is not None,
                'context_manager': self.context_manager is not None,
                'analytics': self.analytics_available,  # Phase 1
                'compliance': self.compliance_available,  # Phase 1
                'integrations': self.integrations_available,  # Phase 2
            },
            'phase2_integrations': {
                'siem': self.integrations_available,
                'ticketing': self.integrations_available,
                'communication': self.integrations_available
            } if self.integrations_available else {},
            'stats': self.get_stats()
        }
        
        return health


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("COPILOT ENGINE - MODULE 1")
    print("="*70)
    
    # Initialize engine
    print("\n1. Initializing Copilot Engine...")
    engine = CopilotEngine(
        llm_provider="openai",
        model="gpt-4-turbo",
        temperature=0.7
    )
    
    # Health check
    print("\n2. Health Check:")
    health = engine.health_check()
    print(json.dumps(health, indent=2))
    
    # Process sample query
    print("\n3. Processing Sample Query:")
    response = engine.process_query(
        user_id="user_123",
        message="What is SQL injection and how dangerous is it?",
        access_level="customer"
    )
    
    print(f"\nQuery ID: {response.query_id}")
    print(f"Processing Time: {response.processing_time_ms}ms")
    print(f"Model Used: {response.model_used}")
    print(f"\nResponse:\n{response.response_text}")
    
    if response.quick_replies:
        print(f"\nQuick Replies: {', '.join(response.quick_replies)}")
    
    # Get statistics
    print("\n4. Engine Statistics:")
    stats = engine.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("MODULE 1 COMPLETE ✅")
    print("="*70)
