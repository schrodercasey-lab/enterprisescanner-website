/**
 * Enterprise Scanner - API Documentation Portal JavaScript
 * Interactive functionality for API testing, key management, and documentation
 */

class APIDocumentationPortal {
    constructor() {
        this.apiKeys = this.loadAPIKeys();
        this.baseURL = 'http://localhost:5000/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.renderAPIKeys();
        this.setupCodeHighlighting();
    }

    setupEventListeners() {
        // API Key Generation
        document.getElementById('generateKeyBtn')?.addEventListener('click', () => this.showAPIKeyModal());
        document.getElementById('generateNewKeyBtn')?.addEventListener('click', () => this.showAPIKeyModal());
        document.getElementById('generateKeySubmit')?.addEventListener('click', () => this.generateAPIKey());
        document.getElementById('copyKeyBtn')?.addEventListener('click', () => this.copyAPIKey());

        // Quick Start
        document.getElementById('quickStartBtn')?.addEventListener('click', () => this.scrollToSection('authentication'));

        // Navigation
        document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                this.scrollToSection(targetId);
            });
        });

        // API Testing Interface
        this.setupAPITesting();
    }

    setupNavigation() {
        // Smooth scrolling and active navigation
        const sections = document.querySelectorAll('.content-section');
        const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

        // Update active navigation on scroll
        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= (sectionTop - 200)) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });
    }

    scrollToSection(targetId) {
        const target = document.getElementById(targetId);
        if (target) {
            const offsetTop = target.offsetTop - 80; // Account for navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }

    showAPIKeyModal() {
        const modal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
        // Reset form
        document.getElementById('keyName').value = '';
        document.getElementById('keyPermissions').value = 'read';
        document.getElementById('keyGenerationForm').style.display = 'block';
        document.getElementById('generatedKey').style.display = 'none';
        document.getElementById('generateKeySubmit').style.display = 'block';
        modal.show();
    }

    async generateAPIKey() {
        const keyName = document.getElementById('keyName').value;
        const permissions = document.getElementById('keyPermissions').value;

        if (!keyName.trim()) {
            this.showAlert('Please enter a name for your API key.', 'warning');
            return;
        }

        try {
            // Generate a random API key
            const apiKey = this.generateRandomKey();
            
            // Store the key
            const keyData = {
                id: Date.now().toString(),
                name: keyName,
                key: apiKey,
                permissions: permissions,
                created: new Date().toISOString(),
                lastUsed: null
            };

            this.apiKeys.push(keyData);
            this.saveAPIKeys();

            // Show the generated key
            document.getElementById('newApiKey').value = apiKey;
            document.getElementById('keyGenerationForm').style.display = 'none';
            document.getElementById('generatedKey').style.display = 'block';
            document.getElementById('generateKeySubmit').style.display = 'none';

            // Update the API keys list
            this.renderAPIKeys();

        } catch (error) {
            console.error('Error generating API key:', error);
            this.showAlert('Failed to generate API key. Please try again.', 'danger');
        }
    }

    generateRandomKey() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = 'es_';
        for (let i = 0; i < 32; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }

    copyAPIKey() {
        const keyInput = document.getElementById('newApiKey');
        keyInput.select();
        keyInput.setSelectionRange(0, 99999); // For mobile devices
        
        try {
            document.execCommand('copy');
            this.showAlert('API key copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy API key:', err);
            this.showAlert('Please manually copy the API key.', 'warning');
        }
    }

    renderAPIKeys() {
        const container = document.getElementById('apiKeysList');
        if (!container) return;

        if (this.apiKeys.length === 0) {
            container.innerHTML = '<p class="text-muted">No API keys generated yet. Click "Generate API Key" to create your first key.</p>';
            return;
        }

        const keysHTML = this.apiKeys.map(key => `
            <div class="api-key-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${this.escapeHtml(key.name)}</h6>
                        <div class="api-key-value small">
                            ${key.key.substring(0, 8)}...${key.key.substring(key.key.length - 4)}
                        </div>
                        <small class="text-muted">
                            Created: ${new Date(key.created).toLocaleDateString()} • 
                            Permissions: ${key.permissions} • 
                            Last used: ${key.lastUsed ? new Date(key.lastUsed).toLocaleDateString() : 'Never'}
                        </small>
                    </div>
                    <div class="btn-group-vertical btn-group-sm">
                        <button class="btn btn-outline-primary btn-sm" onclick="apiPortal.copyKey('${key.key}')">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="apiPortal.deleteKey('${key.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = keysHTML;
    }

    copyKey(key) {
        navigator.clipboard.writeText(key).then(() => {
            this.showAlert('API key copied to clipboard!', 'success');
        }).catch(() => {
            this.showAlert('Please manually copy the API key.', 'warning');
        });
    }

    deleteKey(keyId) {
        if (confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
            this.apiKeys = this.apiKeys.filter(key => key.id !== keyId);
            this.saveAPIKeys();
            this.renderAPIKeys();
            this.showAlert('API key deleted successfully.', 'info');
        }
    }

    setupAPITesting() {
        // Create API testing interface
        this.createAPITestingInterface();
    }

    createAPITestingInterface() {
        const testingSection = document.getElementById('testing');
        if (!testingSection) return;

        const testingHTML = `
            <h2 class="mb-4">
                <i class="fas fa-vial text-primary me-2"></i>
                Interactive API Testing
            </h2>

            <div class="api-testing-interface">
                <div class="row">
                    <div class="col-lg-8">
                        <div class="test-endpoint-card">
                            <h5 class="mb-3">
                                <i class="fas fa-play-circle me-2"></i>
                                Test API Endpoints
                            </h5>
                            
                            <div class="mb-3">
                                <label class="form-label">Select Endpoint:</label>
                                <select class="form-select" id="testEndpoint">
                                    <option value="/health">GET /health - Health Check</option>
                                    <option value="/security-assessment">POST /security-assessment - Security Assessment</option>
                                    <option value="/chat/send">POST /chat/send - Send Chat Message</option>
                                    <option value="/analytics/metrics">GET /analytics/metrics - Analytics Data</option>
                                    <option value="/deployment/verify">GET /deployment/verify - Deployment Status</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">API Key:</label>
                                <select class="form-select" id="testApiKey">
                                    <option value="">Select API Key</option>
                                    ${this.apiKeys.map(key => `<option value="${key.key}">${key.name}</option>`).join('')}
                                </select>
                            </div>

                            <div class="mb-3" id="requestBodySection" style="display: none;">
                                <label class="form-label">Request Body (JSON):</label>
                                <textarea class="form-control font-monospace" id="requestBody" rows="6" placeholder="Enter JSON request body..."></textarea>
                            </div>

                            <button class="btn btn-primary" id="testAPIBtn">
                                <i class="fas fa-play me-1"></i>
                                Send Request
                            </button>
                            <button class="btn btn-outline-secondary" id="clearResponseBtn">
                                <i class="fas fa-eraser me-1"></i>
                                Clear Response
                            </button>
                        </div>

                        <div class="response-section" id="responseSection" style="display: none;">
                            <h6>Response:</h6>
                            <div class="mb-2">
                                <span class="response-status" id="responseStatus">200 OK</span>
                                <span class="text-muted ms-2" id="responseTime">Response time: 123ms</span>
                            </div>
                            <pre><code class="language-json" id="responseBody"></code></pre>
                        </div>
                    </div>

                    <div class="col-lg-4">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-info-circle me-2"></i>
                                    Testing Tips
                                </h6>
                            </div>
                            <div class="card-body">
                                <ul class="list-unstyled mb-0">
                                    <li class="mb-2">
                                        <i class="fas fa-lightbulb text-warning me-2"></i>
                                        Generate an API key first to test authenticated endpoints
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-shield-alt text-info me-2"></i>
                                        Use the health check endpoint to verify connectivity
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-code text-success me-2"></i>
                                        JSON request bodies are required for POST endpoints
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-clock text-primary me-2"></i>
                                        Response times are measured automatically
                                    </li>
                                </ul>
                            </div>
                        </div>

                        <div class="card mt-3">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-book me-2"></i>
                                    Sample Requests
                                </h6>
                            </div>
                            <div class="card-body">
                                <div class="accordion" id="sampleRequests">
                                    <div class="accordion-item">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sampleAssessment">
                                                Security Assessment
                                            </button>
                                        </h2>
                                        <div id="sampleAssessment" class="accordion-collapse collapse" data-bs-parent="#sampleRequests">
                                            <div class="accordion-body">
                                                <pre><code class="language-json">{
  "contactName": "John Doe",
  "email": "john@example.com",
  "companyName": "Example Corp",
  "jobTitle": "CISO",
  "companySize": "1000-5000",
  "industry": "Technology"
}</code></pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        testingSection.innerHTML = testingHTML;

        // Setup testing event listeners
        document.getElementById('testEndpoint')?.addEventListener('change', (e) => {
            const isPost = e.target.value.includes('assessment') || e.target.value.includes('chat');
            document.getElementById('requestBodySection').style.display = isPost ? 'block' : 'none';
        });

        document.getElementById('testAPIBtn')?.addEventListener('click', () => this.sendTestRequest());
        document.getElementById('clearResponseBtn')?.addEventListener('click', () => this.clearResponse());
    }

    async sendTestRequest() {
        const endpoint = document.getElementById('testEndpoint').value;
        const apiKey = document.getElementById('testApiKey').value;
        const requestBody = document.getElementById('requestBody').value;

        if (!apiKey) {
            this.showAlert('Please select an API key for testing.', 'warning');
            return;
        }

        const startTime = performance.now();
        
        try {
            const isPost = endpoint.includes('assessment') || endpoint.includes('chat');
            const url = `${this.baseURL}${endpoint}`;
            
            const options = {
                method: isPost ? 'POST' : 'GET',
                headers: {
                    'X-API-Key': apiKey,
                    'Content-Type': 'application/json'
                }
            };

            if (isPost && requestBody.trim()) {
                try {
                    JSON.parse(requestBody); // Validate JSON
                    options.body = requestBody;
                } catch (e) {
                    this.showAlert('Invalid JSON in request body.', 'danger');
                    return;
                }
            }

            document.getElementById('testAPIBtn').disabled = true;
            document.getElementById('testAPIBtn').innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Sending...';

            const response = await fetch(url, options);
            const endTime = performance.now();
            const responseTime = Math.round(endTime - startTime);
            
            const responseData = await response.json();

            this.displayResponse(response.status, responseData, responseTime);

            // Update last used timestamp for API key
            const keyIndex = this.apiKeys.findIndex(key => key.key === apiKey);
            if (keyIndex !== -1) {
                this.apiKeys[keyIndex].lastUsed = new Date().toISOString();
                this.saveAPIKeys();
                this.renderAPIKeys();
            }

        } catch (error) {
            console.error('API test error:', error);
            this.displayResponse(0, { error: error.message }, 0);
        } finally {
            document.getElementById('testAPIBtn').disabled = false;
            document.getElementById('testAPIBtn').innerHTML = '<i class="fas fa-play me-1"></i>Send Request';
        }
    }

    displayResponse(status, data, responseTime) {
        const responseSection = document.getElementById('responseSection');
        const responseStatus = document.getElementById('responseStatus');
        const responseTimeElement = document.getElementById('responseTime');
        const responseBody = document.getElementById('responseBody');

        // Show response section
        responseSection.style.display = 'block';

        // Set status
        responseStatus.textContent = status ? `${status} ${this.getStatusText(status)}` : 'Network Error';
        responseStatus.className = `response-status ${this.getStatusClass(status)}`;

        // Set response time
        responseTimeElement.textContent = responseTime ? `Response time: ${responseTime}ms` : 'Request failed';

        // Set response body
        responseBody.textContent = JSON.stringify(data, null, 2);

        // Re-highlight code
        if (window.Prism) {
            Prism.highlightElement(responseBody);
        }

        // Scroll to response
        responseSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    getStatusText(status) {
        const statusTexts = {
            200: 'OK',
            201: 'Created',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        };
        return statusTexts[status] || 'Unknown';
    }

    getStatusClass(status) {
        if (status >= 200 && status < 300) return 'status-200';
        if (status >= 400 && status < 500) return 'status-400';
        if (status >= 500) return 'status-500';
        return 'status-400';
    }

    clearResponse() {
        document.getElementById('responseSection').style.display = 'none';
        document.getElementById('requestBody').value = '';
    }

    setupCodeHighlighting() {
        // Initialize Prism.js for code highlighting
        if (window.Prism) {
            Prism.highlightAll();
        }
    }

    loadAPIKeys() {
        try {
            const stored = localStorage.getItem('enterpriseScanner_apiKeys');
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading API keys:', error);
            return [];
        }
    }

    saveAPIKeys() {
        try {
            localStorage.setItem('enterpriseScanner_apiKeys', JSON.stringify(this.apiKeys));
        } catch (error) {
            console.error('Error saving API keys:', error);
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Insert alert at top of page
        const container = document.querySelector('main .container-fluid') || document.body;
        const alertElement = document.createElement('div');
        alertElement.innerHTML = alertHTML;
        container.insertBefore(alertElement.firstElementChild, container.firstElementChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            warning: 'exclamation-triangle',
            danger: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the API Documentation Portal
let apiPortal;
document.addEventListener('DOMContentLoaded', () => {
    apiPortal = new APIDocumentationPortal();
});

// Global functions for inline event handlers
window.apiPortal = {
    copyKey: (key) => apiPortal.copyKey(key),
    deleteKey: (id) => apiPortal.deleteKey(id)
};