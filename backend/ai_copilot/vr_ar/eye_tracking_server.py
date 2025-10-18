"""
JUPITER Eye Tracking Server
WebSocket + REST API for VR eye tracking analytics

Provides real-time eye tracking data processing:
- Gaze event streaming
- Dwell selection notifications
- Attention metrics calculation
- Heatmap generation

Port: 5008
Protocol: WebSocket (Socket.IO) + REST API

Author: Enterprise Scanner Development Team
Date: October 17, 2025
Version: 1.0.0
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import asyncio
from datetime import datetime
import logging
import numpy as np

# Import eye tracking components
import sys
sys.path.append('..')
from eye_tracking_system import (
    EyeTrackingSystem,
    EyeTrackingDevice,
    EyeGazeData,
    GazeTarget,
    AttentionLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eye_tracking_secret_key_2025'
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Eye tracking systems per user
eye_systems: dict = {}  # user_id -> EyeTrackingSystem

# Active connections
active_connections = {}  # socket_id -> {user_id, device_type, calibrated}


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'success', 'message': 'Connected to eye tracking server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if request.sid in active_connections:
        conn_info = active_connections[request.sid]
        logger.info(f"Client disconnected: {conn_info.get('user_id')}")
        del active_connections[request.sid]


@socketio.on('initialize_eye_tracking')
def handle_initialize(data):
    """
    Initialize eye tracking system for user
    
    Expected data:
    {
        "user_id": "user-123",
        "device_type": "meta_quest_pro"
    }
    """
    try:
        user_id = data.get('user_id')
        device_type_str = data.get('device_type', 'generic')
        
        # Convert to enum
        device_type = EyeTrackingDevice[device_type_str.upper()]
        
        # Create eye tracking system
        eye_systems[user_id] = EyeTrackingSystem(device_type)
        
        # Track connection
        active_connections[request.sid] = {
            'user_id': user_id,
            'device_type': device_type_str,
            'calibrated': False,
            'connected_at': datetime.now()
        }
        
        emit('eye_tracking_initialized', {
            'status': 'success',
            'user_id': user_id,
            'device_type': device_type_str,
            'sampling_rate': eye_systems[user_id].eye_tracker.sampling_rate_hz
        })
        
        logger.info(f"Eye tracking initialized for {user_id} ({device_type_str})")
        
    except Exception as e:
        logger.error(f"Error initializing eye tracking: {e}")
        emit('error', {'message': str(e)})


@socketio.on('calibrate')
def handle_calibrate(data):
    """
    Calibrate eye tracking
    
    Expected data:
    {
        "user_id": "user-123",
        "num_points": 9
    }
    """
    try:
        user_id = data.get('user_id')
        num_points = data.get('num_points', 9)
        
        if user_id not in eye_systems:
            emit('error', {'message': 'Eye tracking not initialized'})
            return
        
        # Run calibration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        quality = loop.run_until_complete(
            eye_systems[user_id].calibrate(num_points)
        )
        loop.close()
        
        # Update connection status
        if request.sid in active_connections:
            active_connections[request.sid]['calibrated'] = True
        
        emit('calibration_complete', {
            'status': 'success',
            'quality': quality,
            'calibrated': True
        })
        
        logger.info(f"Calibration complete for {user_id}: quality {quality:.2f}")
        
    except Exception as e:
        logger.error(f"Error during calibration: {e}")
        emit('error', {'message': str(e)})


@socketio.on('gaze_data')
def handle_gaze_data(data):
    """
    Process gaze data frame
    
    Expected data:
    {
        "user_id": "user-123",
        "gaze_point": [x, y, z],
        "pupil_diameter": 4.5,
        "confidence": 0.95
    }
    """
    try:
        user_id = data.get('user_id')
        
        if user_id not in eye_systems:
            return
        
        # Parse gaze data
        gaze_point = tuple(data.get('gaze_point', [0, 0, -2]))
        pupil = data.get('pupil_diameter', 4.0)
        confidence = data.get('confidence', 0.95)
        
        # Create gaze data object
        gaze_data = EyeGazeData(
            timestamp=datetime.now(),
            left_eye_position=(0, 0, 0),
            right_eye_position=(0, 0, 0),
            left_eye_direction=gaze_point,
            right_eye_direction=gaze_point,
            combined_gaze_point=gaze_point,
            pupil_diameter_left=pupil,
            pupil_diameter_right=pupil,
            confidence=confidence
        )
        
        # Process gaze frame
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event = loop.run_until_complete(
            eye_systems[user_id].process_gaze_frame(gaze_data, user_id)
        )
        loop.close()
        
        # If selection occurred, notify client
        if event and event.gaze_target:
            emit('gaze_selection', {
                'target_id': event.gaze_target,
                'target_type': event.target_type.value,
                'duration': event.gaze_duration,
                'timestamp': event.timestamp.isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error processing gaze data: {e}")


@socketio.on('register_gaze_target')
def handle_register_target(data):
    """
    Register object as gaze-interactable
    
    Expected data:
    {
        "user_id": "user-123",
        "object_id": "threat-001",
        "object_type": "threat_node",
        "position": [x, y, z],
        "radius": 0.3
    }
    """
    try:
        user_id = data.get('user_id')
        object_id = data.get('object_id')
        object_type_str = data.get('object_type', 'threat_node')
        position = tuple(data.get('position', [0, 0, -2]))
        radius = data.get('radius', 0.3)
        
        if user_id not in eye_systems:
            emit('error', {'message': 'Eye tracking not initialized'})
            return
        
        # Convert object type
        object_type = GazeTarget[object_type_str.upper()]
        
        # Register target
        eye_systems[user_id].gaze_interaction.register_gaze_target(
            object_id, object_type, position, radius
        )
        
        emit('target_registered', {
            'object_id': object_id,
            'object_type': object_type_str
        })
        
    except Exception as e:
        logger.error(f"Error registering gaze target: {e}")
        emit('error', {'message': str(e)})


@socketio.on('get_attention_metrics')
def handle_get_metrics(data):
    """
    Get current attention metrics
    
    Expected data:
    {
        "user_id": "user-123"
    }
    """
    try:
        user_id = data.get('user_id')
        
        if user_id not in eye_systems:
            emit('error', {'message': 'Eye tracking not initialized'})
            return
        
        # Get metrics
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        metrics = loop.run_until_complete(
            eye_systems[user_id].get_attention_metrics()
        )
        loop.close()
        
        emit('attention_metrics', {
            'avg_fixation': metrics.average_fixation_duration,
            'saccade_frequency': metrics.saccade_frequency,
            'pupil_diameter': metrics.pupil_diameter_avg,
            'cognitive_load': metrics.cognitive_load,
            'attention_level': metrics.attention_level.value,
            'gaze_stability': metrics.gaze_stability
        })
        
    except Exception as e:
        logger.error(f"Error getting attention metrics: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'eye_tracking_server',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/statistics/<user_id>', methods=['GET'])
def get_statistics(user_id):
    """Get eye tracking statistics for user"""
    if user_id not in eye_systems:
        return jsonify({'error': 'User not found'}), 404
    
    stats = eye_systems[user_id].get_statistics()
    return jsonify({'statistics': stats})


@app.route('/api/heatmap/<user_id>', methods=['GET'])
def get_heatmap(user_id):
    """Get attention heatmap for user"""
    if user_id not in eye_systems:
        return jsonify({'error': 'User not found'}), 404
    
    top_n = request.args.get('top_n', default=20, type=int)
    heatmap = eye_systems[user_id].get_attention_heatmap()
    
    # Convert to JSON-serializable format
    heatmap_data = [
        {
            'position': point.position,
            'dwell_time': point.dwell_time,
            'visit_count': point.visit_count,
            'importance': point.importance_score
        }
        for point in heatmap[:top_n]
    ]
    
    return jsonify({'heatmap': heatmap_data})


@app.route('/api/gaze-stats/<user_id>/<object_id>', methods=['GET'])
def get_gaze_stats(user_id, object_id):
    """Get gaze statistics for specific object"""
    if user_id not in eye_systems:
        return jsonify({'error': 'User not found'}), 404
    
    stats = eye_systems[user_id].gaze_interaction.get_gaze_statistics(object_id)
    return jsonify({'statistics': stats})


@app.route('/api/active-users', methods=['GET'])
def get_active_users():
    """Get list of active users"""
    users = [
        {
            'user_id': conn['user_id'],
            'device_type': conn['device_type'],
            'calibrated': conn['calibrated'],
            'connected_at': conn['connected_at'].isoformat()
        }
        for conn in active_connections.values()
    ]
    
    return jsonify({'active_users': users, 'count': len(users)})


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting eye tracking server on port 5008...")
    socketio.run(app, host='0.0.0.0', port=5008, debug=False)
