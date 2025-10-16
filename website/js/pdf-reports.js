/**
 * Enterprise Scanner - Professional PDF Reports Interface
 * Generate Fortune 500-grade cybersecurity assessment reports
 */

class PDFReportsManager {
    constructor() {
        this.selectedReportType = null;
        this.selectedFramework = 'NIST';
        this.assessmentData = null;
        this.demoMode = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeInterface();
    }

    setupEventListeners() {
        // Assessment validation
        document.getElementById('assessmentId').addEventListener('input', () => {
            this.clearAssessmentInfo();
        });

        // Framework selection for compliance reports
        document.querySelectorAll('input[name="framework"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.selectedFramework = e.target.value;
                this.updatePreview();
            });
        });
    }

    initializeInterface() {
        // Show navigation indicators
        this.updateNavigationState();
    }

    loadDemoAssessment() {
        // Load demo assessment data for testing
        this.demoMode = true;
        const demoAssessmentId = 'demo-' + Date.now().toString(36);
        
        document.getElementById('assessmentId').value = demoAssessmentId;
        
        this.assessmentData = {
            assessment_id: demoAssessmentId,
            target_domain: 'demo-company.com',
            overall_score: 87,
            threats_blocked: 2847,
            cost_avoidance: '$3.2M',
            vulnerability_count: 46,
            high_risk_findings: 7,
            compliance_scores: {
                'NIST': 92,
                'ISO27001': 89,
                'SOX': 76,
                'GDPR': 94
            },
            assessment_date: new Date().toISOString(),
            status: 'completed'
        };
        
        this.showAssessmentInfo();
        this.showSuccessMessage('Demo assessment loaded successfully!');
    }

    async validateAssessment() {
        const assessmentId = document.getElementById('assessmentId').value.trim();
        
        if (!assessmentId) {
            this.showError('Please enter an assessment ID');
            return;
        }

        try {
            // Check if it's demo mode
            if (assessmentId.startsWith('demo-')) {
                this.loadDemoAssessment();
                return;
            }

            this.showLoading('Validating assessment...');
            
            // Validate with API
            const response = await fetch(`/api/security-assessment/status/${assessmentId}`);
            
            if (!response.ok) {
                throw new Error('Assessment not found');
            }
            
            const data = await response.json();
            
            if (data.status !== 'completed') {
                throw new Error('Assessment not completed yet');
            }
            
            // Get full assessment results
            const resultsResponse = await fetch(`/api/security-assessment/results/${assessmentId}`);
            
            if (!resultsResponse.ok) {
                throw new Error('Could not retrieve assessment results');
            }
            
            this.assessmentData = await resultsResponse.json();
            this.assessmentData.assessment_id = assessmentId;
            
            this.showAssessmentInfo();
            this.hideLoading();
            this.showSuccessMessage('Assessment validated successfully!');
            
        } catch (error) {
            this.hideLoading();
            this.showError(`Validation failed: ${error.message}`);
        }
    }

    showAssessmentInfo() {
        const infoDiv = document.getElementById('assessmentInfo');
        const detailsDiv = document.getElementById('assessmentDetails');
        
        if (!this.assessmentData) return;
        
        const targetDomain = this.assessmentData.target_domain || 'N/A';
        const overallScore = this.assessmentData.overall_score || 'N/A';
        const threatsBlocked = this.assessmentData.threats_blocked || 'N/A';
        const vulnerabilityCount = this.assessmentData.vulnerability_count || 'N/A';
        
        detailsDiv.innerHTML = `
            <div class="mb-2">
                <strong>Target:</strong> ${targetDomain}
            </div>
            <div class="mb-2">
                <strong>Security Score:</strong> 
                <span class="badge ${overallScore >= 80 ? 'bg-success' : overallScore >= 60 ? 'bg-warning' : 'bg-danger'}">${overallScore}/100</span>
            </div>
            <div class="mb-2">
                <strong>Threats Blocked:</strong> ${threatsBlocked}
            </div>
            <div class="mb-2">
                <strong>Findings:</strong> ${vulnerabilityCount}
            </div>
            <div class="mb-2">
                <strong>Status:</strong> 
                <span class="badge bg-success">Completed</span>
            </div>
        `;
        
        infoDiv.style.display = 'block';
        this.updateNavigationState();
    }

    clearAssessmentInfo() {
        document.getElementById('assessmentInfo').style.display = 'none';
        this.assessmentData = null;
        this.updateNavigationState();
    }

    selectReportType(type) {
        // Remove previous selection
        document.querySelectorAll('.report-type-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection to clicked card
        document.querySelector(`[data-type="${type}"]`).classList.add('selected');
        
        this.selectedReportType = type;
        
        // Show/hide compliance framework selection
        const complianceDiv = document.getElementById('complianceFramework');
        if (type === 'compliance') {
            complianceDiv.style.display = 'block';
        } else {
            complianceDiv.style.display = 'none';
        }
        
        this.updatePreview();
        this.updateNavigationState();
    }

    updatePreview() {
        if (!this.selectedReportType || !this.assessmentData) {
            document.getElementById('reportPreview').style.display = 'none';
            return;
        }

        const previewDiv = document.getElementById('reportPreview');
        const contentDiv = document.getElementById('previewContent');
        
        const reportInfo = this.getReportInfo(this.selectedReportType);
        const companyName = document.getElementById('companyName').value || 'Your Company';
        
        contentDiv.innerHTML = `
            <div class="row">
                <div class="col-lg-8">
                    <h5><i class="bi bi-file-earmark-pdf me-2"></i>${reportInfo.title}</h5>
                    <p class="text-muted">${reportInfo.description}</p>
                    
                    <div class="preview-pages">
                        ${reportInfo.sections.map((section, index) => `
                            <div class="preview-page">
                                <div class="preview-page-icon">
                                    <i class="bi bi-file-earmark-text"></i>
                                </div>
                                <h6>${section}</h6>
                                <small class="text-muted">Page ${index + 2}</small>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="report-summary">
                        <h6>Report Summary</h6>
                        <div class="mb-2">
                            <strong>Company:</strong> ${companyName}
                        </div>
                        <div class="mb-2">
                            <strong>Report Type:</strong> ${reportInfo.title}
                        </div>
                        ${this.selectedReportType === 'compliance' ? `
                            <div class="mb-2">
                                <strong>Framework:</strong> ${this.selectedFramework}
                            </div>
                        ` : ''}
                        <div class="mb-2">
                            <strong>Estimated Pages:</strong> ${reportInfo.estimatedPages}
                        </div>
                        <div class="mb-2">
                            <strong>Security Score:</strong> 
                            <span class="badge bg-success">${this.assessmentData.overall_score}/100</span>
                        </div>
                        <div class="mb-2">
                            <strong>Business Value:</strong> ${this.assessmentData.cost_avoidance}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        previewDiv.style.display = 'block';
    }

    getReportInfo(type) {
        const reportTypes = {
            executive: {
                title: 'Executive Security Report',
                description: 'Board-ready presentation for C-suite executives with business impact analysis and ROI calculations',
                estimatedPages: '8-12 pages',
                sections: [
                    'Executive Summary',
                    'Security Posture Overview',
                    'Risk Assessment Summary',
                    'Business Impact Analysis',
                    'Strategic Recommendations'
                ]
            },
            technical: {
                title: 'Technical Security Report',
                description: 'Comprehensive technical analysis for IT teams with detailed findings and remediation roadmaps',
                estimatedPages: '20-30 pages',
                sections: [
                    'Assessment Methodology',
                    'Detailed Security Findings',
                    'Vulnerability Analysis',
                    'Compliance Assessment',
                    'Remediation Roadmap',
                    'Technical Controls',
                    'Implementation Guide'
                ]
            },
            compliance: {
                title: `${this.selectedFramework} Compliance Report`,
                description: 'Regulatory compliance assessment for auditors with framework mapping and gap analysis',
                estimatedPages: '15-25 pages',
                sections: [
                    'Compliance Executive Summary',
                    'Framework Mapping',
                    'Control Assessment',
                    'Gap Analysis',
                    'Remediation Roadmap',
                    'Compliance Timeline'
                ]
            }
        };
        
        return reportTypes[type] || reportTypes.executive;
    }

    async generateReport() {
        // Validate inputs
        if (!this.assessmentData) {
            this.showError('Please validate an assessment first');
            return;
        }
        
        if (!this.selectedReportType) {
            this.showError('Please select a report type');
            return;
        }
        
        const companyName = document.getElementById('companyName').value.trim();
        if (!companyName) {
            this.showError('Please enter company name');
            return;
        }

        try {
            this.showGenerationProgress();
            
            // Prepare request data
            const requestData = {
                assessment_id: this.assessmentData.assessment_id,
                report_type: this.selectedReportType,
                framework: this.selectedFramework,
                company_info: {
                    name: companyName,
                    industry: document.getElementById('industry').value,
                    contact_name: document.getElementById('contactName').value,
                    contact_email: document.getElementById('contactEmail').value
                }
            };

            // Generate report
            const response = await fetch('/api/security-assessment/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Report generation failed');
            }

            // Download PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Get filename from response headers or create one
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'Enterprise_Scanner_Report.pdf';
            if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/"/g, '');
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.hideGenerationProgress();
            this.showSuccessMessage('Professional report generated and downloaded successfully!');
            
            // Track event
            this.trackReportGeneration(this.selectedReportType, companyName);

        } catch (error) {
            this.hideGenerationProgress();
            this.showError(`Report generation failed: ${error.message}`);
        }
    }

    showGenerationProgress() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex';
        
        // Simulate progress steps
        this.simulateProgress();
    }

    hideGenerationProgress() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
        
        // Reset progress
        this.resetProgress();
    }

    simulateProgress() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        const progressBar = document.getElementById('progressBar');
        let currentStep = 0;
        
        const updateProgress = () => {
            if (currentStep > 0) {
                document.getElementById(steps[currentStep - 1]).classList.add('completed');
                document.getElementById(steps[currentStep - 1]).classList.remove('active');
            }
            
            if (currentStep < steps.length) {
                document.getElementById(steps[currentStep]).classList.add('active');
                progressBar.style.width = `${((currentStep + 1) / steps.length) * 100}%`;
                currentStep++;
                
                setTimeout(updateProgress, 1500 + Math.random() * 1000);
            }
        };
        
        updateProgress();
    }

    resetProgress() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            step.classList.remove('active', 'completed');
        });
        
        document.getElementById('step1').classList.add('active');
        document.getElementById('progressBar').style.width = '0%';
    }

    updateNavigationState() {
        // Update visual indicators for completed steps
        const hasAssessment = !!this.assessmentData;
        const hasReportType = !!this.selectedReportType;
        
        // This could be used to show step completion indicators
        // Implementation depends on desired UX
    }

    showLoading(message) {
        // Simple loading indicator
        const button = event?.target;
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>' + message;
        }
    }

    hideLoading() {
        // Reset button states
        document.querySelectorAll('button[disabled]').forEach(btn => {
            btn.disabled = false;
            // Reset button text based on context
        });
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
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

    trackReportGeneration(reportType, companyName) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', 'report_generated', {
                event_category: 'pdf_reports',
                report_type: reportType,
                company_name: companyName,
                demo_mode: this.demoMode
            });
        }

        console.log('Report Generated:', {
            type: reportType,
            company: companyName,
            demo: this.demoMode
        });
    }
}

// Global functions for HTML onclick handlers
function selectReportType(type) {
    window.pdfReportsManager.selectReportType(type);
}

function loadDemoAssessment() {
    window.pdfReportsManager.loadDemoAssessment();
}

function validateAssessment() {
    window.pdfReportsManager.validateAssessment();
}

function generateReport() {
    window.pdfReportsManager.generateReport();
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pdfReportsManager = new PDFReportsManager();
});

// Add CSS animation for loading spinner
const style = document.createElement('style');
style.textContent = `
    .spin {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);