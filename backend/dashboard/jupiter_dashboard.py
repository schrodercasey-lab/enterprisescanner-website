"""
Jupiter Interactive Dashboard
==============================

Real-time web dashboard for Jupiter security scanner with:
- Live vulnerability visualization
- AI chat with Grok
- Real-time threat intelligence
- Remediation workflow tracking
- WebSocket updates

Flask + SocketIO + Modern UI

Author: Enterprise Scanner Team
Version: 1.0.0
Date: October 18, 2025
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from backend directory
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded environment variables from: {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import Jupiter modules
try:
    from modules.jupiter_integration_hub import JupiterIntegrationHub, process_jupiter_scan
    from modules.test_report_generator import TestReportGenerator
    from modules.grok_threat_intel import GrokThreatIntel, ThreatSeverity
    from ai_copilot.utils.llm_providers import LLMProvider
    from utils.error_handler import (
        retry_with_backoff, with_fallback, CircuitBreaker,
        error_aggregator, graceful_degradation, safe_api_call,
        handle_api_error
    )
    print("✅ Imported Jupiter modules successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import Jupiter modules: {e}")
    # Provide dummy implementations
    JupiterIntegrationHub = None
    TestReportGenerator = None
    GrokThreatIntel = None
    ThreatSeverity = None
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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'jupiter-dashboard-secret-key')

# Enable CORS for development
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
active_scans = {}
chat_history = []
threat_feed = []


class JupiterDashboard:
    """Jupiter Dashboard Manager with Advanced Error Handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jupiter_hub = None
        self.grok_intel = None
        self.grok_chat = None
        
        # Circuit breakers for external services
        self.grok_chat_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.grok_intel_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        
        # Register features with graceful degradation
        graceful_degradation.register_feature(
            'grok_chat',
            enabled=True,
            fallback="I'm currently experiencing connectivity issues. Please try again in a moment."
        )
        graceful_degradation.register_feature(
            'threat_intelligence',
            enabled=True,
            fallback=[]
        )
        graceful_degradation.register_feature(
            'scan_processing',
            enabled=True,
            fallback={'error': 'Scan processing temporarily unavailable'}
        )
        
        # Initialize Jupiter components with error handling
        self._init_jupiter_hub()
        self._init_grok_intel()
        self._init_grok_chat()
    
    def _init_jupiter_hub(self):
        """Initialize Jupiter Hub with retry logic"""
        if not JupiterIntegrationHub:
            self.logger.warning("JupiterIntegrationHub not available")
            graceful_degradation.disable_feature('scan_processing', 'Module not imported')
            return
        
        try:
            self.jupiter_hub = JupiterIntegrationHub()
            self.logger.info("✅ Jupiter Integration Hub initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Jupiter Hub: {e}")
            error_aggregator.record_error('jupiter_hub_init', str(e))
            graceful_degradation.disable_feature('scan_processing', str(e))
    
    def _init_grok_intel(self):
        """Initialize Grok Threat Intelligence with retry logic"""
        if not GrokThreatIntel:
            self.logger.warning("GrokThreatIntel not available")
            graceful_degradation.disable_feature('threat_intelligence', 'Module not imported')
            return
        
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        def _init():
            return GrokThreatIntel()
        
        try:
            self.grok_intel = _init()
            self.logger.info("✅ Grok Threat Intelligence initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Grok Threat Intel: {e}")
            error_aggregator.record_error('grok_intel_init', str(e))
            graceful_degradation.disable_feature('threat_intelligence', str(e))
    
    def _init_grok_chat(self):
        """Initialize Grok Chat with retry logic"""
        if not LLMProvider:
            self.logger.warning("LLMProvider not available")
            graceful_degradation.disable_feature('grok_chat', 'Module not imported')
            return
        
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        def _init():
            return LLMProvider(provider="grok", model="grok-beta")
        
        try:
            self.grok_chat = _init()
            self.logger.info("✅ Grok Chat initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Grok Chat: {e}")
            error_aggregator.record_error('grok_chat_init', str(e))
            graceful_degradation.disable_feature('grok_chat', str(e))
    
    def process_scan(self, scan_data: Dict, scan_id: str) -> Dict:
        """Process Jupiter scan with real-time updates"""
        if not self.jupiter_hub:
            return {"error": "Jupiter Hub not initialized"}
        
        try:
            # Emit starting event
            socketio.emit('scan_started', {
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Process scan
            result = self.jupiter_hub.process_scan_data(scan_data)
            
            # Emit completion event
            socketio.emit('scan_completed', {
                'scan_id': scan_id,
                'result': result.get_summary(),
                'timestamp': datetime.now().isoformat()
            })
            
            return result.to_dict()
            
        except Exception as e:
            self.logger.error(f"Scan processing failed: {e}")
            socketio.emit('scan_error', {
                'scan_id': scan_id,
                'error': str(e)
            })
            return {"error": str(e)}
    
    def chat_with_jupiter(self, message: str) -> str:
        """Chat with Jupiter AI (using Grok) with advanced error handling"""
        
        # Check if feature is enabled
        if not graceful_degradation.is_enabled('grok_chat'):
            return graceful_degradation.get_fallback('grok_chat')
        
        if not self.grok_chat:
            error_msg = "Jupiter AI is not available. Please check the Grok API configuration."
            self.logger.warning(error_msg)
            return error_msg
        
        def _chat():
            """Internal chat function with error handling"""
            try:
                # Build chat context
                messages = [
                    {
                        'role': 'system',
                        'content': 'You are Jupiter, an AI cybersecurity assistant for Enterprise Scanner. You help users understand vulnerabilities, provide remediation advice, explain security concepts, and analyze threats. Be helpful, clear, actionable, and security-focused. If you don\'t know something, say so.'
                    }
                ]
                
                # Add recent chat history (last 10 messages for context)
                for msg in chat_history[-10:]:
                    messages.append(msg)
                
                # Add user message
                messages.append({
                    'role': 'user',
                    'content': message
                })
                
                # Call through circuit breaker
                response = self.grok_chat_breaker.call(
                    self.grok_chat.complete,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=600
                )
                
                # Save to history on success
                chat_history.append({'role': 'user', 'content': message})
                chat_history.append({'role': 'assistant', 'content': response.content})
                
                return response.content
                
            except TimeoutError:
                raise Exception("Request timed out. The AI is taking too long to respond.")
            except Exception as e:
                # Log specific error types
                error_type = type(e).__name__
                self.logger.error(f"Chat error ({error_type}): {e}")
                raise
        
        # Use safe API call with retry and fallback
        result = safe_api_call(
            func=_chat,
            fallback="I'm experiencing technical difficulties right now. My systems are being refreshed. Please try again in a moment, or rephrase your question.",
            max_retries=2,
            log_name="Grok Chat"
        )
        
        # If we got the fallback, it means we failed
        if result == safe_api_call.__defaults__[0]:  # Check if it's the fallback
            error_aggregator.record_error(
                'grok_chat_failure',
                'Multiple chat attempts failed',
                {'message_preview': message[:50]}
            )
        
        return result
    
    def get_threat_feed(self, hours: int = 24) -> List[Dict]:
        """Get latest threat intelligence with error handling"""
        
        # Check if feature is enabled
        if not graceful_degradation.is_enabled('threat_intelligence'):
            self.logger.warning("Threat intelligence feature disabled")
            return graceful_degradation.get_fallback('threat_intelligence')
        
        if not self.grok_intel:
            self.logger.warning("Grok threat intelligence not initialized")
            return []
        
        def _get_threats():
            """Internal function to get threats"""
            threats = self.grok_intel_breaker.call(
                self.grok_intel.get_latest_threats,
                hours=hours
            )
            return [threat.to_dict() for threat in threats]
        
        # Use safe API call with retry
        threats = safe_api_call(
            func=_get_threats,
            fallback=[],
            max_retries=2,
            log_name="Threat Feed"
        )
        
        if not threats:
            error_aggregator.record_error(
                'threat_feed_failure',
                f'Failed to fetch threats for last {hours} hours',
                {'hours': hours}
            )
        
        return threats
    
    def get_community_pulse(self) -> Dict:
        """Get security community pulse with error handling"""
        
        if not graceful_degradation.is_enabled('threat_intelligence'):
            self.logger.warning("Threat intelligence feature disabled")
            return {}
        
        if not self.grok_intel:
            self.logger.warning("Grok threat intelligence not initialized")
            return {}
        
        @retry_with_backoff(max_attempts=2, initial_delay=1.0)
        def _get_pulse():
            """Internal function to get community pulse"""
            pulse = self.grok_intel_breaker.call(
                self.grok_intel.get_community_pulse
            )
            return {
                'trending_topics': pulse.trending_topics,
                'hot_cves': pulse.hot_cves,
                'sentiment': pulse.sentiment,
                'timestamp': pulse.timestamp.isoformat(),
                'status': 'live'
            }
        
        try:
            return _get_pulse()
        except Exception as e:
            self.logger.error(f"Community pulse failed: {e}")
            error_aggregator.record_error(
                'community_pulse_failure',
                str(e),
                {}
            )
            return {
                'trending_topics': [],
                'hot_cves': [],
                'sentiment': 'unknown',
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'message': 'Unable to fetch community pulse data'
            }
    
    def get_error_stats(self) -> Dict:
        """Get error statistics for monitoring"""
        return error_aggregator.get_error_stats()
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Get recent errors for debugging"""
        errors = error_aggregator.get_recent_errors(limit)
        return [{
            'timestamp': e['timestamp'].isoformat(),
            'type': e['type'],
            'message': e['message'],
            'context': e['context']
        } for e in errors]
    
    def get_feature_status(self) -> Dict:
        """Get status of all features"""
        return {
            'grok_chat': {
                'enabled': graceful_degradation.is_enabled('grok_chat'),
                'circuit_breaker': self.grok_chat_breaker.state.value,
                'failures': self.grok_chat_breaker.failure_count
            },
            'threat_intelligence': {
                'enabled': graceful_degradation.is_enabled('threat_intelligence'),
                'circuit_breaker': self.grok_intel_breaker.state.value,
                'failures': self.grok_intel_breaker.failure_count
            },
            'scan_processing': {
                'enabled': graceful_degradation.is_enabled('scan_processing')
            }
        }


# Initialize dashboard
dashboard = JupiterDashboard()


# Routes

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'jupiter_hub': dashboard.jupiter_hub is not None,
            'grok_intel': dashboard.grok_intel is not None,
            'grok_chat': dashboard.grok_chat is not None
        }
    })

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    return jsonify({
        'active_scans': len(active_scans),
        'total_messages': len(chat_history),
        'threat_feed_items': len(threat_feed),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/threat-feed')
def get_threat_feed_api():
    """Get threat intelligence feed"""
    hours = request.args.get('hours', 24, type=int)
    threats = dashboard.get_threat_feed(hours=hours)
    return jsonify({'threats': threats})

@app.route('/api/community-pulse')
def get_community_pulse_api():
    """Get security community pulse"""
    pulse = dashboard.get_community_pulse()
    return jsonify(pulse)

@app.route('/api/error-stats')
def get_error_stats_api():
    """Get error statistics"""
    stats = dashboard.get_error_stats()
    return jsonify(stats)

@app.route('/api/recent-errors')
def get_recent_errors_api():
    """Get recent errors"""
    limit = request.args.get('limit', 10, type=int)
    errors = dashboard.get_recent_errors(limit=limit)
    return jsonify({'errors': errors})

@app.route('/api/feature-status')
def get_feature_status_api():
    """Get feature status and circuit breaker states"""
    status = dashboard.get_feature_status()
    return jsonify(status)

@app.route('/api/reset-circuit-breaker/<feature>')
def reset_circuit_breaker_api(feature):
    """Reset circuit breaker for a feature"""
    try:
        if feature == 'chat':
            dashboard.grok_chat_breaker.reset()
            graceful_degradation.enable_feature('grok_chat')
        elif feature == 'intel':
            dashboard.grok_intel_breaker.reset()
            graceful_degradation.enable_feature('threat_intelligence')
        else:
            return jsonify({'error': 'Unknown feature'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Circuit breaker reset for {feature}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# SocketIO Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'message': 'Connected to Jupiter Dashboard',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('start_scan')
def handle_start_scan(data):
    """Handle scan start request"""
    scan_id = f"SCAN-{int(time.time())}"
    logger.info(f"Starting scan: {scan_id}")
    
    try:
        # Store scan info
        active_scans[scan_id] = {
            'status': 'processing',
            'started_at': datetime.now().isoformat()
        }
        
        # Process scan (in background)
        scan_file = data.get('scan_file')
        scan_data = data.get('scan_data')
        
        if scan_file:
            # Load scan from file
            with open(scan_file, 'r') as f:
                scan_data = json.load(f)
        
        if scan_data:
            result = dashboard.process_scan(scan_data, scan_id)
            
            # Update scan status
            active_scans[scan_id]['status'] = 'completed'
            active_scans[scan_id]['completed_at'] = datetime.now().isoformat()
            active_scans[scan_id]['result'] = result
            
            emit('scan_result', {
                'scan_id': scan_id,
                'result': result
            })
        else:
            emit('scan_error', {
                'scan_id': scan_id,
                'error': 'No scan data provided'
            })
            
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        emit('scan_error', {
            'scan_id': scan_id,
            'error': str(e)
        })

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat message with enhanced error handling"""
    message = data.get('message', '').strip()
    
    if not message:
        emit('chat_error', {
            'error': 'Message cannot be empty',
            'type': 'validation_error'
        })
        return
    
    logger.info(f"💬 Chat message: {message[:50]}...")
    
    try:
        # Emit thinking status
        emit('chat_thinking', {
            'message': 'Jupiter is thinking...',
            'timestamp': datetime.now().isoformat()
        })
        
        # Get response from Jupiter AI
        response = dashboard.chat_with_jupiter(message)
        
        # Check if it's an error response
        is_error = any(keyword in response.lower() for keyword in [
            'not available', 'technical difficulties', 'connectivity issues',
            'experiencing issues', 'unavailable'
        ])
        
        # Emit response
        emit('chat_response', {
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'is_error': is_error,
            'feature_status': dashboard.get_feature_status()
        })
        
        logger.info(f"✅ Chat response sent ({len(response)} chars)")
        
    except Exception as e:
        error_msg = handle_api_error(e, "Chat")
        logger.error(f"❌ Chat error: {error_msg}")
        
        emit('chat_error', {
            'error': error_msg,
            'type': type(e).__name__,
            'timestamp': datetime.now().isoformat(),
            'recoverable': True,
            'suggestion': 'Please try again in a moment, or check the system status.'
        })
        
        # Record error
        error_aggregator.record_error(
            'websocket_chat',
            str(e),
            {'message_length': len(message)}
        )

@socketio.on('request_threats')
def handle_request_threats(data):
    """Handle threat feed request with enhanced error handling"""
    hours = data.get('hours', 24)
    logger.info(f"🔍 Requesting threats for last {hours} hours")
    
    try:
        # Emit loading status
        emit('threats_loading', {
            'message': 'Loading threat intelligence...',
            'timestamp': datetime.now().isoformat()
        })
        
        threats = dashboard.get_threat_feed(hours=hours)
        
        emit('threats_update', {
            'threats': threats,
            'count': len(threats),
            'timestamp': datetime.now().isoformat(),
            'success': True
        })
        
        logger.info(f"✅ Sent {len(threats)} threats")
        
    except Exception as e:
        error_msg = handle_api_error(e, "Threat Feed")
        logger.error(f"❌ Threat feed error: {error_msg}")
        
        emit('threats_error', {
            'error': error_msg,
            'type': type(e).__name__,
            'timestamp': datetime.now().isoformat(),
            'recoverable': True
        })
        
        error_aggregator.record_error(
            'websocket_threats',
            str(e),
            {'hours': hours}
        )

@socketio.on('request_pulse')
def handle_request_pulse():
    """Handle community pulse request with enhanced error handling"""
    logger.info("📊 Requesting community pulse")
    
    try:
        pulse = dashboard.get_community_pulse()
        
        emit('pulse_update', {
            **pulse,
            'success': pulse.get('status') != 'error'
        })
        
        if pulse.get('status') == 'error':
            logger.warning(f"⚠️ Pulse returned error state")
        else:
            logger.info(f"✅ Sent community pulse")
        
    except Exception as e:
        error_msg = handle_api_error(e, "Community Pulse")
        logger.error(f"❌ Pulse error: {error_msg}")
        
        emit('pulse_error', {
            'error': error_msg,
            'type': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        })
        
        error_aggregator.record_error(
            'websocket_pulse',
            str(e),
            {}
        )

@socketio.on('request_status')
def handle_request_status():
    """Handle system status request"""
    logger.info("📡 Requesting system status")
    
    try:
        status = dashboard.get_feature_status()
        error_stats = dashboard.get_error_stats()
        
        emit('status_update', {
            'features': status,
            'errors': error_stats,
            'timestamp': datetime.now().isoformat(),
            'health': 'healthy' if all(f['enabled'] for f in status.values()) else 'degraded'
        })
        
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        emit('error', {'message': str(e)})


# Utility functions

def broadcast_vulnerability(vuln_data: Dict):
    """Broadcast vulnerability to all connected clients"""
    socketio.emit('vulnerability_found', vuln_data)

def broadcast_metric_update(metrics: Dict):
    """Broadcast metrics update"""
    socketio.emit('metrics_update', metrics)


# Main entry point

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run the dashboard server"""
    logger.info(f"Starting Jupiter Dashboard on {host}:{port}")
    logger.info(f"Dashboard URL: http://localhost:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    port = int(os.getenv('DASHBOARD_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    print("="*70)
    print("JUPITER INTERACTIVE DASHBOARD")
    print("="*70)
    print(f"\n🚀 Starting server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"\n🌐 Dashboard URL: http://localhost:{port}")
    print(f"\n💬 Features:")
    print(f"   ✅ Real-time vulnerability visualization")
    print(f"   ✅ AI chat with Jupiter (Grok-powered)")
    print(f"   ✅ Live threat intelligence feed")
    print(f"   ✅ Security community pulse")
    print(f"   ✅ WebSocket real-time updates")
    print(f"\n" + "="*70)
    print("Press Ctrl+C to stop\n")
    
    run_dashboard(host=host, port=port, debug=debug)
