#!/usr/bin/env python3
"""
Enterprise Scanner - Enterprise Integration Hub
Seamless integration with existing enterprise systems and third-party tools
"""

from flask import Flask, render_template_string, jsonify, request
import json
import threading
import time
import random
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

class EnterpriseIntegrationHub:
    def __init__(self):
        self.integrations = {
            'siem_systems': {
                'splunk': {'status': 'CONNECTED', 'last_sync': datetime.now(), 'data_points': 15847},
                'qradar': {'status': 'CONNECTED', 'last_sync': datetime.now(), 'data_points': 12350},
                'arcsight': {'status': 'AVAILABLE', 'last_sync': None, 'data_points': 0}
            },
            'identity_management': {
                'active_directory': {'status': 'CONNECTED', 'users_synced': 2847, 'groups_synced': 156},
                'okta': {'status': 'CONNECTED', 'users_synced': 1250, 'groups_synced': 89},
                'azure_ad': {'status': 'CONNECTED', 'users_synced': 3200, 'groups_synced': 245}
            },
            'cloud_platforms': {
                'aws': {'status': 'CONNECTED', 'accounts': 15, 'resources_monitored': 2847},
                'azure': {'status': 'CONNECTED', 'subscriptions': 8, 'resources_monitored': 1650},
                'gcp': {'status': 'AVAILABLE', 'projects': 0, 'resources_monitored': 0}
            },
            'ticketing_systems': {
                'servicenow': {'status': 'CONNECTED', 'tickets_processed': 1247, 'avg_resolution': '4.2h'},
                'jira': {'status': 'CONNECTED', 'tickets_processed': 856, 'avg_resolution': '6.1h'},
                'remedy': {'status': 'AVAILABLE', 'tickets_processed': 0, 'avg_resolution': 'N/A'}
            },
            'communication': {
                'slack': {'status': 'CONNECTED', 'channels': 25, 'alerts_sent': 847},
                'teams': {'status': 'CONNECTED', 'channels': 18, 'alerts_sent': 652},
                'email': {'status': 'CONNECTED', 'recipients': 150, 'alerts_sent': 1250}
            }
        }
        
        self.integration_metrics = {
            'total_integrations': 15,
            'active_connections': 12,
            'data_sync_rate': '99.7%',
            'api_calls_today': 25847,
            'average_latency': '120ms',
            'error_rate': '0.1%'
        }
        
        self.data_flows = []
        self.start_data_sync()

    def start_data_sync(self):
        """Start continuous data synchronization"""
        def sync_data():
            while True:
                self.simulate_data_sync()
                self.update_integration_metrics()
                time.sleep(15)  # Sync every 15 seconds
        
        thread = threading.Thread(target=sync_data, daemon=True)
        thread.start()

    def simulate_data_sync(self):
        """Simulate data synchronization across integrations"""
        sync_types = [
            'Security Events from Splunk',
            'User Authentication from Azure AD',
            'Cloud Resource Changes from AWS',
            'Incident Updates from ServiceNow',
            'Alert Notifications to Slack',
            'Vulnerability Scans from Qualys',
            'Compliance Data from RSA Archer',
            'Network Flow Data from NetFlow'
        ]
        
        # Random data sync event
        if random.random() < 0.6:  # 60% chance of sync event
            sync_event = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'type': random.choice(sync_types),
                'status': 'SUCCESS',
                'records_processed': random.randint(50, 500),
                'latency': f"{random.randint(80, 200)}ms",
                'source': self.get_source_system(random.choice(sync_types)),
                'destination': 'Enterprise Scanner'
            }
            
            self.data_flows.append(sync_event)
            
            # Keep only last 50 sync events
            if len(self.data_flows) > 50:
                self.data_flows = self.data_flows[-50:]

    def get_source_system(self, sync_type):
        """Get source system based on sync type"""
        source_mapping = {
            'Security Events from Splunk': 'Splunk SIEM',
            'User Authentication from Azure AD': 'Azure Active Directory',
            'Cloud Resource Changes from AWS': 'Amazon Web Services',
            'Incident Updates from ServiceNow': 'ServiceNow ITSM',
            'Alert Notifications to Slack': 'Slack Workspace',
            'Vulnerability Scans from Qualys': 'Qualys VMDR',
            'Compliance Data from RSA Archer': 'RSA Archer GRC',
            'Network Flow Data from NetFlow': 'Cisco NetFlow'
        }
        return source_mapping.get(sync_type, 'Unknown System')

    def update_integration_metrics(self):
        """Update integration performance metrics"""
        self.integration_metrics['api_calls_today'] += random.randint(10, 50)
        self.integration_metrics['average_latency'] = f"{random.randint(100, 150)}ms"
        
        # Simulate high reliability
        success_rate = random.uniform(99.5, 99.9)
        self.integration_metrics['data_sync_rate'] = f"{success_rate:.1f}%"

    def get_integration_status(self):
        """Get comprehensive integration status"""
        return {
            'integrations': self.integrations,
            'metrics': self.integration_metrics,
            'recent_syncs': self.data_flows[-20:],  # Last 20 sync events
            'health_check': self.perform_health_check()
        }

    def perform_health_check(self):
        """Perform health check on all integrations"""
        health_status = {}
        
        for category, systems in self.integrations.items():
            category_health = {
                'total': len(systems),
                'connected': len([s for s in systems.values() if s['status'] == 'CONNECTED']),
                'available': len([s for s in systems.values() if s['status'] == 'AVAILABLE'])
            }
            category_health['health_score'] = (category_health['connected'] / category_health['total']) * 100
            health_status[category] = category_health
        
        return health_status

    def create_integration(self, system_name, system_type, config):
        """Create new integration"""
        if system_type not in self.integrations:
            self.integrations[system_type] = {}
        
        self.integrations[system_type][system_name] = {
            'status': 'CONNECTING',
            'created': datetime.now().isoformat(),
            'config': config
        }
        
        return {'status': 'success', 'message': f'Integration {system_name} created'}

# Initialize Enterprise Integration Hub
integration_hub = EnterpriseIntegrationHub()

@app.route('/')
def dashboard():
    """Main Enterprise Integration Hub Dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Integration Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: #ffffff; }
        .card { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); }
        .integration-connected { border-left: 4px solid #28a745; }
        .integration-available { border-left: 4px solid #ffc107; }
        .integration-error { border-left: 4px solid #dc3545; }
        .sync-flow { animation: flowAnimation 3s infinite; }
        @keyframes flowAnimation { 0%, 100% { opacity: 0.7; } 50% { opacity: 1; } }
        .metric-card { transition: transform 0.3s; }
        .metric-card:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body text-center">
                        <h1><i class="fas fa-network-wired"></i> Enterprise Integration Hub</h1>
                        <p class="mb-0">Seamless Integration | Real-time Data Sync | Enterprise Connectivity</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Integration Metrics Row -->
        <div class="row mb-4">
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 class="text-success"><span id="totalIntegrations">15</span></h3>
                        <p>Total Integrations</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 class="text-primary"><span id="activeConnections">12</span></h3>
                        <p>Active Connections</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 class="text-info"><span id="syncRate">99.7%</span></h3>
                        <p>Sync Success Rate</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 class="text-warning"><span id="apiCalls">25,847</span></h3>
                        <p>API Calls Today</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 class="text-secondary"><span id="avgLatency">120ms</span></h3>
                        <p>Avg Latency</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 class="text-success"><span id="errorRate">0.1%</span></h3>
                        <p>Error Rate</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Integration Categories -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-shield-alt"></i> Security Systems</h5>
                    </div>
                    <div class="card-body">
                        <div id="siemIntegrations"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-users"></i> Identity Management</h5>
                    </div>
                    <div class="card-body">
                        <div id="identityIntegrations"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cloud"></i> Cloud Platforms</h5>
                    </div>
                    <div class="card-body">
                        <div id="cloudIntegrations"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-ticket-alt"></i> Ticketing & Communication</h5>
                    </div>
                    <div class="card-body">
                        <div id="ticketingIntegrations"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Real-time Data Flows -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-exchange-alt sync-flow"></i> Real-time Data Flows</h5>
                    </div>
                    <div class="card-body">
                        <div id="dataFlows"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/integration-status')
                .then(response => response.json())
                .then(data => {
                    // Update metrics
                    document.getElementById('totalIntegrations').textContent = data.metrics.total_integrations;
                    document.getElementById('activeConnections').textContent = data.metrics.active_connections;
                    document.getElementById('syncRate').textContent = data.metrics.data_sync_rate;
                    document.getElementById('apiCalls').textContent = data.metrics.api_calls_today.toLocaleString();
                    document.getElementById('avgLatency').textContent = data.metrics.average_latency;
                    document.getElementById('errorRate').textContent = data.metrics.error_rate;

                    // Update integration categories
                    updateIntegrationCategory('siemIntegrations', data.integrations.siem_systems);
                    updateIntegrationCategory('identityIntegrations', data.integrations.identity_management);
                    updateIntegrationCategory('cloudIntegrations', data.integrations.cloud_platforms);
                    
                    // Combine ticketing and communication
                    const ticketingAndComm = {...data.integrations.ticketing_systems, ...data.integrations.communication};
                    updateIntegrationCategory('ticketingIntegrations', ticketingAndComm);

                    // Update data flows
                    updateDataFlows(data.recent_syncs);
                });
        }

        function updateIntegrationCategory(containerId, integrations) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            
            Object.entries(integrations).forEach(([name, integration]) => {
                const statusClass = integration.status === 'CONNECTED' ? 'integration-connected' : 
                                  integration.status === 'AVAILABLE' ? 'integration-available' : 'integration-error';
                
                const integrationDiv = document.createElement('div');
                integrationDiv.className = `card mb-2 ${statusClass}`;
                integrationDiv.innerHTML = `
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span><strong>${name.toUpperCase()}</strong></span>
                            <span class="badge ${integration.status === 'CONNECTED' ? 'bg-success' : 'bg-warning'}">${integration.status}</span>
                        </div>
                    </div>
                `;
                container.appendChild(integrationDiv);
            });
        }

        function updateDataFlows(flows) {
            const container = document.getElementById('dataFlows');
            container.innerHTML = '';
            
            flows.forEach(flow => {
                const flowDiv = document.createElement('div');
                flowDiv.className = 'alert alert-info mb-2';
                flowDiv.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${flow.type}</strong> - ${flow.records_processed} records
                            <small class="text-muted d-block">From: ${flow.source}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-success">${flow.status}</span>
                            <small class="d-block">${flow.latency}</small>
                        </div>
                    </div>
                `;
                container.appendChild(flowDiv);
            });
        }

        // Initial load and periodic updates
        updateDashboard();
        setInterval(updateDashboard, 10000); // Update every 10 seconds
    </script>
</body>
</html>
    ''')

@app.route('/api/integration-status')
def api_integration_status():
    """API endpoint for integration status"""
    return jsonify(integration_hub.get_integration_status())

@app.route('/api/create-integration', methods=['POST'])
def api_create_integration():
    """API endpoint to create new integration"""
    data = request.get_json()
    result = integration_hub.create_integration(
        data.get('name'),
        data.get('type'),
        data.get('config', {})
    )
    return jsonify(result)

@app.route('/admin/manage')
def admin_manage():
    """Admin interface for managing integrations"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Integration Hub - Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: #ffffff; }
        .card { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h3><i class="fas fa-cogs"></i> Enterprise Integration Hub - Admin</h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Integration Management</h5>
                                <div class="mb-3">
                                    <label class="form-label">System Name</label>
                                    <input type="text" class="form-control" id="systemName" placeholder="e.g., CrowdStrike">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">System Type</label>
                                    <select class="form-control" id="systemType">
                                        <option value="siem_systems">SIEM Systems</option>
                                        <option value="identity_management">Identity Management</option>
                                        <option value="cloud_platforms">Cloud Platforms</option>
                                        <option value="ticketing_systems">Ticketing Systems</option>
                                        <option value="communication">Communication</option>
                                    </select>
                                </div>
                                <button class="btn btn-primary" onclick="createIntegration()">
                                    <i class="fas fa-plus"></i> Add Integration
                                </button>
                            </div>
                            <div class="col-md-6">
                                <h5>System Status</h5>
                                <div class="alert alert-success">
                                    <i class="fas fa-check-circle"></i> All integrations operational
                                </div>
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle"></i> 12 of 15 integrations connected
                                </div>
                            </div>
                        </div>
                        
                        <hr>
                        
                        <div class="row">
                            <div class="col-12">
                                <h5>Quick Actions</h5>
                                <a href="/" class="btn btn-primary me-2">
                                    <i class="fas fa-tachometer-alt"></i> Main Dashboard
                                </a>
                                <a href="/api/integration-status" class="btn btn-info me-2">
                                    <i class="fas fa-code"></i> API Status
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function createIntegration() {
            const name = document.getElementById('systemName').value;
            const type = document.getElementById('systemType').value;
            
            if (!name) {
                alert('Please enter a system name');
                return;
            }
            
            fetch('/api/create-integration', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, type: type, config: {} })
            })
            .then(response => response.json())
            .then(data => {
                alert('Integration created successfully!');
                document.getElementById('systemName').value = '';
            });
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              Enterprise Integration Hub                      ║
    ║                                                              ║
    ║  🔗 Seamless System Integration                              ║
    ║  🔄 Real-time Data Synchronization                           ║
    ║  📊 Enterprise Connectivity Dashboard                        ║
    ║  🛠️  API Management & Monitoring                             ║
    ║                                                              ║
    ║  🌐 Dashboard: http://localhost:5009                         ║
    ║  🔧 Admin: http://localhost:5009/admin/manage                ║
    ║  📡 API: http://localhost:5009/api/integration-status        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5009, debug=False)