/**
 * Simple CRM Dashboard JavaScript
 * Works with the simple_server.py backend
 */

// API Configuration
const API_BASE = 'http://localhost:5000';

// Global state
let allLeads = [];
let currentFilter = 'all';

// Fortune 500 domains for detection
const FORTUNE_500_DOMAINS = [
    'microsoft.com', 'apple.com', 'amazon.com', 'google.com', 'jpmorgan.com',
    'berkshirehathaway.com', 'unitedhealth.com', 'mckesson.com', 'cvs.com',
    'walmart.com', 'exxonmobil.com', 'att.com', 'verizon.com', 'chevron.com',
    'ford.com', 'gm.com', 'citigroup.com', 'fanniemae.com', 'homedepot.com'
];

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 CRM Dashboard initializing...');
    loadDashboardData();
    initializeCharts();
});

/**
 * Load all dashboard data
 */
async function loadDashboardData() {
    try {
        console.log('📊 Loading dashboard data...');
        
        const response = await fetch(`${API_BASE}/api/leads`);
        const data = await response.json();
        
        allLeads = data.leads || [];
        console.log(`✅ Loaded ${allLeads.length} leads`);
        
        updateStatistics();
        updateLeadsTable(allLeads);
        updateCharts();
        
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        showError('Failed to load dashboard data. Make sure the backend server is running.');
    }
}

/**
 * Update statistics cards
 */
function updateStatistics() {
    const totalLeads = allLeads.length;
    
    const fortune500Count = allLeads.filter(lead => 
        isFortune500Email(lead.email)
    ).length;
    
    const avgScore = totalLeads > 0 
        ? Math.round(allLeads.reduce((sum, lead) => sum + (lead.lead_score || 0), 0) / totalLeads)
        : 0;
    
    const pipelineValue = allLeads.reduce((sum, lead) => {
        return sum + (lead.estimated_deal_value || 50000);
    }, 0);
    
    document.getElementById('total-leads').textContent = totalLeads;
    document.getElementById('fortune500-leads').textContent = fortune500Count;
    document.getElementById('avg-score').textContent = avgScore;
    document.getElementById('pipeline-value').textContent = formatCurrency(pipelineValue);
}

/**
 * Update leads table
 */
function updateLeadsTable(leads) {
    const tbody = document.getElementById('leads-table-body');
    const leadsCount = document.getElementById('leads-count');
    
    if (leads.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: #666;">
                    <i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.3;"></i>
                    <div style="margin-top: 15px;">No leads found</div>
                </td>
            </tr>
        `;
        leadsCount.textContent = 'No leads';
        return;
    }
    
    leadsCount.textContent = `${leads.length} lead${leads.length !== 1 ? 's' : ''}`;
    
    tbody.innerHTML = leads.map(lead => {
        const isFortune500 = isFortune500Email(lead.email);
        const scoreClass = getScoreClass(lead.lead_score || 0);
        const statusClass = getStatusClass(lead.lead_status || 'new');
        
        return `
            <tr onclick="viewLeadDetail(${lead.id})">
                <td>
                    <strong>${escapeHtml(lead.first_name)} ${escapeHtml(lead.last_name)}</strong>
                    ${isFortune500 ? '<br><span class="fortune-badge"><i class="bi bi-star-fill"></i> F500</span>' : ''}
                </td>
                <td>${escapeHtml(lead.company_name || 'N/A')}</td>
                <td>${escapeHtml(lead.email)}</td>
                <td>${escapeHtml(lead.job_title || 'N/A')}</td>
                <td><span class="badge bg-secondary">${escapeHtml(lead.lead_source || 'website')}</span></td>
                <td><span class="status-badge status-${statusClass}">${escapeHtml(lead.lead_status || 'new')}</span></td>
                <td><span class="lead-score score-${scoreClass}">${lead.lead_score || 0}</span></td>
                <td>${formatDate(lead.created_at)}</td>
                <td onclick="event.stopPropagation()">
                    <button class="action-btn btn btn-sm btn-primary" onclick="viewLeadDetail(${lead.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="action-btn btn btn-sm btn-success" onclick="contactLead(${lead.id})">
                        <i class="bi bi-envelope"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Filter leads
 */
function filterLeads(filterType) {
    currentFilter = filterType;
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    let filteredLeads = [...allLeads];
    
    switch(filterType) {
        case 'new':
            filteredLeads = allLeads.filter(l => l.lead_status === 'new');
            break;
        case 'contacted':
            filteredLeads = allLeads.filter(l => l.lead_status === 'contacted');
            break;
        case 'qualified':
            filteredLeads = allLeads.filter(l => l.lead_status === 'qualified');
            break;
        case 'fortune500':
            filteredLeads = allLeads.filter(l => isFortune500Email(l.email));
            break;
        case 'high-score':
            filteredLeads = allLeads.filter(l => (l.lead_score || 0) >= 80);
            break;
    }
    
    updateLeadsTable(filteredLeads);
}

/**
 * Search leads
 */
function searchLeads() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    if (!searchTerm) {
        filterLeads(currentFilter);
        return;
    }
    
    const searchResults = allLeads.filter(lead => {
        return (
            (lead.first_name && lead.first_name.toLowerCase().includes(searchTerm)) ||
            (lead.last_name && lead.last_name.toLowerCase().includes(searchTerm)) ||
            (lead.email && lead.email.toLowerCase().includes(searchTerm)) ||
            (lead.company_name && lead.company_name.toLowerCase().includes(searchTerm)) ||
            (lead.job_title && lead.job_title.toLowerCase().includes(searchTerm))
        );
    });
    
    updateLeadsTable(searchResults);
}

/**
 * View lead detail modal
 */
function viewLeadDetail(leadId) {
    const lead = allLeads.find(l => l.id === leadId);
    if (!lead) return;
    
    const isFortune500 = isFortune500Email(lead.email);
    
    const modalBody = document.getElementById('lead-detail-body');
    modalBody.innerHTML = `
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label"><strong>First Name</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.first_name)}" readonly>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Last Name</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.last_name)}" readonly>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Email</strong></label>
                <input type="email" class="form-control" value="${escapeHtml(lead.email)}" readonly>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Phone</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.phone || 'N/A')}" readonly>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Company</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.company_name || 'N/A')}" readonly>
                ${isFortune500 ? '<br><span class="fortune-badge mt-2"><i class="bi bi-star-fill"></i> Fortune 500 Company</span>' : ''}
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Job Title</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.job_title || 'N/A')}" readonly>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Lead Status</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.lead_status || 'new')}" readonly>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Lead Score</strong></label>
                <input type="number" class="form-control" value="${lead.lead_score || 0}" readonly>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Lead Source</strong></label>
                <input type="text" class="form-control" value="${escapeHtml(lead.lead_source || 'website')}" readonly>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Created</strong></label>
                <p class="text-muted">${formatDateTime(lead.created_at)}</p>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Lead ID</strong></label>
                <p class="text-muted">#${lead.id}</p>
            </div>
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('leadModal'));
    modal.show();
}

/**
 * Contact lead (open email)
 */
function contactLead(leadId) {
    const lead = allLeads.find(l => l.id === leadId);
    if (!lead) return;
    
    const subject = encodeURIComponent(`Enterprise Scanner - Security Assessment Follow-up`);
    const body = encodeURIComponent(`Hi ${lead.first_name},\n\nThank you for your interest in Enterprise Scanner...\n\nBest regards,\nEnterprise Scanner Team`);
    
    window.location.href = `mailto:${lead.email}?subject=${subject}&body=${body}`;
}

/**
 * Export leads to CSV
 */
function exportToCSV() {
    if (allLeads.length === 0) {
        showError('No leads to export');
        return;
    }
    
    const headers = ['ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Company', 'Job Title', 'Status', 'Score', 'Source', 'Created Date'];
    const rows = allLeads.map(lead => [
        lead.id,
        lead.first_name,
        lead.last_name,
        lead.email,
        lead.phone || '',
        lead.company_name || '',
        lead.job_title || '',
        lead.lead_status || 'new',
        lead.lead_score || 0,
        lead.lead_source || 'website',
        lead.created_at
    ]);
    
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `enterprise-scanner-leads-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    showSuccess(`Exported ${allLeads.length} leads to CSV`);
}

/**
 * Refresh dashboard
 */
function refreshDashboard() {
    console.log('🔄 Refreshing dashboard...');
    loadDashboardData();
    showSuccess('Dashboard refreshed!');
}

/**
 * Initialize charts
 */
let leadsChart, sourcesChart;

function initializeCharts() {
    const leadsCtx = document.getElementById('leads-chart');
    if (leadsCtx) {
        leadsChart = new Chart(leadsCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Leads',
                    data: [12, 19, 15, 25, 22, 30, 28],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
    
    const sourcesCtx = document.getElementById('sources-chart');
    if (sourcesCtx) {
        sourcesChart = new Chart(sourcesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Website', 'Assessment', 'Partner Portal', 'Direct'],
                datasets: [{
                    data: [45, 30, 15, 10],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * Update charts with real data
 */
function updateCharts() {
    const sourceCount = {};
    allLeads.forEach(lead => {
        const source = lead.lead_source || 'website';
        sourceCount[source] = (sourceCount[source] || 0) + 1;
    });
    
    if (sourcesChart && Object.keys(sourceCount).length > 0) {
        sourcesChart.data.labels = Object.keys(sourceCount);
        sourcesChart.data.datasets[0].data = Object.values(sourceCount);
        sourcesChart.update();
    }
}

/**
 * Utility Functions
 */
function isFortune500Email(email) {
    if (!email) return false;
    const domain = email.split('@')[1]?.toLowerCase();
    return FORTUNE_500_DOMAINS.includes(domain);
}

function getScoreClass(score) {
    if (score >= 80) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

function getStatusClass(status) {
    return status.toLowerCase().replace(' ', '-');
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-check-circle me-2"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    setTimeout(() => toast.remove(), 3000);
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-exclamation-circle me-2"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    setTimeout(() => toast.remove(), 5000);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '../index.html';
    }
}
