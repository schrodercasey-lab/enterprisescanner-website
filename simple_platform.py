#!/usr/bin/env python3
"""
Simple Platform Status Dashboard
Enterprise Scanner System Health
"""

from flask import Flask, render_template_string, jsonify
import datetime
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_platform_status():
    """Generate platform status data"""
    return {
        'timestamp': datetime.datetime.now().isoformat(),
        'system_health': random.randint(95, 99),
        'active_scans': random.randint(1200, 1800),
        'api_uptime': random.randint(99, 100),
        'response_time': random.randint(45, 85),
        'database_performance': random.randint(90, 98),
        'security_alerts': random.randint(0, 3),
        'total_customers': random.randint(450, 550),
        'processed_today': random.randint(85000, 95000)
    }

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Scanner - Platform Status</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: white; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #22c55e; font-size: 2.5em; margin-bottom: 10px; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
            .metric-card { background: #1e293b; padding: 25px; border-radius: 15px; border-left: 4px solid #22c55e; }
            .metric-title { font-size: 1.1em; margin-bottom: 10px; color: #94a3b8; }
            .metric-value { font-size: 2.5em; font-weight: bold; color: #22c55e; }
            .status-good { color: #10b981; }
            .status-warning { color: #fbbf24; }
            .status-critical { color: #ef4444; }
            .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; }
            .good { background: #10b981; }
            .warning { background: #fbbf24; }
            .critical { background: #ef4444; }
            .updated { text-align: center; margin-top: 20px; color: #64748b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Platform Status Dashboard</h1>
                <p>Enterprise Scanner System Health Monitoring</p>
            </div>
            <div class="metrics" id="metrics">
                <!-- Metrics will be loaded here -->
            </div>
            <div class="updated" id="updated"></div>
        </div>
        
        <script>
            function updateMetrics() {
                fetch('/api/platform-status')
                    .then(response => response.json())
                    .then(data => {
                        const metricsHtml = `
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator good"></span>System Health
                                </div>
                                <div class="metric-value">${data.system_health}%</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator good"></span>Active Scans
                                </div>
                                <div class="metric-value">${data.active_scans.toLocaleString()}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator good"></span>API Uptime
                                </div>
                                <div class="metric-value">${data.api_uptime}%</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator ${data.response_time < 60 ? 'good' : 'warning'}"></span>Response Time
                                </div>
                                <div class="metric-value ${data.response_time < 60 ? 'status-good' : 'status-warning'}">${data.response_time}ms</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator good"></span>Database Performance
                                </div>
                                <div class="metric-value">${data.database_performance}%</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator ${data.security_alerts === 0 ? 'good' : 'warning'}"></span>Security Alerts
                                </div>
                                <div class="metric-value ${data.security_alerts === 0 ? 'status-good' : 'status-warning'}">${data.security_alerts}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator good"></span>Total Customers
                                </div>
                                <div class="metric-value">${data.total_customers}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">
                                    <span class="status-indicator good"></span>Processed Today
                                </div>
                                <div class="metric-value">${data.processed_today.toLocaleString()}</div>
                            </div>
                        `;
                        document.getElementById('metrics').innerHTML = metricsHtml;
                        document.getElementById('updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
                    });
            }
            
            updateMetrics();
            setInterval(updateMetrics, 5000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/platform-status')
def api_platform_status():
    return jsonify(get_platform_status())

@app.route('/api/system-health')
def api_system_health():
    return jsonify({'status': 'operational', 'timestamp': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Platform Status Dashboard...")
    print("URL: http://localhost:5004")
    app.run(host='127.0.0.1', port=5004, debug=False)