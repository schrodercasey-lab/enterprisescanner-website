#!/usr/bin/env python3
"""
Enterprise Scanner - Local Development Server
Serves the professional homepage locally for development and testing
"""

from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)

# Read the homepage content
def get_homepage_content():
    try:
        with open('website/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enterprise Scanner - Development</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #0f172a; }
                .status { background: #10b981; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; }
                .info { background: #fbbf24; color: #0f172a; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Enterprise Scanner - Local Development Server</h1>
                <div class="status">✅ Server Running on localhost:5000</div>
                
                <div class="info">
                    <strong>📁 File Not Found:</strong> website/index.html<br>
                    The homepage file was not found in the expected location.
                </div>
                
                <h2>🔧 Development Status</h2>
                <ul>
                    <li>✅ Flask Server: Running</li>
                    <li>✅ Port 5000: Available</li>
                    <li>❌ Homepage File: Missing</li>
                    <li>🌐 Live Site: https://enterprisescanner.com (working)</li>
                </ul>
                
                <h2>📊 Available Endpoints</h2>
                <ul>
                    <li><a href="/">/ - Homepage (this page)</a></li>
                    <li><a href="/status">Status Check</a></li>
                    <li><a href="/test">Test Page</a></li>
                </ul>
                
                <p><strong>Next Steps:</strong> Create or copy the homepage file to website/index.html</p>
            </div>
        </body>
        </html>
        """

@app.route('/')
def homepage():
    content = get_homepage_content()
    return content

@app.route('/status')
def status():
    return {
        "status": "running",
        "server": "Enterprise Scanner Local Dev",
        "port": 5000,
        "homepage_file_exists": os.path.exists('website/index.html'),
        "live_site": "https://enterprisescanner.com"
    }

@app.route('/test')
def test():
    return """
    <h1>🧪 Test Page</h1>
    <p>Local development server is working correctly!</p>
    <p><a href="/">← Back to Homepage</a></p>
    """

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('website/assets', filename)

if __name__ == '__main__':
    print("🚀 Starting Enterprise Scanner Local Development Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🌐 Live site: https://enterprisescanner.com")
    print("🔧 Press Ctrl+C to stop the server")
    print("")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )