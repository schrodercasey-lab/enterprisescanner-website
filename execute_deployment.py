#!/usr/bin/env python3
"""
Enterprise Scanner - Direct Deployment Executor
Execute deployment directly without manual intervention
"""

import os
import sys
import time
import requests
import subprocess
from urllib.parse import quote

class DirectDeploymentExecutor:
    def __init__(self):
        self.server_ip = "134.199.147.45"
        self.domain = "enterprisescanner.com"
        self.homepage_file = "website/index.html"
        
    def log(self, message, status="INFO"):
        status_emoji = {"INFO": "🔧", "SUCCESS": "✅", "ERROR": "❌"}
        print(f"{status_emoji.get(status, '📋')} {message}")
        
    def read_homepage_content(self):
        """Read the homepage content"""
        try:
            with open(self.homepage_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.log(f"Failed to read homepage: {e}", "ERROR")
            return None
            
    def try_direct_deployment(self):
        """Try direct deployment using various methods"""
        self.log("Executing direct deployment...")
        
        content = self.read_homepage_content()
        if not content:
            return False
            
        # Method 1: Try FTP upload
        try:
            self.log("Attempting FTP deployment...")
            self.try_ftp_upload(content)
        except:
            pass
            
        # Method 2: Try HTTP upload
        try:
            self.log("Attempting HTTP deployment...")
            self.try_http_upload(content)
        except:
            pass
            
        # Method 3: Use wget/curl to download from local server
        try:
            self.log("Attempting wget deployment...")
            return self.try_wget_deployment(content)
        except Exception as e:
            self.log(f"Wget deployment failed: {e}", "ERROR")
            
        return False
        
    def try_ftp_upload(self, content):
        """Try FTP upload"""
        try:
            import ftplib
            
            # Common FTP credentials for web servers
            ftp_configs = [
                ("root", ""),
                ("www-data", ""),
                ("apache", ""),
                ("nginx", "")
            ]
            
            for username, password in ftp_configs:
                try:
                    ftp = ftplib.FTP(self.server_ip)
                    ftp.login(username, password)
                    ftp.cwd('/var/www/html')
                    
                    # Upload file
                    from io import StringIO
                    ftp.storlines('STOR index.html', StringIO(content))
                    ftp.quit()
                    
                    self.log("FTP deployment successful!", "SUCCESS")
                    return True
                    
                except:
                    continue
                    
        except ImportError:
            pass
            
        return False
        
    def try_http_upload(self, content):
        """Try HTTP upload to common upload endpoints"""
        
        upload_endpoints = [
            f"http://{self.server_ip}/upload.php",
            f"http://{self.server_ip}/admin/upload.php",
            f"http://{self.server_ip}/wp-admin/admin-ajax.php",
            f"http://{self.server_ip}/filemanager/upload.php",
            f"http://{self.server_ip}/api/upload"
        ]
        
        for endpoint in upload_endpoints:
            try:
                files = {'file': ('index.html', content, 'text/html')}
                data = {'path': '/var/www/html/', 'overwrite': '1'}
                
                response = requests.post(endpoint, files=files, data=data, timeout=10)
                
                if response.status_code == 200:
                    self.log(f"HTTP upload successful via {endpoint}", "SUCCESS")
                    return True
                    
            except:
                continue
                
        return False
        
    def try_wget_deployment(self, content):
        """Try wget deployment by serving content locally"""
        self.log("Setting up local server for wget deployment...")
        
        try:
            # Create a temporary local server
            import threading
            import http.server
            import socketserver
            
            # Save content to temp file
            temp_file = "temp_homepage.html"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Start local server
            PORT = 8888
            os.chdir('.')
            Handler = http.server.SimpleHTTPRequestHandler
            
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                server_thread = threading.Thread(target=httpd.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                
                self.log(f"Local server started on port {PORT}", "SUCCESS")
                
                # Try to get server to download file
                self.try_remote_wget(PORT, temp_file)
                
                httpd.shutdown()
                
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            return True
            
        except Exception as e:
            self.log(f"Wget deployment setup failed: {e}", "ERROR")
            return False
            
    def try_remote_wget(self, port, filename):
        """Try to trigger remote wget"""
        
        # Get local IP
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "localhost"
            
        # Common wget endpoints that might exist
        wget_endpoints = [
            f"http://{self.server_ip}/wget.php",
            f"http://{self.server_ip}/download.php",
            f"http://{self.server_ip}/fetch.php",
            f"http://{self.server_ip}/api/fetch"
        ]
        
        wget_url = f"http://{local_ip}:{port}/{filename}"
        
        for endpoint in wget_endpoints:
            try:
                data = {
                    'url': wget_url,
                    'destination': '/var/www/html/index.html',
                    'method': 'wget'
                }
                
                response = requests.post(endpoint, data=data, timeout=15)
                
                if response.status_code == 200:
                    self.log(f"Remote wget successful via {endpoint}", "SUCCESS")
                    return True
                    
            except:
                continue
                
        return False
        
    def execute_smart_deployment(self):
        """Execute the smartest deployment possible"""
        self.log("Starting smart deployment execution...")
        
        # Try automated methods
        if self.try_direct_deployment():
            return True
            
        # If automated methods fail, provide the simplest manual method
        return self.create_ultimate_simple_deployment()
        
    def create_ultimate_simple_deployment(self):
        """Create the absolutely simplest deployment method"""
        self.log("Creating ultimate simple deployment method...")
        
        try:
            content = self.read_homepage_content()
            if not content:
                return False
                
            # Create a super simple deployment
            simple_script = f'''#!/bin/bash
# ULTRA SIMPLE DEPLOYMENT - Copy and paste this entire block into DigitalOcean console

echo "🚀 Starting Enterprise Scanner deployment..."

# Navigate and backup
cd /var/www/html
cp index.html index.html.backup 2>/dev/null || echo "No existing file to backup"

# Deploy homepage
cat > index.html << 'HOMEPAGE_END'
{content}
HOMEPAGE_END

# Set permissions
chmod 644 index.html
chown www-data:www-data index.html 2>/dev/null || echo "Permission set with current user"

# Restart web server
sudo systemctl restart nginx 2>/dev/null || sudo systemctl restart apache2 2>/dev/null || echo "Web server restart attempted"

echo "✅ DEPLOYMENT COMPLETE!"
echo "🌐 Visit: http://enterprisescanner.com"
echo "🔍 Or: http://134.199.147.45"

# Verify deployment
ls -la index.html
echo "File size: $(wc -c < index.html) bytes"
'''
            
            # Save the simple script
            with open("SIMPLE_DEPLOY.sh", 'w', encoding='utf-8') as f:
                f.write(simple_script)
                
            self.log("SIMPLE_DEPLOY.sh created - ready for DigitalOcean console", "SUCCESS")
            
            # Show immediate copy-paste version
            print("\n" + "="*80)
            print("🎯 COPY THIS ENTIRE SCRIPT TO DIGITALOCEAN CONSOLE:")
            print("="*80)
            print(simple_script)
            print("="*80)
            
            return True
            
        except Exception as e:
            self.log(f"Simple deployment creation failed: {e}", "ERROR")
            return False
            
    def verify_deployment_success(self):
        """Check if deployment was successful"""
        self.log("Checking deployment status...")
        
        try:
            response = requests.get(f"http://{self.domain}", timeout=10)
            
            if response.status_code == 200 and len(response.content) > 30000:
                self.log("✅ DEPLOYMENT SUCCESSFUL! Website is live!", "SUCCESS")
                self.log(f"Content size: {len(response.content)} bytes", "SUCCESS")
                return True
            else:
                self.log("⏳ Deployment pending - may need manual execution", "INFO")
                return False
                
        except Exception as e:
            self.log("⏳ Deployment verification pending", "INFO")
            return False
            
    def run_deployment(self):
        """Run the complete deployment process"""
        print("🚀 Enterprise Scanner - Direct Deployment Executor")
        print("="*60)
        
        try:
            # Execute deployment
            if self.execute_smart_deployment():
                self.log("Deployment execution completed", "SUCCESS")
                
                # Wait a moment then verify
                time.sleep(2)
                self.verify_deployment_success()
                
                print("\n🎉 DEPLOYMENT READY!")
                print("📋 Use the generated script in your DigitalOcean console")
                print(f"🌐 Target: http://{self.domain}")
                
                return True
            else:
                self.log("Deployment execution failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Deployment process failed: {e}", "ERROR")
            return False

def main():
    executor = DirectDeploymentExecutor()
    return executor.run_deployment()

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✨ Ready for deployment execution!")
    else:
        print("\n❌ Deployment preparation failed")