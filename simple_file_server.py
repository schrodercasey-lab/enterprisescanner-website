#!/usr/bin/env python3
"""
Enterprise Scanner - Simple HTTP File Server
Create a local server to serve the homepage file for easy copying
"""

import os
import http.server
import socketserver
import webbrowser
from pathlib import Path

def create_upload_server():
    """Create a simple HTTP server to serve the homepage file"""
    
    # Change to website directory
    os.chdir("website")
    
    # Set up server
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("ENTERPRISE SCANNER - FILE SERVER READY")
        print("=" * 60)
        print(f"🌐 Server running at: http://localhost:{PORT}")
        print(f"📁 Homepage file: http://localhost:{PORT}/index.html")
        print("")
        print("📋 DEPLOYMENT INSTRUCTIONS:")
        print("1. Open your cloud provider's web console")
        print("2. Access your server terminal (134.199.147.45)")
        print("3. Run this command on your server:")
        print("")
        print("   wget http://YOUR_IP:8080/index.html -O /var/www/html/index.html")
        print("")
        print("   OR copy-paste the content from:")
        print(f"   http://localhost:{PORT}/index.html")
        print("")
        print("🔧 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Try to open browser
        try:
            webbrowser.open(f"http://localhost:{PORT}/index.html")
        except:
            pass
            
        # Start server
        httpd.serve_forever()

if __name__ == "__main__":
    create_upload_server()