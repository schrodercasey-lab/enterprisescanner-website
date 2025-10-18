#!/usr/bin/env python3
"""
Enterprise Scanner - Email System Test
Test email configuration and delivery for Google Workspace integration
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import from backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load development environment for testing
load_dotenv('.env.development')

def test_email_configuration():
    """Test email configuration and connectivity"""
    print("🧪 Enterprise Scanner - Email System Test")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Checking Email Configuration:")
    
    email_vars = [
        'EMAIL_HOST',
        'EMAIL_PORT', 
        'EMAIL_USE_TLS',
        'EMAIL_USERNAME',
        'EMAIL_PASSWORD'
    ]
    
    config_status = {}
    for var in email_vars:
        value = os.environ.get(var, 'NOT_SET')
        config_status[var] = value
        
        if var == 'EMAIL_PASSWORD':
            # Don't show password, just indicate if it's set
            display_value = "***SET***" if value != 'NOT_SET' and value else "NOT_SET"
        else:
            display_value = value
            
        print(f"   {var}: {display_value}")
    
    # Test SMTP connectivity
    print("\n🔌 Testing SMTP Connectivity:")
    
    try:
        import smtplib
        
        host = config_status.get('EMAIL_HOST', 'smtp.gmail.com')
        port = int(config_status.get('EMAIL_PORT', 587))
        
        print(f"   Connecting to {host}:{port}...")
        
        server = smtplib.SMTP(host, port)
        server.starttls()
        
        print("   ✅ SMTP connection successful")
        print("   ✅ TLS encryption enabled")
        
        # Test authentication if credentials are provided
        username = config_status.get('EMAIL_USERNAME')
        password = config_status.get('EMAIL_PASSWORD')
        
        if username and password and password != 'NOT_SET':
            try:
                server.login(username, password)
                print("   ✅ SMTP authentication successful")
            except Exception as auth_error:
                print(f"   ❌ SMTP authentication failed: {auth_error}")
                print("   💡 Check EMAIL_PASSWORD in .env.development")
        else:
            print("   ⚠️ SMTP authentication not tested (credentials not configured)")
            
        server.quit()
        
    except Exception as e:
        print(f"   ❌ SMTP connection failed: {e}")
        return False
    
    return True

def test_email_sending():
    """Test actual email sending functionality"""
    print("\n📧 Testing Email Sending:")
    
    try:
        # Import the email function from our Flask app
        from backend.app import send_email, EMAIL_CONFIG
        
        # Test email content
        test_subject = f"Enterprise Scanner Email Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        test_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background: #1e3c72; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .success { color: #28a745; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧪 Email System Test</h1>
            </div>
            <div class="content">
                <p><strong>Enterprise Scanner Email System Test</strong></p>
                <p>This is a test email to verify Google Workspace integration.</p>
                <p class="success">✅ Email system is working correctly!</p>
                <p><strong>Test Details:</strong></p>
                <ul>
                    <li>Timestamp: """ + datetime.now().isoformat() + """</li>
                    <li>Environment: """ + os.environ.get('FLASK_ENV', 'development') + """</li>
                    <li>From: """ + EMAIL_CONFIG['username'] + """</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Get test recipient (use configured username as recipient for testing)
        test_recipient = EMAIL_CONFIG['username']
        
        print(f"   Sending test email to: {test_recipient}")
        
        # Send test email
        success = send_email(
            to_email=test_recipient,
            subject=test_subject,
            html_content=test_content
        )
        
        if success:
            print("   ✅ Test email sent successfully!")
            print("   📬 Check your inbox for the test message")
        else:
            print("   ❌ Test email sending failed")
            
        return success
        
    except Exception as e:
        print(f"   ❌ Email sending test failed: {e}")
        return False

def test_business_email_routing():
    """Test business email routing functionality"""
    print("\n🏢 Testing Business Email Routing:")
    
    try:
        from backend.app import BUSINESS_EMAILS
        
        print("   Business email addresses configured:")
        for role, email in BUSINESS_EMAILS.items():
            print(f"     {role}: {email}")
            
        # Test Fortune 500 lead notification
        print("\n   Testing Fortune 500 lead notification...")
        
        from backend.app import send_high_value_lead_notification
        
        test_lead_data = {
            'name': 'John Doe',
            'email': 'john.doe@testcorp.com',
            'company': 'Test Fortune 500 Corp',
            'title': 'Chief Information Security Officer',
            'phone': '+1-555-0123',
            'message': 'Interested in enterprise cybersecurity assessment for our organization.'
        }
        
        result = send_high_value_lead_notification(test_lead_data)
        
        if result:
            print("   ✅ Fortune 500 lead notification test successful")
        else:
            print("   ❌ Fortune 500 lead notification test failed")
            
        return result
        
    except Exception as e:
        print(f"   ❌ Business email routing test failed: {e}")
        return False

def run_comprehensive_email_test():
    """Run comprehensive email system test"""
    print("🚀 Starting Comprehensive Email System Test\n")
    
    tests = [
        ("Email Configuration", test_email_configuration),
        ("Email Sending", test_email_sending),
        ("Business Email Routing", test_business_email_routing)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Email System Test Summary:")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All email system tests passed!")
        print("📧 Email system is ready for production deployment")
    else:
        print("⚠️ Some email system tests failed")
        print("🔧 Please check configuration and credentials")
        
        # Provide troubleshooting guidance
        print("\n💡 Troubleshooting Steps:")
        print("1. Verify EMAIL_PASSWORD is set in .env.development")
        print("2. Check Google Workspace app password configuration")
        print("3. Ensure 2FA is enabled and app password is generated")
        print("4. Verify SMTP settings are correct for your Google Workspace")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_comprehensive_email_test()
    sys.exit(0 if success else 1)