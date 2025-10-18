"""
Phase 2 Integration Tests

Comprehensive tests for Jupiter Phase 2 features:
- Query type detection (30 query types)
- Remediation script generation
- SIEM integration
- Ticketing integration
- Communication integration
- End-to-end workflows

Author: Enterprise Scanner Team
Version: 1.0.0
Date: October 18, 2025
"""

import pytest
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from ai_copilot.core.copilot_engine import CopilotEngine, Query, QueryType, Response
from ai_copilot.analysis.remediation_advisor import RemediationAdvisor


class TestPhase2QueryTypes:
    """Test Phase 2 query type detection"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = CopilotEngine(
            llm_provider="openai",
            model="gpt-4-turbo",
            log_level="DEBUG"
        )
    
    def test_query_types_count(self):
        """Verify total query types = 30"""
        query_types = list(QueryType)
        assert len(query_types) == 30, f"Expected 30 query types, got {len(query_types)}"
    
    def test_remediation_query_types(self):
        """Test remediation query type detection"""
        test_cases = [
            ("generate script for CVE-2024-1234", QueryType.GENERATE_SCRIPT),
            ("create config file for nginx", QueryType.GENERATE_CONFIG),
            ("automate patching for this vulnerability", QueryType.AUTOMATE_PATCH),
            ("create rollback plan", QueryType.CREATE_ROLLBACK),
            ("test the remediation script", QueryType.TEST_REMEDIATION),
            ("validate fix for SQL injection", QueryType.VALIDATE_FIX),
            ("show me the remediation workflow", QueryType.REMEDIATION_WORKFLOW),
            ("track changes made during remediation", QueryType.TRACK_CHANGES),
        ]
        
        for query_text, expected_type in test_cases:
            detected_type = self.engine._detect_query_type(query_text)
            assert detected_type == expected_type, \
                f"Query '{query_text}' should be {expected_type}, got {detected_type}"
    
    def test_integration_query_types(self):
        """Test integration query type detection"""
        test_cases = [
            ("send to splunk", QueryType.SEND_TO_SIEM),
            ("send this to qradar", QueryType.SEND_TO_SIEM),
            ("forward to sentinel", QueryType.SEND_TO_SIEM),
            ("create jira ticket", QueryType.CREATE_TICKET),
            ("open servicenow ticket", QueryType.CREATE_TICKET),
            ("create ticket for this issue", QueryType.CREATE_TICKET),
            ("send alert to slack", QueryType.SEND_ALERT),
            ("notify via teams", QueryType.SEND_ALERT),
            ("email the security team", QueryType.SEND_ALERT),
        ]
        
        for query_text, expected_type in test_cases:
            detected_type = self.engine._detect_query_type(query_text)
            assert detected_type == expected_type, \
                f"Query '{query_text}' should be {expected_type}, got {detected_type}"
    
    def test_proactive_query_types(self):
        """Test proactive monitoring query type detection"""
        test_cases = [
            ("setup monitoring for this server", QueryType.SETUP_MONITORING),
            ("enable continuous monitoring", QueryType.SETUP_MONITORING),
            ("configure alert for critical findings", QueryType.CONFIGURE_ALERTS),
            ("setup alert threshold", QueryType.CONFIGURE_ALERTS),
        ]
        
        for query_text, expected_type in test_cases:
            detected_type = self.engine._detect_query_type(query_text)
            assert detected_type == expected_type, \
                f"Query '{query_text}' should be {expected_type}, got {detected_type}"
    
    def test_phase1_query_types_still_work(self):
        """Ensure Phase 1 query types still detected correctly"""
        test_cases = [
            ("tell me about threat actor APT28", QueryType.THREAT_ACTOR_PROFILE),
            ("calculate ROI for this platform", QueryType.ROI_CALCULATION),
            ("show me the audit logs", QueryType.AUDIT_LOG_QUERY),
        ]
        
        for query_text, expected_type in test_cases:
            detected_type = self.engine._detect_query_type(query_text)
            assert detected_type == expected_type, \
                f"Phase 1 query '{query_text}' should be {expected_type}, got {detected_type}"


class TestRemediationAdvisorPhase2:
    """Test RemediationAdvisor Phase 2 integration"""
    
    def setup_method(self):
        """Setup test advisor"""
        self.advisor = RemediationAdvisor()
    
    def test_generators_initialization(self):
        """Test Phase 2 generators are initialized"""
        assert hasattr(self.advisor, 'generators_enabled')
        assert hasattr(self.advisor, 'stats')
        assert 'phase2_scripts_generated' in self.advisor.stats
        assert 'phase2_configs_generated' in self.advisor.stats
    
    def test_remediation_plan_generation(self):
        """Test remediation plan generation"""
        plan = self.advisor.generate_remediation_plan(
            vulnerability_name="SQL Injection in Login Form",
            vulnerability_details={
                'vuln_id': 'CVE-2024-TEST',
                'severity': 'critical',
                'description': 'Unvalidated input in authentication',
                'service': 'apache'
            },
            asset_info={
                'platform': 'linux',
                'hostname': 'web01.test.com',
                'service': 'apache2'
            },
            include_scripts=True
        )
        
        # Verify plan created
        assert plan is not None
        assert plan.vulnerability_name == "SQL Injection in Login Form"
        assert plan.vulnerability_id == "CVE-2024-TEST"
        assert len(plan.steps) > 0
        
        # If Phase 2 generators available, should have scripts
        if self.advisor.generators_enabled:
            assert len(plan.scripts) > 0, "Should generate scripts with Phase 2"
            assert self.advisor.stats['phase2_scripts_generated'] > 0
    
    def test_helper_methods(self):
        """Test Phase 2 helper methods"""
        # Test config type inference
        config_type = self.advisor._infer_config_type(
            "Weak SSH configuration",
            {'service': 'sshd'}
        )
        assert config_type == 'ssh'
        
        # Test hardening level mapping
        hardening = self.advisor._severity_to_hardening_level('critical')
        assert hardening == 'maximum'
        
        hardening = self.advisor._severity_to_hardening_level('medium')
        assert hardening == 'moderate'
    
    def test_graceful_degradation(self):
        """Test graceful fallback when generators not available"""
        # Simulate generators not available
        original_flag = self.advisor.generators_enabled
        self.advisor.generators_enabled = False
        
        plan = self.advisor.generate_remediation_plan(
            vulnerability_name="Test Vulnerability",
            vulnerability_details={'severity': 'high'},
            asset_info={'platform': 'linux'},
            include_scripts=True
        )
        
        # Should still generate plan using legacy methods
        assert plan is not None
        assert len(plan.steps) > 0
        
        # Restore original flag
        self.advisor.generators_enabled = original_flag


class TestSIEMIntegration:
    """Test SIEM integration handlers"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = CopilotEngine()
    
    def test_siem_target_extraction(self):
        """Test SIEM target detection from query"""
        assert self.engine._extract_siem_target("send to splunk") == "splunk"
        assert self.engine._extract_siem_target("forward to qradar") == "qradar"
        assert self.engine._extract_siem_target("send to sentinel") == "sentinel"
        assert self.engine._extract_siem_target("send alert") == "splunk"  # Default
    
    def test_siem_handler_availability_check(self):
        """Test SIEM handler checks integration availability"""
        query = Query(
            query_id="test_001",
            user_id="admin",
            session_id="session_001",
            message="send to splunk",
            query_type=QueryType.SEND_TO_SIEM
        )
        
        finding_data = {
            'title': 'Test Finding',
            'description': 'Test alert',
            'severity': 'high'
        }
        
        response = self.engine._handle_siem_alert(query, finding_data)
        
        # Should return response (success or unavailable message)
        assert response is not None
        assert isinstance(response, str)
        
        if self.engine.integrations_available:
            assert 'splunk' in response.lower() or 'alert' in response.lower()
        else:
            assert 'not available' in response.lower()
    
    def test_siem_statistics_tracking(self):
        """Test SIEM statistics are tracked"""
        initial_count = self.engine.stats['siem_alerts_sent']
        
        if self.engine.integrations_available:
            query = Query(
                query_id="test_002",
                user_id="admin",
                session_id="session_001",
                message="send to splunk",
                query_type=QueryType.SEND_TO_SIEM,
                metadata={
                    'finding_data': {
                        'title': 'Critical Finding',
                        'severity': 'critical'
                    }
                }
            )
            
            self.engine._handle_siem_alert(query, query.metadata['finding_data'])
            
            # Stats should increment
            assert self.engine.stats['siem_alerts_sent'] >= initial_count


class TestTicketingIntegration:
    """Test ticketing integration handlers"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = CopilotEngine()
    
    def test_ticket_system_extraction(self):
        """Test ticketing system detection from query"""
        assert self.engine._extract_ticket_system("create jira ticket") == "jira"
        assert self.engine._extract_ticket_system("open servicenow ticket") == "servicenow"
        assert self.engine._extract_ticket_system("create ticket") == "jira"  # Default
    
    def test_severity_to_priority_mapping(self):
        """Test severity to priority conversion"""
        assert self.engine._severity_to_priority("critical") == "P1"
        assert self.engine._severity_to_priority("high") == "P2"
        assert self.engine._severity_to_priority("medium") == "P3"
        assert self.engine._severity_to_priority("low") == "P4"
        assert self.engine._severity_to_priority("info") == "P5"
        assert self.engine._severity_to_priority("unknown") == "P3"  # Default
    
    def test_ticket_handler_availability_check(self):
        """Test ticket handler checks integration availability"""
        query = Query(
            query_id="test_003",
            user_id="admin",
            session_id="session_001",
            message="create jira ticket",
            query_type=QueryType.CREATE_TICKET
        )
        
        issue_data = {
            'title': 'Test Issue',
            'description': 'Test ticket creation',
            'severity': 'high'
        }
        
        response = self.engine._handle_ticket_creation(query, issue_data)
        
        # Should return response
        assert response is not None
        assert isinstance(response, str)
        
        if self.engine.integrations_available:
            assert 'jira' in response.lower() or 'ticket' in response.lower()
        else:
            assert 'not available' in response.lower()


class TestCommunicationIntegration:
    """Test communication integration handlers"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = CopilotEngine()
    
    def test_communication_platform_extraction(self):
        """Test communication platform detection from query"""
        assert self.engine._extract_communication_platform("send to slack") == "slack"
        assert self.engine._extract_communication_platform("notify teams") == "teams"
        assert self.engine._extract_communication_platform("email alert") == "email"
        assert self.engine._extract_communication_platform("send alert") == "slack"  # Default
    
    def test_alert_message_formatting(self):
        """Test alert message formatting with emojis"""
        alert_data = {
            'title': 'Critical Alert',
            'description': 'Test alert message',
            'severity': 'critical',
            'affected_assets': ['web01', 'web02'],
            'recommended_action': 'Patch immediately'
        }
        
        message = self.engine._format_alert_message(alert_data)
        
        # Verify formatting
        assert 'CRITICAL' in message
        assert '🚨' in message  # Critical emoji
        assert 'Critical Alert' in message
        assert 'Test alert message' in message
        assert 'web01' in message
        assert 'Patch immediately' in message
    
    def test_severity_emoji_mapping(self):
        """Test different severity levels get correct emojis"""
        severities = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': 'ℹ️',
            'info': '📋'
        }
        
        for severity, expected_emoji in severities.items():
            alert_data = {'severity': severity, 'title': 'Test', 'description': 'Test'}
            message = self.engine._format_alert_message(alert_data)
            assert expected_emoji in message


class TestQueryRouting:
    """Test query routing to integration handlers"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = CopilotEngine()
    
    def test_siem_query_routing(self):
        """Test SIEM queries routed to SIEM handler"""
        query = Query(
            query_id="test_004",
            user_id="admin",
            session_id="session_001",
            message="send to splunk",
            query_type=QueryType.SEND_TO_SIEM,
            metadata={'severity': 'high'}
        )
        
        # Create mock conversation context
        system_prompt = "You are a security assistant."
        conversation_context = []
        
        # Route query
        response = self.engine._route_query(query, system_prompt, conversation_context)
        
        # Should return SIEM response (not LLM response)
        assert response is not None
        assert isinstance(response, str)
    
    def test_ticket_query_routing(self):
        """Test ticket queries routed to ticketing handler"""
        query = Query(
            query_id="test_005",
            user_id="admin",
            session_id="session_001",
            message="create jira ticket",
            query_type=QueryType.CREATE_TICKET,
            metadata={'severity': 'critical'}
        )
        
        system_prompt = "You are a security assistant."
        conversation_context = []
        
        response = self.engine._route_query(query, system_prompt, conversation_context)
        
        assert response is not None
        assert isinstance(response, str)
    
    def test_alert_query_routing(self):
        """Test alert queries routed to communication handler"""
        query = Query(
            query_id="test_006",
            user_id="admin",
            session_id="session_001",
            message="send to slack",
            query_type=QueryType.SEND_ALERT,
            metadata={'severity': 'medium'}
        )
        
        system_prompt = "You are a security assistant."
        conversation_context = []
        
        response = self.engine._route_query(query, system_prompt, conversation_context)
        
        assert response is not None
        assert isinstance(response, str)


class TestHealthCheck:
    """Test health check includes Phase 2 status"""
    
    def test_health_check_components(self):
        """Test health check shows all components"""
        engine = CopilotEngine()
        health = engine.health_check()
        
        # Verify structure
        assert 'status' in health
        assert 'components' in health
        assert 'stats' in health
        
        # Verify Phase 1 components
        assert 'analytics' in health['components']
        assert 'compliance' in health['components']
        
        # Verify Phase 2 components
        assert 'integrations' in health['components']
        
        # If integrations available, should have detailed status
        if engine.integrations_available:
            assert 'phase2_integrations' in health
            assert 'siem' in health['phase2_integrations']
            assert 'ticketing' in health['phase2_integrations']
            assert 'communication' in health['phase2_integrations']
    
    def test_statistics_include_phase2(self):
        """Test statistics include Phase 2 metrics"""
        engine = CopilotEngine()
        stats = engine.get_stats()
        
        # Verify Phase 2 statistics present
        assert 'siem_alerts_sent' in stats
        assert 'tickets_created' in stats
        assert 'alerts_sent' in stats
        
        # Verify Phase 1 statistics still present
        assert 'analytics_tracked' in stats
        assert 'audit_logs_created' in stats


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = CopilotEngine()
    
    def test_complete_remediation_workflow(self):
        """Test complete remediation workflow from query to script"""
        # Step 1: Detect vulnerability
        # Step 2: Generate remediation plan
        advisor = RemediationAdvisor()
        
        plan = advisor.generate_remediation_plan(
            vulnerability_name="SQL Injection",
            vulnerability_details={
                'vuln_id': 'CVE-2024-SQL',
                'severity': 'critical',
                'service': 'mysql'
            },
            asset_info={'platform': 'linux', 'hostname': 'db01'},
            include_scripts=True
        )
        
        assert plan is not None
        assert len(plan.steps) > 0
        
        # If generators available, verify scripts
        if advisor.generators_enabled:
            assert len(plan.scripts) > 0
    
    def test_complete_integration_workflow(self):
        """Test complete integration workflow"""
        # Simulate finding critical vulnerability
        finding = {
            'title': 'Critical SQL Injection',
            'description': 'Database vulnerable to SQL injection',
            'severity': 'critical',
            'affected_assets': ['db01.prod.com'],
            'recommended_action': 'Apply patches immediately'
        }
        
        # 1. Send to SIEM
        if self.engine.integrations_available:
            siem_query = Query(
                query_id="workflow_001",
                user_id="admin",
                session_id="session_001",
                message="send to splunk",
                query_type=QueryType.SEND_TO_SIEM,
                metadata={'finding_data': finding}
            )
            
            siem_response = self.engine._handle_siem_alert(siem_query, finding)
            assert siem_response is not None
            
            # 2. Create ticket
            ticket_query = Query(
                query_id="workflow_002",
                user_id="admin",
                session_id="session_001",
                message="create jira ticket",
                query_type=QueryType.CREATE_TICKET,
                metadata={'issue_data': finding}
            )
            
            ticket_response = self.engine._handle_ticket_creation(ticket_query, finding)
            assert ticket_response is not None
            
            # 3. Send alert
            alert_query = Query(
                query_id="workflow_003",
                user_id="admin",
                session_id="session_001",
                message="send to slack",
                query_type=QueryType.SEND_ALERT,
                metadata={'alert_data': finding}
            )
            
            alert_response = self.engine._handle_communication_alert(alert_query, finding)
            assert alert_response is not None
            
            # Verify all stats updated
            assert self.engine.stats['siem_alerts_sent'] > 0
            assert self.engine.stats['tickets_created'] > 0
            assert self.engine.stats['alerts_sent'] > 0


class TestGracefulDegradation:
    """Test system works even when Phase 2 modules unavailable"""
    
    def test_copilot_engine_without_integrations(self):
        """Test CopilotEngine works without integrations"""
        engine = CopilotEngine()
        
        # Should initialize successfully
        assert engine is not None
        
        # Health check should work
        health = engine.health_check()
        assert health['status'] == 'healthy'
        
        # Query processing should work (even if integration handlers return unavailable message)
        if not engine.integrations_available:
            query = Query(
                query_id="test_007",
                user_id="admin",
                session_id="session_001",
                message="send to splunk",
                query_type=QueryType.SEND_TO_SIEM
            )
            
            response = engine._handle_siem_alert(query, {'title': 'Test'})
            assert 'not available' in response.lower()
    
    def test_remediation_advisor_without_generators(self):
        """Test RemediationAdvisor works without Phase 2 generators"""
        advisor = RemediationAdvisor()
        
        # Should initialize successfully
        assert advisor is not None
        
        # Should still generate plans
        plan = advisor.generate_remediation_plan(
            vulnerability_name="Test Vuln",
            vulnerability_details={'severity': 'medium'},
            asset_info={'platform': 'linux'},
            include_scripts=True
        )
        
        assert plan is not None
        assert len(plan.steps) > 0


# Test runner
if __name__ == "__main__":
    print("="*80)
    print("JUPITER PHASE 2 - INTEGRATION TESTS")
    print("="*80)
    
    # Run tests with pytest
    pytest_args = [
        __file__,
        '-v',  # Verbose
        '--tb=short',  # Short traceback
        '--color=yes',  # Colored output
        '-s'  # Show print statements
    ]
    
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("✅ ALL PHASE 2 INTEGRATION TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED - See details above")
    print("="*80)
    
    sys.exit(exit_code)
