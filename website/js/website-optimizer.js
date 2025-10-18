/**
 * Performance Optimizer & Integration Tester - Phase 2 Final Polish
 * Enterprise Scanner Website
 * Features: Performance monitoring, integration testing, accessibility checks, bug detection
 */

class WebsiteOptimizer {
    constructor(options = {}) {
        this.options = {
            enablePerformanceMonitoring: options.enablePerformanceMonitoring !== false,
            enableAccessibilityChecks: options.enableAccessibilityChecks !== false,
            enableIntegrationTests: options.enableIntegrationTests !== false,
            enableErrorTracking: options.enableErrorTracking !== false,
            reportingEndpoint: options.reportingEndpoint || null,
            ...options
        };

        this.performanceMetrics = {
            pageLoad: {},
            componentLoad: {},
            animations: {},
            interactions: {}
        };

        this.errors = [];
        this.warnings = [];
        this.accessibilityIssues = [];

        this.init();
    }

    init() {
        console.log('%c🚀 Website Optimizer Initialized', 'color: #3b82f6; font-size: 14px; font-weight: bold;');
        
        if (this.options.enablePerformanceMonitoring) {
            this.setupPerformanceMonitoring();
        }

        if (this.options.enableAccessibilityChecks) {
            this.runAccessibilityChecks();
        }

        if (this.options.enableIntegrationTests) {
            this.runIntegrationTests();
        }

        if (this.options.enableErrorTracking) {
            this.setupErrorTracking();
        }

        // Run checks after page fully loads
        window.addEventListener('load', () => {
            this.collectPerformanceMetrics();
            this.optimizeImages();
            this.optimizeScripts();
            this.checkBrowserCompatibility();
        });
    }

    // ==================== PERFORMANCE MONITORING ====================

    setupPerformanceMonitoring() {
        if (!('performance' in window)) {
            console.warn('Performance API not supported');
            return;
        }

        // Monitor Long Tasks
        if ('PerformanceObserver' in window) {
            try {
                const longTaskObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {
                            this.warnings.push({
                                type: 'performance',
                                message: `Long task detected: ${entry.duration.toFixed(2)}ms`,
                                entry: entry
                            });
                        }
                    }
                });
                longTaskObserver.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                // Long tasks not supported in all browsers
            }

            // Monitor Layout Shifts (CLS)
            const clsObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        this.performanceMetrics.layoutShift = (this.performanceMetrics.layoutShift || 0) + entry.value;
                    }
                }
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });

            // Monitor Largest Contentful Paint (LCP)
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.performanceMetrics.largestContentfulPaint = lastEntry.renderTime || lastEntry.loadTime;
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

            // Monitor First Input Delay (FID)
            const fidObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    this.performanceMetrics.firstInputDelay = entry.processingStart - entry.startTime;
                }
            });
            fidObserver.observe({ entryTypes: ['first-input'] });
        }

        // Monitor frame rate
        this.monitorFrameRate();
    }

    monitorFrameRate() {
        let lastTime = performance.now();
        let frames = 0;
        let fps = 60;

        const measureFPS = () => {
            const currentTime = performance.now();
            frames++;

            if (currentTime >= lastTime + 1000) {
                fps = Math.round((frames * 1000) / (currentTime - lastTime));
                this.performanceMetrics.currentFPS = fps;

                if (fps < 30) {
                    this.warnings.push({
                        type: 'performance',
                        message: `Low FPS detected: ${fps} FPS`,
                        timestamp: new Date().toISOString()
                    });
                }

                frames = 0;
                lastTime = currentTime;
            }

            requestAnimationFrame(measureFPS);
        };

        requestAnimationFrame(measureFPS);
    }

    collectPerformanceMetrics() {
        const perfData = performance.getEntriesByType('navigation')[0];
        
        if (perfData) {
            this.performanceMetrics.pageLoad = {
                dns: perfData.domainLookupEnd - perfData.domainLookupStart,
                tcp: perfData.connectEnd - perfData.connectStart,
                request: perfData.responseStart - perfData.requestStart,
                response: perfData.responseEnd - perfData.responseStart,
                domProcessing: perfData.domComplete - perfData.domInteractive,
                domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                totalTime: perfData.loadEventEnd - perfData.fetchStart
            };
        }

        // Collect resource timing
        const resources = performance.getEntriesByType('resource');
        this.performanceMetrics.resources = {
            scripts: resources.filter(r => r.name.endsWith('.js')),
            styles: resources.filter(r => r.name.endsWith('.css')),
            images: resources.filter(r => /\.(jpg|jpeg|png|gif|svg|webp)/.test(r.name)),
            fonts: resources.filter(r => /\.(woff|woff2|ttf|otf)/.test(r.name))
        };

        this.analyzeResourcePerformance();
        this.generatePerformanceReport();
    }

    analyzeResourcePerformance() {
        const { resources } = this.performanceMetrics;

        // Check for large resources
        [...resources.scripts, ...resources.styles, ...resources.images].forEach(resource => {
            if (resource.transferSize > 500000) { // 500KB
                this.warnings.push({
                    type: 'performance',
                    message: `Large resource detected: ${resource.name} (${(resource.transferSize / 1024).toFixed(2)} KB)`,
                    resource: resource.name
                });
            }

            if (resource.duration > 1000) { // 1 second
                this.warnings.push({
                    type: 'performance',
                    message: `Slow resource load: ${resource.name} (${resource.duration.toFixed(2)}ms)`,
                    resource: resource.name
                });
            }
        });
    }

    // ==================== ACCESSIBILITY CHECKS ====================

    runAccessibilityChecks() {
        console.log('%c♿ Running Accessibility Audit...', 'color: #10b981; font-size: 12px;');

        const checks = [
            this.checkImageAltText.bind(this),
            this.checkFormLabels.bind(this),
            this.checkHeadingStructure.bind(this),
            this.checkColorContrast.bind(this),
            this.checkAriaLabels.bind(this),
            this.checkKeyboardNavigation.bind(this),
            this.checkFocusIndicators.bind(this),
            this.checkLinkText.bind(this)
        ];

        checks.forEach(check => check());

        if (this.accessibilityIssues.length === 0) {
            console.log('%c✅ No accessibility issues found!', 'color: #10b981; font-weight: bold;');
        } else {
            console.warn(`⚠️ Found ${this.accessibilityIssues.length} accessibility issues`);
            this.accessibilityIssues.forEach(issue => {
                console.warn(`  - ${issue.message}`, issue.element);
            });
        }
    }

    checkImageAltText() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (!img.alt && !img.getAttribute('role') === 'presentation') {
                this.accessibilityIssues.push({
                    type: 'missing-alt',
                    severity: 'high',
                    message: 'Image missing alt text',
                    element: img,
                    wcag: 'WCAG 2.1 A - 1.1.1'
                });
            }
        });
    }

    checkFormLabels() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const id = input.id;
            const label = id ? document.querySelector(`label[for="${id}"]`) : null;
            const ariaLabel = input.getAttribute('aria-label');
            
            if (!label && !ariaLabel && input.type !== 'hidden' && input.type !== 'submit') {
                this.accessibilityIssues.push({
                    type: 'missing-label',
                    severity: 'high',
                    message: 'Form input missing label',
                    element: input,
                    wcag: 'WCAG 2.1 A - 3.3.2'
                });
            }
        });
    }

    checkHeadingStructure() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let previousLevel = 0;

        headings.forEach(heading => {
            const level = parseInt(heading.tagName[1]);
            
            if (level - previousLevel > 1) {
                this.accessibilityIssues.push({
                    type: 'heading-skip',
                    severity: 'medium',
                    message: `Heading level skipped from H${previousLevel} to H${level}`,
                    element: heading,
                    wcag: 'WCAG 2.1 A - 1.3.1'
                });
            }
            
            previousLevel = level;
        });
    }

    checkColorContrast() {
        // Simplified contrast check - would need more sophisticated color analysis in production
        const textElements = document.querySelectorAll('p, span, a, button, h1, h2, h3, h4, h5, h6');
        
        textElements.forEach(element => {
            const styles = window.getComputedStyle(element);
            const fontSize = parseFloat(styles.fontSize);
            const fontWeight = styles.fontWeight;
            
            // Check if text is large (18pt+ or 14pt+ bold)
            const isLargeText = fontSize >= 24 || (fontSize >= 18.66 && parseInt(fontWeight) >= 700);
            
            // This is a simplified check - real contrast checking requires color analysis
            if (styles.opacity && parseFloat(styles.opacity) < 0.5) {
                this.accessibilityIssues.push({
                    type: 'low-contrast',
                    severity: 'medium',
                    message: 'Element may have low contrast (opacity < 0.5)',
                    element: element,
                    wcag: 'WCAG 2.1 AA - 1.4.3'
                });
            }
        });
    }

    checkAriaLabels() {
        const interactiveElements = document.querySelectorAll('button, a, [role="button"], [role="link"]');
        
        interactiveElements.forEach(element => {
            const hasText = element.textContent.trim().length > 0;
            const hasAriaLabel = element.getAttribute('aria-label');
            const hasAriaLabelledBy = element.getAttribute('aria-labelledby');
            const hasTitle = element.getAttribute('title');
            
            if (!hasText && !hasAriaLabel && !hasAriaLabelledBy && !hasTitle) {
                this.accessibilityIssues.push({
                    type: 'missing-accessible-name',
                    severity: 'high',
                    message: 'Interactive element missing accessible name',
                    element: element,
                    wcag: 'WCAG 2.1 A - 4.1.2'
                });
            }
        });
    }

    checkKeyboardNavigation() {
        const focusableElements = document.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        focusableElements.forEach(element => {
            if (element.tabIndex < 0 && !element.hasAttribute('disabled')) {
                this.warnings.push({
                    type: 'keyboard-nav',
                    message: 'Element removed from tab order',
                    element: element
                });
            }
        });
    }

    checkFocusIndicators() {
        const styles = Array.from(document.styleSheets)
            .flatMap(sheet => {
                try {
                    return Array.from(sheet.cssRules || []);
                } catch {
                    return [];
                }
            })
            .filter(rule => rule.selectorText && rule.selectorText.includes(':focus'));
        
        if (styles.length === 0) {
            this.accessibilityIssues.push({
                type: 'missing-focus-styles',
                severity: 'high',
                message: 'No :focus styles detected in CSS',
                wcag: 'WCAG 2.1 AA - 2.4.7'
            });
        }
    }

    checkLinkText() {
        const links = document.querySelectorAll('a');
        const genericText = ['click here', 'read more', 'here', 'more', 'link'];
        
        links.forEach(link => {
            const text = link.textContent.trim().toLowerCase();
            if (genericText.includes(text)) {
                this.accessibilityIssues.push({
                    type: 'generic-link-text',
                    severity: 'low',
                    message: `Generic link text: "${text}"`,
                    element: link,
                    wcag: 'WCAG 2.1 A - 2.4.4'
                });
            }
        });
    }

    // ==================== INTEGRATION TESTS ====================

    runIntegrationTests() {
        console.log('%c🔧 Running Integration Tests...', 'color: #8b5cf6; font-size: 12px;');

        const tests = [
            { name: 'Toast Notifications', fn: this.testToastNotifications.bind(this) },
            { name: 'Loading Indicators', fn: this.testLoadingIndicators.bind(this) },
            { name: 'Enhanced Navbar', fn: this.testEnhancedNavbar.bind(this) },
            { name: 'Counter Animations', fn: this.testCounterAnimations.bind(this) },
            { name: '3D Card Effects', fn: this.testCardEffects.bind(this) },
            { name: 'Scroll Animations', fn: this.testScrollAnimations.bind(this) },
            { name: 'Form Validation', fn: this.testFormValidation.bind(this) },
            { name: 'Video Player', fn: this.testVideoPlayer.bind(this) },
            { name: 'Case Studies', fn: this.testCaseStudies.bind(this) }
        ];

        const results = {
            passed: 0,
            failed: 0,
            skipped: 0
        };

        tests.forEach(test => {
            try {
                const result = test.fn();
                if (result === true) {
                    results.passed++;
                    console.log(`  ✅ ${test.name}: PASSED`);
                } else if (result === false) {
                    results.failed++;
                    console.error(`  ❌ ${test.name}: FAILED`);
                } else {
                    results.skipped++;
                    console.log(`  ⏭️  ${test.name}: SKIPPED`);
                }
            } catch (error) {
                results.failed++;
                console.error(`  ❌ ${test.name}: ERROR`, error.message);
                this.errors.push({
                    type: 'integration-test',
                    test: test.name,
                    error: error.message
                });
            }
        });

        console.log(`\n📊 Test Results: ${results.passed} passed, ${results.failed} failed, ${results.skipped} skipped`);
        return results;
    }

    testToastNotifications() {
        if (typeof showToast === 'undefined') return null;
        
        // Check if toast functions exist
        const hasSuccess = typeof showToast.success === 'function';
        const hasError = typeof showToast.error === 'function';
        const hasWarning = typeof showToast.warning === 'function';
        const hasInfo = typeof showToast.info === 'function';
        
        return hasSuccess && hasError && hasWarning && hasInfo;
    }

    testLoadingIndicators() {
        if (typeof showLoading === 'undefined' || typeof hideLoading === 'undefined') return null;
        return typeof showLoading === 'function' && typeof hideLoading === 'function';
    }

    testEnhancedNavbar() {
        const navbar = document.querySelector('.navbar');
        return navbar !== null;
    }

    testCounterAnimations() {
        const counters = document.querySelectorAll('[data-counter]');
        return counters.length > 0;
    }

    testCardEffects() {
        const cards = document.querySelectorAll('[data-card-3d]');
        return cards.length > 0;
    }

    testScrollAnimations() {
        return typeof window.scrollAnimations !== 'undefined';
    }

    testFormValidation() {
        const forms = document.querySelectorAll('[data-validate]');
        return forms.length > 0;
    }

    testVideoPlayer() {
        return typeof VideoPlayer !== 'undefined';
    }

    testCaseStudies() {
        return typeof window.interactiveCaseStudies !== 'undefined';
    }

    // ==================== ERROR TRACKING ====================

    setupErrorTracking() {
        window.addEventListener('error', (event) => {
            this.errors.push({
                type: 'javascript-error',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                timestamp: new Date().toISOString()
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.errors.push({
                type: 'unhandled-promise-rejection',
                message: event.reason,
                timestamp: new Date().toISOString()
            });
        });
    }

    // ==================== OPTIMIZATION UTILITIES ====================

    optimizeImages() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            // Check for missing width/height
            if (!img.width || !img.height) {
                this.warnings.push({
                    type: 'optimization',
                    message: 'Image missing explicit dimensions (causes layout shift)',
                    element: img
                });
            }

            // Check for lazy loading
            if (!img.loading && !img.classList.contains('no-lazy')) {
                img.loading = 'lazy';
            }

            // Check image format
            if (img.src.match(/\.(jpg|jpeg|png)$/i)) {
                this.warnings.push({
                    type: 'optimization',
                    message: 'Consider using WebP format for better compression',
                    element: img
                });
            }
        });
    }

    optimizeScripts() {
        const scripts = document.querySelectorAll('script[src]');
        
        scripts.forEach(script => {
            if (!script.defer && !script.async && !script.type === 'module') {
                this.warnings.push({
                    type: 'optimization',
                    message: 'Script blocking page render (consider defer/async)',
                    element: script
                });
            }
        });
    }

    checkBrowserCompatibility() {
        const features = [
            { name: 'IntersectionObserver', check: 'IntersectionObserver' in window },
            { name: 'Fetch API', check: 'fetch' in window },
            { name: 'Promise', check: 'Promise' in window },
            { name: 'localStorage', check: 'localStorage' in window },
            { name: 'CSS Grid', check: CSS.supports('display', 'grid') },
            { name: 'CSS Custom Properties', check: CSS.supports('--test', '0') }
        ];

        features.forEach(feature => {
            if (!feature.check) {
                this.warnings.push({
                    type: 'compatibility',
                    message: `${feature.name} not supported in this browser`
                });
            }
        });
    }

    // ==================== REPORTING ====================

    generatePerformanceReport() {
        const metrics = this.performanceMetrics;
        
        console.group('%c📊 Performance Report', 'color: #3b82f6; font-size: 14px; font-weight: bold;');
        
        if (metrics.pageLoad) {
            console.log('%cPage Load Metrics:', 'font-weight: bold;');
            console.table({
                'DNS Lookup': `${metrics.pageLoad.dns.toFixed(2)}ms`,
                'TCP Connection': `${metrics.pageLoad.tcp.toFixed(2)}ms`,
                'Request Time': `${metrics.pageLoad.request.toFixed(2)}ms`,
                'Response Time': `${metrics.pageLoad.response.toFixed(2)}ms`,
                'DOM Processing': `${metrics.pageLoad.domProcessing.toFixed(2)}ms`,
                'Total Load Time': `${metrics.pageLoad.totalTime.toFixed(2)}ms`
            });
        }

        if (metrics.largestContentfulPaint) {
            const lcp = metrics.largestContentfulPaint;
            const lcpStatus = lcp < 2500 ? '✅ Good' : lcp < 4000 ? '⚠️ Needs Improvement' : '❌ Poor';
            console.log(`%cLCP (Largest Contentful Paint): ${lcp.toFixed(2)}ms ${lcpStatus}`, 
                lcp < 2500 ? 'color: #10b981' : lcp < 4000 ? 'color: #f59e0b' : 'color: #ef4444');
        }

        if (metrics.firstInputDelay) {
            const fid = metrics.firstInputDelay;
            const fidStatus = fid < 100 ? '✅ Good' : fid < 300 ? '⚠️ Needs Improvement' : '❌ Poor';
            console.log(`%cFID (First Input Delay): ${fid.toFixed(2)}ms ${fidStatus}`,
                fid < 100 ? 'color: #10b981' : fid < 300 ? 'color: #f59e0b' : 'color: #ef4444');
        }

        if (metrics.layoutShift !== undefined) {
            const cls = metrics.layoutShift;
            const clsStatus = cls < 0.1 ? '✅ Good' : cls < 0.25 ? '⚠️ Needs Improvement' : '❌ Poor';
            console.log(`%cCLS (Cumulative Layout Shift): ${cls.toFixed(3)} ${clsStatus}`,
                cls < 0.1 ? 'color: #10b981' : cls < 0.25 ? 'color: #f59e0b' : 'color: #ef4444');
        }

        if (metrics.currentFPS) {
            console.log(`%cCurrent FPS: ${metrics.currentFPS}`,
                metrics.currentFPS >= 55 ? 'color: #10b981' : 'color: #f59e0b');
        }

        console.groupEnd();
    }

    generateAccessibilityReport() {
        console.group('%c♿ Accessibility Report', 'color: #10b981; font-size: 14px; font-weight: bold;');
        
        if (this.accessibilityIssues.length === 0) {
            console.log('%c✅ No accessibility issues found!', 'color: #10b981; font-weight: bold;');
        } else {
            const bySeverity = {
                high: this.accessibilityIssues.filter(i => i.severity === 'high'),
                medium: this.accessibilityIssues.filter(i => i.severity === 'medium'),
                low: this.accessibilityIssues.filter(i => i.severity === 'low')
            };

            console.log(`Total Issues: ${this.accessibilityIssues.length}`);
            console.log(`  ❌ High: ${bySeverity.high.length}`);
            console.log(`  ⚠️  Medium: ${bySeverity.medium.length}`);
            console.log(`  ℹ️  Low: ${bySeverity.low.length}`);

            this.accessibilityIssues.forEach(issue => {
                const icon = issue.severity === 'high' ? '❌' : issue.severity === 'medium' ? '⚠️' : 'ℹ️';
                console.log(`${icon} ${issue.message} (${issue.wcag})`);
            });
        }

        console.groupEnd();
    }

    generateFullReport() {
        this.generatePerformanceReport();
        this.generateAccessibilityReport();

        if (this.warnings.length > 0) {
            console.group('%c⚠️ Warnings', 'color: #f59e0b; font-size: 14px; font-weight: bold;');
            this.warnings.forEach(warning => {
                console.warn(warning.message, warning);
            });
            console.groupEnd();
        }

        if (this.errors.length > 0) {
            console.group('%c❌ Errors', 'color: #ef4444; font-size: 14px; font-weight: bold;');
            this.errors.forEach(error => {
                console.error(error.message || error.type, error);
            });
            console.groupEnd();
        }

        return {
            performance: this.performanceMetrics,
            accessibility: this.accessibilityIssues,
            warnings: this.warnings,
            errors: this.errors
        };
    }

    // ==================== PUBLIC API ====================

    getPerformanceScore() {
        const metrics = this.performanceMetrics;
        let score = 100;

        // LCP scoring
        if (metrics.largestContentfulPaint) {
            const lcp = metrics.largestContentfulPaint;
            if (lcp > 4000) score -= 20;
            else if (lcp > 2500) score -= 10;
        }

        // FID scoring
        if (metrics.firstInputDelay) {
            const fid = metrics.firstInputDelay;
            if (fid > 300) score -= 20;
            else if (fid > 100) score -= 10;
        }

        // CLS scoring
        if (metrics.layoutShift !== undefined) {
            const cls = metrics.layoutShift;
            if (cls > 0.25) score -= 20;
            else if (cls > 0.1) score -= 10;
        }

        // FPS scoring
        if (metrics.currentFPS && metrics.currentFPS < 30) {
            score -= 15;
        }

        return Math.max(0, score);
    }

    getAccessibilityScore() {
        const issues = this.accessibilityIssues;
        let score = 100;

        issues.forEach(issue => {
            if (issue.severity === 'high') score -= 10;
            else if (issue.severity === 'medium') score -= 5;
            else if (issue.severity === 'low') score -= 2;
        });

        return Math.max(0, score);
    }

    exportReport(format = 'json') {
        const report = this.generateFullReport();

        if (format === 'json') {
            return JSON.stringify(report, null, 2);
        } else if (format === 'html') {
            return this.generateHTMLReport(report);
        }

        return report;
    }

    generateHTMLReport(report) {
        // Generate a simple HTML report
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Website Optimization Report</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .score { font-size: 48px; font-weight: bold; }
                    .good { color: #10b981; }
                    .warning { color: #f59e0b; }
                    .error { color: #ef4444; }
                </style>
            </head>
            <body>
                <h1>Enterprise Scanner Website - Optimization Report</h1>
                <p>Generated: ${new Date().toISOString()}</p>
                
                <h2>Performance Score: <span class="score">${this.getPerformanceScore()}/100</span></h2>
                <h2>Accessibility Score: <span class="score">${this.getAccessibilityScore()}/100</span></h2>
                
                <h3>Issues Summary:</h3>
                <ul>
                    <li>Accessibility Issues: ${report.accessibility.length}</li>
                    <li>Warnings: ${report.warnings.length}</li>
                    <li>Errors: ${report.errors.length}</li>
                </ul>
            </body>
            </html>
        `;
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.websiteOptimizer = new WebsiteOptimizer({
        enablePerformanceMonitoring: true,
        enableAccessibilityChecks: true,
        enableIntegrationTests: true,
        enableErrorTracking: true
    });

    // Generate report after page fully loads
    window.addEventListener('load', () => {
        setTimeout(() => {
            const report = window.websiteOptimizer.generateFullReport();
            console.log('%c🎉 Website Optimization Complete!', 'color: #10b981; font-size: 16px; font-weight: bold;');
            console.log(`Performance Score: ${window.websiteOptimizer.getPerformanceScore()}/100`);
            console.log(`Accessibility Score: ${window.websiteOptimizer.getAccessibilityScore()}/100`);
        }, 2000);
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebsiteOptimizer;
}
