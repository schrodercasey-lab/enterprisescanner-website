#!/usr/bin/env python3
"""
Enterprise Scanner - Direct File Upload via Python
Uses paramiko library for SSH/SCP upload
"""

import os
import sys

def check_paramiko():
    """Check if paramiko is available, install if needed"""
    try:
        import paramiko
        return True
    except ImportError:
        print("📦 Installing paramiko for SSH upload...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
            import paramiko
            return True
        except Exception as e:
            print(f"❌ Failed to install paramiko: {e}")
            return False

def upload_homepage():
    """Upload homepage using SSH/SCP"""
    if not check_paramiko():
        return False
    
    import paramiko
    from paramiko import SSHClient, AutoAddPolicy
    
    # Connection details
    hostname = "134.199.147.45"
    username = "root"
    password = "Schroeder123!"
    local_file = "website/index.html"
    remote_file = "/var/www/html/index.html"
    
    print("🚀 ENTERPRISE SCANNER - AUTOMATED UPLOAD")
    print("=" * 50)
    
    # Check local file
    if not os.path.exists(local_file):
        print(f"❌ Local file not found: {local_file}")
        return False
    
    file_size = os.path.getsize(local_file)
    print(f"📁 Local file: {local_file} ({file_size:,} bytes)")
    
    try:
        # Create SSH client
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        
        print(f"🔗 Connecting to {hostname}...")
        ssh.connect(hostname, username=username, password=password, timeout=10)
        
        # Create SCP client
        scp = ssh.open_sftp()
        
        print(f"📤 Uploading {local_file} to {remote_file}...")
        scp.put(local_file, remote_file)
        
        # Set permissions
        ssh.exec_command(f"chmod 644 {remote_file}")
        ssh.exec_command(f"chown www-data:www-data {remote_file}")
        
        print("✅ Upload successful!")
        
        # Verify upload
        stdin, stdout, stderr = ssh.exec_command(f"ls -la {remote_file}")
        result = stdout.read().decode().strip()
        print(f"📋 File on server: {result}")
        
        # Close connections
        scp.close()
        ssh.close()
        
        print("")
        print("🎉 DEPLOYMENT COMPLETE!")
        print("🌐 Visit: http://enterprisescanner.com")
        print("🌐 Direct: http://134.199.147.45")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    success = upload_homepage()
    if not success:
        print("")
        print("🔄 FALLBACK OPTIONS:")
        print("1. Manual WinSCP upload")
        print("2. Online SSH client (https://www.fastssh.com/)")
        print("3. Git Bash: scp website/index.html root@134.199.147.45:/var/www/html/")
        sys.exit(1)