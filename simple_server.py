#!/usr/bin/env python3
"""
Enterprise Scanner - Simple HTTP File Server
Creates a local server to serve the homepage file for easy deployment
"""

import http.server
import socketserver
import os
import webbrowser
import threading
import time

def create_simple_server():
    """Create a simple HTTP server to serve files"""
    
    # Change to website directory
    os.chdir('website')
    
    PORT = 8000
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print("🚀 ENTERPRISE SCANNER - FILE SERVER")
            print("=" * 50)
            print(f"📁 Serving files from: {os.getcwd()}")
            print(f"🌐 Server running at: http://localhost:{PORT}")
            print(f"📄 Homepage URL: http://localhost:{PORT}/index.html")
            print("")
            print("MANUAL DEPLOYMENT OPTIONS:")
            print("=" * 30)
            print("1. Download index.html from the server above")
            print("2. Use any FTP client to upload to 134.199.147.45")
            print("3. Or copy-paste the file content manually")
            print("")
            print("📋 Server Details:")
            print(f"   Host: 134.199.147.45")
            print(f"   Username: root")
            print(f"   Password: Schroeder123!")
            print(f"   Target: /var/www/html/index.html")
            print("")
            print("Press Ctrl+C to stop server")
            
            # Open browser
            webbrowser.open(f'http://localhost:{PORT}/index.html')
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    create_simple_server()