#!/usr/bin/env python3
"""
Simple Security Assessment Dashboard
Fortune 500 Security Evaluation
"""

from flask import Flask, render_template_string, jsonify, request
import datetime
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_assessment_data():
    """Generate security assessment data"""
    return {
        'timestamp': datetime.datetime.now().isoformat(),
        'overall_score': random.randint(65, 85),
        'network_security': random.randint(70, 90),
        'data_protection': random.randint(60, 85),
        'access_control': random.randint(75, 95),
        'compliance': random.randint(80, 98),
        'incident_response': random.randint(55, 80),
        'total_assessed': random.randint(45000, 55000),
        'vulnerabilities_found': random.randint(450, 650),
        'critical_risks': random.randint(5, 15)
    }

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Scanner - Security Assessment</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: white; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #ef4444; font-size: 2.5em; margin-bottom: 10px; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metric-card { background: #1e293b; padding: 25px; border-radius: 15px; border-left: 4px solid #ef4444; }
            .metric-title { font-size: 1.1em; margin-bottom: 10px; color: #94a3b8; }
            .metric-value { font-size: 2.5em; font-weight: bold; color: #ef4444; }
            .good { color: #10b981; }
            .warning { color: #fbbf24; }
            .critical { color: #ef4444; }
            .progress-bar { background: #374151; height: 10px; border-radius: 5px; margin-top: 10px; }
            .progress-fill { height: 100%; border-radius: 5px; transition: width 0.3s; }
            .updated { text-align: center; margin-top: 20px; color: #64748b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Security Assessment Dashboard</h1>
                <p>Real-time Fortune 500 Security Evaluation</p>
            </div>
            <div class="metrics" id="metrics">
                <!-- Metrics will be loaded here -->
            </div>
            <div class="updated" id="updated"></div>
        </div>
        
        <script>
            function updateMetrics() {
                fetch('/api/assessment-data')
                    .then(response => response.json())
                    .then(data => {
                        const metricsHtml = `
                            <div class="metric-card">
                                <div class="metric-title">Overall Security Score</div>
                                <div class="metric-value ${data.overall_score > 80 ? 'good' : 'warning'}">${data.overall_score}/100</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${data.overall_score}%; background: ${data.overall_score > 80 ? '#10b981' : '#fbbf24'};"></div>
                                </div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Network Security</div>
                                <div class="metric-value ${data.network_security > 80 ? 'good' : 'warning'}">${data.network_security}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${data.network_security}%; background: ${data.network_security > 80 ? '#10b981' : '#fbbf24'};"></div>
                                </div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Data Protection</div>
                                <div class="metric-value ${data.data_protection > 75 ? 'good' : 'warning'}">${data.data_protection}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${data.data_protection}%; background: ${data.data_protection > 75 ? '#10b981' : '#fbbf24'};"></div>
                                </div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Access Control</div>
                                <div class="metric-value ${data.access_control > 85 ? 'good' : 'warning'}">${data.access_control}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${data.access_control}%; background: ${data.access_control > 85 ? '#10b981' : '#fbbf24'};"></div>
                                </div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Compliance Status</div>
                                <div class="metric-value good">${data.compliance}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${data.compliance}%; background: #10b981;"></div>
                                </div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Critical Risks Found</div>
                                <div class="metric-value ${data.critical_risks > 10 ? 'critical' : 'warning'}">${data.critical_risks}</div>
                                <div style="margin-top: 10px; color: #94a3b8;">
                                    Immediate attention required
                                </div>
                            </div>
                        `;
                        document.getElementById('metrics').innerHTML = metricsHtml;
                        document.getElementById('updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
                    });
            }
            
            updateMetrics();
            setInterval(updateMetrics, 8000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/assessment-data')
def api_assessment_data():
    return jsonify(get_assessment_data())

@app.route('/api/assessment-status')
def api_assessment_status():
    return jsonify({'status': 'operational', 'timestamp': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Security Assessment Dashboard...")
    print("URL: http://localhost:5003")
    app.run(host='127.0.0.1', port=5003, debug=False)