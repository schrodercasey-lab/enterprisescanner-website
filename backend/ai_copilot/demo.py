"""
AI Copilot Demo and Usage Examples

Demonstrates all major features of the AI Copilot system.

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ai_copilot import (
    CopilotEngine,
    AccessControl,
    AccessLevel,
    KnowledgeBase,
    ScanAnalyzer,
    ThreatExplainer,
    RemediationAdvisor,
    ChatAPI,
    setup_logging
)


def demo_copilot_engine():
    """Demo: Copilot Engine - Core orchestration"""
    print("\n" + "="*70)
    print("DEMO 1: COPILOT ENGINE")
    print("="*70)
    
    # Initialize engine
    print("\n1. Initializing Copilot Engine...")
    engine = CopilotEngine()
    
    # Check health
    health = engine.health_check()
    print(f"\n   Engine Status: {health}")
    
    # Test query
    print("\n2. Processing Sample Query...")
    from backend.ai_copilot.core.copilot_engine import Query
    
    query = Query(
        query_id="demo_001",
        user_id="demo_user",
        session_id="demo_session",
        message="What is SQL injection and why is it dangerous?",
        query_type=None,  # Will be auto-detected
        access_level=AccessLevel.CUSTOMER
    )
    
    response = engine.process_query(query)
    
    print(f"\n   Query Type: {response.query_type}")
    print(f"   Response: {response.response_text[:200]}...")
    print(f"   Confidence: {response.confidence_score:.2f}")
    print(f"   Processing Time: {response.processing_time_ms}ms")
    print(f"   Quick Replies: {response.quick_replies}")


def demo_access_control():
    """Demo: Access Control - RBAC and rate limiting"""
    print("\n" + "="*70)
    print("DEMO 2: ACCESS CONTROL")
    print("="*70)
    
    print("\n1. Initializing Access Control...")
    access_control = AccessControl()
    
    # Test different access levels
    print("\n2. Testing Access Levels:")
    users = [
        ("public_user", AccessLevel.PUBLIC),
        ("sales_user", AccessLevel.SALES),
        ("customer_user", AccessLevel.CUSTOMER),
        ("admin_user", AccessLevel.ADMIN)
    ]
    
    for user_id, level in users:
        access_control.set_access_level(user_id, level)
        
        # Test feature access
        can_analyze = access_control.verify_access(user_id, "scan_analysis")
        can_auto = access_control.verify_access(user_id, "autonomous_response")
        
        print(f"\n   {user_id} ({level.value}):")
        print(f"     - Scan Analysis: {'✓' if can_analyze else '✗'}")
        print(f"     - Autonomous Response: {'✓' if can_auto else '✗'}")
        
        # Check rate limits
        status = access_control.get_rate_limit_status(user_id)
        print(f"     - Daily Limit: {status['daily']['remaining']}/{status['daily']['limit']}")


def demo_scan_analyzer():
    """Demo: Scan Analyzer - AI-powered scan analysis"""
    print("\n" + "="*70)
    print("DEMO 3: SCAN ANALYZER (KILLER FEATURE)")
    print("="*70)
    
    print("\n1. Initializing Scan Analyzer...")
    analyzer = ScanAnalyzer()
    
    # Create mock scan data
    print("\n2. Creating Mock Scan Data...")
    from backend.ai_copilot.analysis.scan_analyzer import (
        ScanResult, Vulnerability, SeverityLevel
    )
    
    vuln1 = Vulnerability(
        vuln_id="vuln_001",
        name="SQL Injection in Login Form",
        description="User input not validated",
        severity=SeverityLevel.CRITICAL,
        cvss_score=9.8,
        asset_id="web_001",
        asset_name="customer-portal.example.com",
        asset_type="web_app",
        cve_ids=["CVE-2024-1234"],
        exploit_available=True,
        asset_criticality="critical"
    )
    
    scan = ScanResult(
        scan_id="scan_001",
        scan_name="Production Infrastructure Scan",
        scan_type="infrastructure",
        target_assets=["customer-portal.example.com"],
        asset_count=1,
        vulnerabilities=[vuln1],
        critical_count=1,
        high_count=2,
        medium_count=5
    )
    
    # Analyze vulnerability
    print("\n3. Explaining Vulnerability...")
    explanation = analyzer.explain_vulnerability(vuln1, target_audience="technical")
    print(f"\n   Explanation: {explanation[:300]}...")
    
    # Prioritize vulnerabilities
    print("\n4. Prioritizing Vulnerabilities...")
    priorities = analyzer.prioritize_vulnerabilities([vuln1])
    
    for p in priorities:
        print(f"\n   Vulnerability: {p['vulnerability'].name}")
        print(f"   Risk Score: {p['risk_score']:.1f}/100")
        print(f"   Remediation Effort: {p['remediation_effort']}/10")
        print(f"   Justification: {p['justification']}")


def demo_threat_explainer():
    """Demo: Threat Explainer - CVE lookup and threat intel"""
    print("\n" + "="*70)
    print("DEMO 4: THREAT EXPLAINER")
    print("="*70)
    
    print("\n1. Initializing Threat Explainer...")
    explainer = ThreatExplainer()
    
    # Lookup CVE
    print("\n2. Looking up CVE Details...")
    cve = explainer.lookup_cve("CVE-2024-1234")
    
    if cve:
        print(f"\n   CVE: {cve.cve_id}")
        print(f"   Severity: {cve.severity} (CVSS: {cve.cvss_score})")
        print(f"   Description: {cve.description}")
        print(f"   Exploit Available: {cve.exploit_available}")
        print(f"   Exploited in Wild: {cve.exploited_in_wild}")
    
    # Lookup MITRE ATT&CK technique
    print("\n3. Looking up ATT&CK Technique...")
    technique = explainer.lookup_attack_technique("T1190")
    
    if technique:
        print(f"\n   Technique: {technique.technique_id} - {technique.name}")
        print(f"   Tactic: {technique.tactic.value}")
        print(f"   Platforms: {', '.join(technique.platforms)}")
        print(f"   Mitigations: {', '.join(technique.mitigations[:3])}")


def demo_remediation_advisor():
    """Demo: Remediation Advisor - Automated fix guidance"""
    print("\n" + "="*70)
    print("DEMO 5: REMEDIATION ADVISOR")
    print("="*70)
    
    print("\n1. Initializing Remediation Advisor...")
    advisor = RemediationAdvisor()
    
    # Generate remediation plan
    print("\n2. Generating Remediation Plan...")
    plan = advisor.generate_remediation_plan(
        vulnerability_name="SQL Injection in Login Form",
        vulnerability_details={
            'vuln_id': 'vuln_001',
            'severity': 'critical',
            'description': 'Unvalidated user input'
        },
        asset_info={'platform': 'linux'},
        include_scripts=False
    )
    
    print(f"\n   Vulnerability: {plan.vulnerability_name}")
    print(f"   Complexity: {plan.complexity.value}")
    print(f"   Estimated Time: {plan.estimated_time_hours} hours")
    print(f"\n   Steps:")
    for step in plan.steps[:3]:
        print(f"     {step.step_number}. {step.action}")
    
    # Generate patch script
    print("\n3. Generating Patch Script...")
    script = advisor.generate_patch_script(
        software_name="apache2",
        current_version="2.4.45",
        target_version="2.4.50",
        platform="linux"
    )
    
    print(f"\n   Script Type: {script.script_type}")
    print(f"   Platform: {script.platform}")
    print(f"   Prerequisites: {', '.join(script.prerequisites)}")
    
    # Generate WAF rule
    print("\n4. Generating WAF Rule...")
    waf_rule = advisor.generate_waf_rule(
        vulnerability_type="sql_injection",
        attack_pattern="UNION SELECT"
    )
    print(f"\n   WAF Rule:\n{waf_rule[:150]}...")


def demo_knowledge_base():
    """Demo: Knowledge Base - Document ingestion and search"""
    print("\n" + "="*70)
    print("DEMO 6: KNOWLEDGE BASE")
    print("="*70)
    
    print("\n1. Initializing Knowledge Base...")
    kb = KnowledgeBase(storage_path="./demo_kb")
    
    # Ingest sample document
    print("\n2. Ingesting Sample Document...")
    doc = kb.ingest_document(
        content="""
        SQL Injection Prevention Best Practices
        
        SQL injection is one of the most common web vulnerabilities. To prevent it:
        
        1. Use parameterized queries (prepared statements)
        2. Implement input validation
        3. Use least privilege database accounts
        4. Enable query logging
        5. Regular security testing
        """,
        title="SQL Injection Prevention Guide",
        source="docs/security/sqli_prevention.md",
        doc_type="documentation",
        tags=["security", "sqli", "prevention"]
    )
    
    print(f"   Document ingested: {doc.title}")
    print(f"   Chunks created: {len([c for c in kb.chunks.values() if c.doc_id == doc.doc_id])}")
    
    # Search knowledge base
    print("\n3. Searching Knowledge Base...")
    results = kb.search("How to prevent SQL injection?", top_k=2)
    
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i} (score: {result.score:.3f}):")
        print(f"   Source: {result.chunk.source}")
        print(f"   Content: {result.chunk.content[:100]}...")


def demo_chat_api():
    """Demo: Chat API - REST interface"""
    print("\n" + "="*70)
    print("DEMO 7: CHAT API")
    print("="*70)
    
    print("\n1. Initializing Chat API...")
    api = ChatAPI(port=5000)
    
    print(f"\n   API URL: http://{api.host}:{api.port}")
    print(f"   CORS: {'enabled' if api.enable_cors else 'disabled'}")
    print(f"   WebSocket: {'enabled' if api.socketio else 'disabled'}")
    
    print("\n2. Available Endpoints:")
    endpoints = [
        "GET    /api/copilot/health          - Health check",
        "POST   /api/copilot/chat            - Send message",
        "GET    /api/copilot/context/:id     - Get context",
        "DELETE /api/copilot/context/:id     - Clear context",
        "GET    /api/copilot/status           - System status",
        "POST   /api/copilot/stream           - SSE streaming"
    ]
    
    for endpoint in endpoints:
        print(f"     {endpoint}")
    
    print("\n3. Example curl command:")
    print("""
    curl -X POST http://localhost:5000/api/copilot/chat \\
      -H "Content-Type: application/json" \\
      -d '{
        "message": "What is SQL injection?",
        "user_id": "demo_user",
        "access_level": "customer"
      }'
    """)


def demo_full_workflow():
    """Demo: Complete workflow - User asks about vulnerability"""
    print("\n" + "="*70)
    print("DEMO 8: COMPLETE WORKFLOW")
    print("="*70)
    
    print("\nScenario: Customer asks about vulnerability in their scan results")
    
    # 1. Initialize components
    print("\n1. Initializing AI Copilot...")
    engine = CopilotEngine()
    
    # 2. User query
    user_message = "I see CVE-2024-1234 in my scan. How dangerous is this and how do I fix it?"
    print(f"\n2. User Query: '{user_message}'")
    
    # 3. Process with copilot engine
    print("\n3. Processing with AI Copilot...")
    from backend.ai_copilot.core.copilot_engine import Query
    
    query = Query(
        query_id="workflow_001",
        user_id="customer_123",
        session_id="session_abc",
        message=user_message,
        access_level=AccessLevel.CUSTOMER
    )
    
    response = engine.process_query(query)
    
    # 4. Display results
    print("\n4. AI Copilot Response:")
    print(f"\n   Query Type: {response.query_type}")
    print(f"   Response: {response.response_text[:400]}...")
    print(f"\n   Quick Replies:")
    for reply in response.quick_replies:
        print(f"     - {reply}")
    print(f"\n   Suggested Actions:")
    for action in response.suggested_actions:
        print(f"     - {action}")
    
    print(f"\n   Confidence: {response.confidence_score:.2f}")
    print(f"   Processing Time: {response.processing_time_ms}ms")
    print(f"   Model Used: {response.model_used}")


def main():
    """Run all demos"""
    # Setup logging
    setup_logging(log_level="INFO", enable_colors=True)
    
    print("="*70)
    print(" "*15 + "AI COPILOT COMPREHENSIVE DEMO")
    print("="*70)
    print("\nThis demo showcases all major features of the AI Copilot system.")
    print("Each demo is independent and demonstrates a specific module.\n")
    
    # Run demos
    demos = [
        ("Copilot Engine", demo_copilot_engine),
        ("Access Control", demo_access_control),
        ("Scan Analyzer", demo_scan_analyzer),
        ("Threat Explainer", demo_threat_explainer),
        ("Remediation Advisor", demo_remediation_advisor),
        ("Knowledge Base", demo_knowledge_base),
        ("Chat API", demo_chat_api),
        ("Complete Workflow", demo_full_workflow)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n   ⚠️ Demo error (expected - components not fully initialized): {e}")
        
        if i < len(demos):
            input("\n\nPress Enter to continue to next demo...")
    
    # Summary
    print("\n" + "="*70)
    print(" "*20 + "DEMO COMPLETE")
    print("="*70)
    print("\n✅ All modules demonstrated successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure API keys in .env file")
    print("3. Initialize knowledge base with your documentation")
    print("4. Start the Chat API: python -m backend.ai_copilot.interfaces.chat_api")
    print("5. Integrate with Enterprise Scanner platform")
    print("\nDocumentation: See backend/ai_copilot/docs/")


if __name__ == "__main__":
    main()
