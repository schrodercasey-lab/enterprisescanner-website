/**
 * Enterprise Scanner Analytics Dashboard JavaScript
 * Real-time cybersecurity analytics and visualization for Fortune 500 enterprises
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.currentTimeRange = '7d';
        this.currentIndustry = 'financial';
        this.refreshInterval = null;
        this.threatFeedInterval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadThreatFeed();
        this.startAutoRefresh();
        this.trackPageView();
    }

    setupEventListeners() {
        // Time range selector
        document.getElementById('time-range').addEventListener('change', (e) => {
            this.currentTimeRange = e.target.value;
            this.refreshAllCharts();
        });

        // Refresh button
        document.getElementById('refresh-data').addEventListener('click', () => {
            this.refreshAllData();
        });

        // Export button
        document.getElementById('export-report').addEventListener('click', () => {
            this.exportDashboard();
        });

        // Industry selector
        document.getElementById('industry-selector').addEventListener('change', (e) => {
            this.currentIndustry = e.target.value;
            this.updateIndustryBenchmark();
        });

        // Chart type buttons
        document.querySelectorAll('[data-chart-type]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chartType = e.target.dataset.chartType;
                this.switchThreatChart(chartType);
                
                // Update active state
                e.target.parentElement.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Quick action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleQuickAction(e.target.closest('.action-btn'));
            });
        });
    }

    initializeCharts() {
        this.createThreatLandscapeChart();
        this.createSecurityTrendChart();
        this.createIndustryBenchmarkChart();
        this.updateMetrics();
    }

    createThreatLandscapeChart() {
        const ctx = document.getElementById('threat-landscape-chart').getContext('2d');
        
        this.charts.threatLandscape = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(),
                datasets: [{
                    label: 'Critical Threats',
                    data: this.generateThreatData('critical'),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'High Threats',
                    data: this.generateThreatData('high'),
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Medium Threats',
                    data: this.generateThreatData('medium'),
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#1e3c72',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            beginAtZero: true
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    createSecurityTrendChart() {
        const ctx = document.getElementById('security-trend-chart').getContext('2d');
        
        this.charts.securityTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(),
                datasets: [{
                    label: 'Security Score',
                    data: this.generateSecurityScoreData(),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#28a745',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#28a745',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                return `Security Score: ${context.parsed.y}/100`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        min: 60,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: (value) => `${value}%`
                        }
                    }
                }
            }
        });
    }

    createIndustryBenchmarkChart() {
        const ctx = document.getElementById('industry-benchmark-chart').getContext('2d');
        
        this.charts.industryBenchmark = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'Threat Detection',
                    'Incident Response',
                    'Compliance',
                    'Data Protection',
                    'Access Control',
                    'Security Training',
                    'Risk Management',
                    'Monitoring'
                ],
                datasets: [{
                    label: 'Your Organization',
                    data: [87, 92, 94, 89, 85, 78, 91, 88],
                    borderColor: '#1e3c72',
                    backgroundColor: 'rgba(30, 60, 114, 0.2)',
                    pointBackgroundColor: '#1e3c72',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                }, {
                    label: 'Industry Average',
                    data: [75, 78, 82, 76, 74, 68, 79, 77],
                    borderColor: '#6c757d',
                    backgroundColor: 'rgba(108, 117, 125, 0.1)',
                    pointBackgroundColor: '#6c757d',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                }, {
                    label: 'Industry Leaders',
                    data: [95, 96, 98, 94, 92, 89, 97, 94],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    pointBackgroundColor: '#28a745',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: ${context.parsed.r}%`;
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        pointLabels: {
                            font: {
                                size: 12
                            }
                        },
                        ticks: {
                            beginAtZero: true,
                            max: 100,
                            stepSize: 20,
                            callback: (value) => `${value}%`
                        }
                    }
                }
            }
        });
    }

    generateTimeLabels() {
        const labels = [];
        const range = this.currentTimeRange;
        let count, unit;

        switch (range) {
            case '24h':
                count = 24;
                unit = 'hour';
                break;
            case '7d':
                count = 7;
                unit = 'day';
                break;
            case '30d':
                count = 30;
                unit = 'day';
                break;
            case '90d':
                count = 12;
                unit = 'week';
                break;
            default:
                count = 7;
                unit = 'day';
        }

        for (let i = count - 1; i >= 0; i--) {
            const date = new Date();
            if (unit === 'hour') {
                date.setHours(date.getHours() - i);
                labels.push(date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
            } else if (unit === 'day') {
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString([], { month: 'short', day: 'numeric' }));
            } else if (unit === 'week') {
                date.setDate(date.getDate() - (i * 7));
                labels.push(`Week ${Math.ceil((new Date() - date) / (7 * 24 * 60 * 60 * 1000))}`);
            }
        }

        return labels;
    }

    generateThreatData(severity) {
        const baseValues = {
            'critical': { min: 0, max: 5, trend: -0.1 },
            'high': { min: 5, max: 15, trend: -0.2 },
            'medium': { min: 10, max: 25, trend: 0.1 }
        };

        const config = baseValues[severity];
        const labels = this.generateTimeLabels();
        const data = [];

        for (let i = 0; i < labels.length; i++) {
            const base = config.min + Math.random() * (config.max - config.min);
            const trendEffect = config.trend * i;
            const randomVariation = (Math.random() - 0.5) * 3;
            
            data.push(Math.max(0, Math.round(base + trendEffect + randomVariation)));
        }

        return data;
    }

    generateSecurityScoreData() {
        const labels = this.generateTimeLabels();
        const data = [];
        let baseScore = 82;

        for (let i = 0; i < labels.length; i++) {
            const improvement = 0.3 * i; // Gradual improvement
            const randomVariation = (Math.random() - 0.5) * 2;
            const score = Math.min(100, Math.max(60, baseScore + improvement + randomVariation));
            
            data.push(Math.round(score));
        }

        return data;
    }

    loadThreatFeed() {
        const threatFeed = document.getElementById('threat-feed');
        const threats = this.generateThreatFeedData();
        
        threatFeed.innerHTML = threats.map(threat => `
            <div class="threat-item">
                <div class="threat-severity ${threat.severity}"></div>
                <div class="threat-content">
                    <h6>${threat.title}</h6>
                    <p>${threat.description}</p>
                    <div class="threat-time">${threat.time}</div>
                </div>
            </div>
        `).join('');
    }

    generateThreatFeedData() {
        const threatTemplates = [
            {
                title: 'Suspicious Login Attempt Detected',
                description: 'Multiple failed authentication attempts from unusual geographic location',
                severity: 'medium',
                category: 'authentication'
            },
            {
                title: 'Critical Vulnerability Identified',
                description: 'CVE-2023-XXXX detected in production web server - immediate patch required',
                severity: 'high',
                category: 'vulnerability'
            },
            {
                title: 'Malware Signature Updated',
                description: 'New ransomware variant signatures added to threat database',
                severity: 'low',
                category: 'malware'
            },
            {
                title: 'Data Exfiltration Attempt Blocked',
                description: 'Automated system blocked suspicious outbound data transfer',
                severity: 'high',
                category: 'data_protection'
            },
            {
                title: 'Compliance Scan Completed',
                description: 'Automated NIST framework compliance check finished - 3 issues found',
                severity: 'medium',
                category: 'compliance'
            },
            {
                title: 'Phishing Campaign Detected',
                description: 'Coordinated phishing emails targeting finance department',
                severity: 'high',
                category: 'email_security'
            }
        ];

        return threatTemplates.map((template, index) => ({
            ...template,
            time: this.getRelativeTime(index * 15) // Stagger times
        })).slice(0, 5); // Limit to 5 items
    }

    getRelativeTime(minutesAgo) {
        if (minutesAgo < 1) return 'Just now';
        if (minutesAgo < 60) return `${minutesAgo} minutes ago`;
        
        const hoursAgo = Math.floor(minutesAgo / 60);
        if (hoursAgo < 24) return `${hoursAgo} hour${hoursAgo > 1 ? 's' : ''} ago`;
        
        const daysAgo = Math.floor(hoursAgo / 24);
        return `${daysAgo} day${daysAgo > 1 ? 's' : ''} ago`;
    }

    updateMetrics() {
        // Simulate real-time metric updates
        const metrics = {
            securityScore: 87 + Math.round((Math.random() - 0.5) * 4),
            activeThreats: 23 + Math.round((Math.random() - 0.5) * 6),
            complianceScore: 94 + Math.round((Math.random() - 0.5) * 2),
            scannedAssets: 1247 + Math.round(Math.random() * 10)
        };

        // Update DOM elements
        document.getElementById('security-score').textContent = metrics.securityScore;
        document.getElementById('active-threats').textContent = metrics.activeThreats;
        document.getElementById('compliance-score').textContent = `${metrics.complianceScore}%`;
        document.getElementById('scanned-assets').textContent = metrics.scannedAssets.toLocaleString();

        // Update trends (simplified)
        this.updateMetricTrends(metrics);
    }

    updateMetricTrends(metrics) {
        // This would normally compare with historical data
        // For demo purposes, we'll generate random trends
        const trends = [
            { element: '.metric-card:nth-child(1) .metric-trend', positive: metrics.securityScore > 85 },
            { element: '.metric-card:nth-child(2) .metric-trend', positive: metrics.activeThreats < 25 },
            { element: '.metric-card:nth-child(3) .metric-trend', positive: metrics.complianceScore > 93 },
            { element: '.metric-card:nth-child(4) .metric-trend', positive: true }
        ];

        trends.forEach(trend => {
            const element = document.querySelector(trend.element);
            if (element) {
                element.className = `metric-trend ${trend.positive ? 'positive' : 'negative'}`;
            }
        });
    }

    switchThreatChart(chartType) {
        // Update chart data based on selected type
        let newData;
        
        switch (chartType) {
            case 'vulnerabilities':
                newData = {
                    datasets: [{
                        label: 'Critical Vulnerabilities',
                        data: this.generateThreatData('critical').map(v => v * 0.7),
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'High Vulnerabilities',
                        data: this.generateThreatData('high').map(v => v * 1.2),
                        borderColor: '#fd7e14',
                        backgroundColor: 'rgba(253, 126, 20, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                };
                break;
                
            case 'incidents':
                newData = {
                    datasets: [{
                        label: 'Security Incidents',
                        data: this.generateThreatData('critical').map(v => Math.max(0, v - 2)),
                        borderColor: '#6f42c1',
                        backgroundColor: 'rgba(111, 66, 193, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Resolved Incidents',
                        data: this.generateThreatData('medium').map(v => v * 0.8),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                };
                break;
                
            default: // threats
                newData = {
                    datasets: [{
                        label: 'Critical Threats',
                        data: this.generateThreatData('critical'),
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'High Threats',
                        data: this.generateThreatData('high'),
                        borderColor: '#fd7e14',
                        backgroundColor: 'rgba(253, 126, 20, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Medium Threats',
                        data: this.generateThreatData('medium'),
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                };
        }

        this.charts.threatLandscape.data.datasets = newData.datasets;
        this.charts.threatLandscape.update();
    }

    updateIndustryBenchmark() {
        // Industry-specific benchmark data
        const industryData = {
            financial: [87, 92, 94, 89, 85, 78, 91, 88],
            healthcare: [82, 88, 96, 91, 83, 75, 87, 85],
            technology: [91, 89, 87, 93, 89, 82, 88, 92],
            retail: [79, 84, 89, 82, 78, 71, 83, 80],
            manufacturing: [76, 81, 86, 79, 75, 68, 80, 77]
        };

        const industryAverages = {
            financial: [75, 78, 82, 76, 74, 68, 79, 77],
            healthcare: [72, 75, 85, 78, 71, 65, 76, 74],
            technology: [83, 82, 79, 85, 81, 75, 81, 84],
            retail: [70, 73, 78, 72, 68, 62, 74, 71],
            manufacturing: [68, 71, 76, 69, 65, 59, 72, 69]
        };

        const leaderData = {
            financial: [95, 96, 98, 94, 92, 89, 97, 94],
            healthcare: [92, 94, 98, 95, 90, 87, 93, 91],
            technology: [97, 95, 92, 98, 94, 90, 95, 96],
            retail: [89, 91, 94, 87, 85, 82, 90, 88],
            manufacturing: [86, 89, 92, 84, 82, 79, 87, 85]
        };

        // Update chart data
        this.charts.industryBenchmark.data.datasets[0].data = industryData[this.currentIndustry];
        this.charts.industryBenchmark.data.datasets[1].data = industryAverages[this.currentIndustry];
        this.charts.industryBenchmark.data.datasets[2].data = leaderData[this.currentIndustry];
        
        this.charts.industryBenchmark.update();
    }

    refreshAllCharts() {
        // Show loading state
        Object.values(this.charts).forEach(chart => {
            chart.canvas.parentElement.classList.add('loading');
        });

        // Simulate API call delay
        setTimeout(() => {
            // Update all charts with new data
            this.charts.threatLandscape.data.labels = this.generateTimeLabels();
            this.charts.threatLandscape.data.datasets.forEach((dataset, index) => {
                const severities = ['critical', 'high', 'medium'];
                dataset.data = this.generateThreatData(severities[index]);
            });

            this.charts.securityTrend.data.labels = this.generateTimeLabels();
            this.charts.securityTrend.data.datasets[0].data = this.generateSecurityScoreData();

            // Update all charts
            Object.values(this.charts).forEach(chart => {
                chart.update();
                chart.canvas.parentElement.classList.remove('loading');
            });

            this.updateMetrics();
            this.loadThreatFeed();

            this.trackEvent('dashboard_refreshed', { timeRange: this.currentTimeRange });
        }, 1000);
    }

    refreshAllData() {
        this.refreshAllCharts();
        
        // Show success message
        const btn = document.getElementById('refresh-data');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check"></i> Updated';
        btn.classList.add('btn-success');
        btn.classList.remove('btn-outline-light');

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-light');
        }, 2000);
    }

    handleQuickAction(actionBtn) {
        const action = actionBtn.querySelector('span').textContent.trim();
        
        switch (action) {
            case 'Run Security Scan':
                this.simulateSecurityScan();
                break;
            case 'Generate Report':
                this.exportDashboard();
                break;
            case 'Configure Alerts':
                this.showConfigModal();
                break;
            case 'Schedule Training':
                this.scheduleTraining();
                break;
            case 'Contact Expert':
                window.location.href = 'mailto:sales@enterprisescanner.com?subject=Expert Consultation Request';
                break;
        }

        this.trackEvent('quick_action_clicked', { action: action });
    }

    simulateSecurityScan() {
        // Show scan progress
        const modal = this.createModal('Security Scan', 'Running comprehensive security scan...', 'scan');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                setTimeout(() => {
                    modal.hide();
                    this.refreshAllData();
                }, 1000);
            }
            
            const progressBar = modal._element.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${Math.round(progress)}%`;
            }
        }, 200);
    }

    exportDashboard() {
        // Generate export data
        const exportData = {
            timestamp: new Date().toISOString(),
            timeRange: this.currentTimeRange,
            metrics: {
                securityScore: document.getElementById('security-score').textContent,
                activeThreats: document.getElementById('active-threats').textContent,
                complianceScore: document.getElementById('compliance-score').textContent,
                scannedAssets: document.getElementById('scanned-assets').textContent
            },
            industry: this.currentIndustry
        };

        // Create downloadable file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `enterprise_scanner_dashboard_${new Date().toISOString().split('T')[0]}.json`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);

        this.trackEvent('dashboard_exported', { format: 'json', timeRange: this.currentTimeRange });
    }

    createModal(title, content, type = 'info') {
        const modalHtml = `
            <div class="modal fade" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${type === 'scan' ? `
                                <p>${content}</p>
                                <div class="progress">
                                    <div class="progress-bar" style="width: 0%">0%</div>
                                </div>
                            ` : `<p>${content}</p>`}
                        </div>
                    </div>
                </div>
            </div>
        `;

        const modalElement = document.createElement('div');
        modalElement.innerHTML = modalHtml;
        document.body.appendChild(modalElement.firstElementChild);

        const modal = new bootstrap.Modal(modalElement.firstElementChild);
        modal.show();

        // Clean up after modal is hidden
        modalElement.firstElementChild.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modalElement.firstElementChild);
        });

        return modal;
    }

    startAutoRefresh() {
        // Refresh threat feed every 30 seconds
        this.threatFeedInterval = setInterval(() => {
            this.loadThreatFeed();
        }, 30000);

        // Refresh metrics every 60 seconds
        this.refreshInterval = setInterval(() => {
            this.updateMetrics();
        }, 60000);
    }

    trackEvent(eventName, data = {}) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'analytics_dashboard',
                ...data
            });
        }

        console.log('Dashboard Event:', eventName, data);
    }

    trackPageView() {
        this.trackEvent('dashboard_viewed', {
            timeRange: this.currentTimeRange,
            industry: this.currentIndustry
        });
    }

    destroy() {
        // Clean up intervals
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        if (this.threatFeedInterval) clearInterval(this.threatFeedInterval);

        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            chart.destroy();
        });
    }
}

// Enterprise Features Implementation

// ROI Calculator Functions
function generateROIReport() {
    const revenue = document.getElementById('annual-revenue').value;
    const budget = document.getElementById('security-budget').value;
    
    const roiData = {
        annualRevenue: revenue,
        securityBudget: budget,
        estimatedSavings: '$3.2M',
        roiPercentage: '320%',
        riskReduction: '78%',
        generatedAt: new Date().toISOString()
    };
    
    // Create downloadable ROI report
    const reportContent = `
ENTERPRISE SCANNER - ROI ANALYSIS REPORT
========================================

Company Information:
- Annual Revenue: ${revenue}
- Current Security Budget: ${budget}

ROI Analysis:
- Estimated Annual Savings: $3.2M
- Return on Investment: 320%
- Risk Reduction: 78%
- Payback Period: 3.8 months

Key Benefits:
- Reduced security incidents by 67%
- Improved compliance score to 94%
- Decreased incident response time by 85%
- Enhanced threat detection accuracy by 92%

Generated: ${new Date().toLocaleString()}
    `;
    
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `Enterprise_Scanner_ROI_Report_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    // Track ROI report generation
    window.analyticsDashboard?.trackEvent('roi_report_generated', roiData);
    
    // Show success message
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check me-2"></i>Report Generated';
    btn.classList.add('btn-success');
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove('btn-success');
    }, 2000);
}

// Executive Report Generation
function generateExecutiveReport() {
    const executiveData = {
        securityScore: 87,
        threatsBlocked: 2847,
        avgResponseTime: '12 minutes',
        costAvoidance: '$3.2M',
        complianceRate: '94%',
        riskReduction: '78%'
    };
    
    // Simulate PowerPoint export
    const reportHtml = `
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Scanner - Executive Security Summary</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; border-radius: 10px; }
        .metric { display: inline-block; margin: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        .metric-value { font-size: 2em; font-weight: bold; color: #1e3c72; }
        .metric-label { color: #6c757d; }
        .summary { margin: 30px 0; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Enterprise Scanner - Executive Security Summary</h1>
        <p>Board-Ready Cybersecurity Report | ${new Date().toLocaleDateString()}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Overview</h2>
        <p>Your organization's cybersecurity investment has delivered exceptional results, with a <strong>78% reduction in security incidents</strong> and an estimated <strong>$3.2M in cost avoidance</strong> this quarter.</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">${executiveData.securityScore}</div>
            <div class="metric-label">Security Score</div>
        </div>
        <div class="metric">
            <div class="metric-value">${executiveData.threatsBlocked.toLocaleString()}</div>
            <div class="metric-label">Threats Blocked</div>
        </div>
        <div class="metric">
            <div class="metric-value">${executiveData.avgResponseTime}</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        <div class="metric">
            <div class="metric-value">${executiveData.costAvoidance}</div>
            <div class="metric-label">Cost Avoidance</div>
        </div>
    </div>
    
    <div class="summary">
        <h2>Strategic Recommendations</h2>
        <ul>
            <li>Continue zero-trust architecture implementation (67% complete)</li>
            <li>Enhance employee security training program (target: 95% completion)</li>
            <li>Schedule quarterly penetration testing assessments</li>
        </ul>
    </div>
</body>
</html>
    `;
    
    const blob = new Blob([reportHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `Executive_Security_Report_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    window.analyticsDashboard?.trackEvent('executive_report_generated', executiveData);
    
    // Show success notification
    showNotification('Executive report generated successfully!', 'success');
}

// Schedule Executive Briefing
function scheduleExecutiveBriefing() {
    const calendarEvent = {
        title: 'Enterprise Scanner - Executive Security Briefing',
        description: 'Quarterly cybersecurity posture review with CISO and executive team',
        duration: '60 minutes',
        attendees: 'C-Suite, CISO, IT Leadership'
    };
    
    // Create calendar file
    const calendarContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Enterprise Scanner//Executive Briefing//EN
BEGIN:VEVENT
UID:${Date.now()}@enterprisescanner.com
DTSTAMP:${new Date().toISOString().replace(/[-:]/g, '').split('.')[0]}Z
DTSTART:${new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().replace(/[-:]/g, '').split('.')[0]}Z
DTEND:${new Date(Date.now() + 7 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString().replace(/[-:]/g, '').split('.')[0]}Z
SUMMARY:${calendarEvent.title}
DESCRIPTION:${calendarEvent.description}
LOCATION:Executive Conference Room / Virtual Meeting
END:VEVENT
END:VCALENDAR`;
    
    const blob = new Blob([calendarContent], { type: 'text/calendar' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'Executive_Security_Briefing.ics';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showNotification('Executive briefing scheduled! Calendar invite downloaded.', 'info');
}

// Advanced Action Functions
function initiateSecurityScan() {
    // Redirect to live security assessment tool
    window.open('security-assessment.html', '_blank');
    window.analyticsDashboard?.trackEvent('security_scan_initiated', { source: 'analytics_dashboard' });
}

function generateRiskReport() {
    const riskData = {
        criticalRisks: 2,
        highRisks: 7,
        mediumRisks: 14,
        lowRisks: 23,
        businessImpact: '$4.8M potential',
        riskScore: 'Medium',
        recommendations: [
            'Address SSL certificate expiration (7 days)',
            'Update 15 critical security patches',
            'Review access control policies (23 accounts)'
        ]
    };
    
    const riskReportHtml = `
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Scanner - Risk Assessment Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #dc3545; color: white; padding: 20px; border-radius: 8px; }
        .risk-matrix { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }
        .risk-item { padding: 15px; border-radius: 6px; text-align: center; font-weight: bold; }
        .critical { background: #dc3545; color: white; }
        .high { background: #fd7e14; color: white; }
        .medium { background: #ffc107; color: black; }
        .low { background: #28a745; color: white; }
        .recommendations { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Enterprise Scanner - Risk Assessment Report</h1>
        <p>Comprehensive Security Risk Analysis | ${new Date().toLocaleDateString()}</p>
    </div>
    
    <h2>Risk Distribution</h2>
    <div class="risk-matrix">
        <div class="risk-item critical">Critical: ${riskData.criticalRisks}</div>
        <div class="risk-item high">High: ${riskData.highRisks}</div>
        <div class="risk-item medium">Medium: ${riskData.mediumRisks}</div>
        <div class="risk-item low">Low: ${riskData.lowRisks}</div>
    </div>
    
    <h2>Business Impact Analysis</h2>
    <p><strong>Potential Financial Impact:</strong> ${riskData.businessImpact}</p>
    <p><strong>Overall Risk Score:</strong> ${riskData.riskScore}</p>
    
    <div class="recommendations">
        <h2>Immediate Action Items</h2>
        <ul>
            ${riskData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    </div>
</body>
</html>
    `;
    
    const blob = new Blob([riskReportHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `Risk_Assessment_Report_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showNotification('Risk assessment report generated!', 'warning');
}

function scheduleExpertConsultation() {
    // Open contact form or calendar booking
    window.open('mailto:sales@enterprisescanner.com?subject=Expert Consultation Request&body=I would like to schedule a consultation with a cybersecurity expert to discuss our security posture and recommendations.', '_blank');
    window.analyticsDashboard?.trackEvent('expert_consultation_requested');
}

function configureAlerts() {
    const alertModal = document.createElement('div');
    alertModal.innerHTML = `
        <div class="modal fade" id="alertsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">🔔 Configure Security Alerts</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert-config">
                            <h6>Critical Alerts</h6>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="criticalThreats" checked>
                                <label class="form-check-label" for="criticalThreats">Critical security threats detected</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="sslExpiry" checked>
                                <label class="form-check-label" for="sslExpiry">SSL certificate expiration warnings</label>
                            </div>
                            
                            <h6 class="mt-3">High Priority Alerts</h6>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="vulnPatches" checked>
                                <label class="form-check-label" for="vulnPatches">Critical vulnerability patches available</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="complianceIssues">
                                <label class="form-check-label" for="complianceIssues">Compliance framework violations</label>
                            </div>
                            
                            <h6 class="mt-3">Notification Settings</h6>
                            <div class="row">
                                <div class="col-md-6">
                                    <label for="emailNotifications">Email Notifications</label>
                                    <input type="email" class="form-control" id="emailNotifications" placeholder="security@company.com">
                                </div>
                                <div class="col-md-6">
                                    <label for="alertFrequency">Alert Frequency</label>
                                    <select class="form-select" id="alertFrequency">
                                        <option value="immediate">Immediate</option>
                                        <option value="hourly">Hourly Summary</option>
                                        <option value="daily">Daily Digest</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="saveAlertConfig()">Save Configuration</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(alertModal);
    const modal = new bootstrap.Modal(document.getElementById('alertsModal'));
    modal.show();
    
    // Clean up after modal is hidden
    document.getElementById('alertsModal').addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(alertModal);
    });
}

function saveAlertConfig() {
    const config = {
        criticalThreats: document.getElementById('criticalThreats').checked,
        sslExpiry: document.getElementById('sslExpiry').checked,
        vulnPatches: document.getElementById('vulnPatches').checked,
        complianceIssues: document.getElementById('complianceIssues').checked,
        email: document.getElementById('emailNotifications').value,
        frequency: document.getElementById('alertFrequency').value
    };
    
    // Save configuration (would normally send to API)
    localStorage.setItem('enterpriseScanner_alertConfig', JSON.stringify(config));
    
    showNotification('Alert configuration saved successfully!', 'success');
    bootstrap.Modal.getInstance(document.getElementById('alertsModal')).hide();
}

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Demo data loading function
function loadDemoData(industry) {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.currentIndustry = industry;
        window.analyticsDashboard.updateIndustryBenchmark();
        window.analyticsDashboard.refreshAllData();
        
        // Update dropdown text
        const dropdown = document.querySelector('.nav-link.dropdown-toggle');
        dropdown.innerHTML = `<i class="bi bi-person-circle"></i> ${industry.charAt(0).toUpperCase() + industry.slice(1)} Demo`;
        
        showNotification(`Loaded ${industry} industry demo data`, 'info');
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsDashboard = new AnalyticsDashboard();
});

// Clean up before page unload
window.addEventListener('beforeunload', () => {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.destroy();
    }
});