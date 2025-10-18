/**
 * Enhanced Security Assessment JavaScript
 * Real-time vulnerability scanning and reporting for Enterprise Scanner
 */

class SecurityAssessment {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 6;
        this.assessmentData = {};
        this.assessmentId = null;
        this.statusCheckInterval = null;
        
        this.initializeEventListeners();
        this.updateProgress();
    }

    
    initializeEventListeners() {
        // Form navigation
        document.getElementById('next-step').addEventListener('click', () => this.nextStep());
        document.getElementById('prev-step').addEventListener('click', () => this.prevStep());
        document.getElementById('security-assessment-form').addEventListener('submit', (e) => this.submitAssessment(e));
        
        // Real-time form validation
        this.setupFormValidation();
        
        // Initialize tooltips and help text
        this.initializeHelpers();
    }
    
    setupFormValidation() {
        const form = document.getElementById('security-assessment-form');
        const inputs = form.querySelectorAll('input[required], select[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }
    
    validateField(field) {
        const isValid = field.checkValidity();
        const fieldGroup = field.closest('.col-md-6') || field.closest('.question-group') || field.parentElement;
        
        // Remove existing validation classes
        fieldGroup.classList.remove('has-error', 'has-success');
        
        // Remove existing feedback
        const existingFeedback = fieldGroup.querySelector('.field-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        if (!isValid) {
            fieldGroup.classList.add('has-error');
            const feedback = document.createElement('div');
            feedback.className = 'field-feedback text-danger mt-1';
            feedback.innerHTML = '<i class="bi bi-exclamation-circle me-1"></i>' + field.validationMessage;
            fieldGroup.appendChild(feedback);
        } else if (field.value) {
            fieldGroup.classList.add('has-success');
        }
        
        return isValid;
    }
    
    clearFieldError(field) {
        const fieldGroup = field.closest('.col-md-6') || field.closest('.question-group') || field.parentElement;
        fieldGroup.classList.remove('has-error');
        
        const feedback = fieldGroup.querySelector('.field-feedback');
        if (feedback) {
            feedback.remove();
        }
    }

    
    nextStep() {
        if (this.validateCurrentStep()) {
            if (this.currentStep < this.totalSteps) {
                this.collectStepData();
                this.currentStep++;
                this.updateStepDisplay();
                this.updateProgress();
                this.scrollToTop();
            }
        }
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
            this.updateProgress();
            this.scrollToTop();
        }
    }
    
    validateCurrentStep() {
        const currentStepElement = document.querySelector(`.assessment-step[data-step="${this.currentStep}"]`);
        const requiredFields = currentStepElement.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            this.showNotification('Please fill in all required fields before continuing.', 'warning');
        }
        
        return isValid;
    }
    
    collectStepData() {
        const currentStepElement = document.querySelector(`.assessment-step[data-step="${this.currentStep}"]`);
        const formElements = currentStepElement.querySelectorAll('input, select, textarea');
        
        formElements.forEach(element => {
            if (element.type === 'checkbox') {
                if (element.checked) {
                    if (!this.assessmentData[element.name]) {
                        this.assessmentData[element.name] = [];
                    }
                    this.assessmentData[element.name].push(element.value);
                }
            } else if (element.type === 'radio') {
                if (element.checked) {
                    this.assessmentData[element.name] = element.value;
                }
            } else {
                this.assessmentData[element.id] = element.value;
            }
        });
    }
    
    updateStepDisplay() {
        // Hide all steps
        document.querySelectorAll('.assessment-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show current step
        const currentStepElement = document.querySelector(`.assessment-step[data-step="${this.currentStep}"]`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
        
        // Update navigation buttons
        const prevBtn = document.getElementById('prev-step');
        const nextBtn = document.getElementById('next-step');
        const submitBtn = document.getElementById('submit-assessment');
        
        prevBtn.style.display = this.currentStep > 1 ? 'inline-block' : 'none';
        
        if (this.currentStep === this.totalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }
        
        // Update step indicator
        this.updateStepIndicator();
    }
    
    updateStepIndicator() {
        const stepText = document.querySelector('.progress-text');
        if (stepText) {
            stepText.innerHTML = `<span id="current-step">${this.currentStep}</span> of <span id="total-steps">${this.totalSteps}</span> sections completed`;
        }
    }
    
    updateProgress() {
        const progressBar = document.getElementById('assessment-progress');
        const progressPercentage = ((this.currentStep - 1) / this.totalSteps) * 100;
        
        if (progressBar) {
            progressBar.style.width = `${progressPercentage}%`;
            progressBar.setAttribute('aria-valuenow', progressPercentage);
        }
    }
    
    scrollToTop() {
        document.querySelector('.assessment-form-section').scrollIntoView({
            behavior: 'smooth'
        });
    }

    
    async submitAssessment(event) {
        event.preventDefault();
        
        if (!this.validateCurrentStep()) {
            return;
        }
        
        // Collect final step data
        this.collectStepData();
        
        // Add metadata
        this.assessmentData.submission_time = new Date().toISOString();
        this.assessmentData.user_agent = navigator.userAgent;
        
        try {
            // Show loading state
            this.showLoadingState();
            
            // Submit assessment to backend
            const response = await fetch('/api/assessment/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.assessmentData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.assessmentId = result.assessment_id;
                this.showAssessmentProgress();
                this.startStatusPolling();
            } else {
                throw new Error(result.error || 'Assessment submission failed');
            }
            
        } catch (error) {
            console.error('Assessment submission error:', error);
            this.showNotification('Failed to start assessment. Please try again.', 'error');
            this.hideLoadingState();
        }
    }
    
    showLoadingState() {
        const submitBtn = document.getElementById('submit-assessment');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Starting Assessment...';
    }
    
    hideLoadingState() {
        const submitBtn = document.getElementById('submit-assessment');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Complete Assessment';
    }
    
    showAssessmentProgress() {
        // Hide the form
        document.getElementById('security-assessment-form').style.display = 'none';
        
        // Create and show progress interface
        const progressHTML = `
            <div class="assessment-progress-container">
                <div class="text-center mb-4">
                    <h3><i class="bi bi-gear-fill fa-spin me-2"></i>Analyzing Your Security Posture...</h3>
                    <p class="text-muted">This comprehensive assessment typically takes 3-5 minutes</p>
                </div>
                
                <div class="progress mb-3" style="height: 20px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         id="scan-progress-bar" 
                         role="progressbar" 
                         style="width: 0%"
                         aria-valuenow="0" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        <span id="progress-percentage">0%</span>
                    </div>
                </div>
                
                <div class="scan-status-container">
                    <div class="d-flex align-items-center mb-2">
                        <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                        <span id="current-phase">Initializing assessment...</span>
                    </div>
                    
                    <div class="scan-phases mt-3">
                        <div class="phase-item" data-phase="infrastructure">
                            <i class="bi bi-circle text-muted"></i>
                            <span>Infrastructure Analysis</span>
                        </div>
                        <div class="phase-item" data-phase="network">
                            <i class="bi bi-circle text-muted"></i>
                            <span>Network Security Scan</span>
                        </div>
                        <div class="phase-item" data-phase="ssl">
                            <i class="bi bi-circle text-muted"></i>
                            <span>SSL/TLS Configuration</span>
                        </div>
                        <div class="phase-item" data-phase="vulnerability">
                            <i class="bi bi-circle text-muted"></i>
                            <span>Vulnerability Assessment</span>
                        </div>
                        <div class="phase-item" data-phase="compliance">
                            <i class="bi bi-circle text-muted"></i>
                            <span>Compliance Analysis</span>
                        </div>
                        <div class="phase-item" data-phase="report">
                            <i class="bi bi-circle text-muted"></i>
                            <span>Report Generation</span>
                        </div>
                    </div>
                </div>
                
                <div class="assessment-stats mt-4">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-number">15+</div>
                                <div class="stat-label">Security Checks</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-number">50+</div>
                                <div class="stat-label">Vulnerability Tests</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-number">10+</div>
                                <div class="stat-label">Compliance Frameworks</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-number">AI</div>
                                <div class="stat-label">Powered Analysis</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const cardBody = document.querySelector('.assessment-card .card-body');
        cardBody.innerHTML = progressHTML;
    }
    
    startStatusPolling() {
        this.statusCheckInterval = setInterval(() => {
            this.checkAssessmentStatus();
        }, 2000);
    }
    
    async checkAssessmentStatus() {
        try {
            const response = await fetch(`/api/assessment/status/${this.assessmentId}`);
            const status = await response.json();
            
            if (status.error) {
                throw new Error(status.error);
            }
            
            // Update progress
            this.updateScanProgress(status.progress, status.current_phase);
            
            // Update phase indicators
            this.updatePhaseIndicators(status.progress);
            
            if (status.status === 'completed' && status.results) {
                clearInterval(this.statusCheckInterval);
                this.showResults(status.results);
            } else if (status.status === 'error') {
                clearInterval(this.statusCheckInterval);
                this.showNotification('Assessment failed. Please try again.', 'error');
            }
            
        } catch (error) {
            console.error('Status check error:', error);
            clearInterval(this.statusCheckInterval);
            this.showNotification('Assessment monitoring failed. Please refresh and try again.', 'error');
        }
    }
    
    updateScanProgress(progress, phase) {
        const progressBar = document.getElementById('scan-progress-bar');
        const progressText = document.getElementById('progress-percentage');
        const currentPhase = document.getElementById('current-phase');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (progressText) {
            progressText.textContent = `${progress}%`;
        }
        
        if (currentPhase && phase) {
            currentPhase.textContent = phase;
        }
    }
    
    updatePhaseIndicators(progress) {
        const phases = document.querySelectorAll('.phase-item');
        const phaseProgress = [
            { threshold: 10, phase: 'infrastructure' },
            { threshold: 25, phase: 'network' },
            { threshold: 40, phase: 'ssl' },
            { threshold: 60, phase: 'vulnerability' },
            { threshold: 80, phase: 'compliance' },
            { threshold: 95, phase: 'report' }
        ];
        
        phaseProgress.forEach((item, index) => {
            const phaseElement = document.querySelector(`[data-phase="${item.phase}"]`);
            if (phaseElement) {
                const icon = phaseElement.querySelector('i');
                if (progress >= item.threshold) {
                    icon.className = 'bi bi-check-circle-fill text-success';
                } else if (index === 0 || progress >= phaseProgress[index - 1].threshold) {
                    icon.className = 'bi bi-arrow-right-circle-fill text-primary';
                } else {
                    icon.className = 'bi bi-circle text-muted';
                }
            }
        });
    }
    
    showResults(results) {
        // Create results display
        const resultsHTML = this.generateResultsHTML(results);
        
        // Update card body with results
        const cardBody = document.querySelector('.assessment-card .card-body');
        cardBody.innerHTML = resultsHTML;
        
        // Initialize results interactions
        this.initializeResultsInteractions();
        
        // Show success notification
        this.showNotification('Security assessment completed successfully!', 'success');
    }

    
    generateResultsHTML(results) {
        const scoreColor = this.getScoreColor(results.overall_score);
        const riskBadgeClass = this.getRiskBadgeClass(results.risk_level);
        
        return `
            <div class="assessment-results">
                <!-- Results Header -->
                <div class="results-header text-center mb-4">
                    <h2><i class="bi bi-clipboard-data me-2"></i>Your Security Assessment Results</h2>
                    <p class="text-muted">Comprehensive analysis completed for ${results.assessment_metadata.company_name}</p>
                </div>
                
                <!-- Overall Score -->
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="score-display text-center">
                            <div class="score-circle ${scoreColor}" style="margin: 0 auto;">
                                <span class="score-value">${results.overall_score}</span>
                                <small>/100</small>
                            </div>
                            <h4 class="mt-2">Overall Security Score</h4>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="risk-summary">
                            <div class="d-flex align-items-center mb-3">
                                <h4 class="me-3">Risk Level:</h4>
                                <span class="badge ${riskBadgeClass} fs-6">${results.risk_level}</span>
                            </div>
                            <p class="lead">${results.risk_description}</p>
                            
                            <div class="vulnerability-summary">
                                <div class="row">
                                    <div class="col-6 col-md-3">
                                        <div class="vuln-stat critical">
                                            <div class="vuln-number">${results.vulnerability_counts.critical}</div>
                                            <div class="vuln-label">Critical</div>
                                        </div>
                                    </div>
                                    <div class="col-6 col-md-3">
                                        <div class="vuln-stat high">
                                            <div class="vuln-number">${results.vulnerability_counts.high}</div>
                                            <div class="vuln-label">High</div>
                                        </div>
                                    </div>
                                    <div class="col-6 col-md-3">
                                        <div class="vuln-stat medium">
                                            <div class="vuln-number">${results.vulnerability_counts.medium}</div>
                                            <div class="vuln-label">Medium</div>
                                        </div>
                                    </div>
                                    <div class="col-6 col-md-3">
                                        <div class="vuln-stat low">
                                            <div class="vuln-number">${results.vulnerability_counts.low}</div>
                                            <div class="vuln-label">Low</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Category Scores -->
                <div class="category-scores mb-4">
                    <h4><i class="bi bi-bar-chart me-2"></i>Security Category Breakdown</h4>
                    ${this.generateCategoryScoresHTML(results.category_scores)}
                </div>
                
                <!-- Security Findings -->
                <div class="security-findings mb-4">
                    <h4><i class="bi bi-exclamation-triangle me-2"></i>Security Findings</h4>
                    <div class="findings-container">
                        ${this.generateFindingsHTML(results.findings)}
                    </div>
                </div>
                
                <!-- Recommendations -->
                <div class="recommendations mb-4">
                    <h4><i class="bi bi-lightbulb me-2"></i>Priority Recommendations</h4>
                    <div class="recommendations-list">
                        ${results.recommendations.map((rec, index) => `
                            <div class="recommendation-item">
                                <div class="recommendation-number">${index + 1}</div>
                                <div class="recommendation-text">${rec}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="results-actions text-center">
                    <button class="btn btn-primary btn-lg me-3" onclick="securityAssessment.downloadReport()">
                        <i class="bi bi-download me-2"></i>Download Full Report
                    </button>
                    <button class="btn btn-success btn-lg" onclick="securityAssessment.scheduleConsultation()">
                        <i class="bi bi-calendar me-2"></i>Schedule Security Consultation
                    </button>
                </div>
            </div>
        `;
    }
    
    generateCategoryScoresHTML(categoryScores) {
        return Object.entries(categoryScores).map(([category, score]) => {
            const scoreColor = this.getScoreColor(score);
            return `
                <div class="category-item">
                    <div class="category-info">
                        <span class="category-name">${category}</span>
                        <span class="category-score ${scoreColor}">${score}/100</span>
                    </div>
                    <div class="category-bar">
                        <div class="category-progress" style="width: ${score}%; background-color: var(--${scoreColor.replace('score-', '')}-color);"></div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    generateFindingsHTML(findings) {
        if (findings.length === 0) {
            return '<div class="no-findings"><i class="bi bi-shield-check text-success me-2"></i>No significant security issues detected.</div>';
        }
        
        return findings.map(finding => {
            const severityClass = this.getSeverityClass(finding.severity);
            const severityIcon = this.getSeverityIcon(finding.severity);
            
            return `
                <div class="finding-item ${severityClass}">
                    <div class="finding-header">
                        <div class="finding-title">
                            <i class="${severityIcon} me-2"></i>
                            ${finding.type}
                        </div>
                        <span class="severity-badge badge-${finding.severity}">${finding.severity.toUpperCase()}</span>
                    </div>
                    <div class="finding-description">${finding.description}</div>
                    <div class="finding-recommendation">
                        <strong>Recommendation:</strong> ${finding.recommendation}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    getScoreColor(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 65) return 'score-good';
        return 'score-poor';
    }
    
    getRiskBadgeClass(riskLevel) {
        const classes = {
            'LOW': 'bg-success',
            'MEDIUM': 'bg-warning',
            'HIGH': 'bg-danger',
            'CRITICAL': 'bg-dark'
        };
        return classes[riskLevel] || 'bg-secondary';
    }
    
    getSeverityClass(severity) {
        return `finding-${severity}`;
    }
    
    getSeverityIcon(severity) {
        const icons = {
            'critical': 'bi bi-exclamation-triangle-fill text-danger',
            'high': 'bi bi-exclamation-circle-fill text-warning',
            'medium': 'bi bi-info-circle-fill text-info',
            'low': 'bi bi-check-circle-fill text-success'
        };
        return icons[severity] || 'bi bi-circle';
    }
    
    initializeResultsInteractions() {
        // Add any interactive elements for results
        this.initializeTooltips();
        this.animateCounters();
    }
    
    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }
    
    animateCounters() {
        const counters = document.querySelectorAll('.vuln-number, .score-value');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            let current = 0;
            const increment = target / 30;
            
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
    
    async downloadReport() {
        if (!this.assessmentId) {
            this.showNotification('Assessment ID not found. Please run assessment again.', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/assessment/report/${this.assessmentId}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `security_assessment_${this.assessmentId.substring(0, 8)}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showNotification('Report downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to download report');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showNotification('Failed to download report. Please try again.', 'error');
        }
    }
    
    scheduleConsultation() {
        const companyName = this.assessmentData['company-name'] || 'Unknown Company';
        const email = this.assessmentData['email'] || '';
        
        const subject = encodeURIComponent('Security Consultation Request - Enterprise Scanner');
        const body = encodeURIComponent(`Hi Enterprise Scanner Team,

I just completed a security assessment for ${companyName} and would like to schedule a consultation to discuss the results and next steps.

Assessment Details:
- Company: ${companyName}
- Industry: ${this.assessmentData['industry'] || 'Not specified'}
- Contact Email: ${email}
- Assessment ID: ${this.assessmentId || 'Not available'}

I'm interested in learning more about your enterprise security solutions.

Best regards`);
        
        window.location.href = `mailto:sales@enterprisescanner.com?subject=${subject}&body=${body}`;
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        
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
    
    getBootstrapAlertClass(type) {
        const classes = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classes[type] || 'info';
    }
    
    initializeHelpers() {
        // Add help tooltips and information
        this.addHelpTooltips();
    }
    
    addHelpTooltips() {
        const helpTexts = {
            'industry': 'Select the industry that best describes your organization\'s primary business focus.',
            'company-size': 'Choose the range that best represents your total number of employees.',
            'annual-revenue': 'This helps us provide industry-appropriate security recommendations.',
            'security-team': 'Indicates your current cybersecurity staffing situation.',
            'assessment-frequency': 'How often your organization conducts formal security assessments.'
        };
        
        Object.entries(helpTexts).forEach(([id, text]) => {
            const element = document.getElementById(id);
            if (element) {
                element.setAttribute('data-bs-toggle', 'tooltip');
                element.setAttribute('data-bs-placement', 'top');
                element.setAttribute('title', text);
            }
        });
    }
}
}

// Initialize the assessment when the page loads
let securityAssessment;

document.addEventListener('DOMContentLoaded', function() {
    securityAssessment = new SecurityAssessment();
});

// CSS for enhanced styling
const assessmentStyles = `
    .assessment-step {
        display: none;
        animation: fadeIn 0.3s ease-in;
    }
    
    .assessment-step.active {
        display: block;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .has-error .form-control,
    .has-error .form-select {
        border-color: #dc3545;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
    }
    
    .has-success .form-control,
    .has-success .form-select {
        border-color: #198754;
        box-shadow: 0 0 0 0.2rem rgba(25, 135, 84, 0.25);
    }
    
    .field-feedback {
        font-size: 0.875rem;
    }
    
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .score-excellent { background: linear-gradient(135deg, #28a745, #20c997); }
    .score-good { background: linear-gradient(135deg, #ffc107, #fd7e14); }
    .score-poor { background: linear-gradient(135deg, #dc3545, #e83e8c); }
    
    .vuln-stat {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .vuln-stat.critical { background-color: rgba(220, 53, 69, 0.1); }
    .vuln-stat.high { background-color: rgba(255, 193, 7, 0.1); }
    .vuln-stat.medium { background-color: rgba(13, 202, 240, 0.1); }
    .vuln-stat.low { background-color: rgba(25, 135, 84, 0.1); }
    
    .vuln-number {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .category-item {
        margin-bottom: 1rem;
    }
    
    .category-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .category-bar {
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .category-progress {
        height: 100%;
        transition: width 0.6s ease;
    }
    
    .finding-item {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .finding-critical { border-left-color: #dc3545; }
    .finding-high { border-left-color: #ffc107; }
    .finding-medium { border-left-color: #0dcaf0; }
    .finding-low { border-left-color: #198754; }
    
    .finding-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .finding-title {
        font-weight: 600;
    }
    
    .severity-badge {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }
    
    .badge-critical { background-color: #dc3545; color: white; }
    .badge-high { background-color: #ffc107; color: black; }
    .badge-medium { background-color: #0dcaf0; color: black; }
    .badge-low { background-color: #198754; color: white; }
    
    .recommendation-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .recommendation-number {
        background-color: #0d6efd;
        color: white;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .phase-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
    }
    
    .phase-item i {
        margin-right: 0.5rem;
        width: 1rem;
    }
    
    .assessment-progress-container {
        max-width: 600px;
        margin: 0 auto;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = assessmentStyles;
document.head.appendChild(styleSheet);