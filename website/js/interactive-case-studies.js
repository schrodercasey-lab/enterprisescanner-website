/**
 * Interactive Case Studies - Phase 2
 * Enterprise Scanner Website
 * Features: Before/after sliders, metric visualizations, testimonials, timeline
 */

class InteractiveCaseStudies {
    constructor(options = {}) {
        this.options = {
            containerId: options.containerId || 'case-studies-container',
            autoPlay: options.autoPlay !== false,
            autoPlayInterval: options.autoPlayInterval || 5000,
            animationDuration: options.animationDuration || 600,
            ...options
        };

        this.currentSlide = 0;
        this.isAnimating = false;
        this.autoPlayTimer = null;
        this.caseStudies = this.getCaseStudiesData();

        this.init();
    }

    init() {
        this.injectStyles();
        this.createCaseStudiesUI();
        this.attachEventListeners();
        
        if (this.options.autoPlay) {
            this.startAutoPlay();
        }

        // Initialize any existing case study elements on the page
        this.initializeExistingElements();
    }

    getCaseStudiesData() {
        return [
            {
                id: 'global-finance',
                company: 'Global Financial Services Corp',
                industry: 'Financial Services',
                size: '50,000+ employees',
                logo: 'assets/logos/finance-corp.svg',
                challenge: 'Legacy security infrastructure struggling with modern threats. Multiple compliance violations and $12M in potential regulatory fines.',
                solution: 'Comprehensive Enterprise Scanner deployment with AI-powered threat detection and automated compliance monitoring.',
                timeline: '6 months',
                metrics: {
                    threatDetection: { before: 67, after: 98.8, unit: '%' },
                    responseTime: { before: 4.5, after: 0.3, unit: 'hours' },
                    complianceScore: { before: 72, after: 99, unit: '%' },
                    costSavings: { before: 0, after: 3.2, unit: '$M' }
                },
                testimonial: {
                    quote: "Enterprise Scanner transformed our security posture from reactive to proactive. The ROI was evident within 90 days.",
                    author: "Sarah Chen",
                    title: "Chief Information Security Officer",
                    image: "assets/testimonials/sarah-chen.jpg"
                },
                results: [
                    "98.8% threat detection accuracy",
                    "$3.2M annual cost savings",
                    "Zero compliance violations in 12 months",
                    "15-minute average assessment time"
                ],
                timelineEvents: [
                    { month: 1, event: "Initial assessment & planning", icon: "clipboard-check" },
                    { month: 2, event: "Platform deployment & integration", icon: "gear" },
                    { month: 3, event: "Team training & SOC setup", icon: "people" },
                    { month: 4, event: "AI model optimization", icon: "cpu" },
                    { month: 5, event: "Full production rollout", icon: "rocket" },
                    { month: 6, event: "100% compliance achieved", icon: "trophy" }
                ]
            },
            {
                id: 'healthcare-network',
                company: 'National Healthcare Network',
                industry: 'Healthcare',
                size: '25,000+ employees',
                logo: 'assets/logos/healthcare-network.svg',
                challenge: 'HIPAA compliance gaps and inadequate protection of sensitive patient data. 3 security breaches in the previous year.',
                solution: 'Enterprise Scanner with healthcare-specific compliance templates and real-time patient data monitoring.',
                timeline: '8 months',
                metrics: {
                    dataBreaches: { before: 3, after: 0, unit: 'incidents' },
                    hipaaCompliance: { before: 78, after: 100, unit: '%' },
                    patientDataSecurity: { before: 82, after: 99.5, unit: '%' },
                    costSavings: { before: 0, after: 5.8, unit: '$M' }
                },
                testimonial: {
                    quote: "Patient safety is our top priority. Enterprise Scanner gave us the confidence that their data is truly protected.",
                    author: "Dr. Michael Rodriguez",
                    title: "Chief Medical Information Officer",
                    image: "assets/testimonials/michael-rodriguez.jpg"
                },
                results: [
                    "Zero security breaches in 18 months",
                    "100% HIPAA compliance maintained",
                    "$5.8M in avoided breach costs",
                    "99.5% patient data security score"
                ],
                timelineEvents: [
                    { month: 1, event: "HIPAA compliance audit", icon: "shield-check" },
                    { month: 2, event: "Risk assessment & gap analysis", icon: "exclamation-triangle" },
                    { month: 3, event: "Platform customization for healthcare", icon: "hospital" },
                    { month: 4, event: "Patient data encryption upgrade", icon: "lock" },
                    { month: 6, event: "Staff security training program", icon: "mortarboard" },
                    { month: 8, event: "Full HIPAA compliance certification", icon: "award" }
                ]
            },
            {
                id: 'tech-giant',
                company: 'Global Technology Corporation',
                industry: 'Technology',
                size: '100,000+ employees',
                logo: 'assets/logos/tech-corp.svg',
                challenge: 'Massive attack surface with cloud infrastructure across 40+ countries. Inability to detect zero-day threats.',
                solution: 'Enterprise Scanner with advanced AI algorithms and global threat intelligence integration.',
                timeline: '12 months',
                metrics: {
                    zeroDayDetection: { before: 45, after: 94, unit: '%' },
                    globalCoverage: { before: 60, after: 98, unit: '%' },
                    incidentResponse: { before: 6.2, after: 0.5, unit: 'hours' },
                    costSavings: { before: 0, after: 4.1, unit: '$M' }
                },
                testimonial: {
                    quote: "The AI-powered threat detection is years ahead of anything else on the market. It's like having a crystal ball for cybersecurity.",
                    author: "James Park",
                    title: "VP of Global Security",
                    image: "assets/testimonials/james-park.jpg"
                },
                results: [
                    "94% zero-day threat detection rate",
                    "98% global infrastructure coverage",
                    "$4.1M annual operational savings",
                    "30-minute average incident response"
                ],
                timelineEvents: [
                    { month: 1, event: "Global infrastructure assessment", icon: "globe" },
                    { month: 3, event: "AI model training on historical data", icon: "robot" },
                    { month: 5, event: "Multi-region deployment", icon: "diagram-3" },
                    { month: 7, event: "Threat intelligence integration", icon: "lightning" },
                    { month: 9, event: "Zero-day detection optimization", icon: "bug" },
                    { month: 12, event: "Enterprise-wide protection active", icon: "shield-fill-check" }
                ]
            }
        ];
    }

    injectStyles() {
        if (document.getElementById('case-studies-styles')) return;

        const style = document.createElement('style');
        style.id = 'case-studies-styles';
        style.textContent = `
            /* Case Studies Container */
            .case-studies-wrapper {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                padding: 80px 0;
                position: relative;
                overflow: hidden;
            }

            .case-study-card {
                background: rgba(30, 41, 59, 0.6);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 50px;
                margin: 30px 0;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .case-study-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
            }

            /* Company Header */
            .case-study-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 40px;
                padding-bottom: 30px;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }

            .company-info {
                flex: 1;
            }

            .company-logo {
                width: 120px;
                height: 60px;
                object-fit: contain;
                margin-bottom: 15px;
            }

            .company-name {
                font-size: 1.8rem;
                font-weight: 700;
                color: white;
                margin-bottom: 10px;
            }

            .company-meta {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }

            .meta-item {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #94a3b8;
                font-size: 0.95rem;
            }

            .meta-item i {
                color: #3b82f6;
            }

            /* Before/After Slider */
            .before-after-container {
                position: relative;
                margin: 40px 0;
                border-radius: 16px;
                overflow: hidden;
                background: rgba(15, 23, 42, 0.8);
            }

            .comparison-slider {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                padding: 40px;
            }

            .metric-comparison {
                text-align: center;
                padding: 30px;
                background: rgba(30, 41, 59, 0.6);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .metric-comparison::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, #ef4444, #3b82f6);
                transform: scaleX(0);
                transition: transform 0.6s ease;
            }

            .metric-comparison.revealed::before {
                transform: scaleX(1);
            }

            .metric-comparison:hover {
                transform: translateY(-5px);
                border-color: rgba(59, 130, 246, 0.5);
            }

            .metric-label {
                font-size: 1rem;
                color: #94a3b8;
                margin-bottom: 20px;
                font-weight: 500;
            }

            .metric-values {
                display: flex;
                justify-content: space-around;
                align-items: center;
                gap: 20px;
            }

            .metric-value {
                flex: 1;
            }

            .value-label {
                font-size: 0.8rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
            }

            .value-number {
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 5px;
                display: block;
            }

            .value-number.before {
                color: #ef4444;
            }

            .value-number.after {
                color: #10b981;
            }

            .value-unit {
                font-size: 0.9rem;
                color: #94a3b8;
            }

            .metric-arrow {
                font-size: 2rem;
                color: #10b981;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            /* Animated Counter for Metrics */
            .metric-value[data-animate="true"] .value-number {
                opacity: 0;
                transform: translateY(20px);
                animation: countUp 1s ease-out forwards;
            }

            @keyframes countUp {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Timeline */
            .timeline-container {
                margin: 50px 0;
                position: relative;
            }

            .timeline-header {
                text-align: center;
                margin-bottom: 40px;
            }

            .timeline-header h3 {
                font-size: 1.8rem;
                color: white;
                margin-bottom: 10px;
            }

            .timeline-duration {
                color: #94a3b8;
                font-size: 1.1rem;
            }

            .timeline {
                position: relative;
                padding: 40px 0;
            }

            .timeline::before {
                content: '';
                position: absolute;
                left: 50%;
                top: 0;
                bottom: 0;
                width: 3px;
                background: linear-gradient(180deg, #3b82f6, #8b5cf6, #ec4899);
                transform: translateX(-50%);
            }

            .timeline-event {
                display: flex;
                align-items: center;
                margin-bottom: 50px;
                position: relative;
                opacity: 0;
                transform: translateX(-30px);
                transition: all 0.6s ease;
            }

            .timeline-event.revealed {
                opacity: 1;
                transform: translateX(0);
            }

            .timeline-event:nth-child(even) {
                flex-direction: row-reverse;
                transform: translateX(30px);
            }

            .timeline-event:nth-child(even).revealed {
                transform: translateX(0);
            }

            .timeline-content {
                flex: 1;
                padding: 25px;
                background: rgba(30, 41, 59, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin: 0 30px;
                position: relative;
            }

            .timeline-event:nth-child(odd) .timeline-content {
                text-align: right;
            }

            .timeline-month {
                font-size: 1.3rem;
                font-weight: 700;
                color: #3b82f6;
                margin-bottom: 10px;
            }

            .timeline-event-text {
                color: #e2e8f0;
                font-size: 1.05rem;
            }

            .timeline-icon {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                color: white;
                box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
                position: relative;
                z-index: 2;
            }

            /* Testimonial */
            .testimonial-section {
                margin: 50px 0;
                padding: 40px;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
                border-radius: 16px;
                border: 1px solid rgba(59, 130, 246, 0.3);
                position: relative;
                overflow: hidden;
            }

            .testimonial-section::before {
                content: '"';
                position: absolute;
                top: -20px;
                left: 20px;
                font-size: 120px;
                color: rgba(59, 130, 246, 0.2);
                font-family: Georgia, serif;
                line-height: 1;
            }

            .testimonial-quote {
                font-size: 1.4rem;
                color: white;
                line-height: 1.8;
                margin-bottom: 30px;
                font-style: italic;
                position: relative;
                z-index: 1;
            }

            .testimonial-author {
                display: flex;
                align-items: center;
                gap: 20px;
            }

            .author-image {
                width: 70px;
                height: 70px;
                border-radius: 50%;
                border: 3px solid #3b82f6;
                object-fit: cover;
            }

            .author-info {
                flex: 1;
            }

            .author-name {
                font-size: 1.2rem;
                font-weight: 600;
                color: white;
                margin-bottom: 5px;
            }

            .author-title {
                color: #94a3b8;
                font-size: 1rem;
            }

            /* Results Grid */
            .results-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }

            .result-item {
                padding: 25px;
                background: rgba(16, 185, 129, 0.1);
                border-left: 4px solid #10b981;
                border-radius: 8px;
                display: flex;
                align-items: center;
                gap: 15px;
                transition: all 0.3s ease;
            }

            .result-item:hover {
                background: rgba(16, 185, 129, 0.2);
                transform: translateX(5px);
            }

            .result-icon {
                font-size: 1.8rem;
                color: #10b981;
            }

            .result-text {
                color: #e2e8f0;
                font-size: 1.05rem;
                font-weight: 500;
            }

            /* Case Study Navigation */
            .case-study-nav {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin-top: 40px;
            }

            .case-study-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .case-study-dot:hover {
                background: rgba(255, 255, 255, 0.6);
                transform: scale(1.3);
            }

            .case-study-dot.active {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                transform: scale(1.5);
                box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
            }

            /* Navigation Arrows */
            .case-study-arrows {
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
            }

            .nav-arrow {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                border: none;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            }

            .nav-arrow:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 25px rgba(59, 130, 246, 0.6);
            }

            .nav-arrow:disabled {
                opacity: 0.3;
                cursor: not-allowed;
            }

            /* Mobile Responsive */
            @media (max-width: 768px) {
                .case-study-card {
                    padding: 30px 20px;
                }

                .case-study-header {
                    flex-direction: column;
                    text-align: center;
                }

                .timeline::before {
                    left: 30px;
                }

                .timeline-event,
                .timeline-event:nth-child(even) {
                    flex-direction: column;
                    align-items: flex-start;
                    padding-left: 80px;
                }

                .timeline-content {
                    margin: 20px 0 0 0;
                    text-align: left !important;
                }

                .timeline-icon {
                    position: absolute;
                    left: 0;
                }

                .comparison-slider {
                    grid-template-columns: 1fr;
                    padding: 20px;
                }

                .metric-values {
                    flex-direction: column;
                    gap: 10px;
                }

                .metric-arrow {
                    transform: rotate(90deg);
                }

                .company-name {
                    font-size: 1.4rem;
                }

                .testimonial-quote {
                    font-size: 1.1rem;
                }
            }

            /* Animation delays for stagger effect */
            .timeline-event:nth-child(1) { transition-delay: 0.1s; }
            .timeline-event:nth-child(2) { transition-delay: 0.2s; }
            .timeline-event:nth-child(3) { transition-delay: 0.3s; }
            .timeline-event:nth-child(4) { transition-delay: 0.4s; }
            .timeline-event:nth-child(5) { transition-delay: 0.5s; }
            .timeline-event:nth-child(6) { transition-delay: 0.6s; }
        `;
        document.head.appendChild(style);
    }

    createCaseStudiesUI() {
        const container = document.getElementById(this.options.containerId);
        if (!container) return;

        container.innerHTML = this.generateCaseStudiesHTML();
        this.setupObservers();
    }

    generateCaseStudiesHTML() {
        const caseStudy = this.caseStudies[this.currentSlide];
        
        return `
            <div class="case-study-card" data-case-study-id="${caseStudy.id}">
                ${this.generateHeaderHTML(caseStudy)}
                ${this.generateMetricsHTML(caseStudy)}
                ${this.generateTimelineHTML(caseStudy)}
                ${this.generateTestimonialHTML(caseStudy)}
                ${this.generateResultsHTML(caseStudy)}
            </div>
            ${this.generateNavigationHTML()}
        `;
    }

    generateHeaderHTML(caseStudy) {
        return `
            <div class="case-study-header">
                <div class="company-info">
                    <h2 class="company-name">${caseStudy.company}</h2>
                    <div class="company-meta">
                        <span class="meta-item">
                            <i class="bi bi-building"></i>
                            ${caseStudy.industry}
                        </span>
                        <span class="meta-item">
                            <i class="bi bi-people"></i>
                            ${caseStudy.size}
                        </span>
                        <span class="meta-item">
                            <i class="bi bi-clock"></i>
                            ${caseStudy.timeline} implementation
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    generateMetricsHTML(caseStudy) {
        const metrics = Object.entries(caseStudy.metrics);
        
        return `
            <div class="before-after-container">
                <div class="comparison-slider">
                    ${metrics.map(([key, data]) => `
                        <div class="metric-comparison" data-metric="${key}">
                            <div class="metric-label">${this.formatMetricLabel(key)}</div>
                            <div class="metric-values">
                                <div class="metric-value">
                                    <div class="value-label">Before</div>
                                    <span class="value-number before" data-value="${data.before}">
                                        ${data.before}
                                    </span>
                                    <span class="value-unit">${data.unit}</span>
                                </div>
                                <div class="metric-arrow">
                                    <i class="bi bi-arrow-right"></i>
                                </div>
                                <div class="metric-value">
                                    <div class="value-label">After</div>
                                    <span class="value-number after" data-value="${data.after}">
                                        ${data.after}
                                    </span>
                                    <span class="value-unit">${data.unit}</span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateTimelineHTML(caseStudy) {
        return `
            <div class="timeline-container">
                <div class="timeline-header">
                    <h3>Implementation Journey</h3>
                    <p class="timeline-duration">
                        <i class="bi bi-calendar-check"></i> ${caseStudy.timeline} timeline
                    </p>
                </div>
                <div class="timeline">
                    ${caseStudy.timelineEvents.map(event => `
                        <div class="timeline-event" data-month="${event.month}">
                            <div class="timeline-content">
                                <div class="timeline-month">Month ${event.month}</div>
                                <div class="timeline-event-text">${event.event}</div>
                            </div>
                            <div class="timeline-icon">
                                <i class="bi bi-${event.icon}"></i>
                            </div>
                            <div class="timeline-content" style="opacity: 0;"></div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateTestimonialHTML(caseStudy) {
        const { testimonial } = caseStudy;
        
        return `
            <div class="testimonial-section">
                <div class="testimonial-quote">
                    ${testimonial.quote}
                </div>
                <div class="testimonial-author">
                    <div class="author-info">
                        <div class="author-name">${testimonial.author}</div>
                        <div class="author-title">${testimonial.title}</div>
                        <div class="author-title">${caseStudy.company}</div>
                    </div>
                </div>
            </div>
        `;
    }

    generateResultsHTML(caseStudy) {
        return `
            <div class="results-section">
                <h3 style="color: white; margin-bottom: 25px; font-size: 1.6rem;">
                    <i class="bi bi-trophy"></i> Key Results
                </h3>
                <div class="results-grid">
                    ${caseStudy.results.map(result => `
                        <div class="result-item">
                            <i class="bi bi-check-circle result-icon"></i>
                            <span class="result-text">${result}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateNavigationHTML() {
        return `
            <div class="case-study-arrows">
                <button class="nav-arrow nav-prev" ${this.currentSlide === 0 ? 'disabled' : ''}>
                    <i class="bi bi-chevron-left"></i>
                </button>
                <button class="nav-arrow nav-next" ${this.currentSlide === this.caseStudies.length - 1 ? 'disabled' : ''}>
                    <i class="bi bi-chevron-right"></i>
                </button>
            </div>
            <div class="case-study-nav">
                ${this.caseStudies.map((_, index) => `
                    <div class="case-study-dot ${index === this.currentSlide ? 'active' : ''}" 
                         data-slide="${index}"></div>
                `).join('')}
            </div>
        `;
    }

    formatMetricLabel(key) {
        const labels = {
            threatDetection: 'Threat Detection Rate',
            responseTime: 'Average Response Time',
            complianceScore: 'Compliance Score',
            costSavings: 'Annual Cost Savings',
            dataBreaches: 'Security Breaches',
            hipaaCompliance: 'HIPAA Compliance',
            patientDataSecurity: 'Patient Data Security',
            zeroDayDetection: 'Zero-Day Detection',
            globalCoverage: 'Global Coverage',
            incidentResponse: 'Incident Response Time'
        };
        return labels[key] || key;
    }

    setupObservers() {
        // Observe metrics for animation
        const metricObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    this.animateMetricCounters(entry.target);
                }
            });
        }, { threshold: 0.3 });

        document.querySelectorAll('.metric-comparison').forEach(metric => {
            metricObserver.observe(metric);
        });

        // Observe timeline events
        const timelineObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.2 });

        document.querySelectorAll('.timeline-event').forEach(event => {
            timelineObserver.observe(event);
        });
    }

    animateMetricCounters(metricElement) {
        const numbers = metricElement.querySelectorAll('.value-number');
        
        numbers.forEach(numberElement => {
            const targetValue = parseFloat(numberElement.dataset.value);
            const duration = 2000; // 2 seconds
            const steps = 60;
            const increment = targetValue / steps;
            let currentValue = 0;
            let step = 0;

            const interval = setInterval(() => {
                currentValue += increment;
                step++;

                if (step >= steps) {
                    currentValue = targetValue;
                    clearInterval(interval);
                }

                // Format with decimals if needed
                const displayValue = targetValue % 1 !== 0 
                    ? currentValue.toFixed(1) 
                    : Math.round(currentValue);
                    
                numberElement.textContent = displayValue;
            }, duration / steps);
        });
    }

    attachEventListeners() {
        const container = document.getElementById(this.options.containerId);
        if (!container) return;

        // Navigation arrows
        container.addEventListener('click', (e) => {
            if (e.target.closest('.nav-prev')) {
                this.previousSlide();
            } else if (e.target.closest('.nav-next')) {
                this.nextSlide();
            } else if (e.target.closest('.case-study-dot')) {
                const slideIndex = parseInt(e.target.dataset.slide);
                this.goToSlide(slideIndex);
            }
        });

        // Pause auto-play on hover
        container.addEventListener('mouseenter', () => {
            this.pauseAutoPlay();
        });

        container.addEventListener('mouseleave', () => {
            if (this.options.autoPlay) {
                this.startAutoPlay();
            }
        });
    }

    previousSlide() {
        if (this.currentSlide > 0 && !this.isAnimating) {
            this.goToSlide(this.currentSlide - 1);
        }
    }

    nextSlide() {
        if (this.currentSlide < this.caseStudies.length - 1 && !this.isAnimating) {
            this.goToSlide(this.currentSlide + 1);
        }
    }

    goToSlide(index) {
        if (index === this.currentSlide || this.isAnimating) return;

        this.isAnimating = true;
        this.currentSlide = index;
        
        const container = document.getElementById(this.options.containerId);
        const card = container.querySelector('.case-study-card');
        
        // Fade out
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            this.createCaseStudiesUI();
            
            // Fade in
            const newCard = container.querySelector('.case-study-card');
            newCard.style.opacity = '0';
            newCard.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                newCard.style.transition = 'all 0.6s ease';
                newCard.style.opacity = '1';
                newCard.style.transform = 'translateY(0)';
                
                setTimeout(() => {
                    this.isAnimating = false;
                }, this.options.animationDuration);
            }, 50);
        }, this.options.animationDuration);
    }

    startAutoPlay() {
        this.pauseAutoPlay();
        
        this.autoPlayTimer = setInterval(() => {
            if (this.currentSlide < this.caseStudies.length - 1) {
                this.nextSlide();
            } else {
                this.goToSlide(0);
            }
        }, this.options.autoPlayInterval);
    }

    pauseAutoPlay() {
        if (this.autoPlayTimer) {
            clearInterval(this.autoPlayTimer);
            this.autoPlayTimer = null;
        }
    }

    initializeExistingElements() {
        // Look for any manual case study elements and enhance them
        document.querySelectorAll('[data-case-study]').forEach(element => {
            this.enhanceExistingCaseStudy(element);
        });
    }

    enhanceExistingCaseStudy(element) {
        // Add intersection observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.1 });

        observer.observe(element);
    }

    destroy() {
        this.pauseAutoPlay();
        const container = document.getElementById(this.options.containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('case-studies-container')) {
        window.interactiveCaseStudies = new InteractiveCaseStudies({
            containerId: 'case-studies-container',
            autoPlay: true,
            autoPlayInterval: 8000
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InteractiveCaseStudies;
}
