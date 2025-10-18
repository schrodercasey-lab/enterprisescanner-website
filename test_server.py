#!/usr/bin/env python3
"""
Simple Test Server to verify Flask is working
"""

from flask import Flask
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def test():
    return '''
    <html>
    <head><title>Enterprise Scanner Test</title></head>
    <body>
        <h1>✅ Flask Test Server Working!</h1>
        <p>Enterprise Scanner systems are ready to deploy.</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🧪 Starting Flask test server...")
    print("📍 URL: http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)