# Enterprise Scanner Security Monitoring
# Real-time security event monitoring and alerting

import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import redis
import os

class SecurityMonitor:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
        self.alert_email = os.getenv('EMAIL_SECURITY', 'security@enterprisescanner.com')
        self.smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', 587))
        self.smtp_user = os.getenv('EMAIL_USERNAME', '')
        self.smtp_password = os.getenv('EMAIL_PASSWORD', '')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/security_events.log'),
                logging.StreamHandler()
            ]
        )
    
    def log_security_event(self, event_type, details, severity='INFO'):
        """Log security event with alerting"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'severity': severity,
            'details': details
        }
        
        # Log to file
        logging.info(f"Security Event: {json.dumps(event)}")
        
        # Store in Redis for real-time monitoring
        self.redis_client.lpush('security_events', json.dumps(event))
        self.redis_client.ltrim('security_events', 0, 1000)  # Keep last 1000 events
        
        # Send alert for high severity events
        if severity in ['HIGH', 'CRITICAL']:
            self.send_security_alert(event)
    
    def send_security_alert(self, event):
        """Send security alert email"""
        try:
            subject = f"Security Alert - {event['type']}"
            
            body = f"""
Security Alert Detected

Event Type: {event['type']}
Severity: {event['severity']}
Timestamp: {event['timestamp']}

Details:
{json.dumps(event['details'], indent=2)}

This is an automated security alert from Enterprise Scanner.
Please investigate immediately.

Enterprise Scanner Security Team
            """
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Security alert sent for event: {event['type']}")
            
        except Exception as e:
            logging.error(f"Failed to send security alert: {e}")
    
    def check_failed_logins(self):
        """Monitor and alert on failed login attempts"""
        try:
            failed_login_key = 'failed_logins'
            failed_logins = self.redis_client.lrange(failed_login_key, 0, -1)
            
            # Check for brute force attempts
            recent_failures = []
            now = datetime.now()
            
            for login_data in failed_logins:
                login_event = json.loads(login_data)
                event_time = datetime.fromisoformat(login_event['timestamp'])
                
                # Check last 15 minutes
                if now - event_time <= timedelta(minutes=15):
                    recent_failures.append(login_event)
            
            # Alert if more than 10 failed attempts in 15 minutes
            if len(recent_failures) > 10:
                self.log_security_event(
                    'BRUTE_FORCE_ATTEMPT',
                    {
                        'failed_attempts': len(recent_failures),
                        'time_window': '15 minutes',
                        'attempts': recent_failures
                    },
                    'HIGH'
                )
        
        except Exception as e:
            logging.error(f"Failed login monitoring error: {e}")
    
    def monitor_suspicious_requests(self):
        """Monitor for suspicious request patterns"""
        try:
            # Get recent security events
            events = self.redis_client.lrange('security_events', 0, 100)
            
            suspicious_patterns = {}
            now = datetime.now()
            
            for event_data in events:
                event = json.loads(event_data)
                event_time = datetime.fromisoformat(event['timestamp'])
                
                # Check last hour
                if now - event_time <= timedelta(hours=1):
                    event_type = event.get('type', 'unknown')
                    if event_type not in suspicious_patterns:
                        suspicious_patterns[event_type] = 0
                    suspicious_patterns[event_type] += 1
            
            # Alert on high frequency suspicious events
            for pattern, count in suspicious_patterns.items():
                if count > 50:  # More than 50 events per hour
                    self.log_security_event(
                        'HIGH_FREQUENCY_SUSPICIOUS_ACTIVITY',
                        {
                            'pattern': pattern,
                            'count': count,
                            'time_window': '1 hour'
                        },
                        'HIGH'
                    )
        
        except Exception as e:
            logging.error(f"Suspicious request monitoring error: {e}")

# Initialize security monitor
security_monitor = SecurityMonitor()

def log_failed_login(ip_address, username, user_agent):
    """Log failed login attempt"""
    security_monitor.log_security_event(
        'FAILED_LOGIN',
        {
            'ip_address': ip_address,
            'username': username,
            'user_agent': user_agent
        },
        'MEDIUM'
    )

def log_successful_login(ip_address, username):
    """Log successful login"""
    security_monitor.log_security_event(
        'SUCCESSFUL_LOGIN',
        {
            'ip_address': ip_address,
            'username': username
        },
        'INFO'
    )

def log_suspicious_request(ip_address, path, details):
    """Log suspicious request"""
    security_monitor.log_security_event(
        'SUSPICIOUS_REQUEST',
        {
            'ip_address': ip_address,
            'path': path,
            'details': details
        },
        'MEDIUM'
    )
