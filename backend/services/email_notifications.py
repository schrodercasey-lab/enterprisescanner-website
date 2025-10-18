"""
Enterprise Scanner - Automated Email Notification System
Handles client onboarding email sequences and trial management communications
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailTemplates:
    """Pre-defined email templates for client onboarding and trial management"""
    
    @staticmethod
    def welcome_email(client_data: Dict) -> Dict[str, str]:
        """Welcome email template for new trial clients"""
        return {
            'subject': f"Welcome to Enterprise Scanner - Your Trial is Now Active ({client_data['company_name']})",
            'html_body': f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .highlight {{ background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .button {{ background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; }}
                    .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 Welcome to Enterprise Scanner</h1>
                    <p>Your Fortune 500 cybersecurity transformation begins now</p>
                </div>
                
                <div class="content">
                    <h2>Hello {client_data['contact_name']},</h2>
                    
                    <p>Congratulations! Your Enterprise Scanner trial has been successfully activated for <strong>{client_data['company_name']}</strong>.</p>
                    
                    <div class="highlight">
                        <h3>Your Trial Details:</h3>
                        <ul>
                            <li><strong>Package:</strong> {client_data['package_type'].title().replace('-', ' ')}</li>
                            <li><strong>Start Date:</strong> {client_data['start_date']}</li>
                            <li><strong>End Date:</strong> {client_data['end_date']}</li>
                            <li><strong>Potential Annual Savings:</strong> ${client_data.get('potential_savings', '3-5M')}</li>
                        </ul>
                    </div>
                    
                    <h3>What Happens Next:</h3>
                    <ol>
                        <li><strong>Within 2 hours:</strong> Your dedicated security consultant will contact you</li>
                        <li><strong>Within 24 hours:</strong> Initial vulnerability scan will be completed</li>
                        <li><strong>Within 48 hours:</strong> Comprehensive security report delivered</li>
                        <li><strong>Week 1:</strong> Live threat monitoring activated</li>
                    </ol>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{client_data.get('dashboard_url', '#')}" class="button">Access Your Dashboard</a>
                    </p>
                    
                    <h3>Your Support Team:</h3>
                    <p>
                        <strong>Security Consultant:</strong> Will be assigned within 2 hours<br>
                        <strong>Technical Support:</strong> support@enterprisescanner.com<br>
                        <strong>Account Manager:</strong> sales@enterprisescanner.com
                    </p>
                </div>
                
                <div class="footer">
                    <p>Enterprise Scanner - Protecting Fortune 500 Companies Worldwide</p>
                    <p>Questions? Reply to this email or call our priority support line.</p>
                </div>
            </body>
            </html>
            """,
            'text_body': f"""
            Welcome to Enterprise Scanner!
            
            Hello {client_data['contact_name']},
            
            Your Enterprise Scanner trial has been successfully activated for {client_data['company_name']}.
            
            Trial Details:
            - Package: {client_data['package_type'].title().replace('-', ' ')}
            - Start Date: {client_data['start_date']}
            - End Date: {client_data['end_date']}
            
            What Happens Next:
            1. Within 2 hours: Dedicated security consultant will contact you
            2. Within 24 hours: Initial vulnerability scan completed
            3. Within 48 hours: Comprehensive security report delivered
            
            Your Support Team:
            - Technical Support: support@enterprisescanner.com
            - Account Manager: sales@enterprisescanner.com
            
            Best regards,
            Enterprise Scanner Team
            """
        }
    
    @staticmethod
    def consultant_assignment(client_data: Dict, consultant: Dict) -> Dict[str, str]:
        """Email template for consultant assignment notification"""
        return {
            'subject': f"Your Dedicated Security Consultant - {consultant['name']} ({client_data['company_name']})",
            'html_body': f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(135deg, #10b981, #34d399); color: white; padding: 30px; text-align: center; }}
                    .consultant-card {{ background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
                    .content {{ padding: 30px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>👨‍💼 Your Security Consultant Assigned</h1>
                </div>
                
                <div class="content">
                    <h2>Hello {client_data['contact_name']},</h2>
                    
                    <p>Great news! We've assigned a dedicated security consultant to your Enterprise Scanner trial.</p>
                    
                    <div class="consultant-card">
                        <h3>{consultant['name']}</h3>
                        <p><strong>Title:</strong> {consultant['title']}</p>
                        <p><strong>Experience:</strong> {consultant['experience']}</p>
                        <p><strong>Specialization:</strong> {consultant['specialization']}</p>
                        <p><strong>Email:</strong> {consultant['email']}</p>
                        <p><strong>Phone:</strong> {consultant['phone']}</p>
                    </div>
                    
                    <p><strong>{consultant['name']}</strong> will be reaching out to you within the next 2 hours to:</p>
                    <ul>
                        <li>Introduce themselves and understand your specific security needs</li>
                        <li>Schedule your initial vulnerability assessment</li>
                        <li>Configure monitoring for your critical systems</li>
                        <li>Answer any questions about the Enterprise Scanner platform</li>
                    </ul>
                    
                    <p>In the meantime, feel free to reach out directly to {consultant['name']} at {consultant['email']} or {consultant['phone']}.</p>
                </div>
            </body>
            </html>
            """
        }
    
    @staticmethod
    def trial_expiration_warning(client_data: Dict, days_remaining: int) -> Dict[str, str]:
        """Email template for trial expiration warning"""
        urgency = "urgent" if days_remaining <= 3 else "standard"
        
        return {
            'subject': f"⚠️ Trial Expires in {days_remaining} Days - Convert to Full Protection ({client_data['company_name']})",
            'html_body': f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; padding: 30px; text-align: center; }}
                    .warning {{ background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                    .savings {{ background: #ecfdf5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .button {{ background: #ef4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>⚠️ Trial Expiration Notice</h1>
                    <p>Don't lose your cybersecurity protection</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2>Hello {client_data['contact_name']},</h2>
                    
                    <div class="warning">
                        <h3>⏰ Your Enterprise Scanner trial expires in {days_remaining} days</h3>
                        <p>After expiration, you'll lose access to:</p>
                        <ul>
                            <li>Real-time threat monitoring</li>
                            <li>Vulnerability scanning</li>
                            <li>Executive security reports</li>
                            <li>24/7 SOC support</li>
                        </ul>
                    </div>
                    
                    <div class="savings">
                        <h3>💰 Your Proven ROI During Trial:</h3>
                        <ul>
                            <li>Threats detected and blocked: {client_data.get('threats_blocked', '247')}</li>
                            <li>Vulnerabilities identified: {client_data.get('vulnerabilities_found', '89')}</li>
                            <li>Estimated cost savings: ${client_data.get('trial_savings', '450K')}</li>
                            <li>Security posture improvement: {client_data.get('improvement', '78%')}</li>
                        </ul>
                    </div>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="mailto:sales@enterprisescanner.com?subject=Convert Trial - {client_data['company_name']}" class="button">
                            Convert to Full Protection Now
                        </a>
                    </p>
                    
                    <p>Your dedicated account manager will contact you within 2 hours to discuss:</p>
                    <ul>
                        <li>Custom pricing based on your organization size</li>
                        <li>Seamless transition from trial to full protection</li>
                        <li>Additional features for your specific industry</li>
                        <li>Implementation timeline and support</li>
                    </ul>
                </div>
            </body>
            </html>
            """
        }

class EmailNotificationSystem:
    """Automated email notification system for Enterprise Scanner clients"""
    
    def __init__(self, smtp_config: Dict[str, str]):
        """
        Initialize email system with SMTP configuration
        
        Args:
            smtp_config: Dictionary containing SMTP settings
        """
        self.smtp_config = smtp_config
        self.templates = EmailTemplates()
        
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Send an email using SMTP configuration"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text version
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            
            # Add HTML version
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                
                if self.smtp_config.get('username') and self.smtp_config.get('password'):
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(self, client_data: Dict) -> bool:
        """Send welcome email to new trial client"""
        template = self.templates.welcome_email(client_data)
        return self.send_email(
            client_data['contact_email'],
            template['subject'],
            template['html_body'],
            template['text_body']
        )
    
    def send_consultant_assignment(self, client_data: Dict, consultant: Dict) -> bool:
        """Send consultant assignment notification"""
        template = self.templates.consultant_assignment(client_data, consultant)
        return self.send_email(
            client_data['contact_email'],
            template['subject'],
            template['html_body']
        )
    
    def send_trial_expiration_warning(self, client_data: Dict, days_remaining: int) -> bool:
        """Send trial expiration warning"""
        template = self.templates.trial_expiration_warning(client_data, days_remaining)
        return self.send_email(
            client_data['contact_email'],
            template['subject'],
            template['html_body']
        )
    
    def schedule_email_sequence(self, client_data: Dict) -> List[Dict]:
        """Schedule automated email sequence for trial client"""
        start_date = datetime.fromisoformat(client_data['start_date'])
        end_date = datetime.fromisoformat(client_data['end_date'])
        
        email_schedule = [
            {
                'type': 'welcome',
                'send_date': start_date,
                'status': 'pending'
            },
            {
                'type': 'consultant_assignment',
                'send_date': start_date + timedelta(hours=2),
                'status': 'pending'
            },
            {
                'type': 'week_1_check_in',
                'send_date': start_date + timedelta(days=7),
                'status': 'pending'
            },
            {
                'type': 'week_2_progress',
                'send_date': start_date + timedelta(days=14),
                'status': 'pending'
            },
            {
                'type': 'week_3_optimization',
                'send_date': start_date + timedelta(days=21),
                'status': 'pending'
            },
            {
                'type': 'expiration_warning_7_days',
                'send_date': end_date - timedelta(days=7),
                'status': 'pending'
            },
            {
                'type': 'expiration_warning_3_days',
                'send_date': end_date - timedelta(days=3),
                'status': 'pending'
            },
            {
                'type': 'expiration_warning_1_day',
                'send_date': end_date - timedelta(days=1),
                'status': 'pending'
            }
        ]
        
        logger.info(f"Scheduled {len(email_schedule)} emails for {client_data['company_name']}")
        return email_schedule

# Example usage and configuration
def create_email_system():
    """Create email notification system with configuration"""
    
    # Example SMTP configuration (would be loaded from environment variables)
    smtp_config = {
        'smtp_server': 'smtp.gmail.com',  # Or your SMTP server
        'smtp_port': 587,
        'from_email': 'info@enterprisescanner.com',
        'username': 'info@enterprisescanner.com',  # Would be from env
        'password': 'your_app_password',  # Would be from env
        'use_tls': True
    }
    
    return EmailNotificationSystem(smtp_config)

# Sample consultant data
SAMPLE_CONSULTANTS = [
    {
        'name': 'Michael Rodriguez',
        'title': 'Senior Security Architect',
        'experience': '15+ years in Fortune 500 cybersecurity',
        'specialization': 'Financial Services & Healthcare',
        'email': 'michael.rodriguez@enterprisescanner.com',
        'phone': '+1 (555) 123-4567'
    },
    {
        'name': 'Lisa Wang',
        'title': 'Principal Security Consultant',
        'experience': '12+ years in enterprise security',
        'specialization': 'Technology & Manufacturing',
        'email': 'lisa.wang@enterprisescanner.com',
        'phone': '+1 (555) 234-5678'
    },
    {
        'name': 'David Chen',
        'title': 'Lead Cybersecurity Analyst',
        'experience': '10+ years in threat intelligence',
        'specialization': 'Retail & E-commerce',
        'email': 'david.chen@enterprisescanner.com',
        'phone': '+1 (555) 345-6789'
    }
]

def assign_consultant(client_data: Dict) -> Dict:
    """Assign appropriate consultant based on client industry"""
    import random
    
    # In production, this would use intelligent matching logic
    # For now, randomly assign from available consultants
    consultant = random.choice(SAMPLE_CONSULTANTS)
    
    logger.info(f"Assigned consultant {consultant['name']} to {client_data['company_name']}")
    return consultant