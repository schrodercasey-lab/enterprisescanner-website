/**
 * Enterprise Scanner - Backend API Integration
 * Handles form submissions and data capture to backend database
 * Version: 1.0.0
 * Date: October 18, 2025
 */

// Backend API Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:5000',
    endpoints: {
        leads: '/api/leads',
        assessments: '/api/security-assessment',
        chat: '/api/chat',
        analytics: '/api/analytics/event'
    },
    timeout: 10000
};

/**
 * Main API Client Class
 */
class EnterpriseAPI {
    constructor(config = API_CONFIG) {
        this.config = config;
    }

    /**
     * Generic API POST request
     */
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.config.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data),
                signal: AbortSignal.timeout(this.config.timeout)
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }

    /**
     * Generic API GET request
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.config.baseURL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                signal: AbortSignal.timeout(this.config.timeout)
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }

    /**
     * Submit a lead to the backend
     */
    async submitLead(leadData) {
        return await this.post(this.config.endpoints.leads, leadData);
    }

    /**
     * Submit a security assessment
     */
    async submitAssessment(assessmentData) {
        return await this.post(this.config.endpoints.assessments, assessmentData);
    }

    /**
     * Track analytics event
     */
    async trackEvent(eventType, eventData) {
        return await this.post(this.config.endpoints.analytics, {
            event_type: eventType,
            event_data: eventData,
            timestamp: new Date().toISOString()
        });
    }
}

// Create global API instance
window.enterpriseAPI = new EnterpriseAPI();

/**
 * Form Handler Class
 */
class FormHandler {
    constructor(formId, api) {
        this.form = document.getElementById(formId);
        this.api = api;
        this.isSubmitting = false;

        if (this.form) {
            this.init();
        }
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();

        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;
        const submitButton = this.form.querySelector('[type="submit"]');
        const originalText = submitButton ? submitButton.textContent : '';

        try {
            // Show loading state
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
            }

            // Get form data
            const formData = this.getFormData();

            // Submit to backend
            const response = await this.submitToBackend(formData);

            // Show success message
            this.showSuccess(response);

            // Reset form
            this.form.reset();

            // Track success event
            await this.api.trackEvent('form_submit_success', {
                form_id: this.form.id,
                data: formData
            });

        } catch (error) {
            console.error('Form submission error:', error);
            this.showError(error.message);

            // Track error event
            await this.api.trackEvent('form_submit_error', {
                form_id: this.form.id,
                error: error.message
            });

        } finally {
            this.isSubmitting = false;
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        }
    }

    getFormData() {
        const data = {};
        const formData = new FormData(this.form);

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Also get data from inputs with IDs
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.id && !data[input.id]) {
                data[input.id] = input.value;
            }
        });

        return data;
    }

    async submitToBackend(data) {
        // Override this in subclasses
        return await this.api.submitLead(data);
    }

    showSuccess(response) {
        // Create success alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <strong>Success!</strong> Your information has been received. We'll contact you soon!
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => alert.remove(), 5000);
    }

    showError(message) {
        // Create error alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <strong>Error!</strong> ${message}. Please try again or contact us directly.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        // Auto remove after 7 seconds
        setTimeout(() => alert.remove(), 7000);
    }
}

/**
 * Security Assessment Form Handler
 */
class AssessmentFormHandler extends FormHandler {
    async submitToBackend(data) {
        // Extract email and name for lead creation
        const leadData = {
            first_name: data['contact-name']?.split(' ')[0] || 'Unknown',
            last_name: data['contact-name']?.split(' ').slice(1).join(' ') || 'Unknown',
            email: data['contact-email'] || data.email,
            company: data['company-name'] || data.company,
            job_title: data['job-title'] || data['contact-role'],
            phone: data['contact-phone'] || data.phone,
            lead_source: 'security_assessment',
            lead_status: 'qualified'
        };

        // Submit as lead first
        await this.api.submitLead(leadData);

        // Then submit full assessment
        return await this.api.submitAssessment(data);
    }
}

/**
 * ROI Calculator Form Handler
 */
class ROIFormHandler extends FormHandler {
    async submitToBackend(data) {
        const leadData = {
            first_name: data['first-name'] || data.firstName || 'ROI',
            last_name: data['last-name'] || data.lastName || 'Calculator User',
            email: data.email,
            company: data.company || 'Unknown',
            job_title: data['job-title'] || data.jobTitle,
            lead_source: 'roi_calculator',
            lead_status: 'interested',
            estimated_deal_value: parseInt(data['current-budget']) || null
        };

        return await this.api.submitLead(leadData);
    }
}

/**
 * Demo Request Form Handler
 */
class DemoFormHandler extends FormHandler {
    async submitToBackend(data) {
        const leadData = {
            first_name: data['first-name'] || data.firstName || data.name?.split(' ')[0],
            last_name: data['last-name'] || data.lastName || data.name?.split(' ').slice(1).join(' '),
            email: data.email,
            company: data.company,
            job_title: data['job-title'] || data.title || data.position,
            phone: data.phone,
            lead_source: 'demo_request',
            lead_status: 'demo_requested',
            seniority_level: this.detectSeniorityLevel(data['job-title'] || data.title)
        };

        return await this.api.submitLead(leadData);
    }

    detectSeniorityLevel(title) {
        if (!title) return null;
        const titleLower = title.toLowerCase();
        
        if (titleLower.includes('ceo') || titleLower.includes('cto') || 
            titleLower.includes('cio') || titleLower.includes('ciso') ||
            titleLower.includes('chief')) {
            return 'C-Level';
        } else if (titleLower.includes('vp') || titleLower.includes('vice president')) {
            return 'VP';
        } else if (titleLower.includes('director')) {
            return 'Director';
        } else if (titleLower.includes('manager')) {
            return 'Manager';
        }
        return 'Individual';
    }
}

/**
 * Initialize form handlers when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enterprise Scanner API Integration Loaded');

    // Initialize security assessment form
    if (document.getElementById('security-assessment-form')) {
        new AssessmentFormHandler('security-assessment-form', window.enterpriseAPI);
        console.log('✅ Security assessment form connected to backend');
    }

    // Initialize ROI calculator form
    if (document.getElementById('roi-form')) {
        new ROIFormHandler('roi-form', window.enterpriseAPI);
        console.log('✅ ROI calculator form connected to backend');
    }

    // Initialize partner application form
    if (document.getElementById('partnerApplicationForm')) {
        new FormHandler('partnerApplicationForm', window.enterpriseAPI);
        console.log('✅ Partner application form connected to backend');
    }

    // Initialize any generic contact forms
    const contactForms = document.querySelectorAll('[id*="contact"], [id*="demo"], [id*="request"]');
    contactForms.forEach(form => {
        if (!form.dataset.apiConnected) {
            new DemoFormHandler(form.id, window.enterpriseAPI);
            form.dataset.apiConnected = 'true';
            console.log(`✅ ${form.id} connected to backend`);
        }
    });

    // Track page view
    window.enterpriseAPI.trackEvent('page_view', {
        page: window.location.pathname,
        referrer: document.referrer,
        timestamp: new Date().toISOString()
    });
});

/**
 * Detect Fortune 500 companies from email domain
 */
function detectFortune500(email) {
    const domain = email.split('@')[1]?.toLowerCase();
    const fortune500Domains = [
        'microsoft.com', 'apple.com', 'google.com', 'amazon.com',
        'jpmorgan.com', 'walmart.com', 'exxonmobil.com', 'chevron.com',
        'berkshirehathaway.com', 'unitedhealth.com', 'cvs.com', 'att.com',
        'verizon.com', 'ford.com', 'gm.com', 'ge.com', 'boeing.com'
    ];
    
    return fortune500Domains.includes(domain);
}

// Export for global use
window.detectFortune500 = detectFortune500;

console.log('🚀 Enterprise Scanner Backend Integration Ready!');
console.log('📡 API Base URL:', API_CONFIG.baseURL);
console.log('✅ All forms will auto-save to database');
