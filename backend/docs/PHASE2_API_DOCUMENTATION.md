# Jupiter Phase 2 - API Documentation

**Version**: 1.4.0  
**Date**: October 18, 2025  
**Coverage**: 30 Query Types (17 Phase 1 + 13 Phase 2)

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 2 Query Types](#phase-2-query-types)
3. [Remediation Automation API](#remediation-automation-api)
4. [Integration API](#integration-api)
5. [Proactive Monitoring API](#proactive-monitoring-api)
6. [Response Formats](#response-formats)
7. [Error Handling](#error-handling)
8. [Code Examples](#code-examples)

---

## Overview

Jupiter Phase 2 extends the AI Copilot Engine with **13 new query types** across three major categories:

- **Remediation Automation** (8 types): Automated vulnerability fixing with script/config generation
- **Third-Party Integrations** (3 types): SIEM, Ticketing, and Communication platform integration
- **Proactive Monitoring** (2 types): Continuous monitoring and alert configuration

**Business Value**: +$40K ARPU  
**Total Query Types**: 30  
**Backward Compatible**: ✅ All Phase 1 queries still supported

---

## Phase 2 Query Types

### Remediation Automation (8 Types)

#### 1. GENERATE_SCRIPT
**Purpose**: Generate remediation scripts for vulnerability fixes

**Trigger Patterns**:
- "generate script"
- "create script"
- "remediation script"
- "write script for"
- "automated fix script"

**Query Example**:
```python
query = Query(
    message="Generate a remediation script for SQL injection in our Django app",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "vulnerability_type": "sql_injection",
        "severity": "critical",
        "asset_info": {
            "type": "web_app",
            "framework": "django",
            "language": "python"
        }
    }
)

response = copilot.process_query(query)
```

**Response Format**:
```json
{
  "query_type": "GENERATE_SCRIPT",
  "script": {
    "language": "python",
    "code": "#!/usr/bin/env python3\n# SQL Injection Remediation Script\n...",
    "filename": "remediate_sql_injection.py",
    "description": "Automated script to fix SQL injection vulnerabilities"
  },
  "execution_instructions": [
    "Review the script before execution",
    "Test in staging environment first",
    "Run with: python remediate_sql_injection.py"
  ],
  "rollback_plan": "Script creates automatic backup before changes"
}
```

**Business Value**: Core of +$25K ARPU remediation automation

---

#### 2. GENERATE_CONFIG
**Purpose**: Generate secure configuration files

**Trigger Patterns**:
- "generate config"
- "create config"
- "configuration file"
- "secure config for"
- "hardened configuration"

**Query Example**:
```python
query = Query(
    message="Generate a hardened SSH config for our production servers",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "config_type": "ssh",
        "hardening_level": "maximum",
        "asset_info": {
            "type": "server",
            "os": "linux",
            "environment": "production"
        }
    }
)
```

**Response Format**:
```json
{
  "query_type": "GENERATE_CONFIG",
  "config": {
    "type": "ssh",
    "filename": "sshd_config_hardened",
    "content": "# Hardened SSH Configuration\nPort 22\nPermitRootLogin no\n...",
    "format": "text"
  },
  "security_improvements": [
    "Disabled root login",
    "Enabled key-based authentication only",
    "Set strong cipher suites",
    "Configured connection timeout"
  ],
  "deployment_path": "/etc/ssh/sshd_config",
  "restart_required": true,
  "restart_command": "sudo systemctl restart sshd"
}
```

**Supported Config Types**:
- `ssh`: SSH server hardening
- `firewall`: Firewall rules (iptables, ufw)
- `web_server`: Nginx, Apache security configs
- `database`: PostgreSQL, MySQL secure configs
- `application`: Framework-specific security configs

---

#### 3. AUTOMATE_PATCH
**Purpose**: Automate vulnerability patching process

**Trigger Patterns**:
- "automate patch"
- "automatic patching"
- "deploy patch"
- "auto-fix vulnerability"
- "automated remediation"

**Query Example**:
```python
query = Query(
    message="Automate patching for CVE-2024-1234 across all servers",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "cve_id": "CVE-2024-1234",
        "affected_assets": ["server-1", "server-2", "server-3"],
        "maintenance_window": "2025-10-20T02:00:00Z"
    }
)
```

**Response Format**:
```json
{
  "query_type": "AUTOMATE_PATCH",
  "automation_plan": {
    "patch_id": "PATCH-2024-1234",
    "affected_assets": 3,
    "execution_strategy": "rolling",
    "estimated_duration": "45 minutes",
    "maintenance_window": "2025-10-20T02:00:00Z"
  },
  "steps": [
    {
      "step": 1,
      "action": "Create snapshots",
      "duration": "5 minutes"
    },
    {
      "step": 2,
      "action": "Apply patch to server-1",
      "duration": "10 minutes"
    },
    {
      "step": 3,
      "action": "Verify server-1",
      "duration": "5 minutes"
    }
  ],
  "rollback_available": true,
  "approval_required": false,
  "automation_id": "AUTO-PATCH-456"
}
```

---

#### 4. CREATE_ROLLBACK
**Purpose**: Create rollback points before remediation

**Trigger Patterns**:
- "rollback"
- "create snapshot"
- "backup before"
- "create restore point"
- "save current state"

**Query Example**:
```python
query = Query(
    message="Create a rollback point before applying the database patch",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "asset_id": "db-server-01",
        "asset_type": "database",
        "snapshot_type": "full"
    }
)
```

**Response Format**:
```json
{
  "query_type": "CREATE_ROLLBACK",
  "snapshot": {
    "snapshot_id": "SNAP-2025-10-18-001",
    "created_at": "2025-10-18T14:30:00Z",
    "asset_id": "db-server-01",
    "snapshot_type": "full",
    "size_mb": 2048,
    "retention_days": 30
  },
  "rollback_command": "restore_snapshot SNAP-2025-10-18-001",
  "verification": "Snapshot verified and ready for rollback",
  "storage_location": "s3://backups/snapshots/SNAP-2025-10-18-001"
}
```

---

#### 5. TEST_REMEDIATION
**Purpose**: Test remediation scripts before deployment

**Trigger Patterns**:
- "test remediation"
- "test the remediation"
- "test fix"
- "test script"
- "validate script"
- "dry run"

**Query Example**:
```python
query = Query(
    message="Test the remediation script in our staging environment",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "script_id": "SCRIPT-123",
        "environment": "staging",
        "test_mode": "dry_run"
    }
)
```

**Response Format**:
```json
{
  "query_type": "TEST_REMEDIATION",
  "test_results": {
    "test_id": "TEST-2025-10-18-001",
    "status": "passed",
    "environment": "staging",
    "tests_run": 15,
    "tests_passed": 15,
    "tests_failed": 0,
    "duration_seconds": 45
  },
  "detailed_results": [
    {
      "test": "Syntax validation",
      "result": "passed"
    },
    {
      "test": "Dependency check",
      "result": "passed"
    },
    {
      "test": "Dry run execution",
      "result": "passed"
    }
  ],
  "ready_for_production": true,
  "recommendation": "Script is safe to deploy to production"
}
```

---

#### 6. VALIDATE_FIX
**Purpose**: Verify vulnerability is fixed after remediation

**Trigger Patterns**:
- "validate fix"
- "verify fix"
- "check if fixed"
- "confirm remediation"
- "has the issue been resolved"

**Query Example**:
```python
query = Query(
    message="Validate that the SQL injection vulnerability is fixed",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "vulnerability_id": "VULN-123",
        "remediation_id": "REM-456",
        "asset_id": "web-app-01"
    }
)
```

**Response Format**:
```json
{
  "query_type": "VALIDATE_FIX",
  "validation": {
    "vulnerability_id": "VULN-123",
    "status": "fixed",
    "verified_at": "2025-10-18T14:35:00Z",
    "validation_method": "automated_scan",
    "confidence": 0.98
  },
  "verification_tests": [
    {
      "test": "SQL injection payload test",
      "result": "blocked",
      "details": "All malicious payloads properly sanitized"
    },
    {
      "test": "Parameterized query check",
      "result": "passed",
      "details": "All queries now use parameterized statements"
    }
  ],
  "residual_risk": "none",
  "recommendation": "Vulnerability successfully remediated. Close ticket."
}
```

---

#### 7. REMEDIATION_WORKFLOW
**Purpose**: Get complete remediation workflow for complex vulnerabilities

**Trigger Patterns**:
- "remediation workflow"
- "fix workflow"
- "remediation process"
- "step-by-step fix"
- "complete remediation plan"

**Query Example**:
```python
query = Query(
    message="Show me the complete remediation workflow for the XSS vulnerability",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "vulnerability_id": "VULN-789",
        "vulnerability_type": "xss",
        "severity": "high"
    }
)
```

**Response Format**:
```json
{
  "query_type": "REMEDIATION_WORKFLOW",
  "workflow": {
    "workflow_id": "WORKFLOW-2025-10-18-001",
    "vulnerability_type": "xss",
    "total_steps": 6,
    "estimated_duration": "2 hours"
  },
  "steps": [
    {
      "step": 1,
      "phase": "Preparation",
      "action": "Create rollback point",
      "duration": "10 minutes",
      "automated": true
    },
    {
      "step": 2,
      "phase": "Analysis",
      "action": "Identify all XSS injection points",
      "duration": "20 minutes",
      "automated": true
    },
    {
      "step": 3,
      "phase": "Remediation",
      "action": "Generate sanitization script",
      "duration": "30 minutes",
      "automated": true
    },
    {
      "step": 4,
      "phase": "Testing",
      "action": "Test in staging environment",
      "duration": "30 minutes",
      "automated": true
    },
    {
      "step": 5,
      "phase": "Deployment",
      "action": "Deploy to production",
      "duration": "20 minutes",
      "automated": false,
      "approval_required": true
    },
    {
      "step": 6,
      "phase": "Validation",
      "action": "Verify fix effectiveness",
      "duration": "10 minutes",
      "automated": true
    }
  ],
  "automation_level": "semi_auto",
  "approval_points": [5]
}
```

---

#### 8. TRACK_CHANGES
**Purpose**: Track all remediation changes for audit trail

**Trigger Patterns**:
- "track changes"
- "change log"
- "change history"
- "audit trail"
- "what was changed"

**Query Example**:
```python
query = Query(
    message="Show me the change history for the database server remediation",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "asset_id": "db-server-01",
        "time_range": "last_7_days"
    }
)
```

**Response Format**:
```json
{
  "query_type": "TRACK_CHANGES",
  "changes": [
    {
      "change_id": "CHG-001",
      "timestamp": "2025-10-18T10:00:00Z",
      "type": "configuration",
      "asset": "db-server-01",
      "description": "Applied hardened PostgreSQL configuration",
      "performed_by": "automation_engine",
      "files_modified": ["/etc/postgresql/postgresql.conf"],
      "rollback_available": true
    },
    {
      "change_id": "CHG-002",
      "timestamp": "2025-10-17T15:30:00Z",
      "type": "patch",
      "asset": "db-server-01",
      "description": "Installed security patch CVE-2024-5678",
      "performed_by": "automation_engine",
      "version_before": "14.2",
      "version_after": "14.3",
      "rollback_available": true
    }
  ],
  "total_changes": 2,
  "blockchain_verified": true,
  "audit_trail_url": "https://audit.jupiter.com/changes/db-server-01"
}
```

---

### Third-Party Integrations (3 Types)

#### 9. SEND_TO_SIEM
**Purpose**: Send security findings to SIEM platforms

**Trigger Patterns**:
- "send to siem"
- "send to splunk"
- "send to qradar"
- "send to sentinel"
- "forward to siem"

**Supported Platforms**:
- Splunk
- IBM QRadar
- Microsoft Sentinel
- (Auto-detected from query or configuration)

**Query Example**:
```python
query = Query(
    message="Send this critical vulnerability to Splunk",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "finding_data": {
            "title": "Critical SQL Injection Detected",
            "severity": "critical",
            "description": "SQL injection in user login endpoint",
            "affected_asset": "web-app-01",
            "cve_id": "CVE-2024-1234",
            "cvss_score": 9.8
        }
    }
)
```

**Response Format**:
```json
{
  "query_type": "SEND_TO_SIEM",
  "siem_alert": {
    "platform": "splunk",
    "event_id": "SIEM-EVENT-2025-10-18-001",
    "timestamp": "2025-10-18T14:40:00Z",
    "status": "sent",
    "severity": "critical"
  },
  "finding": {
    "title": "Critical SQL Injection Detected",
    "severity": "critical",
    "affected_asset": "web-app-01",
    "cvss_score": 9.8
  },
  "siem_url": "https://splunk.company.com/en-US/app/search/SIEM-EVENT-2025-10-18-001",
  "indexed": true,
  "correlation_id": "CORR-123456"
}
```

**Integration Setup**: See [SIEM Integration Guide](./SIEM_INTEGRATION_GUIDE.md)

**Business Value**: +$4K ARPU

---

#### 10. CREATE_TICKET
**Purpose**: Create tickets in ticketing systems

**Trigger Patterns**:
- "create ticket"
- "create jira ticket"
- "create jira"
- "open ticket"
- "create servicenow ticket"

**Supported Platforms**:
- Jira
- ServiceNow
- (Auto-detected from query or configuration)

**Query Example**:
```python
query = Query(
    message="Create a Jira ticket for this high-severity vulnerability",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "issue_data": {
            "title": "Fix XSS Vulnerability in User Profile Page",
            "description": "Cross-site scripting vulnerability detected in user profile editing",
            "severity": "high",
            "affected_component": "user-profile-service",
            "assigned_to": "security-team"
        }
    }
)
```

**Response Format**:
```json
{
  "query_type": "CREATE_TICKET",
  "ticket": {
    "platform": "jira",
    "ticket_id": "SEC-1234",
    "ticket_url": "https://jira.company.com/browse/SEC-1234",
    "status": "created",
    "created_at": "2025-10-18T14:45:00Z"
  },
  "details": {
    "title": "Fix XSS Vulnerability in User Profile Page",
    "priority": "P2",
    "severity": "high",
    "assigned_to": "security-team",
    "project": "SECURITY"
  },
  "next_steps": [
    "Security team notified",
    "Ticket added to current sprint",
    "Estimated fix: 2-3 days"
  ]
}
```

**Priority Mapping**:
- Critical → P1 (Immediate)
- High → P2 (24 hours)
- Medium → P3 (1 week)
- Low → P4 (2 weeks)
- Info → P5 (Backlog)

**Integration Setup**: See [Ticketing Integration Guide](./TICKETING_INTEGRATION_GUIDE.md)

**Business Value**: +$3K ARPU

---

#### 11. SEND_ALERT
**Purpose**: Send alerts to communication platforms

**Trigger Patterns**:
- "send alert"
- "notify"
- "send to slack"
- "send to teams"
- "send email alert"

**Supported Platforms**:
- Slack
- Microsoft Teams
- Email
- (Auto-detected from query or configuration)

**Query Example**:
```python
query = Query(
    message="Send a Slack alert about this critical vulnerability to the security channel",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "alert_data": {
            "title": "🚨 CRITICAL: SQL Injection Detected",
            "description": "Immediate attention required - SQL injection in production app",
            "severity": "critical",
            "affected_assets": ["web-app-01", "api-gateway"],
            "recommended_actions": [
                "Isolate affected systems",
                "Apply emergency patch",
                "Review access logs"
            ]
        }
    }
)
```

**Response Format**:
```json
{
  "query_type": "SEND_ALERT",
  "alert": {
    "platform": "slack",
    "channel": "#security-alerts",
    "message_id": "MSG-2025-10-18-001",
    "timestamp": "2025-10-18T14:50:00Z",
    "status": "sent"
  },
  "message": {
    "title": "🚨 CRITICAL: SQL Injection Detected",
    "severity": "critical",
    "affected_assets": 2,
    "recipients_notified": 15
  },
  "slack_url": "https://company.slack.com/archives/C123456/p1697643000",
  "thread_id": "THREAD-789",
  "reactions": {
    "acknowledged": 5,
    "investigating": 2
  }
}
```

**Severity Emojis**:
- 🚨 Critical
- ⚠️ High
- ⚡ Medium
- ℹ️ Low
- 📌 Info

**Integration Setup**: See [Communication Integration Guide](./COMMUNICATION_INTEGRATION_GUIDE.md)

**Business Value**: +$3K ARPU

---

### Proactive Monitoring (2 Types)

#### 12. SETUP_MONITORING
**Purpose**: Configure continuous monitoring for assets

**Trigger Patterns**:
- "setup monitoring"
- "enable monitoring"
- "start monitoring"
- "configure monitoring"
- "monitor this system"

**Query Example**:
```python
query = Query(
    message="Setup continuous monitoring for our production web servers",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "assets": ["web-server-01", "web-server-02", "web-server-03"],
        "monitoring_type": "continuous",
        "alert_threshold": "medium"
    }
)
```

**Response Format**:
```json
{
  "query_type": "SETUP_MONITORING",
  "monitoring_config": {
    "monitoring_id": "MON-2025-10-18-001",
    "assets": 3,
    "monitoring_type": "continuous",
    "scan_frequency": "hourly",
    "alert_threshold": "medium"
  },
  "monitored_assets": [
    {
      "asset_id": "web-server-01",
      "status": "monitoring_active",
      "next_scan": "2025-10-18T15:00:00Z"
    }
  ],
  "alerts_configured": [
    "New vulnerability detected",
    "Configuration drift",
    "Compliance violation",
    "Unusual network activity"
  ],
  "dashboard_url": "https://jupiter.com/monitoring/MON-2025-10-18-001"
}
```

**Business Value**: Part of +$5K ARPU proactive monitoring

---

#### 13. CONFIGURE_ALERTS
**Purpose**: Configure alert rules and thresholds

**Trigger Patterns**:
- "configure alert"
- "setup alert"
- "alert threshold"
- "alert rules"
- "notification settings"

**Query Example**:
```python
query = Query(
    message="Configure alerts to notify me when any critical vulnerability is detected",
    user_id="user_123",
    session_id="session_456",
    metadata={
        "alert_rule": {
            "name": "Critical Vulnerability Alert",
            "condition": "severity >= critical",
            "notification_channels": ["slack", "email"],
            "frequency": "immediate"
        }
    }
)
```

**Response Format**:
```json
{
  "query_type": "CONFIGURE_ALERTS",
  "alert_rule": {
    "rule_id": "RULE-2025-10-18-001",
    "name": "Critical Vulnerability Alert",
    "status": "active",
    "created_at": "2025-10-18T14:55:00Z"
  },
  "conditions": {
    "severity": "critical",
    "asset_types": "all",
    "time_window": "immediate"
  },
  "notifications": {
    "channels": ["slack", "email"],
    "recipients": 5,
    "frequency": "immediate"
  },
  "test_alert_sent": true,
  "estimated_alerts_per_week": 2
}
```

**Business Value**: Part of +$5K ARPU proactive monitoring

---

## Response Formats

### Standard Response Structure

All Phase 2 queries return a consistent response structure:

```json
{
  "query_id": "string",
  "query_type": "string",
  "timestamp": "ISO8601",
  "user_id": "string",
  "session_id": "string",
  
  // Query-specific data
  "data": { ... },
  
  // Standard metadata
  "metadata": {
    "processing_time_ms": 150,
    "confidence": 0.95,
    "model_used": "gpt-4-turbo"
  },
  
  // Quick actions
  "quick_replies": [
    "View details",
    "Execute now",
    "Schedule for later"
  ]
}
```

---

## Error Handling

### Graceful Degradation

When Phase 2 modules are unavailable, the system gracefully degrades:

```json
{
  "query_type": "SEND_TO_SIEM",
  "status": "module_unavailable",
  "message": "SIEM integration module not configured. Returning informational response.",
  "fallback_response": {
    "recommendation": "To enable SIEM integration, configure your SIEM connection in settings.",
    "documentation": "https://docs.jupiter.com/integrations/siem",
    "finding_data": { ... }
  },
  "health_check": {
    "integrations_available": false,
    "phase2_integrations": {
      "siem": false,
      "ticketing": false,
      "communication": false
    }
  }
}
```

### Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `MODULE_UNAVAILABLE` | Phase 2 module not installed | Install integration module |
| `AUTHENTICATION_FAILED` | Platform credentials invalid | Update credentials in config |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `INVALID_CONFIGURATION` | Missing required config | Check setup guide |
| `PLATFORM_UNAVAILABLE` | Third-party service down | Check platform status |

---

## Code Examples

### Python SDK Example

```python
from ai_copilot import CopilotEngine, Query

# Initialize engine
copilot = CopilotEngine(
    model="gpt-4-turbo",
    enable_analytics=True,
    enable_compliance=True
)

# Example 1: Generate remediation script
query = Query(
    message="Generate a script to fix the SQL injection vulnerability",
    user_id="analyst_01",
    session_id="session_123",
    metadata={
        "vulnerability_type": "sql_injection",
        "severity": "critical",
        "asset_info": {
            "type": "web_app",
            "framework": "django"
        }
    }
)

response = copilot.process_query(query)
print(f"Script generated: {response.data['script']['filename']}")

# Example 2: Send to SIEM
query = Query(
    message="Send this critical finding to Splunk",
    user_id="analyst_01",
    session_id="session_123",
    metadata={
        "finding_data": {
            "title": "Critical Vulnerability",
            "severity": "critical",
            "cvss_score": 9.8
        }
    }
)

response = copilot.process_query(query)
print(f"SIEM Event ID: {response.data['siem_alert']['event_id']}")

# Example 3: Create Jira ticket
query = Query(
    message="Create a high-priority Jira ticket for this vulnerability",
    user_id="analyst_01",
    session_id="session_123",
    metadata={
        "issue_data": {
            "title": "Fix XSS Vulnerability",
            "severity": "high",
            "assigned_to": "security-team"
        }
    }
)

response = copilot.process_query(query)
print(f"Ticket created: {response.data['ticket']['ticket_url']}")
```

### REST API Example

```bash
# Generate remediation script
curl -X POST https://api.jupiter.com/v1/copilot/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate script to fix SQL injection",
    "user_id": "analyst_01",
    "session_id": "session_123",
    "metadata": {
      "vulnerability_type": "sql_injection",
      "severity": "critical"
    }
  }'

# Send to SIEM
curl -X POST https://api.jupiter.com/v1/copilot/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Send to Splunk",
    "user_id": "analyst_01",
    "session_id": "session_123",
    "metadata": {
      "finding_data": {
        "title": "Critical Vulnerability",
        "severity": "critical"
      }
    }
  }'
```

---

## Migration Guide

### Upgrading from Phase 1 to Phase 2

**Backward Compatibility**: ✅ All Phase 1 queries work unchanged

**New Capabilities Available**:
1. Add remediation automation to your workflow
2. Integrate with existing SIEM/Ticketing platforms
3. Enable proactive monitoring

**Recommended Upgrade Path**:
1. **Week 1**: Deploy Phase 2 engine (no configuration needed)
2. **Week 2**: Configure SIEM integration
3. **Week 3**: Configure ticketing integration
4. **Week 4**: Enable proactive monitoring

**No Breaking Changes**: Existing integrations continue working

---

## Performance Considerations

### Query Processing Times

| Query Type | Avg Processing Time | Notes |
|-----------|---------------------|-------|
| GENERATE_SCRIPT | 2-5 seconds | Depends on script complexity |
| GENERATE_CONFIG | 1-3 seconds | Config template generation |
| SEND_TO_SIEM | 0.5-1 second | Network call to SIEM |
| CREATE_TICKET | 0.5-1 second | Network call to ticketing |
| SEND_ALERT | 0.3-0.5 seconds | Fast notification delivery |

### Rate Limits

- **Default**: 100 queries/minute per user
- **Integration calls**: 50 calls/minute per platform
- **Burst**: 200 queries/minute for 30 seconds

---

## Support & Documentation

### Additional Resources

- [SIEM Integration Guide](./SIEM_INTEGRATION_GUIDE.md)
- [Ticketing Integration Guide](./TICKETING_INTEGRATION_GUIDE.md)
- [Communication Integration Guide](./COMMUNICATION_INTEGRATION_GUIDE.md)
- [Remediation Workflow Guide](./REMEDIATION_WORKFLOW_GUIDE.md)
- [Phase 2 Business Value Guide](./PHASE2_BUSINESS_VALUE.md)

### Getting Help

- **Documentation**: https://docs.jupiter.com
- **API Reference**: https://api.jupiter.com/docs
- **Support**: support@jupiter.com
- **Community**: https://community.jupiter.com

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**API Version**: 1.4.0
