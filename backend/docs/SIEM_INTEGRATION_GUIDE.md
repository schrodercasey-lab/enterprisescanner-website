# SIEM Integration Guide - Jupiter Phase 2

**Version**: 1.0  
**Date**: October 18, 2025  
**Supported Platforms**: Splunk, IBM QRadar, Microsoft Sentinel

---

## Table of Contents

1. [Overview](#overview)
2. [Supported SIEM Platforms](#supported-siem-platforms)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Overview

Jupiter's SIEM integration enables automatic forwarding of security findings to your enterprise SIEM platform for centralized monitoring, correlation, and compliance reporting.

**Business Value**: +$4K ARPU  
**Key Features**:
- ✅ Automatic event forwarding
- ✅ Severity-based routing
- ✅ Correlation ID tracking
- ✅ Real-time indexing
- ✅ Compliance audit trail

---

## Supported SIEM Platforms

### Splunk
- **Versions**: 8.x, 9.x
- **Protocol**: HTTP Event Collector (HEC)
- **Authentication**: Token-based
- **Features**: Full integration with all Splunk apps

### IBM QRadar
- **Versions**: 7.3.x, 7.4.x, 7.5.x
- **Protocol**: Syslog / REST API
- **Authentication**: API key
- **Features**: Custom properties, correlation rules

### Microsoft Sentinel
- **Versions**: Latest
- **Protocol**: Azure Monitor HTTP Data Collector API
- **Authentication**: Workspace ID + Shared Key
- **Features**: KQL queries, workbooks, playbooks

---

## Setup Instructions

### Prerequisites

1. **SIEM Platform Access**
   - Admin or integration user account
   - API access enabled
   - Network connectivity from Jupiter to SIEM

2. **Jupiter Platform**
   - Phase 2 enabled (v1.4.0+)
   - Integration module installed
   - Configuration access

---

### Splunk Setup

#### Step 1: Create HEC Token in Splunk

1. Log into Splunk Web
2. Navigate to **Settings** > **Data Inputs** > **HTTP Event Collector**
3. Click **New Token**
4. Configure:
   - **Name**: `Jupiter-Integration`
   - **Source type**: `jupiter:finding`
   - **Index**: `security` (or your preferred index)
   - **Enable indexer acknowledgment**: Yes (recommended)
5. Click **Review** > **Submit**
6. **Copy the token** - you'll need this for Jupiter configuration

#### Step 2: Configure Jupiter

Create configuration file: `config/integrations/splunk.yaml`

```yaml
siem:
  platform: splunk
  enabled: true
  
  connection:
    url: https://splunk.yourcompany.com:8088
    token: YOUR_HEC_TOKEN_HERE
    verify_ssl: true
    timeout: 30
  
  settings:
    index: security
    source: jupiter
    sourcetype: jupiter:finding
    enable_ack: true
  
  event_mapping:
    severity:
      critical: critical
      high: high
      medium: medium
      low: low
      info: info
    
    fields:
      - vulnerability_id
      - cve_id
      - cvss_score
      - affected_asset
      - detection_time
      - remediation_status
```

#### Step 3: Test Connection

```bash
# Test SIEM connection
python -m ai_copilot.integrations.test_siem --platform splunk

# Expected output:
# ✅ Connection successful
# ✅ HEC token valid
# ✅ Index accessible
# ✅ Test event sent and indexed
```

#### Step 4: Verify in Splunk

Run this SPL query:
```spl
index=security sourcetype=jupiter:finding
| head 10
| table _time, severity, vulnerability_id, affected_asset, cvss_score
```

---

### IBM QRadar Setup

#### Step 1: Create API Key in QRadar

1. Log into QRadar Console
2. Navigate to **Admin** > **Authorized Services**
3. Click **New Authorized Service**
4. Configure:
   - **Name**: `Jupiter Integration`
   - **Token**: Generate new token
   - **Capabilities**: `ADMIN`, `SEM` (for event creation)
5. **Copy the token**

#### Step 2: Configure Jupiter

Create configuration file: `config/integrations/qradar.yaml`

```yaml
siem:
  platform: qradar
  enabled: true
  
  connection:
    url: https://qradar.yourcompany.com
    token: YOUR_API_TOKEN_HERE
    verify_ssl: true
    timeout: 30
  
  settings:
    log_source: Jupiter_Security_Platform
    event_category: 1001  # Custom security events
    low_level_category: 10100
  
  event_mapping:
    severity:
      critical: 10  # QRadar severity scale
      high: 8
      medium: 5
      low: 3
      info: 1
    
    custom_properties:
      - name: vulnerability_id
        id: 1001
      - name: cvss_score
        id: 1002
      - name: remediation_status
        id: 1003
```

#### Step 3: Create Custom Properties (QRadar)

In QRadar, create custom event properties:

```bash
# Use QRadar CLI or UI to create custom properties
# Admin > Custom Event Properties > Add

Property Name: vulnerability_id
Property Type: String
Property ID: 1001

Property Name: cvss_score
Property Type: Numeric
Property ID: 1002

Property Name: remediation_status
Property Type: String
Property ID: 1003
```

#### Step 4: Test Connection

```bash
# Test QRadar connection
python -m ai_copilot.integrations.test_siem --platform qradar

# Expected output:
# ✅ Connection successful
# ✅ API token valid
# ✅ Log source created
# ✅ Test event sent
```

---

### Microsoft Sentinel Setup

#### Step 1: Get Workspace Credentials

1. Log into Azure Portal
2. Navigate to **Microsoft Sentinel** workspace
3. Go to **Settings** > **Workspace settings** > **Agents management**
4. Copy:
   - **Workspace ID**
   - **Primary Key** (or Secondary Key)

#### Step 2: Configure Jupiter

Create configuration file: `config/integrations/sentinel.yaml`

```yaml
siem:
  platform: sentinel
  enabled: true
  
  connection:
    workspace_id: YOUR_WORKSPACE_ID
    shared_key: YOUR_PRIMARY_KEY
    region: eastus  # Your Azure region
    verify_ssl: true
    timeout: 30
  
  settings:
    log_type: JupiterSecurityFindings
    time_generated_field: detection_time
  
  event_mapping:
    severity:
      critical: Critical
      high: High
      medium: Medium
      low: Low
      info: Informational
    
    fields:
      - vulnerability_id
      - cve_id
      - cvss_score
      - affected_asset
      - detection_time
      - remediation_status
      - compliance_impact
```

#### Step 3: Create Data Collection Rule (Optional)

For advanced filtering, create a DCR in Sentinel:

```json
{
  "properties": {
    "dataCollectionEndpointId": "/subscriptions/.../dataCollectionEndpoints/jupiter-dce",
    "streamDeclarations": {
      "Custom-JupiterSecurityFindings": {
        "columns": [
          {"name": "TimeGenerated", "type": "datetime"},
          {"name": "Severity", "type": "string"},
          {"name": "VulnerabilityId", "type": "string"},
          {"name": "CVSSScore", "type": "real"},
          {"name": "AffectedAsset", "type": "string"}
        ]
      }
    }
  }
}
```

#### Step 4: Test Connection

```bash
# Test Sentinel connection
python -m ai_copilot.integrations.test_siem --platform sentinel

# Expected output:
# ✅ Connection successful
# ✅ Workspace accessible
# ✅ Test event sent
# ✅ Custom log table created
```

#### Step 5: Query in Sentinel

Use KQL to query Jupiter events:

```kql
JupiterSecurityFindings_CL
| where TimeGenerated > ago(24h)
| where Severity_s == "Critical"
| project TimeGenerated, VulnerabilityId_s, CVSSScore_d, AffectedAsset_s
| order by TimeGenerated desc
```

---

## Configuration

### Environment Variables

Set these environment variables for secure credential management:

```bash
# Splunk
export JUPITER_SPLUNK_URL=https://splunk.company.com:8088
export JUPITER_SPLUNK_TOKEN=your-hec-token

# QRadar
export JUPITER_QRADAR_URL=https://qradar.company.com
export JUPITER_QRADAR_TOKEN=your-api-token

# Sentinel
export JUPITER_SENTINEL_WORKSPACE_ID=your-workspace-id
export JUPITER_SENTINEL_SHARED_KEY=your-shared-key
```

### Auto-Detection

Jupiter can auto-detect your SIEM platform from query text:

```python
# User says: "send to splunk"
query = Query(message="Send this critical finding to Splunk")
# Platform auto-detected: splunk

# User says: "forward to qradar"
query = Query(message="Forward to QRadar")
# Platform auto-detected: qradar

# User says: "send to sentinel"
query = Query(message="Send to Sentinel")
# Platform auto-detected: sentinel

# No platform specified → uses default from config
query = Query(message="Send to SIEM")
# Platform: Uses default_platform from config
```

---

## Usage Examples

### Example 1: Send Critical Finding

```python
from ai_copilot import CopilotEngine, Query

copilot = CopilotEngine()

query = Query(
    message="Send this critical SQL injection to Splunk",
    user_id="analyst_01",
    session_id="session_123",
    metadata={
        "finding_data": {
            "title": "Critical SQL Injection in Login Endpoint",
            "severity": "critical",
            "description": "SQL injection vulnerability allows authentication bypass",
            "affected_asset": "web-app-01",
            "cve_id": "CVE-2024-1234",
            "cvss_score": 9.8,
            "detection_time": "2025-10-18T14:00:00Z",
            "remediation_status": "pending"
        }
    }
)

response = copilot.process_query(query)

print(f"SIEM Platform: {response.data['siem_alert']['platform']}")
print(f"Event ID: {response.data['siem_alert']['event_id']}")
print(f"SIEM URL: {response.data['siem_url']}")
```

**Output**:
```
SIEM Platform: splunk
Event ID: SIEM-EVENT-2025-10-18-001
SIEM URL: https://splunk.company.com/en-US/app/search/SIEM-EVENT-2025-10-18-001
```

### Example 2: Batch Send Multiple Findings

```python
findings = [
    {"title": "SQL Injection", "severity": "critical", "cvss": 9.8},
    {"title": "XSS Vulnerability", "severity": "high", "cvss": 7.5},
    {"title": "Weak Cipher", "severity": "medium", "cvss": 5.3}
]

for finding in findings:
    query = Query(
        message=f"Send to SIEM",
        user_id="analyst_01",
        session_id="session_123",
        metadata={"finding_data": finding}
    )
    
    response = copilot.process_query(query)
    print(f"✅ Sent {finding['title']} - Event ID: {response.data['siem_alert']['event_id']}")
```

### Example 3: Send with Custom Correlation ID

```python
query = Query(
    message="Send to QRadar with correlation tracking",
    user_id="analyst_01",
    session_id="session_123",
    metadata={
        "finding_data": {
            "title": "Privilege Escalation Attempt",
            "severity": "high",
            "correlation_id": "INCIDENT-2025-456"
        }
    }
)

response = copilot.process_query(query)
print(f"Correlation ID: {response.data['correlation_id']}")
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Connection Timeout

**Error**: `SIEM connection timeout after 30 seconds`

**Solutions**:
1. Check network connectivity:
   ```bash
   ping splunk.yourcompany.com
   telnet splunk.yourcompany.com 8088
   ```

2. Verify firewall rules allow outbound HTTPS
3. Increase timeout in configuration:
   ```yaml
   connection:
     timeout: 60  # Increase to 60 seconds
   ```

#### Issue 2: Authentication Failed

**Error**: `SIEM authentication failed: Invalid token`

**Solutions**:
1. Verify token in SIEM platform
2. Check token hasn't expired
3. Ensure token has correct permissions
4. Regenerate token if necessary

#### Issue 3: Events Not Appearing in SIEM

**Error**: `Event sent successfully but not visible in SIEM`

**Solutions**:

**Splunk**:
```spl
# Check HEC errors
index=_internal sourcetype=splunkd component=HttpEventCollector
| search ERROR

# Verify index permissions
| rest /services/authorization/roles
| search title="jupiter_role"
| table title, imported_srchIndexesAllowed
```

**QRadar**:
- Check QRadar log source status
- Verify custom properties are defined
- Check QRadar event queue

**Sentinel**:
```kql
# Check ingestion errors
AzureDiagnostics
| where Category == "DataCollectionRuleErrors"
| where TimeGenerated > ago(1h)
```

#### Issue 4: SSL Certificate Verification Failed

**Error**: `SSL certificate verification failed`

**Solutions**:
1. For self-signed certificates (development only):
   ```yaml
   connection:
     verify_ssl: false  # Not recommended for production
   ```

2. Add certificate to trust store (recommended):
   ```bash
   # Linux
   cp your-cert.crt /usr/local/share/ca-certificates/
   update-ca-certificates
   
   # Windows
   certutil -addstore "Root" your-cert.crt
   ```

---

## Best Practices

### Security

1. **Use Environment Variables**: Never hardcode credentials
   ```yaml
   connection:
     token: ${JUPITER_SPLUNK_TOKEN}  # From environment
   ```

2. **Rotate Tokens Regularly**: Set up automatic token rotation (every 90 days)

3. **Use SSL/TLS**: Always enable SSL verification in production
   ```yaml
   connection:
     verify_ssl: true  # Always in production
   ```

4. **Least Privilege**: Grant minimum required permissions
   - Splunk: HEC write access only
   - QRadar: Event creation only
   - Sentinel: Data ingestion only

### Performance

1. **Batch Events**: Send multiple findings in batches (up to 100)

2. **Use Async Mode**: Enable async event sending for better performance
   ```yaml
   settings:
     async_mode: true
     batch_size: 50
     batch_timeout: 10  # seconds
   ```

3. **Monitor Queue**: Check event queue size
   ```python
   stats = copilot.get_statistics()
   print(f"SIEM queue: {stats['siem_queue_size']}")
   ```

### Monitoring

1. **Track Success Rate**:
   ```python
   stats = copilot.get_statistics()
   success_rate = (stats['siem_alerts_sent'] / stats['siem_alerts_attempted']) * 100
   print(f"SIEM success rate: {success_rate}%")
   ```

2. **Set Up Alerts**: Alert on failures
   ```yaml
   alerting:
     siem_failure_threshold: 5  # Alert after 5 consecutive failures
     notification_channel: slack
   ```

3. **Health Checks**: Regular health monitoring
   ```python
   health = copilot.health_check()
   if not health['phase2_integrations']['siem']:
       alert_ops_team("SIEM integration down")
   ```

### Compliance

1. **Enable Audit Trail**: Track all SIEM sends
   ```yaml
   compliance:
     audit_siem_events: true
     retention_days: 365
   ```

2. **Add Compliance Tags**:
   ```python
   metadata = {
       "finding_data": {...},
       "compliance_tags": ["PCI-DSS", "SOC2", "ISO27001"]
   }
   ```

3. **Blockchain Verification**: Enable for audit trail
   ```yaml
   compliance:
     blockchain_audit: true
   ```

---

## Event Format

### Splunk Event Format

```json
{
  "time": 1697643600,
  "sourcetype": "jupiter:finding",
  "source": "jupiter",
  "index": "security",
  "event": {
    "event_id": "SIEM-EVENT-2025-10-18-001",
    "vulnerability_id": "VULN-123",
    "title": "Critical SQL Injection",
    "severity": "critical",
    "cvss_score": 9.8,
    "cve_id": "CVE-2024-1234",
    "affected_asset": "web-app-01",
    "detection_time": "2025-10-18T14:00:00Z",
    "remediation_status": "pending",
    "correlation_id": "CORR-456",
    "jupiter_version": "1.4.0"
  }
}
```

### QRadar Event Format

```json
{
  "eventTime": "2025-10-18T14:00:00Z",
  "logSourceId": "jupiter_security_platform",
  "eventCategory": 1001,
  "severity": 10,
  "message": "Critical SQL Injection detected in web-app-01",
  "customProperties": {
    "vulnerability_id": "VULN-123",
    "cvss_score": 9.8,
    "remediation_status": "pending"
  }
}
```

### Sentinel Event Format

```json
{
  "TimeGenerated": "2025-10-18T14:00:00Z",
  "Severity": "Critical",
  "VulnerabilityId": "VULN-123",
  "Title": "Critical SQL Injection",
  "CVSSScore": 9.8,
  "CVEId": "CVE-2024-1234",
  "AffectedAsset": "web-app-01",
  "RemediationStatus": "pending",
  "CorrelationId": "CORR-456"
}
```

---

## Advanced Configuration

### Custom Event Transformation

```python
# config/integrations/custom_transform.py

def custom_event_transform(finding_data, platform):
    """Custom transformation for SIEM events"""
    
    if platform == "splunk":
        # Add Splunk-specific fields
        finding_data['splunk_app'] = "jupiter_security"
        finding_data['event_category'] = "vulnerability"
    
    elif platform == "qradar":
        # Map to QRadar offense
        finding_data['offense_type'] = "vulnerability_detected"
        finding_data['magnitude'] = finding_data['cvss_score']
    
    elif platform == "sentinel":
        # Add Azure-specific metadata
        finding_data['SubscriptionId'] = "your-subscription-id"
        finding_data['ResourceGroup'] = "security-resources"
    
    return finding_data

# Enable in config
settings:
  custom_transform: config.integrations.custom_transform.custom_event_transform
```

---

## Support

### Getting Help

- **Documentation**: https://docs.jupiter.com/integrations/siem
- **Support Email**: support@jupiter.com
- **Community Forum**: https://community.jupiter.com/siem
- **Status Page**: https://status.jupiter.com

### Reporting Issues

When reporting SIEM integration issues, include:

1. SIEM platform and version
2. Jupiter version
3. Error messages and logs
4. Configuration (redact credentials)
5. Network diagnostic output

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**Supported Platforms**: Splunk 8.x/9.x, QRadar 7.3+, Sentinel Latest
