/**
 * Enhanced ROI Calculator with Chart.js Visualization
 * Enterprise Scanner Website
 * Features: Real-time calculation, interactive charts, PDF export, email functionality
 */

class EnhancedROICalculator {
    constructor(options = {}) {
        this.options = {
            formId: options.formId || 'roi-form',
            resultsId: options.resultsId || 'roi-results',
            chartContainerId: options.chartContainerId || 'roi-chart-container',
            animationDuration: options.animationDuration || 1000,
            realTimeCalculation: options.realTimeCalculation !== false,
            ...options
        };

        this.form = null;
        this.resultsSection = null;
        this.chartContainer = null;
        this.charts = {};
        this.currentResults = null;

        this.init();
    }

    init() {
        this.form = document.getElementById(this.options.formId);
        this.resultsSection = document.getElementById(this.options.resultsId);
        
        if (!this.form) {
            console.warn('EnhancedROICalculator: Form not found');
            return;
        }

        this.injectStyles();
        this.enhanceForm();
        this.setupEventListeners();
        
        // Create chart container if it doesn't exist
        if (!document.getElementById(this.options.chartContainerId)) {
            this.createChartContainer();
        }
    }

    injectStyles() {
        if (document.getElementById('enhanced-roi-calculator-styles')) return;

        const style = document.createElement('style');
        style.id = 'enhanced-roi-calculator-styles';
        style.textContent = `
            .roi-calculator-enhanced {
                position: relative;
            }

            .roi-form-group {
                margin-bottom: 1.5rem;
            }

            .roi-form-control {
                transition: all 0.3s ease;
            }

            .roi-form-control:focus {
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                border-color: #3b82f6;
            }

            .roi-results-enhanced {
                background: rgba(30, 41, 59, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 40px;
                margin-top: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            }

            .roi-metric-card {
                background: rgba(15, 23, 42, 0.6);
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
            }

            .roi-metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
            }

            .roi-metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 16px 0;
            }

            .roi-metric-label {
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.9rem;
                font-weight: 500;
            }

            .roi-chart-container {
                background: rgba(15, 23, 42, 0.4);
                border-radius: 12px;
                padding: 30px;
                margin-top: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .roi-chart-wrapper {
                position: relative;
                height: 300px;
                margin-bottom: 20px;
            }

            .roi-actions {
                display: flex;
                gap: 12px;
                margin-top: 30px;
                flex-wrap: wrap;
            }

            .roi-action-btn {
                flex: 1;
                min-width: 150px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
            }

            .roi-action-btn-primary {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
            }

            .roi-action-btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            }

            .roi-action-btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .roi-action-btn-secondary:hover {
                background: rgba(255, 255, 255, 0.15);
            }

            .roi-breakdown {
                margin-top: 30px;
            }

            .roi-breakdown-item {
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .roi-breakdown-item:last-child {
                border-bottom: none;
            }

            .roi-breakdown-label {
                color: rgba(255, 255, 255, 0.8);
            }

            .roi-breakdown-value {
                color: #3b82f6;
                font-weight: 600;
            }

            @media (max-width: 768px) {
                .roi-metric-value {
                    font-size: 2rem;
                }

                .roi-actions {
                    flex-direction: column;
                }

                .roi-action-btn {
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    }

    enhanceForm() {
        this.form.classList.add('roi-calculator-enhanced');
        
        if (this.resultsSection) {
            this.resultsSection.classList.add('roi-results-enhanced');
        }
    }

    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculate();
        });

        // Real-time calculation
        if (this.options.realTimeCalculation) {
            const inputs = this.form.querySelectorAll('select, input');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    if (this.isFormValid()) {
                        this.calculate(true); // Silent calculation
                    }
                });
            });
        }
    }

    isFormValid() {
        const companySize = this.form.querySelector('#company-size')?.value;
        const industry = this.form.querySelector('#industry')?.value;
        const currentBudget = this.form.querySelector('#current-budget')?.value;
        const complianceNeeds = this.form.querySelector('#compliance-needs')?.value;

        return companySize && industry && currentBudget && complianceNeeds;
    }

    calculate(silent = false) {
        if (!this.isFormValid()) {
            if (!silent) {
                showToast.warning('Incomplete Form', 'Please fill in all fields to calculate your ROI.');
            }
            return;
        }

        if (!silent) {
            const loadingId = showLoading('Calculating your ROI...', { style: 'spinner' });
            
            setTimeout(() => {
                this.performCalculation();
                hideLoading(loadingId);
                showToast.success('ROI Calculated!', 'Your personalized analysis is ready');
            }, 1500);
        } else {
            this.performCalculation();
        }
    }

    performCalculation() {
        const companySize = this.form.querySelector('#company-size').value;
        const industry = this.form.querySelector('#industry').value;
        const currentBudget = this.form.querySelector('#current-budget').value;
        const complianceNeeds = this.form.querySelector('#compliance-needs').value;

        // ROI Calculation Logic
        let baseSavings = 0;
        let multiplier = 1;

        // Company size factor
        switch(companySize) {
            case 'small': baseSavings = 250000; break;
            case 'medium': baseSavings = 850000; break;
            case 'large': baseSavings = 1800000; break;
            case 'enterprise': baseSavings = 3200000; break;
        }

        // Industry factor
        switch(industry) {
            case 'financial': multiplier *= 1.5; break;
            case 'healthcare': multiplier *= 1.3; break;
            case 'technology': multiplier *= 1.2; break;
            case 'retail': multiplier *= 1.1; break;
            case 'government': multiplier *= 1.4; break;
            default: multiplier *= 1.0;
        }

        // Budget factor
        switch(currentBudget) {
            case '100k': multiplier *= 0.8; break;
            case '500k': multiplier *= 1.0; break;
            case '1m': multiplier *= 1.2; break;
            case '5m': multiplier *= 1.5; break;
            case '10m': multiplier *= 2.0; break;
        }

        // Compliance factor
        switch(complianceNeeds) {
            case 'basic': multiplier *= 1.0; break;
            case 'moderate': multiplier *= 1.2; break;
            case 'advanced': multiplier *= 1.4; break;
            case 'comprehensive': multiplier *= 1.6; break;
        }

        const annualSavings = Math.round(baseSavings * multiplier);
        const investmentCost = Math.round(annualSavings * 0.15);
        const roiPercentage = Math.round(((annualSavings - investmentCost) / investmentCost) * 100);
        const paybackMonths = Math.ceil(investmentCost / (annualSavings / 12));
        const threeYearSavings = annualSavings * 3;
        const fiveYearSavings = annualSavings * 5;

        this.currentResults = {
            annualSavings,
            investmentCost,
            roiPercentage,
            paybackMonths,
            threeYearSavings,
            fiveYearSavings,
            companySize,
            industry
        };

        this.displayResults();
        this.createCharts();
    }

    displayResults() {
        const { annualSavings, investmentCost, roiPercentage, paybackMonths, threeYearSavings, fiveYearSavings } = this.currentResults;

        // Update metric cards with counter animations
        this.updateMetricCard('annual-savings', annualSavings, '$', '', 0);
        this.updateMetricCard('roi-percentage', roiPercentage, '', '%', 0);
        this.updateMetricCard('payback-period', paybackMonths, '', ' months', 0);

        // Show results section
        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
            this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Update breakdown if it exists
        this.updateBreakdown();
    }

    updateMetricCard(id, value, prefix = '', suffix = '', decimals = 0) {
        const element = document.getElementById(id);
        if (element) {
            // Animate the number
            element.setAttribute('data-counter', value);
            element.setAttribute('data-prefix', prefix);
            element.setAttribute('data-suffix', suffix);
            element.setAttribute('data-decimals', decimals);
            
            // Reset and animate
            if (window.counterAnimations) {
                window.counterAnimations.reset(element);
                setTimeout(() => {
                    const counter = window.counterAnimations.counters.get(element) || {};
                    window.counterAnimations.animateCounter(element, {
                        ...counter,
                        target: value,
                        prefix,
                        suffix,
                        decimals
                    });
                }, 100);
            } else {
                element.textContent = `${prefix}${value.toLocaleString()}${suffix}`;
            }
        }
    }

    updateBreakdown() {
        const breakdownContainer = document.getElementById('roi-breakdown');
        if (!breakdownContainer) return;

        const { annualSavings, investmentCost, threeYearSavings, fiveYearSavings } = this.currentResults;

        breakdownContainer.innerHTML = `
            <div class="roi-breakdown-item">
                <span class="roi-breakdown-label">Initial Investment</span>
                <span class="roi-breakdown-value">$${investmentCost.toLocaleString()}</span>
            </div>
            <div class="roi-breakdown-item">
                <span class="roi-breakdown-label">Year 1 Savings</span>
                <span class="roi-breakdown-value">$${annualSavings.toLocaleString()}</span>
            </div>
            <div class="roi-breakdown-item">
                <span class="roi-breakdown-label">3-Year Savings</span>
                <span class="roi-breakdown-value">$${threeYearSavings.toLocaleString()}</span>
            </div>
            <div class="roi-breakdown-item">
                <span class="roi-breakdown-label">5-Year Savings</span>
                <span class="roi-breakdown-value">$${fiveYearSavings.toLocaleString()}</span>
            </div>
        `;
    }

    createChartContainer() {
        if (!this.resultsSection) return;

        const chartContainer = document.createElement('div');
        chartContainer.id = this.options.chartContainerId;
        chartContainer.className = 'roi-chart-container';
        chartContainer.innerHTML = `
            <h4 class="text-white mb-4">ROI Visualization</h4>
            <div class="roi-chart-wrapper">
                <canvas id="roi-savings-chart"></canvas>
            </div>
            <div class="roi-chart-wrapper">
                <canvas id="roi-comparison-chart"></canvas>
            </div>
        `;

        this.resultsSection.appendChild(chartContainer);
        this.chartContainer = chartContainer;
    }

    async createCharts() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded. Include Chart.js library.');
            return;
        }

        const { annualSavings, investmentCost, threeYearSavings, fiveYearSavings } = this.currentResults;

        // Destroy existing charts
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};

        // Savings Over Time Chart
        const savingsCtx = document.getElementById('roi-savings-chart');
        if (savingsCtx) {
            this.charts.savings = new Chart(savingsCtx, {
                type: 'line',
                data: {
                    labels: ['Initial', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
                    datasets: [{
                        label: 'Cumulative Savings',
                        data: [
                            -investmentCost,
                            annualSavings - investmentCost,
                            annualSavings * 2 - investmentCost,
                            threeYearSavings - investmentCost,
                            annualSavings * 4 - investmentCost,
                            fiveYearSavings - investmentCost
                        ],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    },
                    scales: {
                        y: {
                            ticks: { 
                                color: 'rgba(255, 255, 255, 0.7)',
                                callback: (value) => '$' + (value / 1000000).toFixed(1) + 'M'
                            },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        x: {
                            ticks: { color: 'rgba(255, 255, 255, 0.7)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    }
                }
            });
        }

        // Comparison Chart
        const comparisonCtx = document.getElementById('roi-comparison-chart');
        if (comparisonCtx) {
            this.charts.comparison = new Chart(comparisonCtx, {
                type: 'bar',
                data: {
                    labels: ['Investment', 'Year 1', 'Year 3', 'Year 5'],
                    datasets: [{
                        label: 'Amount ($)',
                        data: [investmentCost, annualSavings, threeYearSavings, fiveYearSavings],
                        backgroundColor: [
                            'rgba(239, 68, 68, 0.7)',
                            'rgba(59, 130, 246, 0.7)',
                            'rgba(139, 92, 246, 0.7)',
                            'rgba(16, 185, 129, 0.7)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    },
                    scales: {
                        y: {
                            ticks: { 
                                color: 'rgba(255, 255, 255, 0.7)',
                                callback: (value) => '$' + (value / 1000000).toFixed(1) + 'M'
                            },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        x: {
                            ticks: { color: 'rgba(255, 255, 255, 0.7)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    }
                }
            });
        }
    }

    exportToPDF() {
        showToast.info('PDF Export', 'PDF generation feature coming soon!');
    }

    emailResults() {
        const { annualSavings, roiPercentage } = this.currentResults;
        const subject = encodeURIComponent('Enterprise Scanner ROI Analysis');
        const body = encodeURIComponent(
            `I've calculated my potential ROI with Enterprise Scanner:\n\n` +
            `Annual Savings: $${annualSavings.toLocaleString()}\n` +
            `ROI: ${roiPercentage}%\n\n` +
            `I'd like to learn more about your platform.`
        );
        window.location.href = `mailto:sales@enterprisescanner.com?subject=${subject}&body=${body}`;
    }

    scheduleDemo() {
        window.location.href = 'mailto:sales@enterprisescanner.com?subject=Schedule%20Demo';
    }

    destroy() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
        
        const styles = document.getElementById('enhanced-roi-calculator-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedROICalculator = new EnhancedROICalculator({
        realTimeCalculation: true
    });
});
