#!/usr/bin/env python3
"""
Enterprise Scanner Live Demo Platform
Interactive Fortune 500 Demonstration System
Real-Time Cybersecurity Assessment Platform
"""

import json
import os
import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'enterprise_scanner_demo_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

class EnterpriseDemoPlatform:
    """Live demonstration platform for Fortune 500 prospects"""
    
    def __init__(self):
        self.demo_sessions = {}
        self.vulnerability_database = self.create_demo_vulnerabilities()
        self.roi_calculator = self.create_roi_calculator()
        
    def create_demo_vulnerabilities(self):
        """Create realistic vulnerability data for demonstrations"""
        return {
            "critical": [
                {
                    "id": "CVE-2024-9841",
                    "title": "Remote Code Execution in Enterprise Web Gateway",
                    "severity": "Critical",
                    "cvss_score": 9.8,
                    "affected_systems": 47,
                    "business_impact": "$2.3M potential exposure",
                    "remediation": "Immediate patch deployment required",
                    "discovery_date": "2024-10-12"
                },
                {
                    "id": "CVE-2024-9832",
                    "title": "SQL Injection in Customer Database Interface",
                    "severity": "Critical", 
                    "cvss_score": 9.4,
                    "affected_systems": 23,
                    "business_impact": "$1.8M data breach risk",
                    "remediation": "Database access controls update",
                    "discovery_date": "2024-10-10"
                }
            ],
            "high": [
                {
                    "id": "CVE-2024-9823",
                    "title": "Privilege Escalation in Active Directory",
                    "severity": "High",
                    "cvss_score": 8.7,
                    "affected_systems": 156,
                    "business_impact": "$850K unauthorized access risk",
                    "remediation": "AD security policy enforcement",
                    "discovery_date": "2024-10-09"
                },
                {
                    "id": "CVE-2024-9814",
                    "title": "Cross-Site Scripting in Executive Portal",
                    "severity": "High",
                    "cvss_score": 8.2,
                    "affected_systems": 12,
                    "business_impact": "$650K executive data exposure",
                    "remediation": "Input validation implementation",
                    "discovery_date": "2024-10-08"
                }
            ],
            "medium": [
                {
                    "id": "CVE-2024-9805",
                    "title": "Information Disclosure in API Endpoints",
                    "severity": "Medium",
                    "cvss_score": 6.8,
                    "affected_systems": 89,
                    "business_impact": "$320K data leakage risk",
                    "remediation": "API security headers configuration",
                    "discovery_date": "2024-10-07"
                }
            ]
        }
    
    def create_roi_calculator(self):
        """Create interactive ROI calculator for demonstrations"""
        return {
            "fortune_500_averages": {
                "annual_security_budget": 45000000,
                "security_incidents_per_year": 156,
                "average_incident_cost": 280000,
                "compliance_audit_costs": 1200000,
                "security_team_size": 85,
                "average_salary": 145000
            },
            "enterprise_scanner_benefits": {
                "vulnerability_reduction": 0.73,
                "incident_response_improvement": 0.89,
                "compliance_efficiency": 0.67,
                "team_productivity_gain": 0.45,
                "security_tool_consolidation": 0.38
            }
        }

# Initialize demo platform
demo_platform = EnterpriseDemoPlatform()

@app.route('/')
def demo_homepage():
    """Main demo platform homepage"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Scanner - Live Demo Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .demo-card { box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: none; transition: transform 0.3s; }
            .demo-card:hover { transform: translateY(-5px); }
            .vulnerability-item { border-left: 4px solid #dc3545; padding: 15px; margin: 10px 0; background: #f8f9fa; }
            .vulnerability-critical { border-left-color: #dc3545; }
            .vulnerability-high { border-left-color: #fd7e14; }
            .vulnerability-medium { border-left-color: #ffc107; }
            .metrics-counter { font-size: 2.5rem; font-weight: bold; color: #667eea; }
            .live-indicator { width: 10px; height: 10px; background: #28a745; border-radius: 50%; display: inline-block; margin-right: 10px; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>
        <!-- Header -->
        <nav class="navbar navbar-expand-lg navbar-dark gradient-bg">
            <div class="container">
                <a class="navbar-brand fw-bold" href="#">
                    <i class="fas fa-shield-alt me-2"></i>Enterprise Scanner
                </a>
                <div class="navbar-nav ms-auto">
                    <span class="nav-link text-light">
                        <span class="live-indicator"></span>Live Demo Platform
                    </span>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <div class="gradient-bg text-white py-5">
            <div class="container text-center">
                <h1 class="display-4 fw-bold mb-4">Fortune 500 Cybersecurity Platform</h1>
                <p class="lead mb-4">Real-time vulnerability assessment and executive risk management</p>
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="bg-white bg-opacity-10 p-4 rounded">
                            <h5 class="mb-3">Live Demo Session</h5>
                            <button id="startDemo" class="btn btn-light btn-lg px-5">
                                <i class="fas fa-play me-2"></i>Start Executive Demo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Real-Time Dashboard -->
        <div class="container py-5">
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-center mb-4">
                        <span class="live-indicator"></span>Real-Time Security Dashboard
                    </h2>
                </div>
            </div>

            <!-- Key Metrics -->
            <div class="row mb-5">
                <div class="col-md-3">
                    <div class="demo-card card text-center p-4">
                        <div class="metrics-counter" id="criticalVulns">0</div>
                        <h6 class="text-muted">Critical Vulnerabilities</h6>
                        <small class="text-danger">Immediate Action Required</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="demo-card card text-center p-4">
                        <div class="metrics-counter text-warning" id="highVulns">0</div>
                        <h6 class="text-muted">High Risk Issues</h6>
                        <small class="text-warning">24-48 Hour Resolution</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="demo-card card text-center p-4">
                        <div class="metrics-counter text-success" id="securityScore">0</div>
                        <h6 class="text-muted">Security Score</h6>
                        <small class="text-success">Enterprise Grade</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="demo-card card text-center p-4">
                        <div class="metrics-counter text-info" id="complianceRate">0%</div>
                        <h6 class="text-muted">Compliance Rate</h6>
                        <small class="text-info">Regulatory Ready</small>
                    </div>
                </div>
            </div>

            <!-- Vulnerability Feed -->
            <div class="row">
                <div class="col-md-8">
                    <div class="demo-card card">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-exclamation-triangle me-2"></i>Live Vulnerability Feed
                            </h5>
                        </div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            <div id="vulnerabilityFeed">
                                <!-- Vulnerabilities will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="demo-card card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-calculator me-2"></i>ROI Calculator
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Annual Security Budget</label>
                                <input type="range" class="form-range" id="securityBudget" 
                                       min="10000000" max="100000000" value="45000000" step="1000000">
                                <small class="text-muted">$<span id="budgetDisplay">45M</span></small>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Company Size (Employees)</label>
                                <input type="range" class="form-range" id="companySize" 
                                       min="10000" max="500000" value="100000" step="10000">
                                <small class="text-muted"><span id="sizeDisplay">100K</span> employees</small>
                            </div>
                            <div class="bg-light p-3 rounded">
                                <h6>Projected Annual Savings</h6>
                                <div class="h4 text-success">$<span id="roiResult">0</span></div>
                                <small class="text-muted">ROI: <span id="roiPercentage">0</span>%</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Executive Summary -->
            <div class="row mt-5">
                <div class="col-12">
                    <div class="demo-card card">
                        <div class="card-header bg-dark text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-chart-line me-2"></i>Executive Risk Summary
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <canvas id="riskChart" width="400" height="200"></canvas>
                                </div>
                                <div class="col-md-6">
                                    <h6>Key Risk Indicators</h6>
                                    <ul class="list-unstyled">
                                        <li><i class="fas fa-shield-alt text-danger me-2"></i>Critical infrastructure exposure: <strong>High</strong></li>
                                        <li><i class="fas fa-database text-warning me-2"></i>Data protection compliance: <strong>Medium</strong></li>
                                        <li><i class="fas fa-users text-info me-2"></i>User access management: <strong>Optimized</strong></li>
                                        <li><i class="fas fa-network-wired text-success me-2"></i>Network security posture: <strong>Strong</strong></li>
                                    </ul>
                                    <div class="mt-3">
                                        <button class="btn btn-primary" id="generateReport">
                                            <i class="fas fa-file-pdf me-2"></i>Generate Executive Report
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Contact Section -->
        <div class="gradient-bg text-white py-5 mt-5">
            <div class="container text-center">
                <h3 class="mb-4">Ready to Transform Your Cybersecurity?</h3>
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <i class="fas fa-phone fa-2x mb-2"></i>
                                <p><strong>Emergency Support</strong><br>+1-800-SCANNER</p>
                            </div>
                            <div class="col-md-4 mb-3">
                                <i class="fas fa-envelope fa-2x mb-2"></i>
                                <p><strong>Sales Inquiries</strong><br>sales@enterprisescanner.com</p>
                            </div>
                            <div class="col-md-4 mb-3">
                                <i class="fas fa-calendar fa-2x mb-2"></i>
                                <p><strong>Executive Briefing</strong><br>Schedule Demo</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Socket.IO connection
            const socket = io();
            
            // Demo state
            let demoActive = false;
            let vulnerabilityCount = { critical: 0, high: 0, medium: 0 };
            
            // Start demo functionality
            document.getElementById('startDemo').addEventListener('click', function() {
                if (!demoActive) {
                    demoActive = true;
                    this.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Demo';
                    this.classList.remove('btn-light');
                    this.classList.add('btn-danger');
                    startLiveDemo();
                } else {
                    demoActive = false;
                    this.innerHTML = '<i class="fas fa-play me-2"></i>Start Executive Demo';
                    this.classList.remove('btn-danger');
                    this.classList.add('btn-light');
                }
            });
            
            // ROI Calculator
            document.getElementById('securityBudget').addEventListener('input', updateROI);
            document.getElementById('companySize').addEventListener('input', updateROI);
            
            function updateROI() {
                const budget = parseInt(document.getElementById('securityBudget').value);
                const size = parseInt(document.getElementById('companySize').value);
                
                // Update displays
                document.getElementById('budgetDisplay').textContent = (budget / 1000000).toFixed(0) + 'M';
                document.getElementById('sizeDisplay').textContent = (size / 1000).toFixed(0) + 'K';
                
                // Calculate ROI
                const savings = budget * 0.34; // 34% average savings
                const roi = (savings / 185000) * 100; // Based on $185K average license cost
                
                document.getElementById('roiResult').textContent = (savings / 1000000).toFixed(1) + 'M';
                document.getElementById('roiPercentage').textContent = roi.toFixed(0);
            }
            
            function startLiveDemo() {
                // Animate metrics
                animateCounter('criticalVulns', 0, 2, 2000);
                animateCounter('highVulns', 0, 4, 2500);
                animateCounter('securityScore', 0, 87, 3000);
                animateCounter('complianceRate', 0, 94, 3500, '%');
                
                // Start vulnerability feed
                setTimeout(() => {
                    addVulnerability('critical', 'CVE-2024-9841', 'Remote Code Execution in Enterprise Web Gateway', 9.8);
                }, 1000);
                
                setTimeout(() => {
                    addVulnerability('high', 'CVE-2024-9823', 'Privilege Escalation in Active Directory', 8.7);
                }, 3000);
                
                setTimeout(() => {
                    addVulnerability('critical', 'CVE-2024-9832', 'SQL Injection in Customer Database Interface', 9.4);
                }, 5000);
                
                // Initialize risk chart
                setTimeout(initRiskChart, 2000);
            }
            
            function animateCounter(elementId, start, end, duration, suffix = '') {
                const element = document.getElementById(elementId);
                const startTime = performance.now();
                
                function updateCounter(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const current = Math.floor(start + (end - start) * progress);
                    
                    element.textContent = current + suffix;
                    
                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    }
                }
                
                requestAnimationFrame(updateCounter);
            }
            
            function addVulnerability(severity, id, title, score) {
                const feed = document.getElementById('vulnerabilityFeed');
                const vulnElement = document.createElement('div');
                vulnElement.className = `vulnerability-item vulnerability-${severity}`;
                vulnElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${title}</h6>
                            <small class="text-muted">${id}</small>
                        </div>
                        <span class="badge bg-${severity === 'critical' ? 'danger' : severity === 'high' ? 'warning' : 'secondary'}">
                            CVSS ${score}
                        </span>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>Detected: ${new Date().toLocaleTimeString()}
                        </small>
                    </div>
                `;
                
                feed.insertBefore(vulnElement, feed.firstChild);
                
                // Highlight new vulnerability
                vulnElement.style.opacity = '0';
                vulnElement.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    vulnElement.style.transition = 'all 0.5s ease';
                    vulnElement.style.opacity = '1';
                    vulnElement.style.transform = 'translateX(0)';
                }, 100);
            }
            
            function initRiskChart() {
                const ctx = document.getElementById('riskChart').getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Critical', 'High', 'Medium', 'Low', 'Secure'],
                        datasets: [{
                            data: [12, 18, 25, 30, 15],
                            backgroundColor: [
                                '#dc3545',
                                '#fd7e14', 
                                '#ffc107',
                                '#28a745',
                                '#6f42c1'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            },
                            title: {
                                display: true,
                                text: 'Risk Distribution'
                            }
                        }
                    }
                });
            }
            
            // Initialize ROI calculator
            updateROI();
            
            // Generate report functionality
            document.getElementById('generateReport').addEventListener('click', function() {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-check me-2"></i>Report Generated';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    
                    // Reset after 3 seconds
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Generate Executive Report';
                        this.classList.remove('btn-success');
                        this.classList.add('btn-primary');
                    }, 3000);
                }, 2000);
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/demo/start', methods=['POST'])
def start_demo_session():
    """Start a new demo session"""
    session_id = str(uuid.uuid4())
    demo_platform.demo_sessions[session_id] = {
        'start_time': datetime.datetime.now(),
        'vulnerabilities_shown': 0,
        'interactions': []
    }
    return jsonify({'session_id': session_id, 'status': 'started'})

@app.route('/api/demo/vulnerabilities')
def get_demo_vulnerabilities():
    """Get demonstration vulnerabilities"""
    return jsonify(demo_platform.vulnerability_database)

@app.route('/api/demo/roi', methods=['POST'])
def calculate_demo_roi():
    """Calculate ROI for demonstration"""
    data = request.get_json()
    budget = data.get('budget', 45000000)
    employees = data.get('employees', 100000)
    
    # Calculate savings based on Enterprise Scanner benefits
    roi_calc = demo_platform.roi_calculator
    benefits = roi_calc['enterprise_scanner_benefits']
    
    vulnerability_savings = budget * 0.15 * benefits['vulnerability_reduction']
    incident_savings = 280000 * 156 * benefits['incident_response_improvement'] * 0.4
    compliance_savings = 1200000 * benefits['compliance_efficiency']
    productivity_savings = employees * 0.05 * 145000 * benefits['team_productivity_gain']
    
    total_savings = vulnerability_savings + incident_savings + compliance_savings + productivity_savings
    license_cost = 185000  # Average Enterprise Scanner license
    roi_percentage = ((total_savings - license_cost) / license_cost) * 100
    
    return jsonify({
        'total_savings': total_savings,
        'license_cost': license_cost,
        'roi_percentage': roi_percentage,
        'breakdown': {
            'vulnerability_reduction': vulnerability_savings,
            'incident_response': incident_savings,
            'compliance_efficiency': compliance_savings,
            'productivity_gains': productivity_savings
        }
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'connected', 'session_id': request.sid})

@socketio.on('start_live_demo')
def handle_live_demo(data):
    """Handle live demo start"""
    session_id = request.sid
    logger.info(f"Starting live demo for session: {session_id}")
    
    # Send live vulnerability updates
    socketio.start_background_task(send_live_updates, session_id)

def send_live_updates(session_id):
    """Send live vulnerability updates"""
    vulnerabilities = demo_platform.vulnerability_database
    
    for category, vulns in vulnerabilities.items():
        for vuln in vulns:
            time.sleep(random.uniform(2, 5))  # Random delay between updates
            socketio.emit('vulnerability_update', {
                'category': category,
                'vulnerability': vuln,
                'timestamp': datetime.datetime.now().isoformat()
            }, room=session_id)

def main():
    """Start the live demo platform"""
    print("=" * 60)
    print("🚀 ENTERPRISE SCANNER LIVE DEMO PLATFORM")
    print("Fortune 500 Interactive Demonstration System")
    print("=" * 60)
    
    try:
        print(f"\n✅ DEMO PLATFORM STARTING...")
        print(f"🌐 Live Demo URL: http://localhost:5000")
        print(f"📊 Real-time vulnerability feed active")
        print(f"💰 Interactive ROI calculator ready")
        print(f"📈 Executive dashboards operational")
        print(f"🔄 WebSocket connections enabled")
        
        print(f"\n🎯 DEMO FEATURES:")
        print(f"   • Real-time vulnerability detection simulation")
        print(f"   • Interactive Fortune 500 ROI calculator")
        print(f"   • Executive risk dashboards and metrics")
        print(f"   • Live security scoring and compliance tracking")
        print(f"   • Professional presentation interface")
        
        print(f"\n📞 DEMO SUPPORT:")
        print(f"   • Sales demonstrations: sales@enterprisescanner.com")
        print(f"   • Executive briefings: Schedule through platform")
        print(f"   • Technical support: support@enterprisescanner.com")
        
        print(f"\n🚀 DEMO PLATFORM READY FOR FORTUNE 500 PRESENTATIONS!")
        
        # Start the demo platform
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"Demo platform failed to start: {e}")
        print(f"\n❌ Demo platform startup failed: {e}")

if __name__ == "__main__":
    main()