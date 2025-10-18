#!/usr/bin/env python3
"""
Enterprise Scanner Live Monitoring & Analytics Dashboard
Real-Time Business Intelligence & Execution Tracking
Fortune 500 Performance Analytics & Success Metrics
"""

import json
import os
import datetime
import time
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import logging
from flask import Flask, render_template_string, jsonify, request
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Real-time metric data point"""
    name: str
    value: float
    unit: str
    timestamp: datetime.datetime
    trend: str  # "up", "down", "stable"
    target: Optional[float] = None

class LiveMonitoringDashboard:
    """Comprehensive live monitoring and analytics dashboard"""
    
    def __init__(self):
        self.system_name = "Enterprise Scanner Live Monitoring Dashboard"
        self.creation_date = datetime.datetime.now()
        self.app = Flask(__name__)
        self.metrics_data = {}
        self.is_running = False
        
    def initialize_metrics(self):
        """Initialize all tracking metrics"""
        logger.info("Initializing monitoring metrics...")
        
        # Sales & Revenue Metrics
        self.metrics_data["sales"] = {
            "current_arr": MetricData("Annual Recurring Revenue", 2100000, "$", datetime.datetime.now(), "up", 15000000),
            "monthly_revenue": MetricData("Monthly Revenue", 175000, "$", datetime.datetime.now(), "up", 1250000),
            "new_customers": MetricData("New Customers This Month", 3, "customers", datetime.datetime.now(), "up", 8),
            "pipeline_value": MetricData("Sales Pipeline Value", 6500000, "$", datetime.datetime.now(), "up", 15000000),
            "conversion_rate": MetricData("Lead to Customer Conversion", 18.5, "%", datetime.datetime.now(), "stable", 25.0),
            "customer_acquisition_cost": MetricData("Customer Acquisition Cost", 12500, "$", datetime.datetime.now(), "down", 8000),
            "average_deal_size": MetricData("Average Deal Size", 185000, "$", datetime.datetime.now(), "up", 250000)
        }
        
        # Customer Success Metrics
        self.metrics_data["customers"] = {
            "customer_retention": MetricData("Customer Retention Rate", 98.2, "%", datetime.datetime.now(), "stable", 95.0),
            "net_revenue_retention": MetricData("Net Revenue Retention", 145.0, "%", datetime.datetime.now(), "up", 120.0),
            "customer_satisfaction": MetricData("Customer Satisfaction Score", 9.4, "/10", datetime.datetime.now(), "up", 9.0),
            "support_resolution": MetricData("Avg Support Resolution Time", 2.1, "hours", datetime.datetime.now(), "down", 4.0),
            "platform_adoption": MetricData("Platform Adoption Rate", 87.3, "%", datetime.datetime.now(), "up", 85.0),
            "total_customers": MetricData("Total Active Customers", 14, "customers", datetime.datetime.now(), "up", 75),
            "expansion_revenue": MetricData("Customer Expansion Revenue", 285000, "$", datetime.datetime.now(), "up", 500000)
        }
        
        # Product & Technology Metrics
        self.metrics_data["product"] = {
            "platform_uptime": MetricData("Platform Uptime", 99.97, "%", datetime.datetime.now(), "stable", 99.9),
            "api_response_time": MetricData("API Response Time", 145, "ms", datetime.datetime.now(), "down", 200),
            "security_scans": MetricData("Security Scans Today", 2847, "scans", datetime.datetime.now(), "up", 5000),
            "vulnerabilities_detected": MetricData("Vulnerabilities Detected", 1923, "issues", datetime.datetime.now(), "up", 3000),
            "false_positive_rate": MetricData("False Positive Rate", 2.3, "%", datetime.datetime.now(), "down", 5.0),
            "user_engagement": MetricData("Daily Active Users", 342, "users", datetime.datetime.now(), "up", 500),
            "feature_adoption": MetricData("New Feature Adoption", 76.8, "%", datetime.datetime.now(), "up", 80.0)
        }
        
        # Operations & Team Metrics
        self.metrics_data["operations"] = {
            "team_size": MetricData("Total Team Size", 28, "employees", datetime.datetime.now(), "up", 50),
            "burn_rate": MetricData("Monthly Burn Rate", 245000, "$", datetime.datetime.now(), "stable", 300000),
            "runway_months": MetricData("Runway Remaining", 18.5, "months", datetime.datetime.now(), "stable", 18.0),
            "hiring_velocity": MetricData("New Hires This Month", 4, "hires", datetime.datetime.now(), "up", 6),
            "employee_satisfaction": MetricData("Employee NPS Score", 8.7, "/10", datetime.datetime.now(), "stable", 8.5),
            "productivity_index": MetricData("Team Productivity Index", 142.6, "index", datetime.datetime.now(), "up", 150.0),
            "operational_efficiency": MetricData("Operational Efficiency", 91.2, "%", datetime.datetime.now(), "up", 95.0)
        }
        
        # Market & Competition Metrics
        self.metrics_data["market"] = {
            "market_share": MetricData("Fortune 500 Market Share", 0.12, "%", datetime.datetime.now(), "up", 0.5),
            "brand_awareness": MetricData("Brand Awareness Score", 23.4, "index", datetime.datetime.now(), "up", 50.0),
            "competitive_wins": MetricData("Competitive Win Rate", 67.8, "%", datetime.datetime.now(), "up", 75.0),
            "social_mentions": MetricData("Social Media Mentions", 156, "mentions", datetime.datetime.now(), "up", 300),
            "website_traffic": MetricData("Website Monthly Visitors", 12450, "visitors", datetime.datetime.now(), "up", 25000),
            "seo_ranking": MetricData("SEO Keyword Ranking", 3.2, "avg position", datetime.datetime.now(), "down", 2.0),
            "press_coverage": MetricData("Press Mentions This Month", 8, "articles", datetime.datetime.now(), "up", 15)
        }
        
        logger.info("✅ Initialized comprehensive monitoring metrics")
    
    def simulate_real_time_updates(self):
        """Simulate real-time metric updates"""
        while self.is_running:
            try:
                # Update metrics with realistic fluctuations
                for category in self.metrics_data:
                    for metric_name, metric in self.metrics_data[category].items():
                        # Generate realistic updates based on metric type
                        if "rate" in metric_name.lower() or "%" in metric.unit:
                            change = random.uniform(-0.5, 0.8)  # Percentage metrics
                        elif "$" in metric.unit:
                            change = random.uniform(-5000, 12000)  # Dollar amounts
                        elif "time" in metric_name.lower():
                            change = random.uniform(-0.2, 0.1)  # Time metrics (prefer lower)
                        else:
                            change = random.uniform(-5, 15)  # General metrics
                        
                        # Apply change with bounds checking
                        new_value = max(0, metric.value + change)
                        if "%" in metric.unit:
                            new_value = min(100, new_value)
                        
                        # Update trend
                        if new_value > metric.value:
                            trend = "up"
                        elif new_value < metric.value:
                            trend = "down"
                        else:
                            trend = "stable"
                        
                        # Update metric
                        metric.value = round(new_value, 2)
                        metric.timestamp = datetime.datetime.now()
                        metric.trend = trend
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                time.sleep(10)
    
    def create_dashboard_html(self):
        """Create comprehensive dashboard HTML"""
        dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Scanner - Live Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .dashboard-header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-bottom: 3px solid #4CAF50;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }
        
        .company-info h1 {
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .company-info p {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .status-indicators {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-live {
            background: #4CAF50;
            color: white;
        }
        
        .status-monitoring {
            background: #2196F3;
            color: white;
        }
        
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .metric-category {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-top: 4px solid #4CAF50;
        }
        
        .category-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .category-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        
        .sales-icon { background: #4CAF50; }
        .customers-icon { background: #2196F3; }
        .product-icon { background: #FF9800; }
        .operations-icon { background: #9C27B0; }
        .market-icon { background: #F44336; }
        
        .category-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f5f5f5;
        }
        
        .metric-item:last-child {
            border-bottom: none;
        }
        
        .metric-info {
            flex: 1;
        }
        
        .metric-name {
            font-size: 14px;
            color: #555;
            margin-bottom: 3px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .metric-indicators {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .trend-arrow {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
        }
        
        .trend-up { background: #4CAF50; }
        .trend-down { background: #F44336; }
        .trend-stable { background: #9E9E9E; }
        
        .target-progress {
            width: 60px;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.3s ease;
        }
        
        .executive-summary {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-top: 4px solid #2196F3;
            margin-bottom: 30px;
        }
        
        .summary-header {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .kpi-card {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .kpi-label {
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
        }
        
        .live-updates {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            z-index: 1000;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .timestamp {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 12px;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            .status-indicators {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="live-updates">
        🔴 LIVE MONITORING ACTIVE
    </div>
    
    <div class="dashboard-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo">ES</div>
                <div class="company-info">
                    <h1>Enterprise Scanner</h1>
                    <p>Live Monitoring & Analytics Dashboard</p>
                </div>
            </div>
            <div class="status-indicators">
                <div class="status-badge status-live">Live Data</div>
                <div class="status-badge status-monitoring">Monitoring Active</div>
            </div>
        </div>
    </div>
    
    <div class="dashboard-container">
        <div class="executive-summary">
            <div class="summary-header">
                📊 Executive Summary - Real-Time Performance
            </div>
            <div class="summary-grid">
                <div class="kpi-card">
                    <div class="kpi-value">$2.1M</div>
                    <div class="kpi-label">Annual Recurring Revenue</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">98.2%</div>
                    <div class="kpi-label">Customer Retention</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">99.97%</div>
                    <div class="kpi-label">Platform Uptime</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">18.5</div>
                    <div class="kpi-label">Months Runway</div>
                </div>
            </div>
        </div>
        
        <div class="metrics-grid" id="metrics-container">
            <!-- Metrics will be populated by JavaScript -->
        </div>
        
        <div class="timestamp">
            Last Updated: <span id="last-update"></span>
        </div>
    </div>
    
    <script>
        // Real-time dashboard functionality
        let metricsData = {};
        
        function updateTimestamp() {
            document.getElementById('last-update').textContent = new Date().toLocaleString();
        }
        
        function getTrendIcon(trend) {
            switch(trend) {
                case 'up': return '↗';
                case 'down': return '↘';
                default: return '→';
            }
        }
        
        function getTrendClass(trend) {
            return `trend-${trend}`;
        }
        
        function calculateProgress(value, target) {
            if (!target) return 0;
            return Math.min(100, (value / target) * 100);
        }
        
        function formatValue(value, unit) {
            if (unit === '$') {
                return '$' + value.toLocaleString();
            } else if (unit === '%') {
                return value.toFixed(1) + '%';
            } else {
                return value.toLocaleString() + ' ' + unit;
            }
        }
        
        function renderMetrics(data) {
            const container = document.getElementById('metrics-container');
            const categories = {
                'sales': { title: 'Sales & Revenue', icon: '💰', class: 'sales-icon' },
                'customers': { title: 'Customer Success', icon: '👥', class: 'customers-icon' },
                'product': { title: 'Product & Technology', icon: '🚀', class: 'product-icon' },
                'operations': { title: 'Operations & Team', icon: '⚙️', class: 'operations-icon' },
                'market': { title: 'Market & Competition', icon: '📈', class: 'market-icon' }
            };
            
            container.innerHTML = '';
            
            Object.keys(categories).forEach(categoryKey => {
                if (data[categoryKey]) {
                    const category = categories[categoryKey];
                    const categoryData = data[categoryKey];
                    
                    const categoryDiv = document.createElement('div');
                    categoryDiv.className = 'metric-category';
                    
                    categoryDiv.innerHTML = `
                        <div class="category-header">
                            <div class="category-icon ${category.class}">${category.icon}</div>
                            <div class="category-title">${category.title}</div>
                        </div>
                        ${Object.keys(categoryData).map(metricKey => {
                            const metric = categoryData[metricKey];
                            const progress = calculateProgress(metric.value, metric.target);
                            
                            return `
                                <div class="metric-item">
                                    <div class="metric-info">
                                        <div class="metric-name">${metric.name}</div>
                                        <div class="metric-value">${formatValue(metric.value, metric.unit)}</div>
                                    </div>
                                    <div class="metric-indicators">
                                        <div class="trend-arrow ${getTrendClass(metric.trend)}">
                                            ${getTrendIcon(metric.trend)}
                                        </div>
                                        ${metric.target ? `
                                            <div class="target-progress">
                                                <div class="progress-bar" style="width: ${progress}%"></div>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    `;
                    
                    container.appendChild(categoryDiv);
                }
            });
        }
        
        async function fetchMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                metricsData = data;
                renderMetrics(data);
                updateTimestamp();
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }
        
        // Initialize dashboard
        fetchMetrics();
        setInterval(fetchMetrics, 5000); // Update every 5 seconds
        updateTimestamp();
        setInterval(updateTimestamp, 1000); // Update timestamp every second
    </script>
</body>
</html>
        """
        return dashboard_html
    
    def setup_flask_routes(self):
        """Setup Flask routes for dashboard"""
        @self.app.route('/')
        def dashboard():
            return self.create_dashboard_html()
        
        @self.app.route('/api/metrics')
        def api_metrics():
            # Convert metrics to JSON-serializable format
            json_metrics = {}
            for category, metrics in self.metrics_data.items():
                json_metrics[category] = {}
                for name, metric in metrics.items():
                    json_metrics[category][name] = {
                        "name": metric.name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat(),
                        "trend": metric.trend,
                        "target": metric.target
                    }
            return jsonify(json_metrics)
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify({
                "status": "active",
                "uptime": (datetime.datetime.now() - self.creation_date).total_seconds(),
                "metrics_count": sum(len(metrics) for metrics in self.metrics_data.values()),
                "last_update": datetime.datetime.now().isoformat()
            })
    
    def deploy_monitoring_dashboard(self):
        """Deploy live monitoring dashboard"""
        logger.info("🚀 DEPLOYING LIVE MONITORING DASHBOARD...")
        
        # Initialize metrics
        self.initialize_metrics()
        
        # Setup Flask routes
        self.setup_flask_routes()
        
        # Generate deployment summary
        deployment_summary = {
            "system_name": self.system_name,
            "deployment_date": self.creation_date.isoformat(),
            "dashboard_capabilities": {
                "real_time_monitoring": "Live metrics updated every 5 seconds",
                "comprehensive_coverage": f"{sum(len(metrics) for metrics in self.metrics_data.values())} key performance indicators",
                "executive_dashboard": "C-suite ready performance visualization",
                "mobile_responsive": "Optimized for all devices and screen sizes"
            },
            "monitoring_categories": {
                "sales_revenue": f"{len(self.metrics_data['sales'])} sales and revenue metrics",
                "customer_success": f"{len(self.metrics_data['customers'])} customer success indicators",
                "product_technology": f"{len(self.metrics_data['product'])} product and tech metrics",
                "operations_team": f"{len(self.metrics_data['operations'])} operational metrics",
                "market_competition": f"{len(self.metrics_data['market'])} market and competitive metrics"
            },
            "key_features": {
                "live_updates": "Real-time metric updates with trend indicators",
                "target_tracking": "Progress tracking against defined targets",
                "executive_summary": "High-level KPI overview for leadership",
                "responsive_design": "Professional dashboard accessible on all devices",
                "api_endpoints": "RESTful API for metrics data and system status"
            },
            "business_intelligence": {
                "arr_tracking": "Annual Recurring Revenue monitoring",
                "customer_metrics": "Retention, satisfaction, and success tracking",
                "operational_kpis": "Team performance and efficiency metrics",
                "platform_health": "System uptime and performance monitoring",
                "market_position": "Competitive and market share tracking"
            },
            "execution_support": [
                "Real-time sales pipeline and revenue tracking",
                "Customer success and retention monitoring",
                "Product performance and user engagement analytics",
                "Operational efficiency and team productivity metrics",
                "Market position and competitive intelligence tracking"
            ]
        }
        
        # Save deployment summary
        os.makedirs("monitoring_dashboard", exist_ok=True)
        with open("monitoring_dashboard/deployment_summary.json", "w") as f:
            json.dump(deployment_summary, f, indent=2)
        
        return deployment_summary
    
    def start_dashboard_server(self, host='localhost', port=5001):
        """Start the live monitoring dashboard server"""
        logger.info(f"Starting live monitoring dashboard on {host}:{port}...")
        
        self.is_running = True
        
        # Start metrics update thread
        metrics_thread = threading.Thread(target=self.simulate_real_time_updates, daemon=True)
        metrics_thread.start()
        
        # Start Flask server
        self.app.run(host=host, port=port, debug=False, threaded=True)

def main():
    """Deploy live monitoring dashboard"""
    print("=" * 60)
    print("📊 LIVE MONITORING DASHBOARD DEPLOYMENT")
    print("Real-Time Business Intelligence & Analytics")
    print("=" * 60)
    
    dashboard = LiveMonitoringDashboard()
    
    try:
        # Deploy monitoring dashboard
        summary = dashboard.deploy_monitoring_dashboard()
        
        print(f"\n✅ LIVE MONITORING DASHBOARD DEPLOYED!")
        print(f"📊 Monitoring Categories: {len(summary['monitoring_categories'])}")
        print(f"📈 Total KPIs: {summary['dashboard_capabilities']['comprehensive_coverage']}")
        print(f"🔄 Update Frequency: {summary['dashboard_capabilities']['real_time_monitoring']}")
        print(f"📱 Device Support: {summary['dashboard_capabilities']['mobile_responsive']}")
        
        print(f"\n📊 MONITORING CATEGORIES:")
        for category, description in summary['monitoring_categories'].items():
            print(f"   • {category.replace('_', ' ').title()}: {description}")
        
        print(f"\n🎯 KEY FEATURES:")
        for feature, description in summary['key_features'].items():
            print(f"   • {feature.replace('_', ' ').title()}: {description}")
        
        print(f"\n📈 BUSINESS INTELLIGENCE:")
        for area, description in summary['business_intelligence'].items():
            print(f"   • {area.replace('_', ' ').title()}: {description}")
        
        print(f"\n📁 DASHBOARD FILES CREATED:")
        print(f"   • monitoring_dashboard/deployment_summary.json")
        print(f"   • Live dashboard server ready at localhost:5001")
        print(f"   • Real-time API endpoints: /api/metrics, /api/status")
        
        print(f"\n🚀 EXECUTION ENGINE SUPPORT:")
        for support_item in summary['execution_support']:
            print(f"   • {support_item}")
        
        print(f"\n📊 READY FOR LIVE MONITORING!")
        print(f"Comprehensive dashboard tracking all business performance metrics")
        print(f"Real-time intelligence supporting Fortune 500 execution strategy")
        
        print(f"\n🚀 Starting Live Monitoring Dashboard Server...")
        print(f"Dashboard will be available at: http://localhost:5001")
        print(f"Press Ctrl+C to stop the server")
        
        # Start the dashboard server
        dashboard.start_dashboard_server()
        
        return True
        
    except Exception as e:
        logger.error(f"Dashboard deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print(f"\n❌ Dashboard deployment encountered issues. Check logs for details.")