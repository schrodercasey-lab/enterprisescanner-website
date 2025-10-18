#!/usr/bin/env python3
"""
Simple Email Test for Enterprise Scanner
Tests SMTP connectivity and email sending without complex imports
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    print("🧪 Testing SMTP Connection...")
    
    # Get configuration from environment
    host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    port = int(os.getenv('EMAIL_PORT', 587))
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Username: {username}")
    print(f"Password: {'***SET***' if password else 'NOT SET'}")
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(host, port)
        server.starttls()
        print("✅ SMTP connection established")
        
        # Test authentication
        server.login(username, password)
        print("✅ SMTP authentication successful")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        return False

def send_test_email():
    """Send a simple test email"""
    print("\n📧 Sending test email...")
    
    # Get configuration
    host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    port = int(os.getenv('EMAIL_PORT', 587))
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = username  # Send to self for testing
    msg['Subject'] = 'Enterprise Scanner Email Test'
    
    body = """
    Hello from Enterprise Scanner!
    
    This is a test email to verify that your Google Workspace SMTP configuration is working correctly.
    
    ✅ Email system is operational
    🚀 Ready for production deployment
    
    Best regards,
    Enterprise Scanner Team
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Send email
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(username, password)
        server.sendmail(username, username, msg.as_string())
        server.quit()
        
        print(f"✅ Test email sent successfully to {username}")
        print("📬 Check your inbox for the test message")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enterprise Scanner - Simple Email Test")
    print("=" * 50)
    
    # Test SMTP connection
    smtp_success = test_smtp_connection()
    
    if smtp_success:
        # Test email sending
        email_success = send_test_email()
        
        if email_success:
            print("\n🎉 All email tests passed!")
            print("✅ Email system is ready for production")
        else:
            print("\n⚠️ Email sending failed")
    else:
        print("\n❌ SMTP connection failed")
        print("💡 Check your Google Workspace app password")
        
    print("\n📋 Next steps:")
    print("1. If tests passed, mark Email System Configuration as complete")
    print("2. Update todo list to begin Production Verification & Testing")
    print("3. Deploy to https://enterprisescanner.com")