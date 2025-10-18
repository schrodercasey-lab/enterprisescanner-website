/**
 * Partner Portal JavaScript
 * Handles partner application, login, and portal functionality
 */

class PartnerPortal {
    constructor() {
        this.partners = this.loadPartners();
        this.currentPartner = this.loadCurrentPartner();
        this.initializeEventListeners();
        this.initializeUI();
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Partner application form
        const applicationForm = document.getElementById('partnerApplicationForm');
        if (applicationForm) {
            applicationForm.addEventListener('submit', (e) => this.handlePartnerApplication(e));
        }

        // Partner login form
        const loginForm = document.getElementById('partnerLoginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handlePartnerLogin(e));
        }

        // Login button
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.showLoginModal());
        }

        // Apply now button
        const applyNowBtn = document.getElementById('applyNowBtn');
        if (applyNowBtn) {
            applyNowBtn.addEventListener('click', () => this.scrollToApplication());
        }

        // Commission calculator
        this.initializeCommissionCalculator();

        // Form validation
        this.initializeFormValidation();
    }

    /**
     * Initialize UI components
     */
    initializeUI() {
        this.updateLoginButton();
        this.animateCounters();
        this.initializeTooltips();
    }

    /**
     * Handle partner application submission
     */
    async handlePartnerApplication(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        
        // Validate form
        if (!this.validateApplicationForm(formData)) {
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        submitBtn.disabled = true;

        try {
            // Collect form data
            const applicationData = {
                companyName: formData.get('companyName'),
                partnerTier: formData.get('partnerTier'),
                contactName: formData.get('contactName'),
                contactTitle: formData.get('contactTitle'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                annualRevenue: formData.get('annualRevenue'),
                securityFocus: formData.get('securityFocus'),
                clientTypes: this.getCheckedValues('clientTypes'),
                experience: formData.get('experience'),
                expectations: formData.get('expectations'),
                submittedAt: new Date().toISOString(),
                status: 'pending',
                id: this.generatePartnerId()
            };

            // Submit application
            const result = await this.submitPartnerApplication(applicationData);
            
            if (result.success) {
                this.showSuccessMessage('Application submitted successfully! We\'ll review your application and contact you within 48 hours.');
                form.reset();
                this.trackEvent('partner_application_submitted', {
                    partner_tier: applicationData.partnerTier,
                    company_name: applicationData.companyName,
                    annual_revenue: applicationData.annualRevenue
                });
            } else {
                throw new Error(result.message || 'Failed to submit application');
            }

        } catch (error) {
            console.error('Application submission error:', error);
            this.showErrorMessage('Failed to submit application. Please try again or contact support.');
        } finally {
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Handle partner login
     */
    async handlePartnerLogin(event) {
        event.preventDefault();
        
        const form = event.target;
        const email = form.loginEmail.value;
        const password = form.loginPassword.value;
        const rememberMe = form.rememberMe.checked;

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...';
        submitBtn.disabled = true;

        try {
            const result = await this.authenticatePartner(email, password);
            
            if (result.success) {
                this.currentPartner = result.partner;
                if (rememberMe) {
                    this.saveCurrentPartner(this.currentPartner);
                }
                
                // Close modal and redirect to dashboard
                const modal = bootstrap.Modal.getInstance(document.getElementById('partnerLoginModal'));
                modal.hide();
                
                this.showSuccessMessage(`Welcome back, ${this.currentPartner.contactName}!`);
                this.updateLoginButton();
                
                // Redirect to partner dashboard
                setTimeout(() => {
                    window.location.href = 'partner-dashboard.html';
                }, 1500);

                this.trackEvent('partner_login', {
                    partner_id: this.currentPartner.id,
                    partner_tier: this.currentPartner.partnerTier
                });

            } else {
                throw new Error(result.message || 'Invalid credentials');
            }

        } catch (error) {
            console.error('Login error:', error);
            this.showErrorMessage('Invalid email or password. Please try again.');
        } finally {
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Submit partner application to backend
     */
    async submitPartnerApplication(applicationData) {
        try {
            const response = await fetch('/api/partners/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(applicationData)
            });

            if (response.ok) {
                const result = await response.json();
                
                // Store locally for demo purposes
                this.partners.push(applicationData);
                this.savePartners();
                
                // Send notification email
                await this.sendNotificationEmail('partner_application', applicationData);
                
                return { success: true, data: result };
            } else {
                const error = await response.json();
                return { success: false, message: error.message };
            }
        } catch (error) {
            console.error('API submission error:', error);
            
            // Fallback to local storage for demo
            this.partners.push(applicationData);
            this.savePartners();
            
            return { success: true, data: applicationData };
        }
    }

    /**
     * Authenticate partner credentials
     */
    async authenticatePartner(email, password) {
        try {
            const response = await fetch('/api/partners/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const result = await response.json();
                return { success: true, partner: result.partner };
            } else {
                return { success: false, message: 'Invalid credentials' };
            }
        } catch (error) {
            console.error('Authentication error:', error);
            
            // Demo authentication - check against stored partners
            const partner = this.partners.find(p => 
                p.email === email && p.status === 'approved'
            );
            
            if (partner) {
                return { success: true, partner };
            } else {
                return { success: false, message: 'Invalid credentials or pending approval' };
            }
        }
    }

    /**
     * Validate application form
     */
    validateApplicationForm(formData) {
        const required = ['companyName', 'partnerTier', 'contactName', 'contactTitle', 'email', 'phone', 'annualRevenue', 'securityFocus'];
        
        for (const field of required) {
            if (!formData.get(field)) {
                this.showErrorMessage(`Please fill in the ${field.replace(/([A-Z])/g, ' $1').toLowerCase()} field.`);
                return false;
            }
        }

        // Validate email format
        const email = formData.get('email');
        if (!this.isValidEmail(email)) {
            this.showErrorMessage('Please enter a valid email address.');
            return false;
        }

        // Validate client types
        const clientTypes = this.getCheckedValues('clientTypes');
        if (clientTypes.length === 0) {
            this.showErrorMessage('Please select at least one client type.');
            return false;
        }

        // Check for duplicate applications
        const existingPartner = this.partners.find(p => p.email === email);
        if (existingPartner) {
            this.showErrorMessage('An application with this email already exists.');
            return false;
        }

        return true;
    }

    /**
     * Initialize form validation
     */
    initializeFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('input', (e) => {
                this.validateField(e.target);
            });
        });
    }

    /**
     * Validate individual form field
     */
    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        switch (field.type) {
            case 'email':
                isValid = this.isValidEmail(value);
                message = isValid ? '' : 'Please enter a valid email address';
                break;
            case 'tel':
                isValid = value.length >= 10;
                message = isValid ? '' : 'Please enter a valid phone number';
                break;
            default:
                if (field.required) {
                    isValid = value.length > 0;
                    message = isValid ? '' : 'This field is required';
                }
        }

        this.setFieldValidation(field, isValid, message);
        return isValid;
    }

    /**
     * Set field validation state
     */
    setFieldValidation(field, isValid, message) {
        const feedback = field.parentNode.querySelector('.invalid-feedback') || 
                        this.createFeedbackElement(field.parentNode);
        
        field.classList.toggle('is-valid', isValid && field.value.trim() !== '');
        field.classList.toggle('is-invalid', !isValid);
        feedback.textContent = message;
    }

    /**
     * Create feedback element for validation
     */
    createFeedbackElement(parent) {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        parent.appendChild(feedback);
        return feedback;
    }

    /**
     * Initialize commission calculator
     */
    initializeCommissionCalculator() {
        const dealSizeInput = document.getElementById('dealSize');
        const tierSelect = document.getElementById('commissionTier');
        const commissionOutput = document.getElementById('commissionAmount');

        if (dealSizeInput && tierSelect && commissionOutput) {
            const calculateCommission = () => {
                const dealSize = parseFloat(dealSizeInput.value) || 0;
                const tier = tierSelect.value;
                
                let rate = 0;
                switch (tier) {
                    case 'authorized': rate = 0.25; break;
                    case 'gold': rate = 0.30; break;
                    case 'platinum': rate = 0.35; break;
                }
                
                const commission = dealSize * rate;
                commissionOutput.textContent = this.formatCurrency(commission);
            };

            dealSizeInput.addEventListener('input', calculateCommission);
            tierSelect.addEventListener('change', calculateCommission);
        }
    }

    /**
     * Show login modal
     */
    showLoginModal() {
        const modal = new bootstrap.Modal(document.getElementById('partnerLoginModal'));
        modal.show();
    }

    /**
     * Scroll to application section
     */
    scrollToApplication() {
        document.getElementById('onboarding').scrollIntoView({
            behavior: 'smooth'
        });
    }

    /**
     * Update login button based on authentication state
     */
    updateLoginButton() {
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn && this.currentPartner) {
            loginBtn.textContent = `Welcome, ${this.currentPartner.contactName}`;
            loginBtn.onclick = () => window.location.href = 'partner-dashboard.html';
        }
    }

    /**
     * Animate counter numbers
     */
    animateCounters() {
        const counters = document.querySelectorAll('.stat-card h3');
        
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => observer.observe(counter));
    }

    /**
     * Animate individual counter
     */
    animateCounter(element) {
        const target = element.textContent;
        const isPercentage = target.includes('%');
        const isCurrency = target.includes('$');
        const numericValue = parseFloat(target.replace(/[^0-9.]/g, ''));
        
        let current = 0;
        const increment = numericValue / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= numericValue) {
                current = numericValue;
                clearInterval(timer);
            }
            
            let display = Math.floor(current);
            if (isPercentage) {
                display += '%';
            } else if (isCurrency) {
                display = '$' + this.formatNumber(display) + (target.includes('M') ? 'M' : '');
            } else {
                display = this.formatNumber(display) + (target.includes('+') ? '+' : '');
            }
            
            element.textContent = display;
        }, 20);
    }

    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Send notification email
     */
    async sendNotificationEmail(type, data) {
        try {
            await fetch('/api/email/partner-notification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type, data })
            });
        } catch (error) {
            console.error('Email notification error:', error);
        }
    }

    /**
     * Track analytics events
     */
    trackEvent(eventName, properties = {}) {
        try {
            // Google Analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, properties);
            }
            
            // Custom analytics
            if (typeof analytics !== 'undefined') {
                analytics.track(eventName, properties);
            }
            
            console.log('Event tracked:', eventName, properties);
        } catch (error) {
            console.error('Analytics tracking error:', error);
        }
    }

    /**
     * Utility functions
     */
    getCheckedValues(name) {
        const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
        return Array.from(checkboxes).map(cb => cb.value);
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    generatePartnerId() {
        return 'PTR-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5).toUpperCase();
    }

    /**
     * Local storage helpers
     */
    loadPartners() {
        try {
            const stored = localStorage.getItem('enterpriseScanner_partners');
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    savePartners() {
        try {
            localStorage.setItem('enterpriseScanner_partners', JSON.stringify(this.partners));
        } catch (error) {
            console.error('Failed to save partners:', error);
        }
    }

    loadCurrentPartner() {
        try {
            const stored = localStorage.getItem('enterpriseScanner_currentPartner');
            return stored ? JSON.parse(stored) : null;
        } catch {
            return null;
        }
    }

    saveCurrentPartner(partner) {
        try {
            localStorage.setItem('enterpriseScanner_currentPartner', JSON.stringify(partner));
        } catch (error) {
            console.error('Failed to save current partner:', error);
        }
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        this.showAlert(message, 'success');
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        this.showAlert(message, 'danger');
    }

    /**
     * Show alert message
     */
    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize Partner Portal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.partnerPortal = new PartnerPortal();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PartnerPortal;
}