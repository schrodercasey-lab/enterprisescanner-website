// CRM Dashboard JavaScript
class CRMDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.leads = [];
        this.charts = {};
        this.filters = {
            status: '',
            companyType: '',
            dealValue: '',
            assignedTo: ''
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.initializeCharts();
        this.setupDragAndDrop();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('href').substring(1);
                this.showSection(section);
            });
        });

        // Sidebar filters
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.applyFilters();
        });

        document.getElementById('companyTypeFilter').addEventListener('change', (e) => {
            this.filters.companyType = e.target.value;
            this.applyFilters();
        });

        document.getElementById('dealValueFilter').addEventListener('change', (e) => {
            this.filters.dealValue = e.target.value;
            this.applyFilters();
        });

        document.getElementById('assignedToFilter').addEventListener('change', (e) => {
            this.filters.assignedTo = e.target.value;
            this.applyFilters();
        });

        // Quick actions
        document.getElementById('addLeadBtn').addEventListener('click', () => {
            this.showAddLeadModal();
        });

        document.getElementById('addLeadModalBtn').addEventListener('click', () => {
            this.showAddLeadModal();
        });

        document.getElementById('importLeadsBtn').addEventListener('click', () => {
            this.importLeads();
        });

        document.getElementById('scheduleFollowUpBtn').addEventListener('click', () => {
            this.scheduleFollowUp();
        });

        // Dashboard actions
        document.getElementById('refreshDashboard').addEventListener('click', () => {
            this.refreshDashboard();
        });

        document.getElementById('exportReportBtn').addEventListener('click', () => {
            this.exportReport();
        });

        // Lead search
        document.getElementById('leadSearch').addEventListener('input', (e) => {
            this.searchLeads(e.target.value);
        });

        // Add lead form
        document.getElementById('addLeadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addLead();
        });

        // Pipeline view selector
        document.getElementById('pipelineViewSelect').addEventListener('change', (e) => {
            this.changePipelineView(e.target.value);
        });

        // Chart time range selectors
        document.getElementById('pipelineTimeRange').addEventListener('change', (e) => {
            this.updatePipelineChart(e.target.value);
        });

        document.getElementById('analyticsTimeRange').addEventListener('change', (e) => {
            this.updateAnalyticsCharts(e.target.value);
        });

        // Forecast controls
        document.querySelectorAll('[data-forecast]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('[data-forecast]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateForecastChart(e.target.dataset.forecast);
            });
        });

        // Generate report
        document.getElementById('generateReportBtn').addEventListener('click', () => {
            this.generateAnalyticsReport();
        });
    }

    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.style.display = 'none';
        });

        // Show selected section
        document.getElementById(section).style.display = 'block';

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[href="#${section}"]`).classList.add('active');

        this.currentSection = section;

        // Load section-specific data
        switch(section) {
            case 'leads':
                this.loadLeads();
                break;
            case 'pipeline':
                this.loadPipeline();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }

    loadInitialData() {
        // Load sample data for demonstration
        this.leads = this.generateSampleLeads();
        this.loadDashboardData();
        this.loadRecentActivity();
        this.loadTopOpportunities();
    }

    generateSampleLeads() {
        const companies = [
            'Microsoft Corporation', 'Apple Inc.', 'Amazon.com Inc.', 'Alphabet Inc.',
            'Meta Platforms Inc.', 'Tesla Inc.', 'Berkshire Hathaway', 'NVIDIA Corporation',
            'JPMorgan Chase & Co.', 'Johnson & Johnson', 'Visa Inc.', 'Procter & Gamble',
            'Mastercard Inc.', 'UnitedHealth Group', 'Home Depot Inc.', 'Bank of America',
            'Pfizer Inc.', 'Coca-Cola Company', 'PepsiCo Inc.', 'Walt Disney Company'
        ];

        const titles = [
            'Chief Information Security Officer', 'IT Director', 'Security Manager',
            'Chief Technology Officer', 'VP of Information Technology', 'Security Analyst',
            'IT Security Specialist', 'Cybersecurity Manager', 'Chief Information Officer',
            'Network Security Manager', 'Information Security Manager', 'IT Manager'
        ];

        const statuses = ['new', 'contacted', 'qualified', 'demo_scheduled', 'proposal_sent', 'closed_won', 'closed_lost'];
        const sources = ['website', 'partner', 'referral', 'advertisement', 'cold_outreach'];

        const leads = [];
        for (let i = 0; i < 50; i++) {
            const firstName = this.generateRandomName();
            const lastName = this.generateRandomName();
            const company = companies[Math.floor(Math.random() * companies.length)];
            const title = titles[Math.floor(Math.random() * titles.length)];
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            const source = sources[Math.floor(Math.random() * sources.length)];
            const dealValue = Math.floor(Math.random() * 2000000) + 50000;
            const score = Math.floor(Math.random() * 100) + 1;

            leads.push({
                id: i + 1,
                firstName,
                lastName,
                email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${company.toLowerCase().replace(/[^a-z0-9]/g, '')}.com`,
                phone: this.generateRandomPhone(),
                company,
                title,
                status,
                source,
                dealValue,
                score,
                createdDate: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000),
                lastContact: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
                nextFollowUp: new Date(Date.now() + Math.random() * 14 * 24 * 60 * 60 * 1000),
                notes: 'Initial contact via website form submission.'
            });
        }

        return leads;
    }

    generateRandomName() {
        const names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Mary',
            'James', 'Patricia', 'William', 'Jennifer', 'Richard', 'Elizabeth',
            'Joseph', 'Linda', 'Thomas', 'Barbara', 'Christopher', 'Susan'
        ];
        return names[Math.floor(Math.random() * names.length)];
    }

    generateRandomPhone() {
        const area = Math.floor(Math.random() * 900) + 100;
        const first = Math.floor(Math.random() * 900) + 100;
        const second = Math.floor(Math.random() * 9000) + 1000;
        return `+1 (${area}) ${first}-${second}`;
    }

    loadDashboardData() {
        // Update KPI cards
        document.getElementById('totalLeads').textContent = this.leads.length.toLocaleString();
        document.getElementById('qualifiedLeads').textContent = this.leads.filter(l => ['qualified', 'demo_scheduled', 'proposal_sent'].includes(l.status)).length;
        document.getElementById('closedDeals').textContent = this.leads.filter(l => l.status === 'closed_won').length;
        
        const totalRevenue = this.leads
            .filter(l => l.status === 'closed_won')
            .reduce((sum, l) => sum + l.dealValue, 0);
        document.getElementById('totalRevenue').textContent = `$${(totalRevenue / 1000000).toFixed(1)}M`;
    }

    loadRecentActivity() {
        const activityContainer = document.getElementById('recentActivity');
        const activities = [
            {
                type: 'new-lead',
                icon: 'fas fa-user-plus',
                title: 'New lead from Microsoft',
                description: 'Sarah Johnson submitted security assessment request',
                time: '2 hours ago'
            },
            {
                type: 'email-sent',
                icon: 'fas fa-envelope',
                title: 'Follow-up email sent',
                description: 'Sent demo invitation to Amazon CISO',
                time: '4 hours ago'
            },
            {
                type: 'meeting-scheduled',
                icon: 'fas fa-calendar',
                title: 'Demo scheduled',
                description: 'Security assessment demo with Apple team',
                time: '1 day ago'
            },
            {
                type: 'deal-closed',
                icon: 'fas fa-handshake',
                title: 'Deal closed',
                description: 'Tesla signed $1.2M security contract',
                time: '2 days ago'
            }
        ];

        activityContainer.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <h6>${activity.title}</h6>
                    <p>${activity.description}</p>
                    <div class="activity-time">${activity.time}</div>
                </div>
            </div>
        `).join('');
    }

    loadTopOpportunities() {
        const opportunitiesContainer = document.getElementById('topOpportunities');
        const opportunities = this.leads
            .filter(l => ['qualified', 'demo_scheduled', 'proposal_sent'].includes(l.status))
            .sort((a, b) => b.dealValue - a.dealValue)
            .slice(0, 5);

        opportunitiesContainer.innerHTML = opportunities.map(opp => `
            <div class="opportunity-item">
                <div class="opportunity-info">
                    <h6>${opp.firstName} ${opp.lastName}</h6>
                    <p>${opp.company} • ${opp.title}</p>
                </div>
                <div class="opportunity-value">
                    <span class="amount">$${(opp.dealValue / 1000).toFixed(0)}K</span>
                    <span class="probability">${this.getStatusProbability(opp.status)}% probability</span>
                </div>
            </div>
        `).join('');
    }

    getStatusProbability(status) {
        const probabilities = {
            'new': 10,
            'contacted': 25,
            'qualified': 50,
            'demo_scheduled': 70,
            'proposal_sent': 85,
            'closed_won': 100,
            'closed_lost': 0
        };
        return probabilities[status] || 0;
    }

    initializeCharts() {
        this.initializePipelineChart();
        this.initializeLeadSourceChart();
        this.initializeAnalyticsCharts();
        this.initializeForecastChart();
    }

    initializePipelineChart() {
        const ctx = document.getElementById('pipelineChart').getContext('2d');
        const statusCounts = this.getStatusCounts();

        this.charts.pipeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'New Leads',
                    data: [65, 59, 80, 81, 56, 85],
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Qualified',
                    data: [28, 48, 40, 39, 46, 47],
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Closed Won',
                    data: [18, 24, 28, 32, 35, 42],
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initializeLeadSourceChart() {
        const ctx = document.getElementById('leadSourceChart').getContext('2d');
        const sourceCounts = this.getSourceCounts();

        this.charts.leadSource = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(sourceCounts),
                datasets: [{
                    data: Object.values(sourceCounts),
                    backgroundColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initializeAnalyticsCharts() {
        // Conversion Rate Chart
        const conversionCtx = document.getElementById('conversionChart').getContext('2d');
        this.charts.conversion = new Chart(conversionCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    data: [22.4, 23.1, 24.5, 24.5],
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });

        // Deal Size Chart
        const dealSizeCtx = document.getElementById('dealSizeChart').getContext('2d');
        this.charts.dealSize = new Chart(dealSizeCtx, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    data: [130, 135, 140, 142],
                    backgroundColor: '#198754'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });

        // Sales Cycle Chart
        const salesCycleCtx = document.getElementById('salesCycleChart').getContext('2d');
        this.charts.salesCycle = new Chart(salesCycleCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    data: [42, 44, 43, 45],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }

    initializeForecastChart() {
        const ctx = document.getElementById('revenueForecastChart').getContext('2d');
        
        this.charts.forecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Conservative',
                    data: [2.1, 2.3, 2.8, 3.2, 3.5, 3.8, 4.1, 4.4, 4.7, 5.0, 5.3, 5.6],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Likely',
                    data: [2.1, 2.5, 3.2, 3.8, 4.5, 5.2, 5.9, 6.6, 7.3, 8.0, 8.7, 9.4],
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Optimistic',
                    data: [2.1, 2.7, 3.6, 4.5, 5.5, 6.6, 7.8, 9.1, 10.5, 12.0, 13.6, 15.3],
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value + 'M';
                            }
                        }
                    }
                }
            }
        });
    }

    getStatusCounts() {
        const counts = {};
        this.leads.forEach(lead => {
            counts[lead.status] = (counts[lead.status] || 0) + 1;
        });
        return counts;
    }

    getSourceCounts() {
        const counts = {};
        this.leads.forEach(lead => {
            const source = lead.source.charAt(0).toUpperCase() + lead.source.slice(1).replace('_', ' ');
            counts[source] = (counts[source] || 0) + 1;
        });
        return counts;
    }

    loadLeads() {
        this.renderLeadsTable();
    }

    renderLeadsTable() {
        const tbody = document.getElementById('leadsTableBody');
        const filteredLeads = this.getFilteredLeads();
        
        tbody.innerHTML = filteredLeads.map(lead => `
            <tr data-lead-id="${lead.id}">
                <td><input type="checkbox" class="lead-checkbox"></td>
                <td>
                    <span class="lead-score ${this.getScoreClass(lead.score)}">${lead.score}</span>
                </td>
                <td>
                    <strong>${lead.firstName} ${lead.lastName}</strong><br>
                    <small class="text-muted">${lead.email}</small>
                </td>
                <td>${lead.company}</td>
                <td>${lead.title}</td>
                <td>
                    <span class="status-badge ${lead.status.replace('_', '-')}">${this.formatStatus(lead.status)}</span>
                </td>
                <td>$${(lead.dealValue / 1000).toFixed(0)}K</td>
                <td>${this.formatDate(lead.lastContact)}</td>
                <td>${this.formatDate(lead.nextFollowUp)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="crmDashboard.viewLead(${lead.id})" title="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="crmDashboard.contactLead(${lead.id})" title="Contact">
                            <i class="fas fa-phone"></i>
                        </button>
                        <button class="btn btn-outline-warning" onclick="crmDashboard.editLead(${lead.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getFilteredLeads() {
        return this.leads.filter(lead => {
            if (this.filters.status && lead.status !== this.filters.status) return false;
            if (this.filters.companyType) {
                // Simple company type detection based on company name
                const isF500 = ['Microsoft', 'Apple', 'Amazon', 'Google', 'Meta', 'Tesla'].some(company => 
                    lead.company.includes(company));
                if (this.filters.companyType === 'fortune_500' && !isF500) return false;
                if (this.filters.companyType === 'enterprise' && isF500) return false;
            }
            if (this.filters.dealValue) {
                const value = lead.dealValue;
                switch(this.filters.dealValue) {
                    case '1000000+': if (value < 1000000) return false; break;
                    case '500000-1000000': if (value < 500000 || value >= 1000000) return false; break;
                    case '100000-500000': if (value < 100000 || value >= 500000) return false; break;
                    case '0-100000': if (value >= 100000) return false; break;
                }
            }
            return true;
        });
    }

    getScoreClass(score) {
        if (score >= 75) return 'high';
        if (score >= 50) return 'medium';
        return 'low';
    }

    formatStatus(status) {
        return status.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: '2-digit'
        });
    }

    applyFilters() {
        if (this.currentSection === 'leads') {
            this.renderLeadsTable();
        }
    }

    searchLeads(query) {
        // Implement lead search functionality
        console.log('Searching leads:', query);
    }

    showAddLeadModal() {
        const modal = new bootstrap.Modal(document.getElementById('addLeadModal'));
        modal.show();
    }

    addLead() {
        const form = document.getElementById('addLeadForm');
        const formData = new FormData(form);
        
        const newLead = {
            id: this.leads.length + 1,
            firstName: formData.get('firstName') || document.getElementById('leadFirstName').value,
            lastName: formData.get('lastName') || document.getElementById('leadLastName').value,
            email: formData.get('email') || document.getElementById('leadEmail').value,
            phone: formData.get('phone') || document.getElementById('leadPhone').value,
            company: formData.get('company') || document.getElementById('leadCompany').value,
            title: formData.get('title') || document.getElementById('leadTitle').value,
            source: formData.get('source') || document.getElementById('leadSource').value,
            dealValue: parseInt(formData.get('dealValue') || document.getElementById('leadDealValue').value) || 0,
            notes: formData.get('notes') || document.getElementById('leadNotes').value,
            status: 'new',
            score: Math.floor(Math.random() * 40) + 60, // Random score between 60-100 for new leads
            createdDate: new Date(),
            lastContact: null,
            nextFollowUp: new Date(Date.now() + 24 * 60 * 60 * 1000) // Tomorrow
        };

        this.leads.push(newLead);
        
        // Close modal and refresh data
        bootstrap.Modal.getInstance(document.getElementById('addLeadModal')).hide();
        form.reset();
        
        if (this.currentSection === 'leads') {
            this.renderLeadsTable();
        }
        this.loadDashboardData();
        
        // Show success message
        this.showNotification('Lead added successfully!', 'success');
    }

    viewLead(id) {
        const lead = this.leads.find(l => l.id === id);
        if (lead) {
            console.log('Viewing lead:', lead);
            // Implement lead detail modal
        }
    }

    contactLead(id) {
        const lead = this.leads.find(l => l.id === id);
        if (lead) {
            console.log('Contacting lead:', lead);
            // Implement contact functionality
        }
    }

    editLead(id) {
        const lead = this.leads.find(l => l.id === id);
        if (lead) {
            console.log('Editing lead:', lead);
            // Implement edit lead modal
        }
    }

    loadPipeline() {
        this.renderPipelineKanban();
    }

    renderPipelineKanban() {
        const stages = ['new', 'contacted', 'qualified', 'demo_scheduled', 'proposal_sent', 'closed_won'];
        
        stages.forEach(stage => {
            const stageElement = document.getElementById(`${stage === 'demo_scheduled' ? 'demo' : stage === 'proposal_sent' ? 'proposal' : stage === 'closed_won' ? 'closedWon' : stage}Stage`);
            if (!stageElement) return;
            
            const stageLeads = this.leads.filter(lead => lead.status === stage);
            
            stageElement.innerHTML = stageLeads.map(lead => `
                <div class="pipeline-card" data-lead-id="${lead.id}" draggable="true">
                    <h6>${lead.firstName} ${lead.lastName}</h6>
                    <p>${lead.company}</p>
                    <div class="card-value">$${(lead.dealValue / 1000).toFixed(0)}K</div>
                    <div class="card-date">${this.formatDate(lead.nextFollowUp)}</div>
                </div>
            `).join('');
        });
    }

    setupDragAndDrop() {
        // Initialize drag and drop for pipeline cards
        document.querySelectorAll('.stage-content').forEach(stage => {
            new Sortable(stage, {
                group: 'pipeline',
                animation: 150,
                ghostClass: 'pipeline-card-ghost',
                chosenClass: 'pipeline-card-chosen',
                dragClass: 'pipeline-card-drag',
                onEnd: (evt) => {
                    this.handlePipelineMove(evt);
                }
            });
        });
    }

    handlePipelineMove(evt) {
        const leadId = parseInt(evt.item.dataset.leadId);
        const newStage = evt.to.parentElement.dataset.stage;
        
        const lead = this.leads.find(l => l.id === leadId);
        if (lead) {
            lead.status = newStage;
            lead.lastContact = new Date();
            console.log(`Moved lead ${leadId} to ${newStage}`);
            
            // Update dashboard data
            this.loadDashboardData();
        }
    }

    changePipelineView(view) {
        console.log('Changing pipeline view to:', view);
        // Implement different pipeline views
    }

    loadAnalytics() {
        // Analytics are loaded with charts initialization
        console.log('Loading analytics data');
    }

    updatePipelineChart(timeRange) {
        console.log('Updating pipeline chart for:', timeRange);
        // Implement chart update logic
    }

    updateAnalyticsCharts(timeRange) {
        console.log('Updating analytics charts for:', timeRange);
        // Implement chart update logic
    }

    updateForecastChart(forecast) {
        console.log('Updating forecast chart for:', forecast);
        // Implement forecast update logic
    }

    refreshDashboard() {
        this.loadDashboardData();
        this.loadRecentActivity();
        this.loadTopOpportunities();
        this.showNotification('Dashboard refreshed!', 'info');
    }

    exportReport() {
        console.log('Exporting report...');
        // Implement report export functionality
        this.showNotification('Report exported successfully!', 'success');
    }

    importLeads() {
        console.log('Importing leads...');
        // Implement lead import functionality
        this.showNotification('Lead import started!', 'info');
    }

    scheduleFollowUp() {
        console.log('Scheduling follow-up...');
        // Implement follow-up scheduling
        this.showNotification('Follow-up scheduled!', 'success');
    }

    generateAnalyticsReport() {
        console.log('Generating analytics report...');
        // Implement analytics report generation
        this.showNotification('Analytics report generated!', 'success');
    }

    showNotification(message, type = 'info') {
        // Create and show notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 70px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    startAutoRefresh() {
        // Refresh dashboard every 5 minutes
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboardData();
            }
        }, 5 * 60 * 1000);
    }
}

// Initialize CRM Dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.crmDashboard = new CRMDashboard();
});

// Lead scoring algorithm
class LeadScoringEngine {
    static calculateScore(lead) {
        let score = 0;
        
        // Company size scoring
        if (lead.company && this.isFortuneCompany(lead.company)) {
            score += 40;
        } else if (lead.dealValue > 500000) {
            score += 30;
        } else if (lead.dealValue > 100000) {
            score += 20;
        } else {
            score += 10;
        }
        
        // Title scoring
        if (lead.title) {
            const title = lead.title.toLowerCase();
            if (title.includes('ciso') || title.includes('chief information security')) {
                score += 25;
            } else if (title.includes('cto') || title.includes('chief technology')) {
                score += 20;
            } else if (title.includes('director') || title.includes('manager')) {
                score += 15;
            } else {
                score += 10;
            }
        }
        
        // Engagement scoring
        if (lead.status === 'demo_scheduled') {
            score += 20;
        } else if (lead.status === 'qualified') {
            score += 15;
        } else if (lead.status === 'contacted') {
            score += 10;
        }
        
        // Source scoring
        if (lead.source === 'referral') {
            score += 15;
        } else if (lead.source === 'partner') {
            score += 10;
        } else if (lead.source === 'website') {
            score += 5;
        }
        
        return Math.min(score, 100);
    }
    
    static isFortuneCompany(company) {
        const fortuneCompanies = [
            'Microsoft', 'Apple', 'Amazon', 'Alphabet', 'Google', 'Meta', 'Tesla',
            'Berkshire Hathaway', 'NVIDIA', 'JPMorgan Chase', 'Johnson & Johnson',
            'Visa', 'Procter & Gamble', 'Mastercard', 'UnitedHealth', 'Home Depot',
            'Bank of America', 'Pfizer', 'Coca-Cola', 'PepsiCo', 'Walt Disney'
        ];
        
        return fortuneCompanies.some(fc => company.toLowerCase().includes(fc.toLowerCase()));
    }
}

// Follow-up automation
class FollowUpAutomation {
    static scheduleFollowUp(lead, days = 3) {
        const followUpDate = new Date();
        followUpDate.setDate(followUpDate.getDate() + days);
        
        lead.nextFollowUp = followUpDate;
        
        // Schedule automated email based on lead status
        this.scheduleAutomatedEmail(lead);
        
        return followUpDate;
    }
    
    static scheduleAutomatedEmail(lead) {
        const emailTemplates = {
            'new': 'welcome_email',
            'contacted': 'follow_up_email',
            'qualified': 'demo_invitation',
            'demo_scheduled': 'demo_reminder',
            'proposal_sent': 'proposal_follow_up'
        };
        
        const template = emailTemplates[lead.status] || 'generic_follow_up';
        
        console.log(`Scheduling ${template} for ${lead.email} on ${lead.nextFollowUp}`);
        
        // In a real implementation, this would integrate with an email service
        return {
            leadId: lead.id,
            template: template,
            scheduledDate: lead.nextFollowUp,
            status: 'scheduled'
        };
    }
    
    static getPersonalizedMessage(lead) {
        const templates = {
            'ciso': `Hi ${lead.firstName}, as a CISO at ${lead.company}, you understand the critical importance of comprehensive security assessments...`,
            'cto': `Hello ${lead.firstName}, technology leaders like yourself at ${lead.company} are always looking for innovative security solutions...`,
            'director': `Hi ${lead.firstName}, I know how challenging it can be to maintain security standards at ${lead.company}...`,
            'default': `Hello ${lead.firstName}, thank you for your interest in Enterprise Scanner's cybersecurity solutions...`
        };
        
        const title = lead.title ? lead.title.toLowerCase() : '';
        
        if (title.includes('ciso') || title.includes('chief information security')) {
            return templates.ciso;
        } else if (title.includes('cto') || title.includes('chief technology')) {
            return templates.cto;
        } else if (title.includes('director') || title.includes('manager')) {
            return templates.director;
        }
        
        return templates.default;
    }
}