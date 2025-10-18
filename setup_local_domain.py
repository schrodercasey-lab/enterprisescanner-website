#!/usr/bin/env python3
"""
Enterprise Scanner - Local Domain and SSL Testing Setup
Simulates enterprisescanner.com locally for development and testing
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def is_admin():
    """Check if running with administrator privileges"""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def modify_hosts_file():
    """Add enterprisescanner.com to hosts file for local testing"""
    if platform.system() == "Windows":
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    else:
        hosts_path = "/etc/hosts"
    
    domain_entries = [
        "127.0.0.1 enterprisescanner.com",
        "127.0.0.1 www.enterprisescanner.com"
    ]
    
    print("🌐 Configuring local domain simulation...")
    
    try:
        # Read existing hosts file
        with open(hosts_path, 'r') as f:
            content = f.read()
        
        # Check if entries already exist
        if "enterprisescanner.com" in content:
            print("✅ Domain entries already exist in hosts file")
            return True
        
        # Add domain entries
        with open(hosts_path, 'a') as f:
            f.write("\n# Enterprise Scanner Local Testing\n")
            for entry in domain_entries:
                f.write(f"{entry}\n")
        
        print("✅ Added domain entries to hosts file:")
        for entry in domain_entries:
            print(f"   {entry}")
        
        return True
        
    except PermissionError:
        print("❌ Permission denied. Please run as Administrator/root")
        return False
    except Exception as e:
        print(f"❌ Error modifying hosts file: {e}")
        return False

def create_self_signed_certificate():
    """Create self-signed SSL certificate for local testing"""
    print("🔒 Creating self-signed SSL certificate...")
    
    ssl_dir = Path("deployment/ssl")
    ssl_dir.mkdir(exist_ok=True)
    
    cert_path = ssl_dir / "cert.pem"
    key_path = ssl_dir / "key.pem"
    
    # Create OpenSSL configuration
    config_content = """
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = California
L = San Francisco
O = Enterprise Scanner
CN = enterprisescanner.com

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = enterprisescanner.com
DNS.2 = www.enterprisescanner.com
DNS.3 = localhost
IP.1 = 127.0.0.1
"""
    
    config_path = ssl_dir / "openssl.conf"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    try:
        # Generate private key and certificate
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(key_path),
            "-out", str(cert_path),
            "-days", "365",
            "-nodes",
            "-config", str(config_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSL certificate created successfully:")
            print(f"   Certificate: {cert_path}")
            print(f"   Private Key: {key_path}")
            return True
        else:
            print(f"❌ Error creating certificate: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL first.")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("   Or use: choco install openssl")
        return False
    except Exception as e:
        print(f"❌ Error creating certificate: {e}")
        return False

def create_local_nginx_config():
    """Create nginx configuration for local testing"""
    print("⚙️ Creating local nginx configuration...")
    
    config_dir = Path("deployment/configs")
    config_dir.mkdir(exist_ok=True)
    
    config_content = """
# Enterprise Scanner - Local Testing Nginx Configuration
# For testing enterprisescanner.com locally

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    # Logging
    access_log logs/access.log;
    error_log logs/error.log;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
    
    # HTTP server - redirect to HTTPS
    server {
        listen 80;
        server_name enterprisescanner.com www.enterprisescanner.com localhost;
        
        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name enterprisescanner.com www.enterprisescanner.com localhost;
        
        # SSL Configuration
        ssl_certificate ../ssl/cert.pem;
        ssl_private_key ../ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        
        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # Document root
        root ../../../website;
        index index.html crm-dashboard.html;
        
        # Main location
        location / {
            try_files $uri $uri/ @flask;
        }
        
        # Proxy to Flask application
        location @flask {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
        
        # API endpoints
        location /api/ {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Static files
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Security
        location ~ /\. {
            deny all;
        }
    }
}
"""
    
    config_path = config_dir / "nginx_local.conf"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Local nginx configuration created: {config_path}")
    return config_path

def create_local_test_script():
    """Create script to test local domain setup"""
    print("🧪 Creating local testing script...")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Enterprise Scanner - Local Domain Testing Script
Tests the local enterprisescanner.com setup
\"\"\"

import requests
import ssl
import socket
from urllib.parse import urlparse
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def test_domain_resolution():
    \"\"\"Test if domain resolves to localhost\"\"\"
    print("🔍 Testing domain resolution...")
    
    try:
        import socket
        ip = socket.gethostbyname('enterprisescanner.com')
        if ip == '127.0.0.1':
            print("✅ enterprisescanner.com resolves to 127.0.0.1")
            return True
        else:
            print(f"❌ enterprisescanner.com resolves to {ip} (expected 127.0.0.1)")
            return False
    except Exception as e:
        print(f"❌ Domain resolution failed: {e}")
        return False

def test_flask_app():
    \"\"\"Test if Flask application is running\"\"\"
    print("🔍 Testing Flask application...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Flask application is running on port 5000")
            return True
        else:
            print(f"❌ Flask application returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask application is not running")
        print("   Start it with: python start_production.py")
        return False
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False

def test_ssl_certificate():
    \"\"\"Test SSL certificate\"\"\"
    print("🔍 Testing SSL certificate...")
    
    try:
        # Test SSL connection
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection(('enterprisescanner.com', 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='enterprisescanner.com') as ssock:
                cert = ssock.getpeercert()
                print("✅ SSL certificate is working")
                print(f"   Subject: {cert.get('subject', 'Unknown')}")
                return True
                
    except Exception as e:
        print(f"❌ SSL certificate test failed: {e}")
        return False

def test_https_redirect():
    \"\"\"Test HTTP to HTTPS redirect\"\"\"
    print("🔍 Testing HTTPS redirect...")
    
    try:
        response = requests.get('http://enterprisescanner.com', allow_redirects=False, timeout=5, verify=False)
        if response.status_code in [301, 302] and 'https://' in response.headers.get('Location', ''):
            print("✅ HTTP to HTTPS redirect is working")
            return True
        else:
            print(f"❌ HTTP redirect failed (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Redirect test failed: {e}")
        return False

def test_crm_dashboard():
    \"\"\"Test CRM dashboard accessibility\"\"\"
    print("🔍 Testing CRM dashboard...")
    
    try:
        response = requests.get('https://enterprisescanner.com/crm-dashboard.html', 
                              timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ CRM dashboard is accessible")
            return True
        else:
            print(f"❌ CRM dashboard returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CRM dashboard test failed: {e}")
        return False

def test_api_endpoints():
    \"\"\"Test API endpoints\"\"\"
    print("🔍 Testing API endpoints...")
    
    try:
        response = requests.get('https://enterprisescanner.com/api/health', 
                              timeout=10, verify=False)
        if response.status_code in [200, 401]:  # 401 is OK (means auth is working)
            print("✅ API endpoints are accessible")
            return True
        else:
            print(f"❌ API endpoints returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    \"\"\"Run all tests\"\"\"
    print("🧪 Enterprise Scanner - Local Domain Testing")
    print("=" * 50)
    
    tests = [
        test_domain_resolution,
        test_flask_app,
        test_ssl_certificate,
        test_https_redirect,
        test_crm_dashboard,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Local setup is working correctly.")
        print("")
        print("🌐 Access points:")
        print("   https://enterprisescanner.com")
        print("   https://enterprisescanner.com/crm-dashboard.html")
        print("   https://enterprisescanner.com/api/")
    else:
        print("⚠️  Some tests failed. Check the setup and try again.")
        print("")
        print("💡 Common solutions:")
        print("   - Make sure Flask app is running: python start_production.py")
        print("   - Check hosts file has domain entries")
        print("   - Verify SSL certificates exist in deployment/ssl/")
        print("   - Make sure nginx is configured and running")

if __name__ == "__main__":
    main()
"""
    
    script_path = Path("test_local_domain.py")
    with open(script_path, 'w') as f:
        f.write(test_script)
    
    print(f"✅ Local testing script created: {script_path}")
    return script_path

def main():
    """Main setup function"""
    print("🌐 Enterprise Scanner - Local Domain and SSL Setup")
    print("=" * 55)
    print("Setting up local testing environment for enterprisescanner.com")
    print()
    
    if not is_admin():
        print("⚠️  Administrator privileges required for hosts file modification")
        print("Please run this script as Administrator (Windows) or with sudo (Linux/Mac)")
        print()
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Modify hosts file
    if modify_hosts_file():
        success_count += 1
    
    # Step 2: Create SSL certificate
    if create_self_signed_certificate():
        success_count += 1
    
    # Step 3: Create nginx config
    if create_local_nginx_config():
        success_count += 1
    
    # Step 4: Create test script
    if create_local_test_script():
        success_count += 1
    
    print()
    print("=" * 55)
    print(f"Setup completed: {success_count}/{total_steps} steps successful")
    print()
    
    if success_count == total_steps:
        print("🎉 Local domain and SSL setup completed successfully!")
        print()
        print("✅ Next steps:")
        print("   1. Start Flask application: python start_production.py")
        print("   2. (Optional) Configure local nginx with created config")
        print("   3. Test the setup: python test_local_domain.py")
        print("   4. Access: https://enterprisescanner.com")
        print()
        print("🔗 Local access points:")
        print("   https://enterprisescanner.com")
        print("   https://enterprisescanner.com/crm-dashboard.html")
        print("   https://enterprisescanner.com/api/")
        print()
    else:
        print("⚠️  Setup partially completed. Check errors above.")
        print()
        print("💡 Common issues:")
        print("   - Run as Administrator for hosts file access")
        print("   - Install OpenSSL for certificate generation")
        print("   - Check file permissions")
    
    print("📋 Files created:")
    print("   - deployment/ssl/cert.pem (SSL certificate)")
    print("   - deployment/ssl/key.pem (SSL private key)")
    print("   - deployment/configs/nginx_local.conf (nginx config)")
    print("   - test_local_domain.py (testing script)")
    print()

if __name__ == "__main__":
    main()