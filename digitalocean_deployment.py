#!/usr/bin/env python3
"""
Enterprise Scanner - DigitalOcean Deployment Guide
Deployment through DigitalOcean Console
"""

import os
from pathlib import Path

def create_digitalocean_deployment_guide():
    """Create deployment guide for DigitalOcean"""
    
    homepage_path = "website/index.html"
    
    if not os.path.exists(homepage_path):
        print("❌ Homepage file not found!")
        return
        
    file_size = os.path.getsize(homepage_path)
    
    guide = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     DIGITALOCEAN DEPLOYMENT GUIDE                           ║
║                        Enterprise Scanner Homepage                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 DROPLET DETAILS:
   • Name: enterprisescanner-prod-01
   • IP: 134.199.147.45 (IPv4)
   • Private IP: 10.126.0.2
   • OS: Ubuntu 22.04 (LTS) x64
   • Memory: 4 GB / Disk: 80 GB
   • Region: SYD1

📁 HOMEPAGE FILE READY:
   • File: {os.path.abspath(homepage_path)}
   • Size: {file_size:,} bytes
   • Status: ✅ Ready for deployment

🚀 DEPLOYMENT STEPS:

STEP 1: Open DigitalOcean Console
   → In your DigitalOcean dashboard, click "Console" 
   → This opens a web terminal directly to your server

STEP 2: Prepare the Directory
   → Run in console: cd /var/www/html
   → Backup existing: mv index.html index.html.backup 2>/dev/null || true

STEP 3: Create New Homepage
   → Run in console: nano index.html
   → This opens the text editor

STEP 4: Copy Homepage Content
   → Copy content from the file below
   → Paste into nano editor (Ctrl+Shift+V or right-click paste)
   → Save and exit: Ctrl+X, then Y, then Enter

STEP 5: Set Permissions
   → Run in console: chmod 644 index.html
   → Run in console: chown www-data:www-data index.html

STEP 6: Restart Web Server (if needed)
   → Run in console: sudo systemctl restart nginx
   → Or: sudo systemctl restart apache2

STEP 7: Verify Deployment
   → Visit: http://enterprisescanner.com
   → Or: http://134.199.147.45

📋 ALTERNATIVE: File Upload Method
   If you prefer, you can use DigitalOcean's file upload feature:
   → Some DigitalOcean interfaces have file upload options
   → Upload: {os.path.abspath(homepage_path)}
   → To: /var/www/html/index.html

🔧 TROUBLESHOOTING:
   • If nano isn't available: apt update && apt install nano
   • If permissions fail: sudo chmod 644 index.html
   • If web server issues: sudo systemctl status nginx

✨ YOUR DIGITALOCEAN INFRASTRUCTURE IS READY!
   The droplet is properly configured and waiting for the homepage deployment.

═══════════════════════════════════════════════════════════════════════════════
"""

    print(guide)
    
    # Also create a simple deployment script for copy-paste
    deployment_commands = """
# DigitalOcean Console Commands (copy-paste these)
cd /var/www/html
mv index.html index.html.backup 2>/dev/null || true
nano index.html
# [Paste homepage content here, then Ctrl+X, Y, Enter]
chmod 644 index.html
chown www-data:www-data index.html
sudo systemctl restart nginx
echo "✅ Deployment complete! Visit http://enterprisescanner.com"
"""
    
    with open("digitalocean_deployment_commands.txt", "w") as f:
        f.write(deployment_commands)
    
    print("📁 Deployment commands saved to: digitalocean_deployment_commands.txt")
    print("🌐 Ready to deploy through your DigitalOcean Console!")

if __name__ == "__main__":
    create_digitalocean_deployment_guide()