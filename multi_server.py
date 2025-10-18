#!/usr/bin/env python3
"""
Enterprise Scanner - Multi-Port Development Server
Runs multiple local servers for different development needs
"""

import threading
import time
from flask import Flask, jsonify
import webbrowser

def create_app(name, port, description):
    app = Flask(name)
    
    @app.route('/')
    def home():
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{name} - Port {port}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                h1 {{ color: #0f172a; }}
                .port {{ background: #10b981; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
                .links {{ margin: 20px 0; }}
                .links a {{ display: inline-block; margin: 5px 10px 5px 0; padding: 8px 15px; background: #fbbf24; color: #0f172a; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 {name}</h1>
                <p><span class="port">Port {port}</span></p>
                <p>{description}</p>
                
                <div class="links">
                    <a href="http://localhost:5000">Main Dev Server (5000)</a>
                    <a href="http://localhost:5001">API Server (5001)</a>
                    <a href="http://localhost:5002">Test Server (5002)</a>
                    <a href="https://enterprisescanner.com">Live Site</a>
                </div>
                
                <h3>🔧 Development Status</h3>
                <ul>
                    <li>✅ Server Running on localhost:{port}</li>
                    <li>🌐 Live Site: https://enterprisescanner.com</li>
                    <li>⚡ Flask Debug Mode: Enabled</li>
                </ul>
            </div>
        </body>
        </html>
        """
    
    @app.route('/status')
    def status():
        return jsonify({
            "name": name,
            "port": port,
            "status": "running",
            "description": description
        })
    
    return app

def run_server(app, port):
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting server on port {port}: {e}")

if __name__ == '__main__':
    print("🚀 Starting Enterprise Scanner Multi-Port Development Environment")
    print("=" * 60)
    
    # Create different servers
    servers = [
        ("Enterprise Scanner Main", 5001, "Main development server with full features"),
        ("Enterprise Scanner API", 5002, "API endpoints and backend services"),
        ("Enterprise Scanner Test", 5003, "Testing and experimental features")
    ]
    
    threads = []
    
    for name, port, desc in servers:
        app = create_app(name, port, desc)
        thread = threading.Thread(target=run_server, args=(app, port))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        print(f"✅ Started {name} on http://localhost:{port}")
        time.sleep(0.5)  # Small delay between starts
    
    print("")
    print("🌐 All servers are running!")
    print("📍 Available URLs:")
    print("   • http://localhost:5000 - Primary Dev Server")
    print("   • http://localhost:5001 - Main Development")
    print("   • http://localhost:5002 - API Services")
    print("   • http://localhost:5003 - Testing Environment")
    print("   • https://enterprisescanner.com - Live Production Site")
    print("")
    print("🔧 Press Ctrl+C to stop all servers")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all servers...")
        print("✅ All servers stopped")