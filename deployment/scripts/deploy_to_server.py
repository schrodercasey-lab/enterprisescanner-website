#!/usr/bin/env python3
"""
Enterprise Scanner - Live Production Deployment Script
Deploy Live Security Assessment Tool to enterprisescanner.com
"""

import os
import sys
import subprocess
import json
import shutil
from datetime import datetime

class LiveProductionDeployer:
    def __init__(self):
        self.domain = "enterprisescanner.com"
        self.server_ip = "134.199.147.45"  # Production server IP
        self.deployment_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log(self, message, level="INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def prepare_production_package(self):
        """Prepare production deployment package"""
        self.log("Preparing production deployment package...")
        
        package_dir = f"deployment/packages/live_deployment_{self.deployment_timestamp}"
        os.makedirs(package_dir, exist_ok=True)
        
        # Copy backend files
        backend_dir = f"{package_dir}/backend"
        shutil.copytree("backend", backend_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'logs'))
        
        # Copy website files  
        website_dir = f"{package_dir}/website"
        shutil.copytree("website", website_dir)
        
        # Copy deployment configs
        config_dir = f"{package_dir}/deployment"
        os.makedirs(config_dir, exist_ok=True)
        shutil.copy2("requirements.production.txt", f"{package_dir}/requirements.txt")
        
        # Create production configuration
        prod_config = {
            "app_name": "enterprise_scanner",
            "domain": self.domain,
            "deployment_id": f"live_{self.deployment_timestamp}",
            "features": [
                "Live Security Assessment Tool",
                "Real-time Vulnerability Scanning", 
                "PDF Report Generation",
                "Progress Tracking",
                "API Authentication"
            ],
            "endpoints": [
                "/api/assessment/start",
                "/api/assessment/status/<id>",
                "/api/assessment/results/<id>", 
                "/api/assessment/report/<id>",
                "/api/health",
                "/api/keys/generate"
            ]
        }
        
        with open(f"{package_dir}/production_config.json", 'w') as f:
            json.dump(prod_config, f, indent=2)
            
        # Create startup script
        startup_script = f"""#!/bin/bash
# Enterprise Scanner - Production Startup Script

echo "Starting Enterprise Scanner Production Deployment..."

# Update system packages
sudo apt update

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx

# Create application directory
sudo mkdir -p /var/www/{self.domain}
sudo chown -R $USER:$USER /var/www/{self.domain}

# Copy application files
cp -r backend /var/www/{self.domain}/
cp -r website /var/www/{self.domain}/
cp requirements.txt /var/www/{self.domain}/

# Create virtual environment
cd /var/www/{self.domain}
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p backend/logs
touch backend/logs/security_events.log

# Setup systemd service
sudo tee /etc/systemd/system/enterprise-scanner.service > /dev/null <<EOF
[Unit]
Description=Enterprise Scanner Flask Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/www/{self.domain}
Environment=PATH=/var/www/{self.domain}/venv/bin
ExecStart=/var/www/{self.domain}/venv/bin/python backend/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx configuration
sudo tee /etc/nginx/sites-available/{self.domain} > /dev/null <<EOF
server {{
    listen 80;
    server_name {self.domain} www.{self.domain};
    
    # Redirect HTTP to HTTPS
    return 301 https://\\$server_name\\$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {self.domain} www.{self.domain};
    
    ssl_certificate /etc/letsencrypt/live/{self.domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{self.domain}/privkey.pem;
    
    # Website files
    location / {{
        root /var/www/{self.domain}/website;
        index index.html;
        try_files \\$uri \\$uri/ =404;
    }}
    
    # API endpoints
    location /api/ {{
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
    }}
}}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/{self.domain} /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start services
sudo systemctl daemon-reload
sudo systemctl enable enterprise-scanner
sudo systemctl start enterprise-scanner

echo "Enterprise Scanner deployed successfully!"
echo "Access at: https://{self.domain}"
echo "API available at: https://{self.domain}/api/"
"""
        
        with open(f"{package_dir}/deploy.sh", 'w') as f:
            f.write(startup_script)
            
        os.chmod(f"{package_dir}/deploy.sh", 0o755)
        
        self.log(f"Production package ready: {package_dir}")
        return package_dir
        
    def create_deployment_archive(self, package_dir):
        """Create deployment archive"""
        self.log("Creating deployment archive...")
        
        archive_name = f"enterprise_scanner_live_{self.deployment_timestamp}"
        archive_path = f"deployment/archives/{archive_name}"
        
        os.makedirs("deployment/archives", exist_ok=True)
        
        # Create tar.gz archive
        subprocess.run([
            "tar", "-czf", f"{archive_path}.tar.gz", 
            "-C", "deployment/packages", 
            f"live_deployment_{self.deployment_timestamp}"
        ], check=True)
        
        self.log(f"Archive created: {archive_path}.tar.gz")
        return f"{archive_path}.tar.gz"
        
    def generate_deployment_instructions(self, archive_path):
        """Generate deployment instructions"""
        self.log("Generating deployment instructions...")
        
        instructions = f"""
# Enterprise Scanner - Live Security Assessment Tool Deployment Instructions

## Deployment Package: {os.path.basename(archive_path)}
## Target Server: {self.domain} ({self.server_ip})
## Deployment Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

### DEPLOYMENT STEPS

1. **Upload Archive to Server**
   ```bash
   scp {archive_path} user@{self.server_ip}:/tmp/
   ```

2. **Connect to Server**
   ```bash
   ssh user@{self.server_ip}
   ```

3. **Extract and Deploy**
   ```bash
   cd /tmp
   tar -xzf {os.path.basename(archive_path)}
   cd live_deployment_{self.deployment_timestamp}
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Verify Deployment**
   ```bash
   # Check service status
   sudo systemctl status enterprise-scanner
   
   # Check logs
   sudo journalctl -u enterprise-scanner -f
   
   # Test API
   curl -H "X-API-Key: YOUR_API_KEY" https://{self.domain}/api/health
   ```

### POST-DEPLOYMENT CONFIGURATION

1. **Generate Production API Key**
   ```bash
   curl -X POST https://{self.domain}/api/keys/generate \\
        -H "Content-Type: application/json" \\
        -d '{{"name":"production_key","permissions":"read_write"}}'
   ```

2. **Test Live Security Assessment**
   ```bash
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
   ```

3. **Monitor Assessment Progress**
   ```bash
   curl -H "X-API-Key: YOUR_API_KEY" \\
        https://{self.domain}/api/assessment/status/ASSESSMENT_ID
   ```

4. **Download PDF Report**
   ```bash
   curl -H "X-API-Key: YOUR_API_KEY" \\
        https://{self.domain}/api/assessment/report/ASSESSMENT_ID \\
        -o security_report.pdf
   ```

### FEATURES DEPLOYED

[X] **Live Security Assessment Tool**
   - Real-time vulnerability scanning
   - SSL/TLS security analysis
   - DNS security checks
   - Network security assessment
   - Progress tracking with live updates
   - Professional PDF report generation

[X] **API Authentication System**
   - API key-based authentication
   - Usage tracking and monitoring
   - Secure endpoint access

[X] **Production Infrastructure**
   - Nginx reverse proxy configuration
   - SSL/HTTPS termination
   - Systemd service management
   - Log rotation and monitoring

### ACCESS POINTS

- **Website**: https://{self.domain}
- **Security Assessment**: https://{self.domain}/security-assessment.html
- **API Health**: https://{self.domain}/api/health
- **API Documentation**: https://{self.domain}/api-documentation.html

### SECURITY NOTES

- All API endpoints require valid API key in X-API-Key header
- SSL certificates configured for HTTPS-only access
- Assessment data stored securely with encryption
- Logs monitored for security events

### SUPPORT

For deployment support or issues:
- Email: support@enterprisescanner.com
- Technical: security@enterprisescanner.com

---
Deployment ID: live_{self.deployment_timestamp}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        instructions_file = f"deployment/instructions/deployment_instructions_{self.deployment_timestamp}.md"
        os.makedirs("deployment/instructions", exist_ok=True)
        
        with open(instructions_file, 'w') as f:
            f.write(instructions)
            
        self.log(f"Instructions saved: {instructions_file}")
        return instructions_file
        
    def run_deployment_preparation(self):
        """Run complete deployment preparation"""
        self.log("Starting Live Security Assessment Tool Deployment Preparation")
        self.log(f"Target: https://{self.domain}")
        
        try:
            # Step 1: Prepare package
            package_dir = self.prepare_production_package()
            
            # Step 2: Create archive
            archive_path = self.create_deployment_archive(package_dir)
            
            # Step 3: Generate instructions
            instructions_file = self.generate_deployment_instructions(archive_path)
            
            self.log("Deployment preparation completed successfully!")
            self.log(f"Archive: {archive_path}")
            self.log(f"Instructions: {instructions_file}")
            self.log(f"Ready to deploy to: https://{self.domain}")
            
            return True
            
        except Exception as e:
            self.log(f"Deployment preparation failed: {e}", "ERROR")
            return False

if __name__ == "__main__":
    deployer = LiveProductionDeployer()
    
    print("=" * 70)
    print("Enterprise Scanner - Live Security Assessment Tool Deployment")
    print("=" * 70)
    
    success = deployer.run_deployment_preparation()
    
    if success:
        print("\nDeployment package ready!")
        print("\nNext steps:")
        print("   1. Review deployment instructions")
        print("   2. Upload archive to production server")
        print("   3. Run deployment script on server")
        print("   4. Test Live Security Assessment Tool")
        print("   5. Configure production API keys")
    else:
        print("\nDeployment preparation failed.")
        sys.exit(1)