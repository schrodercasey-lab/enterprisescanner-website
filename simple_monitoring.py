#!/usr/bin/env python3
"""
Simple Live Monitoring Dashboard
Real-Time Enterprise Scanner Metrics
"""

from flask import Flask, render_template_string, jsonify
import datetime
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_monitoring_metrics():
    """Generate monitoring metrics"""
    return {
        'timestamp': datetime.datetime.now().isoformat(),
        'security_score': random.randint(85, 98),
        'threats_detected': random.randint(5, 25),
        'systems_monitored': 147,
        'uptime': '99.9%',
        'response_time': f"{random.randint(50, 200)}ms"
    }

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Scanner - Live Monitoring</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; background: #1a1a2e; color: white; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #4ade80; font-size: 2.5em; margin-bottom: 10px; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .metric-card { background: #16213e; padding: 20px; border-radius: 10px; border-left: 4px solid #4ade80; }
            .metric-title { font-size: 1.1em; margin-bottom: 10px; color: #94a3b8; }
            .metric-value { font-size: 2.5em; font-weight: bold; color: #4ade80; }
            .status { background: #22c55e; color: white; padding: 5px 15px; border-radius: 15px; display: inline-block; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Enterprise Scanner Live Monitoring</h1>
                <p>Real-Time Security Intelligence Dashboard</p>
            </div>
            <div class="metrics" id="metrics">
                <!-- Metrics will be loaded here -->
            </div>
        </div>
        
        <script>
            function updateMetrics() {
                fetch('/api/metrics')
                    .then(response => response.json())
                    .then(data => {
                        const metricsHtml = `
                            <div class="metric-card">
                                <div class="metric-title">Security Score</div>
                                <div class="metric-value">${data.security_score}%</div>
                                <div class="status">Excellent</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Threats Detected</div>
                                <div class="metric-value">${data.threats_detected}</div>
                                <div class="status">Active</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Systems Monitored</div>
                                <div class="metric-value">${data.systems_monitored}</div>
                                <div class="status">Online</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">System Uptime</div>
                                <div class="metric-value">${data.uptime}</div>
                                <div class="status">Stable</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Response Time</div>
                                <div class="metric-value">${data.response_time}</div>
                                <div class="status">Fast</div>
                            </div>
                        `;
                        document.getElementById('metrics').innerHTML = metricsHtml;
                    });
            }
            
            updateMetrics();
            setInterval(updateMetrics, 5000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/metrics')
def api_metrics():
    return jsonify(get_monitoring_metrics())

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'operational', 'timestamp': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Live Monitoring Dashboard...")
    print("URL: http://localhost:5001")
    app.run(host='127.0.0.1', port=5001, debug=False)