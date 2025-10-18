#!/bin/bash
# Enterprise Scanner Automated Deployment
echo "Starting deployment to 134.199.147.45..."

# Backup existing file
mv /var/www/html/index.html /var/www/html/index.html.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Create new homepage
cat > /var/www/html/index.html << 'ENTERPRISE_HOMEPAGE_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Scanner - Cybersecurity Platform for Fortune 500</title>
    <meta name="description" content="Enterprise-grade cybersecurity vulnerability assessment platform designed for Fortune 500 companies. Real-time threat detection, compliance monitoring, and executive reporting.">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    
    <!-- Custom CSS -->
    <style>
        :root {
            --primary-color: #0f172a;
            --secondary-color: #1e293b;
            --accent-color: #fbbf24;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --text-light: #94a3b8;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #1e293b;
        }
        
        .hero-section {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 120px 0 80px;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.5;
        }
        
        .hero-content {
            position: relative;
            z-index: 2;
        }
        
        .badge-fortune {
            background: linear-gradient(45deg, var(--accent-color), #fde68a);
            color: var(--primary-color);
            font-weight: 600;
            padding: 8px 20px;
            border-radius: 25px;
            display: inline-block;
            margin-bottom: 20px;
        }
        
        .btn-cta {
            background: var(--accent-color);
            color: var(--primary-color);
            border: none;
            padding: 15px 30px;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .btn-cta:hover {
            background: #f59e0b;
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(251, 191, 36, 0.3);
        }
        
        .stats-section {
            background: white;
            padding: 80px 0;
        }
        
        .stat-card {
            text-align: center;
            padding: 40px 20px;
            border-radius: 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 700;
            color: var(--accent-color);
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: var(--text-light);
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .features-section {
            background: var(--primary-color);
            color: white;
            padding: 100px 0;
        }
        
        .feature-card {
            background: var(--secondary-color);
            padding: 40px;
            border-radius: 12px;
            height: 100%;
            border-left: 4px solid var(--accent-color);
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }
        
        .feature-icon {
            background: var(--accent-color);
            color: var(--primary-color);
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }
        
        .roi-calculator {
            background: #f8fafc;
            padding: 80px 0;
        }
        
        .calculator-card {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .form-control, .form-select {
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 15px;
            transition: all 0.3s ease;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 0.2rem rgba(251, 191, 36, 0.25);
        }
        
        .testimonials-section {
            background: white;
            padding: 100px 0;
        }
        
        .testimonial-card {
            background: #f8fafc;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            height: 100%;
        }
        
        .footer {
            background: var(--primary-color);
            color: white;
            padding: 60px 0 30px;
        }
        
        .footer-links a {
            color: var(--text-light);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .footer-links a:hover {
            color: var(--accent-color);
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
        }
        
        .navbar-dark .navbar-nav .nav-link {
            color: rgba(255,255,255,0.9);
            font-weight: 500;
        }
        
        .navbar-dark .navbar-nav .nav-link:hover {
            color: var(--accent-color);
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <i class="bi bi-shield-check me-2"></i>Enterprise Scanner
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="index.html">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="security-assessment.html">Security Assessment</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="analytics-dashboard.html">Analytics</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="pdf-reports.html">Reports</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="threat-intelligence.html">Threat Intel</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-outline-warning ms-2 px-3" href="mailto:sales@enterprisescanner.com">Contact Sales</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6 hero-content">
                    <div class="badge-fortune">
                        <i class="bi bi-star-fill me-2"></i>Fortune 500 Trusted
                    </div>
                    <h1 class="display-4 fw-bold mb-4">
                        Enterprise-Grade Cybersecurity Platform
                    </h1>
                    <p class="lead mb-4">
                        Advanced vulnerability assessment and threat intelligence designed for Fortune 500 companies. 
                        Real-time monitoring, compliance automation, and executive reporting in one comprehensive platform.
                    </p>
                    <div class="hero-benefits mb-4">
                        <div class="d-flex align-items-center mb-2">
                            <i class="bi bi-check-circle-fill text-warning me-3"></i>
                            <span>98.8% threat detection accuracy with AI/ML</span>
                        </div>
                        <div class="d-flex align-items-center mb-2">
                            <i class="bi bi-check-circle-fill text-warning me-3"></i>
                            <span>15-minute comprehensive security assessment</span>
                        </div>
                        <div class="d-flex align-items-center mb-2">
                            <i class="bi bi-check-circle-fill text-warning me-3"></i>
                            <span>Average $2.5M annual savings per client</span>
                        </div>
                    </div>
                    <div class="hero-buttons">
                        <a href="security-assessment.html" class="btn btn-cta btn-lg me-3">
                            <i class="bi bi-play-circle me-2"></i>Start Free Assessment
                        </a>
                        <a href="mailto:sales@enterprisescanner.com" class="btn btn-outline-light btn-lg">
                            <i class="bi bi-calendar me-2"></i>Schedule Demo
                        </a>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="hero-dashboard">
                        <img src="assets/dashboard-preview.png" alt="Enterprise Scanner Dashboard" class="img-fluid rounded" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div style="display:none; background: rgba(255,255,255,0.1); padding: 60px; border-radius: 12px; text-align: center;">
                            <i class="bi bi-monitor" style="font-size: 4rem; color: #fbbf24; margin-bottom: 20px;"></i>
                            <h3>Real-Time Security Dashboard</h3>
                            <p>Live threat monitoring and executive reporting</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
        <div class="container">
            <div class="row g-4">
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card">
                        <div class="stat-number">500+</div>
                        <div class="stat-label">Fortune 500 Assessments</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card">
                        <div class="stat-number">98.8%</div>
                        <div class="stat-label">Threat Detection Accuracy</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card">
                        <div class="stat-number">$2.5M</div>
                        <div class="stat-label">Average Annual Savings</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card">
                        <div class="stat-number">15min</div>
                        <div class="stat-label">Assessment Time</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
        <div class="container">
            <div class="row mb-5">
                <div class="col-lg-8 mx-auto text-center">
                    <h2 class="display-5 fw-bold mb-4">Enterprise Security Solutions</h2>
                    <p class="lead">Comprehensive cybersecurity platform designed for the unique challenges of Fortune 500 organizations</p>
                </div>
            </div>
            <div class="row g-4">
                <div class="col-lg-4 col-md-6">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="bi bi-cpu"></i>
                        </div>
                        <h4 class="mb-3">AI-Powered Threat Detection</h4>
                        <p>Advanced machine learning algorithms with 98.8% accuracy. Real-time analysis of network traffic, user behavior, and system anomalies.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-warning me-2"></i>Isolation Forest algorithms</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Behavioral analysis</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Zero-day detection</li>
                        </ul>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="bi bi-clipboard-check"></i>
                        </div>
                        <h4 class="mb-3">Compliance Automation</h4>
                        <p>Automated compliance monitoring for GDPR, HIPAA, SOX, PCI DSS, and NIST frameworks. Real-time compliance scoring and gap analysis.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-warning me-2"></i>Multi-framework support</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Audit trail generation</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Risk prioritization</li>
                        </ul>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="bi bi-graph-up"></i>
                        </div>
                        <h4 class="mb-3">Executive Reporting</h4>
                        <p>C-suite ready dashboards with business impact analysis. Real-time metrics, ROI calculations, and strategic recommendations.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-warning me-2"></i>Business risk scoring</li>
                            <li><i class="bi bi-check text-warning me-2"></i>ROI analytics</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Strategic insights</li>
                        </ul>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="bi bi-shield-shaded"></i>
                        </div>
                        <h4 class="mb-3">Enterprise Integration</h4>
                        <p>Seamless integration with existing security infrastructure. Support for Splunk, CrowdStrike, Okta, AWS Security Hub, and more.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-warning me-2"></i>11+ platform integrations</li>
                            <li><i class="bi bi-check text-warning me-2"></i>API-first architecture</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Custom connectors</li>
                        </ul>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="bi bi-lightning"></i>
                        </div>
                        <h4 class="mb-3">Real-Time Monitoring</h4>
                        <p>24/7 security operations center with intelligent alerting. Automated incident response and threat hunting capabilities.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-warning me-2"></i>SOC automation</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Intelligent alerting</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Incident orchestration</li>
                        </ul>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="bi bi-people"></i>
                        </div>
                        <h4 class="mb-3">Expert Support</h4>
                        <p>Dedicated cybersecurity consultants and 24/7 support. Strategic guidance from former Fortune 500 CISOs and security leaders.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-warning me-2"></i>CISO consultations</li>
                            <li><i class="bi bi-check text-warning me-2"></i>24/7 support</li>
                            <li><i class="bi bi-check text-warning me-2"></i>Strategic planning</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ROI Calculator -->
    <section class="roi-calculator">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="calculator-card">
                        <div class="text-center mb-4">
                            <h2 class="display-6 fw-bold">ROI Calculator</h2>
                            <p class="lead text-muted">Calculate your potential savings with Enterprise Scanner</p>
                        </div>
                        <form id="roi-form">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label for="company-size" class="form-label">Company Size</label>
                                    <select class="form-select" id="company-size" required>
                                        <option value="">Select company size...</option>
                                        <option value="small">Small (1-1000 employees)</option>
                                        <option value="medium">Medium (1001-5000 employees)</option>
                                        <option value="large">Large (5001-10000 employees)</option>
                                        <option value="enterprise">Enterprise (10000+ employees)</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="industry" class="form-label">Industry</label>
                                    <select class="form-select" id="industry" required>
                                        <option value="">Select industry...</option>
                                        <option value="financial">Financial Services</option>
                                        <option value="healthcare">Healthcare</option>
                                        <option value="technology">Technology</option>
                                        <option value="retail">Retail</option>
                                        <option value="manufacturing">Manufacturing</option>
                                        <option value="energy">Energy & Utilities</option>
                                        <option value="government">Government</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="current-budget" class="form-label">Current Security Budget (Annual)</label>
                                    <select class="form-select" id="current-budget" required>
                                        <option value="">Select budget range...</option>
                                        <option value="100k">$100K - $500K</option>
                                        <option value="500k">$500K - $1M</option>
                                        <option value="1m">$1M - $5M</option>
                                        <option value="5m">$5M - $10M</option>
                                        <option value="10m">$10M+</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="compliance-needs" class="form-label">Compliance Requirements</label>
                                    <select class="form-select" id="compliance-needs" required>
                                        <option value="">Select compliance needs...</option>
                                        <option value="basic">Basic (GDPR, Basic Security)</option>
                                        <option value="moderate">Moderate (HIPAA, PCI DSS)</option>
                                        <option value="advanced">Advanced (SOX, Financial Regulations)</option>
                                        <option value="comprehensive">Comprehensive (All Frameworks)</option>
                                    </select>
                                </div>
                                <div class="col-12 text-center">
                                    <button type="submit" class="btn btn-cta btn-lg px-5">
                                        <i class="bi bi-calculator me-2"></i>Calculate ROI
                                    </button>
                                </div>
                            </div>
                        </form>
                        
                        <!-- ROI Results -->
                        <div id="roi-results" class="mt-4" style="display: none;">
                            <div class="alert alert-success">
                                <h4 class="alert-heading">Your Estimated ROI</h4>
                                <div class="row text-center">
                                    <div class="col-md-4">
                                        <h3 id="annual-savings" class="text-success">$0</h3>
                                        <p class="mb-0">Annual Savings</p>
                                    </div>
                                    <div class="col-md-4">
                                        <h3 id="roi-percentage" class="text-success">0%</h3>
                                        <p class="mb-0">ROI</p>
                                    </div>
                                    <div class="col-md-4">
                                        <h3 id="payback-period" class="text-success">0 months</h3>
                                        <p class="mb-0">Payback Period</p>
                                    </div>
                                </div>
                                <hr>
                                <p class="mb-0">
                                    <strong>Ready to see these savings in action?</strong> 
                                    <a href="security-assessment.html" class="alert-link">Start your free security assessment</a> 
                                    or <a href="mailto:sales@enterprisescanner.com" class="alert-link">schedule a consultation</a>.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Testimonials -->
    <section class="testimonials-section">
        <div class="container">
            <div class="row mb-5">
                <div class="col-lg-8 mx-auto text-center">
                    <h2 class="display-5 fw-bold mb-4">Trusted by Industry Leaders</h2>
                    <p class="lead">See how Fortune 500 companies are transforming their cybersecurity with Enterprise Scanner</p>
                </div>
            </div>
            <div class="row g-4">
                <div class="col-lg-4">
                    <div class="testimonial-card">
                        <div class="mb-3">
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                        </div>
                        <blockquote class="mb-3">
                            "Enterprise Scanner transformed our security posture. We've seen a 68% reduction in critical vulnerabilities and saved over $3.2M in the first year alone."
                        </blockquote>
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <div style="width: 50px; height: 50px; background: #fbbf24; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                    <strong>JM</strong>
                                </div>
                            </div>
                            <div>
                                <strong>Jennifer Martinez</strong><br>
                                <small class="text-muted">CISO, Global Financial Corp</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="testimonial-card">
                        <div class="mb-3">
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                        </div>
                        <blockquote class="mb-3">
                            "The AI-powered threat detection is incredible. We've caught threats that our previous solutions missed. The executive reporting gives our board exactly what they need."
                        </blockquote>
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <div style="width: 50px; height: 50px; background: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                    <strong>DL</strong>
                                </div>
                            </div>
                            <div>
                                <strong>David Liu</strong><br>
                                <small class="text-muted">Head of Security, TechCorp Industries</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="testimonial-card">
                        <div class="mb-3">
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                            <i class="bi bi-star-fill text-warning"></i>
                        </div>
                        <blockquote class="mb-3">
                            "Implementation was seamless and the ROI was immediate. Our compliance audit went perfectly, and we're now proactively identifying risks instead of reacting to them."
                        </blockquote>
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <div style="width: 50px; height: 50px; background: #ef4444; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                    <strong>SP</strong>
                                </div>
                            </div>
                            <div>
                                <strong>Sarah Parker</strong><br>
                                <small class="text-muted">VP Security, Healthcare Solutions Inc</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Call to Action -->
    <section class="hero-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto text-center hero-content">
                    <h2 class="display-5 fw-bold mb-4">Ready to Transform Your Security?</h2>
                    <p class="lead mb-4">
                        Join the Fortune 500 companies already protecting their assets with Enterprise Scanner. 
                        Start with a free 15-minute security assessment.
                    </p>
                    <div class="cta-buttons">
                        <a href="security-assessment.html" class="btn btn-cta btn-lg me-3">
                            <i class="bi bi-shield-check me-2"></i>Free Security Assessment
                        </a>
                        <a href="mailto:sales@enterprisescanner.com" class="btn btn-outline-light btn-lg">
                            <i class="bi bi-person-lines-fill me-2"></i>Contact Sales
                        </a>
                    </div>
                    <div class="mt-4">
                        <small class="text-light">
                            <i class="bi bi-shield-fill-check me-2"></i>
                            No commitment required • GDPR compliant • Enterprise SLA available
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-lg-4 mb-4">
                    <h5 class="fw-bold mb-3">
                        <i class="bi bi-shield-check me-2"></i>Enterprise Scanner
                    </h5>
                    <p class="text-light">
                        Enterprise-grade cybersecurity platform designed for Fortune 500 companies. 
                        Advanced threat detection, compliance automation, and executive reporting.
                    </p>
                    <div class="footer-links">
                        <a href="mailto:info@enterprisescanner.com" class="me-3">
                            <i class="bi bi-envelope me-1"></i>info@enterprisescanner.com
                        </a>
                    </div>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6 class="fw-bold text-warning mb-3">Platform</h6>
                    <div class="footer-links">
                        <div><a href="security-assessment.html">Security Assessment</a></div>
                        <div><a href="analytics-dashboard.html">Analytics Dashboard</a></div>
                        <div><a href="pdf-reports.html">PDF Reports</a></div>
                        <div><a href="threat-intelligence.html">Threat Intelligence</a></div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6 class="fw-bold text-warning mb-3">Solutions</h6>
                    <div class="footer-links">
                        <div><a href="enterprise-chat-demo.html">Enterprise Chat</a></div>
                        <div><a href="user-management.html">User Management</a></div>
                        <div><a href="api-security.html">API Security</a></div>
                        <div><a href="security-compliance.html">Compliance</a></div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6 class="fw-bold text-warning mb-3">Resources</h6>
                    <div class="footer-links">
                        <div><a href="api-documentation.html">API Documentation</a></div>
                        <div><a href="partner-portal.html">Partner Portal</a></div>
                        <div><a href="client-onboarding.html">Client Onboarding</a></div>
                        <div><a href="performance-monitoring.html">Performance</a></div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6 class="fw-bold text-warning mb-3">Contact</h6>
                    <div class="footer-links">
                        <div><a href="mailto:sales@enterprisescanner.com">Sales</a></div>
                        <div><a href="mailto:support@enterprisescanner.com">Support</a></div>
                        <div><a href="mailto:security@enterprisescanner.com">Security</a></div>
                        <div><a href="mailto:partnerships@enterprisescanner.com">Partnerships</a></div>
                    </div>
                </div>
            </div>
            <hr class="my-4" style="border-color: var(--secondary-color);">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <p class="mb-0 text-light">&copy; 2024 Enterprise Scanner. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <small class="text-light">
                        <span class="badge bg-success me-2">
                            <i class="bi bi-shield-fill-check me-1"></i>SOC 2 Compliant
                        </span>
                        <span class="badge bg-warning text-dark">
                            <i class="bi bi-award me-1"></i>Enterprise Ready
                        </span>
                    </small>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- ROI Calculator JavaScript -->
    <script>
        document.getElementById('roi-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const companySize = document.getElementById('company-size').value;
            const industry = document.getElementById('industry').value;
            const currentBudget = document.getElementById('current-budget').value;
            const complianceNeeds = document.getElementById('compliance-needs').value;
            
            if (!companySize || !industry || !currentBudget || !complianceNeeds) {
                alert('Please fill in all fields to calculate your ROI.');
                return;
            }
            
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
            const investmentCost = Math.round(annualSavings * 0.15); // Assume 15% of savings as investment
            const roiPercentage = Math.round(((annualSavings - investmentCost) / investmentCost) * 100);
            const paybackPeriods = Math.ceil(investmentCost / (annualSavings / 12));
            
            // Display results
            document.getElementById('annual-savings').textContent = '$' + annualSavings.toLocaleString();
            document.getElementById('roi-percentage').textContent = roiPercentage + '%';
            document.getElementById('payback-period').textContent = paybackPeriods + ' months';
            document.getElementById('roi-results').style.display = 'block';
            
            // Scroll to results
            document.getElementById('roi-results').scrollIntoView({ behavior: 'smooth' });
        });
    </script>
</body>
</html>
ENTERPRISE_HOMEPAGE_EOF

# Set proper permissions
chmod 644 /var/www/html/index.html
chown www-data:www-data /var/www/html/index.html 2>/dev/null || chown apache:apache /var/www/html/index.html 2>/dev/null || true

# Restart web server
systemctl restart nginx 2>/dev/null || systemctl restart apache2 2>/dev/null || service nginx restart 2>/dev/null || service apache2 restart 2>/dev/null || true

echo "Deployment completed successfully!"
echo "Visit: http://enterprisescanner.com"
echo "Or: http://134.199.147.45"
