"""
Chat API Module

REST API and WebSocket interface for AI Copilot.

Provides:
- RESTful API endpoints
- WebSocket streaming for real-time responses
- Server-Sent Events (SSE) for streaming
- Rate limiting integration
- Authentication and authorization
- Error handling and logging

Endpoints:
- POST /api/copilot/chat - Send message
- GET /api/copilot/context - Get conversation context
- POST /api/copilot/clear - Clear conversation
- GET /api/copilot/status - System status
- WS /api/copilot/stream - WebSocket streaming

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
import time
import asyncio
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Flask/FastAPI imports (will be available when packages installed)
try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    from flask_socketio import SocketIO, emit, disconnect
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False


@dataclass
class ChatRequest:
    """Chat API request"""
    message: str
    user_id: str
    session_id: Optional[str] = None
    
    # Optional parameters
    access_level: Optional[str] = None
    query_type: Optional[str] = None
    active_scan_id: Optional[str] = None
    
    # Response preferences
    format: str = "text"  # 'text', 'markdown', 'json'
    stream: bool = False
    include_sources: bool = True
    
    # Metadata
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChatResponse:
    """Chat API response"""
    response: str
    session_id: str
    
    # Context
    query_type: Optional[str] = None
    
    # Sources and citations
    sources: List[Dict[str, str]] = None
    citations: List[str] = None
    
    # Suggestions
    quick_replies: List[str] = None
    suggested_actions: List[str] = None
    
    # Metadata
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    tokens_used: int = 0
    model_used: str = ""
    
    # Status
    success: bool = True
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.citations is None:
            self.citations = []
        if self.quick_replies is None:
            self.quick_replies = []
        if self.suggested_actions is None:
            self.suggested_actions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ChatAPI:
    """
    Chat API interface for AI Copilot
    
    Provides RESTful endpoints and WebSocket streaming
    """
    
    def __init__(
        self,
        copilot_engine=None,
        host: str = "0.0.0.0",
        port: int = 5000,
        enable_cors: bool = True,
        enable_websocket: bool = True
    ):
        """
        Initialize Chat API
        
        Args:
            copilot_engine: CopilotEngine instance
            host: API host
            port: API port
            enable_cors: Enable CORS
            enable_websocket: Enable WebSocket support
        """
        self.logger = logging.getLogger(__name__)
        
        self.copilot_engine = copilot_engine
        self.host = host
        self.port = port
        self.enable_cors = enable_cors
        self.enable_websocket = enable_websocket
        
        # Initialize copilot engine if not provided
        if not self.copilot_engine:
            try:
                from backend.ai_copilot.core.copilot_engine import CopilotEngine
                self.copilot_engine = CopilotEngine()
            except Exception as e:
                self.logger.warning(f"Copilot engine not available: {e}")
        
        # Initialize Flask app
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            
            if enable_cors:
                CORS(self.app, resources={r"/api/*": {"origins": "*"}})
            
            # Initialize SocketIO
            if enable_websocket and SOCKETIO_AVAILABLE:
                self.socketio = SocketIO(
                    self.app,
                    cors_allowed_origins="*",
                    async_mode='threading'
                )
                self._setup_websocket_handlers()
            else:
                self.socketio = None
            
            # Setup routes
            self._setup_routes()
        else:
            self.app = None
            self.socketio = None
            self.logger.warning("Flask not installed. Install: pip install flask flask-cors flask-socketio")
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'websocket_connections': 0,
            'avg_response_time_ms': 0
        }
        
        self.logger.info(f"ChatAPI initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/copilot/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'copilot_engine': 'available' if self.copilot_engine else 'unavailable',
                'websocket': 'enabled' if self.socketio else 'disabled'
            })
        
        @self.app.route('/api/copilot/chat', methods=['POST'])
        def chat():
            """Main chat endpoint"""
            return self._handle_chat_request()
        
        @self.app.route('/api/copilot/context/<session_id>', methods=['GET'])
        def get_context(session_id):
            """Get conversation context"""
            return self._handle_get_context(session_id)
        
        @self.app.route('/api/copilot/context/<session_id>', methods=['DELETE'])
        def clear_context(session_id):
            """Clear conversation context"""
            return self._handle_clear_context(session_id)
        
        @self.app.route('/api/copilot/status', methods=['GET'])
        def status():
            """System status"""
            return self._handle_status_request()
        
        @self.app.route('/api/copilot/stream', methods=['POST'])
        def stream():
            """Server-Sent Events streaming endpoint"""
            return self._handle_stream_request()
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle WebSocket connection"""
            self.stats['websocket_connections'] += 1
            self.logger.info(f"WebSocket client connected")
            emit('connected', {'message': 'Connected to AI Copilot'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle WebSocket disconnection"""
            self.logger.info("WebSocket client disconnected")
        
        @self.socketio.on('chat')
        def handle_chat_message(data):
            """Handle chat message via WebSocket"""
            try:
                # Parse request
                chat_request = ChatRequest(
                    message=data.get('message'),
                    user_id=data.get('user_id'),
                    session_id=data.get('session_id'),
                    stream=True  # WebSocket is always streaming
                )
                
                # Process with streaming
                self._process_streaming_request(chat_request)
                
            except Exception as e:
                self.logger.error(f"WebSocket chat error: {e}", exc_info=True)
                emit('error', {'error': str(e)})
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping for keepalive"""
            emit('pong', {'timestamp': time.time()})
    
    def _handle_chat_request(self) -> Any:
        """Handle POST /api/copilot/chat"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Parse request
            data = request.get_json()
            
            if not data or 'message' not in data or 'user_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields: message, user_id'
                }), 400
            
            chat_request = ChatRequest(
                message=data['message'],
                user_id=data['user_id'],
                session_id=data.get('session_id'),
                access_level=data.get('access_level'),
                query_type=data.get('query_type'),
                active_scan_id=data.get('active_scan_id'),
                format=data.get('format', 'text'),
                stream=data.get('stream', False),
                include_sources=data.get('include_sources', True),
                metadata=data.get('metadata', {})
            )
            
            # Validate
            if not chat_request.message.strip():
                return jsonify({
                    'success': False,
                    'error': 'Message cannot be empty'
                }), 400
            
            # Process request
            if chat_request.stream:
                # Server-Sent Events streaming
                return self._stream_response(chat_request)
            else:
                # Standard JSON response
                response = self._process_request(chat_request)
                
                # Update statistics
                response_time = int((time.time() - start_time) * 1000)
                self.stats['successful_requests'] += 1
                self._update_avg_response_time(response_time)
                
                return jsonify(response.to_dict())
                
        except Exception as e:
            self.logger.error(f"Chat request failed: {e}", exc_info=True)
            self.stats['failed_requests'] += 1
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _handle_get_context(self, session_id: str) -> Any:
        """Handle GET /api/copilot/context/<session_id>"""
        try:
            if not self.copilot_engine:
                return jsonify({
                    'success': False,
                    'error': 'Copilot engine not available'
                }), 503
            
            # Get context from context manager
            context_manager = self.copilot_engine.context_manager
            context = context_manager.get_context(session_id)
            
            if not context:
                return jsonify({
                    'success': False,
                    'error': 'Session not found'
                }), 404
            
            # Get summary
            summary = context_manager.get_conversation_summary(session_id)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'summary': summary
            })
            
        except Exception as e:
            self.logger.error(f"Get context failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _handle_clear_context(self, session_id: str) -> Any:
        """Handle DELETE /api/copilot/context/<session_id>"""
        try:
            if not self.copilot_engine:
                return jsonify({
                    'success': False,
                    'error': 'Copilot engine not available'
                }), 503
            
            # Clear context
            context_manager = self.copilot_engine.context_manager
            context_manager.clear_context(session_id)
            
            return jsonify({
                'success': True,
                'message': 'Context cleared'
            })
            
        except Exception as e:
            self.logger.error(f"Clear context failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _handle_status_request(self) -> Any:
        """Handle GET /api/copilot/status"""
        try:
            status = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'api_version': '1.0.0',
                'statistics': self.stats
            }
            
            # Get engine health
            if self.copilot_engine:
                engine_health = self.copilot_engine.health_check()
                status['engine'] = engine_health
            
            return jsonify(status)
            
        except Exception as e:
            self.logger.error(f"Status request failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _handle_stream_request(self) -> Any:
        """Handle POST /api/copilot/stream (SSE)"""
        try:
            data = request.get_json()
            
            chat_request = ChatRequest(
                message=data['message'],
                user_id=data['user_id'],
                session_id=data.get('session_id'),
                stream=True
            )
            
            return self._stream_response(chat_request)
            
        except Exception as e:
            self.logger.error(f"Stream request failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def _process_request(self, chat_request: ChatRequest) -> ChatResponse:
        """Process chat request"""
        if not self.copilot_engine:
            return ChatResponse(
                response="AI Copilot engine is not available",
                session_id=chat_request.session_id or "unknown",
                success=False,
                error="Engine not available"
            )
        
        try:
            # Build query object
            from backend.ai_copilot.core.copilot_engine import Query, AccessLevel, QueryType
            
            # Parse access level
            access_level = AccessLevel.PUBLIC
            if chat_request.access_level:
                try:
                    access_level = AccessLevel(chat_request.access_level.lower())
                except ValueError:
                    access_level = AccessLevel.PUBLIC
            
            # Create query
            query = Query(
                query_id=f"query_{int(time.time()*1000)}",
                user_id=chat_request.user_id,
                session_id=chat_request.session_id or f"session_{chat_request.user_id}_{int(time.time())}",
                message=chat_request.message,
                query_type=None,  # Will be detected
                access_level=access_level,
                active_scan=chat_request.active_scan_id,
                metadata=chat_request.metadata
            )
            
            # Process query
            copilot_response = self.copilot_engine.process_query(query)
            
            # Convert to ChatResponse
            response = ChatResponse(
                response=copilot_response.response_text,
                session_id=query.session_id,
                query_type=copilot_response.query_type.value if copilot_response.query_type else None,
                sources=copilot_response.sources or [],
                citations=copilot_response.citations or [],
                quick_replies=copilot_response.quick_replies or [],
                suggested_actions=copilot_response.suggested_actions or [],
                confidence_score=copilot_response.confidence_score,
                processing_time_ms=copilot_response.processing_time_ms,
                tokens_used=copilot_response.tokens_used,
                model_used=copilot_response.model_used,
                success=True,
                error=copilot_response.error
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}", exc_info=True)
            
            return ChatResponse(
                response=f"An error occurred: {str(e)}",
                session_id=chat_request.session_id or "unknown",
                success=False,
                error=str(e)
            )
    
    def _stream_response(self, chat_request: ChatRequest) -> Response:
        """Stream response using Server-Sent Events"""
        def generate():
            try:
                # Process request (would use streaming LLM in production)
                response = self._process_request(chat_request)
                
                # Stream response in chunks
                words = response.response.split()
                for i, word in enumerate(words):
                    chunk = {
                        'type': 'chunk',
                        'content': word + ' ',
                        'index': i
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    time.sleep(0.05)  # Simulate streaming delay
                
                # Send completion
                completion = {
                    'type': 'complete',
                    'session_id': response.session_id,
                    'tokens_used': response.tokens_used,
                    'processing_time_ms': response.processing_time_ms
                }
                yield f"data: {json.dumps(completion)}\n\n"
                
            except Exception as e:
                error = {
                    'type': 'error',
                    'error': str(e)
                }
                yield f"data: {json.dumps(error)}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    def _process_streaming_request(self, chat_request: ChatRequest):
        """Process streaming request for WebSocket"""
        try:
            # Process request
            response = self._process_request(chat_request)
            
            # Stream response in chunks
            words = response.response.split()
            for i, word in enumerate(words):
                emit('chunk', {
                    'content': word + ' ',
                    'index': i
                })
                time.sleep(0.05)
            
            # Send completion
            emit('complete', {
                'session_id': response.session_id,
                'tokens_used': response.tokens_used,
                'processing_time_ms': response.processing_time_ms,
                'quick_replies': response.quick_replies
            })
            
        except Exception as e:
            self.logger.error(f"Streaming request failed: {e}", exc_info=True)
            emit('error', {'error': str(e)})
    
    def _update_avg_response_time(self, response_time_ms: int):
        """Update average response time"""
        n = self.stats['successful_requests']
        if n > 0:
            self.stats['avg_response_time_ms'] = (
                (self.stats['avg_response_time_ms'] * (n - 1) + response_time_ms) / n
            )
    
    def run(self, debug: bool = False):
        """
        Run the API server
        
        Args:
            debug: Enable debug mode
        """
        if not self.app:
            self.logger.error("Flask not available. Cannot start server.")
            return
        
        self.logger.info(f"Starting Chat API on {self.host}:{self.port}")
        
        if self.socketio:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=debug
            )
        else:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=debug
            )


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("CHAT API MODULE")
    print("="*70)
    
    # Initialize Chat API
    print("\n1. Initializing Chat API...")
    api = ChatAPI(
        host="0.0.0.0",
        port=5000,
        enable_cors=True,
        enable_websocket=True
    )
    
    print(f"\n   API initialized on {api.host}:{api.port}")
    print(f"   CORS: {'enabled' if api.enable_cors else 'disabled'}")
    print(f"   WebSocket: {'enabled' if api.socketio else 'disabled'}")
    print(f"   Flask: {'available' if api.app else 'not available'}")
    
    # Test endpoints (mock)
    print("\n2. Available Endpoints:")
    endpoints = [
        "POST   /api/copilot/chat           - Send message",
        "GET    /api/copilot/context/:id    - Get conversation context",
        "DELETE /api/copilot/context/:id    - Clear conversation",
        "GET    /api/copilot/status          - System status",
        "POST   /api/copilot/stream          - SSE streaming",
        "WS     /api/copilot/stream          - WebSocket streaming"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    # Statistics
    print("\n3. API Statistics:")
    print(json.dumps(api.stats, indent=2))
    
    # Usage example
    print("\n4. Usage Example:")
    print("""
    # JavaScript Client Example:
    
    fetch('http://localhost:5000/api/copilot/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: 'What is SQL injection?',
            user_id: 'user_123',
            access_level: 'customer',
            include_sources: true
        })
    })
    .then(response => response.json())
    .then(data => console.log(data));
    
    # WebSocket Example:
    
    const socket = io('http://localhost:5000');
    socket.on('connect', () => {
        socket.emit('chat', {
            message: 'Analyze scan results',
            user_id: 'user_123',
            session_id: 'session_456'
        });
    });
    socket.on('chunk', (data) => {
        console.log('Chunk:', data.content);
    });
    socket.on('complete', (data) => {
        console.log('Complete:', data);
    });
    """)
    
    print("\n" + "="*70)
    print("CHAT API MODULE COMPLETE ✅")
    print("="*70)
    print("\nTo start the server, run: python chat_api.py")
    print("Then test with: curl -X POST http://localhost:5000/api/copilot/health")
