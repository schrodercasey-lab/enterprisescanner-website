#!/usr/bin/env python3
"""
Enterprise Scanner - Simplified Demo Server
Quick startup for immediate demonstration
"""

import os
import sys
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Set up paths
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKSPACE_ROOT)

print("🚀 Enterprise Scanner - Quick Demo Server")
print("🎯 Starting simplified server for immediate demonstration...")

# Create Flask app
app = Flask(__name__, template_folder='website', static_folder='website')
CORS(app)

# Initialize SocketIO for real-time chat
try:
    from flask_socketio import SocketIO, emit
    # Use threading mode for stability
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    print("✅ Real-time chat system initialized")
    HAS_SOCKETIO = True
except Exception as e:
    print(f"⚠️  SocketIO error: {e}")
    HAS_SOCKETIO = False

# Main website routes
@app.route('/')
def home():
    try:
        return send_from_directory('website', 'index.html')
    except:
        return "<h1>Enterprise Scanner</h1><p>Welcome to the platform!</p>"

@app.route('/chat-demo')
def chat_demo():
    try:
        return send_from_directory('website', 'enterprise-chat-demo.html')
    except:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enterprise Chat Demo</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                .chat-container { max-width: 600px; margin: 0 auto; }
                .message { padding: 10px; margin: 10px 0; border-radius: 5px; }
                .user { background: #e3f2fd; text-align: right; }
                .agent { background: #f3e5f5; text-align: left; }
                input { width: 70%; padding: 10px; }
                button { padding: 10px 20px; background: #1976d2; color: white; border: none; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <h1>🚀 Enterprise Scanner - Live Chat Demo</h1>
                <div id="messages">
                    <div class="message agent">Welcome to Enterprise Scanner! How can I help you with your cybersecurity needs?</div>
                </div>
                <div style="margin-top: 20px;">
                    <input type="text" id="messageInput" placeholder="Type your message..." />
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <script>
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const messages = document.getElementById('messages');
                    
                    if (input.value.trim()) {
                        // Add user message
                        const userMsg = document.createElement('div');
                        userMsg.className = 'message user';
                        userMsg.textContent = input.value;
                        messages.appendChild(userMsg);
                        
                        // Add agent response
                        setTimeout(() => {
                            const agentMsg = document.createElement('div');
                            agentMsg.className = 'message agent';
                            agentMsg.textContent = 'Thank you for your message! Our security experts are reviewing your request and will provide a comprehensive assessment shortly.';
                            messages.appendChild(agentMsg);
                        }, 1000);
                        
                        input.value = '';
                    }
                }
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendMessage();
                });
            </script>
        </body>
        </html>
        '''

@app.route('/analytics')
def analytics():
    try:
        return send_from_directory('website', 'analytics-dashboard.html')
    except:
        return "<h1>Analytics Dashboard</h1><p>Real-time security metrics and insights</p>"

@app.route('/reports')
def reports():
    try:
        return send_from_directory('website', 'pdf-reports.html')
    except:
        return "<h1>PDF Reports</h1><p>Professional security assessment reports</p>"

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('website', filename)
    except:
        return f"File not found: {filename}", 404

# Chat API endpoints
@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    return jsonify({
        'success': True,
        'chat_id': 'demo_chat_123',
        'message': 'Chat started successfully',
        'welcome_message': 'Welcome to Enterprise Scanner! How can I help you today?'
    })

@app.route('/api/chat/message', methods=['POST'])
def send_message():
    data = request.get_json() if request.is_json else {}
    message = data.get('message', '')
    
    # Demo responses based on message content
    if 'demo' in message.lower():
        response = 'I\'d be happy to show you our Fortune 500 security assessment capabilities!'
    elif 'price' in message.lower() or 'cost' in message.lower():
        response = 'Our enterprise packages start at $100K annually with proven ROI of 300-800%.'
    else:
        response = 'Thank you for your message! Our security consultant will respond with a comprehensive analysis.'
    
    return jsonify({
        'success': True,
        'response': response,
        'escalate': 'fortune 500' in message.lower() or 'enterprise' in message.lower()
    })

# SocketIO events for real-time chat
if HAS_SOCKETIO:
    @socketio.on('connect')
    def handle_connect():
        print("💬 Client connected to real-time chat")
        emit('status', {'msg': 'Connected to Enterprise Scanner chat system'})
        
    @socketio.on('disconnect')
    def handle_disconnect():
        print("💬 Client disconnected from chat")
        
    @socketio.on('send_message')
    def handle_message(data):
        print(f"💬 Received message: {data}")
        # Echo back with enterprise response
        emit('receive_message', {
            'message': 'Thank you for contacting Enterprise Scanner. Our security experts are analyzing your request.',
            'timestamp': data.get('timestamp'),
            'type': 'agent'
        })

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'features': {
            'real_time_chat': HAS_SOCKETIO,
            'analytics': True,
            'reports': True,
            'api_security': True
        },
        'message': 'Enterprise Scanner is operational'
    })

if __name__ == '__main__':
    print("\n🎯 Demo Server Ready!")
    print("📍 Access points:")
    print("   Main Site: http://localhost:5000")
    print("   Chat Demo: http://localhost:5000/chat-demo")
    print("   Analytics: http://localhost:5000/analytics")
    print("   Health:    http://localhost:5000/health")
    print("\n🚀 Starting server...")
    
    try:
        if HAS_SOCKETIO:
            print("💬 Real-time chat enabled with SocketIO")
            socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
        else:
            print("📡 Basic HTTP server mode")
            app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")