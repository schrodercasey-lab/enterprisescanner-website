"""
Monitoring API Endpoints
RESTful API for Enterprise Scanner continuous monitoring dashboard

Provides endpoints for:
- Real-time monitoring dashboard data
- Security trend analysis
- Alert management
- Historical metrics

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

from .continuous_monitor import ContinuousSecurityMonitor, MonitoringMetric

# Create Flask Blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# Initialize monitor (use environment variable for DB path)
DB_PATH = os.getenv('MONITORING_DB_PATH', 'security_monitoring.db')
monitor = ContinuousSecurityMonitor(db_path=DB_PATH)


@monitoring_bp.route('/dashboard/<company_name>', methods=['GET'])
def get_dashboard(company_name: str):
    """
    Get comprehensive monitoring dashboard data
    
    Args:
        company_name: Company name to retrieve dashboard for
    
    Returns:
        JSON response with dashboard data:
        - current_status: Current security posture
        - category_scores: Breakdown by security category
        - vulnerability_summary: Vulnerability counts
        - trends: Historical trend analysis
        - active_alerts: Current unacknowledged alerts
    
    Example:
        GET /api/monitoring/dashboard/AcmeCorp
    """
    try:
        dashboard_data = monitor.get_monitoring_dashboard_data(company_name)
        
        if not dashboard_data['current_status']:
            return jsonify({
                'success': False,
                'error': f'No monitoring data found for company: {company_name}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_bp.route('/trends/<company_name>/<metric_name>', methods=['GET'])
def get_trends(company_name: str, metric_name: str):
    """
    Get security trend data for specific metric
    
    Args:
        company_name: Company name
        metric_name: Metric name (e.g., 'overall_score', 'critical_findings')
    
    Query Parameters:
        days: Number of days of history (default: 30)
    
    Returns:
        JSON response with time-series trend data
    
    Example:
        GET /api/monitoring/trends/AcmeCorp/overall_score?days=90
    """
    try:
        # Get days parameter
        days = request.args.get('days', default=30, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        # Validate metric name
        try:
            metric = MonitoringMetric[metric_name.upper()]
        except KeyError:
            return jsonify({
                'success': False,
                'error': f'Invalid metric name: {metric_name}. Valid metrics: {[m.name for m in MonitoringMetric]}'
            }), 400
        
        # Get trend data
        trend_data = monitor.get_security_trend(company_name, metric, days=days)
        
        if not trend_data:
            return jsonify({
                'success': False,
                'error': f'No trend data found for {company_name} - {metric_name}'
            }), 404
        
        return jsonify({
            'success': True,
            'company': company_name,
            'metric': metric_name,
            'days': days,
            'data': trend_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_bp.route('/alerts/<company_name>', methods=['GET'])
def get_alerts(company_name: str):
    """
    Get active alerts for company
    
    Args:
        company_name: Company name
    
    Query Parameters:
        severity: Filter by severity (critical, warning, info)
    
    Returns:
        JSON response with active alerts
    
    Example:
        GET /api/monitoring/alerts/AcmeCorp?severity=critical
    """
    try:
        # Get severity filter
        severity = request.args.get('severity', default=None, type=str)
        
        # Validate severity if provided
        if severity and severity.lower() not in ['critical', 'warning', 'info']:
            return jsonify({
                'success': False,
                'error': 'Invalid severity. Valid values: critical, warning, info'
            }), 400
        
        # Get active alerts
        alerts = monitor.get_active_alerts(company_name, severity)
        
        # Convert alerts to dict format
        alerts_data = [
            {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.value,
                'metric': alert.metric,
                'message': alert.message,
                'current_value': str(alert.current_value),
                'threshold': str(alert.threshold),
                'assessment_id': alert.assessment_id,
                'recommendations': alert.recommendations
            }
            for alert in alerts
        ]
        
        return jsonify({
            'success': True,
            'company': company_name,
            'count': len(alerts_data),
            'alerts': alerts_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert_endpoint(alert_id: str):
    """
    Acknowledge an alert
    
    Args:
        alert_id: Alert ID to acknowledge
    
    Returns:
        JSON response confirming acknowledgment
    
    Example:
        POST /api/monitoring/alerts/alert_123/acknowledge
    """
    try:
        # Acknowledge alert
        success = monitor.acknowledge_alert(alert_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': f'Alert not found or already acknowledged: {alert_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'Alert {alert_id} acknowledged successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_bp.route('/snapshot/<company_name>/latest', methods=['GET'])
def get_latest_snapshot(company_name: str):
    """
    Get latest security snapshot for company
    
    Args:
        company_name: Company name
    
    Returns:
        JSON response with latest snapshot data
    
    Example:
        GET /api/monitoring/snapshot/AcmeCorp/latest
    """
    try:
        snapshot = monitor.get_latest_snapshot(company_name)
        
        if not snapshot:
            return jsonify({
                'success': False,
                'error': f'No snapshot found for company: {company_name}'
            }), 404
        
        snapshot_data = {
            'timestamp': snapshot.timestamp.isoformat(),
            'assessment_id': snapshot.assessment_id,
            'company_name': snapshot.company_name,
            'overall_score': snapshot.overall_score,
            'risk_level': snapshot.risk_level,
            'category_scores': snapshot.category_scores,
            'vulnerability_counts': snapshot.vulnerability_counts,
            'total_findings': snapshot.total_findings,
            'critical_findings': snapshot.critical_findings,
            'high_findings': snapshot.high_findings,
            'compliance_score': snapshot.compliance_score,
            'metadata': snapshot.metadata
        }
        
        return jsonify({
            'success': True,
            'data': snapshot_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring API
    
    Returns:
        JSON response with service status
    
    Example:
        GET /api/monitoring/health
    """
    try:
        # Check database connection
        snapshot = monitor.get_latest_snapshot('test_company')
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'success': True,
        'service': 'monitoring_api',
        'status': 'operational',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@monitoring_bp.route('/metrics', methods=['GET'])
def get_available_metrics():
    """
    Get list of available monitoring metrics
    
    Returns:
        JSON response with metric definitions
    
    Example:
        GET /api/monitoring/metrics
    """
    metrics = [
        {
            'name': metric.name.lower(),
            'display_name': metric.value,
            'description': _get_metric_description(metric)
        }
        for metric in MonitoringMetric
    ]
    
    return jsonify({
        'success': True,
        'metrics': metrics,
        'count': len(metrics),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


def _get_metric_description(metric: MonitoringMetric) -> str:
    """Get human-readable metric description"""
    descriptions = {
        MonitoringMetric.OVERALL_SCORE: 'Overall security posture score (0-100)',
        MonitoringMetric.INFRASTRUCTURE_SCORE: 'Infrastructure security score',
        MonitoringMetric.NETWORK_SCORE: 'Network security score',
        MonitoringMetric.CLOUD_SCORE: 'Cloud infrastructure security score',
        MonitoringMetric.CONTAINER_SCORE: 'Container and orchestration security score',
        MonitoringMetric.VULNERABILITY_COUNT: 'Total vulnerability count',
        MonitoringMetric.CRITICAL_FINDINGS: 'Number of critical security findings',
        MonitoringMetric.HIGH_FINDINGS: 'Number of high-severity findings',
        MonitoringMetric.COMPLIANCE_SCORE: 'Compliance framework score'
    }
    
    return descriptions.get(metric, 'Security metric')


# Error handlers
@monitoring_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@monitoring_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# Example Flask app integration
def create_monitoring_app():
    """
    Create Flask app with monitoring blueprint
    
    Returns:
        Configured Flask app
    """
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(monitoring_bp)
    
    return app


if __name__ == '__main__':
    # Run standalone for testing
    app = create_monitoring_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
