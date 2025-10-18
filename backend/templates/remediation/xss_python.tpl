#!/usr/bin/env python3
"""
XSS Remediation Script
Target: {target_system}
Generated: {generated_at}
"""

import re
import sys
import os
import shutil
from datetime import datetime
from html import escape

def backup_file(file_path):
    """Create backup before modification"""
    backup_path = f"{{file_path}}.backup.{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {{backup_path}}")
    return backup_path

def add_xss_protection(file_path):
    """Add XSS protection through output escaping"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Check if using Flask/Jinja2 (auto-escaping enabled by default)
    if 'from flask import' in content:
        print("✅ Flask detected - Jinja2 auto-escaping is enabled by default")
        
        # Check for |safe filter usage
        unsafe_count = content.count('|safe')
        if unsafe_count > 0:
            print(f"⚠️  Found {{unsafe_count}} uses of |safe filter - review these carefully")
    
    # Check for manual HTML generation
    html_concat_pattern = r'["\']<[^>]+>["\']\\s*\+.*\+.*'
    if re.search(html_concat_pattern, content):
        print("⚠️  Found manual HTML concatenation - use template engine instead")
    
    # Add security headers if not present
    if 'X-XSS-Protection' not in content:
        header_code = '''
# XSS Protection Headers
@app.after_request
def set_security_headers(response):
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
'''
        content = content + "\n" + header_code
        print("✅ Added XSS protection headers")
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python xss_fix.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {{file_path}}")
        sys.exit(1)
    
    print(f"Starting XSS remediation for {{file_path}}")
    
    backup_path = backup_file(file_path)
    
    try:
        success = add_xss_protection(file_path)
        
        print("\n✅ Remediation complete!")
        print(f"   Backup: {{backup_path}}")
        print("\nAdditional recommendations:")
        print("1. Use template engines with auto-escaping (Jinja2, Django)")
        print("2. Avoid |safe filter unless absolutely necessary")
        print("3. Implement Content Security Policy (CSP)")
        print("4. Validate and sanitize all user inputs")
    
    except Exception as e:
        print(f"\n❌ Error: {{e}}")
        shutil.copy2(backup_path, file_path)
        sys.exit(1)

if __name__ == "__main__":
    main()
