#!/usr/bin/env python3
"""
Enterprise Scanner - Advanced Analytics Dashboard
Real-time cybersecurity metrics and threat intelligence for Fortune 500 companies
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json
import uuid
import random
import time
import threading
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global data storage
dashboard_data = {
    'threats': [],
    'metrics': {},
    'clients': {},
    'alerts': []
}

# Data generation lock
data_lock = threading.Lock()

class ThreatIntelligence:
    """Real-time threat intelligence generator"""
    
    @staticmethod
    def generate_threats():
        """Generate realistic cybersecurity threats"""
        threat_types = [
            'Malware Detection', 'Phishing Attempt', 'DDoS Attack', 'Data Breach Attempt',
            'Ransomware Activity', 'SQL Injection', 'Cross-Site Scripting', 'Zero-Day Exploit',
            'Insider Threat', 'Advanced Persistent Threat', 'Credential Stuffing', 'Man-in-the-Middle'
        ]
        
        severity_levels = ['Low', 'Medium', 'High', 'Critical']
        industries = ['Financial', 'Healthcare', 'Technology', 'Manufacturing', 'Government']
        
        threat = {
            'id': str(uuid.uuid4()),
            'type': random.choice(threat_types),
            'severity': random.choice(severity_levels),
            'industry': random.choice(industries),
            'timestamp': datetime.now().isoformat(),
            'source_ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'target_port': random.choice([80, 443, 22, 3389, 21, 25, 53, 445]),
            'affected_systems': random.randint(1, 50),
            'mitigation_status': random.choice(['Detected', 'Blocked', 'Investigating', 'Resolved']),
            'risk_score': random.randint(1, 100)
        }
        
        return threat

class SecurityMetrics:
    """Generate real-time security metrics"""
    
    @staticmethod
    def generate_metrics():
        """Generate comprehensive security metrics"""
        return {
            'security_score': random.randint(75, 95),
            'threats_blocked': random.randint(100, 500),
            'vulnerabilities_found': random.randint(5, 25),
            'compliance_score': random.randint(85, 98),
            'incidents_resolved': random.randint(10, 40),
            'mean_time_to_response': random.randint(15, 120),  # minutes
            'uptime_percentage': round(random.uniform(99.0, 99.99), 2),
            'data_protected_gb': random.randint(500, 5000),
            'active_monitoring_endpoints': random.randint(1000, 10000),
            'patch_compliance': random.randint(90, 99)
        }

def update_dashboard_data():
    """Background thread to continuously update dashboard data"""
    while True:
        with data_lock:
            # Add new threat
            new_threat = ThreatIntelligence.generate_threats()
            dashboard_data['threats'].append(new_threat)
            
            # Keep only last 50 threats
            if len(dashboard_data['threats']) > 50:
                dashboard_data['threats'] = dashboard_data['threats'][-50:]
            
            # Update metrics
            dashboard_data['metrics'] = SecurityMetrics.generate_metrics()
            
            # Generate alerts for high-severity threats
            if new_threat['severity'] in ['High', 'Critical']:
                alert = {
                    'id': str(uuid.uuid4()),
                    'message': f"{new_threat['severity']} {new_threat['type']} detected in {new_threat['industry']} sector",
                    'timestamp': new_threat['timestamp'],
                    'type': 'threat',
                    'severity': new_threat['severity']
                }
                dashboard_data['alerts'].append(alert)
                
                # Keep only last 20 alerts
                if len(dashboard_data['alerts']) > 20:
                    dashboard_data['alerts'] = dashboard_data['alerts'][-20:]
        
        time.sleep(3)  # Update every 3 seconds

# Start background data generation
data_thread = threading.Thread(target=update_dashboard_data)
data_thread.daemon = True
data_thread.start()

@app.route('/')
def dashboard():
    """Main analytics dashboard"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Scanner - Advanced Analytics Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background: #0f172a; color: #e2e8f0; }
            .navbar { background: #1e293b; border-bottom: 1px solid #334155; }
            .metric-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
            .metric-value { font-size: 2.5rem; font-weight: 700; }
            .metric-label { color: #94a3b8; font-size: 0.9rem; }
            .live-indicator { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; animation: pulse 2s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
            .threat-item { background: #1e293b; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 10px; border-radius: 0 8px 8px 0; }
            .threat-critical { border-left-color: #ef4444; }
            .threat-high { border-left-color: #f59e0b; }
            .threat-medium { border-left-color: #eab308; }
            .threat-low { border-left-color: #10b981; }
            .alert-item { background: #7f1d1d; border: 1px solid #dc2626; border-radius: 8px; padding: 12px; margin-bottom: 8px; }
            .chart-container { background: #1e293b; border-radius: 12px; padding: 20px; }
            .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 500; }
            .status-resolved { background: #065f46; color: #10b981; }
            .status-blocked { background: #1e40af; color: #3b82f6; }
            .status-investigating { background: #92400e; color: #f59e0b; }
            .status-detected { background: #7c2d12; color: #f97316; }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg">
            <div class="container-fluid">
                <span class="navbar-brand">
                    🛡️ Enterprise Scanner Analytics
                    <span class="live-indicator">LIVE</span>
                </span>
                <div class="d-flex">
                    <span class="navbar-text me-3">
                        <small>Last Updated: <span id="last-update"></span></small>
                    </span>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid py-4">
            <!-- Real-time Metrics Row -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div id="security-score" class="metric-value text-success">--</div>
                        <div class="metric-label">Security Score</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div id="threats-blocked" class="metric-value text-warning">--</div>
                        <div class="metric-label">Threats Blocked Today</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div id="vulnerabilities" class="metric-value text-danger">--</div>
                        <div class="metric-label">Active Vulnerabilities</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card text-center">
                        <div id="compliance-score" class="metric-value text-info">--</div>
                        <div class="metric-label">Compliance Score</div>
                    </div>
                </div>
            </div>
            
            <!-- Secondary Metrics Row -->
            <div class="row mb-4">
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="incidents-resolved" class="metric-value text-primary">--</div>
                        <div class="metric-label">Incidents Resolved</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="response-time" class="metric-value text-secondary">--</div>
                        <div class="metric-label">Avg Response (min)</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="uptime" class="metric-value text-success">--</div>
                        <div class="metric-label">System Uptime</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="data-protected" class="metric-value text-info">--</div>
                        <div class="metric-label">Data Protected (GB)</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="endpoints" class="metric-value text-warning">--</div>
                        <div class="metric-label">Monitored Endpoints</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="metric-card text-center">
                        <div id="patch-compliance" class="metric-value text-success">--</div>
                        <div class="metric-label">Patch Compliance</div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <!-- Threat Intelligence Feed -->
                <div class="col-md-4">
                    <div class="metric-card">
                        <h5 class="mb-3">🚨 Live Threat Intelligence</h5>
                        <div id="threat-feed" style="max-height: 400px; overflow-y: auto;">
                            <!-- Threats will be populated here -->
                        </div>
                    </div>
                </div>
                
                <!-- Security Alerts -->
                <div class="col-md-4">
                    <div class="metric-card">
                        <h5 class="mb-3">⚠️ Security Alerts</h5>
                        <div id="alerts-feed" style="max-height: 400px; overflow-y: auto;">
                            <!-- Alerts will be populated here -->
                        </div>
                    </div>
                </div>
                
                <!-- Threat Distribution Chart -->
                <div class="col-md-4">
                    <div class="chart-container">
                        <h5 class="mb-3">📊 Threat Distribution</h5>
                        <canvas id="threat-chart" width="300" height="200"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Real-time Activity Chart -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="chart-container">
                        <h5 class="mb-3">📈 Real-time Security Activity</h5>
                        <canvas id="activity-chart" width="800" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let threatChart, activityChart;
            let activityData = [];
            let maxDataPoints = 20;
            
            // Initialize charts
            function initCharts() {
                // Threat Distribution Pie Chart
                const threatCtx = document.getElementById('threat-chart').getContext('2d');
                threatChart = new Chart(threatCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Malware', 'Phishing', 'DDoS', 'Data Breach', 'Others'],
                        datasets: [{
                            data: [0, 0, 0, 0, 0],
                            backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { labels: { color: '#e2e8f0' } }
                        }
                    }
                });
                
                // Activity Line Chart
                const activityCtx = document.getElementById('activity-chart').getContext('2d');
                activityChart = new Chart(activityCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Threats per Minute',
                            data: [],
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Security Score',
                            data: [],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4
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
            
            // Update dashboard data
            async function updateDashboard() {
                try {
                    const response = await fetch('/api/dashboard/data');
                    const data = await response.json();
                    
                    // Update metrics
                    updateMetrics(data.metrics);
                    
                    // Update threat feed
                    updateThreatFeed(data.threats);
                    
                    // Update alerts
                    updateAlerts(data.alerts);
                    
                    // Update charts
                    updateCharts(data);
                    
                    // Update last update time
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                    
                } catch (error) {
                    console.error('Error updating dashboard:', error);
                }
            }
            
            function updateMetrics(metrics) {
                document.getElementById('security-score').textContent = metrics.security_score || '--';
                document.getElementById('threats-blocked').textContent = (metrics.threats_blocked || 0).toLocaleString();
                document.getElementById('vulnerabilities').textContent = metrics.vulnerabilities_found || '--';
                document.getElementById('compliance-score').textContent = metrics.compliance_score + '%' || '--';
                document.getElementById('incidents-resolved').textContent = metrics.incidents_resolved || '--';
                document.getElementById('response-time').textContent = metrics.mean_time_to_response || '--';
                document.getElementById('uptime').textContent = metrics.uptime_percentage + '%' || '--';
                document.getElementById('data-protected').textContent = (metrics.data_protected_gb || 0).toLocaleString();
                document.getElementById('endpoints').textContent = (metrics.active_monitoring_endpoints || 0).toLocaleString();
                document.getElementById('patch-compliance').textContent = metrics.patch_compliance + '%' || '--';
            }
            
            function updateThreatFeed(threats) {
                const feed = document.getElementById('threat-feed');
                feed.innerHTML = '';
                
                threats.slice(-10).reverse().forEach(threat => {
                    const item = document.createElement('div');
                    item.className = `threat-item threat-${threat.severity.toLowerCase()}`;
                    item.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${threat.type}</strong>
                                <br><small>${threat.industry} • ${threat.source_ip}</small>
                            </div>
                            <div class="text-end">
                                <span class="status-badge status-${threat.mitigation_status.toLowerCase()}">${threat.mitigation_status}</span>
                                <br><small>${new Date(threat.timestamp).toLocaleTimeString()}</small>
                            </div>
                        </div>
                    `;
                    feed.appendChild(item);
                });
            }
            
            function updateAlerts(alerts) {
                const feed = document.getElementById('alerts-feed');
                feed.innerHTML = '';
                
                alerts.slice(-8).reverse().forEach(alert => {
                    const item = document.createElement('div');
                    item.className = 'alert-item';
                    item.innerHTML = `
                        <div class="d-flex justify-content-between">
                            <span>${alert.message}</span>
                            <small>${new Date(alert.timestamp).toLocaleTimeString()}</small>
                        </div>
                    `;
                    feed.appendChild(item);
                });
            }
            
            function updateCharts(data) {
                // Update threat distribution
                const threatTypes = {};
                data.threats.forEach(threat => {
                    const type = threat.type.split(' ')[0]; // Get first word
                    threatTypes[type] = (threatTypes[type] || 0) + 1;
                });
                
                threatChart.data.datasets[0].data = [
                    threatTypes['Malware'] || 0,
                    threatTypes['Phishing'] || 0,
                    threatTypes['DDoS'] || 0,
                    threatTypes['Data'] || 0,
                    Object.values(threatTypes).reduce((a, b) => a + b, 0) - (threatTypes['Malware'] || 0) - (threatTypes['Phishing'] || 0) - (threatTypes['DDoS'] || 0) - (threatTypes['Data'] || 0)
                ];
                threatChart.update();
                
                // Update activity chart
                const now = new Date().toLocaleTimeString();
                activityData.push({
                    time: now,
                    threats: data.threats.length,
                    score: data.metrics.security_score
                });
                
                if (activityData.length > maxDataPoints) {
                    activityData.shift();
                }
                
                activityChart.data.labels = activityData.map(d => d.time);
                activityChart.data.datasets[0].data = activityData.map(d => d.threats);
                activityChart.data.datasets[1].data = activityData.map(d => d.score);
                activityChart.update();
            }
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                initCharts();
                updateDashboard();
                
                // Update every 3 seconds
                setInterval(updateDashboard, 3000);
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/dashboard/data')
def get_dashboard_data():
    """Get current dashboard data"""
    with data_lock:
        return jsonify(dashboard_data)

@app.route('/api/threats')
def get_threats():
    """Get recent threats"""
    with data_lock:
        return jsonify({
            'threats': dashboard_data['threats'][-20:],  # Last 20 threats
            'total_count': len(dashboard_data['threats'])
        })

@app.route('/api/metrics')
def get_metrics():
    """Get current security metrics"""
    with data_lock:
        return jsonify(dashboard_data['metrics'])

@app.route('/api/alerts')
def get_alerts():
    """Get recent security alerts"""
    with data_lock:
        return jsonify({
            'alerts': dashboard_data['alerts'][-10:],  # Last 10 alerts
            'total_count': len(dashboard_data['alerts'])
        })

@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'advanced_analytics_dashboard',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("📊 Starting Enterprise Scanner Advanced Analytics Dashboard...")
    print("🌐 Dashboard URL: http://localhost:5003")
    print("📈 Real-time threat intelligence and security metrics")
    print("🔄 Auto-refreshing every 3 seconds")
    print("")
    
    app.run(host='0.0.0.0', port=5003, debug=True)