#!/usr/bin/env python3
"""
Enterprise Scanner - Actual Production Deployment
Deploy Live Security Assessment Tool to enterprisescanner.com
"""

import os
import subprocess
import json
from datetime import datetime

class ActualDeployment:
    def __init__(self):
        self.domain = "enterprisescanner.com"
        self.server_ip = "134.199.147.45"
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def verify_deployment_package(self):
        """Verify deployment package exists"""
        self.log("Verifying deployment package...")
        
        # Check if we have the deployment archive
        archive_path = "deployment/archives/enterprise_scanner_live_20251015_114038.tar.gz"
        if os.path.exists(archive_path):
            self.log(f"✓ Found deployment archive: {archive_path}")
            size = os.path.getsize(archive_path) / (1024*1024)  # MB
            self.log(f"✓ Archive size: {size:.1f} MB")
            return archive_path
        else:
            self.log("✗ Deployment archive not found")
            return None
            
    def check_production_server(self):
        """Check production server accessibility"""
        self.log("Checking production server connectivity...")
        
        try:
            # Test HTTPS connectivity
            result = subprocess.run([
                "powershell", "-Command", 
                f"Test-NetConnection -ComputerName {self.domain} -Port 443 -InformationLevel Quiet"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log(f"✓ Server {self.domain} is accessible on port 443")
                return True
            else:
                self.log(f"✗ Cannot reach {self.domain}")
                return False
                
        except Exception as e:
            self.log(f"✗ Connection test failed: {e}")
            return False
            
    def show_deployment_commands(self, archive_path):
        """Show the actual deployment commands to run"""
        self.log("Generating deployment commands...")
        
        commands = f"""
# ENTERPRISE SCANNER - LIVE SECURITY ASSESSMENT DEPLOYMENT
# Server: {self.domain} ({self.server_ip})
# Archive: {archive_path}

# 1. Upload deployment package to server
scp {archive_path} user@{self.server_ip}:/tmp/

# 2. Connect to server
ssh user@{self.server_ip}

# 3. On the server, extract and deploy:
cd /tmp
tar -xzf enterprise_scanner_live_20251015_114038.tar.gz
cd live_deployment_20251015_114038

# 4. Make deployment script executable
chmod +x deploy.sh

# 5. Run deployment
sudo ./deploy.sh

# 6. Verify deployment
sudo systemctl status enterprise-scanner
sudo journalctl -u enterprise-scanner -n 20

# 7. Test API endpoints
curl -X POST https://{self.domain}/api/keys/generate \\
     -H "Content-Type: application/json" \\
     -d '{{"name":"production_key","permissions":"read_write"}}'

# Save the API key from the response, then test:
curl -H "X-API-Key: YOUR_API_KEY" https://{self.domain}/api/health

# 8. Test Live Security Assessment
curl -X POST https://{self.domain}/api/assessment/start \\
     -H "X-API-Key: YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{{
       "company_name": "Test Company",
       "domain": "google.com",
       "email": "test@testcompany.com", 
       "company_size": "large",
       "industry": "technology",
       "scan_types": ["ssl", "dns", "network"]
     }}'

# Monitor assessment progress with the returned assessment_id
curl -H "X-API-Key: YOUR_API_KEY" \\
     https://{self.domain}/api/assessment/status/ASSESSMENT_ID

# Download PDF report when complete
curl -H "X-API-Key: YOUR_API_KEY" \\
     https://{self.domain}/api/assessment/report/ASSESSMENT_ID \\
     -o security_report.pdf
"""
        
        commands_file = "deployment/instructions/LIVE_DEPLOYMENT_COMMANDS.txt"
        with open(commands_file, 'w') as f:
            f.write(commands)
            
        self.log(f"✓ Deployment commands saved to: {commands_file}")
        print(commands)
        
    def create_server_status_check(self):
        """Create a script to check current server status"""
        self.log("Creating server status check...")
        
        status_script = f"""#!/usr/bin/env python3
import requests
import json

def check_server_status():
    print("ENTERPRISE SCANNER - SERVER STATUS CHECK")
    print("=" * 50)
    
    base_url = "https://{self.domain}"
    
    # Test 1: Website
    try:
        response = requests.get(base_url, timeout=10)
        print(f"Website: {response.status_code} - {'✓ Online' if response.status_code == 200 else '✗ Error'}")
    except Exception as e:
        print(f"Website: ✗ Error - {e}")
    
    # Test 2: API Health (might not exist yet)
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"API Health: {response.status_code} - {'✓ Available' if response.status_code == 200 else '✗ Not Available'}")
    except Exception as e:
        print(f"API Health: ✗ Not Available - API not deployed yet")
    
    # Test 3: Security Assessment (our new feature)
    try:
        response = requests.get(f"{base_url}/security-assessment.html", timeout=5)
        print(f"Security Assessment Page: {response.status_code} - {'✓ Available' if response.status_code == 200 else '✗ Not Available'}")
    except Exception as e:
        print(f"Security Assessment Page: ✗ Not Available")
        
    print("\\nNext step: Deploy Live Security Assessment Tool backend API")

if __name__ == "__main__":
    check_server_status()
"""
        
        status_file = "deployment/scripts/check_server_status.py"
        with open(status_file, 'w') as f:
            f.write(status_script)
            
        self.log(f"✓ Status check script created: {status_file}")
        return status_file
        
    def run_deployment_preparation(self):
        """Prepare for actual deployment"""
        self.log("STARTING ACTUAL DEPLOYMENT PREPARATION")
        self.log("=" * 50)
        
        # Step 1: Verify package
        archive_path = self.verify_deployment_package()
        if not archive_path:
            self.log("✗ Cannot proceed without deployment package")
            return False
            
        # Step 2: Check server
        if not self.check_production_server():
            self.log("✗ Cannot reach production server")
            return False
            
        # Step 3: Create status check
        status_script = self.create_server_status_check()
        
        # Step 4: Show deployment commands
        self.show_deployment_commands(archive_path)
        
        self.log("=" * 50)
        self.log("DEPLOYMENT PREPARATION COMPLETE")
        self.log(f"✓ Archive ready: {archive_path}")
        self.log(f"✓ Server accessible: {self.domain}")
        self.log(f"✓ Commands ready: deployment/instructions/LIVE_DEPLOYMENT_COMMANDS.txt")
        self.log(f"✓ Status check: {status_script}")
        
        return True

if __name__ == "__main__":
    deployer = ActualDeployment()
    success = deployer.run_deployment_preparation()
    
    if success:
        print("\\n🚀 READY FOR LIVE DEPLOYMENT!")
        print("\\nNext steps:")
        print("1. Run: python deployment/scripts/check_server_status.py")
        print("2. Execute the deployment commands shown above")
        print("3. Test the Live Security Assessment Tool")
    else:
        print("\\n❌ Deployment preparation failed")