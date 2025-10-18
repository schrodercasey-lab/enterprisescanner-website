from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Scanner - Local Dev</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }
            h1 { color: #0f172a; }
            .status { background: #10b981; color: white; padding: 10px 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Enterprise Scanner - Local Development</h1>
            <div class="status">✅ Server Running on localhost:5000</div>
            <br>
            <p><strong>🌐 Live Production Site:</strong> <a href="https://enterprisescanner.com">https://enterprisescanner.com</a></p>
            <p><strong>📊 Status:</strong> All systems operational</p>
            <p><strong>🔧 Local Development:</strong> Ready for testing</p>
        </div>
    </body>
    </html>
    '''

@app.route('/status')
def status():
    return {"status": "running", "port": 5000, "live_site": "https://enterprisescanner.com"}

if __name__ == '__main__':
    print("🚀 Starting Enterprise Scanner Local Server...")
    print("📍 Available at: http://localhost:5000")
    print("🌐 Live site: https://enterprisescanner.com")
    app.run(host='127.0.0.1', port=5000, debug=False)