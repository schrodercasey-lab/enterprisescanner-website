"""
JUPITER VR/AR Platform - Performance Optimization Server (Module G.3.9)

WebSocket + REST API server for real-time performance monitoring and optimization.
Provides performance metrics streaming and quality control for VR clients.

WebSocket Events (Port 5009):
- performance_update: Real-time performance metrics (30 Hz)
- quality_change: Quality level adjustments
- optimization_applied: Optimization notifications
- benchmark_start/complete: Performance benchmarking

REST API Endpoints:
- GET /api/performance: Current performance metrics
- GET /api/quality-levels: Available quality levels
- POST /api/quality: Set quality level
- GET /api/optimizations: Applied optimizations
- POST /api/benchmark: Run performance benchmark
- GET /api/hardware: Hardware profile
- GET /api/health: Health check

Enterprise Scanner - JUPITER Platform
October 2025
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
from typing import Dict, List
import threading

from performance_optimization import (
    PerformanceOptimizationSystem,
    QualityLevel,
    PerformanceData,
    OptimizationStrategy
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jupiter-performance-secret-2025'
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global performance system
performance_system: PerformanceOptimizationSystem = None
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
        'quality_level': 'high',
        'monitoring': False
    }
    
    emit('connected', {
        'client_id': client_id,
        'server_time': time.time(),
        'target_fps': performance_system.target_fps if performance_system else 90.0
    })
    
    print(f"Client connected: {client_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    
    print(f"Client disconnected: {client_id}")


@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start performance monitoring for client"""
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
    """Stop performance monitoring for client"""
    client_id = request.sid
    
    if client_id in connected_clients:
        connected_clients[client_id]['monitoring'] = False
        
        emit('monitoring_stopped', {
            'client_id': client_id,
            'status': 'stopped',
            'timestamp': time.time()
        })
        
        print(f"Stopped monitoring for client: {client_id}")


@socketio.on('set_quality')
def handle_set_quality(data):
    """Set quality level for performance"""
    try:
        quality_name = data.get('quality_level', 'high')
        quality = QualityLevel[quality_name.upper()]
        
        if performance_system:
            performance_system.force_quality_level(quality)
            
            # Broadcast quality change to all clients
            socketio.emit('quality_changed', {
                'quality_level': quality.value,
                'config': performance_system.adaptive_quality.get_current_config(),
                'timestamp': time.time()
            })
            
            print(f"Quality level changed to: {quality.value}")
            
            emit('quality_set', {
                'success': True,
                'quality_level': quality.value
            })
        else:
            emit('quality_set', {
                'success': False,
                'error': 'Performance system not initialized'
            })
    
    except Exception as e:
        emit('quality_set', {
            'success': False,
            'error': str(e)
        })


@socketio.on('request_benchmark')
def handle_request_benchmark(data):
    """Run performance benchmark"""
    try:
        duration = data.get('duration', 5.0)
        
        emit('benchmark_started', {
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Run benchmark in background thread
        def run_benchmark():
            if performance_system:
                results = performance_system.benchmark(duration_seconds=duration)
                
                socketio.emit('benchmark_complete', {
                    'results': results,
                    'timestamp': time.time()
                }, room=request.sid)
        
        thread = threading.Thread(target=run_benchmark)
        thread.start()
        
        print(f"Started benchmark: {duration}s")
    
    except Exception as e:
        emit('benchmark_error', {
            'error': str(e)
        })


@socketio.on('get_status')
def handle_get_status():
    """Get current performance status"""
    if performance_system:
        status = performance_system.get_status()
        emit('performance_status', status)
    else:
        emit('performance_status', {'error': 'System not initialized'})


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'jupiter-performance-optimization',
        'timestamp': time.time(),
        'connected_clients': len(connected_clients),
        'system_running': performance_system is not None and performance_system.running
    })


@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get current performance metrics"""
    if not performance_system:
        return jsonify({'error': 'Performance system not initialized'}), 503
    
    status = performance_system.get_status()
    
    return jsonify({
        'performance': status['performance'],
        'quality_level': status['quality_level'],
        'timestamp': time.time()
    })


@app.route('/api/quality-levels', methods=['GET'])
def get_quality_levels():
    """Get available quality levels"""
    quality_levels = [
        {
            'name': q.value,
            'display_name': q.value.title(),
            'description': get_quality_description(q)
        }
        for q in QualityLevel
    ]
    
    return jsonify({
        'quality_levels': quality_levels,
        'current': performance_system.adaptive_quality.current_quality.value if performance_system else 'high'
    })


def get_quality_description(quality: QualityLevel) -> str:
    """Get description for quality level"""
    descriptions = {
        QualityLevel.ULTRA: "Maximum quality - 120 FPS target, highest visual fidelity",
        QualityLevel.HIGH: "High quality - 90 FPS target, excellent visuals",
        QualityLevel.MEDIUM: "Balanced - 72 FPS target, good performance",
        QualityLevel.LOW: "Performance mode - 60 FPS minimum, optimized",
        QualityLevel.POTATO: "Minimum viable - 45 FPS, maximum compatibility"
    }
    return descriptions.get(quality, "Unknown quality level")


@app.route('/api/quality', methods=['POST'])
def set_quality():
    """Set quality level"""
    try:
        data = request.get_json()
        quality_name = data.get('quality_level', 'high')
        quality = QualityLevel[quality_name.upper()]
        
        if performance_system:
            performance_system.force_quality_level(quality)
            
            # Broadcast to all connected clients
            socketio.emit('quality_changed', {
                'quality_level': quality.value,
                'config': performance_system.adaptive_quality.get_current_config(),
                'timestamp': time.time()
            })
            
            return jsonify({
                'success': True,
                'quality_level': quality.value,
                'config': performance_system.adaptive_quality.get_current_config()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Performance system not initialized'
            }), 503
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/optimizations', methods=['GET'])
def get_optimizations():
    """Get applied optimizations"""
    if not performance_system:
        return jsonify({'error': 'Performance system not initialized'}), 503
    
    optimizations = performance_system.optimization_engine.get_applied_optimizations()
    
    return jsonify({
        'optimizations': optimizations,
        'count': len(optimizations),
        'timestamp': time.time()
    })


@app.route('/api/benchmark', methods=['POST'])
def run_benchmark():
    """Run performance benchmark"""
    try:
        data = request.get_json()
        duration = data.get('duration', 5.0)
        
        if not performance_system:
            return jsonify({'error': 'Performance system not initialized'}), 503
        
        results = performance_system.benchmark(duration_seconds=duration)
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': time.time()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/hardware', methods=['GET'])
def get_hardware():
    """Get hardware profile"""
    if not performance_system:
        return jsonify({'error': 'Performance system not initialized'}), 503
    
    profile = performance_system.hardware_profile
    
    return jsonify({
        'device_name': profile.device_name,
        'max_fps': profile.max_fps,
        'recommended_quality': profile.recommended_quality.value,
        'gpu_memory_gb': profile.gpu_memory,
        'cpu_cores': profile.cpu_cores,
        'ram_gb': profile.ram,
        'resolution': {
            'width': profile.headset_resolution[0],
            'height': profile.headset_resolution[1]
        },
        'features': {
            'foveated_rendering': profile.supports_foveated,
            'motion_reprojection': profile.supports_reprojection
        }
    })


@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get memory usage statistics"""
    if not performance_system:
        return jsonify({'error': 'Performance system not initialized'}), 503
    
    memory_stats = performance_system.resource_manager.get_memory_stats()
    
    return jsonify({
        'memory': memory_stats,
        'timestamp': time.time()
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive performance statistics"""
    if not performance_system:
        return jsonify({'error': 'Performance system not initialized'}), 503
    
    stats = performance_system.monitor.get_statistics()
    
    return jsonify({
        'statistics': stats,
        'timestamp': time.time()
    })


# ============================================================================
# Background Performance Broadcasting
# ============================================================================

def performance_broadcast_loop():
    """Background thread to broadcast performance updates"""
    while True:
        if performance_system and performance_system.running:
            # Get current metrics
            metrics = performance_system.monitor.capture_metrics()
            
            # Broadcast to monitoring clients
            monitoring_clients = [
                cid for cid, info in connected_clients.items()
                if info.get('monitoring', False)
            ]
            
            if monitoring_clients:
                performance_data = {
                    'timestamp': metrics.timestamp,
                    'fps': round(metrics.fps, 1),
                    'frame_time': round(metrics.frame_time, 2),
                    'gpu_usage': round(metrics.gpu_usage, 1),
                    'cpu_usage': round(metrics.cpu_usage, 1),
                    'memory_mb': round(metrics.memory_usage, 1),
                    'quality_level': metrics.quality_level.value
                }
                
                for client_id in monitoring_clients:
                    socketio.emit('performance_update', performance_data, room=client_id)
        
        time.sleep(1.0 / 30.0)  # 30 Hz update rate


# ============================================================================
# Server Initialization
# ============================================================================

def initialize_performance_system():
    """Initialize the performance optimization system"""
    global performance_system
    
    print("Initializing Performance Optimization System...")
    performance_system = PerformanceOptimizationSystem(target_fps=90.0)
    performance_system.start()
    print("Performance system started (target: 90 FPS)")


if __name__ == '__main__':
    print("=" * 70)
    print("JUPITER VR Performance Optimization Server")
    print("=" * 70)
    print(f"Starting server on port 5009...")
    print(f"WebSocket: ws://localhost:5009")
    print(f"REST API: http://localhost:5009/api/")
    print("=" * 70)
    
    # Initialize performance system
    initialize_performance_system()
    
    # Start background broadcast thread
    broadcast_thread = threading.Thread(target=performance_broadcast_loop, daemon=True)
    broadcast_thread.start()
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5009, debug=False, allow_unsafe_werkzeug=True)
