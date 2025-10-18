#!/usr/bin/env python3
"""
Enterprise Scanner - Email Configuration Setup
Interactive setup for Google Workspace email credentials
"""

import os
import getpass
import re
from datetime import datetime

def validate_email(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def setup_email_credentials():
    """Interactive setup for email credentials"""
    print("📧 Enterprise Scanner - Email Configuration Setup")
    print("=" * 55)
    print()
    print("This setup will configure Google Workspace email credentials")
    print("for the Enterprise Scanner platform.")
    print()
    
    # Get email username
    while True:
        email_username = input("Enter your Google Workspace email address (e.g., info@enterprisescanner.com): ").strip()
        
        if validate_email(email_username):
            break
        else:
            print("❌ Invalid email format. Please try again.")
    
    # Get app password
    print()
    print("📋 Google Workspace App Password Setup:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Enable 2-Factor Authentication if not already enabled")
    print("3. Go to 'App passwords' section")
    print("4. Generate a new app password for 'Enterprise Scanner'")
    print("5. Copy the 16-character app password (no spaces)")
    print()
    
    while True:
        app_password = getpass.getpass("Enter your Google Workspace app password: ").strip()
        
        if len(app_password) >= 16:
            break
        else:
            print("❌ App password should be at least 16 characters. Please try again.")
    
    # Confirm configuration
    print()
    print("📋 Configuration Summary:")
    print(f"   Email Username: {email_username}")
    print(f"   App Password: {'*' * len(app_password)}")
    print()
    
    confirm = input("Save this configuration? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ Configuration cancelled.")
        return False
    
    # Update environment files
    env_files = ['.env.development', '.env.production']
    
    for env_file in env_files:
        update_env_file(env_file, email_username, app_password)
    
    print("✅ Email configuration saved successfully!")
    print()
    print("📋 Next Steps:")
    print("1. Run email system test: python deployment/scripts/test_email_system.py")
    print("2. Start the Flask application: python backend/app.py") 
    print("3. Test email functionality through the application")
    
    return True

def update_env_file(env_file, email_username, app_password):
    """Update environment file with email credentials"""
    
    if not os.path.exists(env_file):
        print(f"⚠️ Environment file {env_file} not found, skipping...")
        return
    
    # Read existing content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update email configuration lines
    updated_lines = []
    email_vars_updated = set()
    
    for line in lines:
        if line.startswith('EMAIL_USERNAME='):
            updated_lines.append(f'EMAIL_USERNAME={email_username}\n')
            email_vars_updated.add('EMAIL_USERNAME')
        elif line.startswith('EMAIL_PASSWORD='):
            updated_lines.append(f'EMAIL_PASSWORD={app_password}\n')
            email_vars_updated.add('EMAIL_PASSWORD')
        elif line.startswith('EMAIL_TESTING_MODE=') and env_file.endswith('.development'):
            # Enable testing mode for development
            updated_lines.append('EMAIL_TESTING_MODE=False\n')
        else:
            updated_lines.append(line)
    
    # Add missing email variables if not found
    if 'EMAIL_USERNAME' not in email_vars_updated:
        updated_lines.append(f'EMAIL_USERNAME={email_username}\n')
    
    if 'EMAIL_PASSWORD' not in email_vars_updated:
        updated_lines.append(f'EMAIL_PASSWORD={app_password}\n')
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Updated {env_file}")

def setup_development_environment():
    """Setup development environment for email testing"""
    print()
    print("🛠️ Development Environment Setup:")
    print()
    
    # Ask if user wants to enable testing mode for development
    testing_mode = input("Enable email testing mode for development? (Y/n): ").strip().lower()
    
    if testing_mode not in ['n', 'no']:
        # Update development environment to enable testing mode
        env_file = '.env.development'
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Enable testing mode
            if 'EMAIL_TESTING_MODE=' in content:
                content = re.sub(r'EMAIL_TESTING_MODE=.*', 'EMAIL_TESTING_MODE=True', content)
            else:
                content += '\nEMAIL_TESTING_MODE=True\n'
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Development environment configured for email testing")
            print("   Emails will be logged to console instead of sent")
        else:
            print("⚠️ Development environment file not found")

def main():
    """Main setup function"""
    print("🏗️ Enterprise Scanner Email Configuration")
    print()
    
    if not os.path.exists('.env.development') or not os.path.exists('.env.production'):
        print("❌ Environment files not found!")
        print("Please ensure .env.development and .env.production exist in the project root.")
        return False
    
    # Setup email credentials
    if not setup_email_credentials():
        return False
    
    # Setup development environment
    setup_development_environment()
    
    print()
    print("🎉 Email configuration setup completed!")
    print()
    print("📋 Configuration Status:")
    print("   ✅ Google Workspace credentials configured")
    print("   ✅ Development environment ready")
    print("   ✅ Production environment configured")
    print()
    print("💡 Remember to:")
    print("   - Keep your app password secure")
    print("   - Test email functionality before production deployment")
    print("   - Update production environment variables on your server")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            exit(1)
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        exit(1)