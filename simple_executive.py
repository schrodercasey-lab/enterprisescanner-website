#!/usr/bin/env python3
"""
Simple Executive Dashboard
C-Suite Business Intelligence
"""

from flask import Flask, render_template_string, jsonify
import datetime
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_executive_metrics():
    """Generate executive metrics"""
    return {
        'timestamp': datetime.datetime.now().isoformat(),
        'revenue_pipeline': f"${random.randint(110, 130)}M",
        'security_posture': random.randint(90, 98),
        'customer_satisfaction': random.randint(85, 95),
        'risk_score': random.randint(5, 15),
        'compliance_status': random.randint(92, 99),
        'roi_percentage': random.randint(250, 400)
    }

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Scanner - Executive Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: white; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #fbbf24; font-size: 2.5em; margin-bottom: 10px; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
            .metric-card { background: #1e293b; padding: 25px; border-radius: 15px; border-left: 4px solid #fbbf24; }
            .metric-title { font-size: 1.1em; margin-bottom: 10px; color: #94a3b8; }
            .metric-value { font-size: 2.5em; font-weight: bold; color: #fbbf24; }
            .status { background: #059669; color: white; padding: 5px 15px; border-radius: 15px; display: inline-block; margin-top: 10px; }
            .updated { text-align: center; margin-top: 20px; color: #64748b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Executive Intelligence Dashboard</h1>
                <p>Fortune 500 C-Suite Business Intelligence</p>
            </div>
            <div class="metrics" id="metrics">
                <!-- Metrics will be loaded here -->
            </div>
            <div class="updated" id="updated"></div>
        </div>
        
        <script>
            function updateMetrics() {
                fetch('/api/executive-metrics')
                    .then(response => response.json())
                    .then(data => {
                        const metricsHtml = `
                            <div class="metric-card">
                                <div class="metric-title">Revenue Pipeline</div>
                                <div class="metric-value">${data.revenue_pipeline}</div>
                                <div class="status">Strong Growth</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Security Posture</div>
                                <div class="metric-value">${data.security_posture}%</div>
                                <div class="status">Excellent</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Customer Satisfaction</div>
                                <div class="metric-value">${data.customer_satisfaction}%</div>
                                <div class="status">High</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Business Risk</div>
                                <div class="metric-value">${data.risk_score}/100</div>
                                <div class="status">Low Risk</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Compliance Status</div>
                                <div class="metric-value">${data.compliance_status}%</div>
                                <div class="status">Compliant</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Security ROI</div>
                                <div class="metric-value">${data.roi_percentage}%</div>
                                <div class="status">Excellent Return</div>
                            </div>
                        `;
                        document.getElementById('metrics').innerHTML = metricsHtml;
                        document.getElementById('updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
                    });
            }
            
            updateMetrics();
            setInterval(updateMetrics, 10000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/executive-metrics')
def api_executive_metrics():
    return jsonify(get_executive_metrics())

@app.route('/api/executive-status')
def api_executive_status():
    return jsonify({'status': 'operational', 'timestamp': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Executive Dashboard...")
    print("URL: http://localhost:5002")
    app.run(host='127.0.0.1', port=5002, debug=False)