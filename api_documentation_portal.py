#!/usr/bin/env python3
"""
Enterprise Scanner - API Documentation Portal
Comprehensive API reference and integration guide for Fortune 500 developers
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# API Documentation Structure
API_DOCUMENTATION = {
    'authentication': {
        'title': 'Authentication',
        'description': 'Secure API authentication using OAuth 2.0 and API keys',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/v1/auth/token',
                'description': 'Generate access token',
                'parameters': [
                    {'name': 'client_id', 'type': 'string', 'required': True, 'description': 'Your application client ID'},
                    {'name': 'client_secret', 'type': 'string', 'required': True, 'description': 'Your application client secret'},
                    {'name': 'grant_type', 'type': 'string', 'required': True, 'description': 'OAuth grant type (client_credentials)'}
                ],
                'response_example': {
                    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'token_type': 'Bearer',
                    'expires_in': 3600
                }
            }
        ]
    },
    'scanning': {
        'title': 'Security Scanning',
        'description': 'Comprehensive vulnerability scanning and assessment APIs',
        'endpoints': [
            {
                'method': 'POST',
                'path': '/api/v1/scans',
                'description': 'Initiate a new security scan',
                'parameters': [
                    {'name': 'target', 'type': 'string', 'required': True, 'description': 'Target IP address or domain'},
                    {'name': 'scan_type', 'type': 'string', 'required': True, 'description': 'Type of scan (full, quick, compliance)'},
                    {'name': 'callback_url', 'type': 'string', 'required': False, 'description': 'Webhook URL for scan completion'}
                ],
                'response_example': {
                    'scan_id': 'scan_1234567890',
                    'status': 'initiated',
                    'estimated_duration': '15-30 minutes',
                    'target': 'example.com'
                }
            },
            {
                'method': 'GET',
                'path': '/api/v1/scans/{scan_id}',
                'description': 'Get scan status and results',
                'parameters': [
                    {'name': 'scan_id', 'type': 'string', 'required': True, 'description': 'Unique scan identifier'}
                ],
                'response_example': {
                    'scan_id': 'scan_1234567890',
                    'status': 'completed',
                    'progress': 100,
                    'vulnerabilities_found': 12,
                    'risk_score': 7.5,
                    'report_url': '/api/v1/scans/scan_1234567890/report'
                }
            }
        ]
    },
    'threats': {
        'title': 'Threat Intelligence',
        'description': 'Real-time threat data and security intelligence feeds',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/v1/threats/live',
                'description': 'Get live threat intelligence feed',
                'parameters': [
                    {'name': 'limit', 'type': 'integer', 'required': False, 'description': 'Number of threats to return (default: 50)'},
                    {'name': 'severity', 'type': 'string', 'required': False, 'description': 'Filter by severity (low, medium, high, critical)'}
                ],
                'response_example': {
                    'threats': [
                        {
                            'id': 'threat_abc123',
                            'type': 'Malware Detection',
                            'severity': 'high',
                            'timestamp': '2024-01-15T10:30:00Z',
                            'source_ip': '192.168.1.100',
                            'description': 'Trojan detected in network traffic'
                        }
                    ],
                    'total_count': 245
                }
            }
        ]
    },
    'compliance': {
        'title': 'Compliance Monitoring',
        'description': 'Regulatory compliance assessment and monitoring APIs',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/v1/compliance/frameworks',
                'description': 'List supported compliance frameworks',
                'parameters': [],
                'response_example': {
                    'frameworks': [
                        {'id': 'gdpr', 'name': 'GDPR', 'description': 'General Data Protection Regulation'},
                        {'id': 'hipaa', 'name': 'HIPAA', 'description': 'Health Insurance Portability and Accountability Act'},
                        {'id': 'sox', 'name': 'SOX', 'description': 'Sarbanes-Oxley Act'}
                    ]
                }
            },
            {
                'method': 'POST',
                'path': '/api/v1/compliance/assessments',
                'description': 'Run compliance assessment',
                'parameters': [
                    {'name': 'framework', 'type': 'string', 'required': True, 'description': 'Compliance framework ID'},
                    {'name': 'target_systems', 'type': 'array', 'required': True, 'description': 'List of systems to assess'}
                ],
                'response_example': {
                    'assessment_id': 'comp_789012',
                    'framework': 'gdpr',
                    'status': 'running',
                    'compliance_score': None,
                    'estimated_completion': '2024-01-15T11:00:00Z'
                }
            }
        ]
    },
    'reporting': {
        'title': 'Reports & Analytics',
        'description': 'Generate comprehensive security reports and analytics',
        'endpoints': [
            {
                'method': 'GET',
                'path': '/api/v1/reports/executive',
                'description': 'Generate executive security report',
                'parameters': [
                    {'name': 'date_from', 'type': 'string', 'required': False, 'description': 'Start date (YYYY-MM-DD)'},
                    {'name': 'date_to', 'type': 'string', 'required': False, 'description': 'End date (YYYY-MM-DD)'},
                    {'name': 'format', 'type': 'string', 'required': False, 'description': 'Report format (pdf, json, csv)'}
                ],
                'response_example': {
                    'report_id': 'report_345678',
                    'status': 'generating',
                    'download_url': None,
                    'estimated_completion': '2024-01-15T10:45:00Z'
                }
            }
        ]
    }
}

# Code examples for different languages
CODE_EXAMPLES = {
    'python': {
        'authentication': '''
import requests

# Authenticate and get access token
auth_response = requests.post('https://api.enterprisescanner.com/v1/auth/token', {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'grant_type': 'client_credentials'
})

token = auth_response.json()['access_token']

# Use token for API calls
headers = {'Authorization': f'Bearer {token}'}
        ''',
        'scanning': '''
import requests

headers = {'Authorization': 'Bearer YOUR_ACCESS_TOKEN'}

# Start a security scan
scan_response = requests.post('https://api.enterprisescanner.com/v1/scans', 
    headers=headers,
    json={
        'target': 'example.com',
        'scan_type': 'full',
        'callback_url': 'https://your-app.com/webhook'
    }
)

scan_id = scan_response.json()['scan_id']

# Check scan status
status_response = requests.get(f'https://api.enterprisescanner.com/v1/scans/{scan_id}', 
    headers=headers
)

print(status_response.json())
        '''
    },
    'javascript': {
        'authentication': '''
const axios = require('axios');

// Authenticate and get access token
const authResponse = await axios.post('https://api.enterprisescanner.com/v1/auth/token', {
    client_id: 'your_client_id',
    client_secret: 'your_client_secret',
    grant_type: 'client_credentials'
});

const token = authResponse.data.access_token;

// Set up axios with token
const api = axios.create({
    baseURL: 'https://api.enterprisescanner.com/v1',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
        ''',
        'scanning': '''
const axios = require('axios');

const api = axios.create({
    baseURL: 'https://api.enterprisescanner.com/v1',
    headers: {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
    }
});

// Start a security scan
const scanResponse = await api.post('/scans', {
    target: 'example.com',
    scan_type: 'full',
    callback_url: 'https://your-app.com/webhook'
});

const scanId = scanResponse.data.scan_id;

// Check scan status
const statusResponse = await api.get(`/scans/${scanId}`);
console.log(statusResponse.data);
        '''
    },
    'curl': {
        'authentication': '''
# Get access token
curl -X POST https://api.enterprisescanner.com/v1/auth/token \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "grant_type": "client_credentials"
  }'
        ''',
        'scanning': '''
# Start a security scan
curl -X POST https://api.enterprisescanner.com/v1/scans \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "target": "example.com",
    "scan_type": "full",
    "callback_url": "https://your-app.com/webhook"
  }'

# Check scan status
curl -X GET https://api.enterprisescanner.com/v1/scans/SCAN_ID \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
        '''
    }
}

@app.route('/')
def index():
    """API Documentation homepage"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Scanner API Documentation</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-dark.min.css">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .sidebar { background: #1e293b; min-height: 100vh; padding: 20px 0; }
            .sidebar a { color: #cbd5e1; text-decoration: none; display: block; padding: 8px 20px; border-radius: 6px; margin: 2px 10px; }
            .sidebar a:hover, .sidebar a.active { background: #334155; color: white; }
            .main-content { padding: 30px; }
            .endpoint-card { border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }
            .endpoint-header { background: #f8fafc; padding: 15px 20px; border-bottom: 1px solid #e2e8f0; }
            .endpoint-body { padding: 20px; }
            .method-badge { font-weight: 600; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .method-get { background: #dcfce7; color: #166534; }
            .method-post { background: #dbeafe; color: #1e40af; }
            .method-put { background: #fef3c7; color: #92400e; }
            .method-delete { background: #fecaca; color: #991b1b; }
            .code-tab { border: 1px solid #e2e8f0; border-radius: 8px; margin: 20px 0; }
            .tab-header { background: #f8fafc; padding: 0; border-bottom: 1px solid #e2e8f0; }
            .tab-content { padding: 0; }
            .hero-section { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 60px 0; }
            .feature-icon { font-size: 2rem; margin-bottom: 1rem; }
        </style>
    </head>
    <body>
        <!-- Hero Section -->
        <div class="hero-section">
            <div class="container">
                <div class="row">
                    <div class="col-lg-8 mx-auto text-center">
                        <h1 class="display-4 fw-bold">🔗 Enterprise Scanner API</h1>
                        <p class="lead">Comprehensive cybersecurity API for Fortune 500 integrations</p>
                        <div class="row mt-5">
                            <div class="col-md-3 text-center">
                                <div class="feature-icon">🛡️</div>
                                <h6>Security Scanning</h6>
                                <small>Automated vulnerability assessment</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="feature-icon">🔍</div>
                                <h6>Threat Intelligence</h6>
                                <small>Real-time threat feeds</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="feature-icon">📊</div>
                                <h6>Compliance</h6>
                                <small>Regulatory framework support</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="feature-icon">📈</div>
                                <h6>Analytics</h6>
                                <small>Comprehensive reporting</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <div class="col-md-3 sidebar">
                    <h6 class="text-white mb-3">API Documentation</h6>
                    <a href="#getting-started" class="active">Getting Started</a>
                    <a href="#authentication">Authentication</a>
                    <a href="#scanning">Security Scanning</a>
                    <a href="#threats">Threat Intelligence</a>
                    <a href="#compliance">Compliance</a>
                    <a href="#reporting">Reports & Analytics</a>
                    <a href="#webhooks">Webhooks</a>
                    <a href="#rate-limits">Rate Limits</a>
                    <a href="#sdks">SDKs & Libraries</a>
                    <a href="#support">Support</a>
                </div>
                
                <!-- Main Content -->
                <div class="col-md-9 main-content">
                    <div id="getting-started">
                        <h2>🚀 Getting Started</h2>
                        <p class="lead">Welcome to the Enterprise Scanner API. Our REST API provides comprehensive cybersecurity capabilities for Fortune 500 companies.</p>
                        
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5>📚 Quick Start Guide</h5>
                                        <p>Get up and running with the Enterprise Scanner API in minutes.</p>
                                        <ol>
                                            <li>Obtain API credentials</li>
                                            <li>Authenticate and get access token</li>
                                            <li>Make your first API call</li>
                                            <li>Integrate webhooks</li>
                                        </ol>
                                        <a href="#authentication" class="btn btn-primary">Start Integration</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5>🔧 Developer Resources</h5>
                                        <p>Tools and resources to accelerate your integration.</p>
                                        <ul>
                                            <li>Interactive API explorer</li>
                                            <li>Postman collection</li>
                                            <li>Code samples & SDKs</li>
                                            <li>Testing sandbox</li>
                                        </ul>
                                        <a href="#sdks" class="btn btn-outline-primary">Download SDKs</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <h6>🔑 API Credentials Required</h6>
                            <p class="mb-0">To use the Enterprise Scanner API, you'll need valid API credentials. Contact our sales team at <strong>sales@enterprisescanner.com</strong> to get started with your Enterprise account.</p>
                        </div>
                        
                        <h4>Base URL</h4>
                        <div class="code-tab">
                            <pre class="bg-dark text-light p-3 mb-0"><code>https://api.enterprisescanner.com/v1</code></pre>
                        </div>
                        
                        <h4>Request Format</h4>
                        <p>All API requests should be made over HTTPS. Request and response bodies are JSON formatted.</p>
                        
                        <h4>Response Format</h4>
                        <p>All API responses include standard HTTP status codes and JSON-formatted response bodies.</p>
                    </div>
                    
                    <hr class="my-5">
                    
                    <div id="authentication">
                        <h2>🔐 Authentication</h2>
                        <p>Enterprise Scanner API uses OAuth 2.0 for secure authentication. All API requests require a valid access token.</p>
                        
                        <!-- Authentication endpoints will be populated here -->
                        <div id="auth-endpoints"></div>
                        
                        <h4>Example: Getting an Access Token</h4>
                        <div class="code-tab">
                            <ul class="nav nav-tabs" role="tablist">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#auth-python">Python</button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" data-bs-toggle="tab" data-bs-target="#auth-javascript">JavaScript</button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" data-bs-toggle="tab" data-bs-target="#auth-curl">cURL</button>
                                </li>
                            </ul>
                            <div class="tab-content">
                                <div class="tab-pane fade show active" id="auth-python">
                                    <pre class="bg-dark text-light p-3 mb-0"><code class="language-python">${CODE_EXAMPLES.python.authentication}</code></pre>
                                </div>
                                <div class="tab-pane fade" id="auth-javascript">
                                    <pre class="bg-dark text-light p-3 mb-0"><code class="language-javascript">${CODE_EXAMPLES.javascript.authentication}</code></pre>
                                </div>
                                <div class="tab-pane fade" id="auth-curl">
                                    <pre class="bg-dark text-light p-3 mb-0"><code class="language-bash">${CODE_EXAMPLES.curl.authentication}</code></pre>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <hr class="my-5">
                    
                    <div id="scanning">
                        <h2>🔍 Security Scanning</h2>
                        <p>Comprehensive vulnerability scanning and security assessment capabilities.</p>
                        <div id="scanning-endpoints"></div>
                    </div>
                    
                    <hr class="my-5">
                    
                    <div id="contact-info" class="text-center py-5 bg-light rounded">
                        <h3>Need Help?</h3>
                        <p>Our integration team is here to help you get started with the Enterprise Scanner API.</p>
                        <div class="row">
                            <div class="col-md-4">
                                <h6>📧 Technical Support</h6>
                                <p><a href="mailto:support@enterprisescanner.com">support@enterprisescanner.com</a></p>
                            </div>
                            <div class="col-md-4">
                                <h6>💼 Sales Inquiries</h6>
                                <p><a href="mailto:sales@enterprisescanner.com">sales@enterprisescanner.com</a></p>
                            </div>
                            <div class="col-md-4">
                                <h6>🤝 Partnership</h6>
                                <p><a href="mailto:partnerships@enterprisescanner.com">partnerships@enterprisescanner.com</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
        <script>
            // Load API documentation
            fetch('/api/documentation')
                .then(response => response.json())
                .then(data => {
                    loadEndpoints('auth-endpoints', data.authentication);
                    loadEndpoints('scanning-endpoints', data.scanning);
                });
            
            function loadEndpoints(containerId, section) {
                const container = document.getElementById(containerId);
                container.innerHTML = '';
                
                section.endpoints.forEach(endpoint => {
                    const endpointHtml = `
                        <div class="endpoint-card">
                            <div class="endpoint-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <span class="method-badge method-${endpoint.method.toLowerCase()}">${endpoint.method}</span>
                                        <code class="ms-2">${endpoint.path}</code>
                                    </div>
                                </div>
                                <p class="mt-2 mb-0">${endpoint.description}</p>
                            </div>
                            <div class="endpoint-body">
                                <h6>Parameters</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Type</th>
                                                <th>Required</th>
                                                <th>Description</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${endpoint.parameters.map(param => `
                                                <tr>
                                                    <td><code>${param.name}</code></td>
                                                    <td>${param.type}</td>
                                                    <td>${param.required ? '✓' : '✗'}</td>
                                                    <td>${param.description}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                                <h6>Example Response</h6>
                                <pre class="bg-dark text-light p-3"><code class="language-json">${JSON.stringify(endpoint.response_example, null, 2)}</code></pre>
                            </div>
                        </div>
                    `;
                    container.innerHTML += endpointHtml;
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/documentation')
def get_documentation():
    """Get API documentation structure"""
    return jsonify(API_DOCUMENTATION)

@app.route('/api/examples/<language>')
def get_code_examples(language):
    """Get code examples for specific language"""
    if language in CODE_EXAMPLES:
        return jsonify(CODE_EXAMPLES[language])
    return jsonify({'error': 'Language not supported'}), 404

@app.route('/playground')
def api_playground():
    """Interactive API testing playground"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Scanner API Playground</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #f8fafc; }
            .playground-container { max-width: 1200px; margin: 0 auto; padding: 30px; }
            .request-panel, .response-panel { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .method-select { max-width: 120px; }
            .response-area { background: #1e293b; color: #e2e8f0; border-radius: 6px; padding: 15px; font-family: 'Courier New', monospace; min-height: 200px; }
        </style>
    </head>
    <body>
        <div class="playground-container">
            <h1 class="mb-4">🧪 API Playground</h1>
            <p class="text-muted mb-4">Test Enterprise Scanner API endpoints interactively</p>
            
            <div class="request-panel">
                <h5>Request</h5>
                <div class="row g-3">
                    <div class="col-md-2">
                        <select class="form-select method-select" id="method">
                            <option value="GET">GET</option>
                            <option value="POST">POST</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                        </select>
                    </div>
                    <div class="col-md-10">
                        <input type="text" class="form-control" id="endpoint" placeholder="Enter API endpoint" value="/api/v1/scans">
                    </div>
                </div>
                
                <div class="mt-3">
                    <label class="form-label">Headers</label>
                    <textarea class="form-control" id="headers" rows="3" placeholder="Authorization: Bearer YOUR_TOKEN">Authorization: Bearer demo_token_12345</textarea>
                </div>
                
                <div class="mt-3">
                    <label class="form-label">Request Body (JSON)</label>
                    <textarea class="form-control" id="body" rows="5" placeholder="Enter JSON request body">{
  "target": "example.com",
  "scan_type": "quick"
}</textarea>
                </div>
                
                <button class="btn btn-primary mt-3" onclick="sendRequest()">🚀 Send Request</button>
            </div>
            
            <div class="response-panel">
                <h5>Response</h5>
                <div id="response-status" class="mb-2"></div>
                <div class="response-area" id="response-body">
                    Click "Send Request" to see the API response here...
                </div>
            </div>
        </div>
        
        <script>
            async function sendRequest() {
                const method = document.getElementById('method').value;
                const endpoint = document.getElementById('endpoint').value;
                const headersText = document.getElementById('headers').value;
                const bodyText = document.getElementById('body').value;
                
                // Parse headers
                const headers = {};
                headersText.split('\\n').forEach(line => {
                    const [key, value] = line.split(': ');
                    if (key && value) {
                        headers[key.trim()] = value.trim();
                    }
                });
                
                // Prepare request options
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        ...headers
                    }
                };
                
                if (method !== 'GET' && bodyText.trim()) {
                    try {
                        options.body = bodyText;
                    } catch (e) {
                        document.getElementById('response-body').textContent = 'Invalid JSON in request body';
                        return;
                    }
                }
                
                try {
                    // Mock API response for demo
                    const mockResponse = {
                        status: 200,
                        data: {
                            message: "This is a demo response from the API playground",
                            endpoint: endpoint,
                            method: method,
                            timestamp: new Date().toISOString(),
                            demo_data: {
                                scan_id: "demo_scan_12345",
                                status: "initiated",
                                target: "example.com"
                            }
                        }
                    };
                    
                    document.getElementById('response-status').innerHTML = 
                        `<span class="badge bg-success">200 OK</span> <small class="text-muted">Response time: 145ms</small>`;
                    
                    document.getElementById('response-body').textContent = 
                        JSON.stringify(mockResponse.data, null, 2);
                    
                } catch (error) {
                    document.getElementById('response-status').innerHTML = 
                        `<span class="badge bg-danger">Error</span>`;
                    document.getElementById('response-body').textContent = 
                        'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'api_documentation_portal',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("📚 Starting Enterprise Scanner API Documentation Portal...")
    print("🌐 Documentation: http://localhost:5004")
    print("🧪 API Playground: http://localhost:5004/playground")
    print("🔗 Integration guides and code samples available")
    print("")
    
    app.run(host='0.0.0.0', port=5004, debug=True)