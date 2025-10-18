#!/usr/bin/env python3
"""
Enterprise Scanner - Email Automation System
Automated email workflows for lead nurturing and customer communication
"""

import smtplib
import ssl
import json
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

class EmailAutomationSystem:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USERNAME', 'info@enterprisescanner.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your_app_password')
        
    def get_database_connection(self):
        """Get connection to Enterprise Scanner database"""
        return sqlite3.connect('enterprise_scanner_production.db')
    
    def send_welcome_email(self, lead_email, lead_name, company_name):
        """Send welcome email to new leads"""
        template_path = 'business/marketing/email_templates/welcome_email.html'
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace template variables
            html_content = html_content.replace('{{name}}', lead_name)
            html_content = html_content.replace('{{company}}', company_name)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Welcome to Enterprise Scanner, {lead_name}"
            msg['From'] = 'Enterprise Scanner Sales <sales@enterprisescanner.com>'
            msg['To'] = lead_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Welcome email sent to {lead_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending welcome email: {e}")
            return False
    
    def send_followup_sequence(self, lead_id):
        """Send automated follow-up sequence based on lead behavior"""
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        # Get lead information
        cursor.execute("""
            SELECT l.email, l.first_name, l.last_name, l.lead_score, 
                   c.company_name, l.created_at
            FROM leads l
            JOIN companies c ON l.company_id = c.id
            WHERE l.id = ?
        """, (lead_id,))
        
        lead = cursor.fetchone()
        if not lead:
            print(f"❌ Lead {lead_id} not found")
            return False
        
        email, first_name, last_name, lead_score, company_name, created_at = lead
        
        # Determine follow-up stage based on creation date
        created_date = datetime.fromisoformat(created_at)
        days_since_creation = (datetime.now() - created_date).days
        
        if days_since_creation == 1:
            # Day 1: Welcome email
            self.send_welcome_email(email, first_name, company_name)
        elif days_since_creation == 3:
            # Day 3: Value proposition email
            self.send_value_proposition_email(email, first_name, company_name, lead_score)
        elif days_since_creation == 7:
            # Day 7: Case study email
            self.send_case_study_email(email, first_name, company_name)
        elif days_since_creation == 14:
            # Day 14: Demo invitation
            self.send_demo_invitation(email, first_name, company_name)
        
        conn.close()
        return True
    
    def send_security_alert_email(self, recipient, alert_type, details):
        """Send security alert emails to security team"""
        msg = MIMEMultipart()
        msg['Subject'] = f"[SECURITY ALERT] {alert_type} - Enterprise Scanner"
        msg['From'] = 'Enterprise Scanner Security <security@enterprisescanner.com>'
        msg['To'] = recipient
        
        body = f"""
Security Alert: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Details: {details}

This is an automated security alert from Enterprise Scanner.
Please investigate immediately.

Enterprise Scanner Security Team
security@enterprisescanner.com
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Security alert sent to {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending security alert: {e}")
            return False
    
    def process_daily_email_queue(self):
        """Process daily email automation queue"""
        print(f"🔄 Processing daily email queue - {datetime.now()}")
        
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        # Get leads created in the last 14 days for follow-up
        cursor.execute("""
            SELECT id FROM leads 
            WHERE created_at >= date('now', '-14 days')
            ORDER BY created_at DESC
        """)
        
        leads = cursor.fetchall()
        
        for (lead_id,) in leads:
            self.send_followup_sequence(lead_id)
        
        conn.close()
        print(f"✅ Processed {len(leads)} leads in email queue")

if __name__ == "__main__":
    email_system = EmailAutomationSystem()
    email_system.process_daily_email_queue()
