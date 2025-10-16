/**
 * API Security Management JavaScript
 * Handles all frontend functionality for API security dashboard
 */

// Global variables
let securityData = {
    stats: {},
    apiKeys: [],
    rateLimits: [],
    securityEvents: [],
    ipWhitelist: []
};

let charts = {
    events: null,
    usage: null
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    loadSecurityData();
});

/**
 * Initialize dashboard components
 */
function initializeDashboard() {
    // Setup tab navigation
    setupTabNavigation();
    
    // Initialize charts
    initializeCharts();
    
    // Setup auto-refresh
    setInterval(refreshSecurityStats, 60000); // Refresh every minute
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('[data-tab]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Form validation
    document.getElementById('ip-address').addEventListener('input', validateIPAddress);
    
    // Filter events
    document.getElementById('event-type-filter').addEventListener('change', filterSecurityEvents);
    document.getElementById('severity-filter').addEventListener('change', filterSecurityEvents);
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
    const tabs = document.querySelectorAll('.tab-content');
    const navLinks = document.querySelectorAll('[data-tab]');
    
    // Show first tab by default
    if (tabs.length > 0) {
        tabs[0].classList.add('active');
    }
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from nav links
    document.querySelectorAll('[data-tab]').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected tab
    const targetTab = document.getElementById(`${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Add active class to nav link
    const navLink = document.querySelector(`[data-tab="${tabName}"]`);
    if (navLink) {
        navLink.classList.add('active');
    }
    
    // Load tab-specific data
    loadTabData(tabName);
}

/**
 * Load data for specific tab
 */
function loadTabData(tabName) {
    switch (tabName) {
        case 'overview':
            refreshSecurityStats();
            break;
        case 'api-keys':
            loadAPIKeys();
            break;
        case 'rate-limits':
            loadRateLimits();
            break;
        case 'security-events':
            loadSecurityEvents();
            break;
        case 'ip-whitelist':
            loadIPWhitelist();
            break;
    }
}

/**
 * Load all security data
 */
async function loadSecurityData() {
    showLoading();
    
    try {
        await Promise.all([
            refreshSecurityStats(),
            loadAPIKeys(),
            loadRateLimits(),
            loadSecurityEvents(),
            loadIPWhitelist()
        ]);
    } catch (error) {
        console.error('Failed to load security data:', error);
        showAlert('Failed to load security data', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Refresh security statistics
 */
async function refreshSecurityStats() {
    try {
        const response = await fetch('/api/security/stats', {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch security stats');
        }
        
        const data = await response.json();
        securityData.stats = data;
        
        updateSecurityMetrics(data);
        updateCharts(data);
        
        // Load recent events for overview
        const eventsResponse = await fetch('/api/security/events?limit=10', {
            headers: getAuthHeaders()
        });
        
        if (eventsResponse.ok) {
            const eventsData = await eventsResponse.json();
            updateRecentEvents(eventsData.events);
        }
        
    } catch (error) {
        console.error('Failed to refresh security stats:', error);
        showAlert('Failed to refresh security statistics', 'danger');
    }
}

/**
 * Update security metrics display
 */
function updateSecurityMetrics(data) {
    document.getElementById('security-score').textContent = data.security_score || 0;
    document.getElementById('active-keys').textContent = data.api_keys?.active || 0;
    document.getElementById('security-events').textContent = data.total_events || 0;
    document.getElementById('whitelisted-ips').textContent = data.whitelisted_ips || 0;
    
    // Update security score color
    const scoreElement = document.getElementById('security-score').parentElement;
    const score = data.security_score || 0;
    
    scoreElement.className = scoreElement.className.replace(/text-\w+/, '');
    if (score >= 90) {
        scoreElement.classList.add('text-success');
    } else if (score >= 70) {
        scoreElement.classList.add('text-info');
    } else if (score >= 50) {
        scoreElement.classList.add('text-warning');
    } else {
        scoreElement.classList.add('text-danger');
    }
}

/**
 * Initialize charts
 */
function initializeCharts() {
    // Events Chart
    const eventsCtx = document.getElementById('eventsChart').getContext('2d');
    charts.events = new Chart(eventsCtx, {
        type: 'doughnut',
        data: {
            labels: ['API Access', 'Rate Limits', 'Unauthorized', 'Malicious Input'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#27ae60',
                    '#f39c12',
                    '#e74c3c',
                    '#8b0000'
                ],
                borderWidth: 2,
                borderColor: '#fff'
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
    
    // Usage Chart
    const usageCtx = document.getElementById('usageChart').getContext('2d');
    charts.usage = new Chart(usageCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'API Requests',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Update charts with new data
 */
function updateCharts(data) {
    if (charts.events && data.event_breakdown) {
        const eventData = data.event_breakdown;
        const eventCounts = [
            (eventData.api_access?.info || 0) + (eventData.api_access?.warning || 0),
            (eventData.rate_limit_exceeded?.warning || 0) + (eventData.rate_limit_exceeded?.high || 0),
            (eventData.unauthorized_access?.warning || 0) + (eventData.unauthorized_access?.high || 0),
            (eventData.malicious_input_detected?.high || 0) + (eventData.malicious_input_detected?.critical || 0)
        ];
        
        charts.events.data.datasets[0].data = eventCounts;
        charts.events.update();
    }
    
    // Generate sample usage data for demo
    if (charts.usage) {
        const labels = [];
        const usageData = [];
        const now = new Date();
        
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
            labels.push(time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
            usageData.push(Math.floor(Math.random() * 100) + 50);
        }
        
        charts.usage.data.labels = labels;
        charts.usage.data.datasets[0].data = usageData;
        charts.usage.update();
    }
}

/**
 * Update recent events table
 */
function updateRecentEvents(events) {
    const tbody = document.getElementById('recent-events-body');
    tbody.innerHTML = '';
    
    events.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDateTime(event.timestamp)}</td>
            <td>
                <span class="badge event-${event.event_type.replace(/_/g, '-')}">${formatEventType(event.event_type)}</span>
            </td>
            <td>
                <span class="badge severity-${event.severity}">${event.severity.toUpperCase()}</span>
            </td>
            <td><code>${event.source_ip}</code></td>
            <td>${truncateText(JSON.stringify(event.details), 50)}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Load API keys
 */
async function loadAPIKeys() {
    try {
        const response = await fetch('/api/security/keys', {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch API keys');
        }
        
        const data = await response.json();
        securityData.apiKeys = data.api_keys;
        
        updateAPIKeysTable(data.api_keys);
        
    } catch (error) {
        console.error('Failed to load API keys:', error);
        showAlert('Failed to load API keys', 'danger');
    }
}

/**
 * Update API keys table
 */
function updateAPIKeysTable(apiKeys) {
    const tbody = document.getElementById('api-keys-body');
    tbody.innerHTML = '';
    
    apiKeys.forEach(key => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><code>${key.key_id}</code></td>
            <td>${key.name}</td>
            <td>
                <div class="d-flex flex-wrap gap-1">
                    ${key.permissions.map(perm => `<span class="badge bg-secondary">${perm}</span>`).join('')}
                </div>
            </td>
            <td>
                <span class="badge ${key.is_active ? 'status-active' : 'status-inactive'}">
                    ${key.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${formatDateTime(key.created_at)}</td>
            <td>${key.last_used_at ? formatDateTime(key.last_used_at) : 'Never'}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-danger" onclick="revokeAPIKey('${key.key_id}')" 
                            ${!key.is_active ? 'disabled' : ''}>
                        <i class="fas fa-ban"></i> Revoke
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Load rate limits
 */
async function loadRateLimits() {
    try {
        const response = await fetch('/api/security/rate-limits', {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch rate limits');
        }
        
        const data = await response.json();
        securityData.rateLimits = data.rate_limits;
        
        updateRateLimitsTable(data.rate_limits);
        
    } catch (error) {
        console.error('Failed to load rate limits:', error);
        showAlert('Failed to load rate limits', 'danger');
    }
}

/**
 * Update rate limits table
 */
function updateRateLimitsTable(rateLimits) {
    const tbody = document.getElementById('rate-limits-body');
    tbody.innerHTML = '';
    
    rateLimits.forEach(limit => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><code>${limit.identifier}</code></td>
            <td>
                <span class="badge bg-info">${formatLimitType(limit.limit_type)}</span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="me-2">${limit.requests_minute}</span>
                    <div class="rate-limit-progress flex-grow-1">
                        <div class="rate-limit-bar rate-limit-${getRateLimitStatus(limit.requests_minute, 60)}"
                             style="width: ${(limit.requests_minute / 60) * 100}%"></div>
                    </div>
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="me-2">${limit.requests_hour}</span>
                    <div class="rate-limit-progress flex-grow-1">
                        <div class="rate-limit-bar rate-limit-${getRateLimitStatus(limit.requests_hour, 1000)}"
                             style="width: ${(limit.requests_hour / 1000) * 100}%"></div>
                    </div>
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="me-2">${limit.requests_day}</span>
                    <div class="rate-limit-progress flex-grow-1">
                        <div class="rate-limit-bar rate-limit-${getRateLimitStatus(limit.requests_day, 10000)}"
                             style="width: ${(limit.requests_day / 10000) * 100}%"></div>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge ${limit.is_blocked ? 'status-blocked' : 'status-active'}">
                    ${limit.is_blocked ? 'Blocked' : 'Normal'}
                </span>
            </td>
            <td>${limit.reset_minute ? formatDateTime(limit.reset_minute) : '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Load security events
 */
async function loadSecurityEvents() {
    try {
        const response = await fetch('/api/security/events?limit=100', {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch security events');
        }
        
        const data = await response.json();
        securityData.securityEvents = data.events;
        
        updateSecurityEventsTable(data.events);
        
    } catch (error) {
        console.error('Failed to load security events:', error);
        showAlert('Failed to load security events', 'danger');
    }
}

/**
 * Update security events table
 */
function updateSecurityEventsTable(events) {
    const tbody = document.getElementById('security-events-body');
    tbody.innerHTML = '';
    
    events.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDateTime(event.timestamp)}</td>
            <td>
                <span class="badge event-${event.event_type.replace(/_/g, '-')}">${formatEventType(event.event_type)}</span>
            </td>
            <td>
                <span class="badge severity-${event.severity}">${event.severity.toUpperCase()}</span>
            </td>
            <td><code>${event.source_ip}</code></td>
            <td><code>${event.endpoint}</code></td>
            <td>${event.user_id || '-'}</td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="showEventDetails('${event.event_id}')">
                    <i class="fas fa-eye"></i> Details
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Load IP whitelist
 */
async function loadIPWhitelist() {
    try {
        const response = await fetch('/api/security/whitelist', {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch IP whitelist');
        }
        
        const data = await response.json();
        securityData.ipWhitelist = data.whitelist;
        
        updateIPWhitelistTable(data.whitelist);
        
    } catch (error) {
        console.error('Failed to load IP whitelist:', error);
        showAlert('Failed to load IP whitelist', 'danger');
    }
}

/**
 * Update IP whitelist table
 */
function updateIPWhitelistTable(whitelist) {
    const tbody = document.getElementById('ip-whitelist-body');
    tbody.innerHTML = '';
    
    whitelist.forEach(ip => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><code>${ip.ip_address}</code></td>
            <td>${ip.description || '-'}</td>
            <td>
                <span class="badge ${ip.is_active ? 'status-active' : 'status-inactive'}">
                    ${ip.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${formatDateTime(ip.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="removeIPFromWhitelist('${ip.ip_address}')"
                        ${!ip.is_active ? 'disabled' : ''}>
                    <i class="fas fa-trash"></i> Remove
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Show create API key modal
 */
function showCreateKeyModal() {
    const modal = new bootstrap.Modal(document.getElementById('createKeyModal'));
    modal.show();
}

/**
 * Create API key
 */
async function createAPIKey() {
    const name = document.getElementById('key-name').value;
    const expiresInput = document.getElementById('key-expires').value;
    const expires_days = expiresInput ? parseInt(expiresInput) : null;
    
    // Get selected permissions
    const permissions = [];
    document.querySelectorAll('#key-permissions input[type="checkbox"]:checked').forEach(checkbox => {
        permissions.push(checkbox.value);
    });
    
    if (!name || permissions.length === 0) {
        showAlert('Please provide a name and select at least one permission', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/security/keys', {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                permissions: permissions,
                expires_days: expires_days
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create API key');
        }
        
        const data = await response.json();
        
        // Show the API key to user
        document.getElementById('show-key-id').value = data.api_key.key_id;
        document.getElementById('show-key-secret').value = data.api_key.key_secret;
        
        // Hide create modal and show key modal
        bootstrap.Modal.getInstance(document.getElementById('createKeyModal')).hide();
        const showModal = new bootstrap.Modal(document.getElementById('showKeyModal'));
        showModal.show();
        
        // Reset form
        document.getElementById('create-key-form').reset();
        
        // Reload API keys
        await loadAPIKeys();
        
        showAlert('API key created successfully', 'success');
        
    } catch (error) {
        console.error('Failed to create API key:', error);
        showAlert(error.message, 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Revoke API key
 */
async function revokeAPIKey(keyId) {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`/api/security/keys/${keyId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to revoke API key');
        }
        
        await loadAPIKeys();
        showAlert('API key revoked successfully', 'success');
        
    } catch (error) {
        console.error('Failed to revoke API key:', error);
        showAlert(error.message, 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Show add IP modal
 */
function showAddIPModal() {
    const modal = new bootstrap.Modal(document.getElementById('addIPModal'));
    modal.show();
}

/**
 * Add IP to whitelist
 */
async function addIPToWhitelist() {
    const ipAddress = document.getElementById('ip-address').value;
    const description = document.getElementById('ip-description').value;
    
    if (!ipAddress) {
        showAlert('Please provide an IP address', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/security/whitelist', {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ip_address: ipAddress,
                description: description
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add IP to whitelist');
        }
        
        // Hide modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('addIPModal')).hide();
        document.getElementById('add-ip-form').reset();
        
        // Reload whitelist
        await loadIPWhitelist();
        
        showAlert('IP address added to whitelist successfully', 'success');
        
    } catch (error) {
        console.error('Failed to add IP to whitelist:', error);
        showAlert(error.message, 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Remove IP from whitelist
 */
async function removeIPFromWhitelist(ipAddress) {
    if (!confirm('Are you sure you want to remove this IP from the whitelist?')) {
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`/api/security/whitelist/${encodeURIComponent(ipAddress)}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to remove IP from whitelist');
        }
        
        await loadIPWhitelist();
        showAlert('IP address removed from whitelist successfully', 'success');
        
    } catch (error) {
        console.error('Failed to remove IP from whitelist:', error);
        showAlert(error.message, 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Filter security events
 */
function filterSecurityEvents() {
    const eventType = document.getElementById('event-type-filter').value;
    const severity = document.getElementById('severity-filter').value;
    
    let filteredEvents = securityData.securityEvents;
    
    if (eventType) {
        filteredEvents = filteredEvents.filter(event => event.event_type === eventType);
    }
    
    if (severity) {
        filteredEvents = filteredEvents.filter(event => event.severity === severity);
    }
    
    updateSecurityEventsTable(filteredEvents);
}

/**
 * Show event details
 */
function showEventDetails(eventId) {
    const event = securityData.securityEvents.find(e => e.event_id === eventId);
    if (!event) return;
    
    const details = JSON.stringify(event, null, 2);
    alert(`Event Details:\n\n${details}`);
}

/**
 * Validate IP address input
 */
function validateIPAddress() {
    const input = document.getElementById('ip-address');
    const value = input.value;
    
    if (!value) {
        input.classList.remove('valid-ip', 'invalid-ip');
        return;
    }
    
    // Simple IP validation (IPv4)
    const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    
    if (ipv4Regex.test(value)) {
        input.classList.remove('invalid-ip');
        input.classList.add('valid-ip');
    } else {
        input.classList.remove('valid-ip');
        input.classList.add('invalid-ip');
    }
}

/**
 * Copy to clipboard
 */
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    
    // Visual feedback
    element.classList.add('copied');
    setTimeout(() => {
        element.classList.remove('copied');
    }, 500);
    
    showAlert('Copied to clipboard', 'success');
}

/**
 * Refresh rate limits
 */
async function refreshRateLimits() {
    await loadRateLimits();
    showAlert('Rate limits refreshed', 'info');
}

// Utility functions

/**
 * Get authentication headers
 */
function getAuthHeaders() {
    // For demo purposes, return empty headers
    // In production, include actual API key headers
    return {
        'X-API-Key': 'demo-key-id',
        'X-API-Secret': 'demo-key-secret'
    };
}

/**
 * Format datetime
 */
function formatDateTime(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
}

/**
 * Format event type
 */
function formatEventType(eventType) {
    return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Format limit type
 */
function formatLimitType(limitType) {
    return limitType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Get rate limit status
 */
function getRateLimitStatus(current, limit) {
    const percentage = (current / limit) * 100;
    if (percentage >= 90) return 'critical';
    if (percentage >= 70) return 'warning';
    return 'normal';
}

/**
 * Truncate text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Show loading spinner
 */
function showLoading() {
    document.getElementById('loading-spinner').classList.remove('d-none');
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    document.getElementById('loading-spinner').classList.add('d-none');
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

/**
 * Get alert icon
 */
function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}