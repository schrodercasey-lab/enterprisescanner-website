#!/usr/bin/env python3
"""
Localhost Diagnostics - Find and fix server startup issues
"""

import socket
import subprocess
import time
import traceback
from flask import Flask

def test_port_availability(port):
    """Test if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0  # True if port is available
    except Exception as e:
        print(f"Error testing port {port}: {e}")
        return False

def test_basic_flask():
    """Test if basic Flask server can start"""
    try:
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return '<h1>🚀 Localhost Diagnostics</h1><p>Basic Flask server is working!</p>'
        
        print("✅ Flask app creation: SUCCESS")
        
        # Test if we can bind to port 5000
        if test_port_availability(5000):
            print("✅ Port 5000 availability: AVAILABLE")
            print("🌟 Starting basic Flask test server on http://localhost:5000")
            app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
        else:
            print("❌ Port 5000 availability: BLOCKED")
            return False
            
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
        traceback.print_exc()
        return False

def check_all_service_ports():
    """Check availability of all service ports"""
    ports = [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010]
    
    print("\n🔍 PORT AVAILABILITY SCAN:")
    print("=" * 40)
    
    available_ports = []
    blocked_ports = []
    
    for port in ports:
        if test_port_availability(port):
            print(f"✅ Port {port}: AVAILABLE")
            available_ports.append(port)
        else:
            print(f"❌ Port {port}: BLOCKED")
            blocked_ports.append(port)
    
    print(f"\n📊 RESULTS:")
    print(f"Available ports: {available_ports}")
    print(f"Blocked ports: {blocked_ports}")
    
    return available_ports, blocked_ports

def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = [
        'flask',
        'flask_socketio',
        'psutil',
        'reportlab',
        'requests'
    ]
    
    print("\n📦 DEPENDENCY CHECK:")
    print("=" * 30)
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: INSTALLED")
        except ImportError:
            print(f"❌ {dep}: MISSING")

if __name__ == "__main__":
    print("🔧 ENTERPRISE SCANNER - LOCALHOST DIAGNOSTICS")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Check port availability
    available_ports, blocked_ports = check_all_service_ports()
    
    if blocked_ports:
        print(f"\n⚠️  WARNING: {len(blocked_ports)} ports are blocked!")
        print("Run: taskkill /f /im python.exe")
        print("Then try starting services again.")
    
    # Test basic Flask functionality
    print("\n🧪 TESTING BASIC FLASK SERVER:")
    print("=" * 35)
    test_basic_flask()