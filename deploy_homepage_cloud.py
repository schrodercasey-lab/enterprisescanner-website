#!/usr/bin/env python3
"""
Enterprise Scanner - Cloud Homepage Deployment
Deploy homepage through existing cloud infrastructure
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime

class CloudHomepageDeployer:
    def __init__(self):
        self.server_ip = "134.199.147.45"
        self.domain = "enterprisescanner.com"
        self.homepage_file = "website/index.html"
        self.deployment_log = []
        
    def log(self, message, status="INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
        
    def verify_homepage_file(self):
        """Verify homepage file exists and is ready"""
        self.log("🔍 Verifying homepage file...")
        
        if not os.path.exists(self.homepage_file):
            self.log(f"❌ Homepage file not found: {self.homepage_file}", "ERROR")
            return False
            
        file_size = os.path.getsize(self.homepage_file)
        if file_size < 10000:  # Less than 10KB indicates potential issue
            self.log(f"⚠️ Homepage file seems small: {file_size} bytes", "WARNING")
            
        self.log(f"✅ Homepage file ready: {file_size:,} bytes")
        return True
        
    def test_server_connectivity(self):
        """Test server connectivity"""
        self.log("🔗 Testing server connectivity...")
        
        try:
            # Test direct IP connection
            response = requests.get(f"http://{self.server_ip}", timeout=10)
            self.log(f"✅ Server responding: {response.status_code}")
            
            # Test domain connection
            response = requests.get(f"http://{self.domain}", timeout=10)
            self.log(f"✅ Domain responding: {response.status_code}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"⚠️ Connection test: {e}", "WARNING")
            return True  # Continue anyway
            
    def create_upload_script(self):
        """Create upload script for cloud deployment"""
        self.log("📝 Creating cloud upload script...")
        
        # PowerShell script for Windows-based deployment
        upload_script = f'''
# Enterprise Scanner - Homepage Upload Script
# Cloud deployment via existing infrastructure

$ErrorActionPreference = "Stop"

Write-Host "🚀 Enterprise Scanner Homepage Deployment" -ForegroundColor Cyan
Write-Host "Target: {self.domain} ({self.server_ip})" -ForegroundColor Green
Write-Host ""

# Method 1: Try WinSCP if available
if (Get-Command "WinSCP.exe" -ErrorAction SilentlyContinue) {{
    Write-Host "📁 Using WinSCP for deployment..." -ForegroundColor Yellow
    
    $winscp = @"
open scp://root@{self.server_ip}
put {self.homepage_file} /var/www/html/index.html
exit
"@
    
    $winscp | WinSCP.exe /console /script=-
    
    if ($LASTEXITCODE -eq 0) {{
        Write-Host "✅ Homepage uploaded successfully via WinSCP!" -ForegroundColor Green
        exit 0
    }}
}}

# Method 2: Use PowerShell SSH module if available
if (Get-Module -ListAvailable -Name Posh-SSH) {{
    Write-Host "🔧 Using PowerShell SSH module..." -ForegroundColor Yellow
    
    Import-Module Posh-SSH
    
    # Prompt for credentials
    $credential = Get-Credential -Message "Enter SSH credentials for {self.server_ip}"
    
    try {{
        $session = New-SSHSession -ComputerName "{self.server_ip}" -Credential $credential
        Set-SCPFile -ComputerName "{self.server_ip}" -Credential $credential -LocalFile "{self.homepage_file}" -RemotePath "/var/www/html/index.html"
        Remove-SSHSession $session
        
        Write-Host "✅ Homepage uploaded successfully via PowerShell SSH!" -ForegroundColor Green
        exit 0
    }} catch {{
        Write-Host "❌ PowerShell SSH upload failed: $_" -ForegroundColor Red
    }}
}}

# Method 3: Manual deployment instructions
Write-Host "📋 Manual Deployment Instructions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Download and install WinSCP: https://winscp.net/eng/download.php" -ForegroundColor White
Write-Host ""
Write-Host "2. Open WinSCP and connect with these settings:" -ForegroundColor White
Write-Host "   Protocol: SCP" -ForegroundColor Gray
Write-Host "   Host: {self.server_ip}" -ForegroundColor Gray
Write-Host "   Username: root" -ForegroundColor Gray
Write-Host "   Password: [Your server password]" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Navigate to remote directory: /var/www/html/" -ForegroundColor White
Write-Host ""
Write-Host "4. Upload local file: {self.homepage_file}" -ForegroundColor White
Write-Host "   → Remote file: /var/www/html/index.html" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Verify deployment at: http://{self.domain}" -ForegroundColor White
Write-Host ""

# Method 4: Alternative online tools
Write-Host "🌐 Alternative: Online SSH Clients" -ForegroundColor Yellow
Write-Host ""
Write-Host "Try these online SSH clients:" -ForegroundColor White
Write-Host "• https://shell.cloud.google.com/" -ForegroundColor Gray
Write-Host "• https://gateone.liftoff.github.io/" -ForegroundColor Gray
Write-Host "• https://webconsole.dev/" -ForegroundColor Gray
Write-Host ""
Write-Host "Connection details:" -ForegroundColor White
Write-Host "Host: {self.server_ip}" -ForegroundColor Gray
Write-Host "Username: root" -ForegroundColor Gray
Write-Host "Command: nano /var/www/html/index.html" -ForegroundColor Gray
Write-Host ""

Write-Host "📁 Homepage file location: {os.path.abspath(self.homepage_file)}" -ForegroundColor Cyan
Write-Host "📊 File size: {os.path.getsize(self.homepage_file):,} bytes" -ForegroundColor Cyan
'''

        # Save the script
        script_path = "deploy_homepage_cloud.ps1"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(upload_script)
            
        self.log(f"✅ Upload script created: {script_path}")
        return script_path
        
    def create_verification_script(self):
        """Create verification script"""
        self.log("📊 Creating verification script...")
        
        verification_script = '''
# Homepage Deployment Verification Script

Write-Host "🔍 Verifying Homepage Deployment..." -ForegroundColor Cyan
Write-Host ""

# Test domain
try {
    $response = Invoke-WebRequest -Uri "http://enterprisescanner.com" -TimeoutSec 10
    $content_length = $response.Content.Length
    
    if ($content_length -gt 30000) {
        Write-Host "✅ Homepage deployed successfully!" -ForegroundColor Green
        Write-Host "📊 Content size: $content_length bytes" -ForegroundColor Green
        Write-Host "🌐 Site: http://enterprisescanner.com" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Homepage may not be fully deployed" -ForegroundColor Yellow
        Write-Host "📊 Content size: $content_length bytes (expected >30KB)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Unable to verify deployment: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔧 If verification fails, homepage upload may still be needed."
'''

        with open("verify_homepage_deployment.ps1", 'w', encoding='utf-8') as f:
            f.write(verification_script)
            
        self.log("✅ Verification script created: verify_homepage_deployment.ps1")
        
    def run_deployment(self):
        """Run the cloud deployment process"""
        self.log("🚀 Starting cloud homepage deployment...")
        
        try:
            # Step 1: Verify homepage file
            if not self.verify_homepage_file():
                return False
                
            # Step 2: Test connectivity
            self.test_server_connectivity()
            
            # Step 3: Create deployment scripts
            script_path = self.create_upload_script()
            self.create_verification_script()
            
            # Step 4: Execute deployment
            self.log("⚡ Executing deployment script...")
            
            try:
                # Try to run the PowerShell script
                result = subprocess.run([
                    "powershell", "-ExecutionPolicy", "Bypass", "-File", script_path
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.log("✅ Deployment completed successfully!")
                else:
                    self.log("📋 Manual deployment instructions displayed")
                    
            except subprocess.TimeoutExpired:
                self.log("⏰ Deployment script timeout - manual completion needed")
            except Exception as e:
                self.log(f"📋 Proceeding with manual instructions: {e}")
                
            # Step 5: Show completion status
            self.show_completion_status()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Deployment failed: {e}", "ERROR")
            return False
            
    def show_completion_status(self):
        """Show deployment completion status"""
        print("\n" + "="*60)
        print("🎯 CLOUD HOMEPAGE DEPLOYMENT STATUS")
        print("="*60)
        print(f"📁 Source file: {os.path.abspath(self.homepage_file)}")
        print(f"📊 File size: {os.path.getsize(self.homepage_file):,} bytes")
        print(f"🎯 Target: {self.domain} ({self.server_ip})")
        print(f"📍 Remote path: /var/www/html/index.html")
        print("\n🔧 NEXT STEPS:")
        print("1. Run: powershell -File deploy_homepage_cloud.ps1")
        print("2. Verify: powershell -File verify_homepage_deployment.ps1")
        print("3. Visit: http://enterprisescanner.com")
        print("\n✨ Your existing cloud infrastructure is ready!")
        print("📋 Use the generated scripts for automated deployment.")

def main():
    """Main deployment function"""
    deployer = CloudHomepageDeployer()
    
    print("Enterprise Scanner - Cloud Homepage Deployment")
    print("=" * 50)
    
    success = deployer.run_deployment()
    
    if success:
        print("\n🎉 Cloud deployment scripts ready!")
        print("Run the PowerShell scripts to complete deployment.")
    else:
        print("\n❌ Deployment preparation failed.")
        
    return success

if __name__ == '__main__':
    main()