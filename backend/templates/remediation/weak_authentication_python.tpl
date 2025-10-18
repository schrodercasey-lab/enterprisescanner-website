#!/usr/bin/env python3
"""
Weak Authentication Remediation Script
Target: {target_system}
Generated: {generated_at}
"""

import re
import sys
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create backup before modification"""
    backup_path = f"{{file_path}}.backup.{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {{backup_path}}")
    return backup_path

def upgrade_authentication(file_path):
    """Upgrade authentication to use bcrypt"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Check for weak hashing
    weak_patterns = [
        (r'import md5', 'MD5 hashing'),
        (r'import sha1', 'SHA1 hashing'),
        (r'hashlib\.md5', 'MD5 hashing'),
        (r'hashlib\.sha1', 'SHA1 hashing'),
    ]
    
    for pattern, description in weak_patterns:
        if re.search(pattern, content):
            print(f"⚠️  Found {{description}} - upgrade to bcrypt")
            changes_made.append(description)
    
    # Add bcrypt import if not present
    if 'import bcrypt' not in content and changes_made:
        import_line = "import bcrypt\n"
        content = import_line + content
        print("✅ Added bcrypt import")
    
    # Add example secure password hashing
    if changes_made:
        example_code = '''
# SECURITY FIX: Use bcrypt for password hashing

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Usage:
# hashed = hash_password("user_password")
# is_valid = verify_password("user_input", hashed)
'''
        content = content + "\n" + example_code
        print("✅ Added secure password hashing functions")
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python auth_fix.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {{file_path}}")
        sys.exit(1)
    
    print(f"Starting authentication upgrade for {{file_path}}")
    
    backup_path = backup_file(file_path)
    
    try:
        success = upgrade_authentication(file_path)
        
        print("\n✅ Remediation complete!")
        print(f"   Backup: {{backup_path}}")
        print("\nAdditional recommendations:")
        print("1. Use bcrypt with work factor >= 12")
        print("2. Implement account lockout after failed attempts")
        print("3. Add multi-factor authentication (MFA)")
        print("4. Enforce strong password policies")
        print("5. Use secure session management")
        print("\nInstall bcrypt:")
        print("   pip install bcrypt")
    
    except Exception as e:
        print(f"\n❌ Error: {{e}}")
        shutil.copy2(backup_path, file_path)
        sys.exit(1)

if __name__ == "__main__":
    main()
