#!/usr/bin/env python3
"""
Enterprise Scanner - Direct SSH File Upload
Automated deployment using paramiko SSH library
"""

import os
import sys

def install_paramiko():
    """Install paramiko for SSH functionality"""
    try:
        import paramiko
        return True
    except ImportError:
        print("Installing paramiko for SSH functionality...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Paramiko installed successfully")
            import paramiko
            return True
        else:
            print("❌ Failed to install paramiko")
            return False

def deploy_homepage():
    """Deploy homepage via SSH"""
    
    # Install paramiko if needed
    if not install_paramiko():
        return False
    
    import paramiko
    from paramiko import SSHClient, AutoAddPolicy
    
    # Connection details
    hostname = "134.199.147.45"
    username = "root"
    password = "Schroeder123!"
    local_file = "website/index.html"
    remote_file = "/var/www/html/index.html"
    
    print("=" * 60)
    print(" ENTERPRISE SCANNER - AUTOMATED DEPLOYMENT")
    print("=" * 60)
    
    # Check local file
    if not os.path.exists(local_file):
        print(f"❌ Local file not found: {local_file}")
        return False
    
    file_size = os.path.getsize(local_file)
    print(f"📁 Local file: {local_file}")
    print(f"📊 File size: {file_size:,} bytes")
    
    try:
        # Create SSH client
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        
        print(f"🔐 Connecting to {hostname}...")
        ssh.connect(hostname, username=username, password=password, timeout=30)
        print("✅ SSH connection established")
        
        # Create SFTP client
        sftp = ssh.open_sftp()
        print("🔧 SFTP session opened")
        
        # Upload file
        print(f"📤 Uploading {local_file} to {remote_file}...")
        sftp.put(local_file, remote_file)
        print("✅ File uploaded successfully")
        
        # Set permissions
        print("🔒 Setting file permissions...")
        ssh.exec_command(f"chmod 644 {remote_file}")
        ssh.exec_command(f"chown www-data:www-data {remote_file}")
        print("✅ Permissions set")
        
        # Reload nginx
        print("🔄 Reloading web server...")
        stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
        stdout.read()  # Wait for command to complete
        print("✅ Web server reloaded")
        
        # Close connections
        sftp.close()
        ssh.close()
        
        print("")
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print("✅ Homepage deployed to production server")
        print("✅ Web server configuration updated")
        print("✅ File permissions set correctly")
        print("")
        print("🌐 Test your website:")
        print("   • http://enterprisescanner.com")
        print("   • http://134.199.147.45")
        print("")
        print("Expected: Professional homepage with ROI calculator")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print("")
        print("💡 Fallback options:")
        print("1. Use WinSCP: https://winscp.net")
        print(f"2. Manual SCP: scp {local_file} {username}@{hostname}:{remote_file}")
        return False

if __name__ == "__main__":
    success = deploy_homepage()
    if success:
        print("\n🚀 Enterprise Scanner website is now live!")
    else:
        print("\n⚠️ Automated deployment failed - use manual method")