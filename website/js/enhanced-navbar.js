/**
 * Enhanced Navbar with Glass Morphism - Jupiter Dashboard Style
 * Enterprise Scanner Website
 * Features: Scroll behavior, glass effect, search functionality, mobile menu
 */

class EnhancedNavbar {
    constructor(options = {}) {
        this.options = {
            scrollThreshold: options.scrollThreshold || 50,
            hideOnScroll: options.hideOnScroll !== false,
            searchEnabled: options.searchEnabled !== false,
            ...options
        };

        this.navbar = null;
        this.lastScrollY = 0;
        this.scrollingDown = false;
        this.isScrolled = false;
        this.mobileMenuOpen = false;

        this.init();
    }

    init() {
        this.navbar = document.querySelector('.navbar, nav');
        if (!this.navbar) {
            console.warn('EnhancedNavbar: No navbar element found');
            return;
        }

        this.injectStyles();
        this.enhanceNavbar();
        this.setupScrollBehavior();
        this.setupMobileMenu();
        
        if (this.options.searchEnabled) {
            this.setupSearch();
        }
    }

    injectStyles() {
        if (document.getElementById('enhanced-navbar-styles')) return;

        const style = document.createElement('style');
        style.id = 'enhanced-navbar-styles';
        style.textContent = `
            /* Enhanced Navbar Styles */
            .navbar-enhanced {
                position: fixed !important;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: transparent !important;
            }

            .navbar-enhanced.scrolled {
                background: rgba(15, 23, 42, 0.8) !important;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }

            .navbar-enhanced.hidden {
                transform: translateY(-100%);
            }

            .navbar-enhanced .navbar-brand {
                font-weight: 700;
                font-size: 1.5rem;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                transition: all 0.3s ease;
            }

            .navbar-enhanced .navbar-brand:hover {
                transform: scale(1.05);
            }

            .navbar-enhanced .nav-link {
                color: rgba(255, 255, 255, 0.8) !important;
                font-weight: 500;
                padding: 0.5rem 1rem !important;
                border-radius: 8px;
                transition: all 0.3s ease;
                position: relative;
            }

            .navbar-enhanced .nav-link:hover {
                color: #ffffff !important;
                background: rgba(59, 130, 246, 0.1);
            }

            .navbar-enhanced .nav-link.active {
                color: #3b82f6 !important;
            }

            .navbar-enhanced .nav-link::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%) scaleX(0);
                width: 80%;
                height: 2px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                transition: transform 0.3s ease;
            }

            .navbar-enhanced .nav-link:hover::after,
            .navbar-enhanced .nav-link.active::after {
                transform: translateX(-50%) scaleX(1);
            }

            /* Search Bar */
            .navbar-search {
                position: relative;
                max-width: 300px;
                margin: 0 1rem;
            }

            .navbar-search input {
                width: 100%;
                padding: 0.5rem 1rem 0.5rem 2.5rem;
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #ffffff;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }

            .navbar-search input:focus {
                outline: none;
                background: rgba(30, 41, 59, 0.8);
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }

            .navbar-search input::placeholder {
                color: rgba(255, 255, 255, 0.4);
            }

            .navbar-search-icon {
                position: absolute;
                left: 0.75rem;
                top: 50%;
                transform: translateY(-50%);
                color: rgba(255, 255, 255, 0.4);
                pointer-events: none;
            }

            .navbar-search-results {
                position: absolute;
                top: calc(100% + 8px);
                left: 0;
                right: 0;
                background: rgba(30, 41, 59, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                max-height: 400px;
                overflow-y: auto;
                display: none;
            }

            .navbar-search-results.active {
                display: block;
            }

            .navbar-search-result {
                padding: 0.75rem 1rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                cursor: pointer;
                transition: background 0.2s ease;
            }

            .navbar-search-result:last-child {
                border-bottom: none;
            }

            .navbar-search-result:hover {
                background: rgba(59, 130, 246, 0.1);
            }

            .navbar-search-result-title {
                color: #ffffff;
                font-weight: 500;
                font-size: 0.9rem;
                margin-bottom: 0.25rem;
            }

            .navbar-search-result-desc {
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.8rem;
            }

            /* CTA Buttons */
            .navbar-cta {
                margin-left: 1rem;
            }

            .navbar-cta .btn {
                padding: 0.5rem 1.5rem;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
            }

            .navbar-cta .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border: none;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }

            .navbar-cta .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            }

            .navbar-cta .btn-outline {
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: #ffffff;
                background: transparent;
            }

            .navbar-cta .btn-outline:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: #ffffff;
            }

            /* Mobile Menu */
            .navbar-toggler {
                border: none;
                padding: 0.5rem;
                background: rgba(30, 41, 59, 0.6);
                border-radius: 8px;
                transition: all 0.3s ease;
            }

            .navbar-toggler:hover {
                background: rgba(30, 41, 59, 0.8);
            }

            .navbar-toggler-icon {
                width: 24px;
                height: 2px;
                background: #ffffff;
                display: block;
                position: relative;
                transition: all 0.3s ease;
            }

            .navbar-toggler-icon::before,
            .navbar-toggler-icon::after {
                content: '';
                position: absolute;
                width: 100%;
                height: 100%;
                background: #ffffff;
                transition: all 0.3s ease;
            }

            .navbar-toggler-icon::before {
                top: -8px;
            }

            .navbar-toggler-icon::after {
                top: 8px;
            }

            .navbar-toggler.active .navbar-toggler-icon {
                background: transparent;
            }

            .navbar-toggler.active .navbar-toggler-icon::before {
                top: 0;
                transform: rotate(45deg);
            }

            .navbar-toggler.active .navbar-toggler-icon::after {
                top: 0;
                transform: rotate(-45deg);
            }

            @media (max-width: 991px) {
                .navbar-collapse {
                    background: rgba(15, 23, 42, 0.95);
                    backdrop-filter: blur(10px);
                    margin-top: 1rem;
                    padding: 1rem;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }

                .navbar-search {
                    max-width: 100%;
                    margin: 1rem 0;
                }

                .navbar-cta {
                    margin-left: 0;
                    margin-top: 1rem;
                }

                .navbar-cta .btn {
                    display: block;
                    width: 100%;
                    margin-bottom: 0.5rem;
                }
            }

            /* Smooth scroll offset for fixed navbar */
            html {
                scroll-padding-top: 80px;
            }
        `;
        document.head.appendChild(style);
    }

    enhanceNavbar() {
        this.navbar.classList.add('navbar-enhanced');
        
        // Add glass effect initially if page is already scrolled
        if (window.scrollY > this.options.scrollThreshold) {
            this.navbar.classList.add('scrolled');
            this.isScrolled = true;
        }

        // Ensure proper spacing for fixed navbar
        if (!document.querySelector('.navbar-spacer')) {
            const spacer = document.createElement('div');
            spacer.className = 'navbar-spacer';
            spacer.style.height = this.navbar.offsetHeight + 'px';
            this.navbar.parentNode.insertBefore(spacer, this.navbar.nextSibling);
        }
    }

    setupScrollBehavior() {
        let ticking = false;

        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    handleScroll() {
        const currentScrollY = window.scrollY;

        // Add/remove scrolled class for glass effect
        if (currentScrollY > this.options.scrollThreshold) {
            if (!this.isScrolled) {
                this.navbar.classList.add('scrolled');
                this.isScrolled = true;
            }
        } else {
            if (this.isScrolled) {
                this.navbar.classList.remove('scrolled');
                this.isScrolled = false;
            }
        }

        // Hide/show on scroll
        if (this.options.hideOnScroll && currentScrollY > this.options.scrollThreshold * 2) {
            if (currentScrollY > this.lastScrollY && !this.scrollingDown) {
                // Scrolling down
                this.navbar.classList.add('hidden');
                this.scrollingDown = true;
            } else if (currentScrollY < this.lastScrollY && this.scrollingDown) {
                // Scrolling up
                this.navbar.classList.remove('hidden');
                this.scrollingDown = false;
            }
        } else {
            this.navbar.classList.remove('hidden');
        }

        this.lastScrollY = currentScrollY;
    }

    setupMobileMenu() {
        const toggler = this.navbar.querySelector('.navbar-toggler');
        if (!toggler) return;

        toggler.addEventListener('click', () => {
            this.mobileMenuOpen = !this.mobileMenuOpen;
            toggler.classList.toggle('active');
        });

        // Close mobile menu when clicking nav links
        const navLinks = this.navbar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (this.mobileMenuOpen && window.innerWidth < 992) {
                    toggler.click();
                }
            });
        });
    }

    setupSearch() {
        const navbarNav = this.navbar.querySelector('.navbar-nav');
        if (!navbarNav) return;

        // Create search bar
        const searchContainer = document.createElement('div');
        searchContainer.className = 'navbar-search d-none d-lg-block';
        searchContainer.innerHTML = `
            <i class="bi bi-search navbar-search-icon"></i>
            <input type="text" placeholder="Search..." aria-label="Search">
            <div class="navbar-search-results"></div>
        `;

        navbarNav.parentNode.insertBefore(searchContainer, navbarNav.nextSibling);

        const searchInput = searchContainer.querySelector('input');
        const searchResults = searchContainer.querySelector('.navbar-search-results');

        // Sample search data (customize based on your site)
        const searchData = [
            { title: 'Security Assessment', desc: 'Enterprise vulnerability scanning', url: '/security-assessment.html' },
            { title: 'Analytics Dashboard', desc: 'Real-time security metrics', url: '/analytics-dashboard.html' },
            { title: 'Case Studies', desc: 'Fortune 500 success stories', url: '/case_studies.html' },
            { title: 'API Documentation', desc: 'Developer integration guides', url: '/api-documentation.html' },
            { title: 'ROI Calculator', desc: 'Calculate your security savings', url: '/#roi-calculator' }
        ];

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('active');
                return;
            }

            const results = searchData.filter(item => 
                item.title.toLowerCase().includes(query) || 
                item.desc.toLowerCase().includes(query)
            );

            if (results.length > 0) {
                searchResults.innerHTML = results.map(result => `
                    <a href="${result.url}" class="navbar-search-result">
                        <div class="navbar-search-result-title">${this.highlightText(result.title, query)}</div>
                        <div class="navbar-search-result-desc">${result.desc}</div>
                    </a>
                `).join('');
                searchResults.classList.add('active');
            } else {
                searchResults.innerHTML = '<div class="navbar-search-result">No results found</div>';
                searchResults.classList.add('active');
            }
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchContainer.contains(e.target)) {
                searchResults.classList.remove('active');
            }
        });
    }

    highlightText(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    destroy() {
        this.navbar.classList.remove('navbar-enhanced', 'scrolled', 'hidden');
        const styles = document.getElementById('enhanced-navbar-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Auto-initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedNavbar = new EnhancedNavbar();
});
