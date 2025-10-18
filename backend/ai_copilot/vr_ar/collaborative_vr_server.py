"""
JUPITER Collaborative VR Server
WebSocket + REST API for real-time multi-user collaboration

Handles:
- Real-time user presence synchronization
- Voice chat signaling (WebRTC)
- Shared investigation updates
- Avatar position streaming
- Team communication

Author: Enterprise Scanner Development Team
Date: October 17, 2025
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional

from collaborative_vr_system import (
    CollaborativeVRSystem,
    UserRole,
    AnnotationType,
    CommunicationChannel,
    VRPosition,
    SessionState
)

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jupiter-collaborative-vr-secret-key'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global collaborative system
collab_system = CollaborativeVRSystem()

# Active connections tracking
active_connections: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    active_connections[client_id] = {
        'connected_at': datetime.now().isoformat(),
        'session_id': None,
        'user_id': None
    }
    
    emit('connection_established', {
        'client_id': client_id,
        'message': 'Connected to JUPITER Collaborative VR server'
    })
    
    print(f"Client connected: {client_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    
    # Clean up user from session
    if client_id in active_connections:
        conn_data = active_connections[client_id]
        session_id = conn_data.get('session_id')
        user_id = conn_data.get('user_id')
        
        if session_id and user_id:
            session = asyncio.run(collab_system.get_session(session_id))
            if session:
                asyncio.run(session.leave_session(user_id))
                
                # Notify other users
                emit('user_left', {
                    'user_id': user_id,
                    'session_id': session_id
                }, room=session_id, skip_sid=client_id)
        
        del active_connections[client_id]
    
    print(f"Client disconnected: {client_id}")


@socketio.on('create_session')
def handle_create_session(data):
    """Create new collaborative session"""
    try:
        session_name = data.get('session_name')
        created_by = data.get('user_id')
        
        # Create session
        session_id = asyncio.run(collab_system.create_session(session_name, created_by))
        
        # Join socket room
        join_room(session_id)
        
        # Track connection
        active_connections[request.sid]['session_id'] = session_id
        active_connections[request.sid]['user_id'] = created_by
        
        emit('session_created', {
            'session_id': session_id,
            'session_name': session_name,
            'created_by': created_by
        })
        
        print(f"Session created: {session_name} ({session_id})")
        
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('join_session')
def handle_join_session(data):
    """Join existing collaborative session"""
    try:
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        username = data.get('username')
        role_str = data.get('role', 'analyst')
        avatar_id = data.get('avatar_id', 'default_avatar')
        
        # Parse role
        role = UserRole[role_str.upper()]
        
        # Join session
        success = asyncio.run(
            collab_system.join_session(session_id, user_id, username, role, avatar_id)
        )
        
        if success:
            # Join socket room
            join_room(session_id)
            
            # Track connection
            active_connections[request.sid]['session_id'] = session_id
            active_connections[request.sid]['user_id'] = user_id
            
            # Get current session state
            session = asyncio.run(collab_system.get_session(session_id))
            users = asyncio.run(session.get_all_users())
            
            # Notify user
            emit('session_joined', {
                'session_id': session_id,
                'user_id': user_id,
                'current_users': [
                    {
                        'user_id': u.user_id,
                        'username': u.username,
                        'role': u.role.value,
                        'avatar_id': u.avatar_id
                    }
                    for u in users
                ]
            })
            
            # Notify other users
            emit('user_joined', {
                'user_id': user_id,
                'username': username,
                'role': role.value,
                'avatar_id': avatar_id
            }, room=session_id, skip_sid=request.sid)
            
            print(f"User {username} joined session {session_id}")
        else:
            emit('error', {'message': 'Failed to join session'})
            
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('update_position')
def handle_update_position(data):
    """Update user position in VR"""
    try:
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        position_data = data.get('position')
        
        # Create VRPosition object
        position = VRPosition(
            x=position_data['x'],
            y=position_data['y'],
            z=position_data['z'],
            rotation_x=position_data.get('rotation_x', 0),
            rotation_y=position_data.get('rotation_y', 0),
            rotation_z=position_data.get('rotation_z', 0)
        )
        
        # Update in system
        avatar_sync = asyncio.run(collab_system.get_avatar_sync(session_id))
        if avatar_sync:
            asyncio.run(avatar_sync.sync_avatar_position(user_id, position))
        
        # Broadcast to other users
        emit('position_update', {
            'user_id': user_id,
            'position': position_data
        }, room=session_id, skip_sid=request.sid)
        
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('sync_gesture')
def handle_sync_gesture(data):
    """Sync gesture to other users"""
    try:
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        gesture_name = data.get('gesture')
        target_position = data.get('target_position')
        
        # Create position if provided
        target_pos = None
        if target_position:
            target_pos = VRPosition(
                x=target_position['x'],
                y=target_position['y'],
                z=target_position['z']
            )
        
        # Sync gesture
        avatar_sync = asyncio.run(collab_system.get_avatar_sync(session_id))
        if avatar_sync:
            asyncio.run(avatar_sync.sync_gesture(user_id, gesture_name, target_pos))
        
        # Broadcast
        emit('gesture_performed', {
            'user_id': user_id,
            'gesture': gesture_name,
            'target_position': target_position
        }, room=session_id, skip_sid=request.sid)
        
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('add_annotation')
def handle_add_annotation(data):
    """Add collaborative annotation"""
    try:
        session_id = data.get('session_id')
        investigation_id = data.get('investigation_id')
        user_id = data.get('user_id')
        annotation_type_str = data.get('annotation_type')
        position_data = data.get('position')
        content = data.get('content')
        target_id = data.get('target_id')
        
        # Parse annotation type
        annotation_type = AnnotationType[annotation_type_str.upper()]
        
        # Create position
        position = VRPosition(
            x=position_data['x'],
            y=position_data['y'],
            z=position_data['z']
        )
        
        # Add annotation
        inv_space = asyncio.run(collab_system.get_investigation_space(session_id))
        if inv_space:
            annotation_id = asyncio.run(
                inv_space.add_annotation(
                    investigation_id, user_id, annotation_type,
                    position, content, target_id
                )
            )
            
            # Broadcast to team
            emit('annotation_added', {
                'annotation_id': annotation_id,
                'investigation_id': investigation_id,
                'user_id': user_id,
                'type': annotation_type_str,
                'position': position_data,
                'content': content,
                'target_id': target_id
            }, room=session_id)
            
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('send_message')
def handle_send_message(data):
    """Send text chat message"""
    try:
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        message = data.get('message')
        mentions = data.get('mentions', [])
        
        # Send message
        comm = asyncio.run(collab_system.get_communication(session_id))
        if comm:
            message_id = asyncio.run(
                comm.send_text_message(user_id, message, mentions=mentions)
            )
            
            # Get username
            session = asyncio.run(collab_system.get_session(session_id))
            username = session.users.get(user_id).username if user_id in session.users else 'Unknown'
            
            # Broadcast
            emit('message_received', {
                'message_id': message_id,
                'user_id': user_id,
                'username': username,
                'message': message,
                'mentions': mentions,
                'timestamp': datetime.now().isoformat()
            }, room=session_id)
            
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('voice_state_change')
def handle_voice_state_change(data):
    """Handle user voice state change (speaking/muted)"""
    try:
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        is_speaking = data.get('is_speaking', False)
        is_muted = data.get('is_muted', False)
        
        # Update session
        session = asyncio.run(collab_system.get_session(session_id))
        if session and user_id in session.users:
            session.users[user_id].is_speaking = is_speaking
            
            # Broadcast
            emit('voice_state_changed', {
                'user_id': user_id,
                'is_speaking': is_speaking,
                'is_muted': is_muted
            }, room=session_id, skip_sid=request.sid)
            
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('start_investigation')
def handle_start_investigation(data):
    """Start new shared investigation"""
    try:
        session_id = data.get('session_id')
        name = data.get('name')
        created_by = data.get('user_id')
        focus_entities = data.get('focus_entities', [])
        
        # Create investigation
        inv_space = asyncio.run(collab_system.get_investigation_space(session_id))
        if inv_space:
            investigation_id = asyncio.run(
                inv_space.create_investigation(name, created_by, focus_entities)
            )
            
            # Broadcast
            emit('investigation_started', {
                'investigation_id': investigation_id,
                'name': name,
                'created_by': created_by,
                'focus_entities': focus_entities
            }, room=session_id)
            
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('request_sync')
def handle_request_sync(data):
    """Request full state synchronization"""
    try:
        session_id = data.get('session_id')
        
        # Get session state
        session = asyncio.run(collab_system.get_session(session_id))
        avatar_sync = asyncio.run(collab_system.get_avatar_sync(session_id))
        
        if session and avatar_sync:
            # Get all avatar states
            avatar_states = asyncio.run(avatar_sync.get_all_avatar_states())
            
            # Send to requester
            emit('sync_response', {
                'session_id': session_id,
                'session_state': session.state.value,
                'avatar_states': avatar_states,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        emit('error', {'message': str(e)})


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all active sessions"""
    try:
        sessions_data = []
        for session_id, session in collab_system.sessions.items():
            stats = session.get_session_stats()
            sessions_data.append(stats)
        
        return jsonify({
            'sessions': sessions_data,
            'total': len(sessions_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session_details(session_id: str):
    """Get detailed session information"""
    try:
        session = asyncio.run(collab_system.get_session(session_id))
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        stats = session.get_session_stats()
        users = asyncio.run(session.get_all_users())
        
        return jsonify({
            'session': stats,
            'users': [
                {
                    'user_id': u.user_id,
                    'username': u.username,
                    'role': u.role.value,
                    'avatar_id': u.avatar_id,
                    'is_speaking': u.is_speaking,
                    'last_update': u.last_update.isoformat()
                }
                for u in users
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>/investigations', methods=['GET'])
def get_investigations(session_id: str):
    """Get all investigations in session"""
    try:
        inv_space = asyncio.run(collab_system.get_investigation_space(session_id))
        if not inv_space:
            return jsonify({'error': 'Session not found'}), 404
        
        investigations = []
        for inv_id in inv_space.investigations:
            summary = asyncio.run(inv_space.get_investigation_summary(inv_id))
            investigations.append(summary)
        
        return jsonify({
            'investigations': investigations,
            'total': len(investigations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>/communication/history', methods=['GET'])
def get_chat_history(session_id: str):
    """Get chat message history"""
    try:
        limit = int(request.args.get('limit', 50))
        
        comm = asyncio.run(collab_system.get_communication(session_id))
        if not comm:
            return jsonify({'error': 'Session not found'}), 404
        
        messages = asyncio.run(comm.get_recent_messages(limit))
        
        return jsonify({
            'messages': messages,
            'count': len(messages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Get overall system statistics"""
    try:
        stats = collab_system.get_system_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'JUPITER Collaborative VR Server',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("JUPITER Collaborative VR Server")
    print("=" * 60)
    print("WebSocket + REST API for multi-user VR collaboration")
    print("Server starting on port 5006...")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5006, debug=False)
