#!/usr/bin/env python3
"""
Enterprise Scanner - Partner Portal System
White-label partner management and channel partner integration
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
import uuid
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Partner data storage
partners = {}
partner_analytics = {}
white_label_configs = {}

# Partner tier configuration
PARTNER_TIERS = {
    'bronze': {
        'name': 'Bronze Partner',
        'commission_rate': 15,
        'features': ['Basic reporting', 'Standard support', 'Marketing materials'],
        'min_revenue': 0,
        'color': '#cd7f32'
    },
    'silver': {
        'name': 'Silver Partner',
        'commission_rate': 20,
        'features': ['Advanced reporting', 'Priority support', 'Co-marketing', 'Training resources'],
        'min_revenue': 50000,
        'color': '#c0c0c0'
    },
    'gold': {
        'name': 'Gold Partner',
        'commission_rate': 25,
        'features': ['Executive reporting', 'Dedicated support', 'Joint marketing', 'Technical training', 'Early access'],
        'min_revenue': 150000,
        'color': '#ffd700'
    },
    'platinum': {
        'name': 'Platinum Partner',
        'commission_rate': 30,
        'features': ['White-label platform', 'Custom integrations', 'Executive support', 'Revenue sharing', 'Product roadmap input'],
        'min_revenue': 500000,
        'color': '#e5e4e2'
    }
}

class PartnerManager:
    @staticmethod
    def create_partner(partner_data):
        """Create new partner account"""
        partner_id = str(uuid.uuid4())
        
        partner = {
            'id': partner_id,
            'company_name': partner_data.get('company_name'),
            'contact_name': partner_data.get('contact_name'),
            'email': partner_data.get('email'),
            'phone': partner_data.get('phone'),
            'address': partner_data.get('address'),
            'tier': 'bronze',
            'status': 'active',
            'created_date': datetime.now().isoformat(),
            'total_revenue': 0,
            'monthly_revenue': 0,
            'commission_earned': 0,
            'clients_referred': 0,
            'conversion_rate': 0,
            'api_key': secrets.token_urlsafe(32),
            'white_label_enabled': False,
            'custom_domain': None
        }
        
        partners[partner_id] = partner
        
        # Initialize analytics
        partner_analytics[partner_id] = {
            'monthly_stats': [],
            'referral_history': [],
            'commission_history': [],
            'client_pipeline': []
        }
        
        return partner_id

    @staticmethod
    def get_partner_tier(partner_id):
        """Determine partner tier based on revenue"""
        if partner_id not in partners:
            return 'bronze'
        
        revenue = partners[partner_id]['total_revenue']
        
        if revenue >= 500000:
            return 'platinum'
        elif revenue >= 150000:
            return 'gold'
        elif revenue >= 50000:
            return 'silver'
        else:
            return 'bronze'

    @staticmethod
    def update_partner_revenue(partner_id, amount):
        """Update partner revenue and tier"""
        if partner_id in partners:
            partners[partner_id]['total_revenue'] += amount
            partners[partner_id]['monthly_revenue'] += amount
            
            # Update tier
            new_tier = PartnerManager.get_partner_tier(partner_id)
            partners[partner_id]['tier'] = new_tier
            
            # Calculate commission
            commission_rate = PARTNER_TIERS[new_tier]['commission_rate'] / 100
            commission = amount * commission_rate
            partners[partner_id]['commission_earned'] += commission
            
            # Log transaction
            if partner_id in partner_analytics:
                partner_analytics[partner_id]['commission_history'].append({
                    'date': datetime.now().isoformat(),
                    'amount': amount,
                    'commission': commission,
                    'tier': new_tier
                })

@app.route('/')
def portal_home():
    """Partner portal homepage"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Scanner Partner Portal</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #f8fafc; }
            .hero-section { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 80px 0; }
            .partner-card { background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 30px; }
            .tier-card { border: 2px solid; border-radius: 12px; padding: 25px; margin-bottom: 20px; text-align: center; }
            .tier-bronze { border-color: #cd7f32; background: linear-gradient(135deg, #cd7f32, #b8860b); color: white; }
            .tier-silver { border-color: #c0c0c0; background: linear-gradient(135deg, #c0c0c0, #a9a9a9); color: white; }
            .tier-gold { border-color: #ffd700; background: linear-gradient(135deg, #ffd700, #ffb347); color: #333; }
            .tier-platinum { border-color: #e5e4e2; background: linear-gradient(135deg, #e5e4e2, #d3d3d3); color: #333; }
            .btn-partner { background: #fbbf24; color: #0f172a; border: none; padding: 12px 25px; font-weight: 600; border-radius: 8px; }
            .metric-value { font-size: 2rem; font-weight: 700; }
            .feature-list { list-style: none; padding: 0; }
            .feature-list li { padding: 8px 0; }
            .feature-list li:before { content: '✓'; color: #10b981; font-weight: bold; margin-right: 10px; }
        </style>
    </head>
    <body>
        <!-- Hero Section -->
        <div class="hero-section">
            <div class="container">
                <div class="row">
                    <div class="col-lg-8 mx-auto text-center">
                        <h1 class="display-4 fw-bold">🤝 Partner Portal</h1>
                        <p class="lead">Enterprise Scanner Channel Partner Program</p>
                        <p>Join our exclusive network of cybersecurity partners serving Fortune 500 companies</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="container py-5">
            <!-- Partner Program Overview -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="partner-card text-center">
                        <h2 class="mb-4">🚀 Why Partner With Enterprise Scanner?</h2>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="metric-value text-primary">30%</div>
                                <p>Commission Rates</p>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-value text-success">$2.5M</div>
                                <p>Average Partner Revenue</p>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-value text-warning">500+</div>
                                <p>Fortune 500 Clients</p>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-value text-info">24/7</div>
                                <p>Partner Support</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Partner Tiers -->
            <div class="row mb-5">
                <div class="col-12">
                    <h2 class="text-center mb-4">📊 Partner Tier Program</h2>
                </div>
                
                <div class="col-md-3">
                    <div class="tier-card tier-bronze">
                        <h4>Bronze Partner</h4>
                        <div class="metric-value">15%</div>
                        <p>Commission Rate</p>
                        <ul class="feature-list mt-3">
                            <li>Basic reporting</li>
                            <li>Standard support</li>
                            <li>Marketing materials</li>
                        </ul>
                        <p class="mt-3"><small>Entry Level</small></p>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="tier-card tier-silver">
                        <h4>Silver Partner</h4>
                        <div class="metric-value">20%</div>
                        <p>Commission Rate</p>
                        <ul class="feature-list mt-3">
                            <li>Advanced reporting</li>
                            <li>Priority support</li>
                            <li>Co-marketing</li>
                            <li>Training resources</li>
                        </ul>
                        <p class="mt-3"><small>$50K+ Revenue</small></p>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="tier-card tier-gold">
                        <h4>Gold Partner</h4>
                        <div class="metric-value">25%</div>
                        <p>Commission Rate</p>
                        <ul class="feature-list mt-3">
                            <li>Executive reporting</li>
                            <li>Dedicated support</li>
                            <li>Joint marketing</li>
                            <li>Technical training</li>
                        </ul>
                        <p class="mt-3"><small>$150K+ Revenue</small></p>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="tier-card tier-platinum">
                        <h4>Platinum Partner</h4>
                        <div class="metric-value">30%</div>
                        <p>Commission Rate</p>
                        <ul class="feature-list mt-3">
                            <li>White-label platform</li>
                            <li>Custom integrations</li>
                            <li>Executive support</li>
                            <li>Revenue sharing</li>
                        </ul>
                        <p class="mt-3"><small>$500K+ Revenue</small></p>
                    </div>
                </div>
            </div>
            
            <!-- Partner Registration -->
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="partner-card">
                        <h3 class="mb-4 text-center">🚀 Become a Partner</h3>
                        <form id="partnerForm">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Company Name</label>
                                    <input type="text" class="form-control" id="companyName" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Contact Name</label>
                                    <input type="text" class="form-control" id="contactName" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Email Address</label>
                                    <input type="email" class="form-control" id="email" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Phone Number</label>
                                    <input type="tel" class="form-control" id="phone" required>
                                </div>
                                <div class="col-12">
                                    <label class="form-label">Business Address</label>
                                    <textarea class="form-control" id="address" rows="3"></textarea>
                                </div>
                                <div class="col-12">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="agreeTerms" required>
                                        <label class="form-check-label" for="agreeTerms">
                                            I agree to the Enterprise Scanner Partner Program terms and conditions
                                        </label>
                                    </div>
                                </div>
                                <div class="col-12 text-center">
                                    <button type="submit" class="btn btn-partner btn-lg">
                                        🤝 Join Partner Program
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Partner Login -->
            <div class="row mt-5">
                <div class="col-lg-6 mx-auto">
                    <div class="partner-card text-center">
                        <h4>🔐 Existing Partner?</h4>
                        <p>Access your partner dashboard, analytics, and resources</p>
                        <a href="/partner/login" class="btn btn-outline-primary">Partner Login</a>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('partnerForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = {
                    company_name: document.getElementById('companyName').value,
                    contact_name: document.getElementById('contactName').value,
                    email: document.getElementById('email').value,
                    phone: document.getElementById('phone').value,
                    address: document.getElementById('address').value
                };
                
                try {
                    const response = await fetch('/api/partners/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert('🎉 Partner registration successful! Check your email for login credentials.');
                        document.getElementById('partnerForm').reset();
                    } else {
                        alert('Registration failed: ' + result.message);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/partner/dashboard')
def partner_dashboard():
    """Partner dashboard with analytics"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Partner Dashboard - Enterprise Scanner</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background: #f8fafc; }
            .sidebar { background: #1e293b; min-height: 100vh; padding: 20px 0; }
            .sidebar a { color: #cbd5e1; text-decoration: none; display: block; padding: 10px 20px; border-radius: 6px; margin: 2px 10px; }
            .sidebar a:hover, .sidebar a.active { background: #334155; color: white; }
            .main-content { padding: 30px; }
            .metric-card { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
            .metric-value { font-size: 2rem; font-weight: 700; }
            .tier-badge { padding: 8px 16px; border-radius: 20px; font-weight: 600; }
            .tier-bronze { background: #cd7f32; color: white; }
            .tier-silver { background: #c0c0c0; color: white; }
            .tier-gold { background: #ffd700; color: #333; }
            .tier-platinum { background: #e5e4e2; color: #333; }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <div class="col-md-3 sidebar">
                    <h5 class="text-white mb-4 px-3">🤝 Partner Portal</h5>
                    <a href="#dashboard" class="active">📊 Dashboard</a>
                    <a href="#analytics">📈 Analytics</a>
                    <a href="#commissions">💰 Commissions</a>
                    <a href="#clients">👥 Clients</a>
                    <a href="#marketing">📢 Marketing</a>
                    <a href="#support">🎧 Support</a>
                    <a href="#white-label">🏷️ White Label</a>
                    <a href="#api">🔗 API Access</a>
                </div>
                
                <!-- Main Content -->
                <div class="col-md-9 main-content">
                    <h1>Partner Dashboard</h1>
                    <p class="text-muted">Welcome back to your Enterprise Scanner partner portal</p>
                    
                    <!-- Partner Status -->
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="metric-card">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h5>Partner Status</h5>
                                        <span class="tier-badge tier-gold">Gold Partner</span>
                                    </div>
                                    <div class="text-end">
                                        <div class="metric-value text-success">25%</div>
                                        <small>Commission Rate</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Key Metrics -->
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="metric-card text-center">
                                <div class="metric-value text-primary">$1,247,580</div>
                                <p class="mb-0">Total Revenue</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="metric-card text-center">
                                <div class="metric-value text-success">$311,895</div>
                                <p class="mb-0">Commission Earned</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="metric-card text-center">
                                <div class="metric-value text-warning">127</div>
                                <p class="mb-0">Clients Referred</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="metric-card text-center">
                                <div class="metric-value text-info">34.2%</div>
                                <p class="mb-0">Conversion Rate</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Revenue Chart -->
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="metric-card">
                                <h5 class="mb-3">📈 Revenue Trend</h5>
                                <canvas id="revenueChart" height="100"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Activity -->
                    <div class="row">
                        <div class="col-md-6">
                            <div class="metric-card">
                                <h5 class="mb-3">🎯 Recent Referrals</h5>
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between">
                                        <span>Acme Corp - Security Assessment</span>
                                        <span class="text-success">$15,000</span>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between">
                                        <span>Tech Solutions Inc - Full Platform</span>
                                        <span class="text-success">$45,000</span>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between">
                                        <span>Global Industries - Compliance Suite</span>
                                        <span class="text-success">$28,000</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="metric-card">
                                <h5 class="mb-3">💰 Commission History</h5>
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between">
                                        <span>December 2024</span>
                                        <span class="text-success">$22,150</span>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between">
                                        <span>November 2024</span>
                                        <span class="text-success">$18,750</span>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between">
                                        <span>October 2024</span>
                                        <span class="text-success">$31,420</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Revenue Chart
            const ctx = document.getElementById('revenueChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [{
                        label: 'Monthly Revenue',
                        data: [45000, 52000, 48000, 61000, 58000, 67000, 71000, 69000, 74000, 82000, 79000, 88000],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Commission Earned',
                        data: [11250, 13000, 12000, 15250, 14500, 16750, 17750, 17250, 18500, 20500, 19750, 22000],
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
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/partners/register', methods=['POST'])
def register_partner():
    """Register new partner"""
    partner_data = request.json
    
    try:
        partner_id = PartnerManager.create_partner(partner_data)
        
        return jsonify({
            'success': True,
            'partner_id': partner_id,
            'message': 'Partner registration successful',
            'tier': 'bronze',
            'api_key': partners[partner_id]['api_key']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/partners/<partner_id>/analytics')
def get_partner_analytics(partner_id):
    """Get partner analytics and performance data"""
    if partner_id not in partners:
        return jsonify({'error': 'Partner not found'}), 404
    
    partner = partners[partner_id]
    analytics = partner_analytics.get(partner_id, {})
    
    return jsonify({
        'partner_info': partner,
        'analytics': analytics,
        'tier_info': PARTNER_TIERS[partner['tier']]
    })

@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'partner_portal_system',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("🤝 Starting Enterprise Scanner Partner Portal...")
    print("🌐 Partner Portal: http://localhost:5005")
    print("📊 Partner Dashboard: http://localhost:5005/partner/dashboard")
    print("🏷️ White-label capabilities included")
    print("💰 Commission tracking and tier management")
    print("")
    
    app.run(host='0.0.0.0', port=5005, debug=True)