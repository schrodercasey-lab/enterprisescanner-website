"""
JUPITER VR/AR Platform - Voice NLP WebSocket Server
Enterprise Scanner - Cybersecurity Vulnerability Assessment Platform

Real-time voice communication server for JUPITER conversational AI.
WebSocket + REST API for browser-based voice interactions.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import asyncio
import json
import base64
import logging
from typing import Dict, Any, Optional
from voice_nlp_interface import (
    VoiceNLPInterface,
    VoicePersonality,
    IntentType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jupiter-voice-nlp-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global voice interface
voice_interface: Optional[VoiceNLPInterface] = None


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_voice_interface(openai_key: str, elevenlabs_key: str):
    """Initialize the voice NLP interface"""
    global voice_interface
    voice_interface = VoiceNLPInterface(
        openai_api_key=openai_key,
        elevenlabs_api_key=elevenlabs_key
    )
    logger.info("Voice NLP interface initialized")


# ============================================================================
# SOCKETIO EVENT HANDLERS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {
        'status': 'connected',
        'sid': request.sid,
        'jupiter_ready': voice_interface is not None
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('voice_input')
def handle_voice_input(data: Dict[str, Any]):
    """
    Receive voice audio and process through JUPITER.
    
    Data format:
    {
        'audio': 'base64-encoded-audio',
        'session_id': 'unique-session-id',
        'language': 'en',
        'personality': 'professional'
    }
    """
    if not voice_interface:
        emit('error', {'message': 'Voice interface not initialized'})
        return
    
    try:
        # Decode audio
        audio_base64 = data.get('audio', '')
        audio_bytes = base64.b64decode(audio_base64)
        
        session_id = data.get('session_id', request.sid)
        language = data.get('language', 'en')
        personality_str = data.get('personality', 'professional')
        personality = VoicePersonality[personality_str.upper()]
        
        # Process voice input
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        transcript, voice_output = loop.run_until_complete(
            voice_interface.process_voice_input(
                audio_data=audio_bytes,
                session_id=session_id,
                language=language,
                personality=personality
            )
        )
        
        loop.close()
        
        # Encode voice response
        audio_response_base64 = base64.b64encode(voice_output.audio_data).decode('utf-8')
        
        # Send results back
        emit('voice_response', {
            'transcript': transcript,
            'response_text': voice_output.text,
            'response_audio': audio_response_base64,
            'duration': voice_output.duration_seconds,
            'personality': personality.value
        })
        
    except Exception as e:
        logger.error(f"Voice input error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('text_query')
def handle_text_query(data: Dict[str, Any]):
    """
    Process text query (keyboard input).
    
    Data format:
    {
        'text': 'User query',
        'session_id': 'unique-session-id',
        'synthesize_voice': true,
        'personality': 'professional'
    }
    """
    if not voice_interface:
        emit('error', {'message': 'Voice interface not initialized'})
        return
    
    try:
        text = data.get('text', '')
        session_id = data.get('session_id', request.sid)
        synthesize_voice = data.get('synthesize_voice', True)
        personality_str = data.get('personality', 'professional')
        personality = VoicePersonality[personality_str.upper()]
        
        # Process text query
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        response_text, voice_output = loop.run_until_complete(
            voice_interface.process_text_query(
                text=text,
                session_id=session_id,
                synthesize_voice=synthesize_voice,
                personality=personality
            )
        )
        
        loop.close()
        
        # Prepare response
        response_data = {
            'response_text': response_text
        }
        
        if voice_output:
            audio_base64 = base64.b64encode(voice_output.audio_data).decode('utf-8')
            response_data['response_audio'] = audio_base64
            response_data['duration'] = voice_output.duration_seconds
        
        emit('text_response', response_data)
        
    except Exception as e:
        logger.error(f"Text query error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('get_conversation_history')
def handle_get_history(data: Dict[str, Any]):
    """Get conversation history for session"""
    if not voice_interface:
        emit('error', {'message': 'Voice interface not initialized'})
        return
    
    session_id = data.get('session_id', request.sid)
    history = voice_interface.get_conversation_history(session_id)
    
    if history:
        emit('conversation_history', {
            'session_id': history.session_id,
            'turn_count': len(history.turns),
            'current_topic': history.current_topic,
            'mentioned_entities': history.mentioned_entities,
            'turns': [
                {
                    'user_input': turn.user_input,
                    'jupiter_response': turn.jupiter_response,
                    'intent': turn.user_intent.value,
                    'confidence': turn.confidence
                }
                for turn in history.turns[-10:]  # Last 10 turns
            ]
        })
    else:
        emit('conversation_history', {'session_id': session_id, 'turns': []})


@socketio.on('get_statistics')
def handle_get_statistics():
    """Get system statistics"""
    if not voice_interface:
        emit('error', {'message': 'Voice interface not initialized'})
        return
    
    stats = voice_interface.get_statistics()
    emit('statistics', stats)


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/voice/status', methods=['GET'])
def get_status():
    """Get system status"""
    if not voice_interface:
        return jsonify({'error': 'System not initialized'}), 503
    
    return jsonify(voice_interface.get_status())


@app.route('/api/voice/statistics', methods=['GET'])
def get_statistics():
    """Get performance statistics"""
    if not voice_interface:
        return jsonify({'error': 'System not initialized'}), 503
    
    return jsonify(voice_interface.get_statistics())


@app.route('/api/voice/personalities', methods=['GET'])
def get_personalities():
    """Get available voice personalities"""
    personalities = [
        {
            'id': p.value,
            'name': p.value.title(),
            'description': get_personality_description(p)
        }
        for p in VoicePersonality
    ]
    
    return jsonify({'personalities': personalities})


def get_personality_description(personality: VoicePersonality) -> str:
    """Get personality description"""
    descriptions = {
        VoicePersonality.PROFESSIONAL: "Clear, confident, authoritative voice for executive briefings",
        VoicePersonality.FRIENDLY: "Warm, conversational tone for casual interactions",
        VoicePersonality.URGENT: "Fast-paced, serious voice for critical alerts",
        VoicePersonality.TEACHING: "Patient, explanatory tone for training and education"
    }
    return descriptions.get(personality, "Default voice")


@app.route('/api/voice/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'system_initialized': voice_interface is not None
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize with demo keys
    initialize_voice_interface(
        openai_key="demo-openai-key",
        elevenlabs_key="demo-elevenlabs-key"
    )
    
    # Run server
    logger.info("Starting Voice NLP Server on port 5005...")
    socketio.run(app, host='0.0.0.0', port=5005, debug=False)
