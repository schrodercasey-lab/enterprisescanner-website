# Continuous Monitoring System - API Documentation

## Overview
The Enterprise Scanner Continuous Monitoring System provides real-time security posture tracking, automated alerting, and historical trend analysis for Fortune 500 enterprises.

**Base URL**: `/api/monitoring`

---

## Table of Contents
1. [Dashboard API](#dashboard-api)
2. [Trends & Metrics API](#trends--metrics-api)
3. [Alerts Management API](#alerts-management-api)
4. [Snapshot API](#snapshot-api)
5. [Alert Handlers Configuration](#alert-handlers-configuration)
6. [Authentication](#authentication)
7. [Error Handling](#error-handling)

---

## Dashboard API

### GET /api/monitoring/dashboard/<company_name>

Retrieve comprehensive monitoring dashboard data for a specific company.

**Parameters:**
- `company_name` (path, required): Company name to retrieve dashboard for

**Response Format:**
```json
{
  "success": true,
  "data": {
    "current_status": {
      "overall_score": 85,
      "risk_level": "LOW",
      "last_assessment": "2024-01-15T10:30:00Z",
      "assessment_id": "abc-123"
    },
    "category_scores": {
      "Infrastructure Security": 88,
      "Network Security": 82,
      "SSL/TLS Security": 90,
      "Vulnerability Assessment": 78,
      "Cloud Security": 92,
      "Container Security": 87,
      "Compliance Posture": 85
    },
    "vulnerability_summary": {
      "total": 45,
      "critical": 2,
      "high": 5,
      "medium": 18,
      "low": 20
    },
    "trends": {
      "direction": "improving",
      "score_history": [
        {"timestamp": "2024-01-15T10:30:00Z", "value": 85},
        {"timestamp": "2024-01-08T10:30:00Z", "value": 82}
      ],
      "critical_findings_history": [
        {"timestamp": "2024-01-15T10:30:00Z", "value": 2},
        {"timestamp": "2024-01-08T10:30:00Z", "value": 4}
      ]
    },
    "active_alerts": [
      {
        "alert_id": "alert_001",
        "severity": "critical",
        "metric": "critical_findings",
        "message": "Critical vulnerabilities detected",
        "current_value": "5",
        "threshold": "5"
      }
    ],
    "alerts_summary": {
      "critical": 1,
      "warning": 3,
      "total": 4
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Dashboard data retrieved successfully
- `404 Not Found`: No monitoring data found for company
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
curl -X GET "https://enterprisescanner.com/api/monitoring/dashboard/AcmeCorp" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

---

## Trends & Metrics API

### GET /api/monitoring/trends/<company_name>/<metric_name>

Retrieve time-series trend data for a specific security metric.

**Parameters:**
- `company_name` (path, required): Company name
- `metric_name` (path, required): Metric name (see available metrics below)
- `days` (query, optional): Number of days of history (default: 30, max: 365)

**Available Metrics:**
- `overall_score`: Overall security posture score (0-100)
- `infrastructure_score`: Infrastructure security score
- `network_score`: Network security score
- `cloud_score`: Cloud infrastructure security score
- `container_score`: Container and orchestration security score
- `vulnerability_count`: Total vulnerability count
- `critical_findings`: Number of critical security findings
- `high_findings`: Number of high-severity findings
- `compliance_score`: Compliance framework score

**Response Format:**
```json
{
  "success": true,
  "company": "AcmeCorp",
  "metric": "overall_score",
  "days": 30,
  "data": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "value": 85,
      "assessment_id": "abc-123"
    },
    {
      "timestamp": "2024-01-08T10:30:00Z",
      "value": 82,
      "assessment_id": "abc-122"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Trend data retrieved successfully
- `400 Bad Request`: Invalid metric name or days parameter
- `404 Not Found`: No trend data found
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
# Get 90 days of overall score trend
curl -X GET "https://enterprisescanner.com/api/monitoring/trends/AcmeCorp/overall_score?days=90" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### GET /api/monitoring/metrics

List all available monitoring metrics with descriptions.

**Response Format:**
```json
{
  "success": true,
  "metrics": [
    {
      "name": "overall_score",
      "display_name": "Overall Score",
      "description": "Overall security posture score (0-100)"
    }
  ],
  "count": 9,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Alerts Management API

### GET /api/monitoring/alerts/<company_name>

Retrieve active (unacknowledged) alerts for a company.

**Parameters:**
- `company_name` (path, required): Company name
- `severity` (query, optional): Filter by severity (critical, warning, info)

**Response Format:**
```json
{
  "success": true,
  "company": "AcmeCorp",
  "count": 2,
  "alerts": [
    {
      "alert_id": "alert_20240115_001",
      "timestamp": "2024-01-15T10:30:00Z",
      "severity": "critical",
      "metric": "critical_findings",
      "message": "Critical security findings exceed threshold",
      "current_value": "5",
      "threshold": "5",
      "assessment_id": "abc-123",
      "recommendations": [
        "Review and patch critical vulnerabilities immediately",
        "Escalate to security team for urgent remediation",
        "Schedule emergency security review meeting"
      ]
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Alerts retrieved successfully
- `400 Bad Request`: Invalid severity parameter
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
# Get critical alerts only
curl -X GET "https://enterprisescanner.com/api/monitoring/alerts/AcmeCorp?severity=critical" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### POST /api/monitoring/alerts/<alert_id>/acknowledge

Acknowledge (mark as handled) a specific alert.

**Parameters:**
- `alert_id` (path, required): Alert ID to acknowledge

**Response Format:**
```json
{
  "success": true,
  "message": "Alert alert_20240115_001 acknowledged successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Alert acknowledged successfully
- `404 Not Found`: Alert not found or already acknowledged
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
curl -X POST "https://enterprisescanner.com/api/monitoring/alerts/alert_20240115_001/acknowledge" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

---

## Snapshot API

### GET /api/monitoring/snapshot/<company_name>/latest

Retrieve the latest security snapshot for a company.

**Parameters:**
- `company_name` (path, required): Company name

**Response Format:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-15T10:30:00Z",
    "assessment_id": "abc-123",
    "company_name": "AcmeCorp",
    "overall_score": 85,
    "risk_level": "LOW",
    "category_scores": {
      "Infrastructure Security": 88,
      "Network Security": 82,
      "Cloud Security": 92,
      "Container Security": 87
    },
    "vulnerability_counts": {
      "critical": 2,
      "high": 5,
      "medium": 18,
      "low": 20,
      "total": 45
    },
    "total_findings": 45,
    "critical_findings": 2,
    "high_findings": 5,
    "compliance_score": 85,
    "metadata": {
      "industry": "Financial Services",
      "company_size": "Enterprise",
      "assessment_duration": "45 minutes"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Snapshot retrieved successfully
- `404 Not Found`: No snapshot found for company
- `500 Internal Server Error`: Server error

---

## Alert Handlers Configuration

The monitoring system supports multiple alert delivery channels. Configure alert handlers in your application code:

### Email Alert Handler

```python
from backend.monitoring.alert_handlers import create_email_handler

# Configure SMTP settings
email_config = {
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'security@enterprisescanner.com',
    'password': 'YOUR_SMTP_PASSWORD',
    'from_email': 'security@enterprisescanner.com',
    'to_emails': ['security-team@company.com', 'ciso@company.com']
}

# Create and register handler
email_handler = create_email_handler(email_config)
monitor.add_alert_handler(email_handler)
```

**Email Features:**
- HTML formatted emails with severity color-coding
- Complete alert details including recommendations
- Direct links to Enterprise Scanner dashboard
- Automatic batching for multiple alerts

### Webhook Alert Handler

```python
from backend.monitoring.alert_handlers import create_webhook_handler

# Create webhook handler (for SIEM/SOAR integration)
webhook_handler = create_webhook_handler(
    webhook_url='https://siem.company.com/api/alerts',
    auth_header='Bearer YOUR_API_TOKEN'
)

monitor.add_alert_handler(webhook_handler)
```

**Webhook Payload Format:**
```json
{
  "alert_id": "alert_20240115_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "severity": "critical",
  "metric": "critical_findings",
  "message": "Critical security findings exceed threshold",
  "current_value": "5",
  "threshold": "5",
  "assessment_id": "abc-123",
  "company_name": "AcmeCorp",
  "recommendations": [
    "Review and patch critical vulnerabilities immediately"
  ]
}
```

### Slack Alert Handler

```python
from backend.monitoring.alert_handlers import create_slack_handler

# Create Slack handler
slack_handler = create_slack_handler(
    webhook_url='https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    channel='#security-alerts'  # Optional channel override
)

monitor.add_alert_handler(slack_handler)
```

**Slack Features:**
- Rich formatted messages with severity color-coding
- Inline alert details with expandable recommendations
- Emoji indicators for alert severity
- Real-time delivery to team channels

### Custom Alert Handler

```python
class CustomAlertHandler:
    """Custom alert handler implementation"""
    
    def __call__(self, alert):
        """
        Handle security alert
        
        Args:
            alert: SecurityAlert object with properties:
                - alert_id: Unique alert identifier
                - timestamp: Alert timestamp
                - severity: AlertSeverity enum (INFO, WARNING, CRITICAL)
                - metric: Metric name that triggered alert
                - message: Human-readable alert message
                - current_value: Current metric value
                - threshold: Threshold that was exceeded
                - assessment_id: Associated assessment ID
                - company_name: Company name
                - recommendations: List of recommended actions
        """
        # Your custom alert handling logic
        print(f"Custom handler: {alert.severity.value} - {alert.message}")

# Register custom handler
custom_handler = CustomAlertHandler()
monitor.add_alert_handler(custom_handler)
```

---

## Alert Thresholds Configuration

Configure custom alert thresholds for your organization:

```python
from backend.monitoring.continuous_monitor import ContinuousSecurityMonitor, MonitoringMetric

monitor = ContinuousSecurityMonitor()

# Configure overall score thresholds
monitor.configure_alert_threshold(
    metric=MonitoringMetric.OVERALL_SCORE,
    severity='critical',
    value=60  # Alert if score drops below 60
)

monitor.configure_alert_threshold(
    metric=MonitoringMetric.OVERALL_SCORE,
    severity='warning',
    value=75  # Warn if score drops below 75
)

# Configure critical findings thresholds
monitor.configure_alert_threshold(
    metric=MonitoringMetric.CRITICAL_FINDINGS,
    severity='critical',
    value=5  # Alert if critical findings >= 5
)

# Configure score degradation thresholds
monitor.configure_alert_threshold(
    metric='score_degradation',
    severity='critical',
    value=-15  # Alert if score drops >15 points
)
```

**Default Thresholds:**
- **Overall Score**: Critical <60, Warning <75
- **Critical Findings**: Critical ≥5, Warning ≥3
- **High Findings**: Critical ≥10, Warning ≥7
- **Score Degradation**: Critical -15pts, Warning -10pts

---

## Authentication

All API endpoints require authentication using Bearer tokens.

**Header Format:**
```
Authorization: Bearer YOUR_API_TOKEN
```

**Obtain API Token:**
```bash
curl -X POST "https://enterprisescanner.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

---

## Error Handling

All API endpoints return consistent error responses:

**Error Response Format:**
```json
{
  "success": false,
  "error": "Detailed error message",
  "code": "ERROR_CODE",  // Optional
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Common Error Codes:**
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Rate Limiting:**
- Dashboard API: 100 requests/minute per company
- Trends API: 200 requests/minute per company
- Alerts API: 500 requests/minute per company

---

## Integration Examples

### Python Integration

```python
import requests
from datetime import datetime, timedelta

class EnterpriseMonitoringClient:
    """Client for Enterprise Scanner Monitoring API"""
    
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_dashboard(self, company_name):
        """Get monitoring dashboard"""
        url = f"{self.base_url}/api/monitoring/dashboard/{company_name}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_trends(self, company_name, metric, days=30):
        """Get security trend data"""
        url = f"{self.base_url}/api/monitoring/trends/{company_name}/{metric}"
        params = {'days': days}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_active_alerts(self, company_name, severity=None):
        """Get active alerts"""
        url = f"{self.base_url}/api/monitoring/alerts/{company_name}"
        params = {'severity': severity} if severity else {}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def acknowledge_alert(self, alert_id):
        """Acknowledge an alert"""
        url = f"{self.base_url}/api/monitoring/alerts/{alert_id}/acknowledge"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
client = EnterpriseMonitoringClient(
    'https://enterprisescanner.com',
    'YOUR_API_TOKEN'
)

# Get dashboard
dashboard = client.get_dashboard('AcmeCorp')
print(f"Overall Score: {dashboard['data']['current_status']['overall_score']}")

# Get 90-day trend
trend = client.get_trends('AcmeCorp', 'overall_score', days=90)
print(f"Trend data points: {len(trend['data'])}")

# Get critical alerts
alerts = client.get_active_alerts('AcmeCorp', severity='critical')
print(f"Critical alerts: {alerts['count']}")

# Acknowledge alert
if alerts['alerts']:
    result = client.acknowledge_alert(alerts['alerts'][0]['alert_id'])
    print(f"Alert acknowledged: {result['success']}")
```

### JavaScript Integration

```javascript
class EnterpriseMonitoringClient {
  constructor(baseUrl, apiToken) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiToken}`,
      'Content-Type': 'application/json'
    };
  }

  async getDashboard(companyName) {
    const response = await fetch(
      `${this.baseUrl}/api/monitoring/dashboard/${companyName}`,
      { headers: this.headers }
    );
    return response.json();
  }

  async getTrends(companyName, metric, days = 30) {
    const response = await fetch(
      `${this.baseUrl}/api/monitoring/trends/${companyName}/${metric}?days=${days}`,
      { headers: this.headers }
    );
    return response.json();
  }

  async getActiveAlerts(companyName, severity = null) {
    const url = severity
      ? `${this.baseUrl}/api/monitoring/alerts/${companyName}?severity=${severity}`
      : `${this.baseUrl}/api/monitoring/alerts/${companyName}`;
    
    const response = await fetch(url, { headers: this.headers });
    return response.json();
  }

  async acknowledgeAlert(alertId) {
    const response = await fetch(
      `${this.baseUrl}/api/monitoring/alerts/${alertId}/acknowledge`,
      { method: 'POST', headers: this.headers }
    );
    return response.json();
  }
}

// Usage
const client = new EnterpriseMonitoringClient(
  'https://enterprisescanner.com',
  'YOUR_API_TOKEN'
);

// Get dashboard
const dashboard = await client.getDashboard('AcmeCorp');
console.log(`Overall Score: ${dashboard.data.current_status.overall_score}`);

// Get 90-day trend
const trend = await client.getTrends('AcmeCorp', 'overall_score', 90);
console.log(`Trend data points: ${trend.data.length}`);
```

---

## Support

**Technical Support:**
- Email: security@enterprisescanner.com
- Documentation: https://enterprisescanner.com/docs
- API Status: https://status.enterprisescanner.com

**Enterprise Support:**
- Dedicated Account Manager
- 24/7 Priority Support
- Custom Integration Assistance
- SLA: 1-hour response time for critical issues

---

**Document Version**: 1.0.0  
**Last Updated**: January 15, 2024  
**API Version**: v1
