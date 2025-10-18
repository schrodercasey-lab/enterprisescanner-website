"""
Health Check & Monitoring Endpoints for Phase 3
Provides health, readiness, and metrics endpoints for production monitoring
"""

from flask import Blueprint, jsonify, Response
from datetime import datetime
import os
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.script_generator import ScriptGenerator
from modules.config_generator import ConfigGenerator
from modules.proactive_monitor import ProactiveMonitor
from modules.config import get_config
from modules.__version__ import __version__, __phase__, __release_date__

logger = logging.getLogger(__name__)

# Create Blueprint
phase3_health_bp = Blueprint('phase3_health', __name__, url_prefix='/api/phase3')


@phase3_health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Overall Phase 3 health check
    
    Returns:
        JSON with health status of all modules
        
    Status Codes:
        200: All modules healthy
        503: One or more modules unhealthy (degraded)
    
    Example:
        GET /api/phase3/health
    """
    status = {
        'status': 'healthy',
        'version': __version__,
        'phase': __phase__,
        'release_date': __release_date__,
        'timestamp': datetime.utcnow().isoformat(),
        'modules': {}
    }
    
    # Check Script Generator
    try:
        script_gen = ScriptGenerator()
        script_stats = script_gen.get_statistics()
        status['modules']['script_generator'] = {
            'status': 'healthy',
            'statistics': {
                'total_generated': script_stats['total_scripts_generated'],
                'safety_warnings': script_stats['safety_warnings_issued']
            }
        }
    except Exception as e:
        status['modules']['script_generator'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        status['status'] = 'degraded'
        logger.error(f"Script Generator health check failed: {e}")
    
    # Check Config Generator
    try:
        config_gen = ConfigGenerator()
        config_stats = config_gen.get_statistics()
        status['modules']['config_generator'] = {
            'status': 'healthy',
            'statistics': {
                'total_generated': config_stats['total_configs_generated']
            }
        }
    except Exception as e:
        status['modules']['config_generator'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        status['status'] = 'degraded'
        logger.error(f"Config Generator health check failed: {e}")
    
    # Check Proactive Monitor
    try:
        monitor = ProactiveMonitor()
        monitor_stats = monitor.get_statistics()
        status['modules']['proactive_monitor'] = {
            'status': 'healthy',
            'statistics': {
                'active_sessions': monitor_stats['active_sessions'],
                'alerts_generated': monitor_stats['alerts_generated'],
                'active_alerts': monitor_stats['active_alerts']
            }
        }
    except Exception as e:
        status['modules']['proactive_monitor'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        status['status'] = 'degraded'
        logger.error(f"Proactive Monitor health check failed: {e}")
    
    # Configuration check
    try:
        config = get_config()
        status['modules']['configuration'] = {
            'status': 'healthy',
            'environment': config.environment,
            'alert_channels': config.get_alert_channels()
        }
    except Exception as e:
        status['modules']['configuration'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        status['status'] = 'degraded'
        logger.error(f"Configuration health check failed: {e}")
    
    status_code = 200 if status['status'] == 'healthy' else 503
    return jsonify(status), status_code


@phase3_health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes-style readiness probe
    
    Checks if Phase 3 is ready to accept requests
    
    Returns:
        JSON with readiness status
        
    Status Codes:
        200: Ready to accept requests
        503: Not ready
    
    Example:
        GET /api/phase3/ready
    """
    checks = {
        'output_dirs_writable': False,
        'dependencies_loaded': False,
        'configuration_valid': False
    }
    
    # Check output directories are writable
    try:
        config = get_config()
        
        script_dir = Path(config.script_output_dir)
        config_dir = Path(config.config_output_dir)
        
        script_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        checks['output_dirs_writable'] = (
            os.access(script_dir, os.W_OK) and 
            os.access(config_dir, os.W_OK)
        )
    except Exception as e:
        logger.error(f"Output directory check failed: {e}")
        checks['output_dirs_writable'] = False
    
    # Check dependencies can be loaded
    try:
        ScriptGenerator()
        ConfigGenerator()
        ProactiveMonitor()
        checks['dependencies_loaded'] = True
    except Exception as e:
        logger.error(f"Dependency check failed: {e}")
        checks['dependencies_loaded'] = False
    
    # Check configuration is valid
    try:
        config = get_config()
        config.to_dict()
        checks['configuration_valid'] = True
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        checks['configuration_valid'] = False
    
    ready = all(checks.values())
    
    response = {
        'ready': ready,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    status_code = 200 if ready else 503
    return jsonify(response), status_code


@phase3_health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes-style liveness probe
    
    Simple check that the service is running
    
    Returns:
        JSON with liveness status
        
    Status Codes:
        200: Service is alive
    
    Example:
        GET /api/phase3/live
    """
    return jsonify({
        'alive': True,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@phase3_health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus-compatible metrics endpoint
    
    Returns metrics in Prometheus text format
    
    Returns:
        Plain text metrics in Prometheus format
        
    Status Codes:
        200: Metrics retrieved successfully
    
    Example:
        GET /api/phase3/metrics
    """
    try:
        script_gen = ScriptGenerator()
        config_gen = ConfigGenerator()
        monitor = ProactiveMonitor()
        
        script_stats = script_gen.get_statistics()
        config_stats = config_gen.get_statistics()
        monitor_stats = monitor.get_statistics()
        
        metrics_text = f"""# HELP phase3_info Phase 3 version information
# TYPE phase3_info gauge
phase3_info{{version="{__version__}",phase="{__phase__}",release_date="{__release_date__}"}} 1

# HELP phase3_scripts_generated_total Total remediation scripts generated
# TYPE phase3_scripts_generated_total counter
phase3_scripts_generated_total {script_stats['total_scripts_generated']}

# HELP phase3_scripts_by_language Scripts generated by language
# TYPE phase3_scripts_by_language counter
"""
        
        for language, count in script_stats['by_language'].items():
            metrics_text += f'phase3_scripts_by_language{{language="{language}"}} {count}\n'
        
        metrics_text += f"""
# HELP phase3_safety_warnings_total Total safety warnings issued
# TYPE phase3_safety_warnings_total counter
phase3_safety_warnings_total {script_stats['safety_warnings_issued']}

# HELP phase3_configs_generated_total Total configurations generated
# TYPE phase3_configs_generated_total counter
phase3_configs_generated_total {config_stats['total_configs_generated']}

# HELP phase3_configs_by_type Configs generated by type
# TYPE phase3_configs_by_type counter
"""
        
        for cfg_type, count in config_stats['by_type'].items():
            metrics_text += f'phase3_configs_by_type{{type="{cfg_type}"}} {count}\n'
        
        metrics_text += f"""
# HELP phase3_alerts_generated_total Total security alerts generated
# TYPE phase3_alerts_generated_total counter
phase3_alerts_generated_total {monitor_stats['alerts_generated']}

# HELP phase3_active_sessions Current active monitoring sessions
# TYPE phase3_active_sessions gauge
phase3_active_sessions {monitor_stats['active_sessions']}

# HELP phase3_active_alerts Current active alerts
# TYPE phase3_active_alerts gauge
phase3_active_alerts {monitor_stats['active_alerts']}

# HELP phase3_active_rules Current active monitoring rules
# TYPE phase3_active_rules gauge
phase3_active_rules {monitor_stats['active_rules']}

# HELP phase3_alerts_by_severity Alerts by severity level
# TYPE phase3_alerts_by_severity counter
"""
        
        for severity, count in monitor_stats['alerts_by_severity'].items():
            metrics_text += f'phase3_alerts_by_severity{{severity="{severity}"}} {count}\n'
        
        return Response(metrics_text, mimetype='text/plain; version=0.0.4; charset=utf-8')
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return Response(
            f"# Error generating metrics: {str(e)}\n",
            status=500,
            mimetype='text/plain; charset=utf-8'
        )


@phase3_health_bp.route('/stats', methods=['GET'])
def statistics():
    """
    Detailed statistics endpoint (JSON format)
    
    Returns detailed statistics from all Phase 3 modules
    
    Returns:
        JSON with detailed statistics
        
    Status Codes:
        200: Statistics retrieved successfully
        500: Error retrieving statistics
    
    Example:
        GET /api/phase3/stats
    """
    try:
        script_gen = ScriptGenerator()
        config_gen = ConfigGenerator()
        monitor = ProactiveMonitor()
        config = get_config()
        
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': __version__,
            'environment': config.environment,
            'script_generator': script_gen.get_statistics(),
            'config_generator': config_gen.get_statistics(),
            'proactive_monitor': monitor.get_statistics(),
            'configuration': {
                'monitoring_interval': config.monitoring_interval,
                'alert_channels': config.get_alert_channels(),
                'performance_monitoring': config.enable_performance_monitoring
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Statistics endpoint failed: {e}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@phase3_health_bp.route('/version', methods=['GET'])
def version():
    """
    Version information endpoint
    
    Returns:
        JSON with version details
        
    Status Codes:
        200: Version info retrieved
    
    Example:
        GET /api/phase3/version
    """
    from modules.__version__ import get_version_info
    
    version_info = get_version_info()
    version_info['timestamp'] = datetime.utcnow().isoformat()
    
    return jsonify(version_info), 200


# Error handlers
@phase3_health_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'timestamp': datetime.utcnow().isoformat()
    }), 404


@phase3_health_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500


# Flask app factory
def create_health_app():
    """
    Create Flask app with health endpoints
    
    Returns:
        Flask app instance
    """
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(phase3_health_bp)
    
    return app


def main():
    """Run standalone health check server"""
    app = create_health_app()
    
    port = int(os.getenv('PHASE3_HEALTH_PORT', '5003'))
    host = os.getenv('PHASE3_HEALTH_HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*80}")
    print(f"Phase 3 Health Check Server")
    print(f"{'='*80}")
    print(f"Version: {__version__}")
    print(f"Listening on: http://{host}:{port}")
    print(f"Endpoints:")
    print(f"  - GET /api/phase3/health   (Overall health)")
    print(f"  - GET /api/phase3/ready    (Readiness probe)")
    print(f"  - GET /api/phase3/live     (Liveness probe)")
    print(f"  - GET /api/phase3/metrics  (Prometheus metrics)")
    print(f"  - GET /api/phase3/stats    (JSON statistics)")
    print(f"  - GET /api/phase3/version  (Version info)")
    print(f"{'='*80}\n")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
