/**
 * Interactive Pricing Table - Phase 2
 * Enterprise Scanner Website
 * Features: Monthly/Annual toggle, feature comparison, hover effects, animations
 */

class InteractivePricingTable {
    constructor(options = {}) {
        this.options = {
            defaultBilling: options.defaultBilling || 'annual', // 'monthly' or 'annual'
            animationDuration: options.animationDuration || 300,
            savingsPercentage: options.savingsPercentage || 20, // Annual discount
            currency: options.currency || '$',
            ...options
        };

        this.currentBilling = this.options.defaultBilling;
        this.plans = [];
        this.init();
    }

    init() {
        this.injectStyles();
        this.createPricingStructure();
        this.setupEventListeners();
    }

    injectStyles() {
        if (document.getElementById('pricing-table-styles')) return;

        const style = document.createElement('style');
        style.id = 'pricing-table-styles';
        style.textContent = `
            .pricing-container {
                padding: 80px 0;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                position: relative;
                overflow: hidden;
            }

            .pricing-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.5;
            }

            .pricing-header {
                text-align: center;
                margin-bottom: 60px;
                position: relative;
                z-index: 2;
            }

            .pricing-title {
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 1rem;
            }

            .pricing-subtitle {
                font-size: 1.2rem;
                color: rgba(255, 255, 255, 0.7);
                max-width: 600px;
                margin: 0 auto;
            }

            .billing-toggle {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }

            .billing-toggle-label {
                color: rgba(255, 255, 255, 0.6);
                font-weight: 500;
                font-size: 1rem;
                transition: all 0.3s ease;
            }

            .billing-toggle-label.active {
                color: #ffffff;
                font-weight: 600;
            }

            .toggle-switch {
                position: relative;
                width: 60px;
                height: 32px;
                background: rgba(30, 41, 59, 0.8);
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .toggle-switch:hover {
                background: rgba(30, 41, 59, 1);
            }

            .toggle-slider {
                position: absolute;
                top: 4px;
                left: 4px;
                width: 24px;
                height: 24px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-radius: 50%;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
            }

            .toggle-switch.annual .toggle-slider {
                transform: translateX(28px);
            }

            .savings-badge {
                background: linear-gradient(135deg, #10b981, #34d399);
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-left: 10px;
                animation: pulse-badge 2s infinite;
            }

            @keyframes pulse-badge {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            .pricing-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 30px;
                max-width: 1200px;
                margin: 0 auto;
                position: relative;
                z-index: 2;
                padding: 0 20px;
            }

            .pricing-card {
                background: rgba(30, 41, 59, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }

            .pricing-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                transform: scaleX(0);
                transform-origin: left;
                transition: transform 0.3s ease;
            }

            .pricing-card:hover {
                transform: translateY(-10px);
                border-color: rgba(59, 130, 246, 0.3);
                box-shadow: 0 20px 60px rgba(59, 130, 246, 0.2);
            }

            .pricing-card:hover::before {
                transform: scaleX(1);
            }

            .pricing-card.featured {
                background: rgba(59, 130, 246, 0.1);
                border: 2px solid #3b82f6;
                transform: scale(1.05);
            }

            .pricing-card.featured::before {
                transform: scaleX(1);
                background: linear-gradient(90deg, #3b82f6, #8b5cf6, #3b82f6);
                background-size: 200% 100%;
                animation: shimmer 3s infinite;
            }

            @keyframes shimmer {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .pricing-card.featured:hover {
                transform: scale(1.05) translateY(-10px);
                box-shadow: 0 30px 80px rgba(59, 130, 246, 0.4);
            }

            .plan-badge {
                position: absolute;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #fbbf24, #f59e0b);
                color: #0f172a;
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .plan-name {
                font-size: 1.5rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 10px;
            }

            .plan-description {
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.95rem;
                margin-bottom: 30px;
                min-height: 40px;
            }

            .plan-price {
                margin-bottom: 30px;
            }

            .price-amount {
                font-size: 3.5rem;
                font-weight: 700;
                color: #ffffff;
                line-height: 1;
                display: flex;
                align-items: flex-start;
                gap: 5px;
            }

            .price-currency {
                font-size: 2rem;
                margin-top: 10px;
            }

            .price-period {
                color: rgba(255, 255, 255, 0.5);
                font-size: 1rem;
                margin-top: 20px;
                font-weight: 400;
            }

            .price-original {
                color: rgba(255, 255, 255, 0.4);
                font-size: 1.2rem;
                text-decoration: line-through;
                margin-top: 5px;
            }

            .plan-features {
                list-style: none;
                padding: 0;
                margin: 30px 0;
            }

            .plan-feature {
                padding: 12px 0;
                color: rgba(255, 255, 255, 0.8);
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 0.95rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }

            .plan-feature:last-child {
                border-bottom: none;
            }

            .feature-icon {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10b981, #34d399);
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }

            .feature-icon::after {
                content: '✓';
                color: white;
                font-size: 12px;
                font-weight: bold;
            }

            .feature-unavailable {
                color: rgba(255, 255, 255, 0.3);
            }

            .feature-unavailable .feature-icon {
                background: rgba(255, 255, 255, 0.1);
            }

            .feature-unavailable .feature-icon::after {
                content: '×';
                font-size: 14px;
            }

            .plan-cta {
                width: 100%;
                padding: 16px 32px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 1rem;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
                position: relative;
                overflow: hidden;
            }

            .plan-cta::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.2);
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }

            .plan-cta:hover::before {
                width: 300px;
                height: 300px;
            }

            .plan-cta-primary {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
            }

            .plan-cta-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 30px rgba(59, 130, 246, 0.5);
            }

            .plan-cta-secondary {
                background: rgba(255, 255, 255, 0.05);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .plan-cta-secondary:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.3);
            }

            .plan-cta span {
                position: relative;
                z-index: 1;
            }

            /* Price transition animation */
            .price-amount {
                transition: all 0.3s ease;
            }

            .price-amount.updating {
                opacity: 0;
                transform: translateY(-10px);
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .pricing-grid {
                    grid-template-columns: 1fr;
                    padding: 0 15px;
                }

                .pricing-card.featured {
                    transform: scale(1);
                }

                .pricing-card.featured:hover {
                    transform: translateY(-10px);
                }

                .pricing-title {
                    font-size: 2rem;
                }

                .price-amount {
                    font-size: 2.5rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    createPricingStructure() {
        // Define pricing plans
        this.plans = [
            {
                name: 'Professional',
                description: 'Perfect for growing security teams',
                monthlyPrice: 2999,
                features: [
                    { text: 'Up to 100 assets monitored', available: true },
                    { text: 'AI-powered threat detection', available: true },
                    { text: 'Compliance automation (3 frameworks)', available: true },
                    { text: 'Executive reporting', available: true },
                    { text: 'Email support', available: true },
                    { text: 'API access', available: true },
                    { text: 'Custom integrations', available: false },
                    { text: 'Dedicated account manager', available: false },
                    { text: 'Advanced threat hunting', available: false }
                ],
                cta: 'Start Professional Trial',
                ctaClass: 'plan-cta-secondary'
            },
            {
                name: 'Enterprise',
                description: 'For Fortune 500 organizations',
                monthlyPrice: 7999,
                featured: true,
                badge: 'Most Popular',
                features: [
                    { text: 'Unlimited assets monitored', available: true },
                    { text: 'AI-powered threat detection', available: true },
                    { text: 'Compliance automation (all frameworks)', available: true },
                    { text: 'Executive & technical reporting', available: true },
                    { text: '24/7 priority support', available: true },
                    { text: 'Full API access', available: true },
                    { text: 'Custom integrations', available: true },
                    { text: 'Dedicated account manager', available: true },
                    { text: 'Advanced threat hunting', available: true }
                ],
                cta: 'Start Enterprise Trial',
                ctaClass: 'plan-cta-primary'
            },
            {
                name: 'Ultimate',
                description: 'Maximum security for critical infrastructure',
                monthlyPrice: 14999,
                features: [
                    { text: 'Unlimited assets + multi-tenant', available: true },
                    { text: 'AI + ML advanced analytics', available: true },
                    { text: 'All compliance frameworks + custom', available: true },
                    { text: 'Custom reporting & dashboards', available: true },
                    { text: 'White-glove support', available: true },
                    { text: 'Full API + webhooks', available: true },
                    { text: 'Unlimited custom integrations', available: true },
                    { text: 'Dedicated security team', available: true },
                    { text: 'Proactive threat hunting & response', available: true }
                ],
                cta: 'Contact Sales',
                ctaClass: 'plan-cta-secondary'
            }
        ];
    }

    setupEventListeners() {
        // Toggle switch event
        document.addEventListener('click', (e) => {
            if (e.target.closest('.toggle-switch, .billing-toggle-label')) {
                this.toggleBilling();
            }

            // CTA button clicks
            if (e.target.closest('.plan-cta')) {
                const planName = e.target.closest('.pricing-card').dataset.plan;
                this.handlePlanSelection(planName);
            }
        });
    }

    toggleBilling() {
        this.currentBilling = this.currentBilling === 'monthly' ? 'annual' : 'monthly';
        this.updatePrices();
        this.updateToggleUI();
    }

    updatePrices() {
        const priceElements = document.querySelectorAll('.price-amount');
        
        priceElements.forEach((el, index) => {
            // Add updating class for animation
            el.classList.add('updating');
            
            setTimeout(() => {
                const plan = this.plans[index];
                const price = this.currentBilling === 'annual' 
                    ? Math.round(plan.monthlyPrice * 12 * (1 - this.options.savingsPercentage / 100))
                    : plan.monthlyPrice;
                
                el.innerHTML = `
                    <span class="price-currency">${this.options.currency}</span>
                    ${price.toLocaleString()}
                `;
                
                // Update period text
                const periodEl = el.parentElement.querySelector('.price-period');
                if (periodEl) {
                    periodEl.textContent = this.currentBilling === 'annual' ? '/year' : '/month';
                }

                // Show/hide original price
                const originalEl = el.parentElement.querySelector('.price-original');
                if (this.currentBilling === 'annual' && originalEl) {
                    const originalPrice = plan.monthlyPrice * 12;
                    originalEl.textContent = `${this.options.currency}${originalPrice.toLocaleString()}`;
                    originalEl.style.display = 'block';
                } else if (originalEl) {
                    originalEl.style.display = 'none';
                }
                
                el.classList.remove('updating');
            }, 150);
        });
    }

    updateToggleUI() {
        const toggleSwitch = document.querySelector('.toggle-switch');
        const monthlyLabel = document.querySelector('.billing-toggle-label[data-billing="monthly"]');
        const annualLabel = document.querySelector('.billing-toggle-label[data-billing="annual"]');
        
        if (this.currentBilling === 'annual') {
            toggleSwitch?.classList.add('annual');
            monthlyLabel?.classList.remove('active');
            annualLabel?.classList.add('active');
        } else {
            toggleSwitch?.classList.remove('annual');
            monthlyLabel?.classList.add('active');
            annualLabel?.classList.remove('active');
        }
    }

    handlePlanSelection(planName) {
        // Show loading
        const loadingId = window.showLoading('Processing your selection...');
        
        setTimeout(() => {
            window.hideLoading(loadingId);
            
            // Show success toast
            window.showToast.success(
                `${planName} Plan Selected`,
                'Redirecting you to the demo portal...'
            );
            
            // In production, redirect to signup/demo
            setTimeout(() => {
                console.log(`Would redirect to signup for: ${planName} - ${this.currentBilling}`);
                // window.location.href = `/demo-portal?plan=${planName}&billing=${this.currentBilling}`;
            }, 1500);
        }, 1000);
    }

    render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container #${containerId} not found`);
            return;
        }

        const annualSavings = Math.round(this.options.savingsPercentage);
        
        const html = `
            <div class="pricing-container">
                <div class="container">
                    <div class="pricing-header">
                        <h2 class="pricing-title">Enterprise Security Pricing</h2>
                        <p class="pricing-subtitle">
                            Transparent pricing designed for Fortune 500 organizations. 
                            All plans include our complete security platform.
                        </p>
                        <div class="billing-toggle">
                            <span class="billing-toggle-label ${this.currentBilling === 'monthly' ? 'active' : ''}" 
                                  data-billing="monthly">Monthly</span>
                            <div class="toggle-switch ${this.currentBilling === 'annual' ? 'annual' : ''}">
                                <div class="toggle-slider"></div>
                            </div>
                            <span class="billing-toggle-label ${this.currentBilling === 'annual' ? 'active' : ''}" 
                                  data-billing="annual">Annual</span>
                            <span class="savings-badge">Save ${annualSavings}%</span>
                        </div>
                    </div>
                    
                    <div class="pricing-grid">
                        ${this.plans.map(plan => this.renderPlan(plan)).join('')}
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        this.updatePrices();
    }

    renderPlan(plan) {
        const price = this.currentBilling === 'annual' 
            ? Math.round(plan.monthlyPrice * 12 * (1 - this.options.savingsPercentage / 100))
            : plan.monthlyPrice;
        
        const originalPrice = plan.monthlyPrice * 12;
        
        return `
            <div class="pricing-card ${plan.featured ? 'featured' : ''}" data-card-3d data-plan="${plan.name}">
                ${plan.badge ? `<div class="plan-badge">${plan.badge}</div>` : ''}
                
                <h3 class="plan-name">${plan.name}</h3>
                <p class="plan-description">${plan.description}</p>
                
                <div class="plan-price">
                    <div class="price-amount">
                        <span class="price-currency">${this.options.currency}</span>
                        ${price.toLocaleString()}
                    </div>
                    <div class="price-period">${this.currentBilling === 'annual' ? '/year' : '/month'}</div>
                    ${this.currentBilling === 'annual' ? `
                        <div class="price-original">${this.options.currency}${originalPrice.toLocaleString()}</div>
                    ` : ''}
                </div>
                
                <ul class="plan-features">
                    ${plan.features.map(feature => `
                        <li class="plan-feature ${!feature.available ? 'feature-unavailable' : ''}">
                            <div class="feature-icon"></div>
                            <span>${feature.text}</span>
                        </li>
                    `).join('')}
                </ul>
                
                <button class="plan-cta ${plan.ctaClass}">
                    <span>${plan.cta}</span>
                </button>
            </div>
        `;
    }
}

// Global instance
window.interactivePricing = new InteractivePricingTable({
    defaultBilling: 'annual',
    savingsPercentage: 20
});

// Auto-render if pricing container exists
document.addEventListener('DOMContentLoaded', () => {
    const pricingContainer = document.getElementById('pricing-section');
    if (pricingContainer) {
        window.interactivePricing.render('pricing-section');
    }
});
