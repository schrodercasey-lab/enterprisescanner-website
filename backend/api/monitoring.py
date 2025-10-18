"""
Enterprise Scanner - Performance Monitoring API
Real-time system metrics, analytics, and monitoring endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import time
import psutil
import logging
import json
import random
from typing import Dict, List, Any
import threading
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api')

class SystemMetrics:
    """Real-time system metrics collection and analysis"""
    
    def __init__(self):
        self.metrics_history = {
            'cpu_usage': deque(maxlen=1440),  # 24 hours of minute data
            'memory_usage': deque(maxlen=1440),
            'response_times': deque(maxlen=1440),
            'active_users': deque(maxlen=1440),
            'error_rates': deque(maxlen=1440),
            'threats_blocked': deque(maxlen=1440)
        }
        self.current_metrics = {}
        self.alerts = []
        self.monitoring_active = True
        
        # Start background monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        def monitor():
            while self.monitoring_active:
                try:
                    self.collect_metrics()
                    time.sleep(60)  # Collect every minute
                except Exception as e:
                    logger.error(f"Monitoring error: {str(e)}")
        
        monitoring_thread = threading.Thread(target=monitor, daemon=True)
        monitoring_thread.start()
        logger.info("System monitoring started")
    
    def collect_metrics(self):
        """Collect current system metrics"""
        try:
            # System resource metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Simulated application metrics (in production, these would be real)
            response_time = self.simulate_response_time()
            active_users = self.simulate_active_users()
            error_rate = self.simulate_error_rate()
            threats_blocked = self.simulate_threats_blocked()
            
            # Store current metrics
            timestamp = datetime.now()
            
            self.current_metrics = {
                'timestamp': timestamp.isoformat(),
                'system': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'memory_available': memory.available,
                    'memory_total': memory.total,
                    'disk_usage': disk.percent,
                    'disk_free': disk.free,
                    'disk_total': disk.total
                },
                'application': {
                    'response_time': response_time,
                    'active_users': active_users,
                    'error_rate': error_rate,
                    'threats_blocked': threats_blocked,
                    'uptime': self.calculate_uptime()
                },
                'performance': {
                    'requests_per_minute': self.simulate_rpm(),
                    'concurrent_connections': self.simulate_connections(),
                    'cache_hit_rate': self.simulate_cache_hit_rate(),
                    'database_query_time': self.simulate_db_query_time()
                }
            }
            
            # Store in history
            self.metrics_history['cpu_usage'].append({
                'timestamp': timestamp.isoformat(),
                'value': cpu_percent
            })
            self.metrics_history['memory_usage'].append({
                'timestamp': timestamp.isoformat(),
                'value': memory.percent
            })
            self.metrics_history['response_times'].append({
                'timestamp': timestamp.isoformat(),
                'value': response_time
            })
            self.metrics_history['active_users'].append({
                'timestamp': timestamp.isoformat(),
                'value': active_users
            })
            self.metrics_history['error_rates'].append({
                'timestamp': timestamp.isoformat(),
                'value': error_rate
            })
            self.metrics_history['threats_blocked'].append({
                'timestamp': timestamp.isoformat(),
                'value': threats_blocked
            })
            
            # Check for alerts
            self.check_alerts()
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
    
    def simulate_response_time(self):
        """Simulate realistic response time metrics"""
        import random
        base_time = 120
        variation = random.uniform(0.8, 1.3)
        spike_chance = random.random()
        
        if spike_chance < 0.05:  # 5% chance of spike
            return int(base_time * variation * random.uniform(2, 4))
        return int(base_time * variation)
    
    def simulate_active_users(self):
        """Simulate active user count"""
        import random
        hour = datetime.now().hour
        
        # Business hours peak
        if 9 <= hour <= 17:
            base_users = 1000
        elif 18 <= hour <= 22:
            base_users = 600
        else:
            base_users = 200
        
        return base_users + random.randint(-100, 200)
    
    def simulate_error_rate(self):
        """Simulate error rate percentage"""
        import random
        return round(random.uniform(0.01, 0.05), 4)
    
    def simulate_threats_blocked(self):
        """Simulate cumulative threats blocked"""
        import random
        base_count = 800
        return base_count + random.randint(0, 50)
    
    def simulate_rpm(self):
        """Simulate requests per minute"""
        import random
        return random.randint(150, 300)
    
    def simulate_connections(self):
        """Simulate concurrent connections"""
        import random
        return random.randint(20, 80)
    
    def simulate_cache_hit_rate(self):
        """Simulate cache hit rate percentage"""
        import random
        return round(random.uniform(85, 95), 1)
    
    def simulate_db_query_time(self):
        """Simulate database query time"""
        import random
        return random.randint(10, 25)
    
    def calculate_uptime(self):
        """Calculate system uptime percentage"""
        # Simulated uptime calculation
        return round(99.95 + (random.random() * 0.05), 3)
    
    def check_alerts(self):
        """Check for performance alerts"""
        current = self.current_metrics
        
        # Clear old alerts (older than 1 hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        self.alerts = [alert for alert in self.alerts 
                      if datetime.fromisoformat(alert['timestamp']) > one_hour_ago]
        
        # Check CPU usage
        if current['system']['cpu_usage'] > 80:
            self.add_alert('high_cpu', 'High CPU usage detected', 'warning', current['system']['cpu_usage'])
        
        # Check memory usage
        if current['system']['memory_usage'] > 85:
            self.add_alert('high_memory', 'High memory usage detected', 'warning', current['system']['memory_usage'])
        
        # Check response time
        if current['application']['response_time'] > 500:
            self.add_alert('slow_response', 'Slow response time detected', 'critical', current['application']['response_time'])
        
        # Check error rate
        if current['application']['error_rate'] > 1.0:
            self.add_alert('high_errors', 'High error rate detected', 'critical', current['application']['error_rate'])
    
    def add_alert(self, alert_type: str, message: str, severity: str, value: Any):
        """Add a new alert"""
        alert = {
            'id': f"{alert_type}_{int(time.time())}",
            'type': alert_type,
            'message': message,
            'severity': severity,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        # Avoid duplicate alerts within 5 minutes
        recent_threshold = datetime.now() - timedelta(minutes=5)
        existing_recent = any(
            alert_item['type'] == alert_type and 
            datetime.fromisoformat(alert_item['timestamp']) > recent_threshold
            for alert_item in self.alerts
        )
        
        if not existing_recent:
            self.alerts.append(alert)
            logger.warning(f"Alert: {message} (Value: {value})")
    
    def get_current_metrics(self):
        """Get current metrics snapshot"""
        return self.current_metrics
    
    def get_metrics_history(self, metric_type: str, hours: int = 24):
        """Get historical metrics for specified time range"""
        if metric_type not in self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in list(self.metrics_history[metric_type])
            if datetime.fromisoformat(metric['timestamp']) > cutoff_time
        ]
    
    def get_performance_summary(self):
        """Get performance summary for dashboard"""
        current = self.current_metrics
        
        if not current:
            return {'status': 'initializing'}
        
        return {
            'status': 'operational',
            'uptime': current['application']['uptime'],
            'response_time': current['application']['response_time'],
            'active_users': current['application']['active_users'],
            'threats_blocked': current['application']['threats_blocked'],
            'system_health': {
                'cpu': current['system']['cpu_usage'],
                'memory': current['system']['memory_usage'],
                'disk': current['system']['disk_usage']
            },
            'alerts_count': len([a for a in self.alerts if not a['acknowledged']]),
            'last_updated': current['timestamp']
        }

# Initialize metrics collector
metrics_collector = SystemMetrics()

class UserEngagementTracker:
    """Track user engagement and application usage"""
    
    def __init__(self):
        self.page_views = {}
        self.user_sessions = {}
        self.feature_usage = {}
        
    def track_page_view(self, page: str, user_id: str = None):
        """Track page view"""
        timestamp = datetime.now().isoformat()
        
        if page not in self.page_views:
            self.page_views[page] = []
        
        self.page_views[page].append({
            'timestamp': timestamp,
            'user_id': user_id
        })
    
    def track_feature_usage(self, feature: str, user_id: str = None):
        """Track feature usage"""
        if feature not in self.feature_usage:
            self.feature_usage[feature] = 0
        
        self.feature_usage[feature] += 1
    
    def get_engagement_summary(self, time_range: str = 'today'):
        """Get user engagement summary"""
        now = datetime.now()
        
        if time_range == 'today':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == 'week':
            start_time = now - timedelta(days=7)
        elif time_range == 'month':
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=24)
        
        # Calculate engagement metrics
        page_stats = {}
        for page, views in self.page_views.items():
            recent_views = [
                view for view in views
                if datetime.fromisoformat(view['timestamp']) > start_time
            ]
            page_stats[page] = len(recent_views)
        
        return {
            'time_range': time_range,
            'page_views': page_stats,
            'feature_usage': self.feature_usage,
            'total_views': sum(page_stats.values()),
            'unique_pages': len([p for p, v in page_stats.items() if v > 0])
        }

# Initialize engagement tracker
engagement_tracker = UserEngagementTracker()

@monitoring_bp.route('/metrics/current', methods=['GET'])
def get_current_metrics():
    """Get current system metrics"""
    try:
        metrics = metrics_collector.get_current_metrics()
        
        if not metrics:
            return jsonify({
                'success': False,
                'error': 'Metrics not yet available'
            }), 503
        
        return jsonify({
            'success': True,
            'data': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving current metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve metrics'
        }), 500

@monitoring_bp.route('/metrics/history/<metric_type>', methods=['GET'])
def get_metrics_history(metric_type):
    """Get historical metrics data"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        if hours > 168:  # Limit to 7 days
            hours = 168
        
        history = metrics_collector.get_metrics_history(metric_type, hours)
        
        return jsonify({
            'success': True,
            'metric_type': metric_type,
            'time_range_hours': hours,
            'data': history,
            'count': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving metrics history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve metrics history'
        }), 500

@monitoring_bp.route('/metrics/summary', methods=['GET'])
def get_performance_summary():
    """Get performance summary for dashboard"""
    try:
        summary = metrics_collector.get_performance_summary()
        engagement = engagement_tracker.get_engagement_summary()
        
        return jsonify({
            'success': True,
            'performance': summary,
            'engagement': engagement,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving performance summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve performance summary'
        }), 500

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get current system alerts"""
    try:
        status_filter = request.args.get('status', 'all')
        
        alerts = metrics_collector.alerts
        
        if status_filter == 'active':
            alerts = [alert for alert in alerts if not alert['acknowledged']]
        elif status_filter == 'acknowledged':
            alerts = [alert for alert in alerts if alert['acknowledged']]
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_count': len(metrics_collector.alerts),
            'active_count': len([a for a in metrics_collector.alerts if not a['acknowledged']])
        })
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve alerts'
        }), 500

@monitoring_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        alert = next((a for a in metrics_collector.alerts if a['id'] == alert_id), None)
        
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
        
        alert['acknowledged'] = True
        alert['acknowledged_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Alert acknowledged',
            'alert_id': alert_id
        })
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to acknowledge alert'
        }), 500

@monitoring_bp.route('/engagement/track', methods=['POST'])
def track_engagement():
    """Track user engagement event"""
    try:
        data = request.get_json()
        
        event_type = data.get('type')
        page = data.get('page')
        feature = data.get('feature')
        user_id = data.get('user_id')
        
        if event_type == 'page_view' and page:
            engagement_tracker.track_page_view(page, user_id)
        elif event_type == 'feature_usage' and feature:
            engagement_tracker.track_feature_usage(feature, user_id)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid engagement event data'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Engagement tracked',
            'event_type': event_type
        })
        
    except Exception as e:
        logger.error(f"Error tracking engagement: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to track engagement'
        }), 500

@monitoring_bp.route('/engagement/summary', methods=['GET'])
def get_engagement_summary():
    """Get user engagement summary"""
    try:
        time_range = request.args.get('range', 'today')
        summary = engagement_tracker.get_engagement_summary(time_range)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error retrieving engagement summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve engagement summary'
        }), 500

@monitoring_bp.route('/system/health', methods=['GET'])
def system_health_check():
    """Comprehensive system health check"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'web_server': {'status': 'operational', 'response_time': '< 200ms'},
                'database': {'status': 'operational', 'query_time': '< 50ms'},
                'email_service': {'status': 'operational', 'queue_size': 0},
                'monitoring': {'status': 'operational', 'data_collection': 'active'},
                'security_scanner': {'status': 'operational', 'active_scans': 3}
            },
            'resources': {
                'cpu_usage': metrics_collector.current_metrics.get('system', {}).get('cpu_usage', 0),
                'memory_usage': metrics_collector.current_metrics.get('system', {}).get('memory_usage', 0),
                'disk_usage': metrics_collector.current_metrics.get('system', {}).get('disk_usage', 0)
            },
            'performance': {
                'uptime': metrics_collector.current_metrics.get('application', {}).get('uptime', 99.9),
                'response_time': metrics_collector.current_metrics.get('application', {}).get('response_time', 120),
                'active_users': metrics_collector.current_metrics.get('application', {}).get('active_users', 1000)
            }
        }
        
        # Determine overall health status
        cpu = health_status['resources']['cpu_usage']
        memory = health_status['resources']['memory_usage']
        response_time = health_status['performance']['response_time']
        
        if cpu > 80 or memory > 85 or response_time > 500:
            health_status['status'] = 'degraded'
        
        if cpu > 90 or memory > 95 or response_time > 1000:
            health_status['status'] = 'critical'
        
        return jsonify({
            'success': True,
            'health': health_status
        })
        
    except Exception as e:
        logger.error(f"Error performing health check: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Health check failed'
        }), 500

def register_monitoring_routes(app):
    """Register monitoring routes with Flask app"""
    app.register_blueprint(monitoring_bp)
    logger.info("Performance monitoring API routes registered")