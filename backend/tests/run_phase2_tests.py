"""
Phase 2 Integration Test Runner (No pytest required)

Simple test runner for Jupiter Phase 2 features.

Author: Enterprise Scanner Team
Version: 1.0.0
Date: October 18, 2025
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
try:
    from ai_copilot.core.copilot_engine import CopilotEngine, Query, QueryType
    from ai_copilot.analysis.remediation_advisor import RemediationAdvisor
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"❌ Import failed: {e}")
    IMPORTS_SUCCESSFUL = False


class TestRunner:
    """Simple test runner"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
    
    def assert_equal(self, actual, expected, message=""):
        """Assert equality"""
        if actual != expected:
            raise AssertionError(f"{message}\nExpected: {expected}\nActual: {actual}")
    
    def assert_true(self, condition, message=""):
        """Assert true"""
        if not condition:
            raise AssertionError(f"{message}\nCondition was False")
    
    def assert_in(self, item, container, message=""):
        """Assert item in container"""
        if item not in container:
            raise AssertionError(f"{message}\n'{item}' not in {container}")
    
    def assert_not_none(self, value, message=""):
        """Assert not None"""
        if value is None:
            raise AssertionError(f"{message}\nValue was None")
    
    def run_test(self, test_func, test_name):
        """Run single test"""
        self.tests_run += 1
        try:
            test_func()
            self.tests_passed += 1
            print(f"  ✅ {test_name}")
            return True
        except Exception as e:
            self.tests_failed += 1
            self.failures.append((test_name, str(e)))
            print(f"  ❌ {test_name}: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failures:
            print("\n" + "-"*80)
            print("FAILURES:")
            print("-"*80)
            for test_name, error in self.failures:
                print(f"\n{test_name}:")
                print(f"  {error}")
        
        print("\n" + "="*80)
        return self.tests_failed == 0


def test_query_types_count(runner):
    """Test total query types = 30"""
    query_types = list(QueryType)
    runner.assert_equal(len(query_types), 30, "Should have 30 query types")


def test_remediation_query_detection(runner):
    """Test remediation query type detection"""
    engine = CopilotEngine()
    
    test_cases = [
        ("generate script for CVE-2024-1234", QueryType.GENERATE_SCRIPT),
        ("create config file for nginx", QueryType.GENERATE_CONFIG),
        ("automate patching", QueryType.AUTOMATE_PATCH),
        ("test the remediation", QueryType.TEST_REMEDIATION),
    ]
    
    for query_text, expected_type in test_cases:
        detected = engine._detect_query_type(query_text)
        runner.assert_equal(detected, expected_type, f"Query: '{query_text}'")


def test_integration_query_detection(runner):
    """Test integration query type detection"""
    engine = CopilotEngine()
    
    test_cases = [
        ("send to splunk", QueryType.SEND_TO_SIEM),
        ("create jira ticket", QueryType.CREATE_TICKET),
        ("send alert to slack", QueryType.SEND_ALERT),
    ]
    
    for query_text, expected_type in test_cases:
        detected = engine._detect_query_type(query_text)
        runner.assert_equal(detected, expected_type, f"Query: '{query_text}'")


def test_siem_target_extraction(runner):
    """Test SIEM target detection"""
    engine = CopilotEngine()
    
    runner.assert_equal(engine._extract_siem_target("send to splunk"), "splunk")
    runner.assert_equal(engine._extract_siem_target("forward to qradar"), "qradar")
    runner.assert_equal(engine._extract_siem_target("send to sentinel"), "sentinel")


def test_ticket_system_extraction(runner):
    """Test ticketing system detection"""
    engine = CopilotEngine()
    
    runner.assert_equal(engine._extract_ticket_system("create jira ticket"), "jira")
    runner.assert_equal(engine._extract_ticket_system("open servicenow ticket"), "servicenow")


def test_communication_platform_extraction(runner):
    """Test communication platform detection"""
    engine = CopilotEngine()
    
    runner.assert_equal(engine._extract_communication_platform("send to slack"), "slack")
    runner.assert_equal(engine._extract_communication_platform("notify teams"), "teams")
    runner.assert_equal(engine._extract_communication_platform("email alert"), "email")


def test_severity_to_priority(runner):
    """Test severity to priority mapping"""
    engine = CopilotEngine()
    
    runner.assert_equal(engine._severity_to_priority("critical"), "P1")
    runner.assert_equal(engine._severity_to_priority("high"), "P2")
    runner.assert_equal(engine._severity_to_priority("medium"), "P3")
    runner.assert_equal(engine._severity_to_priority("low"), "P4")


def test_alert_message_formatting(runner):
    """Test alert message formatting"""
    engine = CopilotEngine()
    
    alert_data = {
        'title': 'Critical Alert',
        'description': 'Test message',
        'severity': 'critical'
    }
    
    message = engine._format_alert_message(alert_data)
    
    runner.assert_in('CRITICAL', message)
    runner.assert_in('🚨', message)
    runner.assert_in('Critical Alert', message)


def test_remediation_advisor_initialization(runner):
    """Test RemediationAdvisor Phase 2 features"""
    advisor = RemediationAdvisor()
    
    runner.assert_true(hasattr(advisor, 'generators_enabled'))
    runner.assert_in('phase2_scripts_generated', advisor.stats)
    runner.assert_in('phase2_configs_generated', advisor.stats)


def test_remediation_plan_generation(runner):
    """Test remediation plan generation"""
    advisor = RemediationAdvisor()
    
    plan = advisor.generate_remediation_plan(
        vulnerability_name="SQL Injection",
        vulnerability_details={'vuln_id': 'TEST-001', 'severity': 'critical'},
        asset_info={'platform': 'linux', 'hostname': 'web01'},
        include_scripts=False  # Don't generate scripts to avoid LLM calls
    )
    
    runner.assert_not_none(plan)
    runner.assert_true(len(plan.steps) > 0)


def test_config_type_inference(runner):
    """Test config type inference"""
    advisor = RemediationAdvisor()
    
    config_type = advisor._infer_config_type("SSH configuration", {'service': 'sshd'})
    runner.assert_equal(config_type, 'ssh')


def test_hardening_level_mapping(runner):
    """Test hardening level mapping"""
    advisor = RemediationAdvisor()
    
    runner.assert_equal(advisor._severity_to_hardening_level('critical'), 'maximum')
    runner.assert_equal(advisor._severity_to_hardening_level('medium'), 'moderate')


def test_health_check_structure(runner):
    """Test health check includes Phase 2"""
    engine = CopilotEngine()
    health = engine.health_check()
    
    runner.assert_in('status', health)
    runner.assert_in('components', health)
    runner.assert_in('integrations', health['components'])
    runner.assert_in('stats', health)


def test_statistics_include_phase2(runner):
    """Test statistics include Phase 2 metrics"""
    engine = CopilotEngine()
    stats = engine.get_stats()
    
    runner.assert_in('siem_alerts_sent', stats)
    runner.assert_in('tickets_created', stats)
    runner.assert_in('alerts_sent', stats)


def test_siem_handler_exists(runner):
    """Test SIEM handler method exists"""
    engine = CopilotEngine()
    
    runner.assert_true(hasattr(engine, '_handle_siem_alert'))
    runner.assert_true(callable(engine._handle_siem_alert))


def test_ticket_handler_exists(runner):
    """Test ticket handler method exists"""
    engine = CopilotEngine()
    
    runner.assert_true(hasattr(engine, '_handle_ticket_creation'))
    runner.assert_true(callable(engine._handle_ticket_creation))


def test_alert_handler_exists(runner):
    """Test alert handler method exists"""
    engine = CopilotEngine()
    
    runner.assert_true(hasattr(engine, '_handle_communication_alert'))
    runner.assert_true(callable(engine._handle_communication_alert))


def test_query_routing_integration(runner):
    """Test query routing handles integration types"""
    engine = CopilotEngine()
    
    query = Query(
        query_id="test_001",
        user_id="admin",
        session_id="session_001",
        message="send to splunk",
        query_type=QueryType.SEND_TO_SIEM,
        metadata={'severity': 'high'}
    )
    
    # Should not raise exception
    try:
        response = engine._route_query(query, "System prompt", [])
        runner.assert_not_none(response)
    except Exception as e:
        raise AssertionError(f"Query routing failed: {e}")


def main():
    """Run all tests"""
    print("="*80)
    print("JUPITER PHASE 2 - INTEGRATION TESTS")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    if not IMPORTS_SUCCESSFUL:
        print("\n❌ IMPORTS FAILED - Cannot run tests")
        return 1
    
    runner = TestRunner()
    
    # Query Type Tests
    print("\n📋 Query Type Detection Tests:")
    runner.run_test(lambda: test_query_types_count(runner), "Total query types = 30")
    runner.run_test(lambda: test_remediation_query_detection(runner), "Remediation query detection")
    runner.run_test(lambda: test_integration_query_detection(runner), "Integration query detection")
    
    # Integration Helper Tests
    print("\n🔧 Integration Helper Tests:")
    runner.run_test(lambda: test_siem_target_extraction(runner), "SIEM target extraction")
    runner.run_test(lambda: test_ticket_system_extraction(runner), "Ticket system extraction")
    runner.run_test(lambda: test_communication_platform_extraction(runner), "Communication platform extraction")
    runner.run_test(lambda: test_severity_to_priority(runner), "Severity to priority mapping")
    runner.run_test(lambda: test_alert_message_formatting(runner), "Alert message formatting")
    
    # RemediationAdvisor Tests
    print("\n🛡️ RemediationAdvisor Phase 2 Tests:")
    runner.run_test(lambda: test_remediation_advisor_initialization(runner), "RemediationAdvisor initialization")
    runner.run_test(lambda: test_remediation_plan_generation(runner), "Remediation plan generation")
    runner.run_test(lambda: test_config_type_inference(runner), "Config type inference")
    runner.run_test(lambda: test_hardening_level_mapping(runner), "Hardening level mapping")
    
    # System Tests
    print("\n⚙️ System Integration Tests:")
    runner.run_test(lambda: test_health_check_structure(runner), "Health check structure")
    runner.run_test(lambda: test_statistics_include_phase2(runner), "Statistics include Phase 2")
    runner.run_test(lambda: test_siem_handler_exists(runner), "SIEM handler exists")
    runner.run_test(lambda: test_ticket_handler_exists(runner), "Ticket handler exists")
    runner.run_test(lambda: test_alert_handler_exists(runner), "Alert handler exists")
    runner.run_test(lambda: test_query_routing_integration(runner), "Query routing integration")
    
    # Print summary
    success = runner.print_summary()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Phase 2 integration is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review failures above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
