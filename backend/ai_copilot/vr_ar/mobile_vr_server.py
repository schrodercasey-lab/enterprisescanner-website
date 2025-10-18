"""
JUPITER VR/AR Platform - Mobile VR Server (Module G.3.10)

WebSocket + REST API server for mobile VR optimization and monitoring.
Provides battery status, thermal management, and offline sync for mobile headsets.

WebSocket Events (Port 5010):
- mobile_status_update: Real-time battery/thermal updates (5 Hz)
- touch_gesture: Touch interaction events
- power_mode_changed: Power optimization notifications
- thermal_warning: Overheating alerts

REST API Endpoints:
- GET /api/device-info: Mobile device specifications
- GET /api/battery: Current battery status
- POST /api/power-mode: Set power optimization mode
- GET /api/thermal: Thermal status
- POST /api/offline-mode: Enable/disable offline mode
- GET /api/cache-stats: Offline cache statistics
- GET /api/health: Health check

Enterprise Scanner - JUPITER Platform
October 2025
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
from typing import Dict
import threading

from mobile_vr_support import (
    MobileVRSystem,
    MobileDevice,
    TouchGesture,
    PowerMode,
    ThermalState
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jupiter-mobile-vr-secret-2025'
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global mobile VR systems (one per connected device)
mobile_systems: Dict[str, MobileVRSystem] = {}
connected_clients: Dict[str, Dict] = {}


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': time.time(),
        'device': None,
        'monitoring': False
    }
    
    emit('connected', {
        'client_id': client_id,
        'server_time': time.time(),
        'supported_devices': [d.value for d in MobileDevice]
    })
    
    print(f"Mobile client connected: {client_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    if client_id in mobile_systems:
        del mobile_systems[client_id]
    
    print(f"Mobile client disconnected: {client_id}")


@socketio.on('register_device')
def handle_register_device(data):
    """Register mobile VR device"""
    client_id = request.sid
    device_name = data.get('device', 'meta_quest_3')
    
    try:
        device = MobileDevice[device_name.upper()]
        mobile_system = MobileVRSystem(device)
        mobile_systems[client_id] = mobile_system
        
        if client_id in connected_clients:
            connected_clients[client_id]['device'] = device.value
        
        emit('device_registered', {
            'success': True,
            'device': device.value,
            'profile': {
                'cpu': mobile_system.device_profile.cpu,
                'gpu': mobile_system.device_profile.gpu,
                'ram_gb': mobile_system.device_profile.ram_gb,
                'resolution': mobile_system.device_profile.display_resolution,
                'refresh_rate': mobile_system.device_profile.refresh_rate,
                'hand_tracking': mobile_system.device_profile.supports_hand_tracking,
                'passthrough': mobile_system.device_profile.supports_passthrough
            }
        })
        
        print(f"Registered device: {device.value} for client {client_id}")
    
    except Exception as e:
        emit('device_registered', {
            'success': False,
            'error': str(e)
        })


@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start mobile status monitoring"""
    client_id = request.sid
    
    if client_id in connected_clients:
        connected_clients[client_id]['monitoring'] = True
        
        emit('monitoring_started', {
            'client_id': client_id,
            'status': 'monitoring',
            'timestamp': time.time()
        })
        
        print(f"Started monitoring for client: {client_id}")


@socketio.on('stop_monitoring')
def handle_stop_monitoring(data):
    """Stop mobile status monitoring"""
    client_id = request.sid
    
    if client_id in connected_clients:
        connected_clients[client_id]['monitoring'] = False
        
        emit('monitoring_stopped', {
            'client_id': client_id,
            'status': 'stopped',
            'timestamp': time.time()
        })


@socketio.on('touch_gesture')
def handle_touch_gesture(data):
    """Process touch gesture from client"""
    client_id = request.sid
    
    try:
        gesture_name = data.get('gesture', 'tap')
        position = tuple(data.get('position', [0.5, 0.5]))
        
        # Broadcast gesture to other clients (for collaboration)
        socketio.emit('gesture_detected', {
            'client_id': client_id,
            'gesture': gesture_name,
            'position': position,
            'timestamp': time.time()
        })
        
        print(f"Touch gesture: {gesture_name} from {client_id}")
    
    except Exception as e:
        print(f"Error processing touch gesture: {e}")


@socketio.on('set_power_mode')
def handle_set_power_mode(data):
    """Set power optimization mode"""
    client_id = request.sid
    
    if client_id not in mobile_systems:
        emit('power_mode_set', {'success': False, 'error': 'Device not registered'})
        return
    
    try:
        mode_name = data.get('power_mode', 'balanced')
        mode = PowerMode[mode_name.upper()]
        
        result = mobile_systems[client_id].battery_optimizer.set_power_mode(mode)
        
        # Broadcast mode change
        socketio.emit('power_mode_changed', {
            'client_id': client_id,
            'mode': mode.value,
            'settings': result['settings'],
            'timestamp': time.time()
        })
        
        emit('power_mode_set', {
            'success': True,
            'mode': mode.value
        })
        
        print(f"Power mode changed to {mode.value} for {client_id}")
    
    except Exception as e:
        emit('power_mode_set', {
            'success': False,
            'error': str(e)
        })


@socketio.on('toggle_offline_mode')
def handle_toggle_offline_mode(data):
    """Toggle offline operation mode"""
    client_id = request.sid
    
    if client_id not in mobile_systems:
        emit('offline_mode_toggled', {'success': False, 'error': 'Device not registered'})
        return
    
    enable = data.get('enable', True)
    
    if enable:
        result = mobile_systems[client_id].enable_offline_mode()
    else:
        result = mobile_systems[client_id].disable_offline_mode()
    
    emit('offline_mode_toggled', {
        'success': True,
        'offline_mode': result['offline_mode'],
        'cached_threats': result.get('cached_threats', 0)
    })


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'jupiter-mobile-vr-support',
        'timestamp': time.time(),
        'connected_devices': len(mobile_systems),
        'connected_clients': len(connected_clients)
    })


@app.route('/api/device-info', methods=['GET'])
def get_device_info():
    """Get mobile device information"""
    client_id = request.args.get('client_id')
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found or device not registered'}), 404
    
    system = mobile_systems[client_id]
    profile = system.device_profile
    
    return jsonify({
        'device': profile.device.value,
        'cpu': profile.cpu,
        'gpu': profile.gpu,
        'ram_gb': profile.ram_gb,
        'storage_gb': profile.storage_gb,
        'battery_mah': profile.battery_mah,
        'display_resolution': profile.display_resolution,
        'refresh_rate': profile.refresh_rate,
        'hand_tracking': profile.supports_hand_tracking,
        'passthrough': profile.supports_passthrough,
        'typical_battery_life': profile.typical_battery_life
    })


@app.route('/api/battery', methods=['GET'])
def get_battery_status():
    """Get battery status"""
    client_id = request.args.get('client_id')
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found'}), 404
    
    system = mobile_systems[client_id]
    battery_status = system.battery_optimizer.get_battery_status()
    
    return jsonify({
        'level_percent': battery_status.level_percent,
        'is_charging': battery_status.is_charging,
        'remaining_time_minutes': battery_status.remaining_time_minutes,
        'power_mode': battery_status.power_mode.value,
        'estimated_session_time': battery_status.estimated_session_time,
        'timestamp': time.time()
    })


@app.route('/api/power-mode', methods=['POST'])
def set_power_mode():
    """Set power optimization mode"""
    data = request.get_json()
    client_id = data.get('client_id')
    mode_name = data.get('power_mode', 'balanced')
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found'}), 404
    
    try:
        mode = PowerMode[mode_name.upper()]
        result = mobile_systems[client_id].battery_optimizer.set_power_mode(mode)
        
        return jsonify({
            'success': True,
            'mode': mode.value,
            'settings': result['settings']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/thermal', methods=['GET'])
def get_thermal_status():
    """Get thermal status"""
    client_id = request.args.get('client_id')
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found'}), 404
    
    system = mobile_systems[client_id]
    thermal_status = system.thermal_manager.get_thermal_status()
    
    return jsonify({
        'temperature_celsius': thermal_status.temperature_celsius,
        'state': thermal_status.state.value,
        'throttling_active': thermal_status.throttling_active,
        'cpu_frequency_percent': thermal_status.cpu_frequency_percent,
        'gpu_frequency_percent': thermal_status.gpu_frequency_percent,
        'timestamp': time.time()
    })


@app.route('/api/offline-mode', methods=['POST'])
def toggle_offline_mode():
    """Enable/disable offline mode"""
    data = request.get_json()
    client_id = data.get('client_id')
    enable = data.get('enable', True)
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found'}), 404
    
    if enable:
        result = mobile_systems[client_id].enable_offline_mode()
    else:
        result = mobile_systems[client_id].disable_offline_mode()
    
    return jsonify({
        'success': True,
        'offline_mode': result['offline_mode'],
        'cached_threats': result.get('cached_threats', 0)
    })


@app.route('/api/cache-stats', methods=['GET'])
def get_cache_stats():
    """Get offline cache statistics"""
    client_id = request.args.get('client_id')
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found'}), 404
    
    system = mobile_systems[client_id]
    stats = system.offline_cache.get_cache_stats()
    
    return jsonify({
        'cache_stats': stats,
        'timestamp': time.time()
    })


@app.route('/api/status', methods=['GET'])
def get_full_status():
    """Get comprehensive mobile VR status"""
    client_id = request.args.get('client_id')
    
    if not client_id or client_id not in mobile_systems:
        return jsonify({'error': 'Client not found'}), 404
    
    system = mobile_systems[client_id]
    status = system.get_status()
    
    return jsonify({
        'status': status,
        'timestamp': time.time()
    })


# ============================================================================
# Background Status Broadcasting
# ============================================================================

def status_broadcast_loop():
    """Background thread to broadcast mobile status updates"""
    while True:
        # Get monitoring clients
        monitoring_clients = [
            (cid, info) for cid, info in connected_clients.items()
            if info.get('monitoring', False) and cid in mobile_systems
        ]
        
        if monitoring_clients:
            for client_id, info in monitoring_clients:
                try:
                    system = mobile_systems[client_id]
                    
                    # Get battery status
                    battery = system.battery_optimizer.get_battery_status()
                    
                    # Get thermal status
                    thermal = system.thermal_manager.get_thermal_status()
                    
                    # Send update
                    socketio.emit('mobile_status_update', {
                        'battery': {
                            'level': round(battery.level_percent, 1),
                            'charging': battery.is_charging,
                            'remaining_minutes': round(battery.remaining_time_minutes, 0),
                            'mode': battery.power_mode.value
                        },
                        'thermal': {
                            'temperature': round(thermal.temperature_celsius, 1),
                            'state': thermal.state.value,
                            'throttling': thermal.throttling_active
                        },
                        'timestamp': time.time()
                    }, room=client_id)
                    
                    # Check for warnings
                    if battery.level_percent < 20 and not battery.is_charging:
                        socketio.emit('battery_warning', {
                            'level': battery.level_percent,
                            'message': 'Battery low! Connect charger or enable power saver mode.'
                        }, room=client_id)
                    
                    if thermal.state in [ThermalState.HOT, ThermalState.CRITICAL]:
                        socketio.emit('thermal_warning', {
                            'temperature': thermal.temperature_celsius,
                            'state': thermal.state.value,
                            'message': 'Device heating up! Consider taking a break.'
                        }, room=client_id)
                
                except Exception as e:
                    print(f"Error broadcasting status for {client_id}: {e}")
        
        time.sleep(0.2)  # 5 Hz update rate


# ============================================================================
# Server Initialization
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("JUPITER Mobile VR Support Server")
    print("=" * 70)
    print(f"Starting server on port 5010...")
    print(f"WebSocket: ws://localhost:5010")
    print(f"REST API: http://localhost:5010/api/")
    print("=" * 70)
    
    # Start background broadcast thread
    broadcast_thread = threading.Thread(target=status_broadcast_loop, daemon=True)
    broadcast_thread.start()
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5010, debug=False, allow_unsafe_werkzeug=True)
