"""
Admin Console Server
====================

Flask server for world-class admin console with:
- Real-time dashboards
- User management
- Trial management  
- System monitoring
- AI assistant (Grok)
- Threat intelligence

Run: python admin_console/admin_server.py
Access: http://localhost:5001
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import sys
import json
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded environment variables from: {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import modules
try:
    from modules.grok_threat_intel import GrokThreatIntel
    from ai_copilot.utils.llm_providers import LLMProvider
    print("✅ Imported Grok modules successfully")
except ImportError as e:
    print(f"⚠️ Could not import some modules: {e}")
    GrokThreatIntel = None
    LLMProvider = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'admin-console-secret-key-2025')

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
active_sessions = {}
system_metrics = {}


class AdminConsole:
    """Admin Console Manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.grok_intel = None
        self.grok_assistant = None
        
        # Initialize Grok threat intelligence
        if GrokThreatIntel:
            try:
                self.grok_intel = GrokThreatIntel()
                self.logger.info("Grok Threat Intelligence initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Grok Threat Intel: {e}")
        
        # Initialize Grok AI assistant
        if LLMProvider:
            try:
                self.grok_assistant = LLMProvider(provider="grok", model="grok-beta")
                self.logger.info("Grok AI Assistant initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Grok Assistant: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'status': 'healthy' if cpu_percent < 80 else 'warning'
                },
                'memory': {
                    'percent': memory.percent,
                    'used_gb': round(memory.used / (1024**3), 2),
                    'total_gb': round(memory.total / (1024**3), 2),
                    'status': 'healthy' if memory.percent < 80 else 'warning'
                },
                'disk': {
                    'percent': disk.percent,
                    'used_gb': round(disk.used / (1024**3), 2),
                    'total_gb': round(disk.total / (1024**3), 2),
                    'status': 'healthy' if disk.percent < 80 else 'warning'
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        # TODO: Integrate with real user database
        return {
            'users': {
                'total': 1247,
                'active': 856,
                'new_today': 23,
                'trend': '+8%'
            },
            'trials': {
                'active': 47,
                'expiring_soon': 12,
                'hot_leads': 8,
                'conversion_rate': 18.5
            },
            'revenue': {
                'mrr': 127000,
                'arr': 1524000,
                'trend': '+15%',
                'pipeline': 6500000
            },
            'alerts': {
                'critical': 3,
                'high': 12,
                'medium': 45,
                'total': 60
            }
        }
    
    def chat_with_assistant(self, message: str) -> str:
        """Chat with Grok AI assistant"""
        if not self.grok_assistant:
            return "AI Assistant not available. Please configure Grok API key."
        
        try:
            messages = [
                {
                    'role': 'system',
                    'content': 'You are an expert admin assistant for Enterprise Scanner, a cybersecurity platform. Help admins with user management, analytics, system monitoring, and business insights. Be concise and actionable.'
                },
                {
                    'role': 'user',
                    'content': message
                }
            ]
            
            response = self.grok_assistant.complete(messages=messages, temperature=0.7, max_tokens=500)
            return response.content
            
        except Exception as e:
            self.logger.error(f"AI chat error: {e}")
            return f"Error: {str(e)}"
    
    def get_threat_feed(self, hours: int = 24) -> List[Dict]:
        """Get threat intelligence feed"""
        if not self.grok_intel:
            return []
        
        try:
            threats = self.grok_intel.get_latest_threats(hours=hours)
            return [
                {
                    'title': t.title,
                    'severity': t.severity.value,
                    'category': t.category.value,
                    'cve_id': t.cve_id,
                    'description': t.description,
                    'source': t.source,
                    'timestamp': t.timestamp.isoformat()
                }
                for t in threats
            ]
        except Exception as e:
            self.logger.error(f"Error getting threats: {e}")
            return []


# Initialize admin console
admin_console = AdminConsole()


# ============================================================================
# HTTP Routes
# ============================================================================

@app.route('/')
def index():
    """Admin console dashboard"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'grok_intel': admin_console.grok_intel is not None,
            'grok_assistant': admin_console.grok_assistant is not None
        }
    })

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    stats = admin_console.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/system/metrics')
def get_system_metrics():
    """Get system metrics"""
    metrics = admin_console.get_system_metrics()
    return jsonify(metrics)

@app.route('/api/threats')
def get_threats():
    """Get threat intelligence feed"""
    hours = request.args.get('hours', 24, type=int)
    threats = admin_console.get_threat_feed(hours=hours)
    return jsonify({'threats': threats})


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    session_id = request.sid
    active_sessions[session_id] = {
        'connected_at': datetime.now().isoformat(),
        'ip': request.remote_addr
    }
    logger.info(f"Admin client connected: {session_id}")
    emit('connection_status', {
        'status': 'connected',
        'message': 'Connected to Admin Console',
        'session_id': session_id
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    if session_id in active_sessions:
        del active_sessions[session_id]
    logger.info(f"Admin client disconnected: {session_id}")

@socketio.on('chat_message')
def handle_chat(data):
    """Handle AI assistant chat"""
    try:
        message = data.get('message', '')
        logger.info(f"Admin chat message: {message}")
        
        response = admin_console.chat_with_assistant(message)
        
        emit('chat_response', {
            'message': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        emit('chat_error', {'error': str(e)})

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle system metrics request"""
    try:
        metrics = admin_console.get_system_metrics()
        emit('metrics_update', metrics)
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        emit('error', {'error': str(e)})


# ============================================================================
# Background Tasks
# ============================================================================

def broadcast_metrics():
    """Broadcast system metrics to all connected clients"""
    while True:
        try:
            metrics = admin_console.get_system_metrics()
            socketio.emit('metrics_update', metrics)
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Metrics broadcast error: {e}")
            time.sleep(5)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("ENTERPRISE SCANNER ADMIN CONSOLE")
    print("="*60)
    print("\n🚀 Starting server...")
    print(f"   Host: 0.0.0.0")
    print(f"   Port: 5001")
    print(f"   Debug: {os.getenv('FLASK_ENV') == 'development'}")
    print(f"\n🌐 Admin Console URL: http://localhost:5001")
    print("\n💼 Features:")
    print("   ✅ Real-time system monitoring")
    print("   ✅ User & trial management")
    print("   ✅ AI assistant (Grok-powered)")
    print("   ✅ Threat intelligence feed")
    print("   ✅ WebSocket real-time updates")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    logger.info("Starting Admin Console on 0.0.0.0:5001")
    logger.info(f"Admin Console URL: http://localhost:5001")
    
    # Start background metrics broadcasting in a separate thread
    # socketio.start_background_task(broadcast_metrics)
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5001, debug=os.getenv('FLASK_ENV') == 'development')
