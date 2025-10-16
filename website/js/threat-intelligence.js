/**
 * Threat Intelligence Dashboard JavaScript
 * Manages real-time threat intelligence data display and interactions
 */

class ThreatIntelligenceManager {
    constructor() {
        this.apiBase = '/api/threat-intelligence';
        this.currentData = {
            dashboard: null,
            cves: [],
            threatActors: [],
            advisories: [],
            industryReport: null
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadDashboardData();
        this.showStatus('Threat intelligence loaded successfully', 'success');
    }

    setupEventListeners() {
        // Refresh buttons
        document.getElementById('refreshFeeds').addEventListener('click', () => {
            this.loadDashboardData();
        });

        document.getElementById('updateIntelligence').addEventListener('click', () => {
            this.updateThreatFeeds();
        });

        // Search functionality
        document.getElementById('searchButton').addEventListener('click', () => {
            this.performSearch();
        });

        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Filter changes
        document.getElementById('categoryFilter').addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('severityFilter').addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('timeFilter').addEventListener('change', () => {
            this.loadCVEData();
        });

        // Tab changes
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetTab = e.target.getAttribute('data-bs-target');
                this.handleTabChange(targetTab);
            });
        });

        // Industry selector
        document.getElementById('industrySelect').addEventListener('change', () => {
            this.loadIndustryReport();
        });

        // Load more buttons
        document.getElementById('loadMoreCves').addEventListener('click', () => {
            this.loadMoreCVEs();
        });
    }

    async loadDashboardData() {
        try {
            this.showStatus('Loading threat intelligence dashboard...', 'info');
            
            const response = await fetch(`${this.apiBase}/dashboard`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.dashboard = result.data;
                this.updateSummaryCards();
                this.updateOverviewTab();
                this.hideStatus();
            } else {
                throw new Error(result.message || 'Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showStatus('Failed to load threat intelligence data', 'error');
        }
    }

    updateSummaryCards() {
        const data = this.currentData.dashboard;
        if (!data || !data.summary) return;

        document.getElementById('criticalCves').textContent = data.summary.critical_cves || 0;
        document.getElementById('highCves').textContent = data.summary.high_cves || 0;
        document.getElementById('activeThreatActors').textContent = data.summary.active_threat_actors || 0;
        document.getElementById('recentAdvisories').textContent = data.summary.recent_advisories || 0;

        // Add animation to cards
        this.animateCounters();
    }

    animateCounters() {
        const counters = document.querySelectorAll('.card-title');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            if (isNaN(target)) return;

            let current = 0;
            const increment = target / 30; // 30 frames for smooth animation
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 50);
        });
    }

    updateOverviewTab() {
        const data = this.currentData.dashboard;
        if (!data) return;

        // Update trending vulnerabilities
        const trendingContainer = document.getElementById('trendingVulns');
        if (data.threat_landscape && data.threat_landscape.trending_vulnerabilities) {
            trendingContainer.innerHTML = this.generateTrendingVulnsHTML(data.threat_landscape.trending_vulnerabilities);
        }

        // Update active campaigns
        const campaignsContainer = document.getElementById('activeCampaigns');
        if (data.threat_landscape && data.threat_landscape.active_campaigns) {
            campaignsContainer.innerHTML = this.generateActiveCampaignsHTML(data.threat_landscape.active_campaigns);
        }

        // Update recommendations
        const recommendationsContainer = document.getElementById('threatRecommendations');
        if (data.recommendations) {
            recommendationsContainer.innerHTML = this.generateRecommendationsHTML(data.recommendations);
        }
    }

    generateTrendingVulnsHTML(trends) {
        return trends.map(trend => `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                <div>
                    <strong>${trend.type}</strong>
                    <span class="text-muted ms-2">${trend.count} instances</span>
                </div>
                <div>
                    <i class="bi ${trend.trend === 'up' ? 'bi-arrow-up text-danger' : 
                                   trend.trend === 'down' ? 'bi-arrow-down text-success' : 
                                   'bi-arrow-right text-muted'}"></i>
                </div>
            </div>
        `).join('');
    }

    generateActiveCampaignsHTML(campaigns) {
        return campaigns.map(campaign => `
            <div class="mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${campaign.campaign}</h6>
                        <small class="text-muted">Actor: ${campaign.actor}</small>
                    </div>
                    <span class="badge ${this.getStatusBadgeClass(campaign.status)}">${campaign.status}</span>
                </div>
            </div>
        `).join('');
    }

    generateRecommendationsHTML(recommendations) {
        return recommendations.map((rec, index) => `
            <div class="d-flex align-items-start mb-2">
                <span class="badge bg-primary me-2">${index + 1}</span>
                <span>${rec}</span>
            </div>
        `).join('');
    }

    async loadCVEData() {
        try {
            const days = document.getElementById('timeFilter').value;
            const severity = document.getElementById('severityFilter').value;
            
            let url = `${this.apiBase}/cves?days=${days}&limit=20`;
            if (severity !== 'all') {
                url += `&severity=${severity}`;
            }

            const response = await fetch(url);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.cves = result.data.cves;
                this.displayCVEs();
            }
        } catch (error) {
            console.error('Error loading CVE data:', error);
            this.showStatus('Failed to load CVE data', 'error');
        }
    }

    displayCVEs() {
        const container = document.getElementById('cvesTable');
        if (!this.currentData.cves || this.currentData.cves.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No CVE data available</p>';
            return;
        }

        const html = this.currentData.cves.map(cve => `
            <div class="cve-card card mb-3">
                <div class="cve-header d-flex justify-content-between align-items-center">
                    <div>
                        <div class="cve-id">${cve.cve_id}</div>
                        <div class="text-light opacity-75">${new Date(cve.published_date).toLocaleDateString()}</div>
                    </div>
                    <div class="text-end">
                        <div class="cvss-score">${cve.cvss_score.toFixed(1)}</div>
                        <span class="severity-badge severity-${cve.severity.toLowerCase()}">${cve.severity}</span>
                    </div>
                </div>
                <div class="card-body">
                    <p class="card-text">${cve.description.substring(0, 200)}${cve.description.length > 200 ? '...' : ''}</p>
                    ${cve.affected_products.length > 0 ? `
                        <div class="mb-2">
                            <small class="text-muted">Affected Products:</small>
                            <div class="mt-1">
                                ${cve.affected_products.slice(0, 3).map(product => 
                                    `<span class="badge bg-secondary me-1">${product.split(':')[3] || product}</span>`
                                ).join('')}
                                ${cve.affected_products.length > 3 ? `<span class="text-muted">+${cve.affected_products.length - 3} more</span>` : ''}
                            </div>
                        </div>
                    ` : ''}
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge ${cve.exploit_availability ? 'bg-danger' : 'bg-success'}">
                                ${cve.exploit_availability ? 'Exploit Available' : 'No Known Exploit'}
                            </span>
                            <span class="badge bg-warning text-dark ms-2">${cve.threat_level} Threat</span>
                        </div>
                        <button class="btn btn-sm btn-outline-primary" onclick="threatIntel.showCVEDetails('${cve.cve_id}')">
                            View Details
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async loadThreatActors() {
        try {
            const response = await fetch(`${this.apiBase}/actors`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.threatActors = result.data.threat_actors;
                this.displayThreatActors();
            }
        } catch (error) {
            console.error('Error loading threat actors:', error);
            this.showStatus('Failed to load threat actor data', 'error');
        }
    }

    displayThreatActors() {
        const container = document.getElementById('threatActorsGrid');
        if (!this.currentData.threatActors || this.currentData.threatActors.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No threat actor data available</p>';
            return;
        }

        const html = this.currentData.threatActors.map(actor => `
            <div class="col-md-6 mb-4">
                <div class="actor-card card h-100">
                    <div class="actor-header">
                        <div class="actor-name">${actor.name}</div>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="actor-attribution">${actor.attribution}</span>
                            <span class="badge ${this.getThreatLevelBadgeClass(actor.threat_level)}">${actor.threat_level}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <small class="text-muted">Aliases:</small>
                            <div class="mt-1">
                                ${JSON.parse(actor.aliases || '[]').map(alias => 
                                    `<span class="badge bg-light text-dark me-1">${alias}</span>`
                                ).join('')}
                            </div>
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">Target Sectors:</small>
                            <div class="mt-1">
                                ${JSON.parse(actor.target_sectors || '[]').map(sector => 
                                    `<span class="badge bg-info me-1">${sector}</span>`
                                ).join('')}
                            </div>
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">Techniques:</small>
                            <div class="mt-1">
                                ${JSON.parse(actor.techniques || '[]').map(technique => 
                                    `<span class="technique-tag">${technique}</span>`
                                ).join('')}
                            </div>
                        </div>
                        <p class="card-text">${actor.description}</p>
                        <div class="text-muted">
                            <small>Last Activity: ${new Date(actor.last_activity).toLocaleDateString()}</small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `<div class="row">${html}</div>`;
    }

    async loadSecurityAdvisories() {
        try {
            const response = await fetch(`${this.apiBase}/advisories`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.advisories = result.data.advisories;
                this.displayAdvisories();
            }
        } catch (error) {
            console.error('Error loading security advisories:', error);
            this.showStatus('Failed to load security advisory data', 'error');
        }
    }

    displayAdvisories() {
        const container = document.getElementById('advisoriesTable');
        if (!this.currentData.advisories || this.currentData.advisories.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No security advisory data available</p>';
            return;
        }

        const html = this.currentData.advisories.map(advisory => `
            <div class="advisory-card card mb-3">
                <div class="advisory-header d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1 text-white">${advisory.title}</h6>
                        <small class="text-white-50">${advisory.advisory_id}</small>
                    </div>
                    <div class="text-end">
                        <span class="vendor-badge">${advisory.vendor}</span>
                        <span class="severity-badge severity-${advisory.severity.toLowerCase()} ms-2">${advisory.severity}</span>
                    </div>
                </div>
                <div class="card-body">
                    <p class="card-text">${advisory.description}</p>
                    <div class="mb-3">
                        <small class="text-muted">Affected Systems:</small>
                        <div class="mt-1">
                            ${JSON.parse(advisory.affected_systems || '[]').slice(0, 4).map(system => 
                                `<span class="badge bg-warning text-dark me-1">${system}</span>`
                            ).join('')}
                            ${JSON.parse(advisory.affected_systems || '[]').length > 4 ? 
                                `<span class="text-muted">+${JSON.parse(advisory.affected_systems).length - 4} more</span>` : ''}
                        </div>
                    </div>
                    <div class="mb-3">
                        <strong>Solution:</strong>
                        <p class="mb-0">${advisory.solution}</p>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">Published: ${new Date(advisory.published_date).toLocaleDateString()}</small>
                        <button class="btn btn-sm btn-outline-primary" onclick="threatIntel.showAdvisoryDetails('${advisory.advisory_id}')">
                            View References
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async loadIndustryReport() {
        try {
            const industry = document.getElementById('industrySelect').value;
            const response = await fetch(`${this.apiBase}/industry-report?industry=${industry}`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.industryReport = result.data;
                this.displayIndustryReport();
            }
        } catch (error) {
            console.error('Error loading industry report:', error);
            this.showStatus('Failed to load industry report', 'error');
        }
    }

    displayIndustryReport() {
        const container = document.getElementById('industryReport');
        const data = this.currentData.industryReport;
        
        if (!data) {
            container.innerHTML = '<p class="text-muted text-center py-4">No industry report data available</p>';
            return;
        }

        let html = '';

        if (data.threat_intelligence) {
            const intel = data.threat_intelligence;
            html = `
                <div class="industry-section">
                    <h6 class="mb-3">
                        ${data.industry.charAt(0).toUpperCase() + data.industry.slice(1)} Industry Threat Profile
                        <span class="threat-level-indicator threat-level-${intel.risk_level.toLowerCase()}"></span>
                        <span class="badge ${this.getThreatLevelBadgeClass(intel.risk_level)}">${intel.risk_level} Risk</span>
                    </h6>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Primary Threats</h6>
                            <ul class="list-unstyled">
                                ${intel.primary_threats.map(threat => `
                                    <li class="mb-1"><i class="bi bi-shield-exclamation text-danger me-2"></i>${threat}</li>
                                `).join('')}
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6>Key Threat Actors</h6>
                            <ul class="list-unstyled">
                                ${intel.threat_actors.map(actor => `
                                    <li class="mb-1"><i class="bi bi-person-fill-exclamation text-warning me-2"></i>${actor}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h6>Common Attack Vectors</h6>
                        <div class="d-flex flex-wrap gap-2">
                            ${intel.common_attack_vectors.map(vector => `
                                <span class="badge bg-danger">${vector}</span>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h6>Recent Campaigns</h6>
                        <ul class="list-unstyled">
                            ${intel.recent_campaigns.map(campaign => `
                                <li class="mb-1"><i class="bi bi-activity text-info me-2"></i>${campaign}</li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            `;
        } else {
            // Cross-industry view
            html = `
                <div class="industry-section">
                    <h6 class="mb-3">Cross-Industry Threat Landscape</h6>
                    <div class="row">
                        <div class="col-md-4">
                            <h6>Industries Covered</h6>
                            <ul class="list-unstyled">
                                ${data.industries_covered.map(industry => `
                                    <li class="mb-1"><i class="bi bi-building text-primary me-2"></i>${industry.charAt(0).toUpperCase() + industry.slice(1)}</li>
                                `).join('')}
                            </ul>
                        </div>
                        <div class="col-md-4">
                            <h6>Cross-Industry Threats</h6>
                            <ul class="list-unstyled">
                                ${data.cross_industry_threats.map(threat => `
                                    <li class="mb-1"><i class="bi bi-exclamation-triangle text-warning me-2"></i>${threat}</li>
                                `).join('')}
                            </ul>
                        </div>
                        <div class="col-md-4">
                            <h6>Emerging Threats</h6>
                            <ul class="list-unstyled">
                                ${data.emerging_threats.map(threat => `
                                    <li class="mb-1"><i class="bi bi-lightning text-danger me-2"></i>${threat}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        // Add recommendations
        if (data.recommendations) {
            html += `
                <div class="industry-section">
                    <h6 class="mb-3">Recommendations</h6>
                    <div class="row">
                        ${data.recommendations.map((rec, index) => `
                            <div class="col-md-6 mb-2">
                                <div class="d-flex align-items-start">
                                    <span class="badge bg-success me-2">${index + 1}</span>
                                    <span>${rec}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
    }

    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        const category = document.getElementById('categoryFilter').value;

        if (!query) {
            this.showStatus('Please enter a search query', 'warning');
            return;
        }

        try {
            this.showStatus(`Searching for "${query}"...`, 'info');
            
            const response = await fetch(`${this.apiBase}/search?q=${encodeURIComponent(query)}&category=${category}`);
            const result = await response.json();

            if (result.status === 'success') {
                this.displaySearchResults(result.data.results);
                this.hideStatus();
            } else {
                throw new Error(result.message || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showStatus('Search failed', 'error');
        }
    }

    displaySearchResults(results) {
        // Create a modal to show search results
        const modal = `
            <div class="modal fade" id="searchResultsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Search Results</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${this.generateSearchResultsHTML(results)}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('searchResultsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to DOM and show
        document.body.insertAdjacentHTML('beforeend', modal);
        const searchModal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
        searchModal.show();
    }

    generateSearchResultsHTML(results) {
        let html = '';

        if (results.cves && results.cves.length > 0) {
            html += `
                <h6>CVEs (${results.cves.length})</h6>
                ${results.cves.slice(0, 5).map(cve => `
                    <div class="border-bottom pb-2 mb-2">
                        <strong>${cve.cve_id}</strong>
                        <span class="severity-badge severity-${cve.severity.toLowerCase()} ms-2">${cve.severity}</span>
                        <p class="mb-1 small">${cve.description.substring(0, 150)}...</p>
                    </div>
                `).join('')}
            `;
        }

        if (results.threat_actors && results.threat_actors.length > 0) {
            html += `
                <h6 class="mt-3">Threat Actors (${results.threat_actors.length})</h6>
                ${results.threat_actors.slice(0, 5).map(actor => `
                    <div class="border-bottom pb-2 mb-2">
                        <strong>${actor.name}</strong>
                        <span class="badge ${this.getThreatLevelBadgeClass(actor.threat_level)} ms-2">${actor.threat_level}</span>
                        <p class="mb-1 small">${actor.description.substring(0, 150)}...</p>
                    </div>
                `).join('')}
            `;
        }

        if (results.advisories && results.advisories.length > 0) {
            html += `
                <h6 class="mt-3">Security Advisories (${results.advisories.length})</h6>
                ${results.advisories.slice(0, 5).map(advisory => `
                    <div class="border-bottom pb-2 mb-2">
                        <strong>${advisory.title}</strong>
                        <span class="severity-badge severity-${advisory.severity.toLowerCase()} ms-2">${advisory.severity}</span>
                        <p class="mb-1 small">${advisory.description.substring(0, 150)}...</p>
                    </div>
                `).join('')}
            `;
        }

        if (html === '') {
            html = '<p class="text-muted text-center py-4">No results found</p>';
        }

        return html;
    }

    async updateThreatFeeds() {
        try {
            this.showLoadingModal();
            
            const response = await fetch(`${this.apiBase}/feed-update`, {
                method: 'POST'
            });
            const result = await response.json();

            this.hideLoadingModal();

            if (result.status === 'success') {
                this.showStatus('Threat intelligence feeds updated successfully', 'success');
                await this.loadDashboardData();
            } else {
                throw new Error(result.message || 'Update failed');
            }
        } catch (error) {
            this.hideLoadingModal();
            console.error('Update error:', error);
            this.showStatus('Failed to update threat intelligence feeds', 'error');
        }
    }

    handleTabChange(targetTab) {
        switch (targetTab) {
            case '#cves':
                if (this.currentData.cves.length === 0) {
                    this.loadCVEData();
                }
                break;
            case '#actors':
                if (this.currentData.threatActors.length === 0) {
                    this.loadThreatActors();
                }
                break;
            case '#advisories':
                if (this.currentData.advisories.length === 0) {
                    this.loadSecurityAdvisories();
                }
                break;
            case '#industry':
                if (!this.currentData.industryReport) {
                    this.loadIndustryReport();
                }
                break;
        }
    }

    showStatus(message, type = 'info') {
        const alertElement = document.getElementById('statusAlert');
        const messageElement = document.getElementById('statusMessage');
        
        alertElement.className = `alert alert-${type} d-flex align-items-center`;
        messageElement.textContent = message;
        alertElement.style.display = 'block';

        if (type === 'success') {
            setTimeout(() => this.hideStatus(), 3000);
        }
    }

    hideStatus() {
        document.getElementById('statusAlert').style.display = 'none';
    }

    showLoadingModal() {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoadingModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }

    // Helper methods
    getThreatLevelBadgeClass(level) {
        const classes = {
            'Critical': 'bg-danger',
            'High': 'bg-warning',
            'Medium': 'bg-info',
            'Low': 'bg-success'
        };
        return classes[level] || 'bg-secondary';
    }

    getStatusBadgeClass(status) {
        const classes = {
            'ongoing': 'bg-danger',
            'active': 'bg-warning',
            'declining': 'bg-success',
            'inactive': 'bg-secondary'
        };
        return classes[status] || 'bg-secondary';
    }

    // Public methods for external calls
    showCVEDetails(cveId) {
        const cve = this.currentData.cves.find(c => c.cve_id === cveId);
        if (cve) {
            this.displayCVEModal(cve);
        }
    }

    showAdvisoryDetails(advisoryId) {
        const advisory = this.currentData.advisories.find(a => a.advisory_id === advisoryId);
        if (advisory) {
            this.displayAdvisoryModal(advisory);
        }
    }

    displayCVEModal(cve) {
        const modal = `
            <div class="modal fade" id="cveDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">${cve.cve_id}</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <strong>CVSS Score:</strong> ${cve.cvss_score}
                                </div>
                                <div class="col-md-6">
                                    <span class="severity-badge severity-${cve.severity.toLowerCase()}">${cve.severity}</span>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Description:</strong>
                                <p>${cve.description}</p>
                            </div>
                            <div class="mb-3">
                                <strong>Remediation:</strong>
                                <p>${cve.remediation}</p>
                            </div>
                            ${cve.references.length > 0 ? `
                                <div class="mb-3">
                                    <strong>References:</strong>
                                    <ul>
                                        ${cve.references.map(ref => `<li><a href="${ref}" target="_blank">${ref}</a></li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modal);
        const cveModal = new bootstrap.Modal(document.getElementById('cveDetailsModal'));
        cveModal.show();

        // Clean up modal after hiding
        document.getElementById('cveDetailsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    displayAdvisoryModal(advisory) {
        const modal = `
            <div class="modal fade" id="advisoryDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">${advisory.title}</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <strong>Advisory ID:</strong> ${advisory.advisory_id}
                                </div>
                                <div class="col-md-6">
                                    <strong>Vendor:</strong> ${advisory.vendor}
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Description:</strong>
                                <p>${advisory.description}</p>
                            </div>
                            <div class="mb-3">
                                <strong>Solution:</strong>
                                <p>${advisory.solution}</p>
                            </div>
                            ${JSON.parse(advisory.references || '[]').length > 0 ? `
                                <div class="mb-3">
                                    <strong>References:</strong>
                                    <ul>
                                        ${JSON.parse(advisory.references).map(ref => `<li><a href="${ref}" target="_blank">${ref}</a></li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modal);
        const advisoryModal = new bootstrap.Modal(document.getElementById('advisoryDetailsModal'));
        advisoryModal.show();

        // Clean up modal after hiding
        document.getElementById('advisoryDetailsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    async loadMoreCVEs() {
        // Implementation for loading more CVEs with pagination
        try {
            const currentCount = this.currentData.cves.length;
            const response = await fetch(`${this.apiBase}/cves?offset=${currentCount}&limit=20`);
            const result = await response.json();

            if (result.status === 'success' && result.data.cves.length > 0) {
                this.currentData.cves = [...this.currentData.cves, ...result.data.cves];
                this.displayCVEs();
            } else {
                document.getElementById('loadMoreCves').textContent = 'No more CVEs';
                document.getElementById('loadMoreCves').disabled = true;
            }
        } catch (error) {
            console.error('Error loading more CVEs:', error);
        }
    }

    applyFilters() {
        // Re-load data with current filter settings
        this.loadCVEData();
    }
}

// Initialize the threat intelligence manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.threatIntel = new ThreatIntelligenceManager();
});