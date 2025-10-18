"""
JUPITER Haptic Feedback Server
WebSocket + REST API for VR haptic feedback

Provides real-time haptic feedback control:
- Device registration and management
- Threat haptic notifications
- Gesture feedback coordination
- Custom vibration patterns

Port: 5007
Protocol: WebSocket (Socket.IO) + REST API

Author: Enterprise Scanner Development Team
Date: October 17, 2025
Version: 1.0.0
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import asyncio
from datetime import datetime
import logging

# Import haptic system components
import sys
sys.path.append('..')
from haptic_feedback_system import (
    HapticFeedbackSystem,
    HapticDeviceType,
    HapticIntensity,
    VibrationPattern,
    ThreatSeverity,
    GestureType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'haptic_feedback_secret_key_2025'
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize haptic system
haptic_system = HapticFeedbackSystem()

# Active connections tracking
active_connections = {}  # socket_id -> {user_id, controller_ids, connected_at}


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'success', 'message': 'Connected to haptic server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if request.sid in active_connections:
        conn_info = active_connections[request.sid]
        logger.info(f"Client disconnected: {conn_info.get('user_id')}")
        del active_connections[request.sid]


@socketio.on('register_controller')
def handle_register_controller(data):
    """
    Register VR controller for haptic feedback
    
    Expected data:
    {
        "user_id": "user-123",
        "controller_id": "left_controller",
        "device_type": "meta_quest_3",
        "hand": "left"
    }
    """
    try:
        user_id = data.get('user_id')
        controller_id = data.get('controller_id')
        device_type_str = data.get('device_type', 'generic')
        hand = data.get('hand', 'right')
        
        # Convert device type string to enum
        device_type = HapticDeviceType[device_type_str.upper()]
        
        # Register controller
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            haptic_system.register_controller(controller_id, device_type)
        )
        loop.close()
        
        if success:
            # Track connection
            if request.sid not in active_connections:
                active_connections[request.sid] = {
                    'user_id': user_id,
                    'controller_ids': [],
                    'connected_at': datetime.now()
                }
            
            active_connections[request.sid]['controller_ids'].append(controller_id)
            
            emit('controller_registered', {
                'status': 'success',
                'controller_id': controller_id,
                'device_type': device_type_str,
                'hand': hand
            })
            
            logger.info(f"Registered controller: {controller_id} ({device_type_str})")
        else:
            emit('error', {'message': 'Failed to register controller'})
            
    except Exception as e:
        logger.error(f"Error registering controller: {e}")
        emit('error', {'message': str(e)})


@socketio.on('threat_detected')
def handle_threat_detected(data):
    """
    Trigger haptic notification for detected threat
    
    Expected data:
    {
        "controller_id": "right_controller",
        "hand": "right",
        "severity": "critical",
        "threat_id": "threat-123"
    }
    """
    try:
        controller_id = data.get('controller_id')
        hand = data.get('hand', 'right')
        severity_str = data.get('severity', 'medium')
        threat_id = data.get('threat_id')
        
        # Convert severity to enum
        severity = ThreatSeverity[severity_str.upper()]
        
        # Trigger haptic feedback
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_id = loop.run_until_complete(
            haptic_system.threat_detected(controller_id, hand, severity)
        )
        loop.close()
        
        emit('haptic_triggered', {
            'event_id': event_id,
            'type': 'threat_detected',
            'severity': severity_str,
            'threat_id': threat_id
        })
        
    except Exception as e:
        logger.error(f"Error triggering threat haptic: {e}")
        emit('error', {'message': str(e)})


@socketio.on('threat_interaction')
def handle_threat_interaction(data):
    """
    Haptic feedback for threat interaction
    
    Expected data:
    {
        "controller_id": "right_controller",
        "hand": "right",
        "interaction": "select",  // hover, select, isolate, remediate, escalate
        "severity": "high",
        "threat_id": "threat-123"
    }
    """
    try:
        controller_id = data.get('controller_id')
        hand = data.get('hand', 'right')
        interaction = data.get('interaction', 'select')
        severity_str = data.get('severity', 'medium')
        threat_id = data.get('threat_id')
        
        severity = ThreatSeverity[severity_str.upper()]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_id = loop.run_until_complete(
            haptic_system.threat_interaction(controller_id, hand, interaction, severity)
        )
        loop.close()
        
        emit('haptic_triggered', {
            'event_id': event_id,
            'type': 'threat_interaction',
            'interaction': interaction,
            'severity': severity_str,
            'threat_id': threat_id
        })
        
    except Exception as e:
        logger.error(f"Error triggering interaction haptic: {e}")
        emit('error', {'message': str(e)})


@socketio.on('gesture_feedback')
def handle_gesture_feedback(data):
    """
    Haptic feedback for gesture
    
    Expected data:
    {
        "controller_id": "right_controller",
        "hand": "right",
        "gesture": "point",  // point, grab, swipe, pinch, rotate, push, pull, throw
        "state": "start",    // start, confirm, release
        "success": true
    }
    """
    try:
        controller_id = data.get('controller_id')
        hand = data.get('hand', 'right')
        gesture_str = data.get('gesture', 'point')
        state = data.get('state', 'start')
        success = data.get('success', True)
        
        gesture = GestureType[gesture_str.upper()]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if state == 'start':
            event_id = loop.run_until_complete(
                haptic_system.gesture_started(controller_id, hand, gesture)
            )
        elif state == 'confirm':
            event_id = loop.run_until_complete(
                haptic_system.gesture_confirmed(controller_id, hand, gesture, success)
            )
        else:
            event_id = None
            
        loop.close()
        
        emit('haptic_triggered', {
            'event_id': event_id,
            'type': 'gesture_feedback',
            'gesture': gesture_str,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"Error triggering gesture haptic: {e}")
        emit('error', {'message': str(e)})


@socketio.on('collision_feedback')
def handle_collision_feedback(data):
    """
    Haptic feedback for object collision
    
    Expected data:
    {
        "controller_id": "right_controller",
        "hand": "right",
        "force": 0.7  // 0.0 to 1.0
    }
    """
    try:
        controller_id = data.get('controller_id')
        hand = data.get('hand', 'right')
        force = data.get('force', 0.5)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            haptic_system.object_collision(controller_id, hand, force)
        )
        loop.close()
        
        emit('haptic_triggered', {
            'type': 'collision',
            'force': force
        })
        
    except Exception as e:
        logger.error(f"Error triggering collision haptic: {e}")
        emit('error', {'message': str(e)})


@socketio.on('custom_pattern')
def handle_custom_pattern(data):
    """
    Trigger custom vibration pattern
    
    Expected data:
    {
        "controller_id": "right_controller",
        "hand": "right",
        "pulses": [[100, 4], [50, 0], [100, 5]]  // [duration_ms, intensity]
    }
    """
    try:
        controller_id = data.get('controller_id')
        hand = data.get('hand', 'right')
        pulses = data.get('pulses', [])
        
        # Convert to list of tuples
        pulse_tuples = [(int(p[0]), int(p[1])) for p in pulses]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_id = loop.run_until_complete(
            haptic_system.haptic_controller.trigger_custom_pattern(
                controller_id, hand, pulse_tuples
            )
        )
        loop.close()
        
        emit('haptic_triggered', {
            'event_id': event_id,
            'type': 'custom_pattern',
            'pulses': pulses
        })
        
    except Exception as e:
        logger.error(f"Error triggering custom pattern: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'haptic_feedback_server',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get haptic system statistics"""
    stats = haptic_system.get_statistics()
    return jsonify({
        'statistics': stats,
        'active_connections': len(active_connections)
    })


@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    """Get available vibration patterns"""
    patterns = [pattern.value for pattern in VibrationPattern]
    return jsonify({
        'patterns': patterns
    })


@app.route('/api/device-types', methods=['GET'])
def get_device_types():
    """Get supported device types"""
    device_types = [device.value for device in HapticDeviceType]
    return jsonify({
        'device_types': device_types
    })


@app.route('/api/severities', methods=['GET'])
def get_severities():
    """Get threat severity levels"""
    severities = [severity.value for severity in ThreatSeverity]
    return jsonify({
        'severities': severities
    })


@app.route('/api/gestures', methods=['GET'])
def get_gestures():
    """Get supported gesture types"""
    gestures = [gesture.value for gesture in GestureType]
    return jsonify({
        'gestures': gestures
    })


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting haptic feedback server on port 5007...")
    socketio.run(app, host='0.0.0.0', port=5007, debug=False)
