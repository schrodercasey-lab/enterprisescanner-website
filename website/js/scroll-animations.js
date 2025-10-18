/**
 * Advanced Scroll Animations - Phase 2
 * Enterprise Scanner Website
 * Features: Parallax, scroll reveals, progress indicators, smooth scrolling
 */

class ScrollAnimations {
    constructor(options = {}) {
        this.options = {
            enableParallax: options.enableParallax !== false,
            enableReveal: options.enableReveal !== false,
            enableProgress: options.enableProgress !== false,
            enableSmoothScroll: options.enableSmoothScroll !== false,
            revealThreshold: options.revealThreshold || 0.15,
            parallaxSpeed: options.parallaxSpeed || 0.5,
            ...options
        };

        this.scrollPosition = 0;
        this.windowHeight = window.innerHeight;
        this.documentHeight = document.documentElement.scrollHeight;
        this.ticking = false;
        this.observers = [];

        this.init();
    }

    init() {
        this.injectStyles();
        
        if (this.options.enableReveal) {
            this.setupScrollReveal();
        }
        
        if (this.options.enableParallax) {
            this.setupParallax();
        }
        
        if (this.options.enableProgress) {
            this.setupScrollProgress();
        }
        
        if (this.options.enableSmoothScroll) {
            this.setupSmoothScroll();
        }
        
        this.setupScrollListener();
        this.setupResizeListener();
    }

    injectStyles() {
        if (document.getElementById('scroll-animations-styles')) return;

        const style = document.createElement('style');
        style.id = 'scroll-animations-styles';
        style.textContent = `
            /* Scroll Reveal Animations */
            [data-scroll-reveal] {
                opacity: 0;
                transition: opacity 0.6s ease-out,
                            transform 0.6s ease-out;
            }

            [data-scroll-reveal].revealed {
                opacity: 1;
            }

            /* Reveal from bottom */
            [data-scroll-reveal="fade-up"] {
                transform: translateY(60px);
            }

            [data-scroll-reveal="fade-up"].revealed {
                transform: translateY(0);
            }

            /* Reveal from top */
            [data-scroll-reveal="fade-down"] {
                transform: translateY(-60px);
            }

            [data-scroll-reveal="fade-down"].revealed {
                transform: translateY(0);
            }

            /* Reveal from left */
            [data-scroll-reveal="fade-left"] {
                transform: translateX(-60px);
            }

            [data-scroll-reveal="fade-left"].revealed {
                transform: translateX(0);
            }

            /* Reveal from right */
            [data-scroll-reveal="fade-right"] {
                transform: translateX(60px);
            }

            [data-scroll-reveal="fade-right"].revealed {
                transform: translateX(0);
            }

            /* Scale reveal */
            [data-scroll-reveal="zoom-in"] {
                transform: scale(0.8);
            }

            [data-scroll-reveal="zoom-in"].revealed {
                transform: scale(1);
            }

            /* Rotate reveal */
            [data-scroll-reveal="rotate-in"] {
                transform: rotate(-10deg) scale(0.9);
            }

            [data-scroll-reveal="rotate-in"].revealed {
                transform: rotate(0) scale(1);
            }

            /* Stagger delays for multiple elements */
            [data-scroll-reveal][data-delay="1"] {
                transition-delay: 0.1s;
            }

            [data-scroll-reveal][data-delay="2"] {
                transition-delay: 0.2s;
            }

            [data-scroll-reveal][data-delay="3"] {
                transition-delay: 0.3s;
            }

            [data-scroll-reveal][data-delay="4"] {
                transition-delay: 0.4s;
            }

            [data-scroll-reveal][data-delay="5"] {
                transition-delay: 0.5s;
            }

            /* Parallax elements */
            [data-parallax] {
                will-change: transform;
                transition: transform 0.1s ease-out;
            }

            /* Scroll progress indicator */
            .scroll-progress-container {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                z-index: 10000;
                pointer-events: none;
            }

            .scroll-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
                width: 0%;
                transition: width 0.1s ease-out;
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
            }

            /* Section progress indicator */
            .section-progress {
                position: fixed;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 12px;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .section-progress.visible {
                opacity: 1;
            }

            .section-progress-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
            }

            .section-progress-dot::after {
                content: attr(data-label);
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(15, 23, 42, 0.9);
                backdrop-filter: blur(10px);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s ease;
            }

            .section-progress-dot:hover::after {
                opacity: 1;
            }

            .section-progress-dot.active {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
                transform: scale(1.5);
            }

            .section-progress-dot:hover {
                background: rgba(255, 255, 255, 0.6);
                transform: scale(1.3);
            }

            /* Back to top button */
            .back-to-top {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                opacity: 0;
                transform: scale(0.8);
                transition: all 0.3s ease;
                z-index: 1000;
                box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
            }

            .back-to-top.visible {
                opacity: 1;
                transform: scale(1);
            }

            .back-to-top:hover {
                transform: scale(1.1) translateY(-3px);
                box-shadow: 0 6px 30px rgba(59, 130, 246, 0.6);
            }

            .back-to-top i {
                color: white;
                font-size: 1.5rem;
            }

            /* Smooth scroll behavior */
            html.smooth-scroll {
                scroll-behavior: smooth;
            }

            /* Scroll snap (optional) */
            .scroll-snap-container {
                scroll-snap-type: y mandatory;
                scroll-padding-top: 80px;
            }

            .scroll-snap-section {
                scroll-snap-align: start;
            }

            /* Floating elements animation */
            @keyframes float {
                0%, 100% {
                    transform: translateY(0px);
                }
                50% {
                    transform: translateY(-20px);
                }
            }

            [data-animate="float"] {
                animation: float 6s ease-in-out infinite;
            }

            [data-animate="float"][data-delay="1"] {
                animation-delay: 0.5s;
            }

            [data-animate="float"][data-delay="2"] {
                animation-delay: 1s;
            }

            /* Pulse animation */
            @keyframes pulse-glow {
                0%, 100% {
                    box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
                }
                50% {
                    box-shadow: 0 0 40px rgba(59, 130, 246, 0.8);
                }
            }

            [data-animate="pulse"] {
                animation: pulse-glow 3s ease-in-out infinite;
            }

            /* Mobile adjustments */
            @media (max-width: 768px) {
                .section-progress {
                    display: none;
                }

                .back-to-top {
                    bottom: 20px;
                    right: 20px;
                    width: 45px;
                    height: 45px;
                }

                [data-scroll-reveal] {
                    transform: translateY(30px) !important;
                }

                [data-scroll-reveal].revealed {
                    transform: translateY(0) !important;
                }
            }

            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                [data-scroll-reveal],
                [data-parallax],
                [data-animate],
                .back-to-top,
                .section-progress-dot {
                    animation: none !important;
                    transition: none !important;
                }

                html.smooth-scroll {
                    scroll-behavior: auto;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setupScrollReveal() {
        const elements = document.querySelectorAll('[data-scroll-reveal]');
        
        if (!elements.length) return;

        const observerOptions = {
            threshold: this.options.revealThreshold,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    
                    // Optionally unobserve after revealing (one-time animation)
                    if (!entry.target.dataset.scrollRepeat) {
                        observer.unobserve(entry.target);
                    }
                } else if (entry.target.dataset.scrollRepeat) {
                    entry.target.classList.remove('revealed');
                }
            });
        }, observerOptions);

        elements.forEach(element => {
            observer.observe(element);
        });

        this.observers.push(observer);
    }

    setupParallax() {
        this.parallaxElements = document.querySelectorAll('[data-parallax]');
        
        if (!this.parallaxElements.length) return;

        // Initial parallax position
        this.updateParallax();
    }

    updateParallax() {
        if (!this.parallaxElements || !this.parallaxElements.length) return;

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        this.parallaxElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const elementTop = rect.top + scrollTop;
            const elementHeight = element.offsetHeight;
            
            // Only apply parallax when element is in viewport
            if (rect.top < this.windowHeight && rect.bottom > 0) {
                const speed = parseFloat(element.dataset.parallax) || this.options.parallaxSpeed;
                const distance = (scrollTop - elementTop) * speed;
                
                element.style.transform = `translateY(${distance}px)`;
            }
        });
    }

    setupScrollProgress() {
        // Create progress bar
        const progressContainer = document.createElement('div');
        progressContainer.className = 'scroll-progress-container';
        progressContainer.innerHTML = '<div class="scroll-progress-bar"></div>';
        document.body.appendChild(progressContainer);

        this.progressBar = progressContainer.querySelector('.scroll-progress-bar');

        // Create section indicators
        this.setupSectionProgress();

        // Create back to top button
        this.setupBackToTop();

        // Update progress
        this.updateScrollProgress();
    }

    setupSectionProgress() {
        const sections = document.querySelectorAll('[data-section]');
        
        if (!sections.length) return;

        const progressContainer = document.createElement('div');
        progressContainer.className = 'section-progress';

        sections.forEach((section, index) => {
            const dot = document.createElement('div');
            dot.className = 'section-progress-dot';
            dot.dataset.section = section.dataset.section || `section-${index}`;
            dot.dataset.label = section.dataset.sectionLabel || `Section ${index + 1}`;
            
            dot.addEventListener('click', () => {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });

            progressContainer.appendChild(dot);
        });

        document.body.appendChild(progressContainer);
        this.sectionProgress = progressContainer;
        this.sections = sections;

        // Show section progress after scrolling
        setTimeout(() => {
            if (window.pageYOffset > 300) {
                this.sectionProgress.classList.add('visible');
            }
        }, 1000);

        // Update active section
        this.updateSectionProgress();
    }

    setupBackToTop() {
        const backToTop = document.createElement('div');
        backToTop.className = 'back-to-top';
        backToTop.innerHTML = '<i class="bi bi-arrow-up"></i>';
        backToTop.title = 'Back to top';
        
        backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        document.body.appendChild(backToTop);
        this.backToTop = backToTop;
    }

    updateScrollProgress() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = this.documentHeight - this.windowHeight;
        const scrollPercentage = (scrollTop / scrollHeight) * 100;

        // Update progress bar
        if (this.progressBar) {
            this.progressBar.style.width = `${Math.min(scrollPercentage, 100)}%`;
        }

        // Show/hide back to top button
        if (this.backToTop) {
            if (scrollTop > 400) {
                this.backToTop.classList.add('visible');
            } else {
                this.backToTop.classList.remove('visible');
            }
        }

        // Show/hide section progress
        if (this.sectionProgress) {
            if (scrollTop > 300) {
                this.sectionProgress.classList.add('visible');
            } else {
                this.sectionProgress.classList.remove('visible');
            }
        }

        this.updateSectionProgress();
    }

    updateSectionProgress() {
        if (!this.sections || !this.sectionProgress) return;

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollMiddle = scrollTop + (this.windowHeight / 2);

        this.sections.forEach((section, index) => {
            const rect = section.getBoundingClientRect();
            const sectionTop = rect.top + scrollTop;
            const sectionBottom = sectionTop + section.offsetHeight;

            const dot = this.sectionProgress.children[index];
            if (!dot) return;

            if (scrollMiddle >= sectionTop && scrollMiddle < sectionBottom) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    setupSmoothScroll() {
        document.documentElement.classList.add('smooth-scroll');

        // Handle anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const href = anchor.getAttribute('href');
                if (href === '#' || href === '#!') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });

                    // Update URL without jumping
                    if (history.pushState) {
                        history.pushState(null, null, href);
                    }
                }
            });
        });
    }

    setupScrollListener() {
        let lastScroll = 0;

        const handleScroll = () => {
            const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
            
            // Prevent negative scroll values
            if (currentScroll < 0) return;

            // Update scroll position
            this.scrollPosition = currentScroll;

            // Request animation frame for smooth animations
            if (!this.ticking) {
                window.requestAnimationFrame(() => {
                    if (this.options.enableParallax) {
                        this.updateParallax();
                    }

                    if (this.options.enableProgress) {
                        this.updateScrollProgress();
                    }

                    this.ticking = false;
                });

                this.ticking = true;
            }

            lastScroll = currentScroll;
        };

        // Use passive listener for better performance
        window.addEventListener('scroll', handleScroll, { passive: true });
    }

    setupResizeListener() {
        const handleResize = () => {
            this.windowHeight = window.innerHeight;
            this.documentHeight = document.documentElement.scrollHeight;

            if (this.options.enableProgress) {
                this.updateScrollProgress();
            }
        };

        window.addEventListener('resize', handleResize);
    }

    // Public methods for manual control
    reveal(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.classList.add('revealed');
        });
    }

    hide(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.classList.remove('revealed');
        });
    }

    scrollToSection(sectionId) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    destroy() {
        // Clean up observers
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];

        // Remove elements
        if (this.progressBar) {
            this.progressBar.parentElement.remove();
        }
        if (this.sectionProgress) {
            this.sectionProgress.remove();
        }
        if (this.backToTop) {
            this.backToTop.remove();
        }

        // Remove smooth scroll class
        document.documentElement.classList.remove('smooth-scroll');
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.scrollAnimations = new ScrollAnimations({
        enableParallax: true,
        enableReveal: true,
        enableProgress: true,
        enableSmoothScroll: true,
        revealThreshold: 0.15,
        parallaxSpeed: 0.5
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScrollAnimations;
}
