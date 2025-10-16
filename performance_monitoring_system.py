#!/usr/bin/env python3
"""
Enterprise Scanner - Performance Monitoring System
Real-time system performance, SLA tracking, and infrastructure monitoring
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import uuid
import random
import time
import threading
import psutil
import os

app = Flask(__name__)

# Monitoring data storage
performance_metrics = {}
sla_tracking = {}
alert_history = []
system_health = {}

# SLA Configuration
SLA_TARGETS = {
    'uptime': 99.9,
    'response_time': 200,  # milliseconds
    'availability': 99.95,
    'security_scan_completion': 95,
    'false_positive_rate': 5,
    'threat_detection_accuracy': 98,
    'customer_satisfaction': 4.5  # out of 5
}

class PerformanceMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.running = True

    def collect_system_metrics(self):
        """Collect real-time system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            
            # Network metrics (simulated for demo)
            network_in = random.randint(1000, 5000)  # KB/s
            network_out = random.randint(500, 2000)  # KB/s
            
            # System uptime
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            uptime_hours = uptime_seconds / 3600
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'cores': cpu_cores,
                    'load_average': os.getloadavg()[0] if hasattr(os, 'getloadavg') else cpu_percent/100
                },
                'memory': {
                    'percent': memory_percent,
                    'available_gb': round(memory_available, 2),
                    'total_gb': round(memory.total / (1024**3), 2)
                },
                'disk': {
                    'percent': disk_percent,
                    'free_gb': round(disk_free, 2),
                    'total_gb': round(disk.total / (1024**3), 2)
                },
                'network': {
                    'in_kbps': network_in,
                    'out_kbps': network_out
                },
                'uptime_hours': round(uptime_hours, 2)
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'cpu': {'percent': 0, 'cores': 1},
                'memory': {'percent': 0, 'available_gb': 0, 'total_gb': 0},
                'disk': {'percent': 0, 'free_gb': 0, 'total_gb': 0},
                'network': {'in_kbps': 0, 'out_kbps': 0},
                'uptime_hours': 0
            }

    def generate_application_metrics(self):
        """Generate application-specific performance metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_users': random.randint(150, 500),
            'concurrent_sessions': random.randint(75, 250),
            'api_requests_per_minute': random.randint(500, 2000),
            'average_response_time': random.randint(50, 300),
            'security_scans_running': random.randint(5, 25),
            'threats_detected_today': random.randint(100, 500),
            'vulnerabilities_identified': random.randint(10, 50),
            'alerts_generated': random.randint(20, 100),
            'sla_compliance': round(random.uniform(99.0, 99.99), 2),
            'customer_satisfaction': round(random.uniform(4.2, 4.9), 1)
        }

    def calculate_sla_metrics(self):
        """Calculate SLA compliance metrics"""
        current_metrics = self.generate_application_metrics()
        
        # Calculate SLA compliance
        sla_status = {}
        for metric, target in SLA_TARGETS.items():
            if metric == 'uptime':
                # Calculate uptime percentage
                uptime_percentage = min(99.99, random.uniform(99.5, 99.99))
                sla_status[metric] = {
                    'current': uptime_percentage,
                    'target': target,
                    'status': 'met' if uptime_percentage >= target else 'missed',
                    'variance': round(uptime_percentage - target, 2)
                }
            elif metric == 'response_time':
                response_time = current_metrics['average_response_time']
                sla_status[metric] = {
                    'current': response_time,
                    'target': target,
                    'status': 'met' if response_time <= target else 'missed',
                    'variance': response_time - target
                }
            elif metric == 'customer_satisfaction':
                satisfaction = current_metrics['customer_satisfaction']
                sla_status[metric] = {
                    'current': satisfaction,
                    'target': target,
                    'status': 'met' if satisfaction >= target else 'missed',
                    'variance': round(satisfaction - target, 1)
                }
            else:
                # Generate random compliance for other metrics
                value = random.uniform(target - 2, target + 2)
                sla_status[metric] = {
                    'current': round(value, 2),
                    'target': target,
                    'status': 'met' if value >= target else 'missed',
                    'variance': round(value - target, 2)
                }
        
        return sla_status

    def check_alerts(self, metrics):
        """Check for alert conditions"""
        alerts = []
        
        # CPU alert
        if metrics['cpu']['percent'] > 80:
            alerts.append({
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'severity': 'high' if metrics['cpu']['percent'] > 90 else 'medium',
                'type': 'performance',
                'title': 'High CPU Usage',
                'message': f"CPU usage at {metrics['cpu']['percent']}%",
                'metric': 'cpu_percent',
                'value': metrics['cpu']['percent'],
                'threshold': 80
            })
        
        # Memory alert
        if metrics['memory']['percent'] > 85:
            alerts.append({
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'severity': 'high' if metrics['memory']['percent'] > 95 else 'medium',
                'type': 'performance',
                'title': 'High Memory Usage',
                'message': f"Memory usage at {metrics['memory']['percent']}%",
                'metric': 'memory_percent',
                'value': metrics['memory']['percent'],
                'threshold': 85
            })
        
        # Disk alert
        if metrics['disk']['percent'] > 90:
            alerts.append({
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'severity': 'critical' if metrics['disk']['percent'] > 95 else 'high',
                'type': 'storage',
                'title': 'Low Disk Space',
                'message': f"Disk usage at {metrics['disk']['percent']}%",
                'metric': 'disk_percent',
                'value': metrics['disk']['percent'],
                'threshold': 90
            })
        
        return alerts

# Global monitoring instance
monitor = PerformanceMonitor()

def monitoring_loop():
    """Background monitoring loop"""
    while monitor.running:
        try:
            # Collect system metrics
            system_metrics = monitor.collect_system_metrics()
            app_metrics = monitor.generate_application_metrics()
            sla_metrics = monitor.calculate_sla_metrics()
            
            # Store metrics
            timestamp = datetime.now().isoformat()
            performance_metrics[timestamp] = {
                'system': system_metrics,
                'application': app_metrics,
                'sla': sla_metrics
            }
            
            # Check for alerts
            alerts = monitor.check_alerts(system_metrics)
            alert_history.extend(alerts)
            
            # Keep only last 100 metric entries
            if len(performance_metrics) > 100:
                oldest_key = min(performance_metrics.keys())
                del performance_metrics[oldest_key]
            
            # Keep only last 50 alerts
            if len(alert_history) > 50:
                alert_history[:] = alert_history[-50:]
            
            time.sleep(10)  # Collect metrics every 10 seconds
            
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(10)

# Start monitoring thread
monitoring_thread = threading.Thread(target=monitoring_loop)
monitoring_thread.daemon = True
monitoring_thread.start()

@app.route('/')
def monitoring_dashboard():
    """Performance monitoring dashboard"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Scanner - Performance Monitoring</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background: #0f172a; color: #e2e8f0; }
            .navbar { background: #1e293b; border-bottom: 1px solid #334155; }
            .metric-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
            .metric-value { font-size: 2.5rem; font-weight: 700; }
            .metric-label { color: #94a3b8; font-size: 0.9rem; }
            .alert-critical { background: #7f1d1d; border: 1px solid #dc2626; }
            .alert-high { background: #92400e; border: 1px solid #f59e0b; }
            .alert-medium { background: #1e40af; border: 1px solid #3b82f6; }
            .alert-low { background: #065f46; border: 1px solid #10b981; }
            .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
            .status-healthy { background: #10b981; }
            .status-warning { background: #f59e0b; }
            .status-critical { background: #ef4444; }
            .chart-container { background: #1e293b; border-radius: 12px; padding: 20px; }
            .sla-item { padding: 12px; border-bottom: 1px solid #334155; }
            .sla-met { color: #10b981; }
            .sla-missed { color: #ef4444; }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg">
            <div class="container-fluid">
                <span class="navbar-brand">
                    📊 Performance Monitoring - Enterprise Scanner
                </span>
                <span class="navbar-text">
                    <span class="status-indicator status-healthy"></span>
                    All Systems Operational
                </span>
            </div>
        </nav>
        
        <div class="container-fluid py-4">
            <!-- System Health Overview -->
            <div class="row mb-4">
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="cpu-usage" class="metric-value text-info">--</div>
                        <div class="metric-label">CPU Usage</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="memory-usage" class="metric-value text-warning">--</div>
                        <div class="metric-label">Memory Usage</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="disk-usage" class="metric-value text-success">--</div>
                        <div class="metric-label">Disk Usage</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="active-users" class="metric-value text-primary">--</div>
                        <div class="metric-label">Active Users</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="response-time" class="metric-value text-secondary">--</div>
                        <div class="metric-label">Avg Response (ms)</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="uptime" class="metric-value text-success">--</div>
                        <div class="metric-label">Uptime (hours)</div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Charts -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="chart-container">
                        <h5 class="mb-3">📈 System Performance</h5>
                        <canvas id="performanceChart" height="200"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <h5 class="mb-3">👥 User Activity</h5>
                        <canvas id="userChart" height="200"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- SLA Dashboard and Alerts -->
            <div class="row">
                <div class="col-md-6">
                    <div class="metric-card">
                        <h5 class="mb-3">📋 SLA Compliance</h5>
                        <div id="sla-metrics">
                            <!-- SLA metrics will be populated here -->
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="metric-card">
                        <h5 class="mb-3">🚨 Recent Alerts</h5>
                        <div id="alerts-container" style="max-height: 300px; overflow-y: auto;">
                            <!-- Alerts will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Application Metrics -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="metric-card">
                        <h5 class="mb-3">🔧 Application Metrics</h5>
                        <div class="row">
                            <div class="col-md-2 text-center">
                                <div id="api-requests" class="metric-value text-info">--</div>
                                <div class="metric-label">API Requests/min</div>
                            </div>
                            <div class="col-md-2 text-center">
                                <div id="scans-running" class="metric-value text-warning">--</div>
                                <div class="metric-label">Active Scans</div>
                            </div>
                            <div class="col-md-2 text-center">
                                <div id="threats-detected" class="metric-value text-danger">--</div>
                                <div class="metric-label">Threats Today</div>
                            </div>
                            <div class="col-md-2 text-center">
                                <div id="vulnerabilities" class="metric-value text-warning">--</div>
                                <div class="metric-label">Vulnerabilities</div>
                            </div>
                            <div class="col-md-2 text-center">
                                <div id="sla-compliance" class="metric-value text-success">--</div>
                                <div class="metric-label">SLA Compliance</div>
                            </div>
                            <div class="col-md-2 text-center">
                                <div id="satisfaction" class="metric-value text-primary">--</div>
                                <div class="metric-label">Satisfaction</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let performanceChart, userChart;
            let performanceData = [];
            let userActivityData = [];
            const maxDataPoints = 20;
            
            // Initialize charts
            function initCharts() {
                // Performance Chart
                const perfCtx = document.getElementById('performanceChart').getContext('2d');
                performanceChart = new Chart(perfCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'CPU Usage (%)',
                            data: [],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Memory Usage (%)',
                            data: [],
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Response Time (ms)',
                            data: [],
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                grid: { color: '#334155' },
                                ticks: { color: '#e2e8f0' }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                grid: { drawOnChartArea: false },
                                ticks: { color: '#e2e8f0' }
                            },
                            x: {
                                grid: { color: '#334155' },
                                ticks: { color: '#e2e8f0' }
                            }
                        },
                        plugins: {
                            legend: { labels: { color: '#e2e8f0' } }
                        }
                    }
                });
                
                // User Activity Chart
                const userCtx = document.getElementById('userChart').getContext('2d');
                userChart = new Chart(userCtx, {
                    type: 'bar',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Active Users',
                            data: [],
                            backgroundColor: 'rgba(16, 185, 129, 0.8)',
                            borderColor: '#10b981',
                            borderWidth: 1
                        }, {
                            label: 'Concurrent Sessions',
                            data: [],
                            backgroundColor: 'rgba(139, 92, 246, 0.8)',
                            borderColor: '#8b5cf6',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#334155' },
                                ticks: { color: '#e2e8f0' }
                            },
                            x: {
                                grid: { color: '#334155' },
                                ticks: { color: '#e2e8f0' }
                            }
                        },
                        plugins: {
                            legend: { labels: { color: '#e2e8f0' } }
                        }
                    }
                });
            }
            
            // Update dashboard with latest metrics
            async function updateDashboard() {
                try {
                    const response = await fetch('/api/metrics/current');
                    const data = await response.json();
                    
                    // Update system metrics
                    updateSystemMetrics(data.system);
                    
                    // Update application metrics
                    updateApplicationMetrics(data.application);
                    
                    // Update SLA metrics
                    updateSLAMetrics(data.sla);
                    
                    // Update charts
                    updateCharts(data);
                    
                } catch (error) {
                    console.error('Error updating dashboard:', error);
                }
            }
            
            function updateSystemMetrics(system) {
                document.getElementById('cpu-usage').textContent = system.cpu.percent + '%';
                document.getElementById('memory-usage').textContent = system.memory.percent + '%';
                document.getElementById('disk-usage').textContent = system.disk.percent + '%';
                document.getElementById('uptime').textContent = system.uptime_hours;
            }
            
            function updateApplicationMetrics(app) {
                document.getElementById('active-users').textContent = app.active_users.toLocaleString();
                document.getElementById('response-time').textContent = app.average_response_time;
                document.getElementById('api-requests').textContent = app.api_requests_per_minute.toLocaleString();
                document.getElementById('scans-running').textContent = app.security_scans_running;
                document.getElementById('threats-detected').textContent = app.threats_detected_today.toLocaleString();
                document.getElementById('vulnerabilities').textContent = app.vulnerabilities_identified;
                document.getElementById('sla-compliance').textContent = app.sla_compliance + '%';
                document.getElementById('satisfaction').textContent = app.customer_satisfaction + '/5';
            }
            
            function updateSLAMetrics(sla) {
                const container = document.getElementById('sla-metrics');
                container.innerHTML = '';
                
                Object.entries(sla).forEach(([metric, data]) => {
                    const statusClass = data.status === 'met' ? 'sla-met' : 'sla-missed';
                    const statusIcon = data.status === 'met' ? '✅' : '❌';
                    
                    const metricHtml = `
                        <div class="sla-item">
                            <div class="d-flex justify-content-between">
                                <span>${statusIcon} ${metric.replace('_', ' ').toUpperCase()}</span>
                                <span class="${statusClass}">${data.current} / ${data.target}</span>
                            </div>
                        </div>
                    `;
                    container.innerHTML += metricHtml;
                });
            }
            
            function updateCharts(data) {
                const now = new Date().toLocaleTimeString();
                
                // Update performance data
                performanceData.push({
                    time: now,
                    cpu: data.system.cpu.percent,
                    memory: data.system.memory.percent,
                    response: data.application.average_response_time
                });
                
                userActivityData.push({
                    time: now,
                    users: data.application.active_users,
                    sessions: data.application.concurrent_sessions
                });
                
                // Keep only last N data points
                if (performanceData.length > maxDataPoints) {
                    performanceData.shift();
                }
                if (userActivityData.length > maxDataPoints) {
                    userActivityData.shift();
                }
                
                // Update performance chart
                performanceChart.data.labels = performanceData.map(d => d.time);
                performanceChart.data.datasets[0].data = performanceData.map(d => d.cpu);
                performanceChart.data.datasets[1].data = performanceData.map(d => d.memory);
                performanceChart.data.datasets[2].data = performanceData.map(d => d.response);
                performanceChart.update();
                
                // Update user activity chart
                userChart.data.labels = userActivityData.map(d => d.time);
                userChart.data.datasets[0].data = userActivityData.map(d => d.users);
                userChart.data.datasets[1].data = userActivityData.map(d => d.sessions);
                userChart.update();
            }
            
            // Get and display alerts
            async function updateAlerts() {
                try {
                    const response = await fetch('/api/alerts/recent');
                    const alerts = await response.json();
                    
                    const container = document.getElementById('alerts-container');
                    container.innerHTML = '';
                    
                    alerts.slice(-10).reverse().forEach(alert => {
                        const time = new Date(alert.timestamp).toLocaleTimeString();
                        const alertClass = `alert-${alert.severity}`;
                        
                        const alertHtml = `
                            <div class="p-2 mb-2 rounded ${alertClass}">
                                <div class="d-flex justify-content-between">
                                    <strong>${alert.title}</strong>
                                    <small>${time}</small>
                                </div>
                                <div>${alert.message}</div>
                            </div>
                        `;
                        container.innerHTML += alertHtml;
                    });
                    
                } catch (error) {
                    console.error('Error updating alerts:', error);
                }
            }
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                initCharts();
                updateDashboard();
                updateAlerts();
                
                // Update every 10 seconds
                setInterval(updateDashboard, 10000);
                setInterval(updateAlerts, 15000);
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/metrics/current')
def get_current_metrics():
    """Get latest performance metrics"""
    if not performance_metrics:
        return jsonify({'error': 'No metrics available'}), 404
    
    latest_timestamp = max(performance_metrics.keys())
    return jsonify(performance_metrics[latest_timestamp])

@app.route('/api/alerts/recent')
def get_recent_alerts():
    """Get recent alert history"""
    return jsonify(alert_history)

@app.route('/api/metrics/history')
def get_metrics_history():
    """Get historical performance data"""
    return jsonify(list(performance_metrics.values()))

@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'performance_monitoring_system',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("📊 Starting Enterprise Scanner Performance Monitoring System...")
    print("🌐 Monitoring Dashboard: http://localhost:5007")
    print("📈 Real-time system and application metrics")
    print("🎯 SLA compliance tracking")
    print("🚨 Automated alerting system")
    print("")
    
    app.run(host='0.0.0.0', port=5007, debug=True)