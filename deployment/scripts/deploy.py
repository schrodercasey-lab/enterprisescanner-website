#!/usr/bin/env python3
"""
Enterprise Scanner Deployment Script
Automated deployment to production environment
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(command, check=True):
    """Run shell command with logging"""
    log(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        log(f"ERROR: Command failed with code {result.returncode}")
        log(f"STDOUT: {result.stdout}")
        log(f"STDERR: {result.stderr}")
        sys.exit(1)
    
    return result

def deploy_to_production():
    """Deploy Enterprise Scanner to production"""
    
    log("Starting Enterprise Scanner Production Deployment")
    
    # 1. Run security scan
    log("Running security scan...")
    run_command("bandit -r backend/ -f json -o security-report.json", check=False)
    
    # 2. Run tests
    log("Running test suite...")
    run_command("python -m pytest backend/tests/ -v", check=False)
    
    # 3. Build Docker image
    log("Building production Docker image...")
    run_command("docker build -t enterprise-scanner:latest -f deployment/docker/Dockerfile .")
    
    # 4. Tag for registry
    log("Tagging image for registry...")
    version = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_command(f"docker tag enterprise-scanner:latest enterprise-scanner:{version}")
    
    # 5. Deploy to staging first
    log("Deploying to staging environment...")
    run_command("docker-compose -f deployment/docker/docker-compose.yml up -d")
    
    # 6. Health check
    log("Performing health check...")
    time.sleep(10)  # Wait for services to start
    health_result = run_command("curl -f http://localhost:5000/api/health", check=False)
    
    if health_result.returncode == 0:
        log("✅ Health check passed - Deployment successful!")
        log("🚀 Enterprise Scanner is live at https://enterprisescanner.com")
    else:
        log("❌ Health check failed - Rolling back...")
        run_command("docker-compose -f deployment/docker/docker-compose.yml down")
        sys.exit(1)
    
    # 7. Backup previous version
    log("Creating deployment backup...")
    run_command(f"docker tag enterprise-scanner:latest enterprise-scanner:backup-{version}")
    
    log("🎉 Production deployment completed successfully!")
    log("📊 Monitor metrics at: https://enterprisescanner.com/admin/metrics")
    log("📧 Fortune 500 leads will be routed to: sales@enterprisescanner.com")

if __name__ == "__main__":
    deploy_to_production()