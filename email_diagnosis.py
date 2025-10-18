#!/usr/bin/env python3
"""
Email Configuration Diagnostic Tool
Helps troubleshoot Google Workspace SMTP issues
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def diagnose_email_config():
    """Diagnose email configuration issues"""
    print("🔍 Enterprise Scanner - Email Configuration Diagnosis")
    print("=" * 60)
    
    # Check environment variables
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = os.getenv('EMAIL_PORT')
    
    print("\n📋 Configuration Check:")
    print(f"EMAIL_HOST: {host}")
    print(f"EMAIL_PORT: {port}")
    print(f"EMAIL_USERNAME: {username}")
    print(f"EMAIL_PASSWORD: {'SET (' + str(len(password)) + ' chars)' if password else 'NOT SET'}")
    
    # Analyze potential issues
    print("\n🔍 Potential Issues Analysis:")
    
    issues = []
    recommendations = []
    
    # Check email address format
    if username and '@enterprisescanner.com' in username:
        if username == 'info@enterprisescanner.com':
            issues.append("Using generic info@ address")
            recommendations.append("Verify that info@enterprisescanner.com actually exists in your Google Workspace")
            recommendations.append("Consider using your actual Google Workspace email address for testing")
    
    # Check password format
    if password:
        if ' ' in password:
            issues.append("App password contains spaces")
            recommendations.append("Remove all spaces from the app password")
        
        if len(password) != 16:
            issues.append(f"App password length is {len(password)}, expected 16 characters")
            recommendations.append("Google app passwords are typically 16 characters long")
    
    # Display issues
    if issues:
        print("❌ Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ No obvious configuration issues detected")
    
    # Display recommendations
    if recommendations:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Google Workspace setup guide
    print("\n📚 Google Workspace App Password Setup Guide:")
    print("1. Go to Google Account settings (myaccount.google.com)")
    print("2. Navigate to Security → 2-Step Verification")
    print("3. Scroll down to 'App passwords'")
    print("4. Select 'Mail' and your device")
    print("5. Copy the 16-character password (without spaces)")
    print("6. Use this password in your .env file")
    
    print("\n🔧 Alternative Testing Approach:")
    print("1. Use your personal Gmail address temporarily for testing")
    print("2. Generate an app password for your personal account")
    print("3. Update EMAIL_USERNAME in .env to your personal Gmail")
    print("4. Test with personal credentials first")
    print("5. Once working, switch to Enterprise Scanner credentials")
    
    # Create a test configuration
    print("\n📝 Sample .env configuration:")
    print("EMAIL_HOST=smtp.gmail.com")
    print("EMAIL_PORT=587")
    print("EMAIL_USE_TLS=True")
    print("EMAIL_USERNAME=your-email@gmail.com")
    print("EMAIL_PASSWORD=your16charapppass")
    print("EMAIL_TESTING_MODE=True")

if __name__ == "__main__":
    diagnose_email_config()