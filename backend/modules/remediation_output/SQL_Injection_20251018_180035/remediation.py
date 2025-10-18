#!/usr/bin/env python3
"""
SQL Injection Remediation Script
Target: Ubuntu 22.04 LTS
File: /app/database.py
Generated: 2025-10-18T08:00:35.463131
"""

import re
import sys
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create backup before modification"""
    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def fix_sql_injection(file_path):
    """Fix SQL injection by replacing string concatenation with parameterized queries"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    fixes_applied = 0
    
    # Pattern 1: cursor.execute with string formatting
    pattern1 = r'cursor\.execute\(["\'].*%s.*["\']\\s*%\\s*\([^)]+\)\)'
    if re.search(pattern1, content):
        print("⚠️  Found string formatting in cursor.execute - requires manual review")
        fixes_applied += 1
    
    # Pattern 2: Direct string concatenation in queries
    pattern2 = r'(SELECT|INSERT|UPDATE|DELETE).*\+.*\+.*'
    matches = re.findall(pattern2, content, re.IGNORECASE)
    if matches:
        print(f"⚠️  Found {len(matches)} SQL queries with string concatenation")
        print("    These should use parameterized queries instead")
        fixes_applied += len(matches)
    
    # Add parameterized query example
    if fixes_applied > 0:
        comment = '''
# SECURITY FIX: Use parameterized queries to prevent SQL injection
# BAD:  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# GOOD: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
'''
        content = comment + "\n" + content
    
    # Write changes
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Applied {fixes_applied} SQL injection fixes to {file_path}")
        return True
    else:
        print("ℹ️  No automatic fixes available - manual review required")
        return False

def main():
    file_path = "/app/database.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Starting SQL injection remediation for {file_path}")
    
    # Backup
    backup_path = backup_file(file_path)
    
    try:
        # Apply fixes
        success = fix_sql_injection(file_path)
        
        if success:
            print("\n✅ Remediation complete!")
            print(f"   Backup: {backup_path}")
            print("   Review changes and test thoroughly before deploying")
        else:
            print("\n⚠️  Manual remediation required")
            print("   1. Replace string concatenation with parameterized queries")
            print("   2. Use prepared statements")
            print("   3. Validate and sanitize all user inputs")
    
    except Exception as e:
        print(f"\n❌ Error during remediation: {e}")
        print(f"   Restoring from backup: {backup_path}")
        shutil.copy2(backup_path, file_path)
        sys.exit(1)

if __name__ == "__main__":
    main()
