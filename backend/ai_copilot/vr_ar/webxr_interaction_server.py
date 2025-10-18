"""
JUPITER VR/AR Platform - WebXR Interaction Integration
Enterprise Scanner - Cybersecurity Vulnerability Assessment Platform

Connects advanced_interaction_system.py backend to WebXR frontend.
Real-time hand tracking, gesture recognition, and voice commands in browser.
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import asyncio
import json
import base64
import logging
from typing import Dict, Any, Optional
from advanced_interaction_system import (
    AdvancedInteractionSystem,
    InteractionMode,
    GestureType,
    HandType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jupiter-vr-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global interaction system
interaction_system: Optional[AdvancedInteractionSystem] = None


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_interaction_system(openai_api_key: str):
    """Initialize the interaction system"""
    global interaction_system
    interaction_system = AdvancedInteractionSystem(openai_api_key)
    logger.info("Interaction system initialized")


# ============================================================================
# SOCKETIO EVENT HANDLERS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('hand_tracking_frame')
def handle_hand_tracking(data: Dict[str, Any]):
    """
    Receive hand tracking data from WebXR frontend.
    
    Data format:
    {
        'left_hand': [[x, y, z], ...],  # 21 landmarks
        'right_hand': [[x, y, z], ...],  # 21 landmarks
        'timestamp': float,
        'confidence': float
    }
    """
    if not interaction_system:
        emit('error', {'message': 'Interaction system not initialized'})
        return
    
    try:
        # Process frame asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            interaction_system.update(data)
        )
        loop.close()
        
        # Send results back to client
        emit('interaction_update', results)
        
    except Exception as e:
        logger.error(f"Hand tracking error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('voice_input')
def handle_voice_input(data: Dict[str, Any]):
    """
    Receive voice audio from WebXR frontend.
    
    Data format:
    {
        'audio': 'base64-encoded-audio-data',
        'format': 'pcm' | 'wav' | 'mp3',
        'timestamp': float
    }
    """
    if not interaction_system:
        emit('error', {'message': 'Interaction system not initialized'})
        return
    
    try:
        # Decode audio
        audio_base64 = data.get('audio', '')
        audio_bytes = base64.b64decode(audio_base64)
        
        # Process audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            interaction_system.update({}, audio_data=audio_bytes)
        )
        loop.close()
        
        # Send results back
        emit('voice_command', results.get('voice_command'))
        
    except Exception as e:
        logger.error(f"Voice input error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('scene_objects')
def handle_scene_objects(data: Dict[str, Any]):
    """
    Receive scene objects for manipulation tracking.
    
    Data format:
    {
        'objects': [
            {
                'id': 'server-001',
                'type': 'server',
                'position': [x, y, z],
                'rotation': [x, y, z, w],
                'scale': [x, y, z]
            },
            ...
        ]
    }
    """
    if not interaction_system:
        emit('error', {'message': 'Interaction system not initialized'})
        return
    
    # Store scene objects for manipulation
    # (Will be used in next hand tracking update)
    emit('scene_objects_received', {'count': len(data.get('objects', []))})


@socketio.on('set_mode')
def handle_set_mode(data: Dict[str, Any]):
    """
    Change interaction mode.
    
    Data format:
    {
        'mode': 'browse' | 'investigate' | 'manipulate' | 'query' | 'collaborate'
    }
    """
    if not interaction_system:
        emit('error', {'message': 'Interaction system not initialized'})
        return
    
    try:
        mode_str = data.get('mode', 'browse')
        mode = InteractionMode[mode_str.upper()]
        interaction_system.set_mode(mode)
        
        emit('mode_changed', {'mode': mode.value})
        
    except Exception as e:
        logger.error(f"Mode change error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('get_statistics')
def handle_get_statistics():
    """Get interaction statistics"""
    if not interaction_system:
        emit('error', {'message': 'Interaction system not initialized'})
        return
    
    stats = interaction_system.get_statistics()
    emit('statistics', stats)


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/interaction/status', methods=['GET'])
def get_status():
    """Get system status"""
    if not interaction_system:
        return jsonify({'error': 'System not initialized'}), 503
    
    return jsonify(interaction_system.get_status())


@app.route('/api/interaction/statistics', methods=['GET'])
def get_statistics():
    """Get interaction statistics"""
    if not interaction_system:
        return jsonify({'error': 'System not initialized'}), 503
    
    return jsonify(interaction_system.get_statistics())


@app.route('/api/interaction/gestures', methods=['GET'])
def get_supported_gestures():
    """Get list of supported gestures"""
    gestures = [
        {
            'type': gesture.value,
            'category': 'navigation' if gesture.value.startswith('swipe') or gesture.value == 'point' else
                       'manipulation' if gesture.value.startswith('rotate') or gesture.value.startswith('scale') else
                       'control'
        }
        for gesture in GestureType
        if gesture != GestureType.NONE
    ]
    
    return jsonify({'gestures': gestures})


@app.route('/api/interaction/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'system_initialized': interaction_system is not None
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize with demo API key
    initialize_interaction_system("demo-openai-key")
    
    # Run server
    logger.info("Starting WebXR Interaction Server on port 5004...")
    socketio.run(app, host='0.0.0.0', port=5004, debug=False)
