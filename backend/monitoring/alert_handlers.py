"""
Security Alert Notification Handlers
Multi-channel alert delivery for Enterprise Scanner continuous monitoring

This module provides notification handlers for security alerts:
- Email notifications (SMTP)
- Webhook notifications (HTTP POST)
- Slack notifications (Slack API)
- Custom handler support

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class EmailAlertHandler:
    """
    Email alert notification handler
    
    Sends security alerts via SMTP email with formatted content.
    """
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str,
                 from_email: str, to_emails: list):
        """
        Initialize email alert handler
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (587 for TLS, 465 for SSL)
            username: SMTP authentication username
            password: SMTP authentication password
            from_email: From email address
            to_emails: List of recipient email addresses
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    def __call__(self, alert):
        """
        Send email alert
        
        Args:
            alert: SecurityAlert object
        """
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.value.upper()}] Enterprise Scanner Security Alert"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Create HTML content
            html_content = self._create_html_email(alert)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, self.to_emails, msg.as_string())
            
            print(f"Email alert sent: {alert.alert_id}")
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def _create_html_email(self, alert) -> str:
        """Create formatted HTML email content"""
        severity_colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        
        color = severity_colors.get(alert.severity.value, '#6c757d')
        
        recommendations_html = ''.join([
            f"<li>{rec}</li>" for rec in alert.recommendations
        ])
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .alert-box {{ 
                    border-left: 5px solid {color}; 
                    padding: 20px; 
                    margin: 20px 0;
                    background-color: #f8f9fa;
                }}
                .severity {{ 
                    color: {color}; 
                    font-weight: bold; 
                    font-size: 18px;
                }}
                .metric {{ color: #6c757d; font-size: 14px; }}
                .recommendations {{ margin-top: 15px; }}
                .footer {{ margin-top: 30px; color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <p class="severity">{alert.severity.value.upper()} SECURITY ALERT</p>
                <p><strong>Company:</strong> {alert.company_name}</p>
                <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                <hr>
                <p><strong>Message:</strong></p>
                <p>{alert.message}</p>
                <p class="metric">
                    <strong>Metric:</strong> {alert.metric}<br>
                    <strong>Current Value:</strong> {alert.current_value}<br>
                    <strong>Threshold:</strong> {alert.threshold}
                </p>
                {f'''
                <div class="recommendations">
                    <p><strong>Recommended Actions:</strong></p>
                    <ul>{recommendations_html}</ul>
                </div>
                ''' if alert.recommendations else ''}
            </div>
            <div class="footer">
                <p>This is an automated alert from Enterprise Scanner Continuous Monitoring System.</p>
                <p>Assessment ID: {alert.assessment_id}</p>
                <p><a href="https://enterprisescanner.com">Enterprise Scanner</a> | <a href="mailto:security@enterprisescanner.com">security@enterprisescanner.com</a></p>
            </div>
        </body>
        </html>
        """
        
        return html


class WebhookAlertHandler:
    """
    Webhook alert notification handler
    
    Sends security alerts to HTTP webhook endpoints (JSON POST).
    """
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize webhook alert handler
        
        Args:
            webhook_url: Webhook endpoint URL
            headers: Optional HTTP headers (e.g., authentication)
        """
        self.webhook_url = webhook_url
        self.headers = headers or {'Content-Type': 'application/json'}
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for webhook handler")
    
    def __call__(self, alert):
        """
        Send webhook alert
        
        Args:
            alert: SecurityAlert object
        """
        try:
            payload = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.value,
                'metric': alert.metric,
                'message': alert.message,
                'current_value': str(alert.current_value),
                'threshold': str(alert.threshold),
                'assessment_id': alert.assessment_id,
                'company_name': alert.company_name,
                'recommendations': alert.recommendations
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            print(f"Webhook alert sent: {alert.alert_id}")
            
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")


class SlackAlertHandler:
    """
    Slack alert notification handler
    
    Sends security alerts to Slack channels via Incoming Webhooks.
    """
    
    def __init__(self, webhook_url: str, channel: Optional[str] = None):
        """
        Initialize Slack alert handler
        
        Args:
            webhook_url: Slack Incoming Webhook URL
            channel: Optional channel override (e.g., '#security-alerts')
        """
        self.webhook_url = webhook_url
        self.channel = channel
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for Slack handler")
    
    def __call__(self, alert):
        """
        Send Slack alert
        
        Args:
            alert: SecurityAlert object
        """
        try:
            # Map severity to Slack colors
            severity_colors = {
                'critical': 'danger',
                'warning': 'warning',
                'info': 'good'
            }
            
            color = severity_colors.get(alert.severity.value, '#808080')
            
            # Build Slack message
            payload = {
                'text': f":rotating_light: *{alert.severity.value.upper()} Security Alert*",
                'attachments': [
                    {
                        'color': color,
                        'fields': [
                            {
                                'title': 'Company',
                                'value': alert.company_name,
                                'short': True
                            },
                            {
                                'title': 'Metric',
                                'value': alert.metric,
                                'short': True
                            },
                            {
                                'title': 'Message',
                                'value': alert.message,
                                'short': False
                            },
                            {
                                'title': 'Current Value',
                                'value': str(alert.current_value),
                                'short': True
                            },
                            {
                                'title': 'Threshold',
                                'value': str(alert.threshold),
                                'short': True
                            }
                        ],
                        'footer': 'Enterprise Scanner',
                        'footer_icon': 'https://enterprisescanner.com/favicon.ico',
                        'ts': int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            # Add recommendations if present
            if alert.recommendations:
                recommendations_text = '\n'.join([f"• {rec}" for rec in alert.recommendations])
                payload['attachments'][0]['fields'].append({
                    'title': 'Recommended Actions',
                    'value': recommendations_text,
                    'short': False
                })
            
            # Add channel override if specified
            if self.channel:
                payload['channel'] = self.channel
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            print(f"Slack alert sent: {alert.alert_id}")
            
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")


class ConsoleAlertHandler:
    """
    Console alert notification handler (for testing/debugging)
    
    Prints security alerts to console with formatting.
    """
    
    def __call__(self, alert):
        """
        Print alert to console
        
        Args:
            alert: SecurityAlert object
        """
        print("\n" + "="*80)
        print(f"[{alert.severity.value.upper()}] SECURITY ALERT")
        print("="*80)
        print(f"Alert ID:      {alert.alert_id}")
        print(f"Company:       {alert.company_name}")
        print(f"Timestamp:     {alert.timestamp}")
        print(f"Metric:        {alert.metric}")
        print(f"Message:       {alert.message}")
        print(f"Current Value: {alert.current_value}")
        print(f"Threshold:     {alert.threshold}")
        
        if alert.recommendations:
            print("\nRecommended Actions:")
            for i, rec in enumerate(alert.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("="*80 + "\n")


# Helper function to create configured handlers
def create_email_handler(config: Dict[str, Any]) -> EmailAlertHandler:
    """
    Create email alert handler from configuration
    
    Args:
        config: Dict with SMTP configuration
    
    Returns:
        Configured EmailAlertHandler
    """
    return EmailAlertHandler(
        smtp_host=config['smtp_host'],
        smtp_port=config['smtp_port'],
        username=config['username'],
        password=config['password'],
        from_email=config['from_email'],
        to_emails=config['to_emails']
    )


def create_webhook_handler(webhook_url: str, auth_header: Optional[str] = None) -> WebhookAlertHandler:
    """
    Create webhook alert handler
    
    Args:
        webhook_url: Webhook endpoint URL
        auth_header: Optional Bearer token or API key
    
    Returns:
        Configured WebhookAlertHandler
    """
    headers = {'Content-Type': 'application/json'}
    if auth_header:
        headers['Authorization'] = auth_header
    
    return WebhookAlertHandler(webhook_url, headers)


def create_slack_handler(webhook_url: str, channel: Optional[str] = None) -> SlackAlertHandler:
    """
    Create Slack alert handler
    
    Args:
        webhook_url: Slack Incoming Webhook URL
        channel: Optional channel override
    
    Returns:
        Configured SlackAlertHandler
    """
    return SlackAlertHandler(webhook_url, channel)
